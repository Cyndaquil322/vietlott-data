# NGUYÊN TẮC BẮT BUỘC VỀ TÍNH TOÀN VẸN DỮ LIỆU & TRUNG THỰC KHOA HỌC
## DỰ ÁN: VIETLOTT ANALYTICS & LIVE EXPLORER

> [!CAUTION]
> **QUY TẮC BẤT DI BẤT DỊCH (NON-NEGOTIABLE LAW):**
> Tuyệt đối KHÔNG BAO GIỜ được sử dụng dữ liệu giả định (mock/fake data) để hiển thị kết quả dự đoán hoặc làm đẹp số liệu. Mọi thông tin phải xuất phát 100% từ dữ liệu thực tế và thuật toán tính toán thật.

---

### 1. TUYỆT ĐỐI CẤM SỬ DỤNG DỮ LIỆU GIẢ ĐỊNH / MOCK DATA
* CẤM TỰ Ý TẠO RA DỮ LIỆU MẪU (MOCK DATA) để giả vờ rằng thuật toán đã dự đoán đúng các kỳ trong quá khứ.
* Mọi bảng đối soát (Lịch sử dự đoán Ensemble, Lịch sử dự đoán Bao 7, Bảng P&L lời/lỗ):
  * **BẮT BUỘC phải được tính toán bằng thuật toán thật từ pipeline dữ liệu (`render_web_data.py`).**
  * Không bao giờ được hardcode các mảng kết quả trúng 4, 5, 6 số để "lấy lòng" người dùng.

---

### 2. KIỂM ĐỊNH QUÁ KHỨ KHÁCH QUAN (WALK-FORWARD BACKTEST 100%)
* Khi đối soát hiệu quả của thuật toán trong quá khứ:
  * Phải tuân thủ nghiêm ngặt nguyên lý **Walk-Forward**: Tại kỳ $T$, chỉ được sử dụng dữ liệu từ kỳ $T-1$ trở về trước để chạy mô hình dự đoán cho kỳ $T$.
  * Tuyệt đối không có thiên lệch nhìn trước tương lai (No Look-Ahead Bias / No Hindsight Bias).
  * Thuật toán bắt trúng mấy số (0 số, 1 số, 2 số, 3 số) thì hiển thị trung thực bấy nhiêu số. Không giấu lỗ, không thổi phồng lãi.

---

### 3. CỐ ĐỊNH BỘ SỐ DỰ ĐOÁN THEO KỲ (DETERMINISTIC SEEDED PREDICTIONS)
* Bộ số dự đoán chính thức cho kỳ tiếp theo phải luôn được gieo mầm cố định theo mã kỳ quay (`Draw ID Seed`).
* Khi người dùng tải lại trang (F5/Reload) hoặc mở trên nhiều thiết bị khác nhau, bộ số đề xuất chính thức phải luôn đồng nhất 100%, không được tự ý nhảy số lung tung do dùng hàm ngẫu nhiên thuần túy.
* Chỉ sinh thêm tổ hợp mới khi người dùng chủ động bấm nút *"Sinh thêm tổ hợp"*.
