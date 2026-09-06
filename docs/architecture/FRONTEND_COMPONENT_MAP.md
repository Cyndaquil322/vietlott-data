# BẢN ĐỒ KIẾN TRÚC FRONTEND & COMPONENT MAP
## TÀI LIỆU THAM CHIẾU MÃ NGUỒN `docs/index.html`

---

## 1. CẤU TRÚC PHÂN CHIA CÁC VIEW (SPA VIEWS & 2-TIER NAVIGATION)

Giao diện là một Single Page Application (SPA) chứa 16 view nội dung được phân thành **4 Cụm Nhóm Tầng 1 (Primary Categories)** và các Tab con ở Tầng 2:

### Nhóm 1: `overview` (🎯 Tổng Quan & Vé)
| ID Thẻ Div | Tên View trên Menu | Chức năng chính |
|---|---|---|
| `view-overview-content` | **Kỳ Quay & Dò Vé** | Đồng hồ đếm ngược trực tiếp, Hero Card kết quả mới nhất, Dò vé trúng thưởng, Soi cầu bóng đặc biệt |
| `view-saved-tickets-content` | **Sổ Tay Vé Đã Lưu** | Quản lý toàn bộ vé cá nhân, tự động đối soát kết quả thật từ Vietlott, tính P&L ròng, Copy/Gửi SMS 9969 |
| `view-history-content` | **Lịch Sử Kỳ Quay** | Bảng tra cứu toàn bộ các kỳ quay quá khứ kèm phân trang |

### Nhóm 2: `predictions` (🤖 AI & Dự Đoán)
| ID Thẻ Div | Tên View trên Menu | Chức năng chính |
|---|---|---|
| `view-consensus-content` | **⭐ Tổng Hợp Dự Đoán** | Bảng đấu sĩ đối soát 100 kỳ walk-forward cho 5 mô hình độc lập + Consensus, Bảng trọng số Top 15 bóng, Ma trận giải trình toán học (Explainable AI), Bộ vé đề xuất chuẩn SEI |
| `view-ensemble-content` | **Dự Đoán Toàn Diện** | Bộ sinh số Ensemble Multi-Model (100 kỳ), bảng Lịch sử dự đoán & đối soát kết quả |
| `view-bao7-content` | **Chiến Lược Bao 7 (70k)** | Trình sinh dàn Bao 7 (hoặc Bao 6 cho 5/35), bảng cơ cấu thưởng chính thức Vietlott, tính lãi/lỗ |
| `view-smart-generator-content` | **Tạo Vé Thông Minh** | Trình tạo vé theo bộ lọc tham số tùy biến |
| `view-simulator-content` | **Giả Lập Nuôi Số** | Backtest chiến lược nuôi số cá nhân qua lịch sử |

### Nhóm 3: `stats` (📊 Thống Kê Cơ Bản)
| ID Thẻ Div | Tên View trên Menu | Chức năng chính |
|---|---|---|
| `view-gap-content` | **Thống Kê Số Gan** | Bảng cảnh báo số vượt nhịp gan, thống kê Current Gap, Max Gap của toàn bộ bóng |
| `view-pairs-content` | **Cặp Số Hay Đi Cùng** | Ma trận cặp đôi (Pairs) và bộ ba (Triples) có tần suất về cùng nhau cao nhất |
| `view-sum-content` | **Phân Tích Tổng Giải** | Biểu đồ phân phối Gaussian, xu hướng tổng dồn, kỳ vọng toán học |
| `view-patterns-content` | **Xu Hướng & Mẫu Hình** | Tỷ lệ số liền kề, tỷ lệ lặp lại từ kỳ trước, phân bố dải đầu số (Decade) |

### Nhóm 4: `quant` (🔬 Định Lượng Sâu)
| ID Thẻ Div | Tên View trên Menu | Chức năng chính |
|---|---|---|
| `view-markov-content` | **Markov & Dự Đoán** | Dự báo xác suất chuyển trạng thái Markov kỳ tới |
| `view-ac-delta-content` | **Độ Phức Tạp & Delta** | Biểu đồ chỉ số Arithmetic Complexity (AC) và khoảng cách giữa các số liên tiếp |
| `view-positional-content` | **Vị Trí & Biên Độ** | Thống kê giá trị từng vị trí bóng (Bóng 1 đến 6) và biên độ dải (Span = Max - Min) |
| `view-digits-ev-content` | **Đuôi Số & Đo +EV** | Phân tích phân bố chữ số hàng đơn vị và kỳ vọng giá trị dương (+EV) |

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

