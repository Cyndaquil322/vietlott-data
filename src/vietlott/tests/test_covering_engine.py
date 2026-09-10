"""
Test suite for Combinatorial Covering Wheel Engine (Task 1).
Tests mathematical coverage guarantees, metrics calculation, and filtered ticket generation.
"""

import pytest
from typing import List, Dict, Any


def test_import_covering_engine():
    """Ensure covering_engine module and required symbols can be imported."""
    from vietlott.model.covering_engine import (
        get_optimal_covering_patterns,
        evaluate_covering_guarantee,
        calculate_ticket_metrics,
        generate_filtered_wheel_tickets,
    )
    assert callable(get_optimal_covering_patterns)
    assert callable(evaluate_covering_guarantee)
    assert callable(calculate_ticket_metrics)
    assert callable(generate_filtered_wheel_tickets)


def test_optimal_covering_patterns_c12_6_6():
    """Verify C(12, 6, 3) 6-ticket covering pattern matches brief exactly."""
    from vietlott.model.covering_engine import get_optimal_covering_patterns

    patterns = get_optimal_covering_patterns(v=12, k=6, num_tickets=6)
    expected = [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 6, 7, 8],
        [0, 3, 4, 6, 9, 10],
        [1, 3, 5, 7, 9, 11],
        [2, 4, 5, 8, 10, 11],
        [6, 7, 8, 9, 10, 11],
    ]
    assert patterns == expected
    assert len(patterns) == 6
    for p in patterns:
        assert len(p) == 6
        assert all(0 <= idx < 12 for idx in p)


def test_optimal_covering_patterns_c12_6_8():
    """Verify C(12, 6, 3) 8-ticket 100% 4-subset covering pattern matches brief exactly."""
    from vietlott.model.covering_engine import get_optimal_covering_patterns

    patterns = get_optimal_covering_patterns(v=12, k=6, num_tickets=8)
    expected = [
        [0, 1, 2, 3, 4, 5],
        [0, 6, 7, 8, 9, 10],
        [1, 2, 3, 6, 7, 11],
        [4, 5, 8, 9, 10, 11],
        [1, 2, 4, 5, 6, 7],
        [3, 4, 5, 8, 9, 10],
        [0, 1, 8, 9, 10, 11],
        [0, 1, 2, 4, 5, 11],
    ]
    assert patterns == expected
    assert len(patterns) == 8
    for p in patterns:
        assert len(p) == 6
        assert all(0 <= idx < 12 for idx in p)


def test_optimal_covering_patterns_c10_5_6():
    """Verify C(10, 5, 3) 6-ticket pattern for 5/35 matches brief exactly."""
    from vietlott.model.covering_engine import get_optimal_covering_patterns

    patterns = get_optimal_covering_patterns(v=10, k=5, num_tickets=6)
    expected = [
        [0, 1, 2, 3, 4],
        [0, 1, 5, 6, 7],
        [0, 2, 5, 8, 9],
        [1, 3, 6, 8, 9],
        [2, 4, 6, 7, 8],
        [3, 4, 5, 7, 9],
    ]
    assert patterns == expected
    assert len(patterns) == 6
    for p in patterns:
        assert len(p) == 5
        assert all(0 <= idx < 10 for idx in p)


def test_optimal_covering_patterns_fallback():
    """Verify fallback and slicing for custom arguments."""
    from vietlott.model.covering_engine import get_optimal_covering_patterns

    # Sliced tickets
    sliced_4 = get_optimal_covering_patterns(v=12, k=6, num_tickets=4)
    assert len(sliced_4) == 4
    assert sliced_4 == [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 6, 7, 8],
        [0, 3, 4, 6, 9, 10],
        [1, 3, 5, 7, 9, 11],
    ]

    # Arbitrary v, k fallback
    custom = get_optimal_covering_patterns(v=8, k=4, num_tickets=3)
    assert len(custom) == 3
    for p in custom:
        assert len(p) == 4
        assert all(0 <= idx < 8 for idx in p)


