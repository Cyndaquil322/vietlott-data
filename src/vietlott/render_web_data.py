#!/usr/bin/env python
"""
render_web_data.py
Generates a lightweight, optimized JSON file (docs/data/vietlott_summary.json)
for the static Web UI. Fast loading, includes latest draws & analytical stats.
"""

import json
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
    """Read JSONL file and return list of dicts."""
    if not file_path.exists():
        return []
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def process_power(records: List[Dict], max_val: int, num_balls: int, has_special: bool = False) -> Dict[str, Any]:
    """Process Power 655, 645, 535."""
    if not records:
        return {}

    total_draws = len(records)
    # Newest draws are at the end, so reverse for display
    latest_draws = records[-100:][::-1]

    # Calculate frequency
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

    # Total main ball appearances
    total_balls = total_draws * num_balls if total_draws else 1

    # Frequency list for all numbers
    freq_list = []
    for num in range(1, max_val + 1):
        cnt = ball_counter.get(num, 0)
        freq_list.append({
            "number": num,
            "count": cnt,
            "pct": round((cnt / total_draws * 100) if total_draws else 0, 2)
        })

    # Hot & Cold
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

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
        "hot_numbers": hot_numbers,
        "cold_numbers": cold_numbers,
        "frequency": freq_list,
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

    # Frequency over the last 1000 draws for performance & recent trends
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

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
        "hot_numbers": sorted_freq[:10],
        "cold_numbers": sorted_freq[-10:][::-1],
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

    return {
        "total_draws": total_draws,
        "first_draw": records[0].get("date"),
        "latest_draw": records[-1].get("date"),
        "latest": latest_draws[0],
        "history": latest_draws,
        "dice_frequency": dice_freq,
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
            "version": "1.0.0",
        },
        "products": {}
    }

    # 1. Power 6/55
    print("Processing Power 6/55...")
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

    # 2. Power 6/45
    print("Processing Mega 6/45...")
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
    print("Processing Power 5/35...")
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

    output_path = DOCS_DATA_DIR / "vietlott_summary.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    file_size_kb = output_path.stat().st_size / 1024
    print(f"Successfully generated {output_path} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
