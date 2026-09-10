"""
Markowitz Portfolio Ticket Optimization & Louvain Community Extraction Module.
File: src/vietlott/model/portfolio_optimizer.py

Triển khai:
1. build_pairwise_covariance_proxy: Xây dựng ma trận hiệp phương sai tương quan cặp đôi N x N.
2. extract_louvain_communities: Phân cụm đồ thị Louvain modularity thuần NumPy (4-5 cụm).
3. optimize_markowitz_ticket: Tối ưu hóa danh mục vé có ràng buộc bậc hai (Quadratic Programming / Beam Search).
"""

import hashlib
import itertools
import random
from typing import Any, Dict, List, Tuple
import numpy as np


def build_pairwise_covariance_proxy(
    records: List[Dict],
    max_val: int,
    num_balls: int,
    window_len: int = 150,
) -> np.ndarray:
    """
    Xây dựng ma trận tương quan hiệp phương sai đối xứng N x N trên window_len kỳ gần nhất.
    Đếm số lần nổ chung cặp C(i, j) và đơn C(i), C(j).
    Lift*(i, j) = ((C(i, j) + 1.0 * P_0) / (C(i) + 1.0)) * (1 / P_0) với P_0 = num_balls / max_val.
    Sigma_ij = 0.5 * (Lift*(i, j) + Lift*(j, i)) - 1.0 cho i != j, Sigma_ii = 0.0.
    """
    if max_val <= 0:
        return np.zeros((0, 0), dtype=float)

    cov = np.zeros((max_val, max_val), dtype=float)
    if not records or num_balls <= 0:
        return cov

    recent = records[-window_len:]
    p0 = float(num_balls) / float(max_val)

    # Đếm số lần xuất hiện đơn C(i) và cặp đôi C(i, j)
    c_single = np.zeros(max_val, dtype=float)
    c_pair = np.zeros((max_val, max_val), dtype=float)

    for r in recent:
        res = r.get("result") or r.get("draw_result") or r.get("numbers") or []
        main_balls = [b for b in res[:num_balls] if 1 <= b <= max_val]
        for b in main_balls:
            c_single[b - 1] += 1.0

        for b1, b2 in itertools.combinations(main_balls, 2):
            idx1, idx2 = b1 - 1, b2 - 1
            c_pair[idx1, idx2] += 1.0
            c_pair[idx2, idx1] += 1.0

    # Tính toán Lift*(i, j) đối xứng và ma trận Sigma
    for i in range(max_val):
        for j in range(i + 1, max_val):
            lift_ij = ((c_pair[i, j] + 1.0 * p0) / (c_single[i] + 1.0)) / p0
            lift_ji = ((c_pair[i, j] + 1.0 * p0) / (c_single[j] + 1.0)) / p0
            lift_sym = 0.5 * (lift_ij + lift_ji)
            sigma_val = lift_sym - 1.0
            cov[i, j] = sigma_val
            cov[j, i] = sigma_val

    np.fill_diagonal(cov, 0.0)
    return cov


