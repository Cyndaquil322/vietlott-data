import pytest
from pathlib import Path
from vietlott.prediction_tracker import get_ledger_web_summary, seed_historical_ledger

def test_ledger_summary_structure():
    summary = get_ledger_web_summary("power655")
    assert "total_tracked_draws" in summary
    assert "overall_win_rate_pct" in summary
    assert "history" in summary
    assert summary["total_tracked_draws"] >= 35

def test_ledger_summary_power645_and_power535():
    s645 = get_ledger_web_summary("power645")
    assert s645["total_tracked_draws"] >= 35
    s535 = get_ledger_web_summary("power535")
    assert s535["total_tracked_draws"] >= 35
