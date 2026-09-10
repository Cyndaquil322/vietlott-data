"""
Integration tests for Wavelet Engine in render_web_data.py (Task 2 of Phase 2).
Verifies:
- Daubechies Wavelet & Hann Spectral hybrid model integration.
- Model metadata, rationale, and trained_hyperparameters.
- Valid numerical fourier scores (no NaN/Inf, > 0).
- Backwards compatibility with the existing consensus schema.
- Zero mock/fake data principles across real and synthetic lottery records.
"""

import math
import random
import unittest
from pathlib import Path
from typing import Dict, List

from vietlott.render_web_data import (
    calculate_multi_model_consensus_and_backtest,
    read_jsonl,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _generate_synthetic_draws(
    count: int, max_val: int, num_balls: int, is_two_matrix: bool = False
) -> List[Dict]:
    """Generates synthetic draw records for deterministic testing without external files."""
    rng = random.Random(42)
    records = []
    for i in range(count):
        balls = sorted(rng.sample(range(1, max_val + 1), num_balls))
        if is_two_matrix:
            balls.append(rng.randint(1, 12))
        records.append({
            "id": f"#{1000 + i}",
            "date": f"2026-01-{(i % 28) + 1:02d}",
            "result": balls,
        })
    return records


class TestWaveletIntegration(unittest.TestCase):
    """Test suite for Wavelet Engine integration into consensus pipeline."""

    def setUp(self):
        p655_path = DATA_DIR / "power655.jsonl"
        p535_path = DATA_DIR / "power535.jsonl"

        if p655_path.exists():
            self.records_655 = read_jsonl(p655_path)[-60:]
        else:
            self.records_655 = _generate_synthetic_draws(60, 55, 6)

        if p535_path.exists():
            self.records_535 = read_jsonl(p535_path)[-60:]
        else:
            self.records_535 = _generate_synthetic_draws(60, 35, 5, is_two_matrix=True)

    def test_wavelet_model_metadata_and_naming(self):
        """Verify models_info['fourier'] is upgraded to Wavelet & Hann Spectral."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_655,
            product_key="power_655",
            max_val=55,
            num_balls=6,
            is_two_matrix=False,
            num_draws=15,
            display_draws=5,
        )

        # Leaderboard metadata
        fourier_entry = next((m for m in res["leaderboard"] if m["id"] == "fourier"), None)
        self.assertIsNotNone(fourier_entry, "Model 'fourier' missing from leaderboard")
        self.assertIn("Wavelet", fourier_entry["name"])
        self.assertEqual(fourier_entry["name"], "Daubechies Wavelet & Hann Spectral")
        self.assertIn("Daubechies DWT", fourier_entry["desc"])

        # Model explanations metadata & rationale
        explanations = res["model_explanations"]
        self.assertIn("fourier", explanations)
        fourier_exp = explanations["fourier"]
        self.assertIn("Wavelet", fourier_exp["name"])
        self.assertEqual(fourier_exp["name"], "Daubechies Wavelet & Hann Spectral")
        self.assertIn("Phân rã sóng con Daubechies DWT và phổ Fourier ghi nhận các bóng", fourier_exp["rationale"])
        self.assertIn("đang hội tụ năng lượng dao động cực đại.", fourier_exp["rationale"])

        # If models_info exposed in result, check directly
        if "models_info" in res:
            self.assertIn("Wavelet", res["models_info"]["fourier"]["name"])
            self.assertEqual(
                res["models_info"]["fourier"]["desc"],
                "Phân rã đa sóng nhỏ Daubechies DWT kết hợp cộng hưởng phổ lọc nhiễu Hann.",
            )

    def test_wavelet_hyperparameters_in_training_report(self):
        """Verify training_report['trained_hyperparameters'] includes wavelet configurations."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_655,
            product_key="power_655",
            max_val=55,
            num_balls=6,
            is_two_matrix=False,
            num_draws=15,
            display_draws=5,
        )

        self.assertIn("training_report", res)
        report = res["training_report"]
        self.assertIn("trained_hyperparameters", report)
        params = report["trained_hyperparameters"]

        self.assertIn("wavelet_family", params)
        self.assertEqual(params["wavelet_family"], "Daubechies-4 (db4)")
        self.assertIn("wavelet_levels", params)
        self.assertEqual(params["wavelet_levels"], 2)

    def test_wavelet_spectral_scores_numerical_validity(self):
        """Verify fourier scores in leaderboard and consensus breakdown are valid numbers."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_655,
            product_key="power_655",
            max_val=55,
            num_balls=6,
            is_two_matrix=False,
            num_draws=15,
            display_draws=5,
        )

        fourier_entry = next(m for m in res["leaderboard"] if m["id"] == "fourier")
        avg_hits = fourier_entry["avg_hits"]
        weight_pct = fourier_entry["weight_pct"]

        self.assertIsInstance(avg_hits, (int, float))
        self.assertFalse(math.isnan(avg_hits))
        self.assertFalse(math.isinf(avg_hits))
        self.assertGreater(avg_hits, 0.0, "Average hits for Wavelet/Fourier model should be > 0")

        self.assertIsInstance(weight_pct, (int, float))
        self.assertFalse(math.isnan(weight_pct))
        self.assertFalse(math.isinf(weight_pct))
        self.assertGreater(weight_pct, 0.0, "Dynamic weight for Wavelet/Fourier model should be > 0")

        # Check breakdown scores across consensus balls
        top_balls = res["top_consensus_balls"]
        self.assertGreater(len(top_balls), 0)
        fourier_scores = [b["breakdown"]["fourier"] for b in top_balls]
        for sc in fourier_scores:
            self.assertIsInstance(sc, (int, float))
            self.assertFalse(math.isnan(sc))
            self.assertFalse(math.isinf(sc))
            self.assertGreaterEqual(sc, 0.0)

        self.assertTrue(any(sc > 0 for sc in fourier_scores), "At least one candidate should have fourier score > 0")

    def test_wavelet_power535_integration(self):
        """Verify integration works correctly on Power 5/35 (35 numbers, 5 balls)."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_535,
            product_key="power_535",
            max_val=35,
            num_balls=5,
            is_two_matrix=True,
            num_draws=15,
            display_draws=5,
        )

        fourier_entry = next(m for m in res["leaderboard"] if m["id"] == "fourier")
        self.assertIn("Wavelet", fourier_entry["name"])
        self.assertEqual(res["training_report"]["trained_hyperparameters"]["wavelet_family"], "Daubechies-4 (db4)")
        self.assertEqual(res["training_report"]["trained_hyperparameters"]["wavelet_levels"], 2)

    def test_schema_backwards_compatibility(self):
        """Verify full schema structure remains intact without breaking changes."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_655,
            product_key="power_655",
            max_val=55,
            num_balls=6,
            is_two_matrix=False,
            num_draws=15,
            display_draws=5,
        )

        required_root_keys = [
            "next_draw_id",
            "evaluated_draws_count",
            "leaderboard",
            "top_consensus_balls",
            "model_explanations",
            "training_report",
            "tickets",
            "history_walk_forward",
        ]
        for key in required_root_keys:
            self.assertIn(key, res, f"Missing root key '{key}'")

        # Leaderboard should have 7 entries: consensus + 5 models + baseline_random
        model_ids = [m["id"] for m in res["leaderboard"]]
        self.assertIn("consensus", model_ids)
        self.assertIn("markov", model_ids)
        self.assertIn("hazard", model_ids)
        self.assertIn("decay", model_ids)
        self.assertIn("bac_nho", model_ids)
        self.assertIn("fourier", model_ids)
        self.assertIn("baseline_random", model_ids)


if __name__ == "__main__":
    unittest.main()
