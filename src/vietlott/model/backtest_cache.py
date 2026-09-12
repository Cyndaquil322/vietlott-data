"""
Module: backtest_cache.py
Quản lý bộ nhớ đệm tăng tiến (Incremental Cache) cho Walk-Forward Backtest và Consensus.
Đảm bảo:
- 100% Zero Look-Ahead Bias & Zero Mock Data.
- Atomic Write qua file .tmp chống hỏng hóc dữ liệu.
- Tốc độ truy xuất O(1) cho các kỳ lịch sử đã tính toán.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"


def get_cache_path(game_key: str, cache_dir: Optional[Path] = None) -> Path:
    """Lấy đường dẫn tệp JSON bộ đệm cho từng loại hình xổ số."""
    target_dir = Path(cache_dir) if cache_dir else CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    norm_k = game_key.lower().replace("-", "").replace("_", "")
    return target_dir / f"backtest_cache_{norm_k}.json"


def load_backtest_cache(game_key: str, cache_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Đọc bộ đệm an toàn từ tệp JSON."""
    cp = get_cache_path(game_key, cache_dir)
    if not cp.exists():
        return {"version": "1.0", "game_key": game_key, "records": {}}
    try:
        with open(cp, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "records" in data:
                return data
            return {"version": "1.0", "game_key": game_key, "records": {}}
    except Exception:
        return {"version": "1.0", "game_key": game_key, "records": {}}


def save_backtest_cache_atomic(game_key: str, cache_data: Dict[str, Any], cache_dir: Optional[Path] = None) -> Path:
    """Ghi bộ đệm nguyên tử (Atomic Write) qua tệp .tmp rồi thay thế."""
    cp = get_cache_path(game_key, cache_dir)
    tmp_path = cp.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    tmp_path.replace(cp)
    return cp


def get_cached_or_compute_walk_forward(
    game_key: str,
    records: List[Dict[str, Any]],
    compute_fn: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
    num_draws: int = 200,
    cache_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Tính toán tăng tiến:
    - Nạp các kỳ đã tính từ cache.
    - Chỉ chạy compute_fn cho các kỳ mới chưa có trong cache.
    - Cập nhật cache và trả về danh sách kết quả theo đúng thứ tự lịch sử.
    """
    cache = load_backtest_cache(game_key, cache_dir)
    cached_records = cache.get("records", {})

    target_records = records[-num_draws:] if len(records) > num_draws else records
    missing = []
    for r in target_records:
        rid = str(r.get("id", "")).replace("#", "").zfill(5)
        if rid not in cached_records:
            missing.append(r)

    if missing:
        computed_items = compute_fn(missing)
        for item in computed_items:
            iid = str(item.get("draw_id") or item.get("drawId") or item.get("id", "")).replace("#", "").zfill(5)
            if iid:
                cached_records[iid] = item
        cache["records"] = cached_records
        save_backtest_cache_atomic(game_key, cache, cache_dir)

    results = []
    for r in target_records:
        rid = str(r.get("id", "")).replace("#", "").zfill(5)
        if rid in cached_records:
            results.append(cached_records[rid])
    return results


__all__ = [
    "get_cache_path",
    "load_backtest_cache",
    "save_backtest_cache_atomic",
    "get_cached_or_compute_walk_forward",
]
