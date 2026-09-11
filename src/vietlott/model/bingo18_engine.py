"""
bingo18_engine.py
Module phân tích định lượng chuyên sâu cho Bingo 18 (Xúc Xắc Sicbo).
Bao gồm:
- Phân tích chuỗi bệt Lớn/Nhỏ (Roadmap), đo xác suất bẻ cầu.
- Phân phối chuông tổng Gaussian 3..18 so sánh với phân phối nhị thức 3d6.
- Radar cảnh báo săn bão (Triple / Storm Hazard Detection).
- Tần suất 6 mặt xúc xắc và ma trận nổ cặp đôi.
"""

from collections import Counter, defaultdict
import itertools
import math
from typing import Any, Dict, List, Tuple
import numpy as np

# Phân phối lý thuyết tổ hợp của 3 con xúc xắc 6 mặt (3d6 = 6^3 = 216 tổ hợp)
THEORETICAL_3D6_SUMS: Dict[int, int] = {
    3: 1,    # (1,1,1)
    4: 3,    # (1,1,2) x3
    5: 6,    # (1,1,3) x3, (1,2,2) x3
    6: 10,   # (1,1,4) x3, (1,2,3) x6, (2,2,2) x1
    7: 15,
    8: 21,
    9: 25,
    10: 27,  # Đỉnh 1: 12.5%
    11: 27,  # Đỉnh 2: 12.5%
    12: 25,
    13: 21,
    14: 15,
    15: 10,
    16: 6,
    17: 3,
    18: 1    # (6,6,6)
}

TOTAL_3D6_COMBINATIONS = 216


def _extract_triple_flag(result: List[int]) -> bool:
    """Xác định kết quả có phải là Bão (Triple / 3 mặt xúc xắc trùng nhau) hay không."""
    return isinstance(result, list) and len(result) == 3 and (result[0] == result[1] == result[2])


def _extract_large_small_type(total: int, explicit_type: str = None) -> str:
    """Chuẩn hóa phân loại thế cầu Lớn / Nhỏ / Hòa."""
    if explicit_type in ["Lớn", "Nhỏ", "Hòa"]:
        return explicit_type
    if total >= 12:
        return "Lớn"
    if total <= 9:
        return "Nhỏ"
    return "Hòa"


