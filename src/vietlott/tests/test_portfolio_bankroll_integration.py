"""
Integration tests for Markowitz Portfolio Optimization and Kelly Bankroll Advisory (CCS)
integrated into vietlott.model.ensemble_engine.

Tests:
1. test_consensus_hub_contains_bankroll_advisory_power655: Complete bankroll advisory on Power 6/55.
2. test_consensus_hub_contains_bankroll_advisory_mega645: Complete bankroll advisory on Mega 6/45.
3. test_consensus_hub_contains_bankroll_advisory_power535: Complete bankroll advisory on Power 5/35.
4. test_golden_ticket_markowitz_optimization_properties: Markowitz Golden Ticket properties (AC, sum range, Louvain >= 4, louvain_spread, utility, return, penalty).
5. test_bankroll_advisory_tier_validity: CCS score tiers {1, 2, 3} and budgets {10000, 20000, 60000}.
6. test_schema_backwards_compatibility: Full backward compatibility of returned dictionary.
"""

import json
from pathlib import Path
import pytest

try:
    from vietlott.model.ensemble_engine import calculate_multi_model_consensus_and_backtest
except ImportError:
    from src.vietlott.model.ensemble_engine import calculate_multi_model_consensus_and_backtest


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


def test_consensus_hub_contains_bankroll_advisory_power655(power655_res):
    """Kiểm tra bankroll_advisory đầy đủ trên Power 6/55."""
    assert "bankroll_advisory" in power655_res, "bankroll_advisory must be present in consensus result"
    adv = power655_res["bankroll_advisory"]

    assert isinstance(adv, dict)
    assert "ccs_score" in adv and isinstance(adv["ccs_score"], (int, float))
    assert 0.0 <= adv["ccs_score"] <= 100.0
    assert "tier_level" in adv and adv["tier_level"] in {1, 2, 3}
    assert "tier_name" in adv and isinstance(adv["tier_name"], str) and len(adv["tier_name"]) > 0
    assert "tier_badge" in adv and isinstance(adv["tier_badge"], str)
    assert "recommended_action" in adv and isinstance(adv["recommended_action"], str)
    assert "recommended_budget" in adv and adv["recommended_budget"] in {10000, 20000, 60000}
    assert "breakdown" in adv and isinstance(adv["breakdown"], dict)
    assert "agreement_score" in adv["breakdown"]
    assert "entropy_score" in adv["breakdown"]
    assert "pull_score" in adv["breakdown"]
    assert "rationale" in adv and isinstance(adv["rationale"], str) and len(adv["rationale"]) > 0


def test_consensus_hub_contains_bankroll_advisory_mega645(mega645_res):
    """Kiểm tra bankroll_advisory đầy đủ trên Mega 6/45."""
    assert "bankroll_advisory" in mega645_res, "bankroll_advisory must be present in Mega 6/45"
    adv = mega645_res["bankroll_advisory"]

    assert isinstance(adv, dict)
    assert "ccs_score" in adv and 0.0 <= adv["ccs_score"] <= 100.0
    assert adv["tier_level"] in {1, 2, 3}
    assert adv["recommended_budget"] in {10000, 20000, 60000}
    assert "breakdown" in adv
    assert "rationale" in adv


def test_consensus_hub_contains_bankroll_advisory_power535(power535_res):
    """Kiểm tra bankroll_advisory đầy đủ trên Power 5/35."""
    assert "bankroll_advisory" in power535_res, "bankroll_advisory must be present in Power 5/35"
    adv = power535_res["bankroll_advisory"]

    assert isinstance(adv, dict)
    assert "ccs_score" in adv and 0.0 <= adv["ccs_score"] <= 100.0
    assert adv["tier_level"] in {1, 2, 3}
    assert adv["recommended_budget"] in {10000, 20000, 60000}
    assert "breakdown" in adv
    assert "rationale" in adv


