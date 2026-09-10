"""
Module: elimination_engine.py
Thuật toán Bộ Lọc Đào Thải Bóng Chết (Negative Elimination Mining)
Loại bỏ các quả bóng có nguy cơ ngủ đông, kỵ nhau hoặc xác suất xuất hiện cực thấp kỳ này.

100% Zero Mock Data - Tuân thủ nguyên tắc thiết kế toán học Walk-Forward.
"""

from typing import List, Dict, Any, Optional
import math
import numpy as np

from vietlott.model.analytic_engines import evaluate_all_models
from vietlott.model.transition_engine import calculate_vector_field_pull


def calculate_elimination_risk_scores(
    sub_records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    models_eval: Optional[Dict[str, Any]] = None,
    transition_pull: Optional[Dict[int, Dict[str, float]]] = None,
) -> Dict[int, Dict[str, Any]]:
    """
    Tính toán Chỉ số Nguy cơ Ngủ Đông / Bóng Chết E(b) cho từng bóng b in [1, max_val]:
    E(b) = 0.30 * hazard_risk + 0.25 * wavelet_dormancy + 0.25 * repulsion_risk + 0.20 * bottom_consensus_risk

    Args:
        sub_records: Danh sách các bản ghi kỳ quay lịch sử (<= T-1).
        max_val: Giá trị bóng lớn nhất (55 cho 6/55, 45 cho 6/45, 35 cho 5/35).
        num_balls: Số bóng chính trong 1 kỳ quay.
        models_eval: Kết quả đánh giá của các mô hình toán học (nếu None sẽ tự gọi evaluate_all_models).
        transition_pull: Trường lực chuyển tiếp liên kỳ (nếu None sẽ tự gọi calculate_vector_field_pull).

    Returns:
        Dict {b: {
            "risk_score": float,
            "reason": str,
            "hazard_risk": float,
            "wavelet_dormancy": float,
            "repulsion_risk": float,
            "bottom_risk": float,
        }}
    """
    if max_val <= 0:
        return {}

    if models_eval is None:
        models_eval = evaluate_all_models(sub_records, max_val, num_balls)

    if transition_pull is None:
        transition_pull = calculate_vector_field_pull(sub_records, max_val, num_balls)

    # 1. Tính toán thống kê nhịp gan g_b, g_bar_b, Z cho hazard_risk
    K = min(120, len(sub_records))
    recent = sub_records[-K:] if sub_records else []
    cur_gap = {b: K for b in range(1, max_val + 1)}
    gaps_history = {b: [] for b in range(1, max_val + 1)}
    prev_seen = {}

    for t, r in enumerate(reversed(recent)):
        res = r.get("result", [])
        for b in res[:num_balls]:
            if 1 <= b <= max_val:
                if b not in prev_seen:
                    cur_gap[b] = t
                    prev_seen[b] = t
                else:
                    gaps_history[b].append(t - prev_seen[b])
                    prev_seen[b] = t

    # 4. Tính toán thứ hạng đồng thuận đáy (bottom_consensus_risk)
    # Lấy điểm số từ các mô hình dự đoán trong models_eval
    score_model_keys = [
        k for k, v in models_eval.items()
        if k != "cur_gap" and isinstance(v, dict)
    ]
    consensus_scores = {b: 0.0 for b in range(1, max_val + 1)}

    if score_model_keys:
        for m in score_model_keys:
            m_dict = models_eval[m]
            max_m = max(m_dict.values()) if m_dict and max(m_dict.values()) > 0 else 1.0
            for b in range(1, max_val + 1):
                consensus_scores[b] += m_dict.get(b, 0.0) / max_m
    elif models_eval and all(isinstance(k, int) for k in models_eval.keys()):
        for b in range(1, max_val + 1):
            consensus_scores[b] = float(models_eval.get(b, 0.0))

    # Xếp hạng từ 1 (điểm cao nhất) đến max_val (điểm thấp nhất)
    # Sắp xếp tất định: (-điểm, bóng)
    ranked_balls = sorted(range(1, max_val + 1), key=lambda b: (-consensus_scores[b], b))
    ball_ranks = {b: idx + 1 for idx, b in enumerate(ranked_balls)}

    results: Dict[int, Dict[str, Any]] = {}
    threshold_rank = 0.75 * max_val
    denom_rank = 0.25 * max_val if max_val > 0 else 1.0

    for b in range(1, max_val + 1):
        # 1. hazard_risk: nhịp gan quá hạn g_b / g_bar_b > 2.0 (và Z > 2.0)
        c_gap = cur_gap[b]
        all_g = gaps_history[b]
        avg_g = (sum(all_g) / len(all_g)) if all_g else (max_val / num_balls)
        std_g = float(np.std(all_g)) if len(all_g) >= 2 else (avg_g * 0.75)
        z = (c_gap - 1.05 * avg_g) / max(1.0, std_g)

        if avg_g > 0 and (c_gap / avg_g > 2.0) and (z > 2.0):
            hazard_risk = min(1.0, c_gap / (2.5 * avg_g))
        else:
            hazard_risk = 0.0

        # 2. wavelet_dormancy: năng lượng phổ sóng con triệt tiêu (s_spectral < 0.20)
        s_spectral = float(models_eval.get("fourier", {}).get(b, 0.0))
        if s_spectral < 0.20:
            wavelet_dormancy = max(0.0, 1.0 - s_spectral / 0.35)
        else:
            wavelet_dormancy = 0.0

        # 3. repulsion_risk: lực kỵ nhau liên kỳ (repulsion_penalty < 0.45)
        repulsion_penalty = float(transition_pull.get(b, {}).get("repulsion_penalty", 1.0))
        if repulsion_penalty < 0.45:
            repulsion_risk = max(0.0, 1.0 - repulsion_penalty / 0.50)
        else:
            repulsion_risk = 0.0

        # 4. bottom_consensus_risk: thứ hạng nằm trong nhóm 25% đáy
        rank = ball_ranks[b]
        bottom_consensus_risk = max(0.0, min(1.0, (rank - threshold_rank) / denom_rank))

        # Điểm nguy cơ tổng hợp
        risk_score = (
            0.30 * hazard_risk
            + 0.25 * wavelet_dormancy
            + 0.25 * repulsion_risk
            + 0.20 * bottom_consensus_risk
        )

        # Gán lý do chủ đạo (reason) theo thành phần cao nhất (ưu tiên trọng số khi hòa)
        components = [
            (hazard_risk, 0.30, "Gan lì lợm (Vắng mặt kéo dài)"),
            (wavelet_dormancy, 0.25, "Ngủ đông (Triệt tiêu phổ sóng)"),
            (repulsion_risk, 0.25, "Xung khắc (Kỵ bóng nổ kỳ trước)"),
            (bottom_consensus_risk, 0.20, "Đáy đồng thuận (Xác suất thấp)"),
        ]
        best_reason = sorted(components, key=lambda x: (x[0], x[1]), reverse=True)[0][2]

        results[b] = {
            "risk_score": round(float(risk_score), 4),
            "reason": best_reason,
            "hazard_risk": round(float(hazard_risk), 4),
            "wavelet_dormancy": round(float(wavelet_dormancy), 4),
            "repulsion_risk": round(float(repulsion_risk), 4),
            "bottom_risk": round(float(bottom_consensus_risk), 4),
        }

    return results


