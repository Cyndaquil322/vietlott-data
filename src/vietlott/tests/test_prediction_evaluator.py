"""
Unit tests for vietlott.model.prediction_evaluator
Tests prize evaluations, Bao 7, and Banker Wheeling for Power 6/55, Mega 6/45, and Power 5/35.
"""

import pytest
from vietlott.model.prediction_evaluator import (
    evaluate_ticket,
    evaluate_bao7,
    evaluate_banker_wheeling,
)


class TestPower655Evaluation:
    """Tests for Power 6/55 prize evaluation rules."""

    actual = [7, 24, 31, 43, 47, 54]
    special = 22

    def test_jackpot_1(self):
        ticket = [7, 24, 31, 43, 47, 54]
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 6
        assert res["is_special_hit"] is False
        assert res["prize_tier"] == "Jackpot 1"
        assert res["prize_vnd"] == 30_000_000_000
        assert res["matched_balls"] == [7, 24, 31, 43, 47, 54]

    def test_jackpot_2(self):
        ticket = [7, 24, 31, 43, 47, 22]
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 5
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Jackpot 2"
        assert res["prize_vnd"] == 3_000_000_000
        assert res["matched_balls"] == [7, 24, 31, 43, 47]

    def test_giai_nhat(self):
        ticket = [7, 24, 31, 43, 47, 1]  # 5 hits, no special
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 5
        assert res["is_special_hit"] is False
        assert res["prize_tier"] == "Giải Nhất"
        assert res["prize_vnd"] == 40_000_000

    def test_giai_nhi(self):
        ticket = [7, 24, 31, 43, 1, 2]  # 4 hits
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 4
        assert res["prize_tier"] == "Giải Nhì"
        assert res["prize_vnd"] == 500_000

    def test_giai_nhi_with_special(self):
        # 4 hits + special ball does not upgrade to JP2; remains Giải Nhì in Power 6/55
        ticket = [7, 24, 31, 43, 22, 2]
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 4
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Nhì"
        assert res["prize_vnd"] == 500_000

    def test_giai_ba(self):
        ticket = [7, 24, 31, 1, 2, 3]  # 3 hits
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 3
        assert res["prize_tier"] == "Giải Ba"
        assert res["prize_vnd"] == 50_000

    def test_no_prize(self):
        ticket = [7, 24, 1, 2, 3, 4]  # 2 hits
        res = evaluate_ticket("power655", ticket, self.actual, self.special)
        assert res["hits"] == 2
        assert res["prize_tier"] == "Không trúng"
        assert res["prize_vnd"] == 0

    def test_implicit_special_ball_in_actual_result(self):
        # actual_result contains 7 balls: first 6 main, 7th is special
        full_actual = [7, 24, 31, 43, 47, 54, 22]
        ticket = [7, 24, 31, 43, 47, 22]
        res = evaluate_ticket("power655", ticket, full_actual, special_ball=None)
        assert res["hits"] == 5
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Jackpot 2"


class TestMega645Evaluation:
    """Tests for Mega 6/45 prize evaluation rules."""

    actual = [14, 18, 20, 21, 26, 27]

    def test_jackpot(self):
        ticket = [14, 18, 20, 21, 26, 27]
        res = evaluate_ticket("power645", ticket, self.actual)
        assert res["hits"] == 6
        assert res["prize_tier"] == "Jackpot"
        assert res["prize_vnd"] == 12_000_000_000

    def test_giai_nhat(self):
        ticket = [14, 18, 20, 21, 26, 1]
        res = evaluate_ticket("power645", ticket, self.actual)
        assert res["hits"] == 5
        assert res["prize_tier"] == "Giải Nhất"
        assert res["prize_vnd"] == 10_000_000

    def test_giai_nhi(self):
        ticket = [14, 18, 20, 21, 1, 2]
        res = evaluate_ticket("power645", ticket, self.actual)
        assert res["hits"] == 4
        assert res["prize_tier"] == "Giải Nhì"
        assert res["prize_vnd"] == 300_000

    def test_giai_ba(self):
        ticket = [14, 18, 20, 1, 2, 3]
        res = evaluate_ticket("power645", ticket, self.actual)
        assert res["hits"] == 3
        assert res["prize_tier"] == "Giải Ba"
        assert res["prize_vnd"] == 30_000

    def test_no_prize(self):
        ticket = [14, 18, 1, 2, 3, 4]
        res = evaluate_ticket("power645", ticket, self.actual)
        assert res["hits"] == 2
        assert res["prize_tier"] == "Không trúng"
        assert res["prize_vnd"] == 0


