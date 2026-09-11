import json
import unittest
from pathlib import Path

from vietlott.render_web_data import process_bingo18


class TestBingo18PredictionIntegration(unittest.TestCase):
    def test_process_bingo18_outputs_prediction_hub(self):
        """Kiểm tra process_bingo18 xuất đầy đủ trường prediction_hub và two_faces_prediction."""
        records = [
            {"id": "0185800", "date": "2026-09-09", "result": [2, 3, 5], "total": 10, "large_small": "Hòa"},
            {"id": "0185801", "date": "2026-09-09", "result": [4, 4, 4], "total": 12, "large_small": "Lớn", "is_triple": True},
            {"id": "0185802", "date": "2026-09-09", "result": [6, 5, 2], "total": 13, "large_small": "Lớn"},
        ]

        res = process_bingo18(records)
        self.assertIn("prediction_hub", res)
        pred = res["prediction_hub"]
        self.assertIn("large_small_prediction", pred)
        self.assertIn("single_face_prediction", pred)
        self.assertIn("two_faces_prediction", pred)
        self.assertIn("target_sum_prediction", pred)
        self.assertIn("storm_trigger", pred)
        self.assertIn("target_draw_id", pred)

        self.assertIn(pred["large_small_prediction"]["predicted_choice"], ["Lớn", "Nhỏ"])
        self.assertTrue(1 <= pred["single_face_prediction"]["best_face"] <= 6)
        self.assertEqual(len(pred["two_faces_prediction"]["best_pair"]), 2)
        self.assertEqual(pred["target_sum_prediction"]["target_range"], [8, 13])

    def test_process_bingo18_real_data_has_valid_prediction_hub(self):
        """Kiểm tra prediction_hub với file dữ liệu thật."""
        p = Path("data/bingo18.jsonl")
        if not p.exists():
            self.skipTest("data/bingo18.jsonl not present")

        records = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        res = process_bingo18(records)
        pred = res["prediction_hub"]
        self.assertGreaterEqual(pred["large_small_prediction"]["confidence_pct"], 50.0)
        self.assertGreaterEqual(pred["single_face_prediction"]["expected_hit_prob_pct"], 40.0)
        self.assertIn("two_faces_prediction", pred)
        self.assertGreaterEqual(pred["two_faces_prediction"]["expected_hit_prob_pct"], 60.0)


if __name__ == "__main__":
    unittest.main()

