"""
Unit tests for 7 independent analytic engines in vietlott.model.analytic_engines:
1. calculate_bayesian_hazard_scores
2. calculate_exponential_decay_scores
3. calculate_markov_ppmi_scores
4. calculate_hybrid_spectral_scores
5. calculate_empirical_bayes_lift_scores
6. calculate_graph_pagerank_scores (New Model 1)
7. calculate_state_space_scores (New Model 2)
8. evaluate_all_models (7 models + cur_gap)
9. Determinism and stability tests
"""

import math
import pytest
from vietlott.model.analytic_engines import (
    calculate_bayesian_hazard_scores,
    calculate_exponential_decay_scores,
    calculate_markov_ppmi_scores,
    calculate_hybrid_spectral_scores,
    calculate_empirical_bayes_lift_scores,
    calculate_graph_pagerank_scores,
    calculate_state_space_scores,
    evaluate_all_models,
)


def _generate_synthetic_records(num_draws: int = 100, max_val: int = 45, num_balls: int = 6):
    """Generate deterministic synthetic draw records for unit testing."""
    records = []
    for i in range(num_draws):
        # Deterministic sequence of balls
        base = (i * 3) % (max_val - num_balls) + 1
        balls = [((base + k - 1) % max_val) + 1 for k in range(num_balls)]
        # Ensure unique sorted balls
        balls = sorted(set(balls))
        while len(balls) < num_balls:
            next_b = (balls[-1] % max_val) + 1
            if next_b not in balls:
                balls.append(next_b)
                balls.sort()
        records.append({"draw_id": i + 1, "result": balls})
    return records


def test_bayesian_hazard_scores():
    max_val = 45
    num_balls = 6
    records = _generate_synthetic_records(num_draws=80, max_val=max_val, num_balls=num_balls)

    scores = calculate_bayesian_hazard_scores(records, max_val=max_val, num_balls=num_balls)
    assert isinstance(scores, dict)
    assert len(scores) == max_val
    for b in range(1, max_val + 1):
        assert b in scores
        assert isinstance(scores[b], float)
        assert scores[b] >= 0.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])
        assert scores[b] == round(scores[b], 3)

    # Empty records check
    empty_scores = calculate_bayesian_hazard_scores([], max_val=max_val, num_balls=num_balls)
    assert len(empty_scores) == max_val
    assert all(s >= 0.0 for s in empty_scores.values())


def test_exponential_decay_scores():
    max_val = 45
    num_balls = 6
    records = _generate_synthetic_records(num_draws=60, max_val=max_val, num_balls=num_balls)
    
    # Ball 10 is forced into the latest draw, Ball 40 is not in recent draws
    records[-1]["result"] = [10, 11, 12, 13, 14, 15]

    scores = calculate_exponential_decay_scores(records, max_val=max_val, num_balls=num_balls, alpha=0.035)
    assert isinstance(scores, dict)
    assert len(scores) == max_val
    assert scores[10] > 0.0
    for b in range(1, max_val + 1):
        assert scores[b] >= 0.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])


def test_markov_ppmi_scores():
    max_val = 45
    num_balls = 6
    # Build sequence where [1, 2, 3, 4, 5, 6] is frequently followed by ball 7
    records = []
    for i in range(50):
        records.append({"draw_id": 2 * i + 1, "result": [1, 2, 3, 4, 5, 6]})
        records.append({"draw_id": 2 * i + 2, "result": [7, 8, 9, 10, 11, 12]})
    # Last draw is [1, 2, 3, 4, 5, 6]
    records.append({"draw_id": 101, "result": [1, 2, 3, 4, 5, 6]})

    scores = calculate_markov_ppmi_scores(records, max_val=max_val, num_balls=num_balls)
    assert isinstance(scores, dict)
    assert len(scores) == max_val
    for b in range(1, max_val + 1):
        assert scores[b] >= 0.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])

    # Ball 7 should have a high transition PPMI score from {1, 2, 3, 4, 5, 6}
    assert scores[7] > 0.0
    assert scores[7] > scores[40]


def test_hybrid_spectral_scores():
    max_val = 45
    num_balls = 6
    records = _generate_synthetic_records(num_draws=70, max_val=max_val, num_balls=num_balls)

    scores = calculate_hybrid_spectral_scores(records, max_val=max_val, num_balls=num_balls, window_len=64)
    assert isinstance(scores, dict)
    assert len(scores) == max_val
    for b in range(1, max_val + 1):
        assert scores[b] >= 0.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])
        assert scores[b] == round(scores[b], 3)


def test_empirical_bayes_lift_scores():
    max_val = 45
    num_balls = 6
    # Build sequence where pair (1, 2) strongly pulls ball 9
    records = []
    for i in range(60):
        records.append({"draw_id": 2 * i + 1, "result": [1, 2, 10, 11, 12, 13]})
        records.append({"draw_id": 2 * i + 2, "result": [9, 20, 21, 22, 23, 24]})
    # Last draw contains pair (1, 2)
    records.append({"draw_id": 121, "result": [1, 2, 30, 31, 32, 33]})

    scores = calculate_empirical_bayes_lift_scores(records, max_val=max_val, num_balls=num_balls)
    assert isinstance(scores, dict)
    assert len(scores) == max_val
    for b in range(1, max_val + 1):
        assert scores[b] >= 0.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])
        assert scores[b] == round(scores[b], 3)

    assert scores[9] > 0.0


