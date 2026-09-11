import json
import pytest
from pathlib import Path

from vietlott.model.bingo18_engine import (
    THEORETICAL_3D6_SUMS,
    TOTAL_3D6_COMBINATIONS,
    analyze_bingo18_streaks,
    analyze_bingo18_sum_distribution,
    analyze_bingo18_storm_radar,
    analyze_bingo18_dice_frequencies,
    generate_bingo18_comprehensive_analytics,
)


def test_theoretical_3d6_sums_distribution():
    """Kiểm tra phân phối lý thuyết 3d6: tổng 216 tổ hợp, đối xứng chuẩn qua 10 và 11."""
    assert sum(THEORETICAL_3D6_SUMS.values()) == TOTAL_3D6_COMBINATIONS == 216

    # Tính đối xứng P(S) == P(21 - S)
    for s in range(3, 11):
        assert THEORETICAL_3D6_SUMS[s] == THEORETICAL_3D6_SUMS[21 - s]

    # Đỉnh cực đại tại 10 và 11: 27 tổ hợp (12.5%)
    assert THEORETICAL_3D6_SUMS[10] == 27
    assert THEORETICAL_3D6_SUMS[11] == 27
    assert THEORETICAL_3D6_SUMS[3] == 1
    assert THEORETICAL_3D6_SUMS[18] == 1


def test_analyze_bingo18_streaks_controlled():
    """Kiểm tra phát hiện chuỗi bệt và roadmap Lớn/Nhỏ."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [5, 6, 5], "total": 16, "large_small": "Lớn"},
        {"id": "00002", "date": "2026-09-01", "result": [4, 5, 4], "total": 13, "large_small": "Lớn"},
        {"id": "00003", "date": "2026-09-01", "result": [6, 6, 2], "total": 14, "large_small": "Lớn"},
        {"id": "00004", "date": "2026-09-01", "result": [1, 2, 3], "total": 6, "large_small": "Nhỏ"},
    ]

    analysis = analyze_bingo18_streaks(records, window_len=10)
    assert analysis["current_streak_type"] == "Nhỏ"
    assert analysis["current_streak_len"] == 1
    assert analysis["max_streak_observed"] >= 3
    assert len(analysis["roadmap"]) == 4

    r_last = analysis["roadmap"][-1]
    assert r_last["drawId"] == "00004"
    assert r_last["type"] == "Nhỏ"
    assert r_last["isTriple"] is False


def test_analyze_bingo18_sum_distribution():
    """Kiểm tra phân tích chuông tổng Gaussian so với lý thuyết."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [3, 4, 3], "total": 10},
        {"id": "00002", "date": "2026-09-01", "result": [4, 4, 3], "total": 11},
        {"id": "00003", "date": "2026-09-01", "result": [1, 1, 1], "total": 3},
    ]

    dist = analyze_bingo18_sum_distribution(records, window_len=10)
    assert "distribution" in dist
    assert len(dist["distribution"]) == 16  # 3..18

    d10 = next(x for x in dist["distribution"] if x["sum"] == 10)
    assert d10["count"] == 1
    assert d10["theoretical_pct"] == round(27 / 216 * 100, 2)
    assert dist["mean_sum"] > 0
    assert len(dist["top_hot_sums"]) > 0


def test_analyze_bingo18_storm_radar():
    """Kiểm tra radar săn bão và phân loại hazard level."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [3, 3, 3], "total": 9, "is_triple": True},
    ]
    # Thêm 40 kỳ thường
    for i in range(2, 42):
        records.append({"id": f"{i:05d}", "date": "2026-09-01", "result": [1, 2, 4], "total": 7, "is_triple": False})

    radar = analyze_bingo18_storm_radar(records)
    assert radar["current_storm_gap"] == 40
    assert radar["hazard_level"]["level"] in ["normal", "accumulating", "critical"]
    assert radar["last_storm"]["drawId"] == "00001"
    assert radar["last_storm"]["triple"] == [3, 3, 3]


def test_analyze_bingo18_dice_frequencies():
    """Kiểm tra tần suất 6 mặt xúc xắc và các cặp nổ chung."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [1, 2, 3], "total": 6},
        {"id": "00002", "date": "2026-09-01", "result": [1, 5, 6], "total": 12},
    ]

    freqs = analyze_bingo18_dice_frequencies(records, window_len=10)
    assert len(freqs["dice_frequencies"]) == 6  # Faces 1..6

    f1 = next(x for x in freqs["dice_frequencies"] if x["face"] == 1)
    assert f1["count"] == 2  # 1 appeared twice
    assert len(freqs["top_pairs"]) > 0


def test_generate_bingo18_comprehensive_analytics_real_data():
    """Kiểm tra tổng hợp định lượng trên dữ liệu thật của repo."""
    data_file = Path("data/bingo18.jsonl")
    if not data_file.exists():
        pytest.skip("data/bingo18.jsonl not present")

    records = []
    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    assert len(records) > 1000

    analytics = generate_bingo18_comprehensive_analytics(records)
    assert "streak_analytics" in analytics
    assert "sum_distribution" in analytics
    assert "storm_radar" in analytics
    assert "dice_frequencies" in analytics
    assert analytics["total_draws"] == len(records)
    assert "latest" in analytics


def test_edge_cases():
    """Kiểm tra xử lý danh sách rỗng và dữ liệu nhỏ."""
    empty = generate_bingo18_comprehensive_analytics([])
    assert empty == {}

    single = generate_bingo18_comprehensive_analytics([
        {"id": "00001", "date": "2026-09-01", "result": [2, 2, 2], "total": 6}
    ])
    assert single["total_draws"] == 1
    assert single["streak_analytics"]["current_streak_len"] == 1
