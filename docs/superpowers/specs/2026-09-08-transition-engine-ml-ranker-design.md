# TÀI LIỆU THIẾT KẾ KỸ THUẬT: ĐỘNG CƠ CHUYỂN TRẠNG THÁI LIÊN KỲ (A -> B) VÀ HỌC MÁY XẾP HẠNG (LEARNING-TO-RANK)

**Ngày lập:** 2026-09-08  
**Trạng thái:** Bản thiết kế hoàn chỉnh (Complete Design Specification)  
**Phân loại:** Kiến trúc Hệ thống & Học máy Định lượng (Machine Learning & Architectural Design)  
**Tác giả:** Antigravity AI Pair Programmer & Người Dùng  

---

## 1. Mục Tiêu Tổng Thể (Executive Summary)

1. **Khai phá & Mô hình hóa Lực kéo Liên kỳ ($A \to B$):**
   - Xây dựng module `src/vietlott/model/transition_engine.py` tự động khai phá toàn bộ lịch sử quay thưởng để phát hiện các quy luật chuyển trạng thái từ quả bóng $A$ ở kỳ trước sang quả bóng $B$ ở kỳ sau ($A_{t-1} \to B_t$).
   - Đánh giá tính xác thực thống kê qua 4 chỉ số: Xác suất có điều kiện $P(B \mid A)$, Độ nâng xác suất $\text{Lift}(A \to B)$, Độ lệch chuẩn nhị thức $Z$-score, và Lực kỵ nhau/triệt tiêu ($\text{Lift} < 0.5$, $Z \le -2.0$).
   - Tính toán **Trường lực hấp dẫn Vector (Vector Field Pull)** từ tập 5–6 bóng nổ của kỳ trước tác động lên từng bóng tiềm năng của kỳ sau.

2. **Học Máy Xếp Hạng Đa Nhân Tố (Machine Learning Learning-to-Rank):**
   - Xây dựng module `src/vietlott/model/ml_ranker.py` sử dụng thuật toán `HistGradientBoostingClassifier` từ thư viện `scikit-learn` (đã có sẵn trong môi trường, zero-dependency).
   - Huấn luyện theo nguyên tắc **Walk-Forward Rolling Window 100 kỳ** (tại kỳ $T$ chỉ học từ dữ liệu $\le T-1$, tuyệt đối không nhìn trước tương lai).
   - Học phi tuyến tính trên **vector đặc trưng 14 chiều** (kết hợp 7 mô hình toán học hiện tại + 4 đặc trưng liên kỳ $A \to B$ + 3 đặc trưng số học/cụm) để dự báo xác suất và xếp hạng tối ưu 55 quả bóng.

3. **Tích hợp Pipeline & Trực quan hóa Giao diện Web:**
   - Tích hợp kết quả vào `src/vietlott/model/ensemble_engine.py` và `render_web_data.py`.
   - Xuất thêm cấu trúc `transition_analytics` trong `vietlott_summary.json` hiển thị:
     - Top luật kéo bóng mạnh nhất từ kết quả kỳ trước.
     - Top luật kỵ nhau cần tránh.
   - Cập nhật giao diện `docs/assets/js/consensus_ensemble.js` với widget trực quan **"Bản đồ Lực Hút Liên Kỳ ($A \to B$)"**.

4. **Tuân thủ Tuyệt đối Các Nguyên Tắc Bất Di Bất Dịch:**
   - **Zero Mock Data:** 100% kết quả đối soát và dự đoán xuất phát từ dữ liệu thật và thuật toán Walk-Forward.
   - **Zero Drift Policy:** Đồng bộ tuyệt đối tài liệu kiến trúc kỹ thuật (`MATHEMATICAL_MODELS.md`, `SYSTEM_ARCHITECTURE.md`).
   - **Backwards Compatibility:** Giữ nguyên vẹn toàn bộ các khóa JSON hiện có của `vietlott_summary.json`.

---

## 2. Nền Tảng Toán Học & Định Lượng (Mathematical Specifications)

### 2.1. Ma Trận Chuyển Trạng Thái & Kiểm Định Ý Nghĩa Thống Kê
Cho chuỗi lịch sử gồm $T$ kỳ quay liên tiếp. Gọi $S_{t-1}$ là tập các con số trúng thưởng tại kỳ $t-1$ và $S_t$ là tập các con số trúng thưởng tại kỳ $t$.

Với mỗi cặp số $(A, B) \in [1, N] \times [1, N]$:
1. **Số lần bóng $A$ xuất hiện ở kỳ trước:**
   $$N_A = \sum_{t=1}^{T-1} \mathbb{I}(A \in S_t)$$
2. **Số lần chuyển tiếp đồng thời $(A_{t-1} \to B_t)$:**
   $$N_{AB} = \sum_{t=1}^{T-1} \mathbb{I}(A \in S_t \land B \in S_{t+1})$$
3. **Xác suất có điều kiện thực nghiệm:**
   $$P(B_t \mid A_{t-1}) = \frac{N_{AB}}{\max(1, N_A)}$$