def analyze_bingo18_streaks(records: List[Dict[str, Any]], window_len: int = 100) -> Dict[str, Any]:
    """
    Phân tích chuỗi bệt Lớn / Nhỏ (Sicbo Roadmap) trên cửa sổ window_len kỳ gần nhất.
    """
    if not records:
        return {
            "roadmap": [],
            "current_streak_type": "Chưa có",
            "current_streak_len": 0,
            "break_probability_pct": 50.0,
            "max_streak_observed": 0,
            "streak_distribution": {},
            "transition_matrix": {},
            "total_large": 0,
            "total_small": 0,
            "total_draws_analyzed": 0,
        }

    # Đảm bảo thứ tự thời gian tăng dần từ quá khứ đến hiện tại
    sample = records[-window_len:]
    roadmap = []
    
    for r in sample:
        res = r.get("result", [])
        tot = r.get("total")
        if tot is None and res:
            tot = sum(res)
        tot_val = int(tot) if tot is not None else 0
        c_type = _extract_large_small_type(tot_val, r.get("large_small"))
        is_triple = bool(r.get("is_triple")) or _extract_triple_flag(res)
        draw_id = str(r.get("id", "")).replace("#", "").strip()
        date_str = str(r.get("date", ""))
        
        roadmap.append({
            "drawId": draw_id,
            "date": date_str,
            "result": res,
            "total": tot_val,
            "type": c_type,
            "isTriple": is_triple,
        })

    # Đếm chuỗi bệt
    streaks = []
    current_type = None
    current_len = 0
    
    # Ma trận chuyển trạng thái
    trans_counts = defaultdict(Counter)

    for i, item in enumerate(roadmap):
        t = item["type"]
        if i > 0:
            prev_t = roadmap[i - 1]["type"]
            trans_counts[prev_t][t] += 1

        if current_type is None:
            current_type = t
            current_len = 1
        elif t == current_type:
            current_len += 1
        else:
            streaks.append((current_type, current_len))
            current_type = t
            current_len = 1

    if current_type is not None:
        streaks.append((current_type, current_len))

    active_streak_type = current_type or "Chưa có"
    active_streak_len = current_len

    # Thống kê phân bố độ dài chuỗi
    streak_len_counter = Counter(s[1] for s in streaks)
    max_streak = max((s[1] for s in streaks), default=0)

    # Ước lượng xác suất bẻ cầu (Mean-reversion break probability)
    # Tần suất chuỗi cùng loại có độ dài >= active_streak_len bị bẻ tại điểm này
    same_type_streaks = [s[1] for s in streaks if s[0] == active_streak_type]
    if same_type_streaks:
        longer_count = sum(1 for sl in same_type_streaks if sl > active_streak_len)
        at_least_count = sum(1 for sl in same_type_streaks if sl >= active_streak_len)
        if at_least_count > 0:
            break_prob = (1.0 - (longer_count / at_least_count)) * 100.0
        else:
            break_prob = min(95.0, 50.0 + active_streak_len * 7.5)
    else:
        break_prob = min(95.0, 50.0 + active_streak_len * 7.5)

    break_prob = round(max(50.0, min(95.0, break_prob)), 1)

    # Đếm tổng Lớn / Nhỏ trong cửa sổ
    total_large = sum(1 for x in roadmap if x["type"] == "Lớn")
    total_small = sum(1 for x in roadmap if x["type"] == "Nhỏ")

    # Format ma trận chuyển tiếp
    fmt_trans = {}
    for from_t in ["Lớn", "Nhỏ"]:
        tot_from = sum(trans_counts[from_t].values()) or 1
        fmt_trans[from_t] = {
            to_t: round((trans_counts[from_t][to_t] / tot_from) * 100.0, 1)
            for to_t in ["Lớn", "Nhỏ", "Hòa"]
        }

    return {
        "roadmap": roadmap,
        "current_streak_type": active_streak_type,
        "current_streak_len": active_streak_len,
        "break_probability_pct": break_prob,
        "max_streak_observed": max_streak,
        "streak_distribution": {f"{k}_ky": v for k, v in sorted(streak_len_counter.items())},
        "transition_matrix": fmt_trans,
        "total_large": total_large,
        "total_small": total_small,
        "total_draws_analyzed": len(roadmap),
    }


def analyze_bingo18_sum_distribution(records: List[Dict[str, Any]], window_len: int = 1000) -> Dict[str, Any]:
    """
    Phân tích phân phối tổng Gaussian 3..18 so sánh với phân phối lý thuyết 3d6.
    """
    if not records:
        return {"distribution": [], "mean_sum": 0.0, "std_sum": 0.0, "top_hot_sums": []}

    sample = records[-window_len:]
    sums_list = []
    for r in sample:
        tot = r.get("total")
        if tot is None and r.get("result"):
            tot = sum(r["result"])
        if tot is not None:
            sums_list.append(int(tot))

    if not sums_list:
        return {"distribution": [], "mean_sum": 0.0, "std_sum": 0.0, "top_hot_sums": []}

    sum_counts = Counter(sums_list)
    total_samples = len(sums_list)

    dist = []
    for s in range(3, 19):
        theo_cnt = THEORETICAL_3D6_SUMS.get(s, 0)
        theo_pct = round((theo_cnt / TOTAL_3D6_COMBINATIONS) * 100.0, 2)
        emp_cnt = sum_counts.get(s, 0)
        emp_pct = round((emp_cnt / total_samples) * 100.0, 2)
        deviation = round(emp_pct - theo_pct, 2)
        
        dist.append({
            "sum": s,
            "count": emp_cnt,
            "empirical_pct": emp_pct,
            "theoretical_pct": theo_pct,
            "deviation": deviation,
        })

    mean_sum = round(float(np.mean(sums_list)), 2)
    std_sum = round(float(np.std(sums_list)), 2)
    top_hot = sorted(dist, key=lambda x: x["count"], reverse=True)[:3]

    return {
        "distribution": dist,
        "mean_sum": mean_sum,
        "std_sum": std_sum,
        "theoretical_mean": 10.5,
        "theoretical_std": 2.96,
        "total_draws_analyzed": total_samples,
        "top_hot_sums": [x["sum"] for x in top_hot],
    }


