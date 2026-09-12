# Real-time Prediction Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Xây dựng hệ thống sổ nhật ký lưu vết và đối soát dự đoán thời gian thực (Real-time Prediction Ledger) cho Power 6/55, Mega 6/45 và Power 5/35; tự động chấm điểm giải thưởng theo luật Vietlott khi cào kết quả mới và hiển thị trực quan bảng đối soát minh bạch trên Web GUI.

**Architecture:** Tách biệt rõ ràng tầng dữ liệu gốc (`data/prediction_ledger_{game}.jsonl`) với cơ chế Atomic Write; module tính toán `prediction_evaluator.py` tính giải thưởng chuẩn xác theo luật Vietlott; module điều phối `prediction_tracker.py` gắn hook 2 chiều vào crawler `sync_live_data.py` và pipeline xuất bản `render_web_data.py`; giao diện Web GUI (`docs/index.html`) tích hợp bảng đối soát tương tác với pill badges nổi bật.

**Tech Stack:** Python 3.11, Pytest, JSONL, Vanilla JS (ES6+), HTML5/CSS3.

**Spec:** `docs/superpowers/specs/2026-09-12-real-time-prediction-ledger-design.md`

## Global Constraints
- Tuyệt đối không dùng Mock data: 100% dữ liệu đối soát và P&L phải xuất phát từ thuật toán thật và kết quả cào thật.
- Không Look-Ahead Bias: Tại kỳ T, chỉ sử dụng dữ liệu từ kỳ T-1 trở về trước để dự đoán.
- Ghi file an toàn theo cơ chế Atomic Write (ghi tệp `.tmp` rồi rename).
- Tương thích 100% với dữ liệu hiện hữu và không xóa bất kỳ file nào của người dùng.

---

### Task 1: Bộ máy chấm điểm & tính giải thưởng chuẩn Vietlott (Prediction Evaluator)

**Files:**
- Create: `src/vietlott/model/prediction_evaluator.py`
- Test: `src/vietlott/tests/test_prediction_evaluator.py`

**Interfaces:**
- Produces: `evaluate_ticket(game_type: str, ticket_numbers: list[int], actual_result: list[int], special_ball: int | None = None) -> dict`
- Produces: `evaluate_bao7(game_type: str, septet_numbers: list[int], actual_result: list[int], special_ball: int | None = None) -> dict`
- Produces: `evaluate_banker_wheeling(game_type: str, banker_tickets: list[dict], actual_result: list[int], special_ball: int | None = None) -> dict`

- [x] **Step 1: Viết test kiểm thử các trường hợp trúng giải**

```python
# src/vietlott/tests/test_prediction_evaluator.py
import pytest
from vietlott.model.prediction_evaluator import (
    evaluate_ticket,
    evaluate_bao7,
    evaluate_banker_wheeling,
)

def test_power655_ticket_prizes():
    actual = [7, 24, 31, 43, 47, 54]
    special = 22
    # Trúng 3 số -> Giải Ba 50k
    res_3 = evaluate_ticket("power655", [7, 24, 31, 1, 2, 3], actual, special)
    assert res_3["hits"] == 3
    assert res_3["prize_vnd"] == 50000
    assert res_3["prize_tier"] == "Giải Ba"
    
    # Trúng 5 số + trúng đặc biệt -> Jackpot 2
    res_jp2 = evaluate_ticket("power655", [7, 24, 31, 43, 47, 22], actual, special)
    assert res_jp2["hits"] == 5
    assert res_jp2["is_special_hit"] is True
    assert res_jp2["prize_tier"] == "Jackpot 2"

def test_mega645_ticket_prizes():
    actual = [14, 18, 20, 21, 26, 27]
    res_4 = evaluate_ticket("power645", [14, 18, 20, 21, 1, 2], actual)
    assert res_4["hits"] == 4
    assert res_4["prize_vnd"] == 300000
    assert res_4["prize_tier"] == "Giải Nhì"

def test_bao7_evaluation():
    actual = [7, 24, 31, 43, 47, 54]
    # Bao 7 trúng 3 số -> Được hưởng 4 giải Ba
    res = evaluate_bao7("power655", [7, 24, 31, 1, 2, 3, 4], actual)
    assert res["hits"] == 3
    assert res["prize_vnd"] == 200000  # 4 * 50,000
    assert res["winning_combinations_count"] == 4
```

- [x] **Step 2: Chạy test để xác nhận test báo lỗi (RED)**

