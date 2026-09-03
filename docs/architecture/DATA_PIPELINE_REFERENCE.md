# TÀI LIỆU CHI TIẾT DATA PIPELINE & CRAWLER REFERENCE
## CÁC MODULE XỬ LÝ DỮ LIỆU & LỊCH TRÌNH TỰ ĐỘNG

---

## 1. FILE THỰC THI CHÍNH: `src/vietlott/sync_live_data.py`

### Mục đích:
Kết nối trực tiếp vào các cổng dịch vụ nội bộ (AjaxPro Handlers) của Vietlott để cào toàn bộ các kỳ quay thưởng mới nhất và cập nhật vào kho dữ liệu JSONL mà không gây trùng lặp.

### Chi tiết các hàm & Biến chính:

#### 1. `sync_power(url_name, key, file_path, max_pages=30)`
* **Mục đích:** Cào kết quả cho Power 6/55 và Mega 6/45.
* **Tham số:**
  * `url_name`: Tên part trên URL (ví dụ: `gamepower655comparewebpart` hoặc `gamemega645comparewebpart`).
  * `key`: Hash key của webpart trên trang Vietlott (Mega: `ca3e5f22`, Power 655: `2123c5e8`).
  * `file_path`: Đường dẫn lưu file `data/power655.jsonl` hoặc `data/power645.jsonl`.
  * `max_pages`: Số trang tối đa cần quét ngược về quá khứ (mỗi trang chứa 10-20 kỳ).
* **Cơ chế chống trùng & dừng sớm (Early Stopping):**
  * Đọc `latest_local_id` từ file JSONL hiện có.
  * Khi quét gặp kỳ quay có `id <= latest_local_id` ở trang > 1, hàm tự động ngắt (`break`) để tiết kiệm băng thông.

#### 2. `sync_power535(file_path, max_pages=40)`
* **Mục đích:** Cào kết quả cho Power 5/35 (Lô ma trận đôi 5 bóng chính 01-35 + 1 bóng đặc biệt 01-12).
* **Đặc tính kỹ thuật khác biệt (2-Step Handshake):**
  * Khác với 6/55 và 6/45, máy chủ Vietlott yêu cầu phiên làm việc có `ORenderInfo` hợp lệ cho endpoint 5/35.
  * **Bước 1:** Gọi method `ServerSideFrontEndCreateRenderInfo` với header `X-AjaxPro-Method` để lấy token phiên `ORenderInfo`.
  * **Bước 2:** Gọi method `ServerSideDrawResult` thuộc WebPart `Game535CompareWebPart` với key `8a8d9359` và gửi kèm `ORenderInfo` vừa nhận.
* **Cấu trúc lưu trữ:**
  * Mỗi bản ghi lưu mảng 6 phần tử: `[c1, c2, c3, c4, c5, db]`, trong đó 5 phần tử đầu là số chính (01-35) và phần tử cuối là bóng đặc biệt (01-12).

#### 3. `sync_keno()`, `sync_bingo18()`, `sync_3d()`, `sync_3d_pro()`:
* Cào các sản phẩm quay nhanh và số 3D phục vụ mở rộng trong tương lai.

---

## 2. FILE THỰC THI TÍNH TOÁN: `src/vietlott/render_web_data.py`

### Mục đích:
Đọc các file `.jsonl` thô trong thư mục `data/`, thực hiện các phép toán thống kê ma trận và xuất bản file `docs/data/vietlott_summary.json`.

### Các hàm phân tích toán học:

#### 1. `calculate_gap_analysis(records, max_val, num_balls)`
* **Đầu vào:** Danh sách các kỳ quay lịch sử, giá trị bóng lớn nhất (35, 45, 55).
* **Đầu ra:** Bảng thống kê từng con số:
  * `current_gap`: Số kỳ liên tiếp con số này chưa về (độ gan hiện tại).
  * `max_gap`: Kỷ lục gan dài nhất trong lịch sử từng ghi nhận.
  * `avg_gap`: Chu kỳ nhịp trung bình ($Avg = rac{Total Draws}{Total Hits}$).
  * `gap_ratio`: Tỷ lệ $rac{Current Gap}{Avg Gap}$ (nếu $> 100\%$ là vượt nhịp gan, nguy cơ nổ cao).

#### 2. `calculate_cooccurrence(records, max_val)`
* Sử dụng `itertools.combinations(result, 2)` và `Counter`.
* Tìm ra Top 15 cặp số có tần suất xuất hiện cùng nhau nhiều nhất trong 100 kỳ và toàn bộ lịch sử.

#### 3. `calculate_sum_distribution(records)`
* Tính tổng 6 số (hoặc 5 số) của từng kỳ quay.
* Tính kỳ vọng toán học $\mu$ (Mean) và độ lệch chuẩn $\sigma$ (Standard Deviation) để dựng đường cong chuẩn Gaussian Bell Curve.

#### 4. `calculate_markov_matrix(records, max_val)`
* Xây dựng ma trận chuyển trạng thái Markov bậc 1: Xác suất con số $B$ xuất hiện ở kỳ $T$ khi con số $A$ đã xuất hiện ở kỳ $T-1$.

---

## 3. LỊCH TRÌNH CRON AUTOMATION (`.github/workflows/crawl.yaml`)

```yaml
schedule:
  - cron: '35 6 * * *'   # 13:35 VN: Ngay sau khi Power 5/35 quay xong kỳ trưa 13:00
  - cron: '45 11 * * *'  # 18:45 VN: Ngay sau khi Power 6/55 hoặc Mega 6/45 quay xong (18:00 - 18:30)
  - cron: '35 14 * * *'  # 21:35 VN: Ngay sau khi Power 5/35 quay xong kỳ tối 21:00
  - cron: '0 5 * * *'    # 12:00 VN: Kỳ kiểm tra đồng bộ trưa
```

Quy trình tự động trên GitHub Runner:
1. `git pull` -> Cài đặt Python 3.12 & dependencies.
2. Chạy `sync_live_data.py` cào số mới.
3. Chạy `render_web_data.py` tính toán lại toàn bộ chỉ số.
4. `git commit` các file `data/*.jsonl`, `docs/data/*.json` và tự động deploy lên GitHub Pages.
