"""
Analytic Engines Module for Vietlott Analytics:
Contains 7 independent mathematical models implemented purely with NumPy and standard library:
1. Bayesian Hazard Rhythm Z-Score (Nhịp gan Gauss Z-score)
2. Exponential Momentum & Time Decay (Động lượng suy giảm mũ)
3. Markov Transition Chain with Laplace Smoothing and PPMI (Xích Markov PPMI)
4. Hybrid Daubechies Wavelet & Hann Fourier Spectral Resonance (Phổ sóng lai)
5. Empirical Bayes Pairwise Lift (Bạc nhớ cặp đôi co cụm Bayes)
6. Graph Co-occurrence PageRank Centrality (Mạng đồ thị liên kết PageRank)
7. Bayesian Dynamic State-Space Filter (Bộ lọc trạng thái Kalman 1D)

Zero mock data. Pure NumPy determinism.
"""

from collections import Counter, defaultdict
import itertools
import math
from typing import Any, Dict, List

import numpy as np

try:
    from vietlott.model.wavelet_engine import calculate_wavelet_spectral_scores
except ImportError:
    try:
        from src.vietlott.model.wavelet_engine import calculate_wavelet_spectral_scores
    except ImportError:
        calculate_wavelet_spectral_scores = None


def calculate_bayesian_hazard_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    1. Bayesian Hazard Rate:
    Calculates Gaussian Z-Score density around the expected cycle gap:
    z = (gap - 1.05 * avg_gap) / max(1.0, std_gap)
    H(z) = 3.0 * exp(-0.5 * z^2) * (0.35 if z > 2.5 else 1.0)
    """
    if max_val <= 0:
        return {}

    K = min(120, len(sub_records))
    recent = sub_records[-K:]
    take_n = 5 if is_two_matrix else num_balls

    cur_gap = {b: K for b in range(1, max_val + 1)}
    gaps_history = {b: [] for b in range(1, max_val + 1)}
    prev_seen = {}

    for t, r in enumerate(reversed(recent)):
        res = r.get("result", [])
        main_b = res[:take_n]
        for b in main_b:
            if 1 <= b <= max_val:
                if b not in prev_seen:
                    cur_gap[b] = t
                    prev_seen[b] = t
                else:
                    gaps_history[b].append(t - prev_seen[b])
                    prev_seen[b] = t

    hazard_scores: Dict[int, float] = {}
    for b in range(1, max_val + 1):
        c_gap = cur_gap[b]
        all_g = gaps_history[b]
        avg_g = (sum(all_g) / len(all_g)) if all_g else (max_val / num_balls)
        std_g = float(np.std(all_g)) if len(all_g) >= 2 else (avg_g * 0.75)
        z = (c_gap - 1.05 * avg_g) / max(1.0, std_g)
        density = math.exp(-0.5 * (z ** 2))
        if z > 2.5:
            density *= 0.35
        hazard_scores[b] = round(density * 3.0, 3)

    return hazard_scores


def calculate_exponential_decay_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    alpha: float = 0.035,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    2. Exponential Time Decay:
    Weights recent appearances exponentially: w(t) = exp(-alpha * t)
    """
    if max_val <= 0:
        return {}

    K = min(120, len(sub_records))
    recent = sub_records[-K:]
    take_n = 5 if is_two_matrix else num_balls
    decay_freq = {b: 0.0 for b in range(1, max_val + 1)}

    for t, r in enumerate(reversed(recent)):
        res = r.get("result", [])
        main_b = res[:take_n]
        for b in main_b:
            if 1 <= b <= max_val:
                decay_freq[b] += math.exp(-alpha * t)

    return {b: round(decay_freq[b], 3) for b in range(1, max_val + 1)}


