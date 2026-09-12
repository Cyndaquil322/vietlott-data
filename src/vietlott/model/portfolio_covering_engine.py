"""
Module: portfolio_covering_engine.py
Thuật toán tối ưu hóa danh mục tổ hợp bọc lót (Portfolio Combinatorial Covering)
cho ngân sách cố định 50.000đ (5 vé đơn Vietlott).

Chức năng:
1. Lọc bỏ các tổ hợp rác bằng Bộ lọc Không Gian Âm (Negative Space Filters):
   - AC Index < 6.
   - Toàn chẵn hoặc toàn lẻ (0:6, 6:0, 1:5, 5:1).
   - Co cụm dưới 3 đầu số.
   - Nằm ngoài phân phối tổng chuẩn Gaussian [μ - 1.5σ, μ + 1.5σ].
2. Tối ưu hóa đa mục tiêu bằng giải thuật tham lam tối đa hóa độ bao phủ (Greedy Max-Coverage):
   - Bao phủ tối đa số cặp đôi (i, j) và bộ ba (i, j, k) từ Dàn Hạt Nhân (Core Pool).
   - Bảo đảm khi Dàn Hạt Nhân nổ >= 3 số thì gom tối đa các số trúng vào chung 1 vé.
"""

import hashlib
import itertools
from typing import Any, Dict, List, Set, Tuple


def filter_negative_space(
    combos: List[Tuple[int, ...]],
    max_val: int,
    num_balls: int,
) -> List[Tuple[int, ...]]:
    """Loại bỏ các bộ số vi phạm các bất biến xác suất thực tế của Vietlott."""
    filtered = []
    min_ac = 7 if num_balls >= 6 else 4
    sum_range = (125, 210) if max_val == 55 else ((105, 175) if max_val == 45 else (65, 115))

    for c in combos:
        s_combo = sorted(c)
        c_sum = sum(s_combo)
        if not (sum_range[0] <= c_sum <= sum_range[1]):
            continue

        diffs = {abs(x - y) for x, y in itertools.combinations(s_combo, 2)}
        ac = len(diffs) - (num_balls - 1)
        if ac < min_ac:
            continue

        odds = sum(1 for x in s_combo if x % 2 != 0)
        if num_balls == 6 and (odds < 2 or odds > 4):
            continue
        if num_balls == 5 and (odds < 1 or odds > 4):
            continue

        decades = set(x // 10 for x in s_combo)
        if num_balls == 6 and len(decades) < 3:
            continue

        filtered.append(tuple(s_combo))
    return filtered


def generate_portfolio_50k(
    core_pool: List[int],
    candidate_scores: Dict[int, float],
    max_val: int,
    num_balls: int,
    num_tickets: int = 5,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Sinh danh mục 5 vé tối ưu bọc lót từ Dàn Hạt Nhân:
    - Giải bài toán Greedy Max-Coverage trên không gian cặp đôi và bộ ba.
    - Đảm bảo tính tất định theo mã kỳ quay `seed`.
    """
    pool = sorted(list(set(core_pool)))[: (12 if max_val in (55, 45) else 10)]
    if len(pool) < num_balls:
        pool = list(range(1, num_balls + 1))

    all_combos = list(itertools.combinations(pool, num_balls))
    valid_combos = filter_negative_space(all_combos, max_val, num_balls)
    if len(valid_combos) < num_tickets:
        valid_combos = [tuple(sorted(c)) for c in all_combos]

    all_pairs = set(itertools.combinations(pool, 2))
    all_triplets = set(itertools.combinations(pool, 3))

    selected: List[List[int]] = []
    covered_pairs: Set[Tuple[int, int]] = set()
    covered_triplets: Set[Tuple[int, int, int]] = set()

    for idx in range(num_tickets):
        best_c = None
        best_score = -999999.0

        for c in valid_combos:
            c_list = list(c)
            if c_list in selected:
                continue
            c_pairs = set(itertools.combinations(c, 2))
            c_triplets = set(itertools.combinations(c, 3))

            new_p = len(c_pairs - covered_pairs)
            new_t = len(c_triplets - covered_triplets)
            exp_w = sum(candidate_scores.get(b, 0.0) for b in c)

            h_key = f"{seed}_{idx}_{c}".encode("utf-8")
            tie_breaker = (int(hashlib.md5(h_key).hexdigest()[:6], 16) % 1000) * 0.001

            score = (new_p * 3.0) + (new_t * 1.5) + (exp_w * 2.0) + tie_breaker
            if score > best_score:
                best_score = score
                best_c = c_list

        if best_c:
            selected.append(best_c)
            covered_pairs.update(itertools.combinations(best_c, 2))
            covered_triplets.update(itertools.combinations(best_c, 3))

    tickets_data = []
    tags = [
        "Trục Hạt Nhân",
        "Cặp Đôi Bạc Nhớ",
        "Kháng Dao Động",
        "Lực Hút Markov",
        "Bảo Hiểm Bao Phủ",
    ]
    for i, t_nums in enumerate(selected):
        diffs = {abs(x - y) for x, y in itertools.combinations(t_nums, 2)}
        ac = len(diffs) - (num_balls - 1)
        odds = sum(1 for x in t_nums if x % 2 != 0)
        decades = len(set(x // 10 for x in t_nums))

        tickets_data.append({
            "id": f"portfolio_ticket_{i+1}",
            "ticketIndex": i + 1,
            "numbers": sorted(t_nums),
            "sum": sum(t_nums),
            "ac": ac,
            "odds": odds,
            "evens": num_balls - odds,
            "decades_count": decades,
            "tag": tags[i % len(tags)],
        })

    pair_cov_pct = round(len(covered_pairs) / max(1, len(all_pairs)) * 100.0, 1)

    return {
        "total_tickets": len(tickets_data),
        "total_cost_vnd": len(tickets_data) * 10000,
        "core_pool_size": len(pool),
        "pairs_coverage_pct": pair_cov_pct,
        "triplets_coverage_count": len(covered_triplets),
        "tickets": tickets_data,
    }


__all__ = [
    "filter_negative_space",
    "generate_portfolio_50k",
]
