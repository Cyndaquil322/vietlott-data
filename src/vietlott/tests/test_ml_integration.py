"""
Integration tests for ML Ranker and Transition Analytics integration into Ensemble Engine
and Render Web Data pipeline.

Tests:
1. test_ensemble_hub_contains_transition_analytics
2. test_ensemble_hub_eight_models_leaderboard
3. test_trained_model_weights_eight_models
4. test_model_explanations_eight_models
5. test_schema_backwards_compatibility
6. test_top_consensus_balls_eight_models_breakdown
7. test_power535_dual_matrix_ml_integration
"""

import json
from pathlib import Path
import pytest

try:
    from vietlott.model.ensemble_engine import (
        calculate_multi_model_consensus_and_backtest,
    )
except ImportError:
    from src.vietlott.model.ensemble_engine import (
        calculate_multi_model_consensus_and_backtest,
    )

DATA_DIR = Path(__file__).resolve().parents[3] / "data"

EXPECTED_EIGHT_MODELS = {
    "markov",
    "hazard",
    "decay",
    "bac_nho",
    "fourier",
    "graph_pagerank",
    "state_space",
    "ml_ranker",
}


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
def power535_records():
    recs = _read_records("power535.jsonl")
    assert len(recs) >= 30, "Power 5/35 requires at least 30 records"
    return recs[-50:]


@pytest.fixture(scope="module")
def power655_consensus(power655_records):
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
def power535_consensus(power535_records):
    return calculate_multi_model_consensus_and_backtest(
        power535_records,
        product_key="power_535",
        max_val=35,
        num_balls=5,
        is_two_matrix=True,
        num_draws=10,
        display_draws=5,
    )


def test_ensemble_hub_contains_transition_analytics(power655_consensus):
    """Kiểm tra transition_analytics có đủ latest_draw_numbers, top_pull_rules, top_repulsion_rules."""
    res = power655_consensus

    assert "transition_analytics" in res, "transition_analytics must be present in consensus result"
    ta = res["transition_analytics"]
    assert isinstance(ta, dict)
    assert "latest_draw_numbers" in ta
    assert "top_pull_rules" in ta
    assert "top_repulsion_rules" in ta

    assert isinstance(ta["latest_draw_numbers"], list)
    assert len(ta["latest_draw_numbers"]) == 6
    assert isinstance(ta["top_pull_rules"], list)
    assert isinstance(ta["top_repulsion_rules"], list)

    if ta["top_pull_rules"]:
        rule = ta["top_pull_rules"][0]
        assert "from_ball" in rule
        assert "to_ball" in rule
        assert "z_score" in rule
        assert "lift" in rule
        assert "historical_hits" in rule
        assert "strength" in rule

    if ta["top_repulsion_rules"]:
        rule = ta["top_repulsion_rules"][0]
        assert "from_ball" in rule
        assert "to_ball" in rule
        assert "z_score" in rule
        assert "lift" in rule
        assert "historical_hits" in rule
        assert "warning" in rule


def test_ensemble_hub_eight_models_leaderboard(power655_consensus):
    """Kiểm tra leaderboard có 10 dòng (consensus + 8 models + baseline_random) và ml_ranker hiện diện."""
    res = power655_consensus

    leaderboard = res["leaderboard"]
    assert len(leaderboard) == 10, f"Leaderboard must have 10 entries (1 consensus + 8 models + 1 baseline), got {len(leaderboard)}"
    assert leaderboard[0]["id"] == "consensus"
    assert leaderboard[-1]["id"] == "baseline_random"

    model_ids = {m["id"] for m in leaderboard[1:-1]}
    assert model_ids == EXPECTED_EIGHT_MODELS, f"Leaderboard models mismatch: {model_ids} vs {EXPECTED_EIGHT_MODELS}"

    ml_entry = next(m for m in leaderboard if m["id"] == "ml_ranker")
    assert ml_entry["name"] == "HistGradientBoosting Ranker (Học Máy)"
    assert ml_entry["icon"] == "brain-circuit"
    assert ml_entry["color"] == "violet"
    assert "Gradient Boosting" in ml_entry["desc"]
    assert isinstance(ml_entry["avg_hits"], float)
    assert isinstance(ml_entry["win_rate_ge3"], float)
    assert isinstance(ml_entry["recent_10_hits"], int)
    assert isinstance(ml_entry["weight_pct"], (int, float))


