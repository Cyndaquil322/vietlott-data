import json
import pytest
from pathlib import Path

from vietlott.model.bingo18_predictor import (
    predict_bingo18_large_small,
    predict_bingo18_single_face,
    predict_bingo18_target_sum,
    evaluate_bingo18_storm_trigger,
    generate_bingo18_prediction_hub,
    evaluate_bingo18_walk_forward_accuracy,
)


def test_predict_bingo18_large_small_streak_logic():
    """Kiểm tra logic bám cầu bệt (streak < 4) và bẻ cầu đảo chiều (streak >= 4)."""
    # Test bám cầu bệt: 2 kỳ Lớn liên tiếp -> dự báo tiếp tục Lớn
    records_short = [
        {"id": "00001", "date": "2026-09-01", "result": [4, 5, 4], "total": 13, "large_small": "Lớn"},
        {"id": "00002", "date": "2026-09-01", "result": [5, 5, 4], "total": 14, "large_small": "Lớn"},
    ]
    p_short = predict_bingo18_large_small(records_short)
    assert p_short["predicted_choice"] == "Lớn"
    assert "Bám Cầu Bệt" in p_short["strategy_name"]
    assert 50.0 <= p_short["confidence_pct"] <= 85.0

    # Test bẻ cầu: 5 kỳ Lớn liên tiếp -> dự báo bẻ sang Nhỏ
    records_long = [
        {"id": f"{i:05d}", "date": "2026-09-01", "result": [5, 5, 4], "total": 14, "large_small": "Lớn"}
        for i in range(1, 6)
    ]
    p_long = predict_bingo18_large_small(records_long)
    assert p_long["predicted_choice"] == "Nhỏ"
    assert "Bẻ Cầu" in p_long["strategy_name"]
    assert p_long["confidence_pct"] >= 65.0


def test_predict_bingo18_single_face():
    """Kiểm tra chọn 1 mặt xúc xắc Bạch Thủ hợp lệ trong 1..6."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [1, 2, 3], "total": 6},
        {"id": "00002", "date": "2026-09-01", "result": [1, 5, 6], "total": 12},
        {"id": "00003", "date": "2026-09-01", "result": [2, 3, 5], "total": 10},
    ]
    face_pred = predict_bingo18_single_face(records)
    assert 1 <= face_pred["best_face"] <= 6
    assert 40.0 <= face_pred["expected_hit_prob_pct"] <= 50.0
    assert "rationale" in face_pred


def test_predict_bingo18_target_sum():
    """Kiểm tra dự báo khoảng tổng Gaussian [8, 13] và tổng mục tiêu."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [3, 4, 3], "total": 10},
        {"id": "00002", "date": "2026-09-01", "result": [4, 4, 3], "total": 11},
    ]
    sum_pred = predict_bingo18_target_sum(records)
    assert sum_pred["target_range"] == [8, 13]
    assert 8 <= sum_pred["best_single_sum"] <= 13
    assert sum_pred["range_probability_pct"] == 68.0


def test_evaluate_bingo18_storm_trigger():
    """Kiểm tra tín hiệu kích hoạt săn bão khi gap >= 70."""
    # Gap nhỏ -> không kích hoạt
    records_safe = [
        {"id": "00001", "date": "2026-09-01", "result": [3, 3, 3], "total": 9, "is_triple": True}
    ]
    for i in range(2, 20):
        records_safe.append({"id": f"{i:05d}", "date": "2026-09-01", "result": [1, 2, 4], "total": 7, "is_triple": False})

    trig_safe = evaluate_bingo18_storm_trigger(records_safe)
    assert trig_safe["is_hunting_active"] is False

    # Gap lớn (80 kỳ) -> kích hoạt săn bão
    records_hot = [
        {"id": "00001", "date": "2026-09-01", "result": [3, 3, 3], "total": 9, "is_triple": True}
    ]
    for i in range(2, 85):
        records_hot.append({"id": f"{i:05d}", "date": "2026-09-01", "result": [1, 2, 4], "total": 7, "is_triple": False})

    trig_hot = evaluate_bingo18_storm_trigger(records_hot)
    assert trig_hot["is_hunting_active"] is True
    assert "NUÔI BÃO" in trig_hot["action_recommendation"]


def test_generate_bingo18_prediction_hub():
    """Kiểm tra hợp nhất đầy đủ 4 chiến lược dự đoán."""
    records = [
        {"id": "00001", "date": "2026-09-01", "result": [2, 3, 5], "total": 10, "large_small": "Nhỏ"},
        {"id": "00002", "date": "2026-09-01", "result": [4, 5, 4], "total": 13, "large_small": "Lớn"},
    ]
    hub = generate_bingo18_prediction_hub(records)
    assert "large_small_prediction" in hub
    assert "single_face_prediction" in hub
    assert "target_sum_prediction" in hub
    assert "storm_trigger" in hub
    assert "target_draw_id" in hub


def test_evaluate_bingo18_walk_forward_accuracy_real_data():
    """Kiểm tra kiểm định Walk-Forward 100 kỳ trên dữ liệu thật của repo."""
    data_file = Path("data/bingo18.jsonl")
    if not data_file.exists():
        pytest.skip("data/bingo18.jsonl not present")

    records = []
    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    assert len(records) > 500
    eval_res = evaluate_bingo18_walk_forward_accuracy(records, num_draws=100)
    assert eval_res["evaluated_draws"] == 100
    assert 45.0 <= eval_res["large_small_accuracy_pct"] <= 75.0
    assert 35.0 <= eval_res["single_face_hit_rate_pct"] <= 60.0
    assert 55.0 <= eval_res["target_range_hit_rate_pct"] <= 85.0
