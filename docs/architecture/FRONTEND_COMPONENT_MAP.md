# BẢN ĐỒ KIẾN TRÚC FRONTEND & COMPONENT MAP
## TÀI LIỆU THAM CHIẾU MÃ NGUỒN `docs/index.html`

---

## 1. CẤU TRÚC PHÂN CHIA CÁC VIEW (SPA VIEWS)

Giao diện là một Single Page Application (SPA) chứa 11 view nội dung được điều hướng bằng hàm `switchView(viewName)`:

| ID Thẻ Div | Tên View trên Menu | Chức năng chính |
|---|---|---|
| `view-overview-content` | **Kỳ Quay & Dò Vé** | Đồng hồ đếm ngược trực tiếp, Hero Card kết quả mới nhất, Dò vé trúng thưởng, Soi cầu bóng đặc biệt (01-55 hoặc 01-12) |
| `view-gap-content` | **Thống Kê Số Gan** | Bảng cảnh báo số vượt nhịp gan, thống kê Current Gap, Max Gap của toàn bộ bóng |
| `view-pairs-content` | **Cặp Số Hay Đi Cùng** | Ma trận cặp đôi (Pairs) và bộ ba (Triples) có tần suất về cùng nhau cao nhất |
| `view-sum-content` | **Phân Tích Tổng Giải** | Biểu đồ phân phối Gaussian, xu hướng tổng dồn, kỳ vọng toán học |
| `view-patterns-content` | **Xu Hướng & Mẫu Hình** | Tỷ lệ số liền kề, tỷ lệ lặp lại từ kỳ trước, phân bố dải đầu số (Decade) |
| `view-positional-content` | **Vị Trí & Biên Độ** | Thống kê giá trị từng vị trí bóng (Bóng 1 đến 6) và biên độ dải (Span = Max - Min) |
| `view-ac-delta-content` | **Độ Phức Tạp & Delta** | Biểu đồ chỉ số Arithmetic Complexity (AC) và khoảng cách giữa các số liên tiếp |
| `view-markov-content` | **Markov & Dự Đoán** | Dự báo xác suất chuyển trạng thái Markov kỳ tới |
| `view-digits-ev-content` | **Đuôi Số & Đo +EV** | Phân tích phân bố chữ số hàng đơn vị và kỳ vọng giá trị dương (+EV) |
| `view-ensemble-content` | **Dự Đoán Toàn Diện** | Bộ sinh số Ensemble Multi-Model (100 kỳ), bảng Lịch sử dự đoán & đối soát kết quả |
| `view-bao7-content` | **Chiến Lược Bao 7 (70k)** | Trình sinh dàn Bao 7 (hoặc Bao 6 cho 5/35), bảng cơ cấu thưởng chính thức Vietlott, tính lãi/lỗ |
| `view-saved-tickets-content` | **Sổ Tay Vé Đã Lưu** | Quản lý toàn bộ vé cá nhân, tự động đối soát kết quả thật từ Vietlott, tính P&L ròng, Copy/Gửi SMS 9969, Tạo link đồng bộ |
| `view-history-content` | **Lịch Sử Kỳ Quay** | Bảng tra cứu toàn bộ các kỳ quay quá khứ kèm phân trang |

---

## 2. BẢNG BIẾN TOÀN CỤC (GLOBAL STATE VARIABLES)

```javascript
let appData = null;                 // Chứa toàn bộ dữ liệu từ vietlott_summary.json
let currentProductKey = 'power_655'; // Game đang chọn: 'power_655' | 'power_645' | 'power_535'
let currentView = 'overview';        // Tab view đang kích hoạt
let currentBao7Ticket = null;        // Dàn Bao 7 / Bao 6 đang hiển thị ở tab Bao
let currentEnsembleTickets = [];     // Danh sách các bộ số vàng đang sinh ở tab Ensemble
let gitSavedTickets = [];            // Danh sách vé được đồng bộ về từ file Git (saved_tickets.json)
let countdownInterval = null;        // Timer đồng hồ đếm ngược kỳ quay kế tiếp
let currentSavedFilter = 'all';      // Bộ lọc game trong Sổ Tay: 'all' | 'power_655' | 'power_645' | 'power_535'
let currentPage = 1;                 // Trang hiện tại ở bảng lịch sử
const PAGE_SIZE = 25;                // Số dòng mỗi trang lịch sử
```

