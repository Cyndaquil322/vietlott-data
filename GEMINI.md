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

---

### 4. QUY TRÌNH KỸ THUẬT BẮT BUỘC (ENGINEERING WORKFLOWS & SUPERPOWERS ENFORCEMENT)
Mỗi khi tiếp nhận bất kỳ yêu cầu nào từ người dùng, Agent BẮT BUỘC phải vận hành theo đúng các nguyên tắc:

1. **Khởi động & Kích hoạt Skill (`using-superpowers`):**
   - Phải xác định và gọi skill phù hợp ngay từ đầu.
   - Luôn tuyên bố minh bạch: `"Using [skill] to [purpose]"` trước khi thực hiện bất kỳ hành động nào.
2. **Theo dõi tiến độ bằng Checklist (Task Tracking):**
   - Tạo và duy trì một Task Checklist rõ ràng (`- [ ]`, `- [/]`, `- [x]`) trong phản hồi để người dùng theo dõi tiến độ từng bước theo thời gian thực.
3. **Tuân thủ chu trình phân lớp:**
   - **Phát triển tính năng mới:** `brainstorming` -> `writing-plans` -> `executing-plans` (hoặc `subagent-driven-development`).
   - **Sửa lỗi / Điều tra:** `systematic-debugging` (Tìm nguyên nhân gốc trước khi sửa).
   - **Viết code:** `test-driven-development` (TDD - Viết test kiểm chứng trước).
   - **Trước khi công bố hoàn thành:** Bắt buộc áp dụng `verification-before-completion`: Chạy lệnh kiểm thử thực tế và trưng ra bằng chứng (Fresh Evidence) trước khi đưa ra bất kỳ kết luận nào (`NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`).
   - **Kết thúc & Bàn giao:** `finishing-a-development-branch`.

---

### 5. QUY TẮC BẢO TOÀN DỮ LIỆU MÁY NGƯỜI DÙNG (DATA SAFETY)
* **TUYỆT ĐỐI KHÔNG ĐƯỢC XOÁ BẤT KỲ FILE NÀO TRÊN MÁY NGƯỜI DÙNG.**
* Khi tích hợp, cấu hình hoặc nâng cấp, **CHỈ ĐƯỢC COPY HOẶC TẠO MỚI** file.

---

### 6. QUY TẮC VỀ LỊCH QUAY & ĐẶC TÍNH SẢN PHẨM (VIETLOTT RULES MEMORY)
* **BẮT BUỘC ĐỌC VÀ TUÂN THỦ TÀI LIỆU:** [VIETLOTT_GAME_RULES.md](file:///d:/Projects/vietlott-data-master/VIETLOTT_GAME_RULES.md).
* **ĐẶC BIỆT LƯU Ý VỀ TẦN SUẤT & LỊCH QUAY:**
  * **Lotto 5/35 (Power 5/35):** Quay **2 LẦN MỖI NGÀY** vào lúc **13:00 (Kỳ Trưa)** và **21:00 (Kỳ Tối)**, tất cả các ngày trong tuần (Thứ Hai đến Chủ Nhật). Tuyệt đối không được bỏ sót kỳ trưa 13:00!
  * **Power 6/55:** Quay lúc **18:00 – 18:30** các ngày **Thứ Ba, Thứ Năm, Thứ Bảy**.
  * **Mega 6/45:** Quay lúc **18:00 – 18:30** các ngày **Thứ Tư, Thứ Sáu, Chủ Nhật**.
* Mọi tính toán Walk-Forward, thời gian đếm ngược (countdown), lập lịch cào dữ liệu và dự đoán kỳ tiếp theo phải luôn căn cứ chuẩn xác theo lịch quay này.
