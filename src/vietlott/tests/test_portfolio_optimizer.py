"""
Unit tests for Markowitz Portfolio Optimizer and Louvain Community Extraction.
File: src/vietlott/tests/test_portfolio_optimizer.py
"""

import pytest
import numpy as np
import random
from typing import List, Dict

from src.vietlott.model.portfolio_optimizer import (
    build_pairwise_covariance_proxy,
    extract_louvain_communities,
    optimize_markowitz_ticket,
)


def _generate_synthetic_draws(n_draws: int, max_val: int, num_balls: int, seed: int = 123) -> List[Dict]:
    """Helper to generate deterministic synthetic draw records."""
    rng = random.Random(seed)
    records = []
    for draw_id in range(1, n_draws + 1):
        combo = sorted(rng.sample(range(1, max_val + 1), num_balls))
        records.append({"draw_id": draw_id, "result": combo})
    return records


class TestPairwiseCovarianceProxy:
    def test_build_pairwise_covariance_proxy_symmetry_and_diagonal(self):
        records = _generate_synthetic_draws(n_draws=100, max_val=55, num_balls=6, seed=42)
        cov = build_pairwise_covariance_proxy(records, max_val=55, num_balls=6, window_len=100)

        assert isinstance(cov, np.ndarray)
        assert cov.shape == (55, 55)
        # Symmetry: Sigma_ij == Sigma_ji
        assert np.allclose(cov, cov.T, atol=1e-9)
        # Zero diagonal: Sigma_ii == 0.0
        assert np.allclose(np.diag(cov), 0.0, atol=1e-9)

    def test_build_pairwise_covariance_proxy_empty_records(self):
        cov = build_pairwise_covariance_proxy([], max_val=45, num_balls=6, window_len=150)
        assert isinstance(cov, np.ndarray)
        assert cov.shape == (45, 45)
        assert np.allclose(cov, cov.T, atol=1e-9)
        assert np.allclose(np.diag(cov), 0.0, atol=1e-9)

    def test_build_pairwise_covariance_proxy_lift_behavior(self):
        # Create records where balls 1 and 2 appear together frequently
        records = []
        for i in range(50):
            if i % 2 == 0:
                records.append({"result": [1, 2, 10, 11, 12, 13]})
            else:
                records.append({"result": [3, 4, 10, 11, 12, 13]})
        cov = build_pairwise_covariance_proxy(records, max_val=35, num_balls=6, window_len=50)

        # Ball 1 (idx 0) and Ball 2 (idx 1) appear together in all their appearances
        # Their lift should be > 1.0, so cov[0, 1] > 0
        assert cov[0, 1] > 0.0
        # Ball 1 (idx 0) and Ball 3 (idx 2) never appear together
        # Their lift should be < 1.0, so cov[0, 2] < 0
        assert cov[0, 2] < 0.0
        assert cov[0, 1] == pytest.approx(cov[1, 0])


class TestLouvainCommunityExtraction:
    def test_extract_louvain_communities_power655(self):
        records = _generate_synthetic_draws(n_draws=120, max_val=55, num_balls=6, seed=99)
        clusters = extract_louvain_communities(records, max_val=55, num_balls=6, window_len=120)

        assert isinstance(clusters, dict)
        # All balls 1..55 must be assigned
        assert set(clusters.keys()) == set(range(1, 56))

        unique_clusters = set(clusters.values())
        # Must produce 4 to 5 clusters
        assert 4 <= len(unique_clusters) <= 5
        # Each cluster ID must be in {0, 1, 2, 3, 4}
        assert unique_clusters.issubset({0, 1, 2, 3, 4})

    def test_extract_louvain_communities_mega645(self):
        records = _generate_synthetic_draws(n_draws=100, max_val=45, num_balls=6, seed=77)
        clusters = extract_louvain_communities(records, max_val=45, num_balls=6, window_len=100)

        assert set(clusters.keys()) == set(range(1, 46))
        unique_clusters = set(clusters.values())
        assert 4 <= len(unique_clusters) <= 5
        assert unique_clusters.issubset({0, 1, 2, 3, 4})

    def test_extract_louvain_communities_power535(self):
        records = _generate_synthetic_draws(n_draws=80, max_val=35, num_balls=5, seed=55)
        clusters = extract_louvain_communities(records, max_val=35, num_balls=5, window_len=80)

        assert set(clusters.keys()) == set(range(1, 36))
        unique_clusters = set(clusters.values())
        assert 4 <= len(unique_clusters) <= 5
        assert unique_clusters.issubset({0, 1, 2, 3, 4})

    def test_extract_louvain_communities_empty_fallback(self):
        clusters = extract_louvain_communities([], max_val=45, num_balls=6)
        assert set(clusters.keys()) == set(range(1, 46))
        assert 4 <= len(set(clusters.values())) <= 5