Run: `.venv\Scripts\pytest.exe src/vietlott/tests/test_prediction_evaluator.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'vietlott.model.prediction_evaluator'`

- [x] **Step 3: Triển khai mã nguồn `prediction_evaluator.py` (GREEN)**

```python
# src/vietlott/model/prediction_evaluator.py
import itertools
from typing import Any, Dict, List, Optional

PRIZE_TABLES = {
    "power655": {
        "cost_per_ticket": 10000,
        3: {"tier": "Giải Ba", "prize": 50000},
        4: {"tier": "Giải Nhì", "prize": 500000},
        5: {"tier": "Giải Nhất", "prize": 40000000},
        "jp2": {"tier": "Jackpot 2", "prize": 3000000000},
        6: {"tier": "Jackpot 1", "prize": 30000000000},
    },
    "power645": {
        "cost_per_ticket": 10000,
        3: {"tier": "Giải Ba", "prize": 30000},
        4: {"tier": "Giải Nhì", "prize": 300000},
        5: {"tier": "Giải Nhất", "prize": 10000000},
        6: {"tier": "Jackpot", "prize": 12000000000},
    },
    "power535": {
        "cost_per_ticket": 10000,
        # 5 bóng chính + 1 đặc biệt
    }
}

def evaluate_ticket(game_type: str, ticket_numbers: List[int], actual_result: List[int], special_ball: Optional[int] = None) -> Dict[str, Any]:
    actual_set = set(actual_result)
    matched = sorted(list(set(ticket_numbers) & actual_set))
    hits = len(matched)
    special_hit = bool(special_ball is not None and special_ball in ticket_numbers)
    
    prize_tier = "Không trúng"
    prize_vnd = 0
    
    if game_type == "power655":
        if hits == 6:
            prize_tier = "Jackpot 1"
            prize_vnd = 30000000000
        elif hits == 5 and special_hit:
            prize_tier = "Jackpot 2"
            prize_vnd = 3000000000
        elif hits == 5:
            prize_tier = "Giải Nhất"
            prize_vnd = 40000000
        elif hits == 4:
            prize_tier = "Giải Nhì"
            prize_vnd = 500000
        elif hits == 3:
            prize_tier = "Giải Ba"
            prize_vnd = 50000
    elif game_type == "power645":
        if hits == 6:
            prize_tier = "Jackpot"
            prize_vnd = 12000000000
        elif hits == 5:
            prize_tier = "Giải Nhất"
            prize_vnd = 10000000
        elif hits == 4:
            prize_tier = "Giải Nhì"
            prize_vnd = 300000
        elif hits == 3:
            prize_tier = "Giải Ba"
            prize_vnd = 30000
    elif game_type == "power535":
        if hits == 5 and special_hit:
            prize_tier = "Giải Nhất Đặc Biệt"
            prize_vnd = 1000000000
        elif hits == 5:
            prize_tier = "Giải Nhất"
            prize_vnd = 30000000
        elif hits == 4 and special_hit:
            prize_tier = "Giải Nhì Đặc Biệt"
            prize_vnd = 1500000
        elif hits == 4:
            prize_tier = "Giải Nhì"
            prize_vnd = 300000
        elif hits == 3 and special_hit:
            prize_tier = "Giải Ba Đặc Biệt"
            prize_vnd = 50000
        elif hits == 3:
            prize_tier = "Giải Ba"
            prize_vnd = 20000
        elif hits == 2 and special_hit:
            prize_tier = "Khuyến Khích"
            prize_vnd = 10000
            
    return {
        "numbers": ticket_numbers,
        "hits": hits,
        "matched_balls": matched,
        "is_special_hit": special_hit,
        "prize_tier": prize_tier,
        "prize_vnd": prize_vnd,
    }

def evaluate_bao7(game_type: str, septet_numbers: List[int], actual_result: List[int], special_ball: Optional[int] = None) -> Dict[str, Any]:
    # Tổ hợp 7 chọn 6 vé chuẩn
    sub_tickets = list(itertools.combinations(septet_numbers, 6))
    total_prize = 0
    winning_count = 0
    sub_results = []
    for sub in sub_tickets:
        res = evaluate_ticket(game_type, list(sub), actual_result, special_ball)
        if res["prize_vnd"] > 0:
            winning_count += 1
            total_prize += res["prize_vnd"]
        sub_results.append(res)
        
    matched = sorted(list(set(septet_numbers) & set(actual_result)))
    return {
        "numbers": septet_numbers,
        "hits": len(matched),
        "matched_balls": matched,
        "cost_vnd": 70000,
        "prize_vnd": total_prize,
        "winning_combinations_count": winning_count,
        "sub_tickets": sub_results,
    }

def evaluate_banker_wheeling(game_type: str, banker_tickets: List[Dict[str, Any]], actual_result: List[int], special_ball: Optional[int] = None) -> Dict[str, Any]:
    total_prize = 0
    best_hits = 0
    winning_tickets = 0
    evaluated_tickets = []
    for t in banker_tickets:
        nums = t.get("numbers", [])
        res = evaluate_ticket(game_type, nums, actual_result, special_ball)
        if res["hits"] > best_hits:
            best_hits = res["hits"]
        if res["prize_vnd"] > 0:
            winning_tickets += 1
            total_prize += res["prize_vnd"]
        evaluated_tickets.append(res)
        
    return {
        "tickets_count": len(banker_tickets),
        "cost_vnd": len(banker_tickets) * 10000,
        "best_hits": best_hits,
        "winning_tickets_count": winning_tickets,
        "total_prize_vnd": total_prize,
        "evaluated_tickets": evaluated_tickets,
    }
```

