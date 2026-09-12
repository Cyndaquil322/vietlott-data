"""
Unit tests for Real-time Prediction Ledger and Walk-Forward Seeding.
Module: vietlott.prediction_tracker
"""

import json
from pathlib import Path
import pytest

from vietlott.prediction_tracker import (
    get_ledger_path,
    load_ledger_records,
    save_ledger_record_atomic,
    save_all_ledger_records_atomic,
    snapshot_next_prediction,
    verify_and_update_ledger,
    get_ledger_web_summary,
    seed_historical_ledger,
    normalize_game_key,
)


def test_normalize_and_get_ledger_path(tmp_path):
    assert normalize_game_key("power655") == "power655"
    assert normalize_game_key("power_655") == "power655"
    assert normalize_game_key("power645") == "power645"
    assert normalize_game_key("power_535") == "power535"

    path_655 = get_ledger_path("power_655", data_dir=tmp_path)
    assert path_655 == tmp_path / "prediction_ledger_power655.jsonl"

    path_645 = get_ledger_path("mega645", data_dir=tmp_path)
    assert path_645 == tmp_path / "prediction_ledger_power645.jsonl"


def test_atomic_save_and_load(tmp_path):
    test_file = tmp_path / "test_ledger.jsonl"

    # Loading non-existent file returns empty list
    assert load_ledger_records(test_file) == []

    record1 = {
        "draw_id": "01397",
        "draw_date": "2026-09-12",
        "target_draw_id": "01397",
        "status": "pending",
        "predictions": {
            "golden_ticket": {"numbers": [1, 2, 3, 4, 5, 6], "cost_vnd": 10000},
        },
    }

    # Save single record
    save_ledger_record_atomic(test_file, record1)
    records = load_ledger_records(test_file)
    assert len(records) == 1
    assert records[0]["draw_id"] == "01397"
    assert records[0]["status"] == "pending"

    # Temporary file must not remain
    tmp_candidates = list(tmp_path.glob("*.tmp"))
    assert len(tmp_candidates) == 0

    # Save second record
    record2 = {
        "draw_id": "01398",
        "draw_date": "2026-09-15",
        "target_draw_id": "01398",
        "status": "pending",
        "predictions": {
            "golden_ticket": {"numbers": [7, 8, 9, 10, 11, 12], "cost_vnd": 10000},
        },
    }
    save_ledger_record_atomic(test_file, record2)
    records = load_ledger_records(test_file)
    assert len(records) == 2
    assert records[1]["draw_id"] == "01398"

    # Update existing record1 to verified
    record1_updated = dict(record1)
    record1_updated["status"] = "verified"
    save_ledger_record_atomic(test_file, record1_updated)
    records = load_ledger_records(test_file)
    assert len(records) == 2
    assert records[0]["status"] == "verified"

    # Save all atomically
    record3 = {"draw_id": "01399", "status": "pending"}
    save_all_ledger_records_atomic(test_file, [record1_updated, record2, record3])
    records = load_ledger_records(test_file)
    assert len(records) == 3
    assert records[2]["draw_id"] == "01399"


def test_snapshot_next_prediction(tmp_path):
    game_key = "power655"
    target_id = "01400"
    predictions = {
        "golden_ticket": {
            "numbers": [7, 24, 31, 43, 47, 54],
            "cost_vnd": 10000,
        },
        "septet_bao7": {
            "numbers": [7, 24, 31, 43, 47, 54, 22],
            "cost_vnd": 70000,
        },
        "banker_wheeling": {
            "banker": 7,
            "tickets": [
                [7, 24, 31, 43, 47, 54],
                [7, 1, 2, 3, 4, 5],
            ],
            "tickets_count": 2,
            "cost_vnd": 20000,
        },
        "core_pool": {
            "numbers": [1, 2, 7, 22, 24, 31, 43, 47, 54, 55],
        },
    }

    rec = snapshot_next_prediction(
        game_key=game_key,
        target_draw_id=target_id,
        predictions_data=predictions,
        draw_date="2026-09-15",
        data_dir=tmp_path,
    )

    assert rec["draw_id"] == "01400"
    assert rec["status"] == "pending"
    assert "predictions" in rec
    assert rec["predictions"]["golden_ticket"]["numbers"] == [7, 24, 31, 43, 47, 54]
    assert rec["summary_metrics"]["total_investment_vnd"] == 100000
    assert rec["summary_metrics"]["total_return_vnd"] == 0

    # Snapshot again for same draw_id should not duplicate
    rec2 = snapshot_next_prediction(
        game_key=game_key,
        target_draw_id=target_id,
        predictions_data=predictions,
        data_dir=tmp_path,
    )
    ledger_file = get_ledger_path(game_key, data_dir=tmp_path)
    all_recs = load_ledger_records(ledger_file)
    assert len(all_recs) == 1


