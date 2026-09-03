#!/usr/bin/env python
"""
render_web_data.py
Generates a lightweight, optimized JSON file (docs/data/vietlott_summary.json)
for the static Web UI. Includes latest draws & deep analytical stats:
- Gap / Skip Analysis (Số gan, chu kỳ nhịp, kỷ lục gan)
- Co-occurrence / Top Pairs & Triples (Cặp số hay về cùng nhau)
- Sum Distribution & Bell Curve (Tổng giải, kỳ vọng toán học)
- Pattern & Streaks (Tỷ lệ số liền kề, tỷ lệ số lặp lại kỳ trước, dải đầu số)
- Keno & Bingo distribution metrics
"""

import itertools
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DATA_DIR = DOCS_DIR / "data"


def read_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Read JSONL file and return list of dicts with unique IDs."""
    if not file_path.exists():
        return []
    records = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    clean_id = str(r.get("id", "")).replace("#", "").strip()
                    records[clean_id] = r
                except json.JSONDecodeError:
                    continue
    return sorted(records.values(), key=lambda x: (x.get("date", ""), str(x.get("id", ""))))


def calculate_gap_analysis(records: List[Dict], max_val: int, num_balls: int) -> List[Dict[str, Any]]:
    """
    Calculate Gap / Skip analysis for all numbers.
    - current_gap: draws since last appearance
    - max_gap: longest historical drought
    - avg_gap: average interval between appearances
    - is_heating_up: if current_gap >= avg_gap
    """
    total_draws = len(records)
    gap_info = []

    for num in range(1, max_val + 1):
        last_idx = None
        max_gap = 0
        appearances = 0

        for idx, r in enumerate(records):
            res = r.get("result", [])[:num_balls]
            if num in res:
                appearances += 1
                if last_idx is not None:
                    gap = idx - last_idx - 1
                    if gap > max_gap:
                        max_gap = gap
                elif idx > max_gap:
                    max_gap = idx
                last_idx = idx

        current_gap = (total_draws - 1 - last_idx) if last_idx is not None else total_draws
        if current_gap > max_gap:
            max_gap = current_gap

        avg_gap = round(total_draws / appearances, 1) if appearances > 0 else total_draws
        heat_ratio = round(current_gap / avg_gap, 2) if avg_gap > 0 else 0

        gap_info.append({
            "number": num,
            "current_gap": current_gap,
            "max_gap": max_gap,
            "avg_gap": avg_gap,
            "appearances": appearances,
            "heat_ratio": heat_ratio,  # >= 1.0 means overdue / gan
        })

    return gap_info


def calculate_cooccurrence(records: List[Dict], num_balls: int, top_n_pairs: int = 15, top_n_triples: int = 10) -> Dict[str, Any]:
    """Calculate pairs and triples that appear together most frequently."""
    pair_counter = Counter()
    triple_counter = Counter()
    total_draws = len(records)

    for r in records:
        main_balls = sorted(r.get("result", [])[:num_balls])
        if len(main_balls) >= 2:
            for pair in itertools.combinations(main_balls, 2):
                pair_counter[pair] += 1
        if len(main_balls) >= 3 and total_draws <= 5000:  # triples for reasonable dataset sizes
            for triple in itertools.combinations(main_balls, 3):
                triple_counter[triple] += 1

    top_pairs = []
    for pair, cnt in pair_counter.most_common(top_n_pairs):
        top_pairs.append({
            "pair": list(pair),
            "count": cnt,
            "pct": round(cnt / total_draws * 100, 2) if total_draws else 0
        })

    top_triples = []
    for triple, cnt in triple_counter.most_common(top_n_triples):
        top_triples.append({
            "triple": list(triple),
            "count": cnt,
            "pct": round(cnt / total_draws * 100, 2) if total_draws else 0
        })

    return {
        "top_pairs": top_pairs,
        "top_triples": top_triples
    }


def calculate_sum_and_patterns(records: List[Dict], num_balls: int, max_val: int) -> Dict[str, Any]:
    """Calculate sum statistics, bell curve distribution, and pattern streaks."""
    if not records:
        return {}

    total_draws = len(records)
    sums = []
    has_consecutive_cnt = 0
    repeats_from_prev_cnt = 0
    total_repeats = 0
    decade_counter = Counter()

    for idx, r in enumerate(records):
        main_balls = sorted(r.get("result", [])[:num_balls])
        if not main_balls:
            continue

        s = sum(main_balls)
        sums.append(s)

        # Decade distribution
        for b in main_balls:
            decade = (b // 10) * 10
            decade_label = f"{decade:02d}-{decade+9:02d}" if decade < 50 else "50-55"
            decade_counter[decade_label] += 1

        # Consecutive pairs check (e.g. 12, 13)
        if any(main_balls[i+1] - main_balls[i] == 1 for i in range(len(main_balls) - 1)):
            has_consecutive_cnt += 1

        # Repeat from previous draw
        if idx > 0:
            prev_balls = set(records[idx-1].get("result", [])[:num_balls])
            common = set(main_balls).intersection(prev_balls)
            if common:
                repeats_from_prev_cnt += 1
                total_repeats += len(common)

    avg_sum = round(sum(sums) / len(sums), 1) if sums else 0
    sorted_sums = sorted(sums)
    median_sum = sorted_sums[len(sorted_sums) // 2] if sorted_sums else 0
    min_sum = min(sums) if sums else 0
    max_sum = max(sums) if sums else 0

    # Standard deviation
    variance = sum((x - avg_sum) ** 2 for x in sums) / len(sums) if sums else 0
    std_dev = round(math.sqrt(variance), 1)

    # Sum ranges / buckets
    if max_val == 55:  # Power 655
        bucket_defs = [
            ("< 120", lambda x: x < 120),
            ("120 - 139", lambda x: 120 <= x <= 139),
            ("140 - 159", lambda x: 140 <= x <= 159),
            ("160 - 179", lambda x: 160 <= x <= 179),
            ("180 - 199", lambda x: 180 <= x <= 199),
            (">= 200", lambda x: x >= 200),
        ]
    elif max_val == 45:  # Mega 645
        bucket_defs = [
            ("< 100", lambda x: x < 100),
            ("100 - 119", lambda x: 100 <= x <= 119),
            ("120 - 139", lambda x: 120 <= x <= 139),
            ("140 - 159", lambda x: 140 <= x <= 159),
            ("160 - 179", lambda x: 160 <= x <= 179),
            (">= 180", lambda x: x >= 180),
        ]
    else:  # Power 535
        bucket_defs = [
            ("< 60", lambda x: x < 60),
            ("60 - 79", lambda x: 60 <= x <= 79),
            ("80 - 99", lambda x: 80 <= x <= 99),
            ("100 - 119", lambda x: 100 <= x <= 119),
            (">= 120", lambda x: x >= 120),
        ]

    sum_distribution = []
    for label, fn in bucket_defs:
        cnt = sum(1 for s in sums if fn(s))
        sum_distribution.append({
            "range": label,
            "count": cnt,
            "pct": round(cnt / total_draws * 100, 1) if total_draws else 0
        })

    # Decade percentages
    total_ball_picks = total_draws * num_balls if total_draws else 1
    decades_stat = [
        {"decade": k, "count": v, "pct": round(v / total_ball_picks * 100, 1)}
        for k, v in sorted(decade_counter.items())
    ]

    return {
        "sum_stats": {
            "avg_sum": avg_sum,
            "median_sum": median_sum,
            "min_sum": min_sum,
            "max_sum": max_sum,
            "std_dev": std_dev,
            "safe_zone": f"{int(avg_sum - std_dev)} - {int(avg_sum + std_dev)}",
            "distribution": sum_distribution,
        },
        "patterns": {
            "consecutive_pct": round(has_consecutive_cnt / total_draws * 100, 1) if total_draws else 0,
            "repeat_from_prev_pct": round(repeats_from_prev_cnt / (total_draws - 1) * 100, 1) if total_draws > 1 else 0,
            "avg_repeat_per_draw": round(total_repeats / (total_draws - 1), 2) if total_draws > 1 else 0,
            "decade_distribution": decades_stat
        }
    }


def process_power(records: List[Dict], max_val: int, num_balls: int, has_special: bool = False) -> Dict[str, Any]:
    """Process Power 655, 645, 535 with full analytics."""
    if not records:
        return {}

    total_draws = len(records)
    latest_draws = records[-100:][::-1]

    # Frequency
    ball_counter = Counter()
    special_counter = Counter()

    for r in records:
        res = r.get("result", [])
        if has_special and len(res) > num_balls:
            main_balls = res[:num_balls]
            special_ball = res[num_balls]
            ball_counter.update(main_balls)
            special_counter.update([special_ball])
        else:
            ball_counter.update(res[:num_balls])

    freq_list = []
    for num in range(1, max_val + 1):
        cnt = ball_counter.get(num, 0)
        freq_list.append({
            "number": num,
            "count": cnt,
            "pct": round((cnt / total_draws * 100) if total_draws else 0, 2)
        })

    sorted_by_freq = sorted(freq_list, key=lambda x: x["count"], reverse=True)
    hot_numbers = sorted_by_freq[:10]
    cold_numbers = sorted_by_freq[-10:][::-1]

    # Odd/Even ratio in latest 50 draws
    odd_count = 0
    even_count = 0
    for r in latest_draws[:50]:
        res = r.get("result", [])[:num_balls]
        for b in res:
            if b % 2 == 0:
                even_count += 1
            else:
                odd_count += 1

    total_oe = (odd_count + even_count) or 1

    # Deep Analytics:
    gap_analysis = calculate_gap_analysis(records, max_val, num_balls)
    cooccurrence = calculate_cooccurrence(records, num_balls)
    sum_patterns = calculate_sum_and_patterns(records, num_balls, max_val)

    # Top overdue numbers (gan nhất hiện tại)
    top_overdue = sorted(gap_analysis, key=lambda x: x["current_gap"], reverse=True)[:10]

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
        "hot_numbers": hot_numbers,
        "cold_numbers": cold_numbers,
        "top_overdue": top_overdue,
        "gap_analysis": gap_analysis,
        "frequency": freq_list,
        "top_pairs": cooccurrence["top_pairs"],
        "top_triples": cooccurrence["top_triples"],
        "sum_stats": sum_patterns.get("sum_stats", {}),
        "patterns": sum_patterns.get("patterns", {}),
        "odd_even": {
            "odd_pct": round(odd_count / total_oe * 100, 1),
            "even_pct": round(even_count / total_oe * 100, 1),
        }
    }


def process_keno(records: List[Dict]) -> Dict[str, Any]:
    """Process Keno (100k+ draws, keep latest 100 + stats)."""
    if not records:
        return {}

    total_draws = len(records)
    latest_draws = records[-100:][::-1]

    sample_records = records[-1000:]
    counter = Counter()
    big_small_counter = Counter()
    odd_even_counter = Counter()

    for r in sample_records:
        counter.update(r.get("result", []))
        bs = r.get("big_small")
        oe = r.get("odd_even")
        if bs:
            big_small_counter.update([bs])
        if oe:
            odd_even_counter.update([oe])

    freq_list = []
    for num in range(1, 81):
        cnt = counter.get(num, 0)
        freq_list.append({
            "number": num,
            "count": cnt,
            "pct": round(cnt / len(sample_records) * 100, 2)
        })

    sorted_freq = sorted(freq_list, key=lambda x: x["count"], reverse=True)

    # Gap analysis on sample 1000 draws
    gap_analysis = calculate_gap_analysis(sample_records, 80, 20)
    top_overdue = sorted(gap_analysis, key=lambda x: x["current_gap"], reverse=True)[:10]

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
        "hot_numbers": sorted_freq[:10],
        "cold_numbers": sorted_freq[-10:][::-1],
        "top_overdue": top_overdue,
        "frequency": freq_list,
        "big_small_distribution": dict(big_small_counter.most_common(5)),
        "odd_even_distribution": dict(odd_even_counter.most_common(5)),
    }


def process_bingo18(records: List[Dict]) -> Dict[str, Any]:
    """Process Bingo 18."""
    if not records:
        return {}

    total_draws = len(records)
    latest_draws = records[-100:][::-1]

    sample_records = records[-1000:]
    counter = Counter()
    total_sum_counter = Counter()
    size_counter = Counter()

    for r in sample_records:
        res = r.get("result", [])
        counter.update(res)
        tot = r.get("total", sum(res) if res else 0)
        total_sum_counter.update([tot])
        sz = r.get("large_small")
        if sz:
            size_counter.update([sz])

    dice_freq = [{"number": i, "count": counter.get(i, 0)} for i in range(1, 7)]
    sum_dist = [{"total": s, "count": total_sum_counter.get(s, 0)} for s in sorted(total_sum_counter.keys())]

    # Gap analysis for numbers 1 to 6
    gap_analysis = calculate_gap_analysis(sample_records, 6, 3)

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
        "dice_frequency": dice_freq,
        "gap_analysis": gap_analysis,
        "sum_distribution": sum_dist,
        "size_distribution": dict(size_counter),
    }


def process_max3d(records: List[Dict]) -> Dict[str, Any]:
    """Process Max 3D and Max 3D Pro."""
    if not records:
        return {}

    total_draws = len(records)
    latest_draws = records[-50:][::-1]

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
    }


def main():
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Reading lottery data from {DATA_DIR}...")

    summary_data = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generator": "vietlott-data automated pipeline",
            "version": "2.0.0",
        },
        "products": {}
    }

    # 1. Power 6/55
    print("Processing Power 6/55 with deep analytics...")
    records_655 = read_jsonl(DATA_DIR / "power655.jsonl")
    summary_data["products"]["power_655"] = {
        "name": "Power 6/55",
        "description": "Chọn 6 số từ 1 đến 55. Trúng Jackpot 1 từ 30 Tỷ, Jackpot 2 từ 3 Tỷ.",
        "type": "lotto",
        "balls": 6,
        "max_number": 55,
        "has_special": True,
        **process_power(records_655, max_val=55, num_balls=6, has_special=True)
    }

    # 2. Mega 6/45
    print("Processing Mega 6/45 with deep analytics...")
    records_645 = read_jsonl(DATA_DIR / "power645.jsonl")
    summary_data["products"]["power_645"] = {
        "name": "Mega 6/45",
        "description": "Chọn 6 số từ 1 đến 45. Trúng Jackpot từ 12 Tỷ.",
        "type": "lotto",
        "balls": 6,
        "max_number": 45,
        "has_special": False,
        **process_power(records_645, max_val=45, num_balls=6, has_special=False)
    }

    # 3. Power 5/35
    print("Processing Power 5/35 with deep analytics...")
    records_535 = read_jsonl(DATA_DIR / "power535.jsonl")
    summary_data["products"]["power_535"] = {
        "name": "Power 5/35",
        "description": "Chọn 5 số từ 1 đến 35.",
        "type": "lotto",
        "balls": 5,
        "max_number": 35,
        "has_special": True,
        **process_power(records_535, max_val=35, num_balls=5, has_special=True)
    }

    # 4. Keno
    print("Processing Keno...")
    records_keno = read_jsonl(DATA_DIR / "keno.jsonl")
    summary_data["products"]["keno"] = {
        "name": "Keno",
        "description": "Quay 10 phút/kỳ. Rút 20 số từ tập 1 đến 80.",
        "type": "keno",
        **process_keno(records_keno)
    }

    # 5. Bingo 18
    print("Processing Bingo 18...")
    records_bingo = read_jsonl(DATA_DIR / "bingo18.jsonl")
    summary_data["products"]["bingo18"] = {
        "name": "Bingo 18",
        "description": "Quay 5 phút/kỳ. Quay 3 số từ 1 đến 6.",
        "type": "bingo18",
        **process_bingo18(records_bingo)
    }

    # 6. Max 3D
    print("Processing Max 3D...")
    records_3d = read_jsonl(DATA_DIR / "3d.jsonl")
    summary_data["products"]["3d"] = {
        "name": "Max 3D",
        "description": "Xổ số 3 chữ số theo cơ cấu giải thưởng.",
        "type": "3d",
        **process_max3d(records_3d)
    }

    # 7. Max 3D Pro
    print("Processing Max 3D Pro...")
    records_3d_pro = read_jsonl(DATA_DIR / "3d_pro.jsonl")
    summary_data["products"]["3d_pro"] = {
        "name": "Max 3D Pro",
        "description": "Xổ số 3 chữ số Pro mở thưởng Thứ 3, 5, 7.",
        "type": "3d",
        **process_max3d(records_3d_pro)
    }

    for out_dir in [DOCS_DATA_DIR, DATA_DIR]:
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / "vietlott_summary.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        file_size_kb = output_path.stat().st_size / 1024
        print(f"Successfully generated {output_path} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
