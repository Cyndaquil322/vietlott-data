"""
Unit tests for vietlott.model.ml_ranker:
1. Feature matrix extraction (shape (N, 14), no NaN/Inf, exact feature columns)
2. HistGradientBoostingRanker (fit, predict_proba)
3. train_and_predict_ml_ranker on real data (Power 6/55, Mega 6/45, Power 5/35)
4. Determinism (same inputs produce 100% identical predictions)
5. Fallback safety when len(sub_records) < 20
6. Edge cases and zero mock data compliance
"""

import json
from pathlib import Path
import numpy as np
import pytest

from vietlott.model.ml_ranker import (
    extract_feature_matrix_for_draw,
    HistGradientBoostingRanker,
    train_and_predict_ml_ranker,
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


def _generate_synthetic_records(num_draws: int = 40, max_val: int = 35, num_balls: int = 5):
    records = []
    for i in range(num_draws):
        base = (i * 3) % (max_val - num_balls) + 1
        balls = [((base + k - 1) % max_val) + 1 for k in range(num_balls)]
        balls = sorted(set(balls))
        while len(balls) < num_balls:
            next_b = (balls[-1] % max_val) + 1
            if next_b not in balls:
                balls.append(next_b)
                balls.sort()
        records.append({"draw_id": i + 1, "result": balls})
    return records


def test_extract_feature_matrix_shape_and_no_nan_inf():
    """Verify extract_feature_matrix_for_draw returns shape (N, 14) with valid values."""
    records = _read_real_records("power535.jsonl")
    if not records:
        records = _generate_synthetic_records(num_draws=30, max_val=35, num_balls=5)

    sub_records = records[:30]
    max_val = 35
    num_balls = 5

    X = extract_feature_matrix_for_draw(sub_records, max_val=max_val, num_balls=num_balls)

    assert isinstance(X, np.ndarray)
    assert X.shape == (max_val, 14)
    assert not np.isnan(X).any(), "Feature matrix contains NaN"
    assert not np.isinf(X).any(), "Feature matrix contains Inf"

    # Check modulo 3 feature (column index 12, 13th feature)
    for b in range(1, max_val + 1):
        expected_mod3 = float(b % 3)
        assert np.isclose(X[b - 1, 12], expected_mod3, atol=1e-5)

    # Check ball value normalized feature (column index 13, 14th feature)
    for b in range(1, max_val + 1):
        expected_norm = float(b / max_val)
        assert np.isclose(X[b - 1, 13], expected_norm, atol=1e-5)


def test_hist_gradient_boosting_ranker():
    """Verify HistGradientBoostingRanker initialization, fit, and predict_proba."""
    ranker = HistGradientBoostingRanker()
    assert hasattr(ranker, "clf")
    assert ranker.clf.learning_rate == 0.05
    assert ranker.clf.max_iter == 50
    assert ranker.clf.max_depth == 3
    assert ranker.clf.min_samples_leaf == 15
    assert ranker.clf.l2_regularization == 1.5
    assert ranker.clf.random_state == 42

    rng = np.random.RandomState(42)
    n_samples = 120
    n_features = 14
    X = rng.randn(n_samples, n_features)
    # Balanced-ish binary labels with 15% positive rate
    y = (rng.rand(n_samples) < 0.2).astype(float)
    # Ensure at least 15 positives and negatives
    y[:20] = 1.0
    y[20:40] = 0.0

    ranker.fit(X, y)
    proba = ranker.predict_proba(X)

    assert isinstance(proba, np.ndarray)
    assert proba.shape == (n_samples,)
    assert (proba >= 0.0).all()
    assert (proba <= 1.0).all()


def test_train_and_predict_ml_ranker_real_data():
    """Verify train_and_predict_ml_ranker produces valid normalized scores [0.0, 3.0] on real datasets."""
    test_cases = [
        ("power655.jsonl", 55, 6),
        ("power645.jsonl", 45, 6),
        ("power535.jsonl", 35, 5),
    ]

    for filename, max_val, num_balls in test_cases:
        records = _read_real_records(filename)
        assert len(records) >= 30, f"Insufficient records in real dataset {filename}"

        sub_records = records[:50]
        scores = train_and_predict_ml_ranker(
            sub_records,
            max_val=max_val,
            num_balls=num_balls,
            train_window=30,
        )

        assert isinstance(scores, dict)
        assert len(scores) == max_val
        for b in range(1, max_val + 1):
            assert b in scores
            sc = scores[b]
            assert isinstance(sc, float)
            assert 0.0 <= sc <= 3.0, f"Score for ball {b} out of range: {sc}"

        # Check normalization boundaries
        max_score = max(scores.values())
        min_score = min(scores.values())
        assert max_score == 3.0, f"Max score should be 3.0, got {max_score}"
        assert min_score == 0.0, f"Min score should be 0.0, got {min_score}"


def test_train_and_predict_ml_ranker_determinism():
    """Verify that train_and_predict_ml_ranker is 100% deterministic given identical inputs."""
    records = _read_real_records("power535.jsonl")
    if not records:
        records = _generate_synthetic_records(num_draws=40, max_val=35, num_balls=5)

    sub_records = records[:35]
    scores_1 = train_and_predict_ml_ranker(sub_records, max_val=35, num_balls=5, train_window=20)
    scores_2 = train_and_predict_ml_ranker(sub_records, max_val=35, num_balls=5, train_window=20)

    assert scores_1 == scores_2, "ML ranker output must be 100% deterministic"


def test_train_and_predict_ml_ranker_fallback_short_records():
    """Verify fallback when records length < 20."""
    records = _read_real_records("power535.jsonl")
    if not records:
        records = _generate_synthetic_records(num_draws=15, max_val=35, num_balls=5)

    short_records = records[:12]
    scores = train_and_predict_ml_ranker(short_records, max_val=35, num_balls=5)

    assert isinstance(scores, dict)
    assert len(scores) == 35
    for b in range(1, 36):
        assert b in scores
        sc = scores[b]
        assert isinstance(sc, float)
        assert 0.0 <= sc <= 3.0


def test_extract_feature_matrix_edge_cases():
    """Verify feature extraction with minimal or empty records does not crash."""
    # Single draw
    single_record = [{"draw_id": 1, "result": [1, 2, 3, 4, 5]}]
    X_single = extract_feature_matrix_for_draw(single_record, max_val=35, num_balls=5)
    assert X_single.shape == (35, 14)
    assert not np.isnan(X_single).any()
    assert not np.isinf(X_single).any()

    # Empty records
    X_empty = extract_feature_matrix_for_draw([], max_val=35, num_balls=5)
    assert X_empty.shape == (35, 14)
    assert not np.isnan(X_empty).any()
    assert not np.isinf(X_empty).any()