def test_verify_and_update_ledger(tmp_path):
    game_key = "power655"
    target_id = "01401"
    predictions = {
        "golden_ticket": {
            "numbers": [7, 24, 31, 10, 20, 30],  # 3 matching balls
            "cost_vnd": 10000,
        },
        "septet_bao7": {
            "numbers": [7, 24, 31, 10, 20, 30, 40],  # 3 matching balls -> 4 Giải Ba = 200k
            "cost_vnd": 70000,
        },
        "banker_wheeling": {
            "banker": 7,
            "tickets": [
                {"numbers": [7, 24, 31, 1, 2, 3]},  # 3 hits -> 50k
                {"numbers": [7, 1, 2, 3, 4, 5]},     # 1 hit -> 0
            ],
            "tickets_count": 2,
            "cost_vnd": 20000,
        },
        "core_pool": {
            "numbers": [7, 24, 31, 43, 1, 2, 3, 4, 5, 6],  # 4 matching balls
        },
    }

    # Snapshot pending
    snapshot_next_prediction(
        game_key=game_key,
        target_draw_id=target_id,
        predictions_data=predictions,
        draw_date="2026-09-17",
        data_dir=tmp_path,
    )

    # Actual draw result: [7, 24, 31, 43, 47, 54] + special 22
    latest_draw = {
        "id": target_id,
        "date": "2026-09-17",
        "result": [7, 24, 31, 43, 47, 54, 22],
    }

    updated = verify_and_update_ledger(game_key, latest_draw, data_dir=tmp_path)
    assert updated is not None
    assert updated["status"] == "verified"
    assert updated["verified_at"] is not None
    assert updated["actual_result"] == [7, 24, 31, 43, 47, 54]
    assert updated["special_ball"] == 22

    # Verify Golden Ticket evaluation: 3 hits -> 50,000 VNĐ
    gt = updated["predictions"]["golden_ticket"]
    assert gt["hits"] == 3
    assert gt["matched_balls"] == [7, 24, 31]
    assert gt["prize_vnd"] == 50000
    assert gt["prize_tier"] == "Giải Ba"

    # Verify Bao 7 evaluation: 3 hits -> 200,000 VNĐ
    bao7 = updated["predictions"]["septet_bao7"]
    assert bao7["hits"] == 3
    assert bao7["matched_balls"] == [7, 24, 31]
    assert bao7["prize_vnd"] == 200000
    assert bao7["winning_combinations_count"] == 4

    # Verify Banker Wheeling evaluation: best_hits=3, total_prize_vnd=50000
    bw = updated["predictions"]["banker_wheeling"]
    assert bw["best_hits"] == 3
    assert bw["winning_tickets_count"] == 1
    assert bw["total_prize_vnd"] == 50000

    # Verify Core Pool: 4 hits
    core = updated["predictions"]["core_pool"]
    assert core["hits"] == 4
    assert core["matched_balls"] == [7, 24, 31, 43]

    # Verify Summary metrics:
    # Total investment: 10k + 70k + 20k = 100,000 VNĐ
    # Total return: 50k + 200k + 50k = 300,000 VNĐ
    # Net profit: 200,000 VNĐ
    # ROI: 200.0%
    sm = updated["summary_metrics"]
    assert sm["total_investment_vnd"] == 100000
    assert sm["total_return_vnd"] == 300000
    assert sm["net_profit_vnd"] == 200000
    assert sm["roi_pct"] == 200.0
    assert sm["has_winning_prize"] is True


