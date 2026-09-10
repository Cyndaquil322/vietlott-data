# TÀI LIỆU THIẾT KẾ KỸ THUẬT: TÍCH HỢP MÔ HÌNH ĐỒ THỊ PAGERANK, BỘ LỌC KALMAN VÀ THU GỌN HỆ THỐNG VIETLOTT ANALYTICS
**Ngày lập:** 2026-09-08  
**Trạng thái:** Đã phê duyệt ý tưởng (Approved Design)  
**Phân loại:** Kiến trúc hệ thống & Mô hình toán học (Architectural Design)  
**Tác giả:** Antigravity AI Pair Programmer & Người Dùng

---

## 1. Mục Tiêu Tổng Thể (Executive Summary)
1. **Nâng cấp mô hình tiên tiến nhất (Advanced Mathematical Modeling):**
   - Tích hợp 2 mô hình toán học - thống kê mạng lưới mới:
     - **Graph Co-occurrence & PageRank Centrality:** Nhận diện các tâm điểm hút bóng (Attractor Nodes) và cụm liên kết chặt chẽ (Cliques) trong không gian xác suất có điều kiện.
     - **Bayesian Dynamic State-Space Filter (Kalman Dynamic Drift):** Theo dõi xung lực xuất hiện tiềm ẩn của từng quả bóng theo thời gian thực, phản ứng cực nhạy với chuyển pha nhịp nổ mà không bị trễ pha.
   - Nâng cấp hệ thống Ensemble từ 5 mô hình lên **7 mô hình dự đoán độc lập**, chạy kiểm định **Walk-Forward 100 kỳ gần nhất** tuân thủ nguyên tắc **Zero Mock Data**.