---

## 3. DANH MỤC CÁC HÀM CỐT LÕI (CORE FUNCTIONS MAP)

### A. Nhóm Khởi Tạo & Điều Hướng (Lifecycle & Navigation):
* `DOMContentLoaded`: Khởi chạy khi DOM sẵn sàng -> Gọi `updateSavedBadge()`, `renderGameTabs()`, `checkUrlSyncParams()`, `loadData()`.
* `loadData()`: Nạp song song `vietlott_summary.json` và `saved_tickets.json` với tham số chống cache `?v=timestamp`.
* `onDataReady()`: Kích hoạt khi có dữ liệu -> Gọi `renderCurrentProduct()` và `updateSavedBadge()`.
* `switchProduct(key)`: Chuyển đổi game -> Xóa vé tạm, reset page, vẽ lại menu game và gọi `renderCurrentProduct()`.
* `switchView(viewName)`: Chuyển tab hiển thị, kích hoạt lại Chart.js tương ứng và gọi hàm render của view đó.

### B. Nhóm Đồng Hồ Đếm Ngược & Soi Cầu Đặc Biệt:
* `startLiveCountdown()` & `updateCountdown()`: Tính toán thời điểm mở thưởng kế tiếp (Power 6/55 lúc 18h T3-T5-T7, Mega 6/45 lúc 18h T4-T6-CN, Power 5/35 lúc 13h và 21h hàng ngày). Tính số giờ:phút:giây còn lại và hiển thị mã kỳ quay kế tiếp `#0xxxx`.
* `renderSpecialBallTracker(product)`: 
  * Cho Power 6/55: Tính thống kê 55 quả cầu vàng (01 - 55), hiển thị Top 6 cầu vàng điểm rơi chu kỳ và ma trận 55 nút bấm thu gọn.
  * Cho Power 5/35: Tính thống kê 12 quả bóng đặc biệt (01 - 12), hiển thị lưới 12 thẻ bóng.
  * Cho Mega 6/45: Ẩn mục này hoàn toàn.

### C. Nhóm Sinh Số & Chiến Lược Bao:
* `generateBao7Ticket(forceNew)`: Thuật toán lọc tổ hợp Monte Carlo tối ưu hóa: Khóa số ruột, kiểm tra tổng dải (minSum - maxSum), kiểm tra tỷ lệ chẵn/lẻ, độ phức tạp AC và đuôi số.
* `getBao7SmsSyntax()` & `openSmsUrl(syntax)`: Sinh cú pháp tin nhắn 9969 chuẩn Vietlott và tự động mở ứng dụng SMS trên iPhone (`&body=`) hoặc Android (`?body=`).

### D. Nhóm Sổ Tay & Đồng Bộ Đa Thiết Bị (Saved Tickets Notebook):
* `getSavedTickets()` & `setSavedTickets(list)`: Đọc/ghi mảng vé cá nhân vào `localStorage['vietlott_user_notebook_tickets']`.
* `getAllMergedSavedTickets()`: Hợp nhất danh sách vé lưu tại máy và danh sách vé kéo về từ Git (`gitSavedTickets`).
* `renderSavedTicketsView()`: Render giao diện Sổ Tay, tự động so khớp vé với kết quả Vietlott thực tế, tính tiền trúng thưởng và lãi/lỗ ròng.
* `createShareSyncLink()`: Mã hóa Base64 toàn bộ vé vào URL param `?sync=...` và copy link để gửi qua Zalo/iMessage.
* `checkUrlSyncParams()`: Tự động phát hiện khi mở link `?sync=...` trên thiết bị khác và nạp vé vào Sổ Tay.
* `exportTicketsJson()` & `importTicketsJson(event)`: Sao lưu và phục hồi sổ tay qua file JSON.