def analyze_bingo18_storm_radar(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Radar cảnh báo săn bão (Triple Hazard Detection) trên toàn bộ lịch sử.
    Xác suất lý thuyết bão bất kỳ: 6/216 = 2.78% (chu kỳ trung bình ~36 kỳ).
    """
    if not records:
        return {
            "current_storm_gap": 0,
            "average_storm_gap": 36.0,
            "hazard_level": {"level": "normal", "name": "Bình Thường", "color": "slate", "alert": False},
            "last_storm": None,
            "recent_storms": [],
            "triple_counts": {},
            "total_storms_found": 0,
        }

    storms = []
    current_gap = 0
    last_storm_info = None

    for i, r in enumerate(records):
        res = r.get("result", [])
        is_triple = bool(r.get("is_triple")) or _extract_triple_flag(res)
        draw_id = str(r.get("id", "")).replace("#", "").strip()
        date_str = str(r.get("date", ""))

        if is_triple:
            triple_val = res[0] if len(res) == 3 else 0
            storm_record = {
                "drawId": draw_id,
                "date": date_str,
                "triple": res,
                "tripleValue": triple_val,
                "gapSincePrevious": current_gap,
                "index": i,
            }
            storms.append(storm_record)
            last_storm_info = storm_record
            current_gap = 0
        else:
            current_gap += 1

    # Thống kê chu kỳ nhịp nổ bão trong lịch sử
    if len(storms) >= 2:
        gaps = [s["gapSincePrevious"] for s in storms[1:]]
        avg_gap = round(float(np.mean(gaps)), 1)
    else:
        avg_gap = 36.0

    # Phân loại cấp độ nguy cơ bão (Hazard Level)
    if current_gap >= 70:
        hazard = {
            "level": "critical",
            "name": "Điểm Rơi Cực Đại (Nguy cơ nổ bão rất cao)",
            "color": "rose",
            "alert": True,
            "badge": "bg-rose-500/20 text-rose-300 border-rose-500/40",
            "rationale": f"Đã {current_gap} kỳ chưa xuất hiện bão (vượt gấp đôi chu kỳ trung bình {avg_gap} kỳ). Năng lượng tích lũy đạt đỉnh.",
        }
    elif current_gap >= 45:
        hazard = {
            "level": "accumulating",
            "name": "Đang Tích Lũy (Vượt chu kỳ trung bình)",
            "color": "amber",
            "alert": False,
            "badge": "bg-amber-500/20 text-amber-300 border-amber-500/40",
            "rationale": f"Đã {current_gap} kỳ chưa nổ bão (chu kỳ trung bình {avg_gap} kỳ). Bắt đầu theo dõi điểm rơi.",
        }
    else:
        hazard = {
            "level": "normal",
            "name": "Bình Thường (Chu kỳ an toàn)",
            "color": "slate",
            "alert": False,
            "badge": "bg-slate-800 text-slate-300 border-slate-700",
            "rationale": f"Số kỳ vắng bóng bão hiện tại là {current_gap} kỳ (dưới chu kỳ trung bình {avg_gap} kỳ).",
        }

    # Đếm số lần nổ từng loại bão cụ thể: 111, 222, 333, 444, 555, 666
    triple_counter = Counter()
    for s in storms:
        val = s.get("tripleValue")
        if 1 <= val <= 6:
            triple_counter[val] += 1

    fmt_triple_counts = {
        f"{v}{v}{v}": triple_counter.get(v, 0)
        for v in range(1, 7)
    }

    recent_storms_formatted = [
        {
            "drawId": s["drawId"],
            "date": s["date"],
            "triple": s["triple"],
            "gap": s["gapSincePrevious"],
        }
        for s in reversed(storms[-5:])
    ]

    return {
        "current_storm_gap": current_gap,
        "average_storm_gap": avg_gap,
        "theoretical_storm_gap": 36.0,
        "hazard_level": hazard,
        "last_storm": last_storm_info,
        "recent_storms": recent_storms_formatted,
        "triple_counts": fmt_triple_counts,
        "total_storms_found": len(storms),
    }


def analyze_bingo18_dice_frequencies(records: List[Dict[str, Any]], window_len: int = 500) -> Dict[str, Any]:
    """
    Phân tích tần suất 6 mặt xúc xắc (1..6) và các cặp đôi nổ chung.
    """
    if not records:
        return {"dice_frequencies": [], "top_pairs": []}

    sample = records[-window_len:]
    dice_counter = Counter()
    pair_counter = Counter()
    cur_gaps = {d: len(sample) for d in range(1, 7)}
    prev_seen = {}

    for t, r in enumerate(reversed(sample)):
        res = r.get("result", [])
        dice_counter.update(res)
        for b in set(res):
            if b not in prev_seen:
                cur_gaps[b] = t
                prev_seen[b] = t
        if len(res) >= 2:
            unique_res = sorted(list(set(res)))
            for p in itertools.combinations(unique_res, 2):
                pair_counter[p] += 1

    total_dice_rolls = len(sample) * 3 or 1
    theo_face_pct = round((1.0 / 6.0) * 100.0, 2)

    freqs = []
    for d in range(1, 7):
        cnt = dice_counter.get(d, 0)
        emp_pct = round((cnt / total_dice_rolls) * 100.0, 2)
        dev = round(emp_pct - theo_face_pct, 2)
        status = "Nóng" if dev >= 1.5 else ("Lạnh" if dev <= -1.5 else "Bình thường")
        
        freqs.append({
            "face": d,
            "count": cnt,
            "empirical_pct": emp_pct,
            "theoretical_pct": theo_face_pct,
            "deviation": dev,
            "current_gap": cur_gaps.get(d, 0),
            "status": status,
        })

    top_pairs_formatted = [
        {"pair": list(p), "count": cnt}
        for p, cnt in pair_counter.most_common(5)
    ]

    return {
        "dice_frequencies": freqs,
        "top_pairs": top_pairs_formatted,
        "total_draws_analyzed": len(sample),
    }


def generate_bingo18_comprehensive_analytics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tổng hợp toàn bộ phân tích định lượng cho Bingo 18 sẵn sàng nạp vào Web UI JSON.
    """
    if not records:
        return {}

    total_draws = len(records)
    latest_draws = records[-100:][::-1]

    streak_analytics = analyze_bingo18_streaks(records, window_len=100)
    sum_distribution = analyze_bingo18_sum_distribution(records, window_len=1000)
    storm_radar = analyze_bingo18_storm_radar(records)
    dice_frequencies = analyze_bingo18_dice_frequencies(records, window_len=500)

    # Thống kê tổng số Lớn / Nhỏ trên 1.000 kỳ gần nhất
    sample_1k = records[-1000:]
    large_small_counter = Counter()
    for r in sample_1k:
        tot = r.get("total") or (sum(r.get("result", [])) if r.get("result") else 0)
        c_type = _extract_large_small_type(int(tot), r.get("large_small"))
        large_small_counter[c_type] += 1

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0] if latest_draws else {},
        "history": latest_draws,
        "streak_analytics": streak_analytics,
        "sum_distribution": sum_distribution,
        "storm_radar": storm_radar,
        "dice_frequencies": dice_frequencies,
        "size_distribution": dict(large_small_counter),
    }