def test_trained_model_weights_eight_models(power655_consensus):
    """Kiểm tra trained_model_weights có đủ 8 mô hình và tổng trọng số xấp xỉ 100%."""
    res = power655_consensus

    trained_weights = res["training_report"]["trained_model_weights"]
    assert set(trained_weights.keys()) == EXPECTED_EIGHT_MODELS

    total_weight = sum(trained_weights.values())
    assert abs(total_weight - 100.0) <= 1.0, f"Total weight {total_weight} must be approx 100%"
    assert trained_weights["ml_ranker"] > 0, "ml_ranker weight must be strictly positive"

    # Leaderboard entries for 8 models sum to approx 100%
    ld_models = [m for m in res["leaderboard"] if m["id"] in EXPECTED_EIGHT_MODELS]
    ld_total = sum(m["weight_pct"] for m in ld_models)
    assert abs(ld_total - 100.0) <= 1.0, f"Leaderboard total weight {ld_total} must be approx 100%"


def test_model_explanations_eight_models(power655_consensus):
    """Kiểm tra giải trình của 8 mô hình bao gồm ml_ranker."""
    res = power655_consensus

    explanations = res["model_explanations"]
    assert set(explanations.keys()) == EXPECTED_EIGHT_MODELS

    ml_exp = explanations["ml_ranker"]
    assert ml_exp["name"] == "HistGradientBoosting Ranker (Học Máy)"
    assert "top_picks" in ml_exp
    assert "math_basis" in ml_exp
    assert "rationale" in ml_exp
    assert len(ml_exp["top_picks"]) >= 4
    for b in ml_exp["top_picks"]:
        assert 1 <= b <= 55


def test_schema_backwards_compatibility(power655_consensus):
    """Đảm bảo không làm mất bất kỳ trường nào của schema cũ (tickets, backtests, reports)."""
    res = power655_consensus

    root_keys = [
        "next_draw_id",
        "evaluated_draws_count",
        "leaderboard",
        "top_consensus_balls",
        "model_explanations",
        "models_info",
        "training_report",
        "tickets",
        "history_walk_forward",
        "transition_analytics",
    ]
    for k in root_keys:
        assert k in res, f"Root key '{k}' missing"

    tickets = res["tickets"]
    expected_ticket_keys = [
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
    for tk in expected_ticket_keys:
        assert tk in tickets, f"Ticket key '{tk}' missing"

    assert "trained_model_weights" in res["training_report"]
    assert "accuracy_gain_vs_random" in res["training_report"]


def test_top_consensus_balls_eight_models_breakdown(power655_consensus):
    """Kiểm tra breakdown trong top_consensus_balls có đủ 8 mô hình."""
    res = power655_consensus

    top_balls = res["top_consensus_balls"]
    assert len(top_balls) > 0
    for tb in top_balls:
        assert "ball" in tb
        assert "score" in tb
        assert "agreement_count" in tb
        assert "agreement_pct" in tb
        assert "is_safe" in tb
        assert "trap_warning" in tb
        assert "breakdown" in tb
        assert set(tb["breakdown"].keys()) == EXPECTED_EIGHT_MODELS


def test_power535_dual_matrix_ml_integration(power535_consensus):
    """Kiểm tra tích hợp ML và Transition trên Power 5/35 (dual matrix)."""
    res = power535_consensus

    assert "transition_analytics" in res
    assert len(res["leaderboard"]) == 10
    assert set(res["training_report"]["trained_model_weights"].keys()) == EXPECTED_EIGHT_MODELS
    assert len(res["tickets"]["core_pool"]) == 10
    for b in res["tickets"]["core_pool"]:
        assert 1 <= b <= 35
