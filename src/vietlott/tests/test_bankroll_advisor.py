"""Unit tests for Bankroll Advisor (Kelly Consensus Conviction Score - CCS).

Validates:
1. CCS score strictly in range [0.0, 100.0%].
2. Accurate 3-tier classification (Tier 1, Tier 2, Tier 3).
3. Exact recommended budgets (10k, 20k, 60k).
4. Edge cases: empty transition analytics, flat scores, missing models.
5. 100% determinism.
"""

import pytest
from vietlott.model.bankroll_advisor import calculate_consensus_conviction_score


def _create_mock_models_info():
    return {
        "markov": {"name": "Markov PPMI"},
        "hazard": {"name": "Hazard Gauss"},
        "decay": {"name": "Exponential Decay"},
        "bac_nho": {"name": "Bạc Nhớ Bayes"},
        "fourier": {"name": "Fourier Spectral"},
        "graph_pagerank": {"name": "Graph PageRank"},
        "state_space": {"name": "Kalman State Space"},
        "ml_ranker": {"name": "HistGradientBoosting"},
    }


def test_ccs_bounds():
    """Kiểm tra điểm CCS và các điểm thành phần luôn nằm trong khoảng [0.0, 100.0%]."""
    models_info = _create_mock_models_info()
    top_candidates = {m: list(range(1, 13)) for m in models_info}
    consensus_scores = {b: float(b) for b in range(1, 56)}
    transition_analytics = {
        "top_pull_rules": [
            {"from_ball": 1, "to_ball": 2, "z_score": 3.5},
            {"from_ball": 3, "to_ball": 4, "z_score": 2.8},
        ]
    }

    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    assert 0.0 <= res["ccs_score"] <= 100.0
    bd = res["breakdown"]
    assert 0.0 <= bd["agreement_score"] <= 100.0
    assert 0.0 <= bd["entropy_score"] <= 100.0
    assert 0.0 <= bd["pull_score"] <= 100.0


def test_tier_3_classification():
    """Kiểm tra phân loại Cấp 3: Super-Convergence (CCS >= 75.0%)."""
    models_info = _create_mock_models_info()
    # 8/8 models agree on balls 1..12
    top_candidates = {m: list(range(1, 13)) for m in models_info}
    # Steep consensus scores on top 12 (top ball has very high score)
    consensus_scores = {b: 0.1 for b in range(1, 56)}
    for idx, b in enumerate(range(1, 13)):
        consensus_scores[b] = 10.0 - idx * 0.5  # steep descent
    consensus_scores[1] = 25.0

    # Strong pull rules: sum Z >= 15.0 -> pull score = 100.0
    transition_analytics = {
        "top_pull_rules": [
            {"from_ball": 1, "to_ball": 2, "z_score": 4.5},
            {"from_ball": 3, "to_ball": 4, "z_score": 4.0},
            {"from_ball": 5, "to_ball": 6, "z_score": 3.8},
            {"from_ball": 7, "to_ball": 8, "z_score": 3.2},
        ]
    }

    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    assert res["ccs_score"] >= 75.0
    assert res["tier_level"] == 3
    assert res["tier_name"] == "Điểm Rơi Vàng (Super-Convergence)"
    assert res["tier_badge"] == "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
    assert res["recommended_action"] == "Kích hoạt Dàn Bọc Lót 6 Vé C(v, k, 3)"
    assert res["recommended_budget"] == 60000
    assert "Đồng thuận hội tụ cực mạnh giữa các mô hình (>= 6/8)" in res["rationale"]


def test_tier_2_classification():
    """Kiểm tra phân loại Cấp 2: Moderate Convergence (55.0 <= CCS < 75.0%)."""
    models_info = _create_mock_models_info()
    # 5/8 models agree on balls 1..12
    model_keys = list(models_info.keys())
    top_candidates = {}
    for idx, m in enumerate(model_keys):
        if idx < 5:
            top_candidates[m] = list(range(1, 13))
        else:
            top_candidates[m] = list(range(20, 32))

    # Moderate scores
    consensus_scores = {b: 1.0 for b in range(1, 56)}
    for b in range(1, 13):
        consensus_scores[b] = 5.0 + (13 - b) * 0.3

    # Moderate pull rules: sum Z around 10.5 -> pull score 70%
    transition_analytics = {
        "top_pull_rules": [
            {"from_ball": 1, "to_ball": 2, "z_score": 3.5},
            {"from_ball": 3, "to_ball": 4, "z_score": 3.5},
            {"from_ball": 5, "to_ball": 6, "z_score": 3.5},
        ]
    }

    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    assert 55.0 <= res["ccs_score"] < 75.0
    assert res["tier_level"] == 2
    assert res["tier_name"] == "Tín Hiệu Khả Quan (Moderate Convergence)"
    assert res["tier_badge"] == "bg-sky-500/20 text-sky-300 border-sky-500/40"
    assert res["recommended_action"] == "Đánh Vé Golden Markowitz + Kiềng 3 Chân Triad"
    assert res["recommended_budget"] == 20000
    assert "Đa số mô hình hội tụ tốt." in res["rationale"]


