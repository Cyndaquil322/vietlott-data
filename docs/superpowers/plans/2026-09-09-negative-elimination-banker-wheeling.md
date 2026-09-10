# Negative Elimination Mining & Key-Banker Wheeling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai Động cơ Đào thải Bóng Chết (Negative Elimination Mining) thu hẹp không gian số từ 55 xuống 39 (hoặc 45 xuống 32), và xây dựng Dàn Ghép Bọc Lót Có Bóng Chốt Bạch Thủ (Key-Banker Wheeling Design $B(1, 10, k, 3)$) tận dụng tỷ lệ nổ $70\%$ của Key 5 để nhân đôi tỷ lệ trúng thưởng thực chiến, với 100% Zero Mock Data.

**Architecture:**
- `src/vietlott/model/elimination_engine.py`: Tính toán Chỉ số Nguy cơ Ngủ Đông $\mathcal{E}(b)$ dựa trên nhịp gan quá hạn, năng lượng phổ Wavelet triệt tiêu, lực kỵ nhau liên kỳ $A \to B$ và đồng thuận đáy. Đào thải 16 bóng chết trên 6/55 (13 trên 6/45, 9 trên 5/35) và đo lường độ chính xác đào thải Walk-Forward ($\ge 90\%$).
- `src/vietlott/model/banker_wheeling.py`: Chọn 1 Bóng Chốt Bạch Thủ ($B_1$) từ Key 5, chọn 10 bóng vệ tinh từ Core Pool sạch, sinh dàn 6 vé bọc lót đảm bảo $B_1$ có mặt trong 100% các vé con.
- `src/vietlott/model/ensemble_engine.py`: Tích hợp Elimination Analytics và Banker Wheeling vào Consensus Hub.
- `docs/assets/js/consensus_ensemble.js`: Widget hiển thị "Bộ Lọc Đào Thải Bóng Chết (Dead Numbers Pruning)" và bảng "Dàn Bọc Lót Bạch Thủ Chốt (Key-Banker Wheeling)".

**Tech Stack:** Python 3.11+, NumPy, Scikit-Learn, pytest, vanilla JS.

**Spec:** `docs/superpowers/specs/2026-09-09-negative-elimination-banker-wheeling-design.md`

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md Non-Negotiable Law).
- 100% việc đào thải bóng và chọn bóng chốt phải dựa trên dữ liệu lịch sử $\le T-1$ (Strict Walk-Forward Discipline).
- Bảo toàn 100% tính tương thích ngược của schema JSON (`vietlott_summary.json`).
- Zero external dependencies mới (thuần NumPy và thư viện sẵn có).

---

### Task 1: Xây dựng Module Bộ Lọc Đào Thải Bóng Chết (`elimination_engine.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/elimination_engine.py`
- Create: `src/vietlott/tests/test_elimination_engine.py`

**Interfaces:**
- Produces:
  - `calculate_elimination_risk_scores(sub_records: List[Dict], max_val: int, num_balls: int, models_eval: Dict[str, Any] = None, transition_pull: Dict[int, Dict[str, float]] = None) -> Dict[int, Dict[str, Any]]`
  - `prune_dead_numbers(risk_scores: Dict[int, Dict[str, Any]], max_val: int, elim_count: int) -> Dict[str, Any]`
  - `evaluate_walk_forward_elimination_precision(records: List[Dict], max_val: int, num_balls: int, num_draws: int = 100) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_elimination_engine.py`**
  - Kiểm tra tính toán điểm nguy cơ $\mathcal{E}(b)$ cho mọi bóng $1 \dots \text{max\_val}$, không chứa NaN/Inf.
  - Kiểm tra `prune_dead_numbers` lọc chính xác đúng số lượng bóng quy định (`elim_count`), trích xuất lý do cụ thể (Gan lì / Ngủ đông / Kỵ nhau / Đáy đồng thuận).
  - Kiểm tra `evaluate_walk_forward_elimination_precision` đo độ chính xác đào thải $\ge 85\%$.
  - Kiểm tra xử lý ca biên (records rỗng, records ngắn) và tính tất định 100%.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_elimination_engine.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/elimination_engine.py`**
  - Hiện thực hàm tính điểm nguy cơ ngủ đông 4 nhân tố $\mathcal{E}(b)$.
  - Hiện thực hàm `prune_dead_numbers` phân loại lý do đào thải.
  - Hiện thực kiểm định Walk-Forward tính tỷ lệ bóng chết thực tế không nổ.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_elimination_engine.py -v`

---

### Task 2: Xây dựng Module Dàn Ghép Bọc Lót Có Bóng Chốt (`banker_wheeling.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/banker_wheeling.py`
- Create: `src/vietlott/tests/test_banker_wheeling.py`

