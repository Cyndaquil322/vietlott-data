"""
Test suite for Daubechies Wavelet Multi-Resolution Analysis Engine (Task 1).
Verifies:
1. Filter coefficients and orthogonality of Daubechies 4 (db4).
2. 1D DWT step with periodic wrap padding and energy conservation.
3. Multi-level Mallat signal decomposition (levels=2: A2, D1, D2).
4. calculate_wavelet_spectral_scores with synthetic and real Vietlott draw data.
5. Edge cases: empty records, short windows, unseen balls, numerical validity.
"""

import math
from pathlib import Path
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def test_import_wavelet_engine():
    """Ensure WaveletAnalyzer and calculate_wavelet_spectral_scores are importable."""
    from vietlott.model.wavelet_engine import (
        WaveletAnalyzer,
        calculate_wavelet_spectral_scores,
    )

    assert hasattr(WaveletAnalyzer, "dwt_step")
    assert hasattr(WaveletAnalyzer, "decompose_signal")
    assert callable(calculate_wavelet_spectral_scores)


def test_db4_filter_coefficients_and_orthogonality():
    """Verify exact DB4 filter coefficients and orthogonality properties."""
    from vietlott.model.wavelet_engine import WaveletAnalyzer

    _sqrt3 = math.sqrt(3)
    _denom = 4 * math.sqrt(2)
    expected_lp = [
        (1 + _sqrt3) / _denom,
        (3 + _sqrt3) / _denom,
        (3 - _sqrt3) / _denom,
        (1 - _sqrt3) / _denom,
    ]
    expected_hp = [
        (1 - _sqrt3) / _denom,
        -(3 - _sqrt3) / _denom,
        (3 + _sqrt3) / _denom,
        -(1 + _sqrt3) / _denom,
    ]

    h0 = np.array(WaveletAnalyzer.DB4_LP, dtype=float)
    h1 = np.array(WaveletAnalyzer.DB4_HP, dtype=float)

    # Check exact values
    np.testing.assert_allclose(h0, expected_lp, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(h1, expected_hp, rtol=1e-12, atol=1e-12)

    # Orthogonality conditions:
    # 1. Energy of low-pass filter sum(h0^2) == 1
    assert math.isclose(float(np.sum(h0**2)), 1.0, rel_tol=1e-10)

    # 2. Energy of high-pass filter sum(h1^2) == 1
    assert math.isclose(float(np.sum(h1**2)), 1.0, rel_tol=1e-10)

    # 3. Cross-orthogonality sum(h0 * h1) == 0
    assert math.isclose(float(np.sum(h0 * h1)), 0.0, abs_tol=1e-10)


def test_dwt_step_shapes_and_energy_conservation():
    """Verify dwt_step output shape (len//2) and energy preservation."""
    from vietlott.model.wavelet_engine import WaveletAnalyzer

    np.random.seed(42)
    # Test on 64-element signal
    signal = np.random.randn(64)

    approx, detail = WaveletAnalyzer.dwt_step(signal)

    assert approx.shape == (32,)
    assert detail.shape == (32,)

    # Parseval energy conservation: sum(signal^2) == sum(approx^2) + sum(detail^2)
    orig_energy = float(np.sum(signal**2))
    dwt_energy = float(np.sum(approx**2) + np.sum(detail**2))
    assert math.isclose(orig_energy, dwt_energy, rel_tol=1e-9)


def test_dwt_step_periodic_wrap():
    """Verify periodic wrap padding does not drop or corrupt edge information."""
    from vietlott.model.wavelet_engine import WaveletAnalyzer

    # An impulse at the boundary
    signal = np.zeros(64)
    signal[0] = 1.0
    approx, detail = WaveletAnalyzer.dwt_step(signal)

    assert approx.shape == (32,)
    assert detail.shape == (32,)
    # Energy must still be conserved for boundary impulse
    assert math.isclose(float(np.sum(signal**2)), float(np.sum(approx**2) + np.sum(detail**2)), rel_tol=1e-9)


def test_decompose_signal_multilevel():
    """Verify Mallat multi-level decomposition shapes: A2 (16,), D1 (32,), D2 (16,)."""
    from vietlott.model.wavelet_engine import WaveletAnalyzer

    np.random.seed(2026)
    signal = np.random.randn(64)

    a2, details = WaveletAnalyzer.decompose_signal(signal, levels=2)

    # A2 should be shape (16,)
    assert a2.shape == (16,)
    # Details should contain [D1, D2]
    assert len(details) == 2
    d1, d2 = details
    assert d1.shape == (32,)
    assert d2.shape == (16,)

    # Total energy conservation across 2 levels: sum(signal^2) == sum(A2^2) + sum(D1^2) + sum(D2^2)
    orig_energy = float(np.sum(signal**2))
    decomp_energy = float(np.sum(a2**2) + np.sum(d1**2) + np.sum(d2**2))
    assert math.isclose(orig_energy, decomp_energy, rel_tol=1e-9)


def test_calculate_wavelet_spectral_scores_synthetic():
    """Verify calculate_wavelet_spectral_scores with synthetic draw records."""
    from vietlott.model.wavelet_engine import calculate_wavelet_spectral_scores

    max_val = 45
    num_balls = 6
    window_len = 64

    # Build 64 synthetic draws where:
    # Ball 7 appears frequently in recent draws (burst)
    # Ball 13 never appears
    # Ball 22 appears with steady spacing
    synthetic_records = []
    for i in range(window_len):
        draw = [1, 2, 3, 4, 5, 6]
        # Ball 7 appears in the last 6 draws
        if i >= window_len - 6:
            draw[0] = 7
        # Ball 22 appears every 8 draws
        if i % 8 == 0:
            draw[1] = 22
        synthetic_records.append({"draw_id": i + 1, "result": draw})

    scores = calculate_wavelet_spectral_scores(
        synthetic_records,
        max_val=max_val,
        num_balls=num_balls,
        window_len=window_len,
    )

    # 1. Output structure
    assert isinstance(scores, dict)
    assert len(scores) == max_val
    for b in range(1, max_val + 1):
        assert b in scores
        assert isinstance(scores[b], float)
        assert scores[b] >= 0.0
        assert not math.isnan(scores[b])
        assert not math.isinf(scores[b])
        # Values should be rounded to 3 decimal places
        assert scores[b] == round(scores[b], 3)

    # 2. Ball 13 never appeared -> score must be 0.0
    assert scores[13] == 0.0

    # 3. Ball 7 had a strong recent burst -> score must be positive and higher than quiet balls
    assert scores[7] > 0.0
    assert scores[7] > scores[13]


def test_calculate_wavelet_spectral_scores_empty_and_short():
    """Verify calculate_wavelet_spectral_scores handles empty or short history safely."""
    from vietlott.model.wavelet_engine import calculate_wavelet_spectral_scores

    # Empty records
    empty_scores = calculate_wavelet_spectral_scores([], max_val=35, num_balls=5)
    assert len(empty_scores) == 35
    assert all(score == 0.0 for score in empty_scores.values())

    # Very short history (< 4 draws)
    short_records = [
        {"draw_id": 1, "result": [1, 2, 3, 4, 5]},
        {"draw_id": 2, "result": [6, 7, 8, 9, 10]},
    ]
    short_scores = calculate_wavelet_spectral_scores(short_records, max_val=35, num_balls=5, window_len=64)
    assert len(short_scores) == 35
    assert all(score >= 0.0 for score in short_scores.values())


def test_calculate_wavelet_spectral_scores_with_real_data():
    """Verify calculate_wavelet_spectral_scores runs on actual Power 6/55 data."""
    import json
    from vietlott.model.wavelet_engine import calculate_wavelet_spectral_scores

    fpath = DATA_DIR / "power655.jsonl"
    if not fpath.exists():
        pytest.skip("power655.jsonl not found in data directory")

    records = []
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    assert len(records) >= 64

    scores = calculate_wavelet_spectral_scores(
        records,
        max_val=55,
        num_balls=6,
        window_len=64,
    )

    assert len(scores) == 55
    # Valid numeric scores, non-negative, at least some non-zero
    non_zeros = [s for s in scores.values() if s > 0.0]
    assert len(non_zeros) > 0
    for b, s in scores.items():
        assert 1 <= b <= 55
        assert isinstance(s, float)
        assert s >= 0.0
        assert not math.isnan(s)
        assert not math.isinf(s)
