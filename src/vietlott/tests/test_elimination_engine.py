"""
Unit tests for vietlott.model.elimination_engine:
1. calculate_elimination_risk_scores bounds [0, 1], valid keys, no NaN/Inf.
2. prune_dead_numbers partition, count for 6/55 (16), 6/45 (13), 5/35 (9), no overlap.
3. evaluate_walk_forward_elimination_precision on real historical records >= 85%.
4. Determinism & edge cases (empty records, short records).
5. Zero mock data verification.
"""

import json
import math
from pathlib import Path
import pytest

from vietlott.model.elimination_engine import (
    calculate_elimination_risk_scores,
    prune_dead_numbers,
    evaluate_walk_forward_elimination_precision,
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


class TestEliminationEngine:
    def test_calculate_elimination_risk_scores_bounds_and_validity(self):
        """Verify scores are in [0, 1], no NaN/Inf, all balls present, valid reasons."""
        records = _read_real_records("power655.jsonl")
        assert len(records) >= 120, "Require at least 120 draws of real data"

        sub_records = records[:200]
        max_val = 55
        num_balls = 6

        scores = calculate_elimination_risk_scores(sub_records, max_val, num_balls)
        assert len(scores) == max_val

        valid_reasons = {
            "Gan lì lợm (Vắng mặt kéo dài)",
            "Ngủ đông (Triệt tiêu phổ sóng)",
            "Xung khắc (Kỵ bóng nổ kỳ trước)",
            "Đáy đồng thuận (Xác suất thấp)",
        }

        for b in range(1, max_val + 1):
            assert b in scores
            entry = scores[b]
            for key in ["risk_score", "hazard_risk", "wavelet_dormancy", "repulsion_risk", "bottom_risk"]:
                val = entry[key]
                assert isinstance(val, (int, float))
                assert not math.isnan(val), f"Ball {b} {key} is NaN"
                assert not math.isinf(val), f"Ball {b} {key} is Inf"
                assert 0.0 <= val <= 1.0, f"Ball {b} {key}={val} out of bounds [0, 1]"

            assert entry["reason"] in valid_reasons, f"Unexpected reason: {entry['reason']}"

    def test_prune_dead_numbers_default_counts_and_partition(self):
        """Verify partition on Power 6/55 (16), Mega 6/45 (13), Power 5/35 (9)."""
        configs = [
            ("power655.jsonl", 55, 6, 16, 39),
            ("power645.jsonl", 45, 6, 13, 32),
            ("power535.jsonl", 35, 5, 9, 26),
        ]

        for filename, max_val, num_balls, expected_elim, expected_pruned in configs:
            records = _read_real_records(filename)
            assert len(records) >= 50
            risk_scores = calculate_elimination_risk_scores(records[-100:], max_val, num_balls)

            pruned_result = prune_dead_numbers(risk_scores, max_val)

            assert pruned_result["eliminated_count"] == expected_elim
            assert pruned_result["pruned_universe_size"] == expected_pruned
            assert len(pruned_result["eliminated_balls"]) == expected_elim
            assert len(pruned_result["eliminated_ball_numbers"]) == expected_elim
            assert len(pruned_result["pruned_universe"]) == expected_pruned

            # Check partition: no overlap, union is full universe
            elim_set = set(pruned_result["eliminated_ball_numbers"])
            pruned_set = set(pruned_result["pruned_universe"])
            universe_set = set(range(1, max_val + 1))

            assert elim_set.isdisjoint(pruned_set)
            assert elim_set | pruned_set == universe_set

            # Check eliminated balls sorted descending by risk score
            elim_scores = [x["risk_score"] for x in pruned_result["eliminated_balls"]]
            assert elim_scores == sorted(elim_scores, reverse=True)

            # Check pruned universe sorted ascending
            assert pruned_result["pruned_universe"] == sorted(pruned_result["pruned_universe"])

            # Check elimination rate percentage
            expected_rate = round((expected_elim / max_val) * 100.0, 1)
            assert pruned_result["elimination_rate_pct"] == expected_rate

    def test_prune_dead_numbers_custom_elim_count(self):
        """Verify explicit elim_count overrides default."""
        records = _read_real_records("power655.jsonl")
        risk_scores = calculate_elimination_risk_scores(records[-80:], 55, 6)

        pruned = prune_dead_numbers(risk_scores, 55, elim_count=10)
        assert pruned["eliminated_count"] == 10
        assert pruned["pruned_universe_size"] == 45
        assert len(pruned["eliminated_ball_numbers"]) == 10

    def test_evaluate_walk_forward_elimination_precision_real_data(self):
        """Verify walk-forward backtest across 100 draws achieves precision >= 85%."""
        records_655 = _read_real_records("power655.jsonl")
        assert len(records_655) >= 120

        # Walk-forward 100 draws on Power 6/55
        wf_655 = evaluate_walk_forward_elimination_precision(
            records_655, max_val=55, num_balls=6, num_draws=100, elim_count=16
        )
        assert "historical_elimination_precision" in wf_655
        precision_655 = wf_655["historical_elimination_precision"]
        assert precision_655 >= 85.0, f"Power 6/55 elimination precision {precision_655}% < 85%"
        assert wf_655["evaluated_draws"] == 100

        # Walk-forward on Mega 6/45 (50 draws to balance speed and rigor)
        records_645 = _read_real_records("power645.jsonl")
        assert len(records_645) >= 100
        wf_645 = evaluate_walk_forward_elimination_precision(
            records_645, max_val=45, num_balls=6, num_draws=50, elim_count=13
        )
        precision_645 = wf_645["historical_elimination_precision"]
        assert precision_645 >= 85.0, f"Mega 6/45 elimination precision {precision_645}% < 85%"

    def test_determinism_and_reproducibility(self):
        """Verify calling methods repeatedly on same data produces 100% deterministic output."""
        records = _read_real_records("power655.jsonl")[:150]
        run1 = calculate_elimination_risk_scores(records, 55, 6)
        run2 = calculate_elimination_risk_scores(records, 55, 6)

        assert run1 == run2

        p1 = prune_dead_numbers(run1, 55, 16)
        p2 = prune_dead_numbers(run2, 55, 16)
        assert p1 == p2

    def test_edge_cases(self):
        """Verify handling of empty records, short records, zero max_val."""
        # Empty records
        empty_scores = calculate_elimination_risk_scores([], 55, 6)
        assert len(empty_scores) == 55
        for b, data in empty_scores.items():
            assert 0.0 <= data["risk_score"] <= 1.0

        p_empty = prune_dead_numbers(empty_scores, 55)
        assert p_empty["eliminated_count"] == 16
        assert p_empty["pruned_universe_size"] == 39

        # Single record
        single_scores = calculate_elimination_risk_scores([{"result": [1, 2, 3, 4, 5, 6]}], 55, 6)
        assert len(single_scores) == 55

        # max_val <= 0
        assert calculate_elimination_risk_scores([], 0, 6) == {}
        assert prune_dead_numbers({}, 0)["eliminated_count"] == 0

        # Walk-forward with too few records
        wf_short = evaluate_walk_forward_elimination_precision(records=[{"result": [1, 2, 3, 4, 5, 6]}], max_val=55, num_balls=6, num_draws=10)
        assert "historical_elimination_precision" in wf_short
