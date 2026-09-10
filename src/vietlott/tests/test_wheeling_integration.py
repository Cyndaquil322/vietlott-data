"""
Integration tests for Combinatorial Wheeling Strategy and Covering Engine integration in render_web_data.py.
"""

import unittest
from pathlib import Path
from typing import Dict, List
import random

from vietlott.render_web_data import (
    generate_wheeling_strategy,
    calculate_multi_model_consensus_and_backtest,
    read_jsonl,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _generate_synthetic_records(count: int, max_val: int, num_balls: int, is_two_matrix: bool = False) -> List[Dict]:
    """Generates synthetic draw records for deterministic testing."""
    rng = random.Random(12345)
    records = []
    for i in range(count):
        balls = sorted(rng.sample(range(1, max_val + 1), num_balls))
        if is_two_matrix:
            spec = rng.randint(1, 12)
            balls.append(spec)
        records.append({
            "id": f"#{1000 + i}",
            "date": f"2026-01-{(i % 28) + 1:02d}",
            "result": balls,
        })
    return records


class TestWheelingStrategyIntegration(unittest.TestCase):
    """Test generate_wheeling_strategy with Power 6/55, Mega 6/45, and Power 5/35."""

    def setUp(self):
        # Prefer real records if available, otherwise synthetic
        p655_path = DATA_DIR / "power655.jsonl"
        p645_path = DATA_DIR / "power645.jsonl"
        p535_path = DATA_DIR / "power535.jsonl"

        if p655_path.exists():
            self.records_655 = read_jsonl(p655_path)[-60:]
        else:
            self.records_655 = _generate_synthetic_records(60, 55, 6)

        if p645_path.exists():
            self.records_645 = read_jsonl(p645_path)[-60:]
        else:
            self.records_645 = _generate_synthetic_records(60, 45, 6)

        if p535_path.exists():
            self.records_535 = read_jsonl(p535_path)[-60:]
        else:
            self.records_535 = _generate_synthetic_records(60, 35, 5, is_two_matrix=True)

    def test_wheeling_strategy_power655(self):
        """Power 6/55: 12-number Core Pool, 6 tickets, AC >= 7, valid coverage dict."""
        res = generate_wheeling_strategy(
            self.records_655, product_key="power_655", max_val=55, num_balls=6, is_two_matrix=False
        )
        # Required keys
        for key in ["core_pool", "core_pool_size", "tickets", "special_recommendation",
                    "guarantee_statement", "total_cost", "total_tickets", "coverage"]:
            self.assertIn(key, res, f"Missing key '{key}' in result")

        self.assertEqual(res["core_pool_size"], 12)
        self.assertEqual(len(res["core_pool"]), 12)
        self.assertEqual(len(set(res["core_pool"])), 12)
        for b in res["core_pool"]:
            self.assertTrue(1 <= b <= 55)

        # 6 tickets
        tickets = res["tickets"]
        self.assertEqual(len(tickets), 6)
        self.assertEqual(res["total_tickets"], 6)
        self.assertEqual(res["total_cost"], 60000)

        for t in tickets:
            self.assertIn("numbers", t)
            self.assertIn("sum", t)
            self.assertIn("ac", t)
            self.assertIn("odds", t)
            self.assertIn("evens", t)
            self.assertIn("distinctTails", t)
            self.assertEqual(len(t["numbers"]), 6)
            self.assertEqual(len(set(t["numbers"])), 6)
            # Arithmetic complexity constraint for 6-ball game
            self.assertGreaterEqual(t["ac"], 7, f"Ticket {t['numbers']} has AC < 7: {t['ac']}")

        # Coverage dict
        cov = res["coverage"]
        self.assertIn("cov_3_if_3_pct", cov)
        self.assertIn("cov_3_if_4_pct", cov)
        self.assertGreater(cov["cov_3_if_3_pct"], 0.0)
        self.assertGreaterEqual(cov["cov_3_if_4_pct"], 95.0)

        # Special recommendation for 6/55
        self.assertEqual(len(res["special_recommendation"]), 2)
        for sb in res["special_recommendation"]:
            self.assertTrue(1 <= sb <= 55)

    def test_wheeling_strategy_mega645(self):
        """Mega 6/45: 12-number Core Pool, 6 tickets, AC >= 7, valid coverage dict."""
        res = generate_wheeling_strategy(
            self.records_645, product_key="power_645", max_val=45, num_balls=6, is_two_matrix=False
        )
        self.assertEqual(res["core_pool_size"], 12)
        self.assertEqual(len(res["core_pool"]), 12)
        self.assertEqual(len(res["tickets"]), 6)

        for t in res["tickets"]:
            self.assertEqual(len(t["numbers"]), 6)
            self.assertGreaterEqual(t["ac"], 7, f"Ticket {t['numbers']} has AC < 7: {t['ac']}")
            for b in t["numbers"]:
                self.assertTrue(1 <= b <= 45)

        cov = res["coverage"]
        self.assertIn("cov_3_if_4_pct", cov)
        self.assertGreaterEqual(cov["cov_3_if_4_pct"], 95.0)

    def test_wheeling_strategy_power535(self):
        """Power 5/35: 10-number Core Pool, 6 tickets, AC >= 4, valid coverage dict."""
        res = generate_wheeling_strategy(
            self.records_535, product_key="power_535", max_val=35, num_balls=5, is_two_matrix=True
        )
        self.assertEqual(res["core_pool_size"], 10)
        self.assertEqual(len(res["core_pool"]), 10)
        self.assertEqual(len(res["tickets"]), 6)

        for t in res["tickets"]:
            self.assertEqual(len(t["numbers"]), 5)
            self.assertGreaterEqual(t["ac"], 4, f"Ticket {t['numbers']} has AC < 4: {t['ac']}")
            for b in t["numbers"]:
                self.assertTrue(1 <= b <= 35)

        cov = res["coverage"]
        self.assertIn("cov_3_if_3_pct", cov)
        self.assertIn("cov_3_if_4_pct", cov)
        self.assertGreaterEqual(cov["cov_3_if_4_pct"], 95.0)

        # Special recommendation for 5/35 (range 1..12)
        self.assertEqual(len(res["special_recommendation"]), 2)
        for sb in res["special_recommendation"]:
            self.assertTrue(1 <= sb <= 12)


class TestMultiModelConsensusWheelingBacktest(unittest.TestCase):
    """Test calculate_multi_model_consensus_and_backtest wheeling output."""

    def test_consensus_wheeling_backtest_power655(self):
        """Verify tickets contains wheeling_tickets, wheeling_4_tickets, and wheel4_backtest."""
        p655_path = DATA_DIR / "power655.jsonl"
        if p655_path.exists():
            records = read_jsonl(p655_path)[-35:]
        else:
            records = _generate_synthetic_records(35, 55, 6)

        res = calculate_multi_model_consensus_and_backtest(
            records, "power_655", max_val=55, num_balls=6, num_draws=5, display_draws=3
        )
        self.assertIn("tickets", res)
        tickets = res["tickets"]

        # Backwards compatibility: wheeling_4_tickets present with 4 tickets
        self.assertIn("wheeling_4_tickets", tickets)
        self.assertEqual(len(tickets["wheeling_4_tickets"]), 4)

        # New covering wheel: wheeling_tickets present with 6 tickets
        self.assertIn("wheeling_tickets", tickets)
        self.assertEqual(len(tickets["wheeling_tickets"]), 6)
        for t in tickets["wheeling_tickets"]:
            self.assertEqual(len(t["numbers"]), 6)
            self.assertEqual(len(set(t["numbers"])), 6)

        # Backtest stats
        self.assertIn("wheel4_backtest", tickets)
        w4 = tickets["wheel4_backtest"]
        self.assertIn("overall_prize_win_rate", w4)
        self.assertIn("core_ge4_count", w4)
        self.assertIn("core_ge4_win_rate", w4)
        self.assertIn("guarantee_coverage", w4)

        # wheel_backtest alias
        self.assertIn("wheel_backtest", tickets)
        wb = tickets["wheel_backtest"]
        self.assertEqual(wb["overall_prize_win_rate"], w4["overall_prize_win_rate"])
        self.assertEqual(wb["core_ge4_count"], w4["core_ge4_count"])
        self.assertEqual(wb["core_ge4_win_rate"], w4["core_ge4_win_rate"])

        # Walk-forward history logs contain wheel4 entry
        history = res.get("history_walk_forward", [])
        self.assertGreater(len(history), 0)
        for h in history:
            self.assertIn("wheel4", h)
            self.assertIn("ticketHits", h["wheel4"])
            self.assertIn("maxHit", h["wheel4"])
            self.assertIn("wonPrize", h["wheel4"])


if __name__ == "__main__":
    unittest.main()