def test_evaluate_covering_guarantee_c12_6_6():
    """Verify mathematical coverage evaluation for C(12, 6, 6) meets >= 95.0%."""
    from vietlott.model.covering_engine import (
        get_optimal_covering_patterns,
        evaluate_covering_guarantee,
    )

    pats = get_optimal_covering_patterns(v=12, k=6, num_tickets=6)
    metrics = evaluate_covering_guarantee(v=12, k=6, patterns=pats)

    assert metrics["total_triples"] == 220  # C(12, 3)
    assert metrics["total_quads"] == 495    # C(12, 4)
    assert metrics["covered_triples"] > 0
    assert metrics["covered_quads"] > 0
    assert metrics["cov_3_if_4_pct"] >= 95.0
    assert 0.0 <= metrics["cov_3_if_3_pct"] <= 100.0


def test_evaluate_covering_guarantee_c12_6_8():
    """Verify C(12, 6, 8) achieves 100% 4-subset coverage."""
    from vietlott.model.covering_engine import (
        get_optimal_covering_patterns,
        evaluate_covering_guarantee,
    )

    pats = get_optimal_covering_patterns(v=12, k=6, num_tickets=8)
    metrics = evaluate_covering_guarantee(v=12, k=6, patterns=pats)

    assert metrics["total_quads"] == 495
    assert metrics["covered_quads"] == 495
    assert metrics["cov_3_if_4_pct"] == 100.0


def test_evaluate_covering_guarantee_c10_5_6():
    """Verify C(10, 5, 6) achieves >= 95.0% 4-subset coverage for 5/35."""
    from vietlott.model.covering_engine import (
        get_optimal_covering_patterns,
        evaluate_covering_guarantee,
    )

    pats = get_optimal_covering_patterns(v=10, k=5, num_tickets=6)
    metrics = evaluate_covering_guarantee(v=10, k=5, patterns=pats)

    assert metrics["total_triples"] == 120  # C(10, 3)
    assert metrics["total_quads"] == 210    # C(10, 4)
    assert metrics["cov_3_if_4_pct"] >= 95.0


def test_calculate_ticket_metrics_arithmetic_complexity():
    """Verify ticket metrics: sum, ac index, odds, evens, distinctTails."""
    from vietlott.model.covering_engine import calculate_ticket_metrics

    # Consecutive numbers: differences are {1, 2, 3, 4, 5} -> len=5 -> AC = 5 - (6 - 1) = 0
    consecutive = [1, 2, 3, 4, 5, 6]
    m1 = calculate_ticket_metrics(consecutive, max_val=55)
    assert m1["sum"] == 21
    assert m1["ac_index"] == 0
    assert m1["ac"] == 0
    assert m1["odds"] == 3
    assert m1["evens"] == 3
    assert m1["distinctTails"] == 6

    # Spread numbers with high complexity
    spread = [5, 12, 23, 31, 42, 54]
    m2 = calculate_ticket_metrics(spread, max_val=55)
    assert m2["sum"] == 167
    assert m2["ac_index"] >= 7
    assert m2["odds"] == 3
    assert m2["evens"] == 3
    assert m2["distinctTails"] >= 4


def test_generate_filtered_wheel_tickets_power655():
    """Verify generate_filtered_wheel_tickets for Power 6/55 with 6 tickets."""
    from vietlott.model.covering_engine import generate_filtered_wheel_tickets

    candidates = [3, 7, 12, 18, 23, 29, 34, 38, 42, 47, 51, 54, 5, 19]
    res = generate_filtered_wheel_tickets(
        candidates=candidates,
        product_key="power_655",
        max_val=55,
        num_balls=6,
        num_tickets=6,
    )

    assert "core_pool" in res
    assert "core_pool_size" in res
    assert "tickets" in res
    assert "coverage" in res
    assert "guarantee_statement" in res

    assert res["core_pool_size"] == 12
    assert len(res["core_pool"]) == 12
    assert len(res["tickets"]) == 6

    # Coverage guarantee check
    assert res["coverage"]["cov_3_if_4_pct"] >= 95.0

    # Guarantee statement
    assert "bảo hiểm" in res["guarantee_statement"].lower()

    # Negative space AC check: all tickets should have AC >= 7 for 6-ball games
    for t in res["tickets"]:
        assert len(t["numbers"]) == 6
        assert t["ac"] >= 7
        assert t["ac_index"] >= 7
        assert "sum" in t
        assert "odds" in t
        assert "evens" in t
        assert "distinctTails" in t


