import json
import pytest
from pathlib import Path

from vietlott.render_web_data import process_bingo18
from vietlott.sync_live_data import main as sync_live_main


def test_process_bingo18_integration_structure():
    """Kiểm tra process_bingo18 trong render_web_data xuất đầy đủ các trường mới."""
    records = [
        {"id": "0185800", "date": "2026-09-09", "result": [2, 3, 5], "total": 10, "large_small": "Nhỏ"},
        {"id": "0185801", "date": "2026-09-09", "result": [4, 4, 4], "total": 12, "large_small": "Lớn", "is_triple": True},
        {"id": "0185802", "date": "2026-09-09", "result": [6, 5, 2], "total": 13, "large_small": "Lớn"},
    ]

    res = process_bingo18(records)
    assert "total_draws" in res
    assert res["total_draws"] == 3
    assert "latest" in res
    assert "streak_analytics" in res
    assert "sum_distribution" in res
    assert "storm_radar" in res
    assert "dice_frequencies" in res

    # Roadmap in streak analytics
    assert len(res["streak_analytics"]["roadmap"]) == 3
    # Storm radar found the triple
    assert res["storm_radar"]["total_storms_found"] >= 1


def test_process_bingo18_real_data_payload():
    """Kiểm tra process_bingo18 với file dữ liệu thật."""
    p = Path("data/bingo18.jsonl")
    if not p.exists():
        pytest.skip("data/bingo18.jsonl not present")

    records = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    res = process_bingo18(records)
    assert res["total_draws"] == len(records)
    assert res["streak_analytics"]["current_streak_len"] >= 1
    assert res["sum_distribution"]["mean_sum"] > 0
    assert res["storm_radar"]["current_storm_gap"] >= 0