def test_graph_pagerank_scores():
    max_val = 45
    num_balls = 6
    # Create records where balls 1, 2, 3, 4, 5, 6 form a tight co-occurrence cluster
    records = []
    for i in range(50):
        records.append({"draw_id": i + 1, "result": [1, 2, 3, 4, 5, 6]})
    for i in range(50, 80):
        records.append({"draw_id": i + 1, "result": [7, 8, 9, 10, 11, 12]})

    scores = calculate_graph_pagerank_scores(
        records, max_val=max_val, num_balls=num_balls, damping=0.85, max_iter=50, window_len=100
    )
    assert isinstance(scores, dict)
    assert len(scores) == max_val

    for b in range(1, max_val + 1):
        assert b in scores
        assert isinstance(scores[b], float)
        assert 0.0 <= scores[b] <= 3.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])
        assert scores[b] == round(scores[b], 3)

    # Balls in the frequent cluster (1..6) should have higher PageRank than balls never drawn (e.g. 40)
    assert scores[1] > scores[40]
    assert max(scores.values()) == 3.0

    # Empty records test
    empty_scores = calculate_graph_pagerank_scores([], max_val=max_val, num_balls=num_balls)
    assert len(empty_scores) == max_val
    assert all(not math.isnan(v) for v in empty_scores.values())


def test_state_space_scores():
    max_val = 45
    num_balls = 6
    # Create a history where ball 5 appears in every one of the last 15 draws (hot burst),
    # while ball 35 never appears at all.
    records = []
    for i in range(50):
        records.append({"draw_id": i + 1, "result": [1, 2, 3, 4, 6, 7]})
    for i in range(50, 70):
        records.append({"draw_id": i + 1, "result": [1, 2, 3, 4, 5, 6]})

    scores = calculate_state_space_scores(
        records, max_val=max_val, num_balls=num_balls, decay=0.92, window_len=80
    )
    assert isinstance(scores, dict)
    assert len(scores) == max_val

    for b in range(1, max_val + 1):
        assert b in scores
        assert isinstance(scores[b], float)
        assert 0.0 <= scores[b] <= 3.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])
        assert scores[b] == round(scores[b], 3)

    # Hot burst ball 5 must have a significantly higher score than ball 35 (never appeared)
    assert scores[5] > scores[35]
    assert max(scores.values()) == 3.0

    # Empty records test
    empty_scores = calculate_state_space_scores([], max_val=max_val, num_balls=num_balls)
    assert len(empty_scores) == max_val
    assert all(not math.isnan(v) for v in empty_scores.values())


def test_evaluate_all_models_seven_models():
    max_val = 35
    num_balls = 5
    records = _generate_synthetic_records(num_draws=50, max_val=max_val, num_balls=num_balls)

    models_dict = evaluate_all_models(records, max_val=max_val, num_balls=num_balls, is_two_matrix=True)
    assert isinstance(models_dict, dict)

    expected_keys = {"hazard", "decay", "markov", "fourier", "bac_nho", "graph_pagerank", "state_space", "cur_gap"}
    assert set(models_dict.keys()) == expected_keys

    for m in ["hazard", "decay", "markov", "fourier", "bac_nho", "graph_pagerank", "state_space", "cur_gap"]:
        assert len(models_dict[m]) == max_val
        for b in range(1, max_val + 1):
            assert b in models_dict[m]
            val = models_dict[m][b]
            assert not math.isnan(val)
            assert not math.isinf(val)
            assert val >= 0


def test_determinism():
    max_val = 55
    num_balls = 6
    records = _generate_synthetic_records(num_draws=60, max_val=max_val, num_balls=num_balls)

    res1 = evaluate_all_models(records, max_val=max_val, num_balls=num_balls)
    res2 = evaluate_all_models(records, max_val=max_val, num_balls=num_balls)

    assert res1 == res2


def test_evaluate_all_models_empty_records():
    max_val = 55
    num_balls = 6
    models_dict = evaluate_all_models([], max_val=max_val, num_balls=num_balls)
    assert isinstance(models_dict, dict)
    expected_keys = {"hazard", "decay", "markov", "fourier", "bac_nho", "graph_pagerank", "state_space", "cur_gap"}
    assert set(models_dict.keys()) == expected_keys
    for m in expected_keys:
        assert len(models_dict[m]) == max_val
        for b in range(1, max_val + 1):
            assert not math.isnan(models_dict[m][b])


def test_kalman_filter_dynamics_and_covariance():
    """Verify that Kalman state estimates and covariance behave correctly."""
    max_val = 10
    num_balls = 2
    # Single ball appearing consecutively
    records = [{"draw_id": i + 1, "result": [1, 2]} for i in range(30)]
    scores = calculate_state_space_scores(records, max_val=max_val, num_balls=num_balls, decay=0.92)
    # Balls 1 and 2 should have score 3.0
    assert scores[1] == 3.0
    assert scores[2] == 3.0
    # Balls 3..10 never appeared, so their score should be 0.0
    for b in range(3, 11):
        assert scores[b] == 0.0

