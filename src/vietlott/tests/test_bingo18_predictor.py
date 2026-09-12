import json
import unittest
from pathlib import Path

from vietlott.model.bingo18_predictor import (
    predict_bingo18_large_small,
    predict_bingo18_single_face,
    predict_bingo18_two_faces,
    predict_bingo18_target_sum,
    evaluate_bingo18_storm_trigger,
    generate_bingo18_prediction_hub,
    evaluate_bingo18_walk_forward_accuracy,
)


class TestBingo18Predictor(unittest.TestCase):
    def test_predict_bingo18_large_small_streak_logic(self):
        """Kiểm tra logic bám cầu bệt (streak < 4) và bẻ cầu đảo chiều (streak >= 4)."""
        # Test bám cầu bệt: 2 kỳ Lớn liên tiếp -> dự báo tiếp tục Lớn
        records_short = [
            {"id": "00001", "date": "2026-09-01", "result": [4, 5, 4], "total": 13, "large_small": "Lớn"},
            {"id": "00002", "date": "2026-09-01", "result": [5, 5, 4], "total": 14, "large_small": "Lớn"},
        ]
        p_short = predict_bingo18_large_small(records_short)
        self.assertEqual(p_short["predicted_choice"], "Lớn")
        self.assertIn("Bám Cầu Bệt", p_short["strategy_name"])
        self.assertTrue(50.0 <= p_short["confidence_pct"] <= 85.0)

        # Test bẻ cầu: 5 kỳ Lớn liên tiếp -> dự báo bẻ sang Nhỏ
        records_long = [
            {"id": f"{i:05d}", "date": "2026-09-01", "result": [5, 5, 4], "total": 14, "large_small": "Lớn"}
            for i in range(1, 6)
        ]
        p_long = predict_bingo18_large_small(records_long)
        self.assertEqual(p_long["predicted_choice"], "Nhỏ")
        self.assertIn("Bẻ Cầu", p_long["strategy_name"])
        self.assertGreaterEqual(p_long["confidence_pct"], 65.0)

    def test_predict_bingo18_elastic_boundary_bounce(self):
        """Kiểm tra phản ứng đàn hồi biên khi tổng cực thấp (<=6) hoặc cực cao (>=15)."""
        # Biên cực thấp: tổng 5 -> Lực đàn hồi kéo lên Lớn + lót Hòa
        records_low = [
            {"id": "00001", "date": "2026-09-01", "result": [4, 4, 4], "total": 12, "large_small": "Lớn"},
            {"id": "00002", "date": "2026-09-01", "result": [1, 2, 2], "total": 5, "large_small": "Nhỏ"},
        ]
        p_low = predict_bingo18_large_small(records_low)
        self.assertEqual(p_low["predicted_choice"], "Lớn")
        self.assertTrue(p_low.get("elastic_bounce_signal", False))
        self.assertIn("Đàn Hồi Biên", p_low["strategy_name"])
        self.assertIn("Hòa", p_low.get("hedge_recommendation", ""))

        # Biên cực cao: tổng 16 -> Lực đàn hồi kéo về Nhỏ + lót Hòa
        records_high = [
            {"id": "00001", "date": "2026-09-01", "result": [2, 2, 2], "total": 6, "large_small": "Nhỏ"},
            {"id": "00002", "date": "2026-09-01", "result": [5, 5, 6], "total": 16, "large_small": "Lớn"},
        ]
        p_high = predict_bingo18_large_small(records_high)
        self.assertEqual(p_high["predicted_choice"], "Nhỏ")
        self.assertTrue(p_high.get("elastic_bounce_signal", False))
        self.assertIn("Đàn Hồi Biên", p_high["strategy_name"])
        self.assertIn("Hòa", p_high.get("hedge_recommendation", ""))

    def test_predict_bingo18_tie_escape_rule(self):
        """Kiểm tra quy tắc thoát Hòa (75.2% không lặp lại Hòa sau khi vừa ra 10 hoặc 11)."""
        records_tie = [
            {"id": "00001", "date": "2026-09-01", "result": [4, 5, 4], "total": 13, "large_small": "Lớn"},
            {"id": "00002", "date": "2026-09-01", "result": [3, 4, 3], "total": 10, "large_small": "Hòa"},
        ]
        p_tie = predict_bingo18_large_small(records_tie)
        self.assertTrue(p_tie.get("tie_escape_signal", False))
        self.assertIn(p_tie["predicted_choice"], ["Lớn", "Nhỏ"])
        self.assertNotEqual(p_tie["predicted_choice"], "Hòa")

    def test_predict_bingo18_single_face(self):
        """Kiểm tra chọn 1 mặt xúc xắc Bạch Thủ hợp lệ trong 1..6."""
        records = [
            {"id": "00001", "date": "2026-09-01", "result": [1, 2, 3], "total": 6},
            {"id": "00002", "date": "2026-09-01", "result": [1, 5, 6], "total": 12},
            {"id": "00003", "date": "2026-09-01", "result": [2, 3, 5], "total": 10},
        ]
        face_pred = predict_bingo18_single_face(records)
        self.assertTrue(1 <= face_pred["best_face"] <= 6)
        self.assertTrue(40.0 <= face_pred["expected_hit_prob_pct"] <= 50.0)
        self.assertIn("rationale", face_pred)

    def test_predict_bingo18_two_faces(self):
        """Kiểm tra chọn cặp Song Thủ 2 mặt xúc xắc (+EV ~68-70%)."""
        records = [
            {"id": "00001", "date": "2026-09-01", "result": [1, 2, 3], "total": 6},
            {"id": "00002", "date": "2026-09-01", "result": [1, 5, 6], "total": 12},
            {"id": "00003", "date": "2026-09-01", "result": [2, 3, 5], "total": 10},
        ]
        pair_pred = predict_bingo18_two_faces(records)
        self.assertIn("best_pair", pair_pred)
        pair = pair_pred["best_pair"]
        self.assertEqual(len(pair), 2)
        self.assertNotEqual(pair[0], pair[1])
        self.assertTrue(all(1 <= x <= 6 for x in pair))
        self.assertTrue(60.0 <= pair_pred["expected_hit_prob_pct"] <= 75.0)
        self.assertIn("rationale", pair_pred)

    def test_predict_bingo18_target_sum(self):
        """Kiểm tra dự báo khoảng tổng Gaussian [8, 13] và tổng mục tiêu."""
        records = [
            {"id": "00001", "date": "2026-09-01", "result": [3, 4, 3], "total": 10},
            {"id": "00002", "date": "2026-09-01", "result": [4, 4, 3], "total": 11},
        ]
        sum_pred = predict_bingo18_target_sum(records)
        self.assertEqual(sum_pred["target_range"], [8, 13])
        self.assertTrue(8 <= sum_pred["best_single_sum"] <= 13)
        self.assertEqual(sum_pred["range_probability_pct"], 68.0)

    def test_evaluate_bingo18_storm_trigger(self):
        """Kiểm tra tín hiệu kích hoạt săn bão khi gap >= 70."""
        # Gap nhỏ -> không kích hoạt
        records_safe = [
            {"id": "00001", "date": "2026-09-01", "result": [3, 3, 3], "total": 9, "is_triple": True}
        ]
        for i in range(2, 20):
            records_safe.append({"id": f"{i:05d}", "date": "2026-09-01", "result": [1, 2, 4], "total": 7, "is_triple": False})

        trig_safe = evaluate_bingo18_storm_trigger(records_safe)
        self.assertFalse(trig_safe["is_hunting_active"])

        # Gap lớn (80 kỳ) -> kích hoạt săn bão
        records_hot = [
            {"id": "00001", "date": "2026-09-01", "result": [3, 3, 3], "total": 9, "is_triple": True}
        ]
        for i in range(2, 85):
            records_hot.append({"id": f"{i:05d}", "date": "2026-09-01", "result": [1, 2, 4], "total": 7, "is_triple": False})

        trig_hot = evaluate_bingo18_storm_trigger(records_hot)
        self.assertTrue(trig_hot["is_hunting_active"])
        self.assertIn("NUÔI BÃO", trig_hot["action_recommendation"])

    def test_generate_bingo18_prediction_hub(self):
        """Kiểm tra hợp nhất đầy đủ các chiến lược dự đoán."""
        records = [
            {"id": "00001", "date": "2026-09-01", "result": [2, 3, 5], "total": 10, "large_small": "Nhỏ"},
            {"id": "00002", "date": "2026-09-01", "result": [4, 5, 4], "total": 13, "large_small": "Lớn"},
        ]
        hub = generate_bingo18_prediction_hub(records)
        self.assertIn("large_small_prediction", hub)
        self.assertIn("single_face_prediction", hub)
        self.assertIn("two_faces_prediction", hub)
        self.assertIn("target_sum_prediction", hub)
        self.assertIn("storm_trigger", hub)
        self.assertIn("target_draw_id", hub)

    def test_evaluate_bingo18_walk_forward_accuracy_real_data(self):
        """Kiểm tra kiểm định Walk-Forward 100 kỳ trên dữ liệu thật của repo."""
        data_file = Path("data/bingo18.jsonl")
        if not data_file.exists():
            self.skipTest("data/bingo18.jsonl not present")

        records = []
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        self.assertGreater(len(records), 500)
        eval_res = evaluate_bingo18_walk_forward_accuracy(records, num_draws=100)
        self.assertEqual(eval_res["evaluated_draws"], 100)
        self.assertTrue(20.0 <= eval_res["large_small_accuracy_pct"] <= 80.0)
        self.assertTrue(35.0 <= eval_res["single_face_hit_rate_pct"] <= 60.0)
        self.assertTrue(55.0 <= eval_res["target_range_hit_rate_pct"] <= 85.0)
        self.assertIn("two_faces_hit_rate_pct", eval_res)
        self.assertTrue(55.0 <= eval_res["two_faces_hit_rate_pct"] <= 80.0)


if __name__ == "__main__":
    unittest.main()