def test_get_ledger_web_summary(tmp_path):
    game_key = "power655"
    summary_empty = get_ledger_web_summary(game_key, data_dir=tmp_path)
    assert summary_empty["total_tracked_draws"] == 0
    assert summary_empty["overall_win_rate_pct"] == 0.0
    assert summary_empty["current_pending_draw"] is None
    assert summary_empty["history"] == []

    # Populate 2 verified draws and 1 pending draw
    rec1 = {
        "draw_id": "01390",
        "draw_date": "2026-09-01",
        "target_draw_id": "01390",
        "status": "verified",
        "actual_result": [1, 2, 3, 4, 5, 6],
        "special_ball": 10,
        "predictions": {
            "golden_ticket": {"hits": 3, "prize_vnd": 50000, "cost_vnd": 10000},
            "septet_bao7": {"hits": 3, "prize_vnd": 200000, "cost_vnd": 70000},
            "banker_wheeling": {"cost_vnd": 60000, "total_prize_vnd": 0},
            "core_pool": {"hits": 4},
        },
        "summary_metrics": {
            "total_investment_vnd": 140000,
            "total_return_vnd": 250000,
            "net_profit_vnd": 110000,
            "roi_pct": 78.57,
            "has_winning_prize": True,
        },
    }

    rec2 = {
        "draw_id": "01391",
        "draw_date": "2026-09-03",
        "target_draw_id": "01391",
        "status": "verified",
        "actual_result": [10, 20, 30, 40, 50, 55],
        "special_ball": 12,
        "predictions": {
            "golden_ticket": {"hits": 1, "prize_vnd": 0, "cost_vnd": 10000},
            "septet_bao7": {"hits": 2, "prize_vnd": 0, "cost_vnd": 70000},
            "banker_wheeling": {"cost_vnd": 60000, "total_prize_vnd": 0},
            "core_pool": {"hits": 2},
        },
        "summary_metrics": {
            "total_investment_vnd": 140000,
            "total_return_vnd": 0,
            "net_profit_vnd": -140000,
            "roi_pct": -100.0,
            "has_winning_prize": False,
        },
    }

    rec3 = {
        "draw_id": "01392",
        "draw_date": "2026-09-05",
        "target_draw_id": "01392",
        "status": "pending",
        "predictions": {
            "golden_ticket": {"numbers": [1, 5, 10, 15, 20, 25], "cost_vnd": 10000},
        },
        "summary_metrics": {
            "total_investment_vnd": 140000,
            "total_return_vnd": 0,
            "net_profit_vnd": 0,
            "roi_pct": 0.0,
            "has_winning_prize": False,
        },
    }

    ledger_file = get_ledger_path(game_key, data_dir=tmp_path)
    save_all_ledger_records_atomic(ledger_file, [rec1, rec2, rec3])

    summary = get_ledger_web_summary(game_key, data_dir=tmp_path)
    assert summary["total_tracked_draws"] == 2
    assert summary["overall_win_rate_pct"] == 50.0  # 1 win out of 2 verified draws
    assert summary["golden_ticket_avg_hits"] == 2.0  # (3 + 1) / 2
    assert summary["septet_avg_hits"] == 2.5        # (3 + 2) / 2

    pnl = summary["cumulative_pnl"]
    assert pnl["total_spent"] == 280000
    assert pnl["total_won"] == 250000
    assert pnl["net_profit"] == -30000
    assert pnl["roi_pct"] == round((-30000 / 280000) * 100, 2)

    assert summary["current_pending_draw"] is not None
    assert summary["current_pending_draw"]["draw_id"] == "01392"
    assert len(summary["history"]) == 2
    # Reverse chronological order
    assert summary["history"][0]["draw_id"] == "01391"
    assert summary["history"][1]["draw_id"] == "01390"


