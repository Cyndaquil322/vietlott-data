"""
Transition Engine (Động Cơ Chuyển Trạng Thái Liên Kỳ A -> B & Vector Field Pull)
==============================================================================
Module tính toán ma trận chuyển tiếp liên kỳ N x N, kiểm định độ lệch chuẩn nhị thức
Z-score, tỷ số độ nâng xác suất Lift(A -> B), Trường lực hấp dẫn Vector (Vector Field Pull)
và trích xuất các quy luật kéo / kỵ nhau có ý nghĩa thống kê.

Tuân thủ nghiêm ngặt:
1. Walk-Forward Temporal Safety (Chỉ dùng dữ liệu t <= T-1 để dự báo cho T).
2. Zero Mock Data (100% tính toán thực nghiệm từ lịch sử mở thưởng).
3. Deterministic Seeding & Numerical Stability (Không phát sinh NaN/Inf).
"""

import math
from typing import Any, Dict, List, Tuple


def build_transition_matrix(
    records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    window_len: int = 150,
) -> Dict[Tuple[int, int], Dict[str, Any]]:
    """
    Xây dựng ma trận chuyển tiếp liên kỳ N x N giữa các kỳ quay liên tiếp (t-1 -> t).

    Args:
        records: Danh sách các bản ghi kỳ quay lịch sử (sắp xếp theo thứ tự thời gian tăng dần).
        max_val: Giá trị bóng lớn nhất (ví dụ: 55 cho Power 6/55, 45 cho Mega 6/45, 35 cho Power 5/35).
        num_balls: Số lượng bóng chính trong 1 kỳ quay (6 hoặc 5).
        window_len: Độ dài cửa sổ trượt lịch sử (mặc định 150 kỳ gần nhất).

    Returns:
        Dict với khóa (A, B) và giá trị là dict chứa các chỉ số thống kê:
        - n_a: Số lần bóng A xuất hiện ở kỳ t-1.
        - n_b: Số lần bóng B xuất hiện ở kỳ t.
        - n_ab: Số lần chuyển tiếp đồng thời A_{t-1} -> B_t.
        - prob: Xác suất có điều kiện P(B_t | A_{t-1}) = n_ab / max(1, n_a).
        - prob_prior: Xác suất tiền nghiệm P_0(B) = n_b / total_transitions.
        - expected: Kỳ vọng xuất hiện độc lập E_AB = n_a * P_0(B).
        - std: Độ lệch chuẩn nhị thức sigma_AB = sqrt(n_a * P_0(B) * (1 - P_0(B)) + 1e-9).
        - z_score: Điểm chuẩn hóa Z(A -> B) = (n_ab - E_AB) / sigma_AB.
        - lift: Độ nâng xác suất Lift(A -> B) = P(B | A) / (P_0(B) + 1e-9).
        - is_repeat: True nếu A == B (cầu rơi lặp lại).
    """
    recent_records = records[-window_len:] if window_len > 0 and records else (records if records else [])
    total_transitions = max(0, len(recent_records) - 1)

    n_a_counts = [0] * (max_val + 1)
    n_b_counts = [0] * (max_val + 1)
    n_ab_counts: Dict[Tuple[int, int], int] = {}

    if total_transitions > 0:
        for idx in range(total_transitions):
            draw_prev = set(recent_records[idx].get("result", [])[:num_balls])
            draw_curr = set(recent_records[idx + 1].get("result", [])[:num_balls])

            valid_prev = [a for a in draw_prev if 1 <= a <= max_val]
            valid_curr = [b for b in draw_curr if 1 <= b <= max_val]

            for a in valid_prev:
                n_a_counts[a] += 1
            for b in valid_curr:
                n_b_counts[b] += 1
            for a in valid_prev:
                for b in valid_curr:
                    pair = (a, b)
                    n_ab_counts[pair] = n_ab_counts.get(pair, 0) + 1

    denom_total = max(1, total_transitions)
    matrix: Dict[Tuple[int, int], Dict[str, Any]] = {}

    for a in range(1, max_val + 1):
        n_a = n_a_counts[a]
        for b in range(1, max_val + 1):
            n_b = n_b_counts[b]
            n_ab = n_ab_counts.get((a, b), 0)

            # Conditional probability P(B_t | A_{t-1})
            prob = n_ab / max(1, n_a) if n_a > 0 else 0.0

            # Prior probability P_0(B)
            p0_b = n_b / denom_total if total_transitions > 0 else 0.0

            # Expected transitions under independence hypothesis
            e_ab = n_a * p0_b

            # Binomial standard deviation with numerical guard
            var_ab = n_a * p0_b * (1.0 - p0_b)
            sigma_ab = math.sqrt(max(0.0, var_ab) + 1e-9)

            # Binomial Z-score
            z_score = (n_ab - e_ab) / sigma_ab if sigma_ab > 0.0 else 0.0

            # Transition Lift
            lift = prob / (p0_b + 1e-9)

            matrix[(a, b)] = {
                "n_a": n_a,
                "n_b": n_b,
                "n_ab": n_ab,
                "prob": float(prob),
                "prob_prior": float(p0_b),
                "expected": float(e_ab),
                "std": float(sigma_ab),
                "z_score": float(z_score),
                "lift": float(lift),
                "is_repeat": (a == b),
            }

    return matrix


