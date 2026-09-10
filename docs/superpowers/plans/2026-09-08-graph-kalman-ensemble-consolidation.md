# Graph PageRank, Kalman State-Space, and System Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai 2 mô hình toán học mới (Graph PageRank Centrality & Bayesian Dynamic State-Space Kalman Filter), nâng cấp Ensemble từ 5 lên 7 mô hình độc lập với Walk-Forward 100 kỳ, và phân rã refactor `render_web_data.py` thành các module độc lập `analytic_engines.py` và `ensemble_engine.py` bảo toàn 100% tính tương thích ngược và zero mock data.

**Architecture:**
- `src/vietlott/model/analytic_engines.py`: Thư viện chứa 7 mô hình toán học độc lập thuần NumPy (Bayesian Hazard, Exponential Decay, Markov PPMI, Wavelet-Fourier Spectral, Empirical Bayes Lift, Graph PageRank Centrality, Bayesian Dynamic State-Space Filter).
- `src/vietlott/model/ensemble_engine.py`: Động cơ tổng hợp Dynamic Alpha Stacking, Walk-Forward Backtester 100 kỳ, và trích xuất vé số học (Triad, Key 5, Core Pool, Wheeling tối ưu, Bao 7 Pareto).
- `src/vietlott/render_web_data.py`: Rút gọn thành pipeline orchestrator đọc JSONL, tính toán các bảng thống kê bề mặt, gọi `ensemble_engine` và xuất `vietlott_summary.json`.
- `docs/assets/js/consensus_ensemble.js`: Bổ sung color scheme và badge cho 2 mô hình mới.

**Tech Stack:** Python 3.11+, NumPy, pytest, vanilla JS.

**Spec:** `docs/superpowers/specs/2026-09-08-graph-kalman-ensemble-consolidation-design.md`

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md Non-Negotiable Law).
- Tất cả các phép tính Walk-Forward tại kỳ $T$ chỉ được sử dụng dữ liệu $\le T-1$.
- 100% bảo toàn cấu trúc schema JSON (`vietlott_summary.json`) để không làm gãy giao diện Web hiện tại.
- Zero external dependencies mới: Tất cả thuật toán đồ thị và Kalman viết bằng thuần NumPy.

---

### Task 1: Xây dựng Module 7 Mô Hình Độc Lập (`analytic_engines.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/analytic_engines.py`
- Create: `src/vietlott/tests/test_analytic_engines.py`

**Interfaces:**
- Produces:
  - `calculate_bayesian_hazard_scores(sub_records: List[Dict], max_val: int, num_balls: int, is_two_matrix: bool = False) -> Dict[int, float]`
  - `calculate_exponential_decay_scores(sub_records: List[Dict], max_val: int, num_balls: int, alpha: float = 0.035, is_two_matrix: bool = False) -> Dict[int, float]`
  - `calculate_markov_ppmi_scores(sub_records: List[Dict], max_val: int, num_balls: int, is_two_matrix: bool = False) -> Dict[int, float]`
  - `calculate_hybrid_spectral_scores(sub_records: List[Dict], max_val: int, num_balls: int, window_len: int = 64) -> Dict[int, float]`
  - `calculate_empirical_bayes_lift_scores(sub_records: List[Dict], max_val: int, num_balls: int, is_two_matrix: bool = False) -> Dict[int, float]`
  - `calculate_graph_pagerank_scores(sub_records: List[Dict], max_val: int, num_balls: int, damping: float = 0.85, max_iter: int = 50, window_len: int = 100, is_two_matrix: bool = False) -> Dict[int, float]`
  - `calculate_state_space_scores(sub_records: List[Dict], max_val: int, num_balls: int, decay: float = 0.92, window_len: int = 80, is_two_matrix: bool = False) -> Dict[int, float]`
  - `evaluate_all_models(sub_records: List[Dict], max_val: int, num_balls: int, opt_alpha: float = 0.035, is_two_matrix: bool = False) -> Dict[str, Dict[int, float]]`

- [ ] **Step 1: Viết test TDD cho các mô hình toán học trong `test_analytic_engines.py`**
  - Kiểm tra tính đối xứng của ma trận kề trong Graph PageRank, tổng xác suất PageRank $\sum p_i = 1$, hội tụ dưới 50 vòng lặp.
  - Kiểm tra bộ lọc Kalman State-Space: trạng thái cập nhật đúng sau khi bóng xuất hiện, hiệp phương sai sai số $P_t$ giảm dần và ổn định.
  - Kiểm tra các hàm trả về dictionary điểm số chuẩn tắc với các khóa từ 1 đến `max_val`, không có NaN/Inf.

