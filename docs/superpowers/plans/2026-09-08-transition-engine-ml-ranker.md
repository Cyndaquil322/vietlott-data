# Inter-Draw Transition Engine & ML Ranker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai Động cơ Khai phá Luật Chuyển trạng thái Liên kỳ ($A \to B$) và Mô hình Học máy Xếp hạng (HistGradientBoosting Ranker) trên vector đặc trưng 14 chiều với Walk-Forward Backtesting 100 kỳ, tích hợp bảng trực quan luật kéo bóng vào giao diện Web, tuân thủ nghiêm ngặt nguyên tắc Zero Mock Data và Zero Drift Specification.

**Architecture:**
- `src/vietlott/model/transition_engine.py`: Xây dựng ma trận chuyển tiếp liên kỳ $N \times N$, tính toán $P(B \mid A)$, $\text{Lift}(A \to B)$, $Z$-score nhị thức, trích xuất luật kéo bóng/kỵ nhau, và tính toán Trường lực hấp dẫn Vector (Vector Field Pull: `max_pull_lift`, `sum_z_score`, `repulsion_penalty`, `repeat_momentum`).
- `src/vietlott/model/ml_ranker.py`: Trích xuất vector đặc trưng 14 chiều cho mỗi con số, huấn luyện mô hình `HistGradientBoostingClassifier` qua cửa sổ trượt Walk-Forward Rolling Window, xuất điểm xếp hạng phi tuyến tính chuẩn hóa.
- `src/vietlott/model/ensemble_engine.py`: Tích hợp mô hình ML Ranker vào hệ thống đồng thuận Ensemble và xuất dữ liệu `transition_analytics`.
- `docs/assets/js/consensus_ensemble.js`: Widget trực quan hiển thị "Bản đồ Lực Hút Liên Kỳ ($A \to B$)" và cảnh báo cặp kỵ nhau.

**Tech Stack:** Python 3.11+, Scikit-Learn (`HistGradientBoostingClassifier`), NumPy, pytest, vanilla JS.

**Spec:** `docs/superpowers/specs/2026-09-08-transition-engine-ml-ranker-design.md`

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md Non-Negotiable Law).
- Huấn luyện mô hình ML và đánh giá Walk-Forward tại kỳ $T$ chỉ được sử dụng dữ liệu lịch sử $\le T-1$.
- Bảo toàn 100% tính tương thích ngược của schema JSON (`vietlott_summary.json`).
- Sử dụng `HistGradientBoostingClassifier` từ `scikit-learn` đã có sẵn trong môi trường, không cài đặt thêm package nặng.

---

### Task 1: Xây dựng Module Động Cơ Chuyển Trạng Thái Liên Kỳ (`transition_engine.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/transition_engine.py`
- Create: `src/vietlott/tests/test_transition_engine.py`

**Interfaces:**
- Produces:
  - `build_transition_matrix(records: List[Dict], max_val: int, num_balls: int, window_len: int = 150) -> Dict[Tuple[int, int], Dict[str, float]]`
  - `calculate_vector_field_pull(records: List[Dict], max_val: int, num_balls: int, window_len: int = 150) -> Dict[int, Dict[str, float]]`
  - `extract_significant_transition_rules(records: List[Dict], max_val: int, num_balls: int, min_z: float = 2.0, max_rules: int = 10) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_transition_engine.py`**
  - Kiểm tra tính toán chính xác của $N_{AB}$, $E_{AB}$, $Z$-score, và Lift.
  - Kiểm tra `calculate_vector_field_pull` trả về đủ 4 trường đặc trưng: `max_pull_lift`, `sum_z_score`, `repulsion_penalty`, `repeat_momentum` cho mọi bóng $1 \dots \text{max\_val}$.
  - Kiểm tra `extract_significant_transition_rules` phân tách chính xác danh sách kéo mạnh ($Z \ge 2.0$) và kỵ nhau ($Z \le -2.0$).
  - Kiểm tra khả năng xử lý ca biên: danh sách rỗng, kích thước nhỏ.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_transition_engine.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/transition_engine.py`**
  - Hiện thực hàm `build_transition_matrix` duyệt tuần tự qua các kỳ liên tiếp.
  - Hiện thực hàm `calculate_vector_field_pull` từ kết quả của kỳ gần nhất.
  - Hiện thực hàm `extract_significant_transition_rules` định dạng kết quả thân thiện cho Web UI.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_transition_engine.py -v`

---

### Task 2: Xây dựng Module Học Máy Xếp Hạng (`ml_ranker.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/ml_ranker.py`
- Create: `src/vietlott/tests/test_ml_ranker.py`

**Interfaces:**
- Consumes: `evaluate_all_models` từ `analytic_engines`, `calculate_vector_field_pull` từ `transition_engine`.
- Produces:
  - `extract_feature_matrix_for_draw(sub_records: List[Dict], max_val: int, num_balls: int, opt_alpha: float = 0.035, is_two_matrix: bool = False) -> np.ndarray` (kích thước $(N, 14)$)
  - `train_and_predict_ml_ranker(sub_records: List[Dict], max_val: int, num_balls: int, train_window: int = 60, opt_alpha: float = 0.035, is_two_matrix: bool = False) -> Dict[int, float]`
  - `HistGradientBoostingRanker` class.

