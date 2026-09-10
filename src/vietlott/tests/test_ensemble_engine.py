"""
Unit tests for Ensemble Engine (ensemble_engine.py):
Tests 7-model consensus hub, Walk-Forward backtest with L2-regularized dynamic weights,
ticket extraction (Triad, Key 5, Core Pool, Wheeling C(v, k, t), Golden Ticket),
and Wheeling Strategy Generation.
"""

import json
import math
from pathlib import Path
import pytest

try:
    from vietlott.model.ensemble_engine import (
        calculate_multi_model_consensus_and_backtest,
        generate_wheeling_strategy,
    )
except ImportError:
    from src.vietlott.model.ensemble_engine import (
        calculate_multi_model_consensus_and_backtest,
        generate_wheeling_strategy,
    )

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _read_records(filename: str):
    path = DATA_DIR / filename
    records = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records


@pytest.fixture(scope="module")
def power655_records():
    recs = _read_records("power655.jsonl")
    assert len(recs) >= 30, "Power 6/55 requires at least 30 records"
    return recs[-50:]


@pytest.fixture(scope="module")
def mega645_records():
    recs = _read_records("power645.jsonl")
    assert len(recs) >= 30, "Mega 6/45 requires at least 30 records"
    return recs[-50:]


@pytest.fixture(scope="module")
def power535_records():
    recs = _read_records("power535.jsonl")
    assert len(recs) >= 30, "Power 5/35 requires at least 30 records"
    return recs[-50:]


EXPECTED_MODELS = {
    "markov",
    "hazard",
    "decay",
    "bac_nho",
    "fourier",
    "graph_pagerank",
    "state_space",
    "ml_ranker",
}


@pytest.fixture(scope="module")
def power655_res(power655_records):
    return calculate_multi_model_consensus_and_backtest(
        power655_records,
        product_key="power_655",
        max_val=55,
        num_balls=6,
        is_two_matrix=False,
        num_draws=10,
        display_draws=5,
    )


@pytest.fixture(scope="module")
def mega645_res(mega645_records):
    return calculate_multi_model_consensus_and_backtest(
        mega645_records,
        product_key="power_645",
        max_val=45,
        num_balls=6,
        is_two_matrix=False,
        num_draws=10,
        display_draws=5,
    )


@pytest.fixture(scope="module")
def power535_res(power535_records):
    return calculate_multi_model_consensus_and_backtest(
        power535_records,
        product_key="power_535",
        max_val=35,
        num_balls=5,
        is_two_matrix=True,
        num_draws=10,
        display_draws=5,
    )


def test_ensemble_engine_structure_power655(power655_res):
    """Kiểm tra leaderboard có đủ 8 mô hình + consensus + baseline_random cho Power 6/55."""
    res = power655_res

    # Validate root keys
    assert "leaderboard" in res
    assert "top_consensus_balls" in res
    assert "model_explanations" in res
    assert "training_report" in res
    assert "tickets" in res
    assert "history_walk_forward" in res
    assert "next_draw_id" in res
    assert res["next_draw_id"].startswith("#")
    assert res["evaluated_draws_count"] == 10

    # Check leaderboard contains consensus, 8 models, and baseline_random
    leaderboard = res["leaderboard"]
    assert len(leaderboard) == 10  # consensus + 8 models + baseline_random
    assert leaderboard[0]["id"] == "consensus"
    assert leaderboard[-1]["id"] == "baseline_random"

    model_ids = {m["id"] for m in leaderboard[1:-1]}
    assert model_ids == EXPECTED_MODELS

    # Check model_explanations has all 8 models
    explanations = res["model_explanations"]
    assert set(explanations.keys()) == EXPECTED_MODELS
    for m in EXPECTED_MODELS:
        assert "name" in explanations[m]
        assert "top_picks" in explanations[m]
        assert "math_basis" in explanations[m]
        assert "rationale" in explanations[m]

    # Check top_consensus_balls breakdown includes all 8 models
    top_balls = res["top_consensus_balls"]
    assert len(top_balls) <= 15
    for tb in top_balls:
        assert "ball" in tb
        assert "score" in tb
        assert "breakdown" in tb
        assert set(tb["breakdown"].keys()) == EXPECTED_MODELS


def test_ensemble_engine_structure_mega645(mega645_res):
    """Kiểm tra Mega 6/45: Đủ 8 mô hình, core pool 12 số, các khóa vé chuẩn xác."""
    res = mega645_res

    leaderboard = res["leaderboard"]
    assert len(leaderboard) == 10
    model_ids = {m["id"] for m in leaderboard[1:-1]}
    assert model_ids == EXPECTED_MODELS

    tickets = res["tickets"]
    assert len(tickets["key_balls"]) == 3
    assert len(tickets["key_5_balls"]) == 5
    assert len(tickets["core_pool"]) == 12

    for b in tickets["core_pool"]:
        assert 1 <= b <= 45