def calculate_markov_ppmi_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    3. Markov Transition Chain with Laplace Smoothing and Positive Pointwise Mutual Information (PPMI).
    """
    if max_val <= 0:
        return {}

    sub_len = min(150, len(sub_records))
    sub_recs = sub_records[-sub_len:]
    take_n = 5 if is_two_matrix else num_balls

    matrix = defaultdict(Counter)
    p_marginal = Counter()
    c_marginal = Counter()

    for t in range(1, len(sub_recs)):
        p_nums = set(sub_recs[t - 1].get("result", [])[:take_n])
        c_nums = set(sub_recs[t].get("result", [])[:take_n])
        for p in p_nums:
            p_marginal[p] += 1
            for c in c_nums:
                matrix[p][c] += 1
        for c in c_nums:
            c_marginal[c] += 1

    total_trans = sum(p_marginal.values()) or 1.0

    markov_score = {b: 0.0 for b in range(1, max_val + 1)}
    last_res = sub_records[-1].get("result", [])[:take_n] if sub_records else []

    for n in last_res:
        p_cnt = p_marginal[n]
        if p_cnt >= 2:
            for b in range(1, max_val + 1):
                cnt = matrix[n][b]
                p_joint = (cnt + 0.1) / (total_trans + 0.1 * max_val)
                p_p = p_marginal[n] / total_trans
                p_c = c_marginal[b] / total_trans
                pmi = math.log2(p_joint / (p_p * p_c)) if (p_p * p_c > 0) else 0.0
                if pmi > 0:
                    markov_score[b] += pmi

    return {b: round(markov_score[b], 3) for b in range(1, max_val + 1)}


def calculate_hybrid_spectral_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    window_len: int = 64,
) -> Dict[int, float]:
    """
    4. Hybrid Spectral Resonance:
    Combines Daubechies 4 Discrete Wavelet Transform (65%) and Hann-windowed Fourier FFT (35%).
    Score = 0.65 * S_wavelet + 0.35 * S_fourier
    """
    if max_val <= 0:
        return {}

    fft_len = min(window_len, len(sub_records))
    fft_records = sub_records[-fft_len:]
    spectral_score = {b: 0.0 for b in range(1, max_val + 1)}

    cur_gap = {b: fft_len for b in range(1, max_val + 1)}
    for t, r in enumerate(reversed(fft_records)):
        for b in r.get("result", [])[:num_balls]:
            if 1 <= b <= max_val and cur_gap[b] == fft_len:
                cur_gap[b] = t

    if fft_len >= 16:
        hann_win = np.hanning(fft_len)
        for b in range(1, max_val + 1):
            sig = [1.0 if b in r.get("result", [])[:num_balls] else 0.0 for r in fft_records]
            if sum(sig) > 0:
                sig_arr = np.array(sig, dtype=float)
                w_sig = (sig_arr - sig_arr.mean()) * hann_win
                fft_vals = np.abs(np.fft.rfft(w_sig))
                if len(fft_vals) > 1:
                    dom_freq = int(np.argmax(fft_vals[1:])) + 1
                    period = fft_len / dom_freq
                    gap_to_period = abs(cur_gap[b] - period)
                    spectral_score[b] = round(math.exp(-0.25 * gap_to_period), 3)

    if calculate_wavelet_spectral_scores is not None:
        wavelet_scores = calculate_wavelet_spectral_scores(
            sub_records, max_val, num_balls, window_len=fft_len
        )
    else:
        wavelet_scores = {b: 0.0 for b in range(1, max_val + 1)}

    hybrid_spectral = {
        b: round(0.65 * wavelet_scores.get(b, 0.0) + 0.35 * spectral_score.get(b, 0.0), 3)
        for b in range(1, max_val + 1)
    }
    return hybrid_spectral


def calculate_empirical_bayes_lift_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    5. Empirical Bayes Pairwise Lift:
    Calculates pairwise synergy from the previous draw pulling future balls with shrinkage (alpha=3.0).
    """
    if max_val <= 0:
        return {}

    p120 = sub_records[-120:] if len(sub_records) >= 120 else sub_records
    take_n = 5 if is_two_matrix else num_balls

    pair_trans = Counter()
    pair_counts = Counter()
    for i in range(len(p120) - 1):
        pr = p120[i].get("result", [])[:take_n]
        cr = p120[i + 1].get("result", [])[:take_n]
        for p in itertools.combinations(sorted(pr), 2):
            pair_counts[p] += 1
            for cb in cr:
                pair_trans[(p, cb)] += 1

    bac_nho_score = {b: 0.0 for b in range(1, max_val + 1)}
    base_prob = num_balls / max_val
    alpha_prior = 3.0
    last_res = sub_records[-1].get("result", [])[:take_n] if sub_records else []
    last_draw_pairs = list(itertools.combinations(sorted(set(last_res)), 2))

    for p in last_draw_pairs:
        p_cnt = pair_counts[p]
        if p_cnt >= 2:
            for b in range(1, max_val + 1):
                cnt = pair_trans.get((p, b), 0)
                if cnt > 0:
                    smooth_prob = (cnt + alpha_prior * base_prob) / (p_cnt + alpha_prior)
                    smooth_lift = smooth_prob / base_prob
                    if smooth_lift > 1.15:
                        bac_nho_score[b] += (smooth_lift - 1.0)

    return {b: round(bac_nho_score[b], 3) for b in range(1, max_val + 1)}


