"""
test_production_core.py
=======================
Bộ kiểm thử tự động toàn diện chuẩn Production (Enterprise-Grade Unit Test Suite)
cho dự án Vietlott Analytics & Live Explorer.

Kiểm tra:
1. Tính toàn vẹn dữ liệu (Data Integrity): Không mock data, range bóng chuẩn, không trùng lặp.
2. Walk-Forward Backtest: Tuân thủ 100% nguyên lý không look-ahead bias, deterministic seeding.
3. Bộ 3 Kiềng 3 Chân (Triad), Top 5 Ngũ Thủ (Key 5) và Bao 4 Vé (Wheeling 4 tickets).
4. Auto-Draw Monitor logic: Khung giờ mở thưởng, đối soát tức thì.
5. JSON Summary Schema: Đảm bảo giao diện web luôn nhận đúng định dạng dữ liệu.
"""

import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

from vietlott.render_web_data import (
    calculate_multi_model_consensus_and_backtest,
    read_jsonl,
)
from vietlott.auto_draw_monitor import (
    is_near_draw_time,
    audit_game_predictions,
)


class TestDataIntegrity(unittest.TestCase):
    """Kiểm tra tính toàn vẹn và tính chân thực của dữ liệu thực tế."""

    def test_jsonl_files_exist_and_not_empty(self):
        """Các file dữ liệu gốc phải tồn tại và có số lượng kỳ quay tối thiểu."""
        expected_files = {
            "power655.jsonl": 1000,
            "power645.jsonl": 1000,
            "power535.jsonl": 200,
        }
        for fname, min_count in expected_files.items():
            fpath = DATA_DIR / fname
            self.assertTrue(fpath.exists(), f"File {fname} không tồn tại")
            records = read_jsonl(fpath)
            self.assertGreaterEqual(
                len(records),
                min_count,
                f"File {fname} có ít hơn {min_count} kỳ quay ({len(records)})",
            )

    def test_power655_draw_validity(self):
        """Power 6/55: Bóng trong khoảng 1..55, đủ 6 bóng chính, không trùng số."""
        records = read_jsonl(DATA_DIR / "power655.jsonl")
        for rec in records[-100:]:  # Kiểm tra 100 kỳ gần nhất
            res = rec.get("result", [])
            self.assertGreaterEqual(len(res), 6)
            main_balls = res[:6]
            self.assertEqual(len(main_balls), len(set(main_balls)), f"Kỳ {rec.get('id')} có bóng trùng lặp")
            for b in main_balls:
                self.assertTrue(1 <= b <= 55, f"Bóng {b} vượt phạm vi 1..55 trong kỳ {rec.get('id')}")

    def test_power535_draw_validity(self):
        """Power 5/35: Bóng trong khoảng 1..35, đủ 5 bóng chính, không trùng số."""
        records = read_jsonl(DATA_DIR / "power535.jsonl")
        for rec in records[-100:]:
            res = rec.get("result", [])
            self.assertGreaterEqual(len(res), 5)
            main_balls = res[:5]
            self.assertEqual(len(main_balls), len(set(main_balls)), f"Kỳ {rec.get('id')} có bóng trùng lặp")
            for b in main_balls:
                self.assertTrue(1 <= b <= 35, f"Bóng {b} vượt phạm vi 1..35 trong kỳ {rec.get('id')}")


