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
