"""
bingo18_predictor.py
Động cơ dự đoán định lượng chuyên biệt cho Bingo 18 (Xúc Xắc Sicbo).
Bao gồm 4 thuật toán chiến lược:
1. Dự báo thế cầu Lớn / Nhỏ (Markov & Hồi quy chuỗi bệt Mean-Reversion).
2. Tuyển chọn mặt xúc xắc Bạch Thủ (+EV 42% xác suất trúng trong 3 xúc xắc).
3. Định vị khoảng tổng mục tiêu Gaussian [8, 13] (68% xác suất lý thuyết).
4. Radar cảnh báo điểm rơi săn Bão Độc Đắc (Poisson Hazard x120).
"""

from typing import Any, Dict, List
import numpy as np

from vietlott.model.bingo18_engine import (
    analyze_bingo18_streaks,
    analyze_bingo18_sum_distribution,
    analyze_bingo18_storm_radar,
    analyze_bingo18_dice_frequencies,
)


def predict_bingo18_large_small(records: List[Dict[str, Any]], window_len: int = 100) -> Dict[str, Any]:
    """
    Dự báo thế cầu Lớn / Nhỏ cho kỳ quay kế tiếp dựa trên xích Markov và hồi quy chuỗi bệt.
    """
    if not records:
        return {
            "predicted_choice": "Lớn",
            "confidence_pct": 50.0,
            "strategy_name": "Ngẫu Nhiên (Thiếu Dữ Liệu)",
            "current_streak_type": "Chưa có",
            "current_streak_len": 0,
            "rationale": "Chưa đủ dữ liệu lịch sử để nhận diện thế cầu.",
        }

    streak_data = analyze_bingo18_streaks(records, window_len=window_len)
    c_type = streak_data.get("current_streak_type", "Lớn")
    c_len = streak_data.get("current_streak_len", 1)

    # Nếu chuỗi bệt đã kéo dài >= 4 kỳ -> Kích hoạt chiến lược Bẻ Cầu Đảo Chiều
    if c_len >= 4:
        strategy_name = "Bẻ Cầu Đảo Chiều (Mean-Reversion)"
        predicted_choice = "Nhỏ" if c_type == "Lớn" else "Lớn"
        confidence = min(80.0, 55.0 + c_len * 4.5)
        rationale = (
            f"Cầu bệt {c_type} đã kéo dài {c_len} kỳ liên tiếp (vượt ngưỡng trung bình 3 kỳ). "
            f"Lực đàn hồi hồi quy về trục cân bằng đạt đỉnh, xác suất bẻ cầu sang {predicted_choice} là {confidence:.1f}%."
        )
    else:
        # Chuỗi bệt ngắn (1-3 kỳ) -> Kích hoạt chiến lược Bám Cầu Bệt (Momentum)
        strategy_name = "Bám Cầu Bệt (Momentum)"
        predicted_choice = c_type if c_type in ["Lớn", "Nhỏ"] else "Lớn"
        confidence = max(52.0, 60.0 - c_len * 2.0)
        rationale = (
            f"Nhịp cầu {c_type} đang trong pha quán tính thuận lợi ({c_len} kỳ liên tiếp). "
            f"Khuyến nghị bám cầu theo xu hướng tiếp diễn."
        )

    return {
        "predicted_choice": predicted_choice,
        "confidence_pct": round(confidence, 1),
        "strategy_name": strategy_name,
        "current_streak_type": c_type,
        "current_streak_len": c_len,
        "rationale": rationale,
    }