def extract_louvain_communities(
    records: List[Dict],
    max_val: int,
    num_balls: int,
    window_len: int = 150,
) -> Dict[int, int]:
    """
    Phân cụm các con số từ 1 .. max_val thành 4 đến 5 cụm tự nhiên dựa trên tần suất nổ chung
    sử dụng thuật toán tối ưu hóa mô-đun modularity tham lam thuần NumPy.
    Trả về dictionary {b: cluster_id} với b in [1, max_val], cluster_id in {0, 1, 2, 3, 4}.
    """
    if max_val <= 0:
        return {}

    target_k = min(5, max_val)
    if not records or num_balls <= 0 or target_k <= 1:
        return {b: (b - 1) % target_k for b in range(1, max_val + 1)}

    recent = records[-window_len:]
    # Xây dựng ma trận kề nổ chung
    adj = np.zeros((max_val, max_val), dtype=float)
    for r in recent:
        res = r.get("result") or r.get("draw_result") or r.get("numbers") or []
        main_balls = [b for b in res[:num_balls] if 1 <= b <= max_val]
        for b1, b2 in itertools.combinations(main_balls, 2):
            adj[b1 - 1, b2 - 1] += 1.0
            adj[b2 - 1, b1 - 1] += 1.0

    total_weight_2m = float(np.sum(adj))
    if total_weight_2m <= 0.0:
        return {b: (b - 1) % target_k for b in range(1, max_val + 1)}

    node_degrees = np.sum(adj, axis=1)

    # Khởi tạo mỗi node là 1 cụm riêng
    active_clusters = {i: {i} for i in range(max_val)}
    cluster_degrees = {i: float(node_degrees[i]) for i in range(max_val)}

    # Ma trận trọng số liên cụm W[u, v]
    inter_weights = {u: {v: float(adj[u, v]) for v in range(max_val)} for u in range(max_val)}

    inv_2m = 1.0 / total_weight_2m
    inv_4m2 = 1.0 / (total_weight_2m * total_weight_2m)

    # Gom cụm tham lam tối ưu hóa Modularity cho đến khi còn đúng target_k cụm
    while len(active_clusters) > target_k:
        best_dq = -1e18
        best_pair = None

        cluster_keys = list(active_clusters.keys())
        num_act = len(cluster_keys)

        for i in range(num_act):
            u = cluster_keys[i]
            d_u = cluster_degrees[u]
            u_weights = inter_weights[u]
            for j in range(i + 1, num_act):
                v = cluster_keys[j]
                w_uv = u_weights.get(v, 0.0)
                d_v = cluster_degrees[v]

                # Delta Q khi gộp cụm u và v:
                # 2 * w_uv / (2m) - 2 * d_u * d_v / (2m)^2
                dq = 2.0 * w_uv * inv_2m - 2.0 * d_u * d_v * inv_4m2

                # Ưu tiên kích thước cân bằng khi dq bằng nhau
                size_penalty = 1e-6 * (len(active_clusters[u]) + len(active_clusters[v]))
                score = dq - size_penalty

                if score > best_dq:
                    best_dq = score
                    best_pair = (u, v)

        if best_pair is None:
            break

        u, v = best_pair
        # Gộp cụm v vào cụm u
        active_clusters[u] = active_clusters[u].union(active_clusters[v])
        cluster_degrees[u] += cluster_degrees[v]

        for w in cluster_keys:
            if w != u and w != v:
                new_w = inter_weights[u].get(w, 0.0) + inter_weights[v].get(w, 0.0)
                inter_weights[u][w] = new_w
                inter_weights[w][u] = new_w
                if v in inter_weights[w]:
                    del inter_weights[w][v]

        del active_clusters[v]
        del cluster_degrees[v]
        del inter_weights[v]

    # Sắp xếp các cụm theo kích thước hoặc phần tử nhỏ nhất và gán cluster_id 0 .. K-1
    sorted_communities = sorted(active_clusters.values(), key=lambda s: (min(s), len(s)))
    mapping: Dict[int, int] = {}
    for cid, comm in enumerate(sorted_communities):
        for node_idx in comm:
            mapping[node_idx + 1] = cid

    # Đảm bảo toàn bộ bóng 1 .. max_val đều có mặt
    for b in range(1, max_val + 1):
        if b not in mapping:
            mapping[b] = (b - 1) % target_k

    return mapping