4. **Kỳ vọng xuất hiện ngẫu nhiên độc lập:**
   $$E_{AB} = N_A \cdot P_0(B) = N_A \cdot \frac{N_B}{T-1}$$
5. **Độ nâng xác suất (Transition Lift):**
   $$\text{Lift}(A \to B) = \frac{P(B_t \mid A_{t-1})}{P_0(B)} = \frac{N_{AB}}{E_{AB} + \epsilon}$$
   - Nếu $\text{Lift}(A \to B) \ge 1.5$: Lực kéo đồng quy liên kỳ mạnh mẽ.
   - Nếu $\text{Lift}(A \to B) \le 0.5$: Lực kỵ nhau/đẩy nhau liên kỳ (Repulsive pair).
6. **Kiểm định độ lệch chuẩn nhị thức ($Z$-score):**
   $$Z(A \to B) = \frac{N_{AB} - E_{AB}}{\sqrt{N_A \cdot P_0(B) \cdot (1 - P_0(B)) + \epsilon}}$$
   - Mối liên hệ có ý nghĩa thống kê thực sự khi $|Z(A \to B)| \ge 2.0$ ($p\text{-value} < 0.05$).

---

### 2.2. Trường Lực Hấp Dẫn Vector (Vector Field Pull)
Tại kỳ quay hiện tại $T$, kết quả kỳ trước đã biết là tập $S_{T-1} = \{a_1, a_2, \dots, a_k\}$.  
Đối với mỗi quả bóng ứng viên $b \in [1, N]$ cho kỳ quay kế tiếp $T$:

1. **Lực kéo cực đại (Max Pull Lift):**
   $$\text{Pull}_{\max}(b) = \max_{a \in S_{T-1}} \text{Lift}(a \to b)$$
2. **Tổng hợp xung lực ý nghĩa (Sum Significant Z-Scores):**
   $$\text{Pull}_{Z}(b) = \sum_{a \in S_{T-1}} \max(0.0, Z(a \to b))$$
3. **Lực kỵ nhau/triệt tiêu (Repulsion Penalty):**
   $$\text{Penalty}_{\text{rep}}(b) = \min_{a \in S_{T-1}} \text{Lift}(a \to b)$$
   (Nếu $\text{Penalty}_{\text{rep}}(b) < 0.5$, bóng $b$ chịu lực triệt tiêu mạnh từ ít nhất một bóng của kỳ trước).
4. **Động lượng Cầu Rơi (Repeat Momentum):**
   $$\text{Momentum}_{\text{repeat}}(b) = \begin{cases} \text{Lift}(b \to b) & \text{nếu } b \in S_{T-1} \\ 0.0 & \text{ngược lại} \end{cases}$$

---

### 2.3. Không Gian Vector Đặc Trưng 14 Chiều (Feature Space)
Mô hình Machine Learning ánh xạ mỗi quả bóng $b \in [1, N]$ tại kỳ $t$ thành vector đặc trưng $\mathbf{x}_{t, b} \in \mathbb{R}^{14}$:

| STT | Tên đặc trưng | Nguồn gốc / Ý nghĩa |
| :---: | :--- | :--- |
| **1** | `f_hazard` | Điểm mật độ nhịp gan Gauss Bayesian Rhythm $Z$-Score từ `analytic_engines` |
| **2** | `f_decay` | Điểm tần suất động lượng suy giảm mũ Exponential Time Decay |
| **3** | `f_markov` | Điểm thông tin tương hỗ dương Markov PPMI từ kỳ trước |
| **4** | `f_spectral` | Điểm cộng hưởng sóng con Daubechies DWT + Fourier Hann từ `wavelet_engine` |
| **5** | `f_lift` | Điểm độ nâng cặp đôi Bạc Nhớ Empirical Bayes Lift |
| **6** | `f_pagerank` | Điểm trung tâm lực hút đồ thị Graph Co-occurrence PageRank |
| **7** | `f_state_space` | Biến trạng thái tiềm ẩn từ Bộ lọc Kalman Bayesian Dynamic State-Space |
| **8** | `f_pull_max_lift` | Lực kéo cực đại $\text{Pull}_{\max}(b)$ từ bộ số kỳ trước |
| **9** | `f_pull_sum_z` | Tổng xung lực ý nghĩa $\text{Pull}_Z(b)$ từ bộ số kỳ trước |
| **10** | `f_repulsion_penalty` | Lực kỵ nhau/triệt tiêu $\text{Penalty}_{\text{rep}}(b)$ |
| **11** | `f_repeat_momentum` | Động lượng lặp lại cầu rơi $\text{Momentum}_{\text{repeat}}(b)$ |
| **12** | `f_current_gap` | Số kỳ vắng mặt hiện tại (Current Gap $g_b$) |
| **13** | `f_modulo_3` | Phần dư số học $b \pmod 3 \in \{0, 1, 2\}$ |
| **14** | `f_louvain_cluster` | Mã định danh cụm đồ thị liên kết tự nhiên Louvain $\{0, 1, 2, 3, 4\}$ |

---

