# Markowitz Portfolio Ticket Optimization & Kelly Bankroll Advisor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai Thuật toán Tối ưu hóa Danh mục Vé Markowitz bậc hai có ràng buộc (Covariance Penalty & Phân bổ Đa cụm Louvain $\ge 4$) cho vé Golden Ticket, xây dựng Động cơ Quản trị Vốn Kelly với Chỉ số Tự tin Đồng thuận (Consensus Conviction Score - CCS) 3 cấp độ, tích hợp vào pipeline dữ liệu và giao diện Web với 100% Zero Mock Data.

**Architecture:**
- `src/vietlott/model/portfolio_optimizer.py`: Giải bài toán tối ưu bậc hai $\max \left( \sum x_i \mu_i - \lambda \sum \sum x_i x_j \Sigma_{ij} \right)$ với các ràng buộc cứng: $AC \ge 7$ (hoặc $\ge 4$ cho 5/35), chuông Gaussian $90\%$, số cụm Louvain $\ge 4$ (tối đa 2 bóng/cụm).
- `src/vietlott/model/bankroll_advisor.py`: Tính toán chỉ số CCS ($0 - 100\%$) dựa trên độ đồng thuận 8 mô hình, độ dốc entropy xác suất, và xung lực kéo liên kỳ $A \to B$. Xuất khuyến nghị phân bổ vốn 3 cấp độ (10k, 20k, 60k).
- `src/vietlott/model/ensemble_engine.py`: Tích hợp Markowitz Optimizer vào hàm sinh vé Golden và gọi Bankroll Advisor xuất `bankroll_advisory`.
- `docs/assets/js/consensus_ensemble.js`: Widget hiển thị "Khuyến Nghị Quản Trị Vốn Kỳ Này" (đồng hồ CCS, badge khuyến nghị) và chi tiết phân bổ cụm Louvain trên vé Golden.

**Tech Stack:** Python 3.11+, NumPy, Scikit-Learn, pytest, vanilla JS.

**Spec:** `docs/superpowers/specs/2026-09-08-markowitz-portfolio-kelly-bankroll-design.md`

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md Non-Negotiable Law).
- 100% các con số và chỉ số phân bổ vốn được tính toán thực tế từ dữ liệu quay thưởng lịch sử.
- Bảo toàn 100% tính tương thích ngược của schema JSON (`vietlott_summary.json`).
- Không thêm dependency bên ngoài (thuần NumPy và thư viện có sẵn trong `.venv`).

---

### Task 1: Xây dựng Module Tối Ưu Hóa Danh Mục Markowitz (`portfolio_optimizer.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/portfolio_optimizer.py`
- Create: `src/vietlott/tests/test_portfolio_optimizer.py`

**Interfaces:**
- Produces:
  - `build_pairwise_covariance_proxy(records: List[Dict], max_val: int, num_balls: int, window_len: int = 150) -> np.ndarray` (ma trận hiệp phương sai $N \times N$)
  - `extract_louvain_communities(records: List[Dict], max_val: int, num_balls: int, window_len: int = 150) -> Dict[int, int]` (ánh xạ bóng $\to$ mã cụm $0 \dots K-1$)
  - `optimize_markowitz_ticket(candidate_scores: Dict[int, float], cov_matrix: np.ndarray, louvain_clusters: Dict[int, int], max_val: int, num_balls: int, target_sum: int, sum_range: Tuple[int, int], min_ac: int, risk_lambda: float = 0.30, seed: int = 42) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_portfolio_optimizer.py`**
  - Kiểm tra ma trận hiệp phương sai tương quan đối xứng, đường chéo chính bằng 0.
  - Kiểm tra thuật toán phân cụm Louvain gán đủ nhãn cụm cho mọi bóng từ 1 đến `max_val`.
  - Kiểm tra vé tối ưu Markowitz:
    - Đúng số lượng bóng $k$ ($k=6$ hoặc $5$).
    - Thỏa mãn $AC \ge 7$ (với 6/55, 6/45) hoặc $AC \ge 4$ (với 5/35).
    - Thỏa mãn tổng nằm trong `sum_range`.
    - Trải đều trên ít nhất 4 cụm Louvain khác nhau, không cụm nào quá 2 bóng.
    - Điểm kỳ vọng trừ phạt rủi ro lớn hơn chọn ngẫu nhiên.
  - Kiểm tra tính tất định 100% với cùng seed.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_portfolio_optimizer.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/portfolio_optimizer.py`**
  - Hiện thực `build_pairwise_covariance_proxy` trên cửa sổ 150 kỳ.
  - Hiện thực thuật toán phân cụm đồ thị Louvain modularity thuần NumPy.
  - Hiện thực thuật toán duyệt tối ưu có ràng buộc Combinatorial Beam Search tìm $\mathbf{x}^*$.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_portfolio_optimizer.py -v`

---

### Task 2: Xây dựng Module Quản Trị Vốn Kelly (`bankroll_advisor.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/bankroll_advisor.py`
- Create: `src/vietlott/tests/test_bankroll_advisor.py`

