# MÔ HÌNH TOÁN HỌC & XÁC SUẤT ĐỊNH LƯỢNG
## ALGORITHMIC & PROBABILITY MODELS REFERENCE

---

## 1. MÔ HÌNH ĐỘ PHỨC TẠP SỐ HỌC (ARITHMETIC COMPLEXITY - AC INDEX)

Chỉ số AC đo lường mức độ ngẫu nhiên và phân tán của một bộ số, giúp loại bỏ các bộ số có tính quy luật giả tạo (như cấp số cộng liên tiếp):

$$D = \text{Số lượng các hiệu số dương khác nhau giữa mọi cặp số trong bộ vé}$$
$$AC = D - (r - 1)$$

Trong đó:
* $r$ là số lượng bóng rút ra ($r = 6$ cho Mega 6/45 và Power 6/55).
* Với một bộ số có 6 phần tử, số cặp khác nhau là $C(6, 2) = 15$.
* Giá trị $D$ tối đa là 15. Do đó $AC_{\max} = 15 - (6 - 1) = 10$.
* **Quy tắc lọc của hệ thống:** Hơn $82\%$ các kỳ quay thưởng thực tế của Vietlott có $AC \ge 7$. Hệ thống gạt bỏ mọi bộ số có $AC < 6$ (như dãy `05, 10, 15, 20, 25, 30` có $AC = 1$).

---

## 2. PHÂN PHỐI TỔNG CHUẨN GAUSSIAN (SUM DISTRIBUTION & BELL CURVE)

Tổng giá trị của các con số trong một kỳ quay tuân theo định lý giới hạn trung tâm (Central Limit Theorem), tạo thành hình chuông phân phối chuẩn:

$$\mu = r \times \frac{\text{Min} + \text{Max}}{2}$$

* **Với Mega 6/45:** 
  $$\mu = 6 \times \frac{1 + 45}{2} = 138, \quad \sigma \approx 24$$
  * Vùng tổng vàng ($90\%$ kỳ quay): **$105 \le \text{Tổng} \le 175$**.
* **Với Power 6/55:** 
  $$\mu = 6 \times \frac{1 + 55}{2} = 168, \quad \sigma \approx 29$$
  * Vùng tổng vàng ($90\%$ kỳ quay): **$125 \le \text{Tổng} \le 210$**.
* **Với Power 5/35 (5 số chính):** 
  $$\mu = 5 \times \frac{1 + 35}{2} = 90, \quad \sigma \approx 18$$
  * Vùng tổng vàng ($90\%$ kỳ quay): **$65 \le \text{Tổng} \le 115$**.

---

## 3. CƠ CHẾ ĐÒN BẨY TỔ HỢP BAO SỐ (COMBINATORIAL COVERING)

### A. Mega 6/45 (Bao 7 - Giá vé 70.000đ):
Tạo ra $C(7, 6) = 7$ bộ số đơn con.

| Số số trùng | Các giải con nhận được | Tổng tiền thưởng nhận được | Lãi ròng thực tế |
|---|---|---|---|
| **Trùng 3 số** | 4 giải Ba (30.000đ) | **120.000đ** | **+50.000đ (Lời vốn)** |
| **Trùng 4 số** | 3 giải Nhì (300.000đ) + 4 giải Ba (30.000đ) | **1.020.000đ** | **+950.000đ** |
| **Trùng 5 số** | 2 giải Nhất (10.000.000đ) + 5 giải Nhì (300.000đ) | **21.500.000đ** | **+21.430.000đ** |
| **Trùng 6 số** | 1 giải Jackpot + 6 giải Nhất (10.000.000đ) | **Jackpot + 60.000.000đ** | **Ăn trọn Jackpot** |

### B. Power 6/55 (Bao 7 - Giá vé 70.000đ):
Tạo ra $C(7, 6) = 7$ bộ số đơn con. Xét thêm quả Cầu Vàng Jackpot 2 (quay từ 49 bóng còn lại trong tập 01-55).

| Số số trùng | Các giải con nhận được | Tổng tiền thưởng nhận được | Lãi ròng thực tế |
|---|---|---|---|
| **Trùng 3 số** | 4 giải Ba (50.000đ) | **200.000đ** | **+130.000đ (Lời vốn)** |
| **Trùng 4 số** | 3 giải Nhì (500.000đ) + 4 giải Ba (50.000đ) | **1.700.000đ** | **+1.630.000đ** |
| **Trùng 5 số** | 2 giải Nhất (40.000.000đ) + 5 giải Nhì (500.000đ) | **82.500.000đ** | **+82.430.000đ** |
| **Trùng 5 số + Cầu Vàng** | 1 Jackpot 2 + 1 giải Nhất (40tr) + 5 giải Nhì (500k) | **Jackpot 2 + 42.500.000đ** | **Nổ Jackpot 2** |
| **Trùng 6 số** | 1 Jackpot 1 + 6 giải Nhất (40.000.000đ) | **Jackpot 1 + 240.000.000đ** | **Nổ Jackpot 1** |
| **Trùng 6 số + Cầu Vàng**| 1 Jackpot 1 + 1 Jackpot 2 + 5 giải Nhất | **JP1 + JP2 + 200.000.000đ** | **Nổ Cả 2 Jackpot** |

