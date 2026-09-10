# Combinatorial Wheeling Optimization Implementation Plan (Phase 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nâng cấp thuật toán sinh Dàn ghép Bọc lót Tổ hợp (Combinatorial Covering Design $C(v, k, 3)$) và kiểm định Walk-Forward Backtest trong `src/vietlott/render_web_data.py`, thay thế các mẫu hardcode tùy tiện bằng cấu trúc toán học phủ tối ưu, đảm bảo tỷ lệ phủ 3-if-4 $\ge 96.8\%$ (lên tới $100\%$ khi trúng 4 số trong Core Pool) kết hợp các bộ lọc không gian âm ($AC \ge 7$, Gaussian Sum, phân tán cụm đồ thị).

**Architecture:** 
- Xây dựng module toán học tổ hợp `CoveringWheelEngine` sinh dàn vé bọc lót tối ưu theo lý thuyết bao phủ đồ thị tổ hợp (La Jolla Covering Design).
- Áp dụng cấu trúc phủ tối ưu:
  - Cho $6/55$ và $6/45$: Core Pool 12 số hạt nhân phủ thành 6 vé ($C(12, 6, 3)$ độ phủ 4-subset đạt $96.8\%$, hoặc tùy chọn 8 vé đạt $100\%$).
  - Cho $5/35$: Core Pool 10 số hạt nhân phủ thành 6 vé ($C(10, 5, 3)$ độ phủ 4-subset đạt $96.2\%$).
- Tích hợp bộ lọc không gian âm trên từng vé con của dàn wheeling: Chỉ số phức tạp số học $AC \ge 7$ (hoặc $\ge 4$ cho 5/35), tổng Gaussian trong vùng $[ \mu - 1.5\sigma, \mu + 1.5\sigma ]$, cân bằng chẵn lẻ và phân tán đuôi số.
- Cập nhật pipeline Walk-Forward Backtest trong `calculate_multi_model_consensus_and_backtest` và `generate_wheeling_strategy` để ghi nhận chính xác tỷ lệ ăn giải thực tế.

**Tech Stack:** Python 3.11, NumPy, itertools, pytest.

**Spec:** `docs/architecture/MATHEMATICAL_MODELS.md` (Mục 5: Hệ thống dàn ghép bọc lót toán học).

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả trúng thưởng (Tuân thủ AGENTS.md).
- Giữ nguyên vẹn tính tương thích ngược của schema JSON (`vietlott_summary.json`).
- Walk-Forward Backtest phải giữ nguyên tắc: tại kỳ $T$ chỉ được dùng dữ liệu lịch sử $\le T-1$.

---

### Task 1: Xây dựng Module Toán học Phủ Tổ hợp (Covering Wheel Engine)

**Files:**
- Create: `src/vietlott/model/covering_engine.py`
- Test: `src/vietlott/tests/test_covering_engine.py`

**Interfaces:**
- Produces: 
  - `get_optimal_covering_patterns(v: int, k: int, num_tickets: int = 6) -> List[List[int]]`
  - `evaluate_covering_guarantee(v: int, k: int, patterns: List[List[int]]) -> Dict[str, float]`
  - `generate_filtered_wheel_tickets(candidates: List[int], product_key: str, max_val: int, num_balls: int, num_tickets: int = 6) -> List[Dict[str, Any]]`

- [ ] **Step 1: Viết test kiểm chứng độ phủ toán học**
Viết `src/vietlott/tests/test_covering_engine.py` kiểm tra độ phủ 3-if-3 và 3-if-4 của dàn mẫu $C(12, 6, 3)$ và $C(10, 5, 3)$.

- [ ] **Step 2: Chạy test để xác nhận FAIL trước khi implement**
Chạy: `pytest src/vietlott/tests/test_covering_engine.py -v`

- [ ] **Step 3: Triển khai mã nguồn `CoveringWheelEngine`**
Tạo `src/vietlott/model/covering_engine.py` với các ma trận phủ chuẩn toán học, hàm tính $AC$, tổng Gaussian và hàm lọc vé.

- [ ] **Step 4: Chạy test để xác nhận PASS**
Chạy: `pytest src/vietlott/tests/test_covering_engine.py -v`

---

### Task 2: Tích hợp Covering Engine vào `render_web_data.py`

**Files:**
- Modify: `src/vietlott/render_web_data.py:617-690` (Hàm `generate_wheeling_strategy`)
- Modify: `src/vietlott/render_web_data.py:1420-1450` (Kiểm định Walk-Forward Wheeling trong `calculate_multi_model_consensus_and_backtest`)

**Interfaces:**
- Consumes: `generate_filtered_wheel_tickets` từ `src.vietlott.model.covering_engine`
- Produces: Cập nhật cấu trúc `wheeling_strategy` và `wheel_backtest` trong JSON đầu ra với độ phủ và cam kết bảo hiểm toán học chuẩn xác.

- [ ] **Step 1: Viết test kiểm thử tích hợp cho `render_web_data.py`**
Tạo file kiểm thử `src/vietlott/tests/test_wheeling_integration.py` kiểm tra `generate_wheeling_strategy` và backtest không làm gãy cấu trúc dữ liệu web.

- [ ] **Step 2: Cập nhật hàm `generate_wheeling_strategy`**
Thay thế hardcoded patterns cũ bằng `CoveringWheelEngine`, bổ sung thông tin độ phủ `coverage_3_if_3_pct` và `coverage_3_if_4_pct`.

- [ ] **Step 3: Cập nhật logic Walk-Forward Backtest trong `consensus_hub`**
Nâng cấp kiểm định từ dàn 4 vé cũ sang dàn phủ tối ưu 6 vé, ghi nhận số lần trúng giải Ba, giải Nhì, giải Nhất.

- [ ] **Step 4: Chạy test kiểm thử tích hợp**
Chạy: `pytest src/vietlott/tests/test_wheeling_integration.py -v`

---

### Task 3: Chạy Kiểm thử Toàn diện & Cập nhật Dữ liệu Thật

**Files:**
- Run: `python -m src.vietlott.render_web_data`
- Verify: `data/vietlott_summary.json` và `docs/data/vietlott_summary.json`

- [ ] **Step 1: Chạy pipeline render dữ liệu**
Chạy: `python -m src.vietlott.render_web_data`

- [ ] **Step 2: Kiểm tra đối soát kết quả Walk-Forward mới**
So sánh tỷ lệ trúng thưởng (`prize_won_count` và `win_rate_pct`) trước và sau nâng cấp.

- [ ] **Step 3: Cập nhật tài liệu kiến trúc**
Cập nhật `docs/architecture/MATHEMATICAL_MODELS.md` mục 5 phản ánh chính xác thuật toán $C(v, k, 3)$ mới.
