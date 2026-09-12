import pytest
from pathlib import Path
from vietlott.model.backtest_cache import (
    load_backtest_cache,
    save_backtest_cache_atomic,
    get_cached_or_compute_walk_forward,
)

def test_cache_save_and_load(tmp_path):
    cache = load_backtest_cache("power655", cache_dir=tmp_path)
    assert cache["records"] == {}
    
    cache["records"]["01397"] = {"hits": 3, "prize": 50000}
    save_backtest_cache_atomic("power655", cache, cache_dir=tmp_path)
    
    loaded = load_backtest_cache("power655", cache_dir=tmp_path)
    assert "01397" in loaded["records"]
    assert loaded["records"]["01397"]["hits"] == 3

def test_incremental_computation_skips_existing(tmp_path):
    call_counts = {"count": 0}
    def mock_compute(missing_records):
        call_counts["count"] += len(missing_records)
        return [{"draw_id": r["id"], "hits": 2} for r in missing_records]

    records = [{"id": "00001", "result": [1, 2, 3, 4, 5, 6]}, {"id": "00002", "result": [7, 8, 9, 10, 11, 12]}]
    res1 = get_cached_or_compute_walk_forward("power655", records, mock_compute, num_draws=2, cache_dir=tmp_path)
    assert call_counts["count"] == 2
    assert len(res1) == 2

    # Lần 2 với cùng dữ liệu: hoàn toàn đọc từ cache, không gọi compute
    call_counts["count"] = 0
    res2 = get_cached_or_compute_walk_forward("power655", records, mock_compute, num_draws=2, cache_dir=tmp_path)
    assert call_counts["count"] == 0
    assert len(res2) == 2