- [ ] **Step 1: Viết test TDD trong `test_ml_ranker.py`**
  - Kiểm tra ma trận đặc trưng $(N, 14)$ không chứa NaN/Inf.
  - Kiểm tra mô hình `HistGradientBoostingRanker` huấn luyện thành công và dự báo xác suất trong đoạn $[0, 1]$.
  - Kiểm tra `train_and_predict_ml_ranker` trả về dictionary điểm số chuẩn tắc $[0, 3.0]$ cho tất cả các bóng từ 1 đến `max_val`.
  - Kiểm tra tính tất định 100% với `random_state=42`.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_ml_ranker.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/ml_ranker.py`**
  - Viết hàm ghép nối 14 đặc trưng định lượng: 7 mô hình toán học + 4 đặc trưng liên kỳ Vector Pull + 3 đặc trưng số học/cụm.
  - Viết class `HistGradientBoostingRanker` bao bọc `HistGradientBoostingClassifier` từ `sklearn.ensemble`.
  - Viết hàm `train_and_predict_ml_ranker` chạy cửa sổ huấn luyện rolling window an toàn.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_ml_ranker.py -v`

---

### Task 3: Tích hợp ML Ranker & Transition Analytics vào `ensemble_engine.py`

**Files:**
- Modify: `src/vietlott/model/ensemble_engine.py`
- Modify: `src/vietlott/render_web_data.py`
- Create: `src/vietlott/tests/test_ml_integration.py`

**Interfaces:**
- Consumes: `train_and_predict_ml_ranker` từ `ml_ranker`, `extract_significant_transition_rules` từ `transition_engine`.
- Produces:
  - Bổ sung mô hình `ml_ranker` vào `models_info` và Walk-Forward backtest.
  - Bổ sung trường `transition_analytics` vào `consensus_hub`.

- [ ] **Step 1: Viết test kiểm thử tích hợp trong `test_ml_integration.py`**
  - Kiểm tra `calculate_multi_model_consensus_and_backtest` xuất trường `transition_analytics` với danh sách luật kéo và luật kỵ.
  - Kiểm tra mô hình `ml_ranker` xuất hiện trong `leaderboard` và `model_explanations`.
  - Kiểm tra schema JSON bảo toàn 100% tương thích ngược.

- [ ] **Step 2: Cập nhật `ensemble_engine.py`**
  - Tích hợp `ml_ranker` vào danh sách mô hình tham gia đồng thuận (tổng cộng 8 mô hình).
  - Thêm phần tính toán và đóng gói `transition_analytics` cho kỳ quay kế tiếp.

- [ ] **Step 3: Cập nhật `render_web_data.py`**
  - Đảm bảo `generate_web_summary` truyền tải đầy đủ `transition_analytics` vào `data/vietlott_summary.json`.

- [ ] **Step 4: Chạy test tích hợp**
  `pytest src/vietlott/tests/test_ml_integration.py -v`

---

### Task 4: Cập nhật Giao Diện Web, Render Dữ Liệu Thật & Cập Nhật Tài Liệu

**Files:**
- Modify: `docs/assets/js/consensus_ensemble.js` (và `assets/js/consensus_ensemble.js`)
- Run: `python -m src.vietlott.render_web_data`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

- [ ] **Step 1: Cập nhật giao diện Web `consensus_ensemble.js`**
  - Thêm thẻ hiển thị trực quan **"Bản đồ Lực Hút Liên Kỳ ($A \to B$)"**:
    - Danh sách các cặp bóng kỳ trước đang kéo mạnh bóng kỳ này (hiển thị rõ số kỳ trước, số kỳ này, hệ số Lift, $Z$-score).
    - Cảnh báo các cặp bóng kỵ nhau cần tránh.
  - Thêm cấu hình màu sắc/icon cho mô hình `ml_ranker` (màu tím Violet/Purple, icon `brain-circuit`).

- [ ] **Step 2: Chạy pipeline tạo dữ liệu thực tế**
  - Chạy `python -m src.vietlott.render_web_data`.
  - Xác nhận tạo thành công `vietlott_summary.json` chứa `transition_analytics` và 8 mô hình.

- [ ] **Step 3: Đồng bộ tài liệu kỹ thuật**
  - Bổ sung Mục 15 vào `docs/architecture/MATHEMATICAL_MODELS.md`: Đặc tả toán học ma trận chuyển tiếp, kiểm định $Z$-score và kiến trúc HistGradientBoosting Ranker 14 chiều.
  - Cập nhật `SYSTEM_ARCHITECTURE.md`.

- [ ] **Step 4: Chạy toàn bộ pytest suite**
  `pytest src/vietlott/tests/ -v` (Đảm bảo 75+ bài test PASS 100%).