class TestOptimizeMarkowitzTicket:
    def test_optimize_markowitz_ticket_power655(self):
        records = _generate_synthetic_draws(n_draws=150, max_val=55, num_balls=6, seed=10)
        cov = build_pairwise_covariance_proxy(records, max_val=55, num_balls=6, window_len=150)
        clusters = extract_louvain_communities(records, max_val=55, num_balls=6, window_len=150)

        # Mock candidate scores favoring varied balls
        candidate_scores = {b: 2.0 + (b % 7) * 0.5 + (b % 5) * 0.3 for b in range(1, 56)}

        result = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=55,
            num_balls=6,
            target_sum=168,
            sum_range=(115, 220),
            min_ac=7,
            risk_lambda=0.30,
            seed=42,
        )

        assert isinstance(result, dict)
        numbers = result["numbers"]
        assert len(numbers) == 6
        assert sorted(numbers) == numbers
        assert len(set(numbers)) == 6
        assert all(1 <= b <= 55 for b in numbers)

        assert result["optimization_type"] == "Markowitz Constrained Portfolio"
        assert result["ac_index"] >= 7
        assert 115 <= result["sum"] <= 220

        # Louvain spread checks
        spread = result["louvain_spread"]
        assert spread["distinct_clusters_count"] >= 4
        # No cluster has > 2 balls
        assert max(spread["cluster_distribution"].values()) <= 2

        # Utility check
        assert result["expected_return"] > 0
        assert result["objective_utility"] == pytest.approx(
            result["expected_return"] - result["covariance_risk_penalty"], abs=1e-3
        )

    def test_optimize_markowitz_ticket_mega645(self):
        records = _generate_synthetic_draws(n_draws=120, max_val=45, num_balls=6, seed=20)
        cov = build_pairwise_covariance_proxy(records, max_val=45, num_balls=6, window_len=120)
        clusters = extract_louvain_communities(records, max_val=45, num_balls=6, window_len=120)

        candidate_scores = {b: 1.5 + (b % 6) * 0.4 for b in range(1, 46)}

        result = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=45,
            num_balls=6,
            target_sum=138,
            sum_range=(95, 180),
            min_ac=7,
            risk_lambda=0.30,
            seed=42,
        )

        numbers = result["numbers"]
        assert len(numbers) == 6
        assert sorted(numbers) == numbers
        assert result["ac_index"] >= 7
        assert 95 <= result["sum"] <= 180
        assert result["louvain_spread"]["distinct_clusters_count"] >= 4
        assert max(result["louvain_spread"]["cluster_distribution"].values()) <= 2

    def test_optimize_markowitz_ticket_power535(self):
        records = _generate_synthetic_draws(n_draws=100, max_val=35, num_balls=5, seed=30)
        cov = build_pairwise_covariance_proxy(records, max_val=35, num_balls=5, window_len=100)
        clusters = extract_louvain_communities(records, max_val=35, num_balls=5, window_len=100)

        candidate_scores = {b: 1.0 + (b % 5) * 0.5 for b in range(1, 36)}

        result = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=35,
            num_balls=5,
            target_sum=90,
            sum_range=(60, 120),
            min_ac=4,
            risk_lambda=0.30,
            seed=42,
        )

        numbers = result["numbers"]
        assert len(numbers) == 5
        assert sorted(numbers) == numbers
        assert result["ac_index"] >= 4
        assert 60 <= result["sum"] <= 120
        # Power 5/35 requires >= 3 clusters (or >= 4 if available), max 2 balls per cluster
        assert result["louvain_spread"]["distinct_clusters_count"] >= 3
        assert max(result["louvain_spread"]["cluster_distribution"].values()) <= 2

    def test_optimize_markowitz_ticket_determinism(self):
        records = _generate_synthetic_draws(n_draws=100, max_val=55, num_balls=6, seed=42)
        cov = build_pairwise_covariance_proxy(records, max_val=55, num_balls=6)
        clusters = extract_louvain_communities(records, max_val=55, num_balls=6)
        candidate_scores = {b: float(b % 11) for b in range(1, 56)}

        res1 = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=55,
            num_balls=6,
            target_sum=168,
            sum_range=(115, 220),
            min_ac=7,
            risk_lambda=0.30,
            seed=12345,
        )

        res2 = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=55,
            num_balls=6,
            target_sum=168,
            sum_range=(115, 220),
            min_ac=7,
            risk_lambda=0.30,
            seed=12345,
        )

        assert res1["numbers"] == res2["numbers"]
        assert res1["objective_utility"] == res2["objective_utility"]
        assert res1["expected_return"] == res2["expected_return"]
        assert res1["covariance_risk_penalty"] == res2["covariance_risk_penalty"]

    def test_optimize_markowitz_risk_penalty_sensitivity(self):
        # Setup covariance matrix with heavy penalty between balls 1 and 2
        cov = np.zeros((45, 45), dtype=float)
        cov[0, 1] = 5.0  # Balls 1 and 2
        cov[1, 0] = 5.0

        clusters = {b: (b - 1) % 5 for b in range(1, 46)}
        # Give ball 1 and ball 2 slightly higher score, but heavy covariance penalty
        candidate_scores = {b: 2.0 for b in range(1, 46)}
        candidate_scores[1] = 2.5
        candidate_scores[2] = 2.5

        # With risk_lambda = 0.0, both 1 and 2 might be chosen
        res_no_risk = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=45,
            num_balls=6,
            target_sum=138,
            sum_range=(95, 180),
            min_ac=7,
            risk_lambda=0.0,
            seed=42,
        )

        # With risk_lambda = 1.0, heavy penalty should discourage having both 1 and 2 together
        res_high_risk = optimize_markowitz_ticket(
            candidate_scores=candidate_scores,
            cov_matrix=cov,
            louvain_clusters=clusters,
            max_val=45,
            num_balls=6,
            target_sum=138,
            sum_range=(95, 180),
            min_ac=7,
            risk_lambda=1.0,
            seed=42,
        )

        assert not (1 in res_high_risk["numbers"] and 2 in res_high_risk["numbers"])