class TestPower535Evaluation:
    """Tests for Power 5/35 (Lotto 5/35) prize evaluation according to Vietlott rules."""

    actual = [5, 12, 18, 25, 33]
    special = 9

    def test_giai_doc_dac(self):
        # 5 main balls + 1 special ball
        ticket = [5, 12, 18, 25, 33, 9]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 5
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Độc Đắc"
        assert res["prize_vnd"] == 6_000_000_000

    def test_giai_nhat(self):
        # 5 main balls, no special ball
        ticket = [5, 12, 18, 25, 33]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 5
        assert res["is_special_hit"] is False
        assert res["prize_tier"] == "Giải Nhất"
        assert res["prize_vnd"] == 10_000_000

    def test_giai_nhi(self):
        # 4 main balls + special
        ticket = [5, 12, 18, 25, 9]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 4
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Nhì"
        assert res["prize_vnd"] == 5_000_000

    def test_giai_ba(self):
        # 4 main balls without special
        ticket = [5, 12, 18, 25, 1]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 4
        assert res["is_special_hit"] is False
        assert res["prize_tier"] == "Giải Ba"
        assert res["prize_vnd"] == 500_000

    def test_giai_tu(self):
        # 3 main balls + special
        ticket = [5, 12, 18, 9, 1]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 3
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Tư"
        assert res["prize_vnd"] == 100_000

    def test_giai_nam(self):
        # 3 main balls without special
        ticket = [5, 12, 18, 1, 2]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 3
        assert res["is_special_hit"] is False
        assert res["prize_tier"] == "Giải Năm"
        assert res["prize_vnd"] == 30_000

    def test_giai_khuyen_khich_2_hits(self):
        # 2 main balls + special
        ticket = [5, 12, 9, 1, 2]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 2
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Khuyến Khích"
        assert res["prize_vnd"] == 10_000

    def test_giai_khuyen_khich_0_hits(self):
        # 0 main balls + special
        ticket = [1, 2, 3, 4, 9]
        res = evaluate_ticket("power535", ticket, self.actual, self.special)
        assert res["hits"] == 0
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Khuyến Khích"
        assert res["prize_vnd"] == 10_000

    def test_power535_implicit_special(self):
        # actual_result with 6 balls: first 5 main, 6th special
        full_actual = [5, 12, 18, 25, 33, 9]
        ticket = [5, 12, 18, 25, 33, 9]
        res = evaluate_ticket("power535", ticket, full_actual)
        assert res["hits"] == 5
        assert res["is_special_hit"] is True
        assert res["prize_tier"] == "Giải Độc Đắc"


class TestGameTypeAliases:
    """Tests that alias strings for game_type resolve properly."""

    actual = [7, 24, 31, 43, 47, 54]

    def test_game_aliases(self):
        for gt in ["power655", "power_655", "Power 6/55"]:
            res = evaluate_ticket(gt, [7, 24, 31, 1, 2, 3], self.actual)
            assert res["prize_tier"] == "Giải Ba"
            assert res["prize_vnd"] == 50_000

        for gt in ["power645", "power_645", "mega645", "mega_645", "Mega 6/45"]:
            res = evaluate_ticket(gt, [7, 24, 31, 1, 2, 3], self.actual)
            assert res["prize_tier"] == "Giải Ba"
            assert res["prize_vnd"] == 30_000


class TestBao7Evaluation:
    """Tests for evaluate_bao7."""

    actual = [7, 24, 31, 43, 47, 54]

    def test_bao7_3_hits_power655(self):
        # Septet with 3 winning numbers -> 4 winning sub-tickets of 3 hits
        res = evaluate_bao7("power655", [7, 24, 31, 1, 2, 3, 4], self.actual)
        assert res["hits"] == 3
        assert res["matched_balls"] == [7, 24, 31]
        assert res["winning_combinations_count"] == 4
        assert res["prize_vnd"] == 4 * 50_000  # 200,000 VND
        assert res["cost_vnd"] == 70_000
        assert len(res["sub_tickets"]) == 7

    def test_bao7_4_hits_power655(self):
        # Septet with 4 winning numbers -> 3 sub-tickets with 4 hits + 4 sub-tickets with 3 hits
        # Total prize = 3 * 500,000 + 4 * 50,000 = 1,700,000 VND
        res = evaluate_bao7("power655", [7, 24, 31, 43, 1, 2, 3], self.actual)
        assert res["hits"] == 4
        assert res["winning_combinations_count"] == 7
        assert res["prize_vnd"] == 3 * 500_000 + 4 * 50_000

    def test_bao7_0_hits(self):
        res = evaluate_bao7("power655", [1, 2, 3, 4, 5, 6, 8], self.actual)
        assert res["hits"] == 0
        assert res["winning_combinations_count"] == 0
        assert res["prize_vnd"] == 0

    def test_bao6_power535(self):
        # 6 numbers for 5/35: creates 6 combinations of 5 balls
        res = evaluate_bao7("power535", [7, 24, 31, 1, 2, 3], [7, 24, 31, 10, 11], special_ball=9)
        assert res["hits"] == 3
        assert res["matched_balls"] == [7, 24, 31]
        assert len(res["sub_tickets"]) == 6
        assert res["cost_vnd"] == 60_000


class TestBankerWheelingEvaluation:
    """Tests for evaluate_banker_wheeling."""

    actual = [7, 24, 31, 43, 47, 54]
    special = 22

    def test_banker_wheeling_dicts(self):
        tickets = [
            {"id": "t1", "numbers": [7, 24, 31, 1, 2, 3]},   # 3 hits -> 50k
            {"id": "t2", "numbers": [7, 24, 31, 43, 1, 2]},  # 4 hits -> 500k
            {"id": "t3", "numbers": [7, 1, 2, 3, 4, 5]},     # 1 hit -> 0
        ]
        res = evaluate_banker_wheeling("power655", tickets, self.actual, self.special)
        assert res["tickets_count"] == 3
        assert res["cost_vnd"] == 30_000
        assert res["best_hits"] == 4
        assert res["winning_tickets_count"] == 2
        assert res["total_prize_vnd"] == 550_000
        assert len(res["evaluated_tickets"]) == 3

    def test_banker_wheeling_raw_lists(self):
        tickets = [
            [7, 24, 31, 1, 2, 3],
            [1, 2, 3, 4, 5, 6],
        ]
        res = evaluate_banker_wheeling("power655", tickets, self.actual)
        assert res["tickets_count"] == 2
        assert res["best_hits"] == 3
        assert res["winning_tickets_count"] == 1
        assert res["total_prize_vnd"] == 50_000

    def test_banker_wheeling_empty(self):
        res = evaluate_banker_wheeling("power655", [], self.actual)
        assert res["tickets_count"] == 0
        assert res["cost_vnd"] == 0
        assert res["best_hits"] == 0
        assert res["winning_tickets_count"] == 0
        assert res["total_prize_vnd"] == 0
        assert res["evaluated_tickets"] == []