def test_tier_1_classification():
    """Kiểm tra phân loại Cấp 1: High Noise / Low Conviction (CCS < 55.0%)."""
    models_info = _create_mock_models_info()
    # Models have disjoint picks (very low agreement)
    model_keys = list(models_info.keys())
    top_candidates = {}
    for idx, m in enumerate(model_keys):
        start = idx * 6 + 1
        top_candidates[m] = list(range(start, start + 6))

    # Flat scores
    consensus_scores = {b: 1.0 for b in range(1, 56)}

    # Empty pull rules
    transition_analytics = {"top_pull_rules": []}

    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    assert res["ccs_score"] < 55.0
    assert res["tier_level"] == 1
    assert res["tier_name"] == "Tín Hiệu Phân Tán (High Noise / Low Conviction)"
    assert res["tier_badge"] == "bg-slate-800 text-slate-300 border-slate-700"
    assert res["recommended_action"] == "Thăm dò nhẹ 1 vé đơn hoặc tạm dừng"
    assert res["recommended_budget"] == 10000
    assert "Các mô hình phân hóa mạnh" in res["rationale"]


def test_recommended_budget_values():
    """Kiểm tra giá trị ngân sách đề xuất chính xác là 10k, 20k, 60k theo cấp độ."""
    models_info = _create_mock_models_info()

    # Tier 1 case
    t1_res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model={m: [] for m in models_info},
        consensus_scores={b: 1.0 for b in range(1, 56)},
        transition_analytics={},
        num_balls=6,
    )
    assert t1_res["recommended_budget"] == 10000

    # Tier 3 case
    t3_res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model={m: list(range(1, 13)) for m in models_info},
        consensus_scores={b: (50.0 if b == 1 else 0.1) for b in range(1, 56)},
        transition_analytics={"top_pull_rules": [{"z_score": 16.0}]},
        num_balls=6,
    )
    assert t3_res["recommended_budget"] == 60000


def test_edge_cases_empty_transition_and_flat_scores():
    """Kiểm tra xử lý ca biên: transition_analytics rỗng, điểm số phẳng, danh sách rỗng."""
    models_info = {}
    top_candidates = {}
    # Flat consensus scores for 12 balls
    consensus_scores = {b: 3.0 for b in range(1, 13)}
    transition_analytics = {}

    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    # When scores are flat, H = ln(12), so entropy_score should be 0.0
    # agreement_score is 0.0 because no models are present
    # pull_score is 0.0 because transition_analytics is empty
    assert res["ccs_score"] == 0.0
    assert res["breakdown"]["agreement_score"] == 0.0
    assert res["breakdown"]["entropy_score"] == 0.0
    assert res["breakdown"]["pull_score"] == 0.0
    assert res["tier_level"] == 1
    assert res["recommended_budget"] == 10000


def test_determinism_100_percent():
    """Kiểm tra tính tất định 100%: 2 lần chạy cùng input ra kết quả giống hệt nhau."""
    models_info = _create_mock_models_info()
    top_candidates = {m: list(range(1, 13)) for m in models_info}
    consensus_scores = {b: float(b % 7) for b in range(1, 56)}
    transition_analytics = {
        "top_pull_rules": [
            {"from_ball": 5, "to_ball": 12, "z_score": 2.7},
            {"from_ball": 10, "to_ball": 18, "z_score": 3.1},
        ]
    }

    res1 = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )
    res2 = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model=top_candidates,
        consensus_scores=consensus_scores,
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    assert res1 == res2


def test_output_schema_and_types():
    """Kiểm tra cấu trúc và kiểu dữ liệu của dictionary trả về."""
    models_info = _create_mock_models_info()
    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model={m: list(range(1, 13)) for m in models_info},
        consensus_scores={b: 1.0 for b in range(1, 36)},
        transition_analytics={},
        num_balls=5,
    )

    expected_keys = {
        "ccs_score",
        "tier_level",
        "tier_name",
        "tier_badge",
        "recommended_action",
        "recommended_budget",
        "breakdown",
        "rationale",
    }
    assert set(res.keys()) == expected_keys
    assert isinstance(res["ccs_score"], float)
    assert isinstance(res["tier_level"], int)
    assert isinstance(res["tier_name"], str)
    assert isinstance(res["tier_badge"], str)
    assert isinstance(res["recommended_action"], str)
    assert isinstance(res["recommended_budget"], int)
    assert isinstance(res["breakdown"], dict)
    assert isinstance(res["rationale"], str)

    expected_bd_keys = {"agreement_score", "entropy_score", "pull_score"}
    assert set(res["breakdown"].keys()) == expected_bd_keys
    for k, v in res["breakdown"].items():
        assert isinstance(v, float)


def test_negative_z_scores_and_extreme_values():
    """Kiểm tra xử lý các giá trị Z-score âm và cực trị."""
    models_info = _create_mock_models_info()
    transition_analytics = {
        "top_pull_rules": [
            {"from_ball": 1, "to_ball": 2, "z_score": -3.5},
            {"from_ball": 3, "to_ball": 4, "z_score": -1.2},
            {"from_ball": 5, "to_ball": 6, "z_score": 50.0},  # Extreme positive
        ]
    }
    res = calculate_consensus_conviction_score(
        models_info=models_info,
        top_candidates_per_model={m: [] for m in models_info},
        consensus_scores={b: 1.0 for b in range(1, 46)},
        transition_analytics=transition_analytics,
        num_balls=6,
    )

    # Negative Z-scores must be ignored via max(0, Z), extreme positive capped at 100.0
    assert res["breakdown"]["pull_score"] == 100.0


def test_empty_inputs_graceful():
    """Kiểm tra khi toàn bộ inputs rỗng không bị lỗi Exception và trả về Tier 1 an toàn."""
    res = calculate_consensus_conviction_score(
        models_info={},
        top_candidates_per_model={},
        consensus_scores={},
        transition_analytics={},
        num_balls=6,
    )
    assert res["ccs_score"] == 0.0
    assert res["tier_level"] == 1
    assert res["recommended_budget"] == 10000