def calculate_graph_pagerank_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    damping: float = 0.85,
    max_iter: int = 50,
    window_len: int = 100,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    6. Graph Co-occurrence PageRank Centrality:
    Constructs an adjacency matrix A_{N x N} over window_len recent draws:
    Lift*(i, j) = ((C(i, j) + alpha * P0) / (C(i) + alpha)) * (1 / P0)
    A_ij = max(0.0, Lift*(i, j) - 1.0) for i != j, A_ii = 0
    Row-normalizes to stochastic transition matrix M, then runs Power Iteration with damping factor d.
    Score_graph(b) = round((p(b) / max_i p(i)) * 3.0, 3)
    """
    N = max_val
    if N <= 0:
        return {}

    take_n = 5 if is_two_matrix else num_balls
    recent = sub_records[-window_len:] if window_len > 0 else sub_records

    C_pair = np.zeros((N, N), dtype=float)
    C_single = np.zeros(N, dtype=float)

    for r in recent:
        balls = sorted(set(b for b in r.get("result", [])[:take_n] if 1 <= b <= N))
        for b in balls:
            C_single[b - 1] += 1.0
        for b1, b2 in itertools.combinations(balls, 2):
            C_pair[b1 - 1, b2 - 1] += 1.0
            C_pair[b2 - 1, b1 - 1] += 1.0

    alpha = 1.0
    P0 = num_balls / max_val
    A = np.zeros((N, N), dtype=float)

    for i in range(N):
        denom = C_single[i] + alpha
        for j in range(N):
            if i == j:
                A[i, j] = 0.0
            else:
                lift = ((C_pair[i, j] + alpha * P0) / denom) * (1.0 / P0)
                A[i, j] = max(0.0, lift - 1.0)

    # Normalize transition matrix M
    row_sums = A.sum(axis=1)
    M = np.zeros((N, N), dtype=float)
    for i in range(N):
        if row_sums[i] > 1e-12:
            M[i, :] = A[i, :] / row_sums[i]
        else:
            M[i, :] = 1.0 / N

    # Power Iteration: p^(t+1) = d * M^T p^(t) + ((1 - d) / N) * 1
    p = np.full(N, 1.0 / N, dtype=float)
    MT = M.T
    for _ in range(max_iter):
        p_next = damping * (MT @ p) + (1.0 - damping) / N
        if np.sum(np.abs(p_next - p)) < 1e-6:
            p = p_next
            break
        p = p_next

    max_p = float(np.max(p))
    scores: Dict[int, float] = {}
    for b in range(1, N + 1):
        val = (p[b - 1] / max_p * 3.0) if max_p > 0.0 else 0.0
        scores[b] = round(float(val), 3)

    return scores


def calculate_state_space_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    decay: float = 0.92,
    window_len: int = 80,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    7. Bayesian Dynamic State-Space Filter (1D Kalman Filter per ball):
    Tracks ball appearance velocity and latent probability:
    x_hat_t = lambda * x_{t-1} + (1 - lambda) * mu0
    P_t^- = lambda^2 * P_{t-1} + Q
    K_t = P_t^- / (P_t^- + R)
    x_t = x_hat_t + K_t * (y_t - x_hat_t)
    P_t = (1 - K_t) * P_t^-
    Prediction for T+1: x_hat_{T+1}(b) = lambda * x_T(b) + (1 - lambda) * mu0
    Score_state(b) = round(((x_hat_{T+1}(b) - min_i) / (max_i - min_i + eps)) * 3.0, 3)
    """
    N = max_val
    if N <= 0:
        return {}

    take_n = 5 if is_two_matrix else num_balls
    recent = sub_records[-window_len:] if window_len > 0 else sub_records

    lam = decay
    mu0 = num_balls / max_val
    Q = 0.05
    R = 0.5

    x = np.full(N, mu0, dtype=float)
    P = np.ones(N, dtype=float)

    for r in recent:
        draw_balls = set(b for b in r.get("result", [])[:take_n] if 1 <= b <= N)
        y = np.zeros(N, dtype=float)
        for b in draw_balls:
            y[b - 1] = 1.0

        x_hat = lam * x + (1.0 - lam) * mu0
        P_minus = (lam ** 2) * P + Q
        K = P_minus / (P_minus + R)
        x = x_hat + K * (y - x_hat)
        P = (1.0 - K) * P_minus

    x_pred = lam * x + (1.0 - lam) * mu0
    min_x = float(np.min(x_pred))
    max_x = float(np.max(x_pred))
    eps = 1e-9

    scores: Dict[int, float] = {}
    for b in range(1, N + 1):
        diff = max_x - min_x
        if diff > 1e-9:
            val = ((x_pred[b - 1] - min_x) / (diff + eps)) * 3.0
        else:
            val = 0.0
        scores[b] = round(float(val), 3)

    return scores