def test_ensemble_engine_structure_power535(power535_res):
    """Kiểm tra Power 5/35 dual matrix: Core pool 10 số, bóng trong phạm vi 1..35."""
    res = power535_res

    leaderboard = res["leaderboard"]
    assert len(leaderboard) == 10
    model_ids = {m["id"] for m in leaderboard[1:-1]}
    assert model_ids == EXPECTED_MODELS

    tickets = res["tickets"]
    assert len(tickets["key_balls"]) == 3
    assert len(tickets["key_5_balls"]) == 5
    assert len(tickets["core_pool"]) == 10

    for b in tickets["core_pool"]:
        assert 1 <= b <= 35


def test_ensemble_weights_sum_to_100(power655_res):
    """Kiểm tra tổng trọng số của 8 mô hình xấp xỉ 100%."""
    res = power655_res

    trained_weights = res["training_report"]["trained_model_weights"]
    assert set(trained_weights.keys()) == EXPECTED_MODELS

    total_weight = sum(trained_weights.values())
    assert abs(total_weight - 100.0) <= 1.0, f"Total weight {total_weight} must be approx 100%"

    # Check leaderboard entries for 8 models sum to approx 100%
    ld_models = [m for m in res["leaderboard"] if m["id"] in EXPECTED_MODELS]
    ld_total = sum(m["weight_pct"] for m in ld_models)
    assert abs(ld_total - 100.0) <= 1.0, f"Leaderboard total weight {ld_total} must be approx 100%"


def test_tickets_backwards_compatibility(power655_res):
    """Kiểm tra đầy đủ các khóa vé con và backtest bảo đảm tương thích ngược 100%."""
    res = power655_res

    tickets = res["tickets"]
    # Required keys in tickets
    required_ticket_keys = [
        "key_balls",
        "key_roles",
        "key_5_balls",
        "triad_backtest",
        "key5_backtest",
        "core_pool",
        "core_backtest",
        "wheeling_tickets",
        "wheeling_4_tickets",
        "wheel_backtest",
        "wheel4_backtest",
        "golden",
        "momentum",
        "breakout",
        "optimal_septet",
        "septet_backtest",
        "bao7",
    ]
    for k in required_ticket_keys:
        assert k in tickets, f"Missing ticket key: {k}"

    # Backwards compatibility check for wheeling_4_tickets
    assert len(tickets["wheeling_4_tickets"]) == 4
    # Covering wheel tickets
    assert len(tickets["wheeling_tickets"]) == 6
    # Wheel backtest
    assert "overall_prize_win_rate" in tickets["wheel4_backtest"]
    assert "core_ge4_win_rate" in tickets["wheel4_backtest"]
    assert "guarantee_coverage" in tickets["wheel4_backtest"]
    assert tickets["wheel_backtest"] == tickets["wheel4_backtest"]

    # Golden ticket structure
    golden = tickets["golden"]
    assert "numbers" in golden
    assert len(golden["numbers"]) == 6
    assert "ac_index" in golden
    assert "sum" in golden
    assert "odd_even" in golden
    assert "sei_score" in golden
    assert "negative_space_check" in golden


def test_wheeling_strategy_generation(power655_records, power535_records):
    """Kiểm tra generate_wheeling_strategy cho cả 6/55 và 5/35."""
    # Power 6/55
    wheel655 = generate_wheeling_strategy(
        power655_records,
        product_key="power_655",
        max_val=55,
        num_balls=6,
        is_two_matrix=False,
    )
    assert wheel655["core_pool_size"] == 12
    assert len(wheel655["core_pool"]) == 12
    assert len(wheel655["tickets"]) == 6
    assert wheel655["total_tickets"] == 6
    assert wheel655["total_cost"] == 60000
    assert "coverage" in wheel655
    assert "guarantee_statement" in wheel655
    assert "special_recommendation" in wheel655

    # Power 5/35
    wheel535 = generate_wheeling_strategy(
        power535_records,
        product_key="power_535",
        max_val=35,
        num_balls=5,
        is_two_matrix=True,
    )
    assert wheel535["core_pool_size"] == 10
    assert len(wheel535["core_pool"]) == 10
    assert len(wheel535["tickets"]) == 6
    assert wheel535["total_tickets"] == 6
    assert wheel535["total_cost"] == 60000


def test_seeded_prediction_determinism(power655_records):
    """Cùng input cho ra cùng Golden Ticket và dàn vé đồng nhất 100%."""
    res1 = calculate_multi_model_consensus_and_backtest(
        power655_records,
        product_key="power_655",
        max_val=55,
        num_balls=6,
        is_two_matrix=False,
        num_draws=2,
        display_draws=2,
    )
    res2 = calculate_multi_model_consensus_and_backtest(
        power655_records,
        product_key="power_655",
        max_val=55,
        num_balls=6,
        is_two_matrix=False,
        num_draws=2,
        display_draws=2,
    )

    assert res1["tickets"]["golden"]["numbers"] == res2["tickets"]["golden"]["numbers"]
    assert res1["tickets"]["key_balls"] == res2["tickets"]["key_balls"]
    assert res1["tickets"]["key_5_balls"] == res2["tickets"]["key_5_balls"]
    assert res1["tickets"]["wheeling_tickets"] == res2["tickets"]["wheeling_tickets"]
    assert res1["tickets"]["optimal_septet"]["numbers"] == res2["tickets"]["optimal_septet"]["numbers"]
    assert res1["top_consensus_balls"] == res2["top_consensus_balls"]
