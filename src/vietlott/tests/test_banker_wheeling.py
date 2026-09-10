"""
Unit tests for vietlott.model.banker_wheeling:
1. select_primary_banker selection logic, consensus + transition pull scoring, fallback.
2. generate_key_banker_tickets:
   - 100% of tickets contain banker
   - Satellite balls are disjoint from banker
   - Exactly 6 tickets generated
   - Negative space AC >= 7 for 6-ball games, AC >= 4 for 5-ball games
   - Valid metrics on all tickets
   - Determinism with fixed seed
3. evaluate_banker_wheeling_walk_forward on real historical data:
   - Real lottery records (Zero Mock Data)
   - Strict Walk-Forward (no look-ahead)
   - Verified output metrics (banker_hit_rate_pct, overall_prize_win_rate, win_rate_when_banker_hit)
4. Edge cases and robust handling (duplicates, padding, empty/short records).
"""

import json
import math
from pathlib import Path
import pytest

from vietlott.model.banker_wheeling import (
    select_primary_banker,
    generate_key_banker_tickets,
    evaluate_banker_wheeling_walk_forward,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _read_real_records(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


class TestSelectPrimaryBanker:
    def test_select_primary_banker_from_key_balls(self):
        """Verify banker is chosen from key_balls with highest combined score."""
        key_balls = [7, 12, 23, 34, 45]
        consensus_scores = {
            7: 4.5,
            12: 5.2,
            23: 5.0,
            34: 3.1,
            45: 5.1,
        }
        # Without pull_data, ball 12 has highest score (5.2)
        banker = select_primary_banker(key_balls, consensus_scores)
        assert banker == 12

        # With pull_data boosting ball 45:
        # Score 45 = 5.1 + (1.6 - 1.0) * 0.5 = 5.1 + 0.3 = 5.4 > 5.2
        pull_data = {
            45: {"max_pull_lift": 1.6},
            12: {"max_pull_lift": 1.0},
        }
        banker_boosted = select_primary_banker(key_balls, consensus_scores, pull_data)
        assert banker_boosted == 45

    def test_select_primary_banker_fallback_empty_key_balls(self):
        """When key_balls is empty, select highest scoring ball from consensus_scores."""
        consensus_scores = {
            3: 2.1,
            15: 6.8,
            28: 4.3,
        }
        banker = select_primary_banker([], consensus_scores)
        assert banker == 15

    def test_select_primary_banker_tie_breaking(self):
        """Deterministic tie-breaking: lower ball number chosen on identical scores."""
        key_balls = [25, 10]
        consensus_scores = {25: 5.0, 10: 5.0}
        banker = select_primary_banker(key_balls, consensus_scores)
        assert banker == 10


class TestGenerateKeyBankerTickets:
    def test_generate_tickets_power_655(self):
        """Verify 6 tickets for Power 6/55: 100% contain banker, AC >= 7."""
        banker = 18
        satellite_pool = [3, 7, 12, 24, 29, 33, 41, 47, 50, 53]
        result = generate_key_banker_tickets(
            banker=banker,
            satellite_pool=satellite_pool,
            product_key="power_655",
            max_val=55,
            num_balls=6,
            num_tickets=6,
            seed=42,
        )

        assert result["banker"] == 18
        assert result["satellite_pool_size"] == 10
        assert set(result["satellite_pool"]) == set(satellite_pool)
        assert banker not in result["satellite_pool"]
        assert result["total_tickets"] == 6
        assert result["total_cost"] == 60000
        assert "leverage_multiplier" in result
        assert "win_guarantee_statement" in result
        assert len(result["tickets"]) == 6

        for idx, ticket in enumerate(result["tickets"]):
            assert ticket["ticketIndex"] == idx + 1
            nums = ticket["numbers"]
            assert len(nums) == 6
            assert banker in nums, f"Ticket {idx+1} missing banker"
            assert ticket["banker"] == banker
            assert len(ticket["satellites"]) == 5
            for sat in ticket["satellites"]:
                assert sat in satellite_pool
                assert sat != banker
            # Arithmetic complexity requirement
            assert ticket["ac"] >= 7, f"Ticket {idx+1} AC={ticket['ac']} < 7"
            assert ticket["passed_ac_filter"] is True
            # Parity and tail metrics
            assert ticket["odds"] + ticket["evens"] == 6
            assert 1 <= ticket["distinctTails"] <= 6
            assert ticket["sum"] == sum(nums)

    def test_generate_tickets_power_535(self):
        """Verify 6 tickets for Power 5/35: 100% contain banker, AC >= 4."""
        banker = 9
        satellite_pool = [2, 5, 11, 14, 18, 22, 26, 29, 31, 35]
        result = generate_key_banker_tickets(
            banker=banker,
            satellite_pool=satellite_pool,
            product_key="power_535",
            max_val=35,
            num_balls=5,
            num_tickets=6,
            seed=42,
        )

        assert result["banker"] == 9
        assert result["satellite_pool_size"] == 10
        assert banker not in result["satellite_pool"]
        assert result["total_tickets"] == 6

        for idx, ticket in enumerate(result["tickets"]):
            nums = ticket["numbers"]
            assert len(nums) == 5
            assert banker in nums
            assert len(ticket["satellites"]) == 4
            assert ticket["ac"] >= 4, f"Ticket {idx+1} AC={ticket['ac']} < 4"
            assert ticket["passed_ac_filter"] is True

    def test_generate_tickets_banker_in_satellites_and_padding(self):
        """Verify robustness when banker is passed inside satellite_pool and pool has < 10 elements."""
        banker = 7
        short_pool = [7, 12, 19, 25]  # contains banker and only 3 other elements
        result = generate_key_banker_tickets(
            banker=banker,
            satellite_pool=short_pool,
            product_key="power_645",
            max_val=45,
            num_balls=6,
            num_tickets=6,
            seed=42,
        )

        assert result["satellite_pool_size"] == 10
        assert banker not in result["satellite_pool"]
        assert len(result["satellite_pool"]) == 10
        assert len(set(result["satellite_pool"])) == 10

    def test_determinism_and_reproducibility(self):
        """Same input parameters produce identical ticket structures."""
        banker = 14
        satellite_pool = [1, 5, 8, 12, 19, 22, 27, 30, 38, 42]
        res1 = generate_key_banker_tickets(banker, satellite_pool, "power_645", 45, 6, seed=42)
        res2 = generate_key_banker_tickets(banker, satellite_pool, "power_645", 45, 6, seed=42)

        assert res1["tickets"] == res2["tickets"]
        assert res1["satellite_pool"] == res2["satellite_pool"]


class TestEvaluateBankerWheelingWalkForward:
    def test_evaluate_walk_forward_real_data(self):
        """Walk-forward evaluation on real historical Power 6/55 draws."""
        records = _read_real_records("power655.jsonl")
        assert len(records) >= 120, "Need at least 120 draws"

        eval_result = evaluate_banker_wheeling_walk_forward(
            records=records,
            max_val=55,
            num_balls=6,
            num_draws=100,
        )

        assert "banker_hit_rate_pct" in eval_result
        assert "overall_prize_win_rate" in eval_result
        assert "win_rate_when_banker_hit" in eval_result
        assert "evaluated_draws" in eval_result

        assert eval_result["evaluated_draws"] == 100
        assert 0.0 <= eval_result["banker_hit_rate_pct"] <= 100.0
        assert 0.0 <= eval_result["overall_prize_win_rate"] <= 100.0
        assert 0.0 <= eval_result["win_rate_when_banker_hit"] <= 100.0
        # When banker hits, prize win rate is significant (> 20%)
        assert eval_result["win_rate_when_banker_hit"] >= 20.0

    def test_evaluate_walk_forward_all_games(self):
        """Walk-forward evaluation on Mega 6/45 and Power 5/35 real datasets."""
        games = [
            ("power645.jsonl", 45, 6),
            ("power535.jsonl", 35, 5),
        ]
        for filename, max_val, num_balls in games:
            records = _read_real_records(filename)
            assert len(records) >= 80
            res = evaluate_banker_wheeling_walk_forward(
                records=records,
                max_val=max_val,
                num_balls=num_balls,
                num_draws=50,
            )
            assert res["evaluated_draws"] == 50
            assert 0.0 <= res["banker_hit_rate_pct"] <= 100.0
            assert 0.0 <= res["overall_prize_win_rate"] <= 100.0

    def test_evaluate_walk_forward_edge_cases(self):
        """Short or empty records should return safe defaults without throwing."""
        empty_res = evaluate_banker_wheeling_walk_forward([], 55, 6, 50)
        assert empty_res["evaluated_draws"] == 0
        assert empty_res["banker_hit_rate_pct"] == 0.0

        short_res = evaluate_banker_wheeling_walk_forward([{"result": [1, 2, 3, 4, 5, 6]}], 55, 6, 50)
        assert short_res["evaluated_draws"] == 0