- [x] **Step 4: Chạy lại test để đảm bảo tất cả đều PASS**

Run: `.venv\Scripts\pytest.exe src/vietlott/tests/test_prediction_evaluator.py -v`  
Expected: `3 passed in 0.05s`

- [x] **Step 5: Git commit task 1**

```bash
git add src/vietlott/model/prediction_evaluator.py src/vietlott/tests/test_prediction_evaluator.py
git commit -m "feat(evaluator): add Vietlott prize evaluation engine with Bao 7 & wheeling support"
```

---

### Task 2: Bộ điều phối sổ nhật ký & Walk-Forward Seeding (Prediction Tracker)

**Files:**
- Create: `src/vietlott/prediction_tracker.py`
- Test: `src/vietlott/tests/test_prediction_tracker.py`

**Interfaces:**
- Consumes: `prediction_evaluator.py`
- Produces: `seed_historical_ledger(game_key: str, history_limit: int = 35) -> str`
- Produces: `verify_and_update_ledger(game_key: str, latest_draw: dict) -> dict`
- Produces: `snapshot_next_prediction(game_key: str, target_draw_id: str, predictions_data: dict) -> dict`
- Produces: `get_ledger_web_summary(game_key: str) -> dict`

- [x] **Step 1: Viết test cho `prediction_tracker.py`**

```python
# src/vietlott/tests/test_prediction_tracker.py
import json
from pathlib import Path
from vietlott.prediction_tracker import (
    save_ledger_record_atomic,
    load_ledger_records,
    verify_and_update_ledger,
)

def test_atomic_save_and_load(tmp_path):
    test_file = tmp_path / "test_ledger.jsonl"
    record = {"draw_id": "00001", "status": "pending", "predictions": {"golden_ticket": {"numbers": [1, 2, 3, 4, 5, 6]}}}
    save_ledger_record_atomic(test_file, record)
    
    records = load_ledger_records(test_file)
    assert len(records) == 1
    assert records[0]["draw_id"] == "00001"
    assert records[0]["status"] == "pending"
```

- [x] **Step 2: Chạy test để xác nhận test fails**

Run: `.venv\Scripts\pytest.exe src/vietlott/tests/test_prediction_tracker.py -v`  
Expected: FAIL with `ModuleNotFoundError`

- [x] **Step 3: Cài đặt logic lưu trữ atomic, đối soát tự động & walk-forward seeding trong `prediction_tracker.py`**

Triển khai các hàm:
- `get_ledger_path(game_key: str) -> Path`: Trả về `data/prediction_ledger_{game}.jsonl`
- `load_ledger_records(file_path: Path) -> List[Dict]`: Đọc toàn bộ các bản ghi
- `save_all_ledger_records_atomic(file_path: Path, records: List[Dict])`: Ghi atomic qua `.tmp`
- `verify_and_update_ledger(game_key: str, latest_draw: Dict) -> Optional[Dict]`: So khớp bản ghi pending với kết quả thật vừa về, tính P&L, đổi trạng thái thành `verified`.
- `snapshot_next_prediction(game_key: str, target_draw_id: str, predictions: Dict) -> Dict`: Niêm phong bộ vé kỳ tới.
- `seed_historical_ledger(game_key: str, count: int = 35) -> int`: Quét lùi 35 kỳ trong lịch sử, áp dụng mô hình tại kỳ T-1 để sinh bộ số cho kỳ T, đối soát với kết quả thật kỳ T, ghi thành các dòng `verified`.
- `get_ledger_web_summary(game_key: str) -> Dict`: Tính toán các chỉ số thống kê (Tỷ lệ trúng giải %, tổng tiền cược, tổng tiền trúng, ROI, chuỗi trúng liên tiếp).

