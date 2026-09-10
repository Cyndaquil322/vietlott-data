"""Module Quản Trị Vốn Kelly & Chỉ Số Tự Tin Đồng Thuận (Consensus Conviction Score - CCS).

Tính toán Chỉ số Tự tin Đồng thuận (Consensus Conviction Score - CCS) trên thang điểm [0, 100%]
và hệ thống phân bổ vốn đầu tư thực chiến 3 cấp độ theo Tiêu chuẩn Kelly:
- Cấp 1 (CCS < 55.0%): Tín Hiệu Phân Tán (High Noise / Low Conviction) -> 10.000đ
- Cấp 2 (55.0% <= CCS < 75.0%): Tín Hiệu Khả Quan (Moderate Convergence) -> 20.000đ
- Cấp 3 (CCS >= 75.0%): Điểm Rơi Vàng (Super-Convergence) -> 60.000đ
"""

from typing import Dict, List, Any
import math
import numpy as np


def calculate_consensus_conviction_score(
    models_info: Dict[str, Any],
    top_candidates_per_model: Dict[str, List[int]],
    consensus_scores: Dict[int, float],
    transition_analytics: Dict[str, Any],
    num_balls: int,
) -> Dict[str, Any]:
    """Tính toán Chỉ số Tự tin Đồng thuận (CCS) và đề xuất phân bổ vốn theo Tiêu chuẩn Kelly.

    Args:
        models_info: Thông tin danh sách 8 mô hình dự đoán.
        top_candidates_per_model: Danh sách ứng viên hàng đầu của từng mô hình.
        consensus_scores: Điểm số đồng thuận cho từng con bóng.
        transition_analytics: Kết quả phân tích luật chuyển tiếp liên kỳ A -> B.
        num_balls: Số lượng bóng của trò chơi (5 hoặc 6).

    Returns:
        Dict:
        {
            "ccs_score": float,
            "tier_level": int,
            "tier_name": str,
            "tier_badge": str,
            "recommended_action": str,
            "recommended_budget": int,
            "breakdown": {
                "agreement_score": float,
                "entropy_score": float,
                "pull_score": float,
            },
            "rationale": str,
        }
    """
    # 0. Xác định Top 12 ứng viên dẫn đầu dựa trên consensus_scores
    if consensus_scores:
        sorted_candidates = sorted(
            consensus_scores.keys(),
            key=lambda b: consensus_scores[b],
            reverse=True,
        )
        top_12 = sorted_candidates[:12]
    else:
        top_12 = []

    # 1. Thành phần 1 (S_agreement): Độ đồng thuận của các mô hình trên Top 12 ứng viên
    total_models = len(models_info) if models_info else (
        len(top_candidates_per_model) if top_candidates_per_model else 8
    )
    if total_models <= 0:
        total_models = 8

    if top_12 and top_candidates_per_model:
        model_agreement_sum = 0.0
        for b in top_12:
            cnt = sum(1 for picks in top_candidates_per_model.values() if b in picks)
            model_agreement_sum += cnt / total_models

        denom_agreement = 12.0 if len(consensus_scores) >= 12 else max(1.0, float(len(top_12)))
        s_agreement = (model_agreement_sum / denom_agreement) * 100.0
    else:
        s_agreement = 0.0

    s_agreement = max(0.0, min(100.0, s_agreement))

    # 2. Thành phần 2 (S_entropy): Độ tập trung xác suất Softmax trên Top 12 bóng
    if len(top_12) >= 2:
        s_vals = np.array([float(consensus_scores[b]) for b in top_12], dtype=float)
        if np.allclose(s_vals, s_vals[0]):
            s_entropy = 0.0
        else:
            max_s = np.max(s_vals)
            exp_s = np.exp(s_vals - max_s)
            sum_exp = np.sum(exp_s)
            probs = exp_s / (sum_exp if sum_exp > 0 else 1.0)

            h_entropy = -float(np.sum(probs * np.log(probs + 1e-12)))
            denom_h = math.log(12) if len(top_12) >= 12 else math.log(len(top_12))
            if denom_h <= 0:
                denom_h = math.log(12)

            s_entropy = max(0.0, min(100.0, (1.0 - (h_entropy / denom_h)) * 250.0))
    else:
        s_entropy = 0.0

    s_entropy = max(0.0, min(100.0, s_entropy))

    # 3. Thành phần 3 (S_pull): Xung lực kéo liên kỳ từ A -> B
    pull_rules = (
        transition_analytics.get("top_pull_rules", [])
        if isinstance(transition_analytics, dict)
        else []
    )
    pos_z_sum = 0.0
    for r in pull_rules:
        if isinstance(r, dict):
            z = float(r.get("z_score", 0.0))
        elif isinstance(r, (int, float)):
            z = float(r)
        else:
            z = 0.0
        if z > 0:
            pos_z_sum += z

    s_pull = max(0.0, min(100.0, (pos_z_sum / 15.0) * 100.0))

    # 4. Điểm tổng hợp CCS
    ccs_raw = 0.40 * s_agreement + 0.35 * s_entropy + 0.25 * s_pull
    ccs_score = max(0.0, min(100.0, round(ccs_raw, 1)))

    # 5. Phân loại 3 cấp độ vốn thực chiến
    if ccs_score >= 75.0:
        tier_level = 3
        tier_name = "Điểm Rơi Vàng (Super-Convergence)"
        tier_badge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
        recommended_action = "Kích hoạt Dàn Bọc Lót 6 Vé C(v, k, 3)"
        recommended_budget = 60000
        rationale = (
            "Đồng thuận hội tụ cực mạnh giữa các mô hình (>= 6/8) và xung lực kéo liên kỳ đạt đỉnh. "
            "Tỷ lệ ăn giải của Dàn bọc lót đạt mức tối ưu."
        )
    elif ccs_score >= 55.0:
        tier_level = 2
        tier_name = "Tín Hiệu Khả Quan (Moderate Convergence)"
        tier_badge = "bg-sky-500/20 text-sky-300 border-sky-500/40"
        recommended_action = "Đánh Vé Golden Markowitz + Kiềng 3 Chân Triad"
        recommended_budget = 20000
        rationale = (
            "Đa số mô hình hội tụ tốt. Khuyến nghị phối hợp 1 vé Golden Markowitz và 1 vé Triad "
            "để bảo toàn vốn."
        )
    else:
        tier_level = 1
        tier_name = "Tín Hiệu Phân Tán (High Noise / Low Conviction)"
        tier_badge = "bg-slate-800 text-slate-300 border-slate-700"
        recommended_action = "Thăm dò nhẹ 1 vé đơn hoặc tạm dừng"
        recommended_budget = 10000
        rationale = (
            "Các mô hình phân hóa mạnh, tín hiệu thị trường có độ nhiễu cao. "
            "Khuyến nghị thăm dò 1 vé đơn 10k hoặc bảo toàn vốn."
        )

    return {
        "ccs_score": ccs_score,
        "tier_level": tier_level,
        "tier_name": tier_name,
        "tier_badge": tier_badge,
        "recommended_action": recommended_action,
        "recommended_budget": recommended_budget,
        "breakdown": {
            "agreement_score": round(float(s_agreement), 1),
            "entropy_score": round(float(s_entropy), 1),
            "pull_score": round(float(s_pull), 1),
        },
        "rationale": rationale,
    }