---

## 4. CẤU TRÚC PHÂN RÃ MODULE TĨNH (STATIC ASSETS ARCHITECTURE)

Giao diện đã được phân rã hoàn toàn từ file nguyên khối sang kiến trúc module tĩnh thuần túy, tối ưu cho GitHub Pages HTTP/2 và PWA Cache Storage v1.1:

```text
docs/
├── index.html                   # Khung HTML tinh gọn (~2.340 dòng, DOM & Template)
├── sw.js                        # Service Worker (Cache Storage v1.1, ignoreSearch JSON)
└── assets/
    ├── css/
    │   └── styles.css           # Hiệu ứng 3D ball, màu sắc bóng, thanh cuộn tùy biến
    └── js/
        ├── core.js              # State toàn cục, PRNG Seeded, PWA, Navigation & Router
        ├── common_analytics.js  # Thống kê cơ bản: Dò vé, Gap, Cặp số, Tổng Gaussian, Lịch sử
        ├── advanced_quant.js    # Định lượng sâu: Vị trí, AC/Delta, Markov, +EV, Wheeling, Bạc Nhớ
        ├── consensus_ensemble.js# Trí tuệ đám đông (Consensus AI), Ensemble 100 kỳ, Countdown
        └── notebook_bao7.js     # Sổ tay vé cá nhân (LocalStorage/Sync), Chiến lược Bao 7 & SMS
```

### Bảng Phân Nhiệm Chi Tiết 5 Module JavaScript:

| File Module | Số hàm | Trách nhiệm & Phạm vi nghiệp vụ | Phụ thuộc chính |
| :--- | :---: | :--- | :--- |
| **`core.js`** | **19** | Quản lý biến state (`appData`, `currentProductKey`, `currentView`), toán học PRNG (`createMulberry32`, `stringToSeedHash`), vòng lặp nạp dữ liệu `loadData()` đa fallback, điều hướng Sidebar & Game Dropdown, đăng ký PWA Service Worker. | DOM Ready, Lucide Icons |
| **`common_analytics.js`** | **21** | Hiển thị kết quả kỳ mới nhất (`renderHero`), dò vé (`checkTicket`), phân tích chu kỳ nhịp (`renderGapAnalysis`), ma trận đồng quy cặp số, biểu đồ chuông dải tổng Gaussian, mẫu hình liền kề/đầu số, giả lập nuôi số (`runSimulation`), bảng lịch sử toàn bộ kỳ quay. | `appData`, Chart.js |
| **`advanced_quant.js`** | **17** | Phân tích điểm rơi vị trí bóng & biên độ Span, chỉ số độ phức tạp Arithmetic Complexity (AC) & Delta gaps, ma trận chuyển trạng thái Markov, đo lường giá trị kỳ vọng đuôi số (+EV), dàn số rút gọn Wheeling và thống kê Bạc Nhớ. | `appData`, Chart.js |
| **`consensus_ensemble.js`** | **29** | Trí tuệ đám đông Consensus Hub (xếp hạng Top 15 bóng theo 5 mô hình độc lập), bộ sinh số vàng Ensemble gieo mầm cố định theo mã kỳ quay (`Draw ID Seed`), bảng đối soát 100 kỳ Walk-Forward, đồng hồ đếm ngược trực tiếp (`updateCountdown`), soi cầu bóng đặc biệt Power 6/55 và Power 5/35. | `createMulberry32`, `stringToSeedHash` |
| **`notebook_bao7.js`** | **26** | Quản lý sổ tay vé cá nhân (Lưu `localStorage`, hợp nhất vé Git, đồng bộ link 1-chạm Base64 `?sync=`, sao lưu/phục hồi file JSON), thuật toán tối ưu dàn Bao 7 (Bao 6 với 5/35), đối soát lãi/lỗ và bộ tạo cú pháp tin nhắn SMS 9969 chuẩn Vietlott. | `createMulberry32`, `stringToSeedHash` |

### Nguyên Tắc Giao Tiếp Phạm Vi Toàn Cục (Global Scope & Event Contract):
* Các module script được nạp tuần tự theo đúng thứ tự phụ thuộc: `core.js` -> `common_analytics.js` -> `advanced_quant.js` -> `consensus_ensemble.js` -> `notebook_bao7.js`.
* Toàn bộ hàm gọi từ sự kiện inline HTML (`onclick`, `onchange`) đều được gắn kết tự nhiên vào `window` scope của trình duyệt, đảm bảo 0 phụ thuộc vào bundler hoặc framework trung gian.