- [x] **Step 4: Chạy lại test để đảm bảo PASS**

Run: `.venv\Scripts\pytest.exe src/vietlott/tests/test_prediction_tracker.py -v`  
Expected: PASS

- [x] **Step 5: Git commit task 2**

```bash
git add src/vietlott/prediction_tracker.py src/vietlott/tests/test_prediction_tracker.py
git commit -m "feat(tracker): implement atomic prediction ledger tracker and walk-forward seeding"
```

---

### Task 3: Tích hợp vào Pipeline Cào Dữ Liệu & Render Web

**Files:**
- Modify: `src/vietlott/sync_live_data.py`
- Modify: `src/vietlott/render_web_data.py`
- Test: `src/vietlott/tests/test_pipeline_ledger_integration.py`

**Interfaces:**
- `sync_live_data.py`: Gọi `verify_and_update_ledger()` ngay sau khi có kết quả mới
- `render_web_data.py`: Trích xuất `get_ledger_web_summary()` và nhúng vào `products[game]["prediction_ledger"]`

- [x] **Step 1: Viết test tích hợp pipeline**

```python
# src/vietlott/tests/test_pipeline_ledger_integration.py
from vietlott.prediction_tracker import get_ledger_web_summary, seed_historical_ledger

def test_ledger_summary_structure():
    summary = get_ledger_web_summary("power655")
    assert "total_tracked_draws" in summary
    assert "overall_win_rate_pct" in summary
    assert "history" in summary
```

- [x] **Step 2: Gắn hook trong `sync_live_data.py`**

Sau khi `sync_power(...)` hoặc `sync_power535(...)` phát hiện `new_draws > 0`, tự động gọi:
```python
from vietlott.prediction_tracker import verify_and_update_ledger
verify_and_update_ledger(game_key, latest_draw_dict)
```

- [x] **Step 3: Gắn hook trong `render_web_data.py`**

Trong hàm xuất bản dữ liệu từng game, bổ sung:
```python
from vietlott.prediction_tracker import get_ledger_web_summary, snapshot_next_prediction
# Cập nhật snapshot cho kỳ tiếp theo nếu chưa có
snapshot_next_prediction(game_key, next_target_id, calculated_tickets)
# Đưa tóm tắt đối soát vào JSON xuất bản
prod_dict["prediction_ledger"] = get_ledger_web_summary(game_key)
```

- [x] **Step 4: Chạy test tích hợp và kiểm tra tệp `docs/data/vietlott_summary.json`**

Run: `.venv\Scripts\python.exe -m pytest src/vietlott/tests/test_pipeline_ledger_integration.py -v`  
Expected: PASS

- [x] **Step 5: Git commit task 3**

```bash
git add src/vietlott/sync_live_data.py src/vietlott/render_web_data.py src/vietlott/tests/test_pipeline_ledger_integration.py
git commit -m "feat(pipeline): integrate prediction ledger hooks into live sync and web render"
```

---

### Task 4: Xây dựng Giao diện Web GUI Đối Soát Thực Tế

**Files:**
- Modify: `docs/index.html`
- Modify: `docs/assets/js/consensus_ensemble.js` hoặc `docs/assets/js/common_analytics.js`
- Modify: `docs/assets/css/styles.css`

- [x] **Step 1: Thêm Container Thẻ Card `#prediction-ledger-section` vào `docs/index.html`**

