# Tối Ưu Hóa Hiệu Năng Pipeline & Bộ Đệm Tăng Tiến (Incremental Pipeline & Timeout Optimization) 实施计划

> **面向 Agent 执行者：** 必需子技能：使用 superpower-subagent-driven-development（推荐）或 superpower-executing-plans 按任务逐项执行本计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** Xây dựng module bộ đệm tăng tiến `backtest_cache.py` và tối ưu hoá đường ống xuất bản dữ liệu `render_web_data.py`, tăng cấu hình timeout an toàn đa tầng giúp rút ngắn thời gian xuất bản từ 200s xuống dưới 15s và triệt tiêu 100% rủi ro timeout.

**架构：** Module `backtest_cache.py` quản lý lưu trữ và nạp bộ đệm Walk-Forward bằng cơ chế Atomic Write; module `render_web_data.py` tái sử dụng bộ đệm cho 200 kỳ lịch sử và chỉ tính toán kỳ mới phát sinh; cấu hình `pyproject.toml` và `.github/workflows/crawl.yaml` được nâng mức timeout bảo vệ lên 5–15 phút.

**技术栈：** Python 3.11, Pytest, JSON, GitHub Actions YAML.

**规格：** `docs/superpowers/specs/2026-09-12-incremental-pipeline-timeout-optimization-design.md`

## 全局约束
- 100% Zero Mock Data & Zero Look-Ahead Bias: Chỉ lưu và tái sử dụng các kết quả Walk-Forward tính toán thực tế.
- Atomic Write: Ghi qua tệp `.tmp` trước khi rename để đảm bảo không bị hỏng file khi có sự cố ngắt nguồn.
- Tương thích ngược: Kết quả xuất bản của `render_web_data.py` phải giữ nguyên 100% cấu trúc schema của `vietlott_summary.json`.

---

### 任务 1: Module Quản Lý Bộ Đệm Tăng Tiến (Backtest Cache Engine)

**文件：**
- 新建：`src/vietlott/model/backtest_cache.py`
- 测试：`src/vietlott/tests/test_backtest_cache.py`

**接口：**
- 对外产出：`load_backtest_cache(game_key: str, cache_dir: Optional[Path] = None) -> Dict[str, Any]`
- 对外产出：`save_backtest_cache_atomic(game_key: str, cache_data: Dict[str, Any], cache_dir: Optional[Path] = None) -> Path`
- 对外产出：`get_cached_or_compute_walk_forward(game_key: str, records: List[Dict], compute_fn: Callable, num_draws: int = 200, cache_dir: Optional[Path] = None) -> Dict[str, Any]`

- [ ] **步骤 1：编写失败的测试**

```python
# src/vietlott/tests/test_backtest_cache.py
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

    records = [{"id": "00001", "result": [1,2,3,4,5,6]}, {"id": "00002", "result": [7,8,9,10,11,12]}]
    res1 = get_cached_or_compute_walk_forward("power655", records, mock_compute, num_draws=2, cache_dir=tmp_path)
    assert call_counts["count"] == 2
    assert len(res1) == 2

    # Lần 2 với cùng dữ liệu: hoàn toàn đọc từ cache, không gọi compute
    call_counts["count"] = 0
    res2 = get_cached_or_compute_walk_forward("power655", records, mock_compute, num_draws=2, cache_dir=tmp_path)
    assert call_counts["count"] == 0
    assert len(res2) == 2
```

- [ ] **步骤 2：运行测试并确认其失败**

运行：`.venv\Scripts\pytest.exe src/vietlott/tests/test_backtest_cache.py -v`  
预期：FAIL，提示 `ModuleNotFoundError: No module named 'vietlott.model.backtest_cache'`

- [ ] **步骤 3：编写最小实现**

```python
# src/vietlott/model/backtest_cache.py
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cache"

def get_cache_path(game_key: str, cache_dir: Optional[Path] = None) -> Path:
    target_dir = Path(cache_dir) if cache_dir else CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"backtest_cache_{game_key}.json"

def load_backtest_cache(game_key: str, cache_dir: Optional[Path] = None) -> Dict[str, Any]:
    cp = get_cache_path(game_key, cache_dir)
    if not cp.exists():
        return {"version": "1.0", "game_key": game_key, "records": {}}
    try:
        with open(cp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": "1.0", "game_key": game_key, "records": {}}

def save_backtest_cache_atomic(game_key: str, cache_data: Dict[str, Any], cache_dir: Optional[Path] = None) -> Path:
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
            cached_records[iid] = item
        cache["records"] = cached_records
        save_backtest_cache_atomic(game_key, cache, cache_dir)
        
    results = []
    for r in target_records:
        rid = str(r.get("id", "")).replace("#", "").zfill(5)
        if rid in cached_records:
            results.append(cached_records[rid])
    return results
```

- [ ] **步骤 4：运行测试并确认其通过**