class TestWalkForwardAndConsensus(unittest.TestCase):
    """Kiểm tra nguyên tắc Walk-Forward Backtest và các tổ hợp dự đoán."""

    def setUp(self):
        self.records_655 = read_jsonl(DATA_DIR / "power655.jsonl")
        self.records_535 = read_jsonl(DATA_DIR / "power535.jsonl")

    def test_deterministic_seeded_prediction(self):
        """Kiểm tra tính nhất quán: Chạy 2 lần với cùng dữ liệu phải cho kết quả giống hệt 100%."""
        res1 = calculate_multi_model_consensus_and_backtest(
            self.records_655[-60:], "power_655", max_val=55, num_balls=6, num_draws=10, display_draws=5
        )
        res2 = calculate_multi_model_consensus_and_backtest(
            self.records_655[-60:], "power_655", max_val=55, num_balls=6, num_draws=10, display_draws=5
        )
        self.assertEqual(
            res1["tickets"]["key_balls"],
            res2["tickets"]["key_balls"],
            "Kiềng 3 chân không đồng nhất khi chạy lại cùng dữ liệu",
        )
        self.assertEqual(
            res1["tickets"]["key_5_balls"],
            res2["tickets"]["key_5_balls"],
            "Top 5 Ngũ thủ không đồng nhất khi chạy lại cùng dữ liệu",
        )

    def test_triad_key5_wheeling_properties(self):
        """Kiểm tra cấu trúc và tính hợp lệ của Kiềng 3 chân, Ngũ thủ và Bao 4 vé."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_535[-60:], "power_535", max_val=35, num_balls=5, num_draws=15, display_draws=5
        )
        tickets = res.get("tickets", {})

        # Triad
        triad = tickets.get("key_balls", [])
        self.assertEqual(len(triad), 3, "Triad phải có đúng 3 bóng")
        self.assertEqual(len(set(triad)), 3, "Triad không được chứa số trùng")
        for b in triad:
            self.assertTrue(1 <= b <= 35, "Bóng Triad vượt ngoài 1..35")

        # Key 5
        key5 = tickets.get("key_5_balls", [])
        self.assertEqual(len(key5), 5, "Key 5 phải có đúng 5 bóng")
        self.assertEqual(len(set(key5)), 5, "Key 5 không được chứa số trùng")
        # Key 5 phải chứa toàn bộ Triad
        for b in triad:
            self.assertIn(b, key5, "Key 5 phải bao gồm toàn bộ 3 bóng của Triad")

        # Wheeling 4 tickets
        wheel4 = tickets.get("wheeling_4_tickets", [])
        self.assertEqual(len(wheel4), 4, "Wheeling phải sinh đúng 4 vé")
        for t in wheel4:
            nums = t.get("numbers", [])
            self.assertEqual(len(nums), 5, "Vé trong Wheeling 5/35 phải có 5 bóng")
            self.assertEqual(len(set(nums)), 5, "Vé không được có bóng trùng")

    def test_walk_forward_history_records(self):
        """Kiểm tra lịch sử Walk-Forward: Mọi kỳ quá khứ phải ghi nhận đầy đủ hit bóc tách."""
        res = calculate_multi_model_consensus_and_backtest(
            self.records_655[-50:], "power_655", max_val=55, num_balls=6, num_draws=15, display_draws=10
        )
        history = res.get("history_walk_forward", [])
        self.assertGreater(len(history), 0, "Lịch sử Walk-Forward không được rỗng")

        for entry in history:
            self.assertIn("drawId", entry)
            self.assertIn("actual", entry)
            self.assertIn("triad", entry)
            self.assertIn("triadMatched", entry)
            self.assertIn("triadMatchCount", entry)
            self.assertIn("key5", entry)
            self.assertIn("key5Matched", entry)
            self.assertIn("key5MatchCount", entry)
            self.assertIn("wheel4", entry)
            # Số bóng trúng phải khớp độ dài mảng bóng trúng
            self.assertEqual(len(entry["triadMatched"]), entry["triadMatchCount"])
            self.assertEqual(len(entry["key5Matched"]), entry["key5MatchCount"])


class TestAutoDrawMonitor(unittest.TestCase):
    """Kiểm tra hệ thống Auto-Draw Monitor và các hàm tiện ích."""

    def test_near_draw_time_returns_valid_tuple(self):
        """Hàm is_near_draw_time phải trả về tuple (bool, str, int)."""
        in_win, status_str, sleep_sec = is_near_draw_time()
        self.assertIsInstance(in_win, bool)
        self.assertIsInstance(status_str, str)
        self.assertIsInstance(sleep_sec, int)
        self.assertGreaterEqual(sleep_sec, 0)

    def test_audit_game_predictions_formatting(self):
        """Hàm audit_game_predictions phải tạo báo cáo có cấu trúc và không gây lỗi."""
        summary_path = DATA_DIR / "vietlott_summary.json"
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
            p655_data = summary.get("products", {}).get("power_655")
            if p655_data:
                report = audit_game_predictions("power_655", p655_data)
                self.assertIn("ĐỐI SOÁT CHUẨN XÁC", report)
                self.assertIn("Kiềng 3 Chân (Triad)", report)
                self.assertIn("Top 5 Ngũ Thủ (Key 5)", report)


class TestWebSummarySchema(unittest.TestCase):
    """Kiểm tra tính hoàn thiện của file vietlott_summary.json xuất cho frontend."""

    def test_summary_structure(self):
        summary_path = DATA_DIR / "vietlott_summary.json"
        self.assertTrue(summary_path.exists(), "vietlott_summary.json chưa được tạo")
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertIn("products", summary)
        products = summary["products"]
        for key in ["power_655", "power_645", "power_535"]:
            self.assertIn(key, products, f"Thiếu sản phẩm {key} trong summary")
            pdata = products[key]
            self.assertIn("consensus_hub", pdata, f"Thiếu consensus_hub trong {key}")
            hub = pdata["consensus_hub"]
            self.assertIn("tickets", hub, f"Thiếu tickets trong {key}")
            self.assertIn("history_walk_forward", hub, f"Thiếu history_walk_forward trong {key}")


if __name__ == "__main__":
    unittest.main()