def calculate_vector_field_pull(
    records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    window_len: int = 150,
) -> Dict[int, Dict[str, float]]:
    """
    Tính toán Trường lực hấp dẫn Vector (Vector Field Pull) tác động từ tập số nổ kỳ gần nhất
    lên từng bóng tiềm năng b in [1, max_val] cho kỳ quay kế tiếp.

    Args:
        records: Danh sách các bản ghi kỳ quay lịch sử.
        max_val: Giá trị bóng lớn nhất.
        num_balls: Số bóng chính trong 1 kỳ quay.
        window_len: Cửa sổ trượt tính toán ma trận chuyển tiếp.

    Returns:
        Dict {b: {
            "max_pull_lift": float,
            "sum_z_score": float,
            "repulsion_penalty": float,
            "repeat_momentum": float,
        }}
    """
    latest_draw = records[-1].get("result", [])[:num_balls] if records else []
    s_latest = [b for b in latest_draw if 1 <= b <= max_val]

    # Handle edge case: empty records or empty latest draw
    if not s_latest:
        return {
            b: {
                "max_pull_lift": 1.0,
                "sum_z_score": 0.0,
                "repulsion_penalty": 1.0,
                "repeat_momentum": 0.0,
            }
            for b in range(1, max_val + 1)
        }

    matrix = build_transition_matrix(records, max_val=max_val, num_balls=num_balls, window_len=window_len)
    pulls: Dict[int, Dict[str, float]] = {}
    s_latest_set = set(s_latest)

    for b in range(1, max_val + 1):
        lifts = [matrix[(a, b)]["lift"] for a in s_latest if (a, b) in matrix]
        z_scores = [matrix[(a, b)]["z_score"] for a in s_latest if (a, b) in matrix]

        max_pull_lift = max(lifts) if lifts else 1.0
        sum_z_score = sum(max(0.0, z) for z in z_scores) if z_scores else 0.0
        repulsion_penalty = min(lifts) if lifts else 1.0

        repeat_momentum = (
            matrix[(b, b)]["lift"]
            if (b in s_latest_set and (b, b) in matrix)
            else 0.0
        )

        pulls[b] = {
            "max_pull_lift": round(float(max_pull_lift), 4),
            "sum_z_score": round(float(sum_z_score), 4),
            "repulsion_penalty": round(float(repulsion_penalty), 4),
            "repeat_momentum": round(float(repeat_momentum), 4),
        }

    return pulls


def extract_significant_transition_rules(
    records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    min_z: float = 1.5,
    max_rules: int = 8,
    window_len: int = 150,
) -> Dict[str, Any]:
    """
    Trích xuất các luật chuyển tiếp liên kỳ có ý nghĩa thống kê xuất phát từ kỳ quay gần nhất:
    - top_pull_rules: Các cặp (a -> b) có lực kéo mạnh (Z >= min_z), xếp hạng giảm dần theo Z và Lift.
    - top_repulsion_rules: Các cặp (a -> b) có lực kỵ nhau/triệt tiêu (Z <= -min_z), xếp hạng tăng dần theo Z.

    Args:
        records: Danh sách các bản ghi kỳ quay lịch sử.
        max_val: Giá trị bóng lớn nhất.
        num_balls: Số bóng chính.
        min_z: Ngưỡng ý nghĩa thống kê tối thiểu (mặc định 1.5).
        max_rules: Số lượng luật tối đa xuất ra cho mỗi loại (mặc định 8).
        window_len: Độ dài cửa sổ trượt.

    Returns:
        Dict:
        {
            "latest_draw_numbers": List[int],
            "top_pull_rules": List[Dict],
            "top_repulsion_rules": List[Dict],
        }
    """
    latest_draw = records[-1].get("result", [])[:num_balls] if records else []
    s_latest = sorted([b for b in latest_draw if 1 <= b <= max_val])

    if not s_latest or len(records) < 2:
        return {
            "latest_draw_numbers": s_latest,
            "top_pull_rules": [],
            "top_repulsion_rules": [],
        }

    matrix = build_transition_matrix(records, max_val=max_val, num_balls=num_balls, window_len=window_len)

    pull_rules: List[Dict[str, Any]] = []
    repulsion_rules: List[Dict[str, Any]] = []

    for a in s_latest:
        for b in range(1, max_val + 1):
            if a == b:
                # Repeat/momentum is handled separately; rules focus on inter-ball transitions
                continue

            cell = matrix.get((a, b))
            if not cell:
                continue

            z = cell["z_score"]
            lift = cell["lift"]
            n_ab = cell["n_ab"]
            n_a = cell["n_a"]

            pct = round((n_ab / max(1, n_a)) * 100.0, 1)
            hits_str = f"{n_ab}/{n_a} ({pct:.1f}%)"

            if z >= min_z:
                strength = "Cực Mạnh" if z >= 2.5 else "Mạnh"
                pull_rules.append({
                    "from_ball": int(a),
                    "to_ball": int(b),
                    "lift": round(float(lift), 2),
                    "z_score": round(float(z), 2),
                    "historical_hits": hits_str,
                    "strength": strength,
                })

            if z <= -min_z:
                warning = "Kỵ nhau mạnh — Nên loại bỏ" if z <= -2.0 else "Xung khắc nhẹ"
                repulsion_rules.append({
                    "from_ball": int(a),
                    "to_ball": int(b),
                    "lift": round(float(lift), 2),
                    "z_score": round(float(z), 2),
                    "historical_hits": hits_str,
                    "warning": warning,
                })

    # Sort pull rules: descending by z_score, then descending by lift
    pull_rules.sort(key=lambda r: (-r["z_score"], -r["lift"]))
    top_pull = pull_rules[:max_rules]

    # Sort repulsion rules: ascending by z_score (most negative first), then lift
    repulsion_rules.sort(key=lambda r: (r["z_score"], r["lift"]))
    top_repulsion = repulsion_rules[:max_rules]

    return {
        "latest_draw_numbers": s_latest,
        "top_pull_rules": top_pull,
        "top_repulsion_rules": top_repulsion,
    }