2. **Thu gọn & Mô-đun hóa hệ thống (Architecture Consolidation):**
   - Giải phóng file monolithic [`src/vietlott/render_web_data.py`](file:///d:/Projects/vietlott-data-master/src/vietlott/render_web_data.py) (2.465 dòng) thành các module chuyên biệt, độc lập trong `src/vietlott/model/`:
     - `analytic_engines.py`: Thư viện chứa 7 mô hình toán học thuần túy (Pure NumPy, không phụ thuộc thư viện ngoài).
     - `ensemble_engine.py`: Động cơ tổng hợp Dynamic Alpha Stacking, Walk-Forward 100 kỳ, và trích xuất vé số học (Triad, Key 5, Core Pool, Wheeling 4 vé, Bao 7 Pareto).
     - `covering_engine.py`: Giữ nguyên vẹn các thuật toán bao toán học đã kiểm định thành công.
   - File `render_web_data.py` rút gọn xuống ~400 dòng, chỉ đóng vai trò Data Pipeline Orchestrator & Serializer.
   - Gom gọn thư mục `strategy/` cũ để loại bỏ hoàn toàn mã nguồn thừa hoặc gây nhầm lẫn.
3. **Bảo toàn 100% tính tương thích ngược (Zero Schema Drift):**
   - Không làm thay đổi bất kỳ khóa dữ liệu nào trong `vietlott_summary.json`. Web UI hiển thị hoàn toàn bình thường và tự động mở rộng thêm thông tin phân tích mô hình mới.

---

## 2. Nền Tảng Toán Học & Định Lượng (Mathematical Specifications)

### 2.1. Mô Hình 1: Mạng Đồ Thị Tương Hỗ & Trung Tâm Lực Hút (Graph Co-occurrence PageRank Centrality)
- **Cơ sở lý thuyết:** Các con số trong xổ số không hoàn toàn độc lập trong ngắn hạn mà tương tác qua các cặp nổ cùng nhau (co-occurrences). Ta mô hình hóa không gian quay số thành một đồ thị vô hướng có trọng số $G = (V, E)$ với $V = \{1, \dots, N\}$.
- **Ma trận kề có trọng số (Adjacency Matrix $A$):**
  Cho một cửa sổ trượt $W = 100$ kỳ gần nhất:
  $$A_{ij} = \begin{cases} \max\left(0, \text{Lift}^*(i, j) - 1.0\right) & \text{với } i \ne j \\ 0 & \text{với } i = j \end{cases}$$
  trong đó $\text{Lift}^*(i, j) = \frac{C(i, j) + \alpha \cdot P_0}{C(i) + \alpha} \cdot \frac{1}{P_0}$ với hệ số làm mịn Dirichlet/Laplace $\alpha = 1.0$.
- **Chuẩn hóa Stochastic Matrix $M$:**
  $$M_{ij} = \frac{A_{ij}}{\sum_{k=1}^N A_{ik} + \epsilon}$$
- **Thuật toán Power Iteration tìm PageRank Centrality:**
  Khởi tạo $p^{(0)} = \left[\frac{1}{N}, \dots, \frac{1}{N}\right]^T$.
  Lặp với hệ số tắt dần (damping factor) $d = 0.85$:
  $$p^{(t+1)} = d \cdot M^T p^{(t)} + \frac{1 - d}{N} \mathbf{1}$$
  Điều kiện dừng: $\|p^{(t+1)} - p^{(t)}\|_1 < 10^{-6}$ (hội tụ trong 15–20 bước lặp ma trận).
- **Chuẩn hóa điểm số:** Điểm số đầu ra của bóng $b$ được chuẩn hóa $\text{Score}_{\text{graph}}(b) = \frac{p(b)}{\max_{i} p(i)}$.

### 2.2. Mô Hình 2: Bộ Lọc Trạng Thái Tiềm Ẩn (Bayesian Dynamic State-Space Filter)
- **Cơ sở lý thuyết:** Xung lực xuất hiện của bóng $b$ tại kỳ $t$ được mô hình hóa như một biến trạng thái tiềm ẩn $x_t(b) \in \mathbb{R}$. Quan sát thực tế $y_t(b) \in \{0, 1\}$ (bóng có nổ hay không).
- **Phương trình hệ thống (State-Space Formulation):**
  - **Phương trình chuyển trạng thái:** $x_t = \lambda \cdot x_{t-1} + (1 - \lambda) \cdot \mu_0 + w_t$, với $w_t \sim \mathcal{N}(0, Q)$.
    - $\lambda = 0.92$ (hệ số nhớ trạng thái).
    - $\mu_0 = \frac{k}{N}$ (xác suất cơ sở lý thuyết).
    - $Q = 0.05$ (phương sai nhiễu nội tại).
  - **Phương trình quan sát:** $y_t = x_t + v_t$, với $v_t \sim \mathcal{N}(0, R)$.
    - $R = 0.5$ (phương sai nhiễu đo lường nhị phân).
- **Thuật toán lọc Kalman cập nhật qua chuỗi lịch sử:**
  Tại mỗi bước kỳ quay $t = 1 \dots T$:
  1. *Dự báo trạng thái trước:* $\hat{x}_t = \lambda x_{t-1} + (1 - \lambda) \mu_0$
  2. *Dự báo phương sai sai số:* $P_t^- = \lambda^2 P_{t-1} + Q$
  3. *Tính toán độ lợi Kalman:* $K_t = \frac{P_t^-}{P_t^- + R}$
  4. *Cập nhật trạng thái sau quan sát:* $x_t = \hat{x}_t + K_t (y_t - \hat{x}_t)$
  5. *Cập nhật phương sai:* $P_t = (1 - K_t) P_t^-$
- **Dự báo cho kỳ tiếp theo $T+1$:**
  $$\hat{x}_{T+1}(b) = \lambda x_T(b) + (1 - \lambda) \mu_0$$
  Chuẩn hóa điểm số: $\text{Score}_{\text{state}}(b) = \max\left(0, \frac{\hat{x}_{T+1}(b) - \min_i \hat{x}_{T+1}(i)}{\max_i \hat{x}_{T+1}(i) - \min_i \hat{x}_{T+1}(i) + \epsilon}\right)$.

### 2.3. Dynamic Alpha Stacking & Ensemble Tổng Hợp 7 Mô Hình
Tập hợp 7 mô hình tham gia đồng thuận:
$$\mathcal{M} = \{\text{hazard}, \text{decay}, \text{markov}, \text{fourier}, \text{wavelet}, \text{graph\_pagerank}, \text{state\_space}\}$$
- Tại kỳ $T$, chạy kiểm định Walk-Forward 100 kỳ gần nhất: với mỗi kỳ $t \in [T-100, T-1]$, mỗi mô hình $m \in \mathcal{M}$ dự đoán top $k$ bóng chỉ dựa trên dữ liệu $[1 \dots t-1]$.
- Tính toán độ chính xác Out-Of-Fold $\text{Hits}_{100}(m)$ và tỷ lệ trúng $\ge 3$ số.
- Tính trọng số thích ứng Softmax bình phương theo Out-Of-Fold Alpha:
  $$w_m = \frac{\exp\left(2.5 \cdot \alpha_m\right)}{\sum_{j \in \mathcal{M}} \exp\left(2.5 \cdot \alpha_j\right)}$$
  trong đó $\alpha_m = \frac{\text{Hits}_{100}(m) - \text{Baseline}(k)}{\text{Baseline}(k)}$.
- Phân bổ điểm đồng thuận bằng Soft-Exponential Rank Conviction:
  $$\text{ConsensusScore}(b) = \sum_{m \in \mathcal{M}} w_m \cdot \exp\left(-0.075 \cdot \text{Rank}_{b, m}\right)$$

---

## 3. Kiến Trúc Phân Rã & Tái Cấu Trúc Hệ Thống (Structural Decomposition)

### 3.1. Cấu Trúc Thư Mục Mới
```
d:\Projects\vietlott-data-master\src\vietlott\
│
├── model/
│   ├── __init__.py
│   ├── analytic_engines.py      # [NEW] 7 mô hình toán học độc lập
│   ├── ensemble_engine.py       # [NEW] Dynamic Alpha Stacking & Walk-Forward Backtester
│   ├── covering_engine.py       # [EXISTING] Bao thu gọn 4 vé & Bao 7 Pareto
│   ├── wavelet_engine.py        # [EXISTING] Biến đổi sóng con Daubechies DWT
│   └── legacy_strategies/       # [CONSOLIDATED] Archive các strategy cũ
│
├── render_web_data.py           # [REFACTORED] Giảm từ 2.465 dòng xuống ~400 dòng
├── auto_draw_monitor.py         # Giữ nguyên
├── sync_live_data.py            # Giữ nguyên
└── tests/
    ├── test_analytic_engines.py # [NEW] Unit test cho Graph PageRank & Kalman Filter
    ├── test_covering_engine.py  # Giữ nguyên
    ├── test_wavelet_engine.py   # Giữ nguyên
    ├── test_production_core.py  # Kiểm định toàn vẹn pipeline
    └── test_crawler/            # Giữ nguyên
```

### 3.2. Chi Tiết Các Module Mới

#### `src/vietlott/model/analytic_engines.py`
Mô-đun chứa các hàm thuần túy tính toán điểm dự báo cho tập bóng $\{1 \dots \text{max\_val}\}$:
- `calculate_bayesian_hazard_scores(records, max_val, num_balls) -> Dict[int, float]`
- `calculate_exponential_decay_scores(records, max_val, num_balls) -> Dict[int, float]`
- `calculate_markov_ppmi_scores(records, max_val, num_balls) -> Dict[int, float]`
- `calculate_fourier_spectral_scores(records, max_val, num_balls) -> Dict[int, float]`
- `calculate_empirical_bayes_lift_scores(records, max_val, num_balls) -> Dict[int, float]`
- `calculate_graph_pagerank_scores(records, max_val, num_balls, damping=0.85, max_iter=50) -> Dict[int, float]`
- `calculate_state_space_scores(records, max_val, num_balls, decay=0.92) -> Dict[int, float]`

#### `src/vietlott/model/ensemble_engine.py`
Chịu trách nhiệm toàn bộ logic đồng thuận và đối soát quá khứ:
- `calculate_multi_model_consensus_and_backtest(records, product_key, max_val, num_balls, has_special, backtest_draws=100) -> Dict[str, Any]`
- Điều phối sinh các tổ hợp vé:
  - Top 3 Kiềng 3 chân
  - Ngũ thủ (Key 5)
  - Dàn hạt nhân 10–12 số
  - Bao thu gọn 4 vé (Covering 4)
  - Bộ 7 số tối ưu (Optimal Septet / Bao 7 Pareto)
- Đảm bảo gieo mầm cố định theo mã kỳ quay (`Draw ID Seed`).

#### `src/vietlott/render_web_data.py`
Thu gọn trở thành pipeline orchestrator:
- Đọc dữ liệu JSONL thô từ `data/`.
- Tính toán các bảng thống kê bề mặt: `gap_analysis`, `cooccurrence`, `sum_and_patterns`, `positional_stats`, `ac_stats`, `delta_stats`, `digit_dynamics`, `ev_metrics`.
- Gọi `ensemble_engine.calculate_multi_model_consensus_and_backtest(...)`.
- Tạo cấu trúc JSON hoàn chỉnh và lưu vào `data/vietlott_summary.json` và `docs/data/vietlott_summary.json`.

---

## 4. Tương Thích Giao Diện & Schema Dữ Liệu (Frontend Compatibility)

### 4.1. Schema JSON (`docs/data/vietlott_summary.json`)
Cấu trúc `consensus_hub` được giữ nguyên vẹn:
```json
{
  "consensus_hub": {
    "generated_at": "...",
    "product_key": "power_655",
    "target_draw": 1396,
    "models": {
      "hazard": { "name": "Chu Kỳ Nhịp Sinh Học Gauss", "avg_hits": 0.71, "win_rate_ge3": 0.02, "weight": 0.15 },
      "decay": { "name": "Động Lượng Suy Giảm Thời Gian", "avg_hits": 0.70, "win_rate_ge3": 0.02, "weight": 0.14 },
      "markov": { "name": "Xích Markov Nhị Phân PPMI", "avg_hits": 0.75, "win_rate_ge3": 0.04, "weight": 0.18 },
      "fourier": { "name": "Phổ Dao Động Hann Fourier", "avg_hits": 0.72, "win_rate_ge3": 0.03, "weight": 0.15 },
      "wavelet": { "name": "Sóng Con Daubechies DWT", "avg_hits": 0.73, "win_rate_ge3": 0.03, "weight": 0.16 },
      "graph_pagerank": { "name": "Mạng Đồ Thị PageRank (Hubs)", "avg_hits": 0.76, "win_rate_ge3": 0.04, "weight": 0.19 },
      "state_space": { "name": "Bộ Lọc Trạng Thái Kalman", "avg_hits": 0.74, "win_rate_ge3": 0.03, "weight": 0.17 }
    },
    "ranked_balls": [ ... ],
    "tickets": {
      "consensus_ticket": [ ... ],
      "triad_anchor": [ ... ],
      "key_5_balls": [ ... ],
      "core_pool_12": [ ... ],
      "wheeling_4_tickets": [ ... ],
      "optimal_septet": [ ... ]
    },
    "audit_history": [ ... ]
  }
}
```

### 4.2. Giao Diện Người Dùng (`docs/assets/js/consensus_ensemble.js`)
- Bảng hiển thị mô hình tự động render danh sách các mô hình trong `hub.models`.
- Bổ sung định dạng màu sắc cho 2 mô hình mới:
  - `graph_pagerank`: Tag màu Cyan/Teal (`bg-cyan-500/10 text-cyan-300 border-cyan-500/20`).
  - `state_space`: Tag màu Rose/Pink (`bg-rose-500/10 text-rose-300 border-rose-500/20`).

---

## 5. Chiến Lược Kiểm Thử & Nghiệm Thu (Verification Plan)

### 5.1. Unit Tests (`pytest`)
- Tạo file `src/vietlott/tests/test_analytic_engines.py`:
  - `test_graph_pagerank_scores_properties`: Xác nhận điểm số không âm, không NaN, tính đối xứng ma trận kề, hội tụ đúng chuẩn.
  - `test_state_space_scores_properties`: Xác nhận độ thích ứng của bộ lọc Kalman khi chuỗi bóng nổ dồn dập hoặc im lìm.
  - `test_determinism`: Khẳng định 100% kết quả tính toán độc lập với thời gian thực thi, cùng input cho ra cùng output.
- Chạy toàn bộ 54+ tests hiện có để bảo đảm zero regressions.

### 5.2. Pipeline Integration & Performance Test
- Chạy `python src/vietlott/render_web_data.py`:
  - Đo thời gian thực thi: Mục tiêu toàn bộ quá trình đọc dữ liệu, tính 7 mô hình và chạy 100 kỳ Walk-Forward cho cả 3 sản phẩm hoàn thành trong < 15 giây.
  - Kiểm tra dung lượng file JSON: ~750KB (gọn nhẹ, truyền tải web nhanh).
  - Chạy `test_production_core.py` xác nhận schema hợp lệ.

### 5.3. Playwright Headless Browser Audit
- Khởi chạy web server nội bộ và mở `http://localhost:8088`.
- Kiểm tra console: **0 errors**.
- Kiểm tra hiển thị bảng mô hình 7 thuật toán và thẻ Bao 7 Pareto trên cả 3 game: Power 6/55, Mega 6/45, Power 5/35.
- Chụp ảnh màn hình bằng chứng nghiệm thu thực tế.