def test_seed_historical_ledger_empty_or_small(tmp_path):
    # Non-existent raw data file returns 0
    res = seed_historical_ledger("power655", count=10, data_dir=tmp_path)
    assert res == 0

    # Less than 15 records returns 0
    raw_file = tmp_path / "power655.jsonl"
    with open(raw_file, "w", encoding="utf-8") as f:
        for i in range(5):
            f.write(json.dumps({"id": str(i + 1), "result": [1, 2, 3, 4, 5, 6, 7]}) + "\n")

    res_small = seed_historical_ledger("power655", count=10, data_dir=tmp_path)
    assert res_small == 0


def test_seed_historical_ledger_with_mocked_engine(monkeypatch, tmp_path):
    # Prepare dummy raw records (>= 15 records)
    raw_file = tmp_path / "power655.jsonl"
    with open(raw_file, "w", encoding="utf-8") as f:
        for i in range(20):
            f.write(json.dumps({
                "id": str(i + 1).zfill(5),
                "date": f"2026-08-{i+1:02d}",
                "result": [1, 2, 3, 4, 5, 6, 7],
            }) + "\n")

    # Mock calculate_multi_model_consensus_and_backtest to test deterministic seeding pipeline
    mock_res = {
        "next_draw_id": "#00021",
        "tickets": {
            "golden": {"numbers": [1, 2, 3, 4, 5, 6]},
            "bao7": {"numbers": [1, 2, 3, 4, 5, 6, 7]},
            "banker_wheeling": {
                "banker": 1,
                "tickets": [[1, 2, 3, 4, 5, 6]],
                "tickets_count": 1,
                "cost_vnd": 10000,
            },
            "core_pool": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        },
        "history_walk_forward": [
            {
                "drawId": "00019",
                "date": "2026-08-19",
                "actual": [1, 2, 3, 4, 5, 6],
                "predicted": [1, 2, 3, 10, 11, 12],
                "optimalSeptet": {"numbers": [1, 2, 3, 10, 11, 12, 13]},
                "corePool": [1, 2, 3, 10, 11, 12, 13, 14, 15, 16],
                "triad": [1, 2, 3],
            },
            {
                "drawId": "00020",
                "date": "2026-08-20",
                "actual": [1, 2, 3, 4, 5, 6],
                "predicted": [1, 2, 3, 4, 5, 6],
                "optimalSeptet": {"numbers": [1, 2, 3, 4, 5, 6, 7]},
                "corePool": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "triad": [1, 2, 3],
            },
        ],
    }

    import vietlott.model.ensemble_engine as ee
    monkeypatch.setattr(ee, "calculate_multi_model_consensus_and_backtest", lambda *args, **kwargs: mock_res)

    seeded_count = seed_historical_ledger("power655", count=2, data_dir=tmp_path)
    assert seeded_count == 2

    # Check ledger contents
    ledger_path = get_ledger_path("power655", data_dir=tmp_path)
    records = load_ledger_records(ledger_path)
    assert len(records) == 3  # 2 verified + 1 pending

    # 2 verified records
    assert records[0]["draw_id"] == "00019"
    assert records[0]["status"] == "verified"
    assert records[0]["predictions"]["golden_ticket"]["hits"] == 3
    assert records[0]["predictions"]["golden_ticket"]["prize_vnd"] == 50000

    assert records[1]["draw_id"] == "00020"
    assert records[1]["status"] == "verified"
    assert records[1]["predictions"]["golden_ticket"]["hits"] == 6
    assert records[1]["predictions"]["golden_ticket"]["prize_vnd"] == 30_000_000_000

    # 1 pending record for #00021
    assert records[2]["draw_id"] == "00021"
    assert records[2]["status"] == "pending"
    assert records[2]["summary_metrics"]["has_winning_prize"] is False

