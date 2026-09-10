"""
Integration tests for Negative Elimination Engine and Key-Banker Wheeling
integrated into vietlott.model.ensemble_engine.

100% Zero Mock Data - Tests run against real historical Vietlott data.

Test Cases:
1. test_consensus_hub_contains_elimination_analytics_power655: Verifies elimination_analytics on Power 6/55.
2. test_consensus_hub_contains_elimination_analytics_mega645: Verifies elimination_analytics on Mega 6/45.
3. test_consensus_hub_contains_elimination_analytics_power535: Verifies elimination_analytics on Power 5/35.
4. test_tickets_contains_banker_wheeling: Verifies tickets.banker_wheeling structure, 6 tickets, 100% contain banker, AC constraints.
5. test_clean_satellites_exclude_eliminated_balls: Verifies satellite pool contains no eliminated balls.
6. test_schema_backwards_compatibility: Ensures zero loss or regression of existing schema fields.
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
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


@pytest.fixture(scope="module")
def power655_records():
    recs = _read_records("power655.jsonl")
    assert len(recs) >= 30, "Power 6/55 requires at least 30 records"
    return recs[-45:]


@pytest.fixture(scope="module")
def mega645_records():
    recs = _read_records("power645.jsonl")
    assert len(recs) >= 30, "Mega 6/45 requires at least 30 records"
    return recs[-45:]


@pytest.fixture(scope="module")
def power535_records():
    recs = _read_records("power535.jsonl")
    assert len(recs) >= 30, "Power 5/35 requires at least 30 records"
    return recs[-45:]


@pytest.fixture(scope="module")
def power655_hub(power655_records):
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
def mega645_hub(mega645_records):
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
def power535_hub(power535_records):
    return calculate_multi_model_consensus_and_backtest(
        power535_records,
        product_key="power_535",
        max_val=35,
        num_balls=5,
        is_two_matrix=True,
        num_draws=10,
        display_draws=5,
    )


def test_consensus_hub_contains_elimination_analytics_power655(power655_hub):
    """Test elimination_analytics exists and is properly structured for Power 6/55."""
    assert "elimination_analytics" in power655_hub, "hub must include elimination_analytics"
    elim = power655_hub["elimination_analytics"]

    assert elim["eliminated_count"] == 16
    assert len(elim["eliminated_balls"]) == 16
    assert len(elim["eliminated_ball_numbers"]) == 16
    assert elim["pruned_universe_size"] == 55 - 16
    assert len(elim["pruned_universe"]) == 39
    assert elim["elimination_rate_pct"] == round(16 / 55 * 100, 1)

    for item in elim["eliminated_balls"]:
        assert 1 <= item["ball"] <= 55
        assert isinstance(item["risk_score"], (int, float))
        assert "reason" in item
        assert len(item["reason"]) > 0


def test_consensus_hub_contains_elimination_analytics_mega645(mega645_hub):
    """Test elimination_analytics exists and is properly structured for Mega 6/45."""
    assert "elimination_analytics" in mega645_hub, "hub must include elimination_analytics"
    elim = mega645_hub["elimination_analytics"]

    assert elim["eliminated_count"] == 13
    assert len(elim["eliminated_balls"]) == 13
    assert len(elim["eliminated_ball_numbers"]) == 13
    assert elim["pruned_universe_size"] == 45 - 13
    assert len(elim["pruned_universe"]) == 32
    assert elim["elimination_rate_pct"] == round(13 / 45 * 100, 1)

    for item in elim["eliminated_balls"]:
        assert 1 <= item["ball"] <= 45
        assert isinstance(item["risk_score"], (int, float))
        assert "reason" in item


def test_consensus_hub_contains_elimination_analytics_power535(power535_hub):
    """Test elimination_analytics exists and is properly structured for Power 5/35."""
    assert "elimination_analytics" in power535_hub, "hub must include elimination_analytics"
    elim = power535_hub["elimination_analytics"]

    assert elim["eliminated_count"] == 9
    assert len(elim["eliminated_balls"]) == 9
    assert len(elim["eliminated_ball_numbers"]) == 9
    assert elim["pruned_universe_size"] == 35 - 9
    assert len(elim["pruned_universe"]) == 26
    assert elim["elimination_rate_pct"] == round(9 / 35 * 100, 1)

    for item in elim["eliminated_balls"]:
        assert 1 <= item["ball"] <= 35
        assert isinstance(item["risk_score"], (int, float))
        assert "reason" in item


@pytest.mark.parametrize(
    "hub_fixture, expected_ball_count, min_ac",
    [
        ("power655_hub", 6, 7),
        ("mega645_hub", 6, 7),
        ("power535_hub", 5, 4),
    ],
)
def test_tickets_contains_banker_wheeling(request, hub_fixture, expected_ball_count, min_ac):
    """Test tickets.banker_wheeling contains banker, satellite_pool, 6 tickets, 100% banker, and valid AC."""
    hub = request.getfixturevalue(hub_fixture)
    assert "tickets" in hub
    tickets_dict = hub["tickets"]

    assert "banker_wheeling" in tickets_dict, "tickets must include banker_wheeling"
    bw = tickets_dict["banker_wheeling"]

    assert "banker" in bw
    banker = bw["banker"]
    assert isinstance(banker, int)

    assert "satellite_pool" in bw
    satellites = bw["satellite_pool"]
    assert len(satellites) == 10
    assert banker not in satellites

    assert bw["total_tickets"] == 6
    assert bw["total_cost"] == 60000
    assert "win_guarantee_statement" in bw
    assert "leverage_multiplier" in bw

    tickets = bw["tickets"]
    assert len(tickets) == 6

    for t in tickets:
        nums = t["numbers"]
        assert len(nums) == expected_ball_count
        assert nums == sorted(nums)
        assert banker in nums, f"Banker {banker} must be in ticket {nums}"
        assert t["ac"] >= min_ac, f"Ticket {nums} AC {t['ac']} must be >= {min_ac}"
        assert "sum" in t
        assert "odds" in t
        assert "evens" in t


def test_clean_satellites_exclude_eliminated_balls(power655_hub, mega645_hub, power535_hub):
    """Verify satellite pool never contains eliminated dead numbers across all products."""
    for hub in (power655_hub, mega645_hub, power535_hub):
        dead_numbers = set(hub["elimination_analytics"]["eliminated_ball_numbers"])
        satellites = hub["tickets"]["banker_wheeling"]["satellite_pool"]
        banker = hub["tickets"]["banker_wheeling"]["banker"]

        for s in satellites:
            assert s not in dead_numbers, f"Satellite ball {s} should not be in eliminated balls: {dead_numbers}"


def test_schema_backwards_compatibility(power655_hub):
    """Verify 100% schema backward compatibility: all existing top-level and tickets keys persist."""
    expected_top_keys = [
        "next_draw_id",
        "evaluated_draws_count",
        "leaderboard",
        "top_consensus_balls",
        "model_explanations",
        "models_info",
        "transition_analytics",
        "bankroll_advisory",
        "training_report",
        "tickets",
        "history_walk_forward",
        "elimination_analytics",  # newly added
    ]
    for key in expected_top_keys:
        assert key in power655_hub, f"Missing expected top-level key: {key}"

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
        "banker_wheeling",  # newly added
    ]
    tickets_dict = power655_hub["tickets"]
    for key in expected_ticket_keys:
        assert key in tickets_dict, f"Missing expected tickets key: {key}"