### 2.4. Thuật Toán Học Máy Xếp Hạng (HistGradientBoosting Ranker)
- **Mục tiêu học:**
  - Tại mỗi kỳ $t$ trong tập huấn luyện, có $N$ mẫu ứng với $N$ con số ($N = 55, 45, 35$).
  - Nhãn $y_{t, b} = 1$ nếu $b \in S_t$ (bóng thực tế trúng thưởng), ngược lại $y_{t, b} = 0$.
- **Cấu hình mô hình `HistGradientBoostingClassifier`:**
  - `learning_rate = 0.05`: Bước học nhỏ chống rung lắc.
  - `max_iter = 60`: Số cây quyết định giới hạn chống overfitting.
  - `max_depth = 3`: Giới hạn độ sâu để chỉ học các tương tác bậc 2–3 (chống bão hòa mẫu nhỏ).
  - `min_samples_leaf = 15`: Bảo đảm mỗi nút lá có đủ mẫu kiểm chứng.
  - `l2_regularization = 1.5`: Điều chuẩn co ngót $L_2$ chống quá khớp.
  - `random_state = 42`: Đảm bảo tính tất định 100%.
- **Dự báo & Xếp hạng:**
  - Với kỳ kế tiếp $T+1$:
    $$\hat{p}(b) = P(y = 1 \mid \mathbf{x}_{T+1, b})$$
  - Điểm chuẩn hóa ML Ranker:
    $$\text{Score}_{\text{ML}}(b) = \frac{\hat{p}(b) - \min_i \hat{p}(i)}{\max_i \hat{p}(i) - \min_i \hat{p}(i) + \epsilon} \times 3.0$$

---

## 3. Kiến Trúc Phân Rã & Module Hệ Thống

```
src/vietlott/
│
├── model/
│   ├── transition_engine.py    # [NEW] Động cơ khai phá luật chuyển tiếp A -> B & Vector Pull
│   ├── ml_ranker.py            # [NEW] Trích xuất đặc trưng 14 chiều & HistGradientBoosting
│   ├── analytic_engines.py     # 7 mô hình toán học nền tảng
│   ├── ensemble_engine.py      # Dynamic Alpha Stacking (Tích hợp thêm ML Ranker)
│   ├── covering_engine.py      # Dàn phủ tổ hợp C(v, k, 3) & lọc AC
│   └── wavelet_engine.py       # Sóng con Daubechies DWT
│
├── render_web_data.py          # Data Pipeline Orchestrator (Xuất transition_analytics)
└── tests/
    ├── test_transition_engine.py # Unit test ma trận chuyển tiếp & Vector Pull
    ├── test_ml_ranker.py         # Unit test feature extraction & Walk-Forward ML training
    └── ...
```

---

## 4. Tương Thích Giao Diện & Schema Dữ Liệu (`vietlott_summary.json`)

Trong `consensus_hub`, bổ sung thêm mục `transition_analytics` mà không làm thay đổi các trường hiện có:

```json
{
  "consensus_hub": {
    "leaderboard": [ ... ],
    "tickets": { ... },
    "transition_analytics": {
      "latest_draw_numbers": [2, 11, 22, 37, 44, 55],
      "top_pull_rules": [
        {
          "from_ball": 11,
          "to_ball": 22,
          "lift": 1.60,
          "z_score": 2.90,
          "historical_hits": "33/162 (20.4%)",
          "strength": "Cực Mạnh"
        },
        {
          "from_ball": 37,
          "to_ball": 44,
          "lift": 1.72,
          "z_score": 2.97,
          "historical_hits": "26/131 (19.8%)",
          "strength": "Cực Mạnh"
        }
      ],
      "top_repulsion_rules": [
        {
          "from_ball": 2,
          "to_ball": 14,
          "lift": 0.28,
          "z_score": -2.83,
          "historical_hits": "4/136 (2.9%)",
          "warning": "Kỵ nhau mạnh — Nên loại bỏ"
        }
      ]
    }
  }
}
```

---

## 5. Kế Hoạch Kiểm Thử & Tiêu Chí Nghiệm Thu (Verification Criteria)

1. **Unit Tests (`pytest`):**
   - `test_transition_engine.py`: Kiểm tra tính đối xứng, công thức $Z$-score, độ nâng Lift, các giá trị biên (bóng chưa bao giờ nổ, kỳ rỗng).
   - `test_ml_ranker.py`: Kiểm tra kích thước ma trận đặc trưng $(N, 14)$, tính hợp lệ của xác suất dự báo $0 \le \hat{p} \le 1$, tính tất định (`random_state=42`).
2. **Kiểm Định Walk-Forward Đối Soát Thực Tế:**
   - Chạy Walk-Forward 100 kỳ trên Power 6/55, Mega 6/45, và Power 5/35.
   - So sánh độ chính xác của mô hình ML Ranker với mốc ngẫu nhiên và 7 mô hình đơn lẻ.
3. **Zero Regression:**
   - Toàn bộ 69+ bài test hiện có phải tiếp tục PASS $100\%$.
4. **Không Có Mock Data:**
   - Mọi dự báo và luật kéo bóng phải được trích xuất từ dữ liệu quay thật trong các file `.jsonl`.