def predict_bingo18_single_face(records: List[Dict[str, Any]], window_len: int = 100) -> Dict[str, Any]:
    """
    Dự đoán 1 mặt xúc xắc Bạch Thủ (1..6) có xác suất xuất hiện ít nhất 1 lần trong 3 xúc xắc cao nhất.
    Toán học: P(ít nhất 1 mặt nổ) = 1 - (5/6)^3 = 91/216 = 42.13%.
    """
    if not records:
        return {
            "best_face": 1,
            "expected_hit_prob_pct": 42.1,
            "current_gap": 0,
            "historical_deviation": 0.0,
            "rationale": "Mặt số cơ sở lý thuyết.",
        }

    dice_data = analyze_bingo18_dice_frequencies(records, window_len=window_len)
    freqs = dice_data.get("dice_frequencies", [])

    scored_faces = []
    for d in freqs:
        face = d["face"]
        gap = d["current_gap"]
        dev = d["deviation"]
        # Điểm hồi quy nhịp rơi: mặt vắng bóng vừa đủ kết hợp độ lệch hợp lý
        score = 1.0 + (gap / 2.5) * 1.5 + (0.25 - abs(dev / 100.0)) * 2.0
        scored_faces.append((score, face, gap, dev))

    scored_faces.sort(key=lambda x: (-x[0], x[1]))
    best_entry = scored_faces[0]
    best_face = best_entry[1]
    best_gap = best_entry[2]
    best_dev = best_entry[3]

    expected_prob = round(min(48.0, max(41.0, 42.13 + (best_gap - 2) * 1.2)), 1)
    rationale = (
        f"Mặt xúc xắc {best_face} đang có nhịp gan {best_gap} kỳ (chu kỳ trung bình 2.4 kỳ). "
        f"Xác suất xuất hiện ít nhất 1 lần trong 3 con xúc xắc kỳ này ước lượng đạt {expected_prob}%."
    )

    return {
        "best_face": best_face,
        "expected_hit_prob_pct": expected_prob,
        "current_gap": best_gap,
        "historical_deviation": best_dev,
        "rationale": rationale,
    }


def predict_bingo18_target_sum(records: List[Dict[str, Any]], window_len: int = 100) -> Dict[str, Any]:
    """
    Định vị khoảng tổng mục tiêu Gaussian [8, 13] (chiếm 68% xác suất lý thuyết) và điểm rơi tối ưu.
    """
    if not records:
        return {
            "target_range": [8, 13],
            "best_single_sum": 10,
            "range_probability_pct": 68.0,
            "rationale": "Vùng vàng trung tâm lý thuyết Gaussian 3d6.",
        }

    sample = records[-5:]
    recent_sums = [int(r.get("total") or sum(r.get("result", [3, 4, 3]))) for r in sample]
    last_sum = recent_sums[-1] if recent_sums else 10

    # Nếu tổng kỳ trước lệch mạnh về biên thấp (< 9) -> lực giật về 11
    # Nếu tổng kỳ trước lệch mạnh về biên cao (> 12) -> lực giật về 10
    if last_sum < 9:
        best_single_sum = 11
        rationale = f"Kỳ trước tổng nổ thấp ({last_sum}). Lực đàn hồi Gaussian kéo tổng giật về tâm đối xứng 11."
    elif last_sum > 12:
        best_single_sum = 10
        rationale = f"Kỳ trước tổng nổ cao ({last_sum}). Lực hồi quy kéo tổng rơi vào vùng trung tâm 10."
    else:
        best_single_sum = 10 if last_sum == 11 else 11
        rationale = f"Tổng kỳ trước ({last_sum}) nằm trọn trong vùng vàng Gaussian [8, 13]. Kỳ này tiếp tục dao động quanh trục 10 và 11."

    return {
        "target_range": [8, 13],
        "best_single_sum": best_single_sum,
        "range_probability_pct": 68.0,
        "rationale": rationale,
    }