def prune_dead_numbers(
    risk_scores: Dict[int, Dict[str, Any]],
    max_val: int,
    elim_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Đào thải Top elim_count bóng có Chỉ số Nguy cơ E(b) cao nhất, thu hẹp không gian số.

    Args:
        risk_scores: Dict điểm nguy cơ từ calculate_elimination_risk_scores.
        max_val: Giá trị bóng lớn nhất (55, 45, 35).
        elim_count: Số lượng bóng bị loại (mặc định: 16 cho 6/55, 13 cho 6/45, 9 cho 5/35).

    Returns:
        Dict {
            "eliminated_count": int,
            "eliminated_balls": List[Dict],
            "eliminated_ball_numbers": List[int],
            "pruned_universe": List[int],
            "pruned_universe_size": int,
            "elimination_rate_pct": float,
        }
    """
    if max_val <= 0 or not risk_scores:
        return {
            "eliminated_count": 0,
            "eliminated_balls": [],
            "eliminated_ball_numbers": [],
            "pruned_universe": [],
            "pruned_universe_size": 0,
            "elimination_rate_pct": 0.0,
        }

    if elim_count is None:
        if max_val == 55:
            elim_count = 16
        elif max_val == 45:
            elim_count = 13
        elif max_val == 35:
            elim_count = 9
        else:
            elim_count = max(1, int(round(max_val * 0.29)))

    elim_count = max(0, min(elim_count, max_val))

    # Sắp xếp giảm dần theo risk_score, tất định bằng mã số bóng
    sorted_balls = sorted(
        range(1, max_val + 1),
        key=lambda b: (-risk_scores.get(b, {}).get("risk_score", 0.0), b),
    )

    eliminated_ids = sorted_balls[:elim_count]
    eliminated_balls = [
        {
            "ball": b,
            "risk_score": round(risk_scores.get(b, {}).get("risk_score", 0.0), 3),
            "reason": risk_scores.get(b, {}).get("reason", "Đáy xác suất"),
        }
        for b in eliminated_ids
    ]

    eliminated_set = set(eliminated_ids)
    pruned_universe = sorted([b for b in range(1, max_val + 1) if b not in eliminated_set])

    eliminated_count = len(eliminated_balls)
    pruned_universe_size = len(pruned_universe)
    elimination_rate_pct = round((eliminated_count / max_val) * 100.0, 1)

    return {
        "eliminated_count": eliminated_count,
        "eliminated_balls": eliminated_balls,
        "eliminated_ball_numbers": eliminated_ids,
        "pruned_universe": pruned_universe,
        "pruned_universe_size": pruned_universe_size,
        "elimination_rate_pct": elimination_rate_pct,
    }


def evaluate_walk_forward_elimination_precision(
    records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    num_draws: int = 100,
    elim_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Kiểm định Walk-Forward độ chính xác đào thải (Elimination Precision) qua num_draws kỳ.
    Strictly No Look-Ahead: Tại mỗi kỳ i, mô hình chỉ được dùng records[:i].

    Đo lường:
    Precision = (Số bóng bị đào thải THỰC TẾ KHÔNG NỔ trong kỳ i) / (Tổng số bóng đào thải) * 100%

    Returns:
        Dict {
            "historical_elimination_precision": float,
            "evaluated_draws": int,
            "total_eliminated_eval": int,
            "total_unhit_eliminated": int,
            "avg_lethal_hits_per_draw": float,
        }
    """
    if len(records) < 10 or max_val <= 0:
        return {
            "historical_elimination_precision": 100.0,
            "evaluated_draws": 0,
            "total_eliminated_eval": 0,
            "total_unhit_eliminated": 0,
            "avg_lethal_hits_per_draw": 0.0,
        }

    test_count = min(num_draws, len(records) - 10)
    start_idx = len(records) - test_count

    total_eliminated = 0
    total_unhit = 0
    total_hits = 0
    draw_precisions: List[float] = []

    for i in range(start_idx, len(records)):
        sub_records = records[:i]
        actual_draw = set(records[i].get("result", [])[:num_balls])

        risk_scores = calculate_elimination_risk_scores(sub_records, max_val, num_balls)
        pruned = prune_dead_numbers(risk_scores, max_val, elim_count=elim_count)

        elim_balls = set(pruned["eliminated_ball_numbers"])
        k_elim = len(elim_balls)

        if k_elim == 0:
            continue

        hits_in_elim = len(elim_balls.intersection(actual_draw))
        unhit_in_elim = k_elim - hits_in_elim
        precision_i = (unhit_in_elim / k_elim) * 100.0

        total_eliminated += k_elim
        total_unhit += unhit_in_elim
        total_hits += hits_in_elim
        draw_precisions.append(precision_i)

    evaluated_draws = len(draw_precisions)
    if evaluated_draws == 0:
        historical_precision = 100.0
        avg_lethal_hits = 0.0
    else:
        historical_precision = round(sum(draw_precisions) / evaluated_draws, 1)
        avg_lethal_hits = round(total_hits / evaluated_draws, 2)

    return {
        "historical_elimination_precision": historical_precision,
        "evaluated_draws": evaluated_draws,
        "total_eliminated_eval": total_eliminated,
        "total_unhit_eliminated": total_unhit,
        "avg_lethal_hits_per_draw": avg_lethal_hits,
    }
