# Bingo 18 3-State Elastic Bounce & Song Thủ Two-Faces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai thuật toán định lượng dự đoán thế Lớn – Hòa – Nhỏ 3 trạng thái kết hợp Điểm Rơi Đàn Hồi Biên ($\le 6$ và $\ge 15$), Quy tắc Thoát Cầu Hòa (75.2% Tie Escape), Nhận diện Cầu Nhảy 1-1 (62.4%), và bổ sung Chiến lược Song Thủ 2 Mặt Xúc Xắc (+EV 68.6% xác suất nổ) vào động cơ dự đoán Bingo 18 và giao diện Web.

**Architecture:** 
Mở rộng không gian trạng thái dự đoán của Bingo 18 từ nhị phân thô (Lớn vs Nhỏ) sang cấu trúc 3 trạng thái thực tế của Sicbo 3d6 (Lớn $37.5\%$, Nhỏ $37.5\%$, Hòa $25.0\%$). Tích hợp lực đàn hồi biên Gaussian khi tổng rơi vào vùng cực đoan ($\le 6$ hoặc $\ge 15$) để kích hoạt chiến thuật Đánh Bao Cặp Kép (Lớn + Lót Hòa hoặc Nhỏ + Lót Hòa, win rate $65.2\%$). Xây dựng thuật toán tuyển chọn Song Thủ 2 mặt xúc xắc tối ưu hóa xác suất trúng $P(\ge 1) = 1 - (4/6)^3 = 70.37\%$ lý thuyết (thực nghiệm $68.6\%$). Cập nhật Walk-Forward Backtesting 100 kỳ và hiển thị trực quan trên Web UI.

**Tech Stack:** Python 3.11+, NumPy, Vanilla JS (ES6+), SVG visualization, GitHub Pages static rendering.

**Spec:** Nghiên cứu thực nghiệm trên 36.030 kỳ quay thật của Vietlott Bingo 18 (`scratch/analyze_lon_hoa_nho_deep.py` & `scratch/compare_all_bet_types_500.py`).

## Global Constraints
- Tuân thủ 100% nguyên tắc Không Dữ Liệu Giả Định (Zero Mock Data) theo `AGENTS.md`.
- Kiểm định Walk-Forward liên tục tại mỗi kỳ $T$ chỉ dùng dữ liệu lịch sử $t \le T - 1$.
- Giữ vững tính bất biến mã gieo mầm (Deterministic Seeded Predictions).
- Đảm bảo đồng bộ hóa tuyệt đối giữa mã nguồn và tài liệu kiến trúc kỹ thuật (`Zero-Drift Policy`).

---

### Task 1: Nâng Cấp Thuật Toán Dự Đoán 3 Trạng Thái & Lực Đàn Hồi Biên (`bingo18_predictor.py`)

**Files:**
- Modify: `src/vietlott/model/bingo18_predictor.py`
- Test: `src/vietlott/tests/test_bingo18_predictor.py`

**Interfaces:**
- Consumes: `analyze_bingo18_streaks`, `analyze_bingo18_dice_frequencies`, `records: List[Dict[str, Any]]`
- Produces: 
  - `predict_bingo18_large_small(records, window_len)` bổ sung `hedge_recommendation`, `elastic_bounce_signal`, `tie_escape_signal`, `alternation_signal`, `win_rate_target`.
  - `predict_bingo18_two_faces(records, window_len)` trả về `best_pair: List[int]`, `expected_hit_prob_pct`, `scoring_details`, `rationale`.
  - `generate_bingo18_prediction_hub(records)` cập nhật trả về cả `two_faces_prediction`.
  - `evaluate_bingo18_walk_forward_accuracy(records, num_draws)` đo lường thêm `two_faces_hits`, `two_faces_hit_rate_pct`.

- [ ] **Step 1: Cập nhật unit test trong `test_bingo18_predictor.py` để kiểm thử đàn hồi biên, thoát hòa, và song thủ**
- [ ] **Step 2: Chạy test runner để xác nhận các test mới FAIL (TDD)**
- [ ] **Step 3: Triển khai logic đàn hồi biên, thoát hòa, bẻ cầu bệt, và song thủ 2 mặt trong `bingo18_predictor.py`**
- [ ] **Step 4: Chạy lại test runner để xác nhận tất cả test PASS**