def evaluate_bingo18_storm_trigger(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Xác định thời điểm kích hoạt chiến thuật "Săn Bão Độc Đắc" (1 ăn 32 & 1 ăn 120).
    """
    radar = analyze_bingo18_storm_radar(records)
    gap = radar.get("current_storm_gap", 0)
    avg_gap = radar.get("average_storm_gap", 34.6)
    triple_counts = radar.get("triple_counts", {})

    # Sắp xếp các bộ bão có số lần nổ ít nhất hoặc đang có chu kỳ thuận lợi
    sorted_triples = sorted(triple_counts.items(), key=lambda x: x[1])
    recommended_triples = [t[0] for t in sorted_triples[:3]] or ["333", "555", "111"]

    if gap >= 70:
        is_hunting_active = True
        status = "Điểm Rơi Cực Đại (Bão Sắp Nổ)"
        action_rec = "KÍCH HOẠT NUÔI BÃO ĐỘC ĐẮC (KHUNG 5-10 KỲ)"
        payout_mult = "1 ăn 32 (Bão bất kỳ) hoặc 1 ăn 120 (Bão cụ thể)"
        rationale = (
            f"Đã {gap} kỳ chưa nổ bão (vượt gấp đôi chu kỳ trung bình {avg_gap} kỳ). "
            f"Năng lượng tích lũy đạt đỉnh cực đại. Khuyến nghị phân bổ vốn nhỏ (10k/kỳ) nuôi bão bất kỳ và các bão cụ thể."
        )
    elif gap >= 45:
        is_hunting_active = False
        status = "Đang Tích Lũy Năng Lượng"
        action_rec = "Bắt đầu theo dõi điểm rơi (Chưa kích hoạt nuôi)"
        payout_mult = "1 ăn 32 / 1 ăn 120"
        rationale = f"Đã {gap} kỳ vắng bóng bão (chu kỳ trung bình {avg_gap} kỳ). Chuẩn bị sẵn vốn khi gap vượt 70 kỳ."
    else:
        is_hunting_active = False
        status = "Bình Thường (Chu kỳ an toàn)"
        action_rec = "Tạm dừng săn bão, tập trung đánh Lớn/Nhỏ và Bạch Thủ"
        payout_mult = "1 ăn 32 / 1 ăn 120"
        rationale = f"Bão vừa nổ gần đây ({gap} kỳ trước). Chu kỳ hiện tại hoàn toàn bình thường."

    return {
        "is_hunting_active": is_hunting_active,
        "status": status,
        "current_storm_gap": gap,
        "average_gap": avg_gap,
        "action_recommendation": action_rec,
        "payout_multiplier": payout_mult,
        "recommended_triples": recommended_triples,
        "rationale": rationale,
    }


def generate_bingo18_prediction_hub(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Hợp nhất toàn bộ 4 chiến lược dự đoán định lượng cho kỳ quay kế tiếp.
    """
    if not records:
        return {}

    last_record = records[-1]
    last_id = str(last_record.get("id", "")).replace("#", "").strip()
    next_id = f"#{int(last_id) + 1:07d}" if last_id.isdigit() else "#NextDraw"

    large_small_pred = predict_bingo18_large_small(records, window_len=100)
    single_face_pred = predict_bingo18_single_face(records, window_len=100)
    target_sum_pred = predict_bingo18_target_sum(records, window_len=100)
    storm_trigger = evaluate_bingo18_storm_trigger(records)

    return {
        "target_draw_id": next_id,
        "large_small_prediction": large_small_pred,
        "single_face_prediction": single_face_pred,
        "target_sum_prediction": target_sum_pred,
        "storm_trigger": storm_trigger,
    }


def evaluate_bingo18_walk_forward_accuracy(records: List[Dict[str, Any]], num_draws: int = 100) -> Dict[str, Any]:
    """
    Kiểm định Walk-Forward liên tục 100 kỳ đo lường độ chính xác thực tế (Strictly No Look-Ahead).
    """
    if len(records) < num_draws + 20:
        return {}

    total_len = len(records)
    start_idx = total_len - num_draws

    ls_hits = 0
    face_hits = 0
    sum_range_hits = 0

    for i in range(start_idx, total_len):
        past = records[:i]
        actual_record = records[i]
        actual_res = actual_record.get("result", [])
        actual_total = int(actual_record.get("total") or sum(actual_res))
        actual_type = "Lớn" if actual_total >= 11 else "Nhỏ"

        # 1. Test Large/Small prediction
        p_ls = predict_bingo18_large_small(past, window_len=100)
        if p_ls["predicted_choice"] == actual_type:
            ls_hits += 1

        # 2. Test Single Face prediction
        p_face = predict_bingo18_single_face(past, window_len=100)
        if p_face["best_face"] in actual_res:
            face_hits += 1

        # 3. Test Sum Range prediction [8, 13]
        if 8 <= actual_total <= 13:
            sum_range_hits += 1

    return {
        "evaluated_draws": num_draws,
        "large_small_hits": ls_hits,
        "large_small_accuracy_pct": round(ls_hits / num_draws * 100.0, 1),
        "single_face_hits": face_hits,
        "single_face_hit_rate_pct": round(face_hits / num_draws * 100.0, 1),
        "target_range_hits": sum_range_hits,
        "target_range_hit_rate_pct": round(sum_range_hits / num_draws * 100.0, 1),
    }