def evaluate_all_models(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    opt_alpha: float = 0.035,
    is_two_matrix: bool = False,
) -> Dict[str, Any]:
    """
    Evaluates all 7 independent analytic models and current gaps for all balls:
    Returns {
        "hazard": ...,
        "decay": ...,
        "markov": ...,
        "fourier": ...,
        "bac_nho": ...,
        "graph_pagerank": ...,
        "state_space": ...,
        "cur_gap": ...
    }
    """
    if max_val <= 0:
        return {}

    K = min(120, len(sub_records))
    cur_gap = {b: K for b in range(1, max_val + 1)}
    take_n = 5 if is_two_matrix else num_balls

    for t, r in enumerate(reversed(sub_records[-K:])):
        res = r.get("result", [])
        for b in res[:take_n]:
            if 1 <= b <= max_val and cur_gap[b] == K:
                cur_gap[b] = t

    hazard = calculate_bayesian_hazard_scores(sub_records, max_val, num_balls, is_two_matrix=is_two_matrix)
    decay = calculate_exponential_decay_scores(sub_records, max_val, num_balls, alpha=opt_alpha, is_two_matrix=is_two_matrix)
    markov = calculate_markov_ppmi_scores(sub_records, max_val, num_balls, is_two_matrix=is_two_matrix)
    fourier = calculate_hybrid_spectral_scores(sub_records, max_val, num_balls)
    bac_nho = calculate_empirical_bayes_lift_scores(sub_records, max_val, num_balls, is_two_matrix=is_two_matrix)
    graph_pagerank = calculate_graph_pagerank_scores(sub_records, max_val, num_balls, is_two_matrix=is_two_matrix)
    state_space = calculate_state_space_scores(sub_records, max_val, num_balls, is_two_matrix=is_two_matrix)

    return {
        "hazard": hazard,
        "decay": decay,
        "markov": markov,
        "fourier": fourier,
        "bac_nho": bac_nho,
        "graph_pagerank": graph_pagerank,
        "state_space": state_space,
        "cur_gap": cur_gap,
    }