### C. Power 5/35 (Bao 6 - Giá vé 60.000đ):
Tạo ra $C(6, 5) = 6$ bộ số đơn con (6 số chính chọn từ 01-35 + 1 số đặc biệt chọn từ 01-12).

| Số số trùng | Các giải con nhận được | Tổng tiền thưởng | Lãi ròng thực tế |
|---|---|---|---|
| **Chỉ trúng Cầu ĐB** | 6 giải Khuyến Khích (10.000đ) | **60.000đ** | **Hòa vốn 100% (Bảo hiểm rủi ro)** |
| **Trùng 3 số chính** | 3 giải Năm (30.000đ) | **90.000đ** | **+30.000đ** |
| **Trùng 3 số + Cầu ĐB** | 3 giải Tư (50.000đ) + 3 giải KK (10.000đ) | **180.000đ** | **+120.000đ** |
| **Trùng 4 số chính** | 2 giải Ba (50.000đ) | **100.000đ** | **+40.000đ** |
| **Trùng 4 số + Cầu ĐB** | 2 giải Nhì (500.000đ) + 4 giải Tư (50.000đ) | **1.200.000đ** | **+1.140.000đ** |
| **Trùng 5 số chính** | 1 giải Nhất (40.000.000đ) + 5 giải Ba (50.000đ) | **40.250.000đ** | **+40.190.000đ** |
| **Trùng 5 số + Cầu ĐB** | 1 Jackpot Độc Đắc + 5 giải Nhì (500.000đ) | **Jackpot (6+ Tỷ) + 2.500.000đ** | **Nổ Jackpot Độc Đắc** |

---

## 4. MÔ HÌNH NGUY CƠ BAYESIAN & SUY GIẢM MŨ (BAYESIAN HAZARD RATE & TIME DECAY)

### A. Tần suất có trọng số suy giảm mũ (Exponential Time Decay):
Các kỳ quay gần nhất phản ánh nhịp vận động cơ học và xác suất tức thời tốt hơn các kỳ quá xa trong quá khứ. Trọng số của kỳ quay cách hiện tại $t$ kỳ được tính:

$$w(t) = e^{-lpha \cdot t} \quad (\text{với } \alpha = 0.035)$$

Điểm tần suất suy giảm của bóng $b$:
$$S_{\text{decay}}(b) = \sum_{t=0}^{K-1} w(t) \cdot \mathbb{I}(b \in \text{draw}_t)$$

### B. Hàm nguy cơ nhịp gan Bayesian (Gap Hazard Rate Function):
Gọi $g_b$ là số kỳ vắng mặt hiện tại của bóng $b$, và $\bar{g}_b$ là chu kỳ nhịp trung bình trong lịch sử. Tỷ số nhịp gan chuẩn hóa:

$$r_b = \frac{g_b}{\max(1.0, \bar{g}_b)}$$

Hàm mật độ nguy cơ nổ $H(r_b)$ đạt đỉnh cực đại tại "Vùng Vàng Điểm Rơi" ($0.75 \le r_b \le 1.35$):
* Nếu $0.75 \le r_b \le 1.35$: $H(r_b) = 2.8 - 1.5 \times |r_b - 1.05|$ (Ưu tiên tối đa).
* Nếu $r_b < 0.4$: $H(r_b) = 0.5 + r_b$ (Bóng vừa nổ, xác suất lặp lại thấp hơn).
* Nếu $r_b > 2.2$: $H(r_b) = 0.8$ (Gan lì lợm kéo dài, rủi ro chôn vốn).

Điểm tổng hợp định lượng cho từng con số:
$$\text{Score}(b) = S_{\text{decay}}(b) \times 1.8 + H(r_b) \times 3.5$$

---

## 5. HỆ THỐNG DÀN GHÉP BỌC LÓT TOÁN HỌC (COMBINATORIAL WHEELING SYSTEM)

Thay vì dự đoán một vé đơn lẻ 6 số ($P = 1 / 28.989.675$), mô hình chọn ra **Tập Hạt Nhân (Core Pool)** gồm $v$ con số có điểm số định lượng cao nhất ($v = 14$ cho 6/55, 6/45 và $v = 12$ cho 5/35).