- [ ] **Step 2: Chạy test để xác nhận FAIL trước khi implement**
  `pytest src/vietlott/tests/test_analytic_engines.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/analytic_engines.py`**
  - Di chuyển các hàm tính điểm hiện tại từ `render_web_data.py` sang `analytic_engines.py`.
  - Triển khai thuật toán Graph PageRank qua Power Iteration thuần NumPy.
  - Triển khai thuật toán Bayesian Dynamic State-Space Filter (1D Kalman Filter per ball) thuần NumPy.
  - Tạo hàm `evaluate_all_models` trả về từ điển điểm của cả 7 mô hình.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_analytic_engines.py -v`

---

### Task 2: Xây dựng Module Tổng Hợp Đồng Thuận (`ensemble_engine.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/ensemble_engine.py`
- Create: `src/vietlott/tests/test_ensemble_engine.py`

**Interfaces:**
- Consumes: `evaluate_all_models` từ `src.vietlott.model.analytic_engines`, `generate_filtered_wheel_tickets` và `get_optimal_covering_patterns` từ `src.vietlott.model.covering_engine`.
- Produces:
  - `calculate_multi_model_consensus_and_backtest(records: List[Dict], product_key: str, max_val: int, num_balls: int, is_two_matrix: bool = False, num_draws: int = 100, display_draws: int = 15) -> Dict[str, Any]`
  - `generate_wheeling_strategy(records: List[Dict], product_key: str, max_val: int, num_balls: int, is_two_matrix: bool = False) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD cho Ensemble Engine trong `test_ensemble_engine.py`**
  - Kiểm thử `calculate_multi_model_consensus_and_backtest`:
    - 7 mô hình xuất hiện đầy đủ trong `leaderboard` và `model_explanations`.
    - `training_report.trained_model_weights` có đủ 7 mô hình với tổng tỷ lệ phần trăm $100\%$.
    - `tickets` có đủ: `key_balls` (Triad), `key_5_balls`, `core_pool`, `wheeling_tickets`, `wheeling_4_tickets`, `golden`.
    - Tính tương thích ngược 100% với schema JSON của Web UI.
  - Kiểm thử `generate_wheeling_strategy` cho 6/55, 6/45, 5/35.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_ensemble_engine.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/ensemble_engine.py`**
  - Tách logic Walk-Forward 100 kỳ và Dynamic Alpha Stacking cho 7 mô hình.
  - Phân bổ trọng số động theo Out-Of-Fold Alpha Softmax bình phương.
  - Tích hợp sinh vé Triad, Key 5, Core Pool, Wheeling $C(v, k, 3)$ và Golden Ticket.
  - Đảm bảo gieo mầm cố định theo mã kỳ quay (`Draw ID Seed`).

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_ensemble_engine.py -v`

---

### Task 3: Thu Gọn `render_web_data.py`, Gom Thư Mục Cũ & Cập Nhật Giao Diện Web

**Files:**
- Modify: `src/vietlott/render_web_data.py` (Refactor từ 2.400+ dòng xuống ~400-500 dòng)
- Create: `src/vietlott/model/legacy_strategies/__init__.py` (Di chuyển các chiến lược cũ)
- Modify: `docs/assets/js/consensus_ensemble.js` (Thêm tag styling cho `graph_pagerank` và `state_space`)
- Test: `src/vietlott/tests/test_production_core.py`

**Interfaces:**
- `render_web_data.py` import `calculate_multi_model_consensus_and_backtest` và `generate_wheeling_strategy` từ `vietlott.model.ensemble_engine`.

- [ ] **Step 1: Cập nhật CSS/JS trong `docs/assets/js/consensus_ensemble.js`**
  Thêm cấu hình badge màu sắc và icon cho `graph_pagerank` (Cyan) và `state_space` (Rose) để bảng giao diện hiển thị đẹp mắt và mượt mà.

- [ ] **Step 2: Tái cấu trúc `render_web_data.py`**
  - Chuyển giao toàn bộ phần tính toán mô hình và consensus sang `ensemble_engine`.
  - Giữ lại các hàm xử lý thống kê bề mặt (`calculate_draw_statistics`, `calculate_cooccurrence`, `calculate_sum_and_patterns`, v.v.).
  - Giữ lại hàm điều phối chính `generate_web_summary`.

- [ ] **Step 3: Gom gọn thư mục `strategy/` cũ**
  Di chuyển nội dung từ `src/vietlott/model/strategy/` sang `src/vietlott/model/legacy_strategies/` và để lại shim import tương thích ngược trong `strategy/__init__.py` để các test cũ không bị gãy.

- [ ] **Step 4: Chạy lại toàn bộ test suite để đảm bảo 0 regression**
  `pytest src/vietlott/tests/ -v`

---

### Task 4: Chạy Kiểm Thử Toàn Diện, Render Dữ Liệu Thật & Cập Nhật Tài Liệu

**Files:**
- Run: `python -m src.vietlott.render_web_data`
- Verify: `data/vietlott_summary.json` và `docs/data/vietlott_summary.json`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

- [ ] **Step 1: Chạy pipeline tạo dữ liệu thực tế**
  Chạy: `python -m src.vietlott.render_web_data`
  Xác nhận file JSON tạo thành công, có đủ 7 mô hình và dung lượng ~750KB.

- [ ] **Step 2: Kiểm tra đối soát kết quả Walk-Forward mới**
  In kết quả Leaderboard 7 mô hình cho Power 6/55, Mega 6/45 và Lotto 5/35.

- [ ] **Step 3: Cập nhật tài liệu kiến trúc kỹ thuật**
  Cập nhật `docs/architecture/MATHEMATICAL_MODELS.md` và `SYSTEM_ARCHITECTURE.md` phản ánh chính xác cấu trúc module mới và 7 mô hình toán học (Zero Drift Policy).

- [ ] **Step 4: Chạy toàn bộ pytest suite**
  `pytest src/vietlott/tests/ -v`
  Đảm bảo 100% tests PASS.
