"""
Module: prediction_evaluator.py
Bộ máy chấm điểm & tính giải thưởng chuẩn Vietlott theo quy chế mở thưởng chính thức.
Hỗ trợ Power 6/55, Mega 6/45 và Power 5/35 (Lotto 5/35), bao gồm vé đơn, Bao 7/Bao 6 và dàn Banker Wheeling.

100% Zero Mock Data - Tuân thủ nguyên tắc trung thực toán học và tính toàn vẹn dữ liệu.
"""

import itertools
from typing import Any, Dict, List, Optional, Union


def _normalize_game_type(game_type: str) -> str:
    """Chuẩn hóa mã sản phẩm xổ số Vietlott."""
    cleaned = game_type.lower().replace("_", "").replace("-", "").replace(" ", "").replace("/", "")
    if "655" in cleaned:
        return "power655"
    if "645" in cleaned:
        return "power645"
    if "535" in cleaned:
        return "power535"
    return cleaned


def evaluate_ticket(
    game_type: str,
    ticket_numbers: List[int],
    actual_result: List[int],
    special_ball: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Chấm điểm 1 vé dự thưởng đơn so với kết quả mở thưởng thực tế.

    Args:
        game_type: "power655", "power645", "power535" (hoặc các alias tương đương).
        ticket_numbers: Dãy số trên vé (6 số cho 6/55, 6/45; 5 hoặc 6 số cho 5/35).
        actual_result: Kết quả mở thưởng chính (hoặc kèm bóng đặc biệt ở cuối).
        special_ball: Bóng đặc biệt (nếu có, hoặc trích xuất từ actual_result).

    Returns:
        Dict chứa:
            - numbers: Dãy số dự thưởng ban đầu.
            - hits: Số bóng chính trùng khớp.
            - matched_balls: Danh sách các bóng chính trúng thưởng (đã sort).
            - is_special_hit: True nếu trúng bóng đặc biệt.
            - prize_tier: Tên hạng giải (Jackpot 1, Jackpot 2, Giải Nhất, v.v.).
            - prize_vnd: Giá trị giải thưởng quy đổi (VNĐ).
    """
    norm_game = _normalize_game_type(game_type)

    # Tách bóng chính và bóng đặc biệt từ actual_result nếu chưa truyền special_ball
    actual_main = list(actual_result)
    actual_special = special_ball

    if norm_game == "power655":
        if actual_special is None and len(actual_main) >= 7:
            actual_special = actual_main[6]
            actual_main = actual_main[:6]
        elif len(actual_main) > 6:
            actual_main = actual_main[:6]
    elif norm_game == "power535":
        if actual_special is None and len(actual_main) >= 6:
            actual_special = actual_main[5]
            actual_main = actual_main[:5]
        elif len(actual_main) > 5:
            actual_main = actual_main[:5]
    elif norm_game == "power645":
        actual_special = None
        if len(actual_main) > 6:
            actual_main = actual_main[:6]

    # Khớp bóng chính
    actual_set = set(actual_main)
    matched = sorted(list(set(ticket_numbers) & actual_set))
    hits = len(matched)

    # Kiểm tra bóng đặc biệt
    special_hit = bool(actual_special is not None and actual_special in ticket_numbers)

    prize_tier = "Không trúng"
    prize_vnd = 0

    if norm_game == "power655":
        # Cơ cấu giải Power 6/55
        if hits == 6:
            prize_tier = "Jackpot 1"
            prize_vnd = 30_000_000_000
        elif hits == 5 and special_hit:
            prize_tier = "Jackpot 2"
            prize_vnd = 3_000_000_000
        elif hits == 5:
            prize_tier = "Giải Nhất"
            prize_vnd = 40_000_000
        elif hits == 4:
            prize_tier = "Giải Nhì"
            prize_vnd = 500_000
        elif hits == 3:
            prize_tier = "Giải Ba"
            prize_vnd = 50_000

    elif norm_game == "power645":
        # Cơ cấu giải Mega 6/45 (Không có bóng đặc biệt)
        if hits == 6:
            prize_tier = "Jackpot"
            prize_vnd = 12_000_000_000
        elif hits == 5:
            prize_tier = "Giải Nhất"
            prize_vnd = 10_000_000
        elif hits == 4:
            prize_tier = "Giải Nhì"
            prize_vnd = 300_000
        elif hits == 3:
            prize_tier = "Giải Ba"
            prize_vnd = 30_000

    elif norm_game == "power535":
        # Cơ cấu giải Lotto 5/35 (Theo chuẩn quy định Vietlott trong VIETLOTT_GAME_RULES.md)
        if hits == 5 and special_hit:
            prize_tier = "Giải Độc Đắc"
            prize_vnd = 6_000_000_000
        elif hits == 5:
            prize_tier = "Giải Nhất"
            prize_vnd = 10_000_000
        elif hits == 4 and special_hit:
            prize_tier = "Giải Nhì"
            prize_vnd = 5_000_000
        elif hits == 4:
            prize_tier = "Giải Ba"
            prize_vnd = 500_000
        elif hits == 3 and special_hit:
            prize_tier = "Giải Tư"
            prize_vnd = 100_000
        elif hits == 3:
            prize_tier = "Giải Năm"
            prize_vnd = 30_000
        elif hits <= 2 and special_hit:
            prize_tier = "Giải Khuyến Khích"
            prize_vnd = 10_000

    return {
        "numbers": ticket_numbers,
        "hits": hits,
        "matched_balls": matched,
        "is_special_hit": special_hit,
        "prize_tier": prize_tier,
        "prize_vnd": prize_vnd,
    }


def evaluate_bao7(
    game_type: str,
    septet_numbers: List[int],
    actual_result: List[int],
    special_ball: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Chấm điểm tổ hợp vé Bao 7 (hoặc Bao 6 đối với 5/35).

    - Với Power 6/55 & Mega 6/45: Tạo C(7, 6) = 7 vé con, mỗi vé 6 số (chi phí 70.000 VNĐ).
    - Với Power 5/35 nếu bộ gồm 6 số: Tạo C(6, 5) = 6 vé con, mỗi vé 5 số (chi phí 60.000 VNĐ).
    - Tính tổng số vé trúng, tổng tiền thưởng cộng dồn, và chi tiết từng vé con.

    Returns:
        Dict chứa numbers, hits, matched_balls, cost_vnd, prize_vnd, winning_combinations_count, sub_tickets.
    """
    norm_game = _normalize_game_type(game_type)
    k = 5 if (norm_game == "power535" and len(septet_numbers) <= 6) else 6
    k = min(k, len(septet_numbers))

    sub_combos = list(itertools.combinations(septet_numbers, k))
    total_prize = 0
    winning_count = 0
    sub_results = []

    for combo in sub_combos:
        sub_ticket = list(combo)
        res = evaluate_ticket(game_type, sub_ticket, actual_result, special_ball)
        if res["prize_vnd"] > 0:
            winning_count += 1
            total_prize += res["prize_vnd"]
        sub_results.append(res)

    # Tách main actual để tính matched của septet tổng thể
    actual_main = list(actual_result)
    if norm_game == "power655" and len(actual_main) >= 7:
        actual_main = actual_main[:6]
    elif norm_game == "power535" and len(actual_main) >= 6:
        actual_main = actual_main[:5]
    elif norm_game == "power645" and len(actual_main) > 6:
        actual_main = actual_main[:6]

    matched = sorted(list(set(septet_numbers) & set(actual_main)))

    return {
        "numbers": septet_numbers,
        "hits": len(matched),
        "matched_balls": matched,
        "cost_vnd": len(sub_combos) * 10_000,
        "prize_vnd": total_prize,
        "winning_combinations_count": winning_count,
        "sub_tickets": sub_results,
    }


def evaluate_banker_wheeling(
    game_type: str,
    banker_tickets: List[Union[Dict[str, Any], List[int]]],
    actual_result: List[int],
    special_ball: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Chấm điểm dàn vé xoay bọc lót có bóng chốt Bạch Thủ (Banker Wheeling).

    Args:
        game_type: Loại game Vietlott.
        banker_tickets: Danh sách các vé (mỗi vé có thể là Dict chứa "numbers" hoặc List[int]).
        actual_result: Kết quả mở thưởng thực tế.
        special_ball: Bóng đặc biệt (nếu có).

    Returns:
        Dict chứa:
            - tickets_count: Tổng số vé trong dàn.
            - cost_vnd: Tổng chi phí cược (10.000 VNĐ * tickets_count).
            - best_hits: Số bóng trúng cao nhất trong các vé con.
            - winning_tickets_count: Số vé con có trúng thưởng (prize_vnd > 0).
            - total_prize_vnd: Tổng tiền thưởng cộng dồn toàn dàn (VNĐ).
            - evaluated_tickets: Danh sách kết quả đánh giá từng vé con.
    """
    total_prize = 0
    best_hits = 0
    winning_count = 0
    evaluated_tickets = []

    for t in banker_tickets:
        nums = t.get("numbers", []) if isinstance(t, dict) else t
        res = evaluate_ticket(game_type, nums, actual_result, special_ball)
        if res["hits"] > best_hits:
            best_hits = res["hits"]
        if res["prize_vnd"] > 0:
            winning_count += 1
            total_prize += res["prize_vnd"]
        evaluated_tickets.append(res)

    return {
        "tickets_count": len(banker_tickets),
        "cost_vnd": len(banker_tickets) * 10_000,
        "best_hits": best_hits,
        "winning_tickets_count": winning_count,
        "total_prize_vnd": total_prize,
        "evaluated_tickets": evaluated_tickets,
    }