Bổ sung cấu trúc HTML responsive:
- Header: "📋 NHẬT KÝ ĐỐI SOÁT DỰ ĐOÁN THỰC TẾ (REAL-TIME PREDICTION LEDGER)"
- Khối Thống kê nhanh: KPI Cards (Tỷ lệ có giải %, ROI %, Tổng P&L, Chuỗi trúng liên tiếp, Kỳ đang chờ).
- Thanh chuyển Tab bộ lọc: *Tất cả các kỳ* | *Chỉ kỳ trúng giải* | *Vé Vàng* | *Bao 7* | *Banker Wheeling*.
- Bảng đối soát chi tiết từng kỳ: Có cột Kỳ/Ngày, Kết quả thật, Vé Vàng (với bóng trúng sáng viền vàng), Vé Bao 7 (bóng trúng sáng xanh), Dàn Banker, P&L ròng.

- [x] **Step 2: Thêm hàm render JavaScript trong `docs/assets/js/consensus_ensemble.js`**

Viết hàm `renderPredictionLedger(gameKey, ledgerData)`:
- Parse dữ liệu `ledgerData.history` và `ledgerData.current_pending_draw`.
- Sinh mã HTML cho từng quả bóng xổ số: nếu bóng nằm trong `matched_balls`, áp dụng class CSS `ball-hit-glow` với viền sáng rực rỡ và badge `✓ Trúng`.
- Hiển thị nhãn giải thưởng rõ ràng (ví dụ: `Giải Ba (+50.000đ)`).
- Xử lý sự kiện click filter chuyển đổi mượt mà.

- [x] **Step 3: Tinh chỉnh CSS trong `docs/assets/css/styles.css`**

Thêm các hiệu ứng visual:
- `.ball-hit-glow`: Box shadow vàng/xanh neon cho bóng trúng thưởng.
- `.pnl-positive`: Chữ xanh lá gradient hiển thị số tiền lời.
- `.pnl-negative`: Chữ đỏ/cam nhạt hiển thị số tiền vốn cược.
- `.badge-pending`: Badge hiệu ứng xung nhịp (pulse) cho kỳ sắp quay.

- [x] **Step 4: Kiểm tra hiển thị trực tiếp**

Kiểm tra DOM elements và cú pháp JS không có lỗi cú pháp.

- [x] **Step 5: Git commit task 4**

```bash
git add docs/index.html docs/assets/js/consensus_ensemble.js docs/assets/css/styles.css
git commit -m "feat(ui): add interactive prediction ledger verification table and KPI cards"
```

---

### Task 5: Chạy Khởi Tạo Lịch Sử 35 Kỳ (Seeding) & Kiểm Thử Toàn Diện (End-to-End)

**Files:**
- Execute: `src/vietlott/prediction_tracker.py` (Seeding cho 6/55, 6/45, 5/35)
- Execute: `src/vietlott/render_web_data.py` (Cập nhật `vietlott_summary.json`)
- Test: Toàn bộ test suite

- [x] **Step 1: Thực thi khởi tạo lịch sử 35 kỳ cho Power 6/55, Mega 6/45, Power 5/35**

Run: `.venv\Scripts\python.exe -c "from vietlott.prediction_tracker import seed_historical_ledger; [seed_historical_ledger(k, 35) for k in ['power655', 'power645', 'power535']]"`  
Expected: Sinh ra 3 tệp `data/prediction_ledger_power655.jsonl`, `power645.jsonl`, `power535.jsonl` đầy đủ 35 kỳ đối soát và 1 kỳ pending tiếp theo.

- [x] **Step 2: Chạy `render_web_data.py` để biên dịch toàn bộ dữ liệu ra web**

Run: `.venv\Scripts\python.exe src/vietlott/render_web_data.py`  
Expected: `docs/data/vietlott_summary.json` có trường `prediction_ledger` cho cả 3 sản phẩm.

- [x] **Step 3: Chạy toàn bộ test suite của dự án**

Run: `.venv\Scripts\pytest.exe src/vietlott/tests/ -v`  
Expected: Toàn bộ test đều PASS.

- [x] **Step 4: Kiểm tra file JSONL và file JSON web để xác nhận số liệu thực tế**

Run: `.venv\Scripts\python.exe -c "import json; d=json.load(open('docs/data/vietlott_summary.json', encoding='utf-8')); print([(k, d['products'][k].get('prediction_ledger', {}).get('total_tracked_draws')) for k in ['power_655', 'power_645', 'power_535']])"`  
Expected: Mỗi game đều ghi nhận $\ge 35$ kỳ đối soát.

- [x] **Step 5: Git commit hoàn thành tính năng**

```bash
git add data/prediction_ledger_*.jsonl docs/data/vietlott_summary.json
git commit -m "feat(ledger): complete out-of-sample prediction ledger initialization and web synchronization"
```
