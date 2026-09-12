# ĐẶC TẢ THIẾT KẾ KỸ THUẬT: TINH GIẢN & TÁI CẤU TRÚC GIAO DIỆN NGƯỜI DÙNG (UI/UX SIMPLIFICATION & MODERNIZATION)

**Mã thiết kế:** `SPEC-UI-SIMPLIFICATION-20260913`  
**Ngày lập:** 13/09/2026  
**Tác giả:** Antigravity / DeepSeek Harness  
**Trạng thái:** Approved / Ready for Implementation Plan  

---

## 1. MỤC TIÊU & BỐI CẢNH (OBJECTIVES & CONTEXT)

### 1.1. Hiện trạng & Vấn đề
- **Quá tải nhận thức (Cognitive Overload):** Thanh điều hướng bên trái (Sidebar) hiện có tới **16 tab lẻ tẻ**, gây rối mắt và làm người dùng khó định hướng.
- **Rối loạn phương án dự đoán:** Màn hình hiển thị quá nhiều bộ vé cùng lúc (Vé A, Vé B, Vé C, Dàn 4 vé, Dàn Banker, Bao 7, Dàn hạt nhân, Bộ 5 vé 50k...).
- **Quyết định mua vé bị chậm:** Người dùng phải đọc qua hàng loạt khối giao diện phức tạp mới tìm được vé cần mua.

### 1.2. Mục tiêu thiết kế mới
1. **Gom gọn Sidebar từ 16 tab thành 4 Không Gian Cốt Lõi (4 Master Hubs):**
   - 🎯 **1. Trung Tâm Dự Đoán (Prediction Hub):** Màn hình chính mặc định khi vào web.
   - 📋 **2. Kết Quả & Sổ Tay Dò Vé (Results & Notebook):** Kỳ mới xổ, lịch sử kết quả, dò vé tự động.
   - 🔬 **3. Lab Phân Tích Định Lượng (Analytics Lab):** Toàn bộ biểu đồ chuyên sâu (Markov, Gap, Cặp đôi, Cầu rơi...) gom vào 1 nơi với thanh chuyển tab con mượt mà.
   - 🎮 **4. Giả Lập Đầu Tư (Simulator):** Kiểm tra P&L và mô phỏng xác suất.
2. **Cấu trúc lại Trang Dự Đoán theo 3 Gói Ngân Sách Thực Tế:**
   - 🟡 **Gói 1: 10.000đ (Vé Vàng Markowitz)** — Tối ưu cho người nuôi 1 vé đơn lẻ.
   - 🟢 **Gói 2: 50.000đ (Bộ 5 Vé Bọc Lót Danh Mục)** — Tối ưu cho ngân sách ngày, lưới gom cặp/bộ ba.
   - 🟣 **Gói 3: 70.000đ (Bao 7 / Bao 6 Pareto)** — Tối ưu cho người săn giải lớn, ăn x4 giải con.
   - Các dàn số hỗ trợ (Dàn Hạt Nhân 12 số, Dàn Banker, Dàn 4 vé) được gom gọn gàng trong **Khối Công Cụ Ghép Số Chuyên Nghiệp (Accordion/Drawer)**.
3. **Giữ nguyên 100% tính năng & dữ liệu thuật toán:** Không làm mất bất kỳ module toán học nào, chỉ sắp xếp lại luồng thị giác.

---

## 2. KIẾN TRÚC PHÂN TẦNG GIAO DIỆN (UI ARCHITECTURE)

### 2.1. Bản đồ điều hướng mới (`docs/assets/js/core.js`)
```javascript
const MASTER_VIEWS = {
  'prediction': { name: 'Trung Tâm Dự Đoán', icon: 'cpu', color: 'amber' },
  'results': { name: 'Kết Quả & Sổ Tay', icon: 'bookmark-check', color: 'emerald' },
  'analytics': { name: 'Lab Phân Tích Định Lượng', icon: 'activity', color: 'indigo' },
  'simulator': { name: 'Giả Lập Đầu Tư', icon: 'play-circle', color: 'cyan' },
};
```

### 2.2. Bố cục 3 Gói Ngân Sách trên màn hình Dự Đoán (`docs/index.html`)
- **Tầng 1 (Hero):** Thước đo tin cậy `Consensus Conviction Meter` + Đồng hồ đếm ngược giờ quay + Góc nhìn chuyên gia.
- **Tầng 2 (3 Gói Ngân Sách):** 3 Thẻ Card nổi bật trực quan đặt cạnh nhau:
  - Card 1: Vé Vàng (10k) + Nút SMS 9969 + Nút Lưu Sổ.
  - Card 2: Bộ 5 Vé Bọc Lót (50k) + Nút SMS 9969 (5 vé) + Nút Lưu Cả 5 Vé.
  - Card 3: Bao 7 Pareto (70k) + Nút SMS 9969 + Nút Lưu Bao 7.
- **Tầng 3 (Dàn Hạt Nhân & Bóc Tách):** Khối Dàn Hạt Nhân (12 số) + Tab mở rộng Dàn Banker & Bao 4 vé thu gọn.
- **Tầng 4 (Bằng Chứng Thực Tế):** Bảng Nhật Ký Đối Soát `prediction_ledger` (minh bạch 100% Walk-Forward).

---

## 3. KẾ HOẠCH KIỂM THỬ GIAO DIỆN
- Kiểm tra hiển thị responsive hoàn hảo trên Mobile, Tablet và Desktop.
- Kiểm tra tính năng chuyển tab và nạp Sharded JSON không phát sinh lỗi.
- Đảm bảo toàn bộ các nút chức năng (Lưu vé, SMS 9969, Copy) hoạt động trơn tru.