def test_golden_ticket_markowitz_optimization_properties(power655_res, mega645_res, power535_res):
    """Kiểm tra vé Golden có optimization_type, AC, tổng trong khoảng, Louvain clusters và louvain_spread."""
    # Power 6/55
    golden_655 = power655_res["tickets"]["golden"]
    assert golden_655.get("optimization_type") == "Markowitz Constrained Portfolio"
    assert "expected_return" in golden_655 and isinstance(golden_655["expected_return"], (int, float))
    assert "covariance_risk_penalty" in golden_655 and isinstance(golden_655["covariance_risk_penalty"], (int, float))
    assert "objective_utility" in golden_655 and isinstance(golden_655["objective_utility"], (int, float))
    assert "louvain_spread" in golden_655 and isinstance(golden_655["louvain_spread"], dict)
    assert golden_655["louvain_spread"]["distinct_clusters_count"] >= 4
    assert "cluster_distribution" in golden_655["louvain_spread"]
    assert golden_655["ac_index"] >= 7
    assert 115 <= golden_655["sum"] <= 220
    assert len(golden_655["numbers"]) == 6
    assert all(1 <= b <= 55 for b in golden_655["numbers"])
    assert "odd_even" in golden_655
    assert "special" in golden_655

    # Mega 6/45
    golden_645 = mega645_res["tickets"]["golden"]
    assert golden_645.get("optimization_type") == "Markowitz Constrained Portfolio"
    assert golden_645["louvain_spread"]["distinct_clusters_count"] >= 4
    assert golden_645["ac_index"] >= 7
    assert 95 <= golden_645["sum"] <= 180
    assert len(golden_645["numbers"]) == 6
    assert all(1 <= b <= 45 for b in golden_645["numbers"])

    # Power 5/35
    golden_535 = power535_res["tickets"]["golden"]
    assert golden_535.get("optimization_type") == "Markowitz Constrained Portfolio"
    assert golden_535["louvain_spread"]["distinct_clusters_count"] >= 3
    assert golden_535["ac_index"] >= 4
    assert 60 <= golden_535["sum"] <= 120
    assert len(golden_535["numbers"]) == 5
    assert all(1 <= b <= 35 for b in golden_535["numbers"])


def test_bankroll_advisory_tier_validity(power655_res, mega645_res, power535_res):
    """Kiểm tra tier_level thuộc {1, 2, 3} và recommended_budget thuộc {10000, 20000, 60000} tương ứng."""
    for res, name in [(power655_res, "Power 6/55"), (mega645_res, "Mega 6/45"), (power535_res, "Power 5/35")]:
        adv = res["bankroll_advisory"]
        tier = adv["tier_level"]
        budget = adv["recommended_budget"]
        ccs = adv["ccs_score"]

        assert tier in {1, 2, 3}, f"{name}: tier_level {tier} must be 1, 2, or 3"
        assert budget in {10000, 20000, 60000}, f"{name}: budget {budget} must be 10k, 20k, or 60k"

        if tier == 1:
            assert budget == 10000
            assert ccs < 55.0
        elif tier == 2:
            assert budget == 20000
            assert 55.0 <= ccs < 75.0
        elif tier == 3:
            assert budget == 60000
            assert ccs >= 75.0


def test_schema_backwards_compatibility(power655_res):
    """Đảm bảo không làm mất hoặc thay đổi kiểu dữ liệu của bất kỳ trường cũ nào."""
    res = power655_res

    # Root fields
    assert "next_draw_id" in res and isinstance(res["next_draw_id"], str)
    assert "evaluated_draws_count" in res and isinstance(res["evaluated_draws_count"], int)
    assert "leaderboard" in res and isinstance(res["leaderboard"], list)
    assert "top_consensus_balls" in res and isinstance(res["top_consensus_balls"], list)
    assert "model_explanations" in res and isinstance(res["model_explanations"], dict)
    assert "models_info" in res and isinstance(res["models_info"], dict)
    assert "transition_analytics" in res and isinstance(res["transition_analytics"], dict)
    assert "training_report" in res and isinstance(res["training_report"], dict)
    assert "tickets" in res and isinstance(res["tickets"], dict)
    assert "history_walk_forward" in res and isinstance(res["history_walk_forward"], list)

    # Tickets subfields
    tickets = res["tickets"]
    for expected_key in [
        "key_balls", "key_roles", "key_5_balls", "triad_backtest", "key5_backtest",
        "core_pool", "core_backtest", "wheeling_tickets", "wheeling_4_tickets",
        "wheel_backtest", "wheel4_backtest", "golden", "momentum", "breakout",
        "optimal_septet", "septet_backtest", "bao7"
    ]:
        assert expected_key in tickets, f"tickets must retain '{expected_key}'"

    # Golden ticket old fields
    golden = tickets["golden"]
    assert "numbers" in golden and isinstance(golden["numbers"], list)
    assert "ac_index" in golden and isinstance(golden["ac_index"], int)
    assert "sum" in golden and isinstance(golden["sum"], int)
    assert "odd_even" in golden and isinstance(golden["odd_even"], str)
    assert "sei_score" in golden and isinstance(golden["sei_score"], (int, float))
    assert "special" in golden
    assert "negative_space_check" in golden and isinstance(golden["negative_space_check"], dict)