def test_generate_filtered_wheel_tickets_mega645_8_tickets():
    """Verify generate_filtered_wheel_tickets for Mega 6/45 with 8 tickets (100% guarantee)."""
    from vietlott.model.covering_engine import generate_filtered_wheel_tickets

    candidates = [2, 5, 11, 16, 22, 28, 33, 37, 40, 41, 44, 45]
    res = generate_filtered_wheel_tickets(
        candidates=candidates,
        product_key="power_645",
        max_val=45,
        num_balls=6,
        num_tickets=8,
    )

    assert res["core_pool_size"] == 12
    assert len(res["tickets"]) == 8
    assert res["coverage"]["cov_3_if_4_pct"] == 100.0
    for t in res["tickets"]:
        assert len(t["numbers"]) == 6
        assert t["ac"] >= 7


def test_generate_filtered_wheel_tickets_power535():
    """Verify generate_filtered_wheel_tickets for Power 5/35 (v=10, k=5, AC >= 4)."""
    from vietlott.model.covering_engine import generate_filtered_wheel_tickets

    candidates = [3, 8, 14, 19, 22, 25, 29, 31, 33, 35]
    res = generate_filtered_wheel_tickets(
        candidates=candidates,
        product_key="power_535",
        max_val=35,
        num_balls=5,
        num_tickets=6,
    )

    assert res["core_pool_size"] == 10
    assert len(res["core_pool"]) == 10
    assert len(res["tickets"]) == 6
    assert res["coverage"]["cov_3_if_4_pct"] >= 95.0

    for t in res["tickets"]:
        assert len(t["numbers"]) == 5
        assert t["ac"] >= 4
        assert t["ac_index"] >= 4


def test_extract_optimal_septet_power655():
    """Verify extract_optimal_septet returns 7 numbers from 12-number core pool with high AC."""
    from vietlott.model.covering_engine import extract_optimal_septet

    core_pool = [3, 8, 12, 19, 24, 27, 33, 38, 42, 45, 50, 53]
    records = [
        {"id": "01001", "result": [3, 12, 24, 33, 42, 50, 8]},
        {"id": "01002", "result": [8, 19, 27, 38, 45, 53, 12]},
        {"id": "01003", "result": [3, 8, 19, 24, 33, 50, 42]},
    ]
    res = extract_optimal_septet(
        core_pool=core_pool,
        past_records=records,
        max_val=55,
        num_balls=6,
        is_two_matrix=False,
        seed=1004,
    )
    assert "numbers" in res
    assert len(res["numbers"]) == 7
    assert set(res["numbers"]).issubset(set(core_pool))
    assert res["ac_index"] >= 10
    assert "sum" in res
    assert "odd_even" in res
    assert "lift_score" in res


def test_extract_optimal_septet_power535():
    """Verify extract_optimal_septet for Power 5/35 returns 6 numbers + special."""
    from vietlott.model.covering_engine import extract_optimal_septet

    core_pool = [2, 7, 11, 15, 18, 22, 26, 29, 31, 35]
    records = [
        {"id": "00801", "result": [2, 11, 18, 26, 31, 7]},
        {"id": "00802", "result": [7, 15, 22, 29, 35, 11]},
    ]
    res = extract_optimal_septet(
        core_pool=core_pool,
        past_records=records,
        max_val=35,
        num_balls=5,
        is_two_matrix=True,
        seed=803,
    )
    assert len(res["numbers"]) == 6
    assert set(res["numbers"]).issubset(set(core_pool))
    assert res["special"] is not None


def test_extract_optimal_septet_determinism():
    """Verify extract_optimal_septet is 100% deterministic given same seed and inputs."""
    from vietlott.model.covering_engine import extract_optimal_septet

    core_pool = [1, 5, 9, 14, 18, 23, 27, 32, 36, 40, 44, 45]
    records = [{"id": "001", "result": [1, 5, 9, 14, 18, 23]}]
    res1 = extract_optimal_septet(core_pool, records, 45, 6, False, seed=999)
    res2 = extract_optimal_septet(core_pool, records, 45, 6, False, seed=999)
    assert res1["numbers"] == res2["numbers"]

