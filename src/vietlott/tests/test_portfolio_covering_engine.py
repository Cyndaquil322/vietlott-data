import pytest
from vietlott.model.portfolio_covering_engine import (
    filter_negative_space,
    generate_portfolio_50k,
)

def test_negative_space_filter_eliminates_bad_combos():
    # Vé toàn chẵn (0 lẻ) -> bị loại
    bad_even = (2, 4, 6, 8, 10, 12)
    # Vé toàn lẻ (6 lẻ) -> bị loại
    bad_odd = (1, 3, 5, 7, 9, 11)
    # Vé chuẩn cân bằng
    good_combo = (5, 11, 24, 31, 47, 54)
    
    filtered = filter_negative_space([bad_even, bad_odd, good_combo], max_val=55, num_balls=6)
    assert good_combo in filtered
    assert bad_even not in filtered
    assert bad_odd not in filtered

def test_generate_portfolio_50k_structure():
    core = [5, 11, 24, 31, 47, 54, 1, 8, 16, 22, 39, 44]
    scores = {b: 1.0 / (idx + 1) for idx, b in enumerate(core)}
    
    res = generate_portfolio_50k(core, scores, max_val=55, num_balls=6, num_tickets=5, seed=1398)
    assert res["total_tickets"] == 5
    assert res["total_cost_vnd"] == 50000
    assert len(res["tickets"]) == 5
    assert res["pairs_coverage_pct"] > 50.0
    for t in res["tickets"]:
        assert len(t["numbers"]) == 6
        assert t["ac"] >= 6
