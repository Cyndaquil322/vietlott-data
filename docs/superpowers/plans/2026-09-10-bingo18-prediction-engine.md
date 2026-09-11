# Bingo 18 Quantitative Prediction Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng Động cơ Dự đoán Định lượng chuyên biệt cho Bingo 18 (`bingo18_predictor.py`) tích hợp 4 chiến lược toán học: Dự báo thế cầu Lớn/Nhỏ (Markov & Hồi quy chuỗi bệt), Mặt xúc xắc Bạch Thủ (+EV 42%), Khoảng tổng Gaussian vàng [8, 13], và Tín hiệu kích hoạt Săn Bão Độc Đắc (Poisson Hazard x120), tích hợp vào đường ống dữ liệu và giao diện Web với 100% Zero Mock Data.

**Architecture:**
- `src/vietlott/model/bingo18_predictor.py`:
  - `predict_bingo18_large_small`: Tính toán ma trận chuyển trạng thái Markov bậc 1 & bậc 2, đo lường độ đàn hồi bẻ cầu, đưa ra khuyến nghị Lớn/Nhỏ kèm độ tin cậy và chiến thuật (Bắt Cầu Bệt vs Bẻ Cầu).
  - `predict_bingo18_single_face`: Tính $Z$-score nhịp rơi của 6 mặt xúc xắc, chọn 1 mặt Bạch Thủ có xác suất trúng cao nhất ($P \approx 42\% - 45\%$).
  - `predict_bingo18_target_sum`: Định vị khoảng tổng mục tiêu Gaussian $[8, 13]$ và điểm rơi đàn hồi Wavelet.
  - `evaluate_bingo18_storm_trigger`: Xác định thời điểm kích hoạt chiến thuật "Nuôi Bão" khi số kỳ vắng bóng bão đạt điểm rơi cực đại ($g \ge 70$ kỳ).
  - `evaluate_bingo18_walk_forward_accuracy`: Kiểm định Walk-Forward 100 kỳ đo độ chính xác thực tế.
- `src/vietlott/render_web_data.py`: Tích hợp `prediction_hub` vào `products.bingo18`.
- `docs/assets/js/common_analytics.js`: Widget trực quan "BẢNG GỢI Ý DỰ ĐOÁN BINGO 18 KỲ KẾ TIẾP" hiển thị 4 thẻ khuyến nghị rõ ràng.

**Tech Stack:** Python 3.11+, NumPy, pytest, vanilla JS.

**Spec:** `docs/architecture/MATHEMATICAL_MODELS.md` (Mục 20: Hệ thống Dự đoán Định lượng Bingo 18).

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md Non-Negotiable Law).
- 100% việc dự đoán kỳ tiếp theo và kiểm định Walk-Forward chỉ sử dụng dữ liệu lịch sử $\le T-1$.
- Bảo toàn 100% tính tương thích ngược của schema JSON (`vietlott_summary.json`).

---

### Task 1: Xây dựng Module Dự Đoán Định Lượng Bingo 18 (`bingo18_predictor.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/bingo18_predictor.py`
- Create: `src/vietlott/tests/test_bingo18_predictor.py`

