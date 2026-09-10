"""
Unit tests for vietlott.model.transition_engine:
1. build_transition_matrix (synthetic & real data)
2. calculate_vector_field_pull (synthetic & real data)
3. extract_significant_transition_rules (pull & repulsion rules)
4. Edge cases (empty records, single draw)
5. Determinism & zero mock data
"""

import math
import json
from pathlib import Path
import pytest

from vietlott.model.transition_engine import (
    build_transition_matrix,
    calculate_vector_field_pull,
    extract_significant_transition_rules,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _read_real_records(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _generate_synthetic_records(num_draws: int = 50, max_val: int = 35, num_balls: int = 5):
    records = []
    for i in range(num_draws):
        base = (i * 2) % (max_val - num_balls) + 1
        balls = [((base + k - 1) % max_val) + 1 for k in range(num_balls)]
        balls = sorted(set(balls))
        while len(balls) < num_balls:
            next_b = (balls[-1] % max_val) + 1
            if next_b not in balls:
                balls.append(next_b)
                balls.sort()
        records.append({"draw_id": i + 1, "result": balls})
    return records


def test_build_transition_matrix_synthetic_calculation():
    """Verify exact calculation of N_A, N_B, N_AB, E_AB, Z-score, Lift on controlled data."""
    # 3 draws:
    # t=1: [1, 2, 3]
    # t=2: [1, 2, 4]
    # t=3: [1, 5, 6]
    records = [
        {"draw_id": 1, "result": [1, 2, 3]},
        {"draw_id": 2, "result": [1, 2, 4]},
        {"draw_id": 3, "result": [1, 5, 6]},
    ]
    max_val = 6
    num_balls = 3
    matrix = build_transition_matrix(records, max_val=max_val, num_balls=num_balls, window_len=10)

    # Number of transitions = 2 (t=1->2 and t=2->3)
    # Ball 1 at t-1: in draw 1, in draw 2 -> N_A[1] = 2
    # Ball 1 at t: in draw 2, in draw 3 -> N_B[1] = 2
    # Pair (1, 1): in 1->2 (1 in draw 1, 1 in draw 2), in 2->3 (1 in draw 2, 1 in draw 3) -> N_AB[(1, 1)] = 2
    cell_1_1 = matrix[(1, 1)]
    assert cell_1_1["n_a"] == 2
    assert cell_1_1["n_b"] == 2
    assert cell_1_1["n_ab"] == 2
    assert cell_1_1["is_repeat"] is True
    assert math.isclose(cell_1_1["prob"], 1.0, rel_tol=1e-5)
    assert math.isclose(cell_1_1["prob_prior"], 1.0, rel_tol=1e-5)
    assert math.isclose(cell_1_1["expected"], 2.0, rel_tol=1e-5)
    assert math.isclose(cell_1_1["lift"], 1.0, rel_tol=1e-3)
    assert math.isclose(cell_1_1["z_score"], 0.0, abs_tol=1e-3)

    # Ball 3 at t-1: in draw 1 -> N_A[3] = 1
    # Ball 4 at t: in draw 2 -> N_B[4] = 1
    # Pair (3, 4): in 1->2 (3 in draw 1, 4 in draw 2) -> N_AB[(3, 4)] = 1
    cell_3_4 = matrix[(3, 4)]
    assert cell_3_4["n_a"] == 1
    assert cell_3_4["n_b"] == 1
    assert cell_3_4["n_ab"] == 1
    assert cell_3_4["is_repeat"] is False
    assert math.isclose(cell_3_4["prob"], 1.0, rel_tol=1e-5)
    assert math.isclose(cell_3_4["prob_prior"], 0.5, rel_tol=1e-5)
    assert math.isclose(cell_3_4["expected"], 0.5, rel_tol=1e-5)
    assert cell_3_4["lift"] > 1.9  # 1.0 / 0.5 = 2.0
    assert cell_3_4["z_score"] > 0.0

    # Pair (3, 6): 3 in draw 1, 6 in draw 3 (not consecutive) -> N_AB[(3, 6)] = 0
    cell_3_6 = matrix[(3, 6)]
    assert cell_3_6["n_ab"] == 0
    assert cell_3_6["lift"] == 0.0
    assert cell_3_6["z_score"] < 0.0  # N_AB < E_AB -> negative Z


def test_build_transition_matrix_real_data():
    """Verify matrix dimensions, no NaN/Inf, valid ranges with real Power 6/55 data."""
    records = _read_real_records("power655.jsonl")
    assert len(records) > 100, "power655.jsonl should have > 100 draws"

    max_val = 55
    num_balls = 6
    matrix = build_transition_matrix(records, max_val=max_val, num_balls=num_balls, window_len=150)

    # Check complete coverage: 55 * 55 = 3025 cells
    assert len(matrix) == max_val * max_val

    required_keys = {"n_a", "n_b", "n_ab", "prob", "prob_prior", "expected", "std", "z_score", "lift", "is_repeat"}
    for (a, b), cell in matrix.items():
        assert 1 <= a <= max_val
        assert 1 <= b <= max_val
        assert required_keys.issubset(cell.keys())
        assert not math.isnan(cell["z_score"])
        assert not math.isinf(cell["z_score"])
        assert not math.isnan(cell["lift"])
        assert not math.isinf(cell["lift"])
        assert 0.0 <= cell["prob"] <= 1.0
        assert 0.0 <= cell["prob_prior"] <= 1.0
        assert cell["lift"] >= 0.0
        assert cell["is_repeat"] == (a == b)


def test_calculate_vector_field_pull():
    """Verify calculate_vector_field_pull returns 4 non-NaN fields for every ball 1..max_val."""
    records = _read_real_records("power535.jsonl")
    if not records:
        records = _generate_synthetic_records(num_draws=80, max_val=35, num_balls=5)

    max_val = 35
    num_balls = 5
    pulls = calculate_vector_field_pull(records, max_val=max_val, num_balls=num_balls, window_len=150)

    assert len(pulls) == max_val
    latest_balls = set(records[-1]["result"][:num_balls])

    for b in range(1, max_val + 1):
        assert b in pulls
        item = pulls[b]
        assert "max_pull_lift" in item
        assert "sum_z_score" in item
        assert "repulsion_penalty" in item
        assert "repeat_momentum" in item

        for key in ["max_pull_lift", "sum_z_score", "repulsion_penalty", "repeat_momentum"]:
            val = item[key]
            assert isinstance(val, (int, float))
            assert not math.isnan(val)
            assert not math.isinf(val)

        assert item["sum_z_score"] >= 0.0
        assert item["max_pull_lift"] >= item["repulsion_penalty"]

        # repeat_momentum must be 0 if ball was not in latest draw
        if b not in latest_balls:
            assert item["repeat_momentum"] == 0.0
        else:
            assert item["repeat_momentum"] >= 0.0


def test_extract_significant_transition_rules():
    """Verify pull rules and repulsion rules filtering, sorting, and structure."""
    records = _read_real_records("power645.jsonl")
    if not records:
        records = _generate_synthetic_records(num_draws=100, max_val=45, num_balls=6)

    max_val = 45
    num_balls = 6
    min_z = 1.5
    max_rules = 8

    res = extract_significant_transition_rules(
        records, max_val=max_val, num_balls=num_balls, min_z=min_z, max_rules=max_rules, window_len=150
    )

    assert "latest_draw_numbers" in res
    assert "top_pull_rules" in res
    assert "top_repulsion_rules" in res

    latest_expected = sorted(records[-1]["result"][:num_balls])
    assert res["latest_draw_numbers"] == latest_expected

    pull_rules = res["top_pull_rules"]
    rep_rules = res["top_repulsion_rules"]

    assert len(pull_rules) <= max_rules
    assert len(rep_rules) <= max_rules

    # Verify pull rules
    for rule in pull_rules:
        assert rule["from_ball"] in latest_expected
        assert rule["to_ball"] != rule["from_ball"]
        assert 1 <= rule["to_ball"] <= max_val
        assert rule["z_score"] >= min_z
        assert rule["lift"] >= 0.0
        assert rule["strength"] in ("Cực Mạnh", "Mạnh")
        if rule["z_score"] >= 2.5:
            assert rule["strength"] == "Cực Mạnh"
        else:
            assert rule["strength"] == "Mạnh"
        assert "/" in rule["historical_hits"]
        assert "%" in rule["historical_hits"]

    # Verify sorting of pull rules (descending by z_score)
    for i in range(len(pull_rules) - 1):
        assert pull_rules[i]["z_score"] >= pull_rules[i + 1]["z_score"]

    # Verify repulsion rules
    for rule in rep_rules:
        assert rule["from_ball"] in latest_expected
        assert rule["to_ball"] != rule["from_ball"]
        assert 1 <= rule["to_ball"] <= max_val
        assert rule["z_score"] <= -min_z
        assert rule["warning"] in ("Kỵ nhau mạnh — Nên loại bỏ", "Xung khắc nhẹ")
        if rule["z_score"] <= -2.0:
            assert rule["warning"] == "Kỵ nhau mạnh — Nên loại bỏ"
        else:
            assert rule["warning"] == "Xung khắc nhẹ"
        assert "/" in rule["historical_hits"]
        assert "%" in rule["historical_hits"]

    # Verify sorting of repulsion rules (ascending by z_score, i.e. most negative first)
    for i in range(len(rep_rules) - 1):
        assert rep_rules[i]["z_score"] <= rep_rules[i + 1]["z_score"]


def test_edge_cases():
    """Verify behavior on empty records and single-draw records."""
    # 1. Empty records
    matrix_empty = build_transition_matrix([], max_val=45, num_balls=6)
    assert len(matrix_empty) == 45 * 45
    for cell in matrix_empty.values():
        assert cell["z_score"] == 0.0
        assert cell["lift"] == 0.0

    pulls_empty = calculate_vector_field_pull([], max_val=45, num_balls=6)
    assert len(pulls_empty) == 45
    for b in range(1, 46):
        assert pulls_empty[b]["max_pull_lift"] == 1.0
        assert pulls_empty[b]["repulsion_penalty"] == 1.0
        assert pulls_empty[b]["sum_z_score"] == 0.0
        assert pulls_empty[b]["repeat_momentum"] == 0.0

    rules_empty = extract_significant_transition_rules([], max_val=45, num_balls=6)
    assert rules_empty["latest_draw_numbers"] == []
    assert rules_empty["top_pull_rules"] == []
    assert rules_empty["top_repulsion_rules"] == []

    # 2. Single draw
    single_record = [{"draw_id": 1, "result": [2, 10, 18, 25, 33, 40]}]
    matrix_single = build_transition_matrix(single_record, max_val=45, num_balls=6)
    assert len(matrix_single) == 45 * 45

    pulls_single = calculate_vector_field_pull(single_record, max_val=45, num_balls=6)
    assert len(pulls_single) == 45
    for b in range(1, 46):
        assert not math.isnan(pulls_single[b]["max_pull_lift"])
        assert not math.isnan(pulls_single[b]["sum_z_score"])

    rules_single = extract_significant_transition_rules(single_record, max_val=45, num_balls=6)
    assert rules_single["latest_draw_numbers"] == [2, 10, 18, 25, 33, 40]
    assert rules_single["top_pull_rules"] == []
    assert rules_single["top_repulsion_rules"] == []


def test_determinism():
    """Verify identical outputs on consecutive invocations (100% deterministic)."""
    records = _read_real_records("power655.jsonl")[:60]
    if not records:
        records = _generate_synthetic_records(num_draws=40, max_val=55, num_balls=6)

    m1 = build_transition_matrix(records, 55, 6, window_len=50)
    m2 = build_transition_matrix(records, 55, 6, window_len=50)
    assert m1 == m2

    p1 = calculate_vector_field_pull(records, 55, 6, window_len=50)
    p2 = calculate_vector_field_pull(records, 55, 6, window_len=50)
    assert p1 == p2

    r1 = extract_significant_transition_rules(records, 55, 6, min_z=1.5, window_len=50)
    r2 = extract_significant_transition_rules(records, 55, 6, min_z=1.5, window_len=50)
    assert r1 == r2