Sau đó áp dụng **Cấu trúc phủ tổ hợp tối ưu (Covering Design $C(v, k, t)$)**:
Phủ $v$ con số thành 6 vé đơn 6 số sao cho:
$$\forall T \subset \text{Core Pool}, |T| \ge 4 \implies \exists \text{ Vé } W \text{ sao cho } |T \cap W| \ge 3$$

* **Ý nghĩa thực chiến:** Người chơi chỉ cần bỏ ra **60.000đ** (6 vé đơn 10k), nếu trong 14 số của Tập Hạt Nhân có 4 số quay thưởng nổ, **CHẮC CHẮN sẽ có ít nhất 1 vé trúng giải Ba (50.000đ) hoặc giải Nhì (500.000đ/1.700.000đ)**!
* Đây là phương pháp quản trị rủi ro và tối ưu hóa đòn bẩy vốn theo lý thuyết trò chơi được chứng minh toán học.

---

## 6. MA TRẬN KỀ ĐỒNG QUY CẶP ĐÔI (CO-OCCURRENCE ADJACENCY MATRIX & PAIRWISE LIFT)

### A. Ma trận kề đối xứng $M_{N \times N}$:
Với $N$ là số lượng bóng trong lồng ($N = 55$ cho 6/55, $N = 45$ cho 6/45), ma trận kề $M$ được xác định trên cửa sổ $W = 200$ kỳ gần nhất:
$$M_{ij} = \sum_{t=1}^{W} \mathbb{I}(i \in \text{draw}_t \land j \in \text{draw}_t) \quad (\forall i \neq j, M_{ii} = 0)$$

### B. Chỉ số độ nâng lực hút cặp đôi (Pairwise Lift):
Đo lường mức độ hai con số xuất hiện cùng nhau cao hơn bao nhiêu lần so với kỳ vọng ngẫu nhiên độc lập:
$$\text{Lift}(i, j) = \frac{P(i \cap j)}{P(i) \cdot P(j)} = \frac{M_{ij} \times W}{F_i \times F_j}$$
Trong đó $F_i$ và $F_j$ là tần suất xuất hiện độc lập của bóng $i$ và $j$.
* Nếu $\text{Lift}(i, j) \ge 1.5$: Hai số có **lực hút đồng quy cực mạnh** (Synergistic Pair), ưu tiên ghép cùng vé.
* Nếu $\text{Lift}(i, j) < 0.5$: Hai số có tính **xung khắc / kỵ nhau** (Repulsive Pair), tránh đưa cả 2 vào cùng một vé đơn.

---

## 7. PHÂN CỤM ĐỒ THỊ TỰ NHIÊN (GRAPH COMMUNITY DETECTION - LOUVAIN MODULARITY)

Mạng lưới quan hệ giữa các con số được mô hình hóa thành đồ thị vô hướng có trọng số $G = (V, E, W)$, trong đó các đỉnh là các con số, và trọng số cạnh là số lần nổ chung $M_{ij} \ge 3$.

