"""
test_consolidation_integration.py
=================================
Integration tests for Task 3:
- render_web_data refactoring & ensemble delegation
- legacy_strategies directory & strategy shim backwards compatibility
- consensus_ensemble.js color/icon mappings
"""

import unittest
from pathlib import Path
from typing import Dict, List

from vietlott.render_web_data import (
    calculate_draw_statistics,
    calculate_odd_even,
    calculate_markov_stats,
    calculate_bayesian_hazard_scores,
    generate_wheeling_strategy,
    calculate_multi_model_consensus_and_backtest,
    generate_web_summary,
    process_power,
)
import vietlott.model.strategy as strategy_shim
import vietlott.model.legacy_strategies as legacy_strategies


class TestRenderWebDataConsolidation(unittest.TestCase):
    """Verify refactored render_web_data functions and surface stats."""

    def test_calculate_draw_statistics_and_odd_even(self):
        sample_records = [
            {"id": "1", "result": [1, 2, 3, 4, 5, 6]},
            {"id": "2", "result": [2, 3, 4, 5, 6, 7]},
            {"id": "3", "result": [3, 4, 5, 6, 7, 8]},
        ]
        stats = calculate_draw_statistics(sample_records, max_val=10, num_balls=6)
        self.assertIn("frequency", stats)
        self.assertIn("hot_numbers", stats)
        self.assertIn("cold_numbers", stats)
        self.assertEqual(len(stats["frequency"]), 10)
        # Numbers 3, 4, 5, 6 appeared in all 3 draws
        top_nums = [x["number"] for x in stats["hot_numbers"][:4]]
        for n in [3, 4, 5, 6]:
            self.assertIn(n, top_nums)

        oe = calculate_odd_even(sample_records, num_balls=6, sample_size=3)
        self.assertIn("odd_pct", oe)
        self.assertIn("even_pct", oe)
        self.assertAlmostEqual(oe["odd_pct"] + oe["even_pct"], 100.0, places=1)

    def test_delegated_ensemble_and_wheeling(self):
        sample_records = [
            {"id": f"#{1000 + i}", "result": [(i + j) % 35 + 1 for j in range(6)]}
            for i in range(35)
        ]
        wheel = generate_wheeling_strategy(sample_records, "power_655", max_val=55, num_balls=6)
        self.assertIn("core_pool", wheel)
        self.assertIn("tickets", wheel)
        self.assertEqual(len(wheel["tickets"]), 6)

    def test_legacy_strategy_shim_compatibility(self):
        # Check that legacy strategies module exports classes
        self.assertTrue(hasattr(legacy_strategies, "PredictModel"))
        self.assertTrue(hasattr(legacy_strategies, "FrequencyStrategy"))
        self.assertTrue(hasattr(legacy_strategies, "RandomModel"))
        self.assertTrue(hasattr(legacy_strategies, "NotRepeatStrategy"))
        self.assertTrue(hasattr(legacy_strategies, "PatternStrategy"))
        self.assertTrue(hasattr(legacy_strategies, "StrategyBacktester"))

        # Check that strategy module re-exports seamlessly via shim
        self.assertTrue(hasattr(strategy_shim, "PredictModel"))
        self.assertTrue(hasattr(strategy_shim, "FrequencyStrategy"))
        self.assertTrue(hasattr(strategy_shim, "RandomModel"))
        self.assertTrue(hasattr(strategy_shim, "NotRepeatStrategy"))
        self.assertTrue(hasattr(strategy_shim, "PatternStrategy"))
        self.assertTrue(hasattr(strategy_shim, "StrategyBacktester"))

        # Ensure types match
        self.assertIs(strategy_shim.PredictModel, legacy_strategies.PredictModel)
        self.assertIs(strategy_shim.FrequencyStrategy, legacy_strategies.FrequencyStrategy)

    def test_consensus_ensemble_js_mappings(self):
        js_path = Path(__file__).resolve().parents[3] / "docs" / "assets" / "js" / "consensus_ensemble.js"
        self.assertTrue(js_path.exists())
        js_content = js_path.read_text(encoding="utf-8")

        self.assertIn('"graph_pagerank"', js_content)
        self.assertIn('"state_space"', js_content)
        self.assertIn('share-2', js_content)
        self.assertIn('cpu', js_content)
        self.assertIn('sky', js_content)
        self.assertIn('amber', js_content)


if __name__ == "__main__":
    unittest.main()