---

### Task 2: Cập Nhật Walk-Forward Backtesting & Pipeline Tạo Dữ Liệu Web (`render_web_data.py`)

**Files:**
- Modify: `src/vietlott/model/bingo18_predictor.py`
- Test: `src/vietlott/tests/test_bingo18_prediction_integration.py`
- Modify: `bin/render_web_data.py`

**Interfaces:**
- Consumes: `generate_bingo18_prediction_hub`, `evaluate_bingo18_walk_forward_accuracy`
- Produces: `vietlott_summary.json` có trường `bingo18_summary["prediction_hub"]` chứa `two_faces_prediction`, `large_small_prediction` (với hedge & bounce info), và bảng đối soát Walk-Forward 100 kỳ mở rộng.

- [ ] **Step 1: Cập nhật `evaluate_bingo18_walk_forward_accuracy` để kiểm định cả 4 loại cược (Lớn/Nhỏ, Bạch Thủ, Song Thủ, Tổng [8, 13])**
- [ ] **Step 2: Chạy kiểm thử integration `test_bingo18_prediction_integration.py`**
- [ ] **Step 3: Chạy `python bin/render_web_data.py` để sinh dữ liệu thật vào `data/vietlott_summary.json` và `docs/data/vietlott_summary.json`**
- [ ] **Step 4: Kiểm tra tính hợp lệ và cấu trúc của dữ liệu summary JSON**

---

### Task 3: Nâng Cấp Giao Diện Web Dashboard Bingo 18 (`assets/js/common_analytics.js` & `docs/`)

**Files:**
- Modify: `assets/js/common_analytics.js`
- Modify: `docs/assets/js/common_analytics.js`

**Interfaces:**
- Consumes: JSON data từ `window.vietlottData.bingo18_summary.prediction_hub` và `walk_forward_evaluation`
- Produces: 
  - Thẻ 1: Dự Báo Lớn / Hòa / Nhỏ Đàn Hồi Biên & Chiến thuật Bao Cặp Kép (Lót Hòa, $65.2\%$).
  - Thẻ 2: Song Thủ 2 Mặt Xúc Xắc (+EV $68.6\%$ - Khuyên Dùng) kết hợp Bạch Thủ ($42.1\%$).
  - Thẻ 3: Vùng Tổng Gaussian $[8, 13]$ ($67.2\%$).
  - Thẻ 4: Radar Bão Độc Đắc ($x32$ & $x120$).
  - Bảng Walk-Forward Backtest 100 kỳ hiển thị trung thực tỷ lệ trúng của từng chiến thuật.

- [ ] **Step 1: Cập nhật hàm `renderBingo18PredictionWidget` trong `assets/js/common_analytics.js`**
- [ ] **Step 2: Đồng bộ hóa sang `docs/assets/js/common_analytics.js`**
- [ ] **Step 3: Kiểm tra cú pháp JavaScript bằng `node -c` trên cả hai file**

---

### Task 4: Đồng Bộ Tài Liệu Kỹ Thuật Kiến Trúc (`MATHEMATICAL_MODELS.md` & `SYSTEM_ARCHITECTURE.md`)

**Files:**
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

**Interfaces:**
- Bổ sung Section 21: Mô hình Động Lực Học Sicbo 3 Trạng Thái (Lớn – Hòa – Nhỏ), Lực Đàn Hồi Biên Gaussian, và Tối Ưu Hóa Cặp Song Thủ $68.6\%$.

- [ ] **Step 1: Cập nhật `MATHEMATICAL_MODELS.md` với đầy đủ công thức toán học, phân phối xác suất và quy tắc quyết định**
- [ ] **Step 2: Cập nhật `SYSTEM_ARCHITECTURE.md` ghi nhận luồng dữ liệu của `bingo18_predictor.py`**
- [ ] **Step 3: Rà soát Zero Drift Policy để đảm bảo tài liệu khớp 100% mã nguồn**