**Interfaces:**
- Produces:
  - `predict_bingo18_large_small(records: List[Dict], window_len: int = 100) -> Dict[str, Any]`
  - `predict_bingo18_single_face(records: List[Dict], window_len: int = 100) -> Dict[str, Any]`
  - `predict_bingo18_target_sum(records: List[Dict], window_len: int = 100) -> Dict[str, Any]`
  - `evaluate_bingo18_storm_trigger(records: List[Dict]) -> Dict[str, Any]`
  - `generate_bingo18_prediction_hub(records: List[Dict]) -> Dict[str, Any]`
  - `evaluate_bingo18_walk_forward_accuracy(records: List[Dict], num_draws: int = 100) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_bingo18_predictor.py`**
  - Kiểm tra `predict_bingo18_large_small` trả về dự báo hợp lệ ("Lớn" hoặc "Nhỏ"), độ tin cậy trong khoảng $[50.0\%, 85.0\%]$.
  - Kiểm tra `predict_bingo18_single_face` chọn đúng mặt xúc xắc từ 1 đến 6.
  - Kiểm tra `predict_bingo18_target_sum` trả về tổng mục tiêu trong $[8, 13]$.
  - Kiểm tra `evaluate_bingo18_storm_trigger` phát tín hiệu kích hoạt khi $g \ge 70$ kỳ.
  - Kiểm tra `evaluate_bingo18_walk_forward_accuracy` đo tỷ lệ thắng thực tế trên dữ liệu lịch sử.
  - Kiểm tra tính tất định và xử lý ca biên (records rỗng/ngắn).

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_bingo18_predictor.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/bingo18_predictor.py`**
  - Hiện thực logic phân tích xích Markov và hồi quy chuỗi bệt.
  - Hiện thực $Z$-score nhịp rơi mặt xúc xắc đơn.
  - Hiện thực khoảng tổng Gaussian và trigger săn bão Poisson.
  - Hiện thực hàm kiểm định Walk-Forward 100 kỳ.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_bingo18_predictor.py -v`

---

### Task 2: Tích Hợp Vào `render_web_data.py` & Kiểm Thử Tích Hợp

**Files:**
- Modify: `src/vietlott/render_web_data.py` (Hàm `process_bingo18`)
- Create: `src/vietlott/tests/test_bingo18_prediction_integration.py`

**Interfaces:**
- Consumes: `generate_bingo18_prediction_hub` từ `bingo18_predictor`.
- Produces: Bổ sung trường `prediction_hub` vào `products.bingo18` trong `vietlott_summary.json`.

- [ ] **Step 1: Viết test kiểm thử tích hợp trong `test_bingo18_prediction_integration.py`**
  - Kiểm tra `process_bingo18` xuất trường `prediction_hub` với đủ 4 thành phần dự đoán.
  - Kiểm tra bảo toàn 100% các trường dữ liệu hiện hữu.

- [ ] **Step 2: Cập nhật `process_bingo18` trong `render_web_data.py`**
  - Gọi `generate_bingo18_prediction_hub(records)` và đưa vào output JSON.

- [ ] **Step 3: Chạy test kiểm thử tích hợp**
  `pytest src/vietlott/tests/test_bingo18_prediction_integration.py -v`

---

### Task 3: Thiết Kế Giao Diện Web Soi Cầu Bingo 18 & Đồng Bộ Tài Liệu

**Files:**
- Modify: `docs/assets/js/common_analytics.js` & `assets/js/common_analytics.js`
- Run: `python -m src.vietlott.render_web_data`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

- [ ] **Step 1: Cập nhật giao diện Web `common_analytics.js`**
  - Thêm thẻ widget nổi bật **"GỢI Ý DỰ ĐOÁN BINGO 18 KỲ TIẾP THEO (SICBO QUANT PREDICTOR)"** gồm 4 khối trực quan:
    1. *Khối Thế Cầu:* Lớn / Nhỏ, độ tin cậy %, chiến thuật Bệt / Bẻ cầu.
    2. *Khối Bạch Thủ:* 1 mặt xúc xắc 3D sáng nhất, xác suất kỳ vọng $42\%$.
    3. *Khối Tổng Rơi Vàng:* Khoảng tổng $[8, 13]$ & tổng tối ưu nhất.
    4. *Khối Săn Bão:* Radar cảnh báo điểm rơi bão x120.
  - Đồng bộ song song `docs/` và root.

- [ ] **Step 2: Chạy pipeline render dữ liệu thật**
  - Chạy `python -m src.vietlott.render_web_data`.
  - Xác nhận `vietlott_summary.json` có đủ `prediction_hub`.

- [ ] **Step 3: Cập nhật tài liệu kiến trúc kỹ thuật (Zero Drift Policy)**
  - Bổ sung Mục 20 vào `docs/architecture/MATHEMATICAL_MODELS.md`.
  - Cập nhật `SYSTEM_ARCHITECTURE.md`.

- [ ] **Step 4: Chạy toàn bộ pytest suite**
  `pytest src/vietlott/tests/ -v` (Đảm bảo 150+ bài test PASS 100%).