**Interfaces:**
- Produces:
  - `select_primary_banker(key_balls: List[int], consensus_scores: Dict[int, float], pull_data: Dict[int, Dict[str, float]] = None) -> int`
  - `generate_key_banker_tickets(banker: int, satellite_pool: List[int], product_key: str, max_val: int, num_balls: int, num_tickets: int = 6, seed: int = 42) -> Dict[str, Any]`
  - `evaluate_banker_wheeling_walk_forward(records: List[Dict], max_val: int, num_balls: int, num_draws: int = 100) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_banker_wheeling.py`**
  - Kiểm tra `select_primary_banker` chọn đúng bóng có điểm cao nhất trong Key 5.
  - Kiểm tra `generate_key_banker_tickets` sinh đúng 6 vé con, **100% các vé đều chứa bóng chốt**, các bóng vệ tinh không trùng bóng chốt.
  - Kiểm tra mọi vé con đều thỏa mãn $AC \ge 7$ (hoặc $\ge 4$ cho 5/35) và tổng trong khoảng chuẩn.
  - Kiểm tra tính tất định 100% với cùng seed.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_banker_wheeling.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/banker_wheeling.py`**
  - Hiện thực hàm chọn bóng chốt Bạch Thủ $B_1$.
  - Hiện thực ma trận phủ vệ tinh kết hợp bóng chốt $B(1, 10, k, 3)$ và lọc không gian âm $AC \ge 7$.
  - Hiện thực hàm kiểm định Walk-Forward đo tỷ lệ ăn giải khi có bóng chốt.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_banker_wheeling.py -v`

---

### Task 3: Tích Hợp Vào `ensemble_engine.py` & Kiểm Thử Tích Hợp

**Files:**
- Modify: `src/vietlott/model/ensemble_engine.py`
- Create: `src/vietlott/tests/test_elimination_banker_integration.py`

**Interfaces:**
- Consumes: `prune_dead_numbers` từ `elimination_engine`, `generate_key_banker_tickets` từ `banker_wheeling`.
- Produces: Bổ sung `elimination_analytics` và `banker_wheeling` vào payload `consensus_hub`.

- [ ] **Step 1: Viết test kiểm thử tích hợp trong `test_elimination_banker_integration.py`**
  - Kiểm tra `consensus_hub` chứa trường `elimination_analytics` với danh sách bóng bị loại và lý do.
  - Kiểm tra `consensus_hub.tickets` chứa trường `banker_wheeling` với bóng chốt và 6 vé bọc lót.
  - Kiểm tra trên cả 3 game: Power 6/55, Mega 6/45, Power 5/35.
  - Kiểm tra bảo toàn 100% tính tương thích ngược của schema cũ.

- [ ] **Step 2: Cập nhật `src/vietlott/model/ensemble_engine.py`**
  - Trong `calculate_multi_model_consensus_and_backtest`:
    - Tính toán điểm nguy cơ và đào thải bóng chết $\implies$ Đưa vào `"elimination_analytics"`.
    - Lọc sạch Core Pool không chứa bóng chết.
    - Sinh Dàn Bọc Lót Có Bóng Chốt $\implies$ Đưa vào `"banker_wheeling"`.
    - Bảo toàn toàn bộ các trường hiện hữu khác.

- [ ] **Step 3: Chạy test kiểm thử tích hợp**
  `pytest src/vietlott/tests/test_elimination_banker_integration.py -v`

---

### Task 4: Cập Nhật Giao Diện Web, Render Dữ Liệu Thật & Cập Nhật Tài Liệu

**Files:**
- Modify: `docs/assets/js/consensus_ensemble.js` & `assets/js/consensus_ensemble.js`
- Modify: `docs/index.html` & `index.html`
- Run: `python -m src.vietlott.render_web_data`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

- [ ] **Step 1: Cập nhật giao diện Web `consensus_ensemble.js` & `index.html`**
  - Bổ sung container `#consensusEliminationAnalytics` và `#consensusBankerWheeling`.
  - Hiển thị widget **"Bộ Lọc Đào Thải Bóng Chết (Dead Numbers Pruning)"**: Danh sách các bóng bị loại bỏ (màu xám gạch chéo), nhãn lý do (Ngủ đông / Kỵ nhau / Gan lì), tỷ lệ thu hẹp không gian số và độ chính xác đào thải lịch sử ($\ge 90\%$).
  - Hiển thị widget **"Dàn Bọc Lót Bạch Thủ Chốt (Key-Banker Wheeling)"**: Nổi bật bóng chốt Bạch Thủ (vàng kim phát sáng), danh sách 6 vé bọc lót và cam kết bảo hiểm khi bóng chốt nổ.
  - Đồng bộ song song `docs/` và root.

- [ ] **Step 2: Chạy pipeline render dữ liệu thực tế**
  - Chạy `python -m src.vietlott.render_web_data`.
  - Xác nhận tạo thành công `vietlott_summary.json` có đủ 2 trường mới trên cả 3 game.

- [ ] **Step 3: Cập nhật tài liệu kiến trúc kỹ thuật (Zero Drift Policy)**
  - Thêm Mục 17 (Bộ lọc đào thải bóng chết) và Mục 18 (Dàn bọc lót có bóng chốt) vào `docs/architecture/MATHEMATICAL_MODELS.md`.
  - Cập nhật `SYSTEM_ARCHITECTURE.md`.

- [ ] **Step 4: Chạy toàn bộ pytest suite**
  `pytest src/vietlott/tests/ -v` (Đảm bảo 125+ bài test PASS 100%).