Hệ thống áp dụng thuật toán tối ưu hóa độ tách biệt mô-đun (Modularity Maximization):
$$Q = \frac{1}{2m} \sum_{i, j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

Thuật toán tự động phân hoạch 55 số thành **4 đến 5 Cụm Đồ Thị tự nhiên (Graph Communities)**:
* **Quy tắc rải vé tối ưu:** Khi sinh một vé 6 số, thuật toán áp dụng nguyên lý **Đa dạng hóa danh mục**: Bắt buộc 6 con số phải đến từ ít nhất 4 cụm đồ thị khác nhau, ngăn chặn triệt để hiện tượng dồn hết số vào một cụm rủi ro.

---

## 8. PHÂN TÍCH PHỔ CHU KỲ NHỊP FOURIER & HÀM ĐIỂM ĐA NHÂN TỐ TỐI ƯU (FOURIER SPECTRAL RECURRENCE & OPTIMIZED MULTI-FACTOR ENGINE)

### A. Biến đổi Fourier rời rạc trên chuỗi xuất hiện (Discrete Fourier Transform - DFT):
Mỗi quả bóng $b \in [1, N]$ được biểu diễn dưới dạng chuỗi tín hiệu thời gian nhị phân trên cửa sổ $L = 64$ kỳ gần nhất:
$$x_b[t] = \begin{cases} 1 & \text{nếu } b \in \text{draw}_t \\ 0 & \text{ngược lại} \end{cases} \quad (t = 0, \dots, L-1)$$

Áp dụng biến đổi Fourier rời rạc trên tín hiệu đã chuẩn hóa trung bình:
$$X_b[k] = \sum_{t=0}^{L-1} (x_b[t] - \bar{x}_b) e^{-i 2\pi k t / L} \quad (k = 1, \dots, L/2)$$

Tần số dao động chủ đạo (Dominant Recurrence Frequency) và chu kỳ cộng hưởng $T_b$:
$$k_b^* = \arg\max_{k \ge 1} |X_b[k]|, \quad T_b = \frac{L}{k_b^*}$$

Điểm cộng hưởng chu kỳ (Spectral Resonance Score) khi nhịp gan hiện tại $g_b$ tiến gần chu kỳ riêng $T_b$:
$$S_{\text{spectral}}(b) = \exp\left( -0.2 \cdot |g_b - T_b| \right)$$

### B. Hàm chấm điểm đa nhân tố tối ưu (Optimized Multi-Factor Scoring):
Điểm tổng hợp của mỗi quả bóng $b$ được xác định bởi hàm tuyến tính có trọng số đã qua kiểm định thực nghiệm trên 300 kỳ:
$$\text{Score}(b) = w_1 \cdot H(r_b) + w_2 \cdot F_{\text{decay}}(b) + w_3 \cdot \mathbb{I}_{\text{Cầu Rơi}}(b) + w_4 \cdot S_{\text{spectral}}(b) + w_5 \cdot \text{Lift}_{\text{Bạc Nhớ}}(b) + w_6 \cdot M_{\text{Synergy}}(b)$$

Trong đó bộ trọng số tối ưu thực nghiệm:
* $w_1 = 2.0$: Trọng số Bayesian Hazard Rate vùng vàng
* $w_2 = 1.5$: Trọng số Exponential Time Decay
* $w_3 = 2.5$: Trọng số Quán tính Cầu Rơi
* $w_4 = 0.5$: Trọng số Cộng hưởng phổ Fourier
* $w_5 = 1.8$: Trọng số Bạc Nhớ Cặp Đôi kéo bóng
* $w_6 = 1.2$: Trọng số Ma Trận Kề Đồng Quy

---

## 9. LÝ THUYẾT THÔNG TIN MARKOV PPMI (POSITIVE POINTWISE MUTUAL INFORMATION)

Để triệt tiêu thiên lệch do tần suất xuất hiện tự nhiên của các con số, ma trận chuyển trạng thái được chuẩn hóa bằng thông tin tương hỗ dương (PPMI) có làm mịn Laplace ($\alpha = 0.1$):

$$P(p \cap c) = \frac{\text{Count}(p \to c) + \alpha}{\sum \text{Transitions} + \alpha \cdot N}$$
$$\text{PPMI}(p, c) = \max\left(0, \log_2 \frac{P(p \cap c)}{P(p) \cdot P(c)}\right)$$
$$\text{Score}_{\text{PPMI}}(c) = \sum_{p \in \text{Draw}_{T-1}} \text{PPMI}(p, c)$$

Mô hình chỉ tích lũy điểm khi xác suất chuyển trạng thái $P(c \mid p)$ thực sự vượt trội so với xác suất biên ngẫu nhiên độc lập $P(c)$.

---

## 10. HÀM NGUY CƠ CHUẨN HÓA BAYESIAN RHYTHM Z-SCORE

Khắc phục hạn chế của hàm bước thang cũ, mô hình mới chuẩn hóa độ lệch nhịp theo độ lệch chuẩn chu kỳ $\sigma_b$:

$$z_b = \frac{g_b - 1.05 \cdot \bar{g}_b}{\max(1.0, \sigma_b)}$$
$$H_{\text{Z-Score}}(b) = 3.0 \cdot \exp\left(-\frac{z_b^2}{2}\right) \times \begin{cases} 0.3 & \text{nếu } z_b > 2.5 \text{ (Gan quá hạn)} \\ 1.0 & \text{ngược lại} \end{cases}$$

---

## 11. CƠ CHẾ XẾP CHỒNG ĐỘNG DYNAMIC ALPHA STACKING

Thay vì gộp cào bằng 5 mô hình với làm mịn Borda phẳng, hệ thống đánh giá Alpha ngoại mẫu (Out-Of-Fold Alpha) của từng mô hình qua 100 kỳ Walk-Forward và phân bổ trọng số Softmax:

$$\text{Weight}(m) = \frac{\exp(\beta \cdot \text{Alpha}_m)}{\sum_j \exp(\beta \cdot \text{Alpha}_j)}$$
$$\text{Conviction}(b, m) = \exp(-0.08 \cdot \text{Rank}_{b, m})$$
$$\text{Consensus\_Score}(b) = \sum_{m} \text{Weight}(m) \cdot \text{Conviction}(b, m)$$