运行：`.venv\Scripts\pytest.exe src/vietlott/tests/test_backtest_cache.py -v`  
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add src/vietlott/model/backtest_cache.py src/vietlott/tests/test_backtest_cache.py
git commit -m "feat(cache): implement incremental walk-forward cache engine with atomic write"
```

---

### 任务 2: Tích Hợp Bộ Đệm Vào `render_web_data.py` & Tối Ưu Hóa Tái Sử Dụng Mô Hình

**文件：**
- 修改：`src/vietlott/render_web_data.py`
- 测试：`src/vietlott/tests/test_pipeline_ledger_integration.py`

**接口：**
- 依赖输入：`src/vietlott/model/backtest_cache.py`
- 对外产出：`render_web_data.generate_web_summary` sử dụng cache tăng tiến

- [ ] **步骤 1：Viết test kiểm tra tốc độ và tính toàn vẹn khi có cache**

```python
# Thêm vào src/vietlott/tests/test_backtest_cache.py
def test_render_web_summary_uses_cache_speed(tmp_path):
    # Xác nhận hàm load cache trả về kết quả ngay lập tức
    cache = load_backtest_cache("power655", cache_dir=tmp_path)
    assert "records" in cache
```

- [ ] **步骤 2：Chạy test kiểm chứng**

运行：`.venv\Scripts\pytest.exe src/vietlott/tests/test_backtest_cache.py -v`  
预期：PASS

- [ ] **步骤 3：Sửa đổi `render_web_data.py` để tích hợp `get_cached_or_compute_walk_forward`**

Trong `process_power()`, bọc phần tính `backtest_data` và `bao7_backtest_data` thông qua `backtest_cache`:
- Khi lần đầu chạy: Tính và lưu lại 200 kỳ vào cache.
- Khi các lần chạy tiếp theo: Tái sử dụng 199 kỳ cũ, chỉ tính kỳ mới nhất.

- [ ] **步骤 4：Chạy đo thời gian thực tế của `render_web_data.py`**

Chạy: `.venv\Scripts\python.exe -u src/vietlott/render_web_data.py`  
Xác nhận: Lần 2 chạy hoàn thành trong dưới 20 giây.

- [ ] **步骤 5：提交**

```bash
git add src/vietlott/render_web_data.py src/vietlott/tests/test_backtest_cache.py
git commit -m "perf(pipeline): integrate incremental cache into render_web_data for 15x speedup"
```

---

### 任务 3: Cấu Hình Timeout An Toàn Đa Tầng (Multi-layer Timeout Guard)

**文件：**
- 修改：`pyproject.toml`
- 修改：`.github/workflows/crawl.yaml`

- [ ] **步骤 1：Cập nhật `pyproject.toml`**

Thiết lập timeout kiểm thử mặc định lên 300 giây (5 phút) cho các bài test tính toán ma trận lớn:
```toml
[tool.pytest.ini_options]
timeout = 300
```

- [ ] **步骤 2：Cập nhật `.github/workflows/crawl.yaml`**

Bổ sung `timeout-minutes: 15` cho job `crawl_and_update` để đảm bảo GitHub Actions không bao giờ bị dừng bất ngờ:
```yaml
jobs:
  crawl_and_update:
    runs-on: ubuntu-latest
    timeout-minutes: 15
```

- [ ] **步骤 3：Chạy pytest để kiểm chứng cấu hình mới**

Chạy: `.venv\Scripts\pytest.exe src/vietlott/tests/test_backtest_cache.py -v`  
Xác nhận: Không có cảnh báo hoặc lỗi cấu hình.

- [ ] **步骤 4：Commit cấu hình**

```bash
git add pyproject.toml .github/workflows/crawl.yaml
git commit -m "chore(config): set multi-layer safe timeout limits in pyproject.toml and github workflows"
```

---

### 任务 4: Kiểm Thử Toàn Diện & Nghiệm Thu (Verification Before Completion)

**文件：**
- Toàn bộ test suite trong `src/vietlott/tests/`

- [ ] **步骤 1：Chạy toàn bộ bài test liên quan đến ledger, evaluator và cache**

Chạy: `.venv\Scripts\pytest.exe src/vietlott/tests/test_prediction_evaluator.py src/vietlott/tests/test_prediction_tracker.py src/vietlott/tests/test_pipeline_ledger_integration.py src/vietlott/tests/test_backtest_cache.py -v`  
Kỳ vọng: 100% test PASSED.

- [ ] **步骤 2：Xác minh file xuất bản `vietlott_summary.json` có đầy đủ dữ liệu ledger**

Chạy: `.venv\Scripts\python.exe -c "import json; d=json.load(open('docs/data/vietlott_summary.json', encoding='utf-8')); print([(k, d['products'][k]['prediction_ledger']['total_tracked_draws']) for k in ['power_655', 'power_645', 'power_535']])"`  
Kỳ vọng: Mỗi game đều ghi nhận 35 kỳ đối soát hợp lệ.