def optimize_markowitz_ticket(
    candidate_scores: Dict[int, float],
    cov_matrix: np.ndarray,
    louvain_clusters: Dict[int, int],
    max_val: int,
    num_balls: int,
    target_sum: int,
    sum_range: Tuple[int, int],
    min_ac: int,
    risk_lambda: float = 0.30,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Giải bài toán tối ưu hóa danh mục vé Markowitz có ràng buộc bậc hai:
    max sum(x_i * mu_i) - lambda * sum_{i < j} x_i * x_j * Sigma_{ij}

    Ràng buộc cứng:
    1. sum(x_i) = num_balls
    2. sum_range[0] <= sum(combo) <= sum_range[1]
    3. Arithmetic Complexity AC(combo) >= min_ac
    4. Đa cụm Louvain: số cụm phân biệt >= 4 (hoặc >= 3 với num_balls == 5), tối đa 2 bóng/cụm.
    """
    if max_val <= 0 or num_balls <= 0:
        return {}

    # Thu thập ứng viên
    sorted_candidates = sorted(
        candidate_scores.keys(),
        key=lambda b: candidate_scores[b],
        reverse=True,
    )
    # Lọc các bóng hợp lệ trong khoảng 1 .. max_val
    valid_candidates = [b for b in sorted_candidates if 1 <= b <= max_val]

    # Nếu thiếu bóng, bổ sung các bóng còn lại
    if len(valid_candidates) < num_balls:
        remaining = [b for b in range(1, max_val + 1) if b not in valid_candidates]
        valid_candidates.extend(remaining)

    # Lấy Top 14-16 ứng viên hàng đầu
    pool_size = min(16, len(valid_candidates))
    candidate_pool = valid_candidates[:pool_size]

    def _eval_combo(combo: Tuple[int, ...]) -> Tuple[float, float, float, int, int, int, Dict[str, int]]:
        """Tính toán các chỉ số của tổ hợp."""
        sorted_c = sorted(combo)
        c_sum = sum(sorted_c)

        # AC Index
        diffs = {abs(x - y) for x, y in itertools.combinations(sorted_c, 2)}
        ac = len(diffs) - (num_balls - 1)

        # Louvain clusters
        c_dist: Dict[int, int] = {}
        for b in sorted_c:
            cid = louvain_clusters.get(b, 0)
            c_dist[cid] = c_dist.get(cid, 0) + 1
        distinct_c = len(c_dist)
        max_in_c = max(c_dist.values()) if c_dist else 0

        # Markowitz Utility
        exp_ret = sum(candidate_scores.get(b, 0.0) for b in sorted_c)
        cov_penalty_raw = 0.0
        for i, j in itertools.combinations(sorted_c, 2):
            cov_penalty_raw += cov_matrix[i - 1, j - 1]
        cov_penalty = risk_lambda * cov_penalty_raw
        utility = exp_ret - cov_penalty

        c_dist_formatted = {f"C{k}": v for k, v in sorted(c_dist.items())}
        return (utility, exp_ret, cov_penalty, c_sum, ac, distinct_c, max_in_c, c_dist_formatted)

    # Ràng buộc cụm theo số lượng bóng
    min_distinct_clusters = 4 if num_balls >= 6 else 3

    # Các tầng nới lỏng an toàn (Multi-tier Relaxation)
    # Tầng 1: Đầy đủ mọi ràng buộc cứng trên candidate_pool (top 16)
    # Tầng 2: Mở rộng pool lên 20 ứng viên, giữ nguyên ràng buộc cứng (ưu tiên đa cụm >= 4)
    # Tầng 3: Nới lỏng số cụm tối thiểu xuống >= 3 trên candidate_pool
    # Tầng 4: Nới lỏng số cụm tối thiểu xuống >= 3 trên pool 20 ứng viên
    # Tầng 5-6: Fallback toàn diện đảm bảo không bao giờ rỗng

    search_stages = [
        # (pool_limit, req_distinct_c, max_per_c, enforce_sum, enforce_ac)
        (candidate_pool, min_distinct_clusters, 2, True, True),
        (valid_candidates[: min(20, len(valid_candidates))], min_distinct_clusters, 2, True, True),
        (candidate_pool, 3, 2, True, True),
        (valid_candidates[: min(20, len(valid_candidates))], 3, 2, True, True),
        (candidate_pool, 2, 3, True, False),
        (valid_candidates[: min(16, len(valid_candidates))], 1, num_balls, False, False),
    ]

    selected_combo = None
    best_metrics = None

    for pool, req_dist, max_per_c, check_sum, check_ac in search_stages:
        if len(pool) < num_balls:
            continue

        feasible_combos = []
        for combo in itertools.combinations(pool, num_balls):
            (
                utility,
                exp_ret,
                cov_penalty,
                c_sum,
                ac,
                dist_c,
                max_in_c,
                c_dist_fmt,
            ) = _eval_combo(combo)

            if check_sum and not (sum_range[0] <= c_sum <= sum_range[1]):
                continue
            if check_ac and ac < min_ac:
                continue
            if dist_c < req_dist:
                continue
            if max_in_c > max_per_c:
                continue

            # Deterministic tie-breaking using seed
            # Băm MD5 kết hợp seed và tổ hợp để hòa điểm tất định tuyệt đối qua mọi tiến trình Python
            combo_key = f"{seed}_{sorted(combo)}".encode("utf-8")
            h = int(hashlib.md5(combo_key).hexdigest()[:8], 16) % 100000

            feasible_combos.append({
                "combo": sorted(combo),
                "utility": utility,
                "exp_ret": exp_ret,
                "cov_penalty": cov_penalty,
                "sum": c_sum,
                "ac": ac,
                "dist_c": dist_c,
                "c_dist": c_dist_fmt,
                "rank_score": (round(utility, 6), -abs(c_sum - target_sum), h),
            })

        if feasible_combos:
            feasible_combos.sort(key=lambda x: x["rank_score"], reverse=True)
            selected = feasible_combos[0]
            selected_combo = selected["combo"]
            best_metrics = selected
            break

    # Nếu vẫn chưa tìm thấy (trường hợp cực đoan), lấy num_balls đầu tiên
    if selected_combo is None:
        selected_combo = sorted(valid_candidates[:num_balls])
        (
            utility,
            exp_ret,
            cov_penalty,
            c_sum,
            ac,
            dist_c,
            max_in_c,
            c_dist_fmt,
        ) = _eval_combo(tuple(selected_combo))
        best_metrics = {
            "combo": selected_combo,
            "utility": utility,
            "exp_ret": exp_ret,
            "cov_penalty": cov_penalty,
            "sum": c_sum,
            "ac": ac,
            "dist_c": dist_c,
            "c_dist": c_dist_fmt,
        }

    return {
        "numbers": best_metrics["combo"],
        "optimization_type": "Markowitz Constrained Portfolio",
        "expected_return": float(round(best_metrics["exp_ret"], 4)),
        "covariance_risk_penalty": float(round(best_metrics["cov_penalty"], 4)),
        "objective_utility": float(round(best_metrics["utility"], 4)),
        "louvain_spread": {
            "distinct_clusters_count": int(best_metrics["dist_c"]),
            "cluster_distribution": best_metrics["c_dist"],
        },
        "ac_index": int(best_metrics["ac"]),
        "sum": int(best_metrics["sum"]),
    }