**Interfaces:**
- Produces:
  - `calculate_consensus_conviction_score(models_info: Dict[str, Any], top_candidates_per_model: Dict[str, List[int]], consensus_scores: Dict[int, float], transition_analytics: Dict[str, Any], num_balls: int) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_bankroll_advisor.py`**
  - Kiểm tra điểm CCS luôn nằm trong khoảng $[0.0, 100.0\%]$.
  - Kiểm tra phân loại chính xác 3 cấp độ:
    - Cấp 1 ($\text{CCS} < 55$): Ngân sách 10.000đ, hành động thăm dò/tạm dừng.
    - Cấp 2 ($55 \le \text{CCS} < 75$): Ngân sách 20.000đ, hành động Golden + Triad.
    - Cấp 3 ($\text{CCS} \ge 75$): Ngân sách 60.000đ, hành động Dàn bọc lót 6 vé $C(12, 6, 3)$.
  - Kiểm tra xử lý ca biên (không có luật kéo bóng, dữ liệu bằng phẳng).
  - Kiểm tra tính tất định 100%.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_bankroll_advisor.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/bankroll_advisor.py`**
  - Hiện thực tính toán $S_{\text{agreement}}$, $S_{\text{entropy}}$, $S_{\text{pull}}$.
  - Tính điểm $\text{CCS} = 0.40 S_{\text{agreement}} + 0.35 S_{\text{entropy}} + 0.25 S_{\text{pull}}$.
  - Đóng gói đầy đủ các trường: `ccs_score`, `tier_level`, `tier_name`, `tier_badge`, `recommended_action`, `recommended_budget`, `breakdown`, `rationale`.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_bankroll_advisor.py -v`

---

### Task 3: Tích Hợp Vào `ensemble_engine.py` & Kiểm Thử Tích Hợp

**Files:**
- Modify: `src/vietlott/model/ensemble_engine.py`
- Modify: `src/vietlott/render_web_data.py`
- Create: `src/vietlott/tests/test_portfolio_bankroll_integration.py`

**Interfaces:**
- Consumes: `optimize_markowitz_ticket` từ `portfolio_optimizer`, `calculate_consensus_conviction_score` từ `bankroll_advisor`.
- Produces: Cập nhật vé `golden` với siêu dữ liệu Markowitz và bổ sung `bankroll_advisory` trong `consensus_hub`.

- [ ] **Step 1: Viết test kiểm thử tích hợp trong `test_portfolio_bankroll_integration.py`**
  - Kiểm tra `calculate_multi_model_consensus_and_backtest` xuất trường `bankroll_advisory` hợp lệ.
  - Kiểm tra vé `golden` có các trường `optimization_type = "Markowitz Constrained Portfolio"`, `louvain_spread`, `expected_return`, `covariance_risk_penalty`.
  - Kiểm tra trên cả 3 game: Power 6/55, Mega 6/45, Power 5/35.
  - Kiểm tra 100% tương thích ngược schema JSON.

- [ ] **Step 2: Cập nhật `src/vietlott/model/ensemble_engine.py`**
  - Trong `calculate_multi_model_consensus_and_backtest`:
    - Trích xuất ma trận hiệp phương sai và cụm Louvain.
    - Gọi `optimize_markowitz_ticket` sinh vé Golden.
    - Gọi `calculate_consensus_conviction_score` sinh `bankroll_advisory`.
    - Đưa vào payload trả về.

- [ ] **Step 3: Chạy test kiểm thử tích hợp**
  `pytest src/vietlott/tests/test_portfolio_bankroll_integration.py -v`

---

### Task 4: Cập Nhật Giao Diện Web, Render Dữ Liệu Thật & Cập Nhật Tài Liệu

**Files:**
- Modify: `docs/assets/js/consensus_ensemble.js` (và `assets/js/consensus_ensemble.js`)
- Modify: `docs/index.html` (và `index.html`)
- Run: `python -m src.vietlott.render_web_data`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

- [ ] **Step 1: Cập nhật giao diện Web `consensus_ensemble.js` & `index.html`**
  - Thêm thẻ widget trực quan **"Khuyến Nghị Quản Trị Vốn Kỳ Này (Kelly Bankroll Advisory)"**:
    - Đồng hồ đo CCS ($0 - 100\%$) kèm thanh tiến trình trực quan.
    - Badge cấp độ hành động nhấp nháy (Cấp 1: Xám, Cấp 2: Xanh dương, Cấp 3: Xanh ngọc phát sáng).
    - Ngân sách vốn đề xuất (10k / 20k / 60k) và giải trình định lượng.
  - Cập nhật hiển thị vé Golden: Thêm badge *"Markowitz Constrained Portfolio"* và hiển thị phân bổ 4 cụm Louvain.

- [ ] **Step 2: Chạy pipeline render dữ liệu thực tế**
  - Chạy `python -m src.vietlott.render_web_data`.
  - Xác nhận tạo thành công `vietlott_summary.json` có đủ `bankroll_advisory` và vé Golden Markowitz trên cả 3 sản phẩm.

- [ ] **Step 3: Cập nhật tài liệu kiến trúc kỹ thuật (Zero Drift Policy)**
  - Cập nhật Mục 2 trong `docs/architecture/MATHEMATICAL_MODELS.md` (Tối ưu hóa Markowitz).
  - Bổ sung Mục 16 trong `docs/architecture/MATHEMATICAL_MODELS.md` (Đặc tả Quản trị vốn Kelly & chỉ số CCS).
  - Cập nhật `SYSTEM_ARCHITECTURE.md` với 2 module mới `portfolio_optimizer.py` và `bankroll_advisor.py`.

- [ ] **Step 4: Chạy toàn bộ pytest suite**
  `pytest src/vietlott/tests/ -v` (Đảm bảo 95+ bài test PASS 100%).
