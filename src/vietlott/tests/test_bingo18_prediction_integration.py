import json
import pytest
from pathlib import Path

from vietlott.render_web_data import process_bingo18


def test_process_bingo18_outputs_prediction_hub():
    """Kiểm tra process_bingo18 xuất đầy đủ trường prediction_hub."""
    records = [
        {"id": "0185800", "date": "2026-09-09", "result": [2, 3, 5], "total": 10, "large_small": "Nhỏ"},
        {"id": "0185801", "date": "2026-09-09", "result": [4, 4, 4], "total": 12, "large_small": "Lớn", "is_triple": True},
        {"id": "0185802", "date": "2026-09-09", "result": [6, 5, 2], "total": 13, "large_small": "Lớn"},
    ]

    res = process_bingo18(records)
    assert "prediction_hub" in res
    pred = res["prediction_hub"]
    assert "large_small_prediction" in pred
    assert "single_face_prediction" in pred
    assert "target_sum_prediction" in pred
    assert "storm_trigger" in pred
    assert "target_draw_id" in pred

    assert pred["large_small_prediction"]["predicted_choice"] in ["Lớn", "Nhỏ"]
    assert 1 <= pred["single_face_prediction"]["best_face"] <= 6
    assert pred["target_sum_prediction"]["target_range"] == [8, 13]


def test_process_bingo18_real_data_has_valid_prediction_hub():
    """Kiểm tra prediction_hub với file dữ liệu thật."""
    p = Path("data/bingo18.jsonl")
    if not p.exists():
        pytest.skip("data/bingo18.jsonl not present")

    records = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    res = process_bingo18(records)
    pred = res["prediction_hub"]
    assert pred["large_small_prediction"]["confidence_pct"] >= 50.0
    assert pred["single_face_prediction"]["expected_hit_prob_pct"] >= 40.0
