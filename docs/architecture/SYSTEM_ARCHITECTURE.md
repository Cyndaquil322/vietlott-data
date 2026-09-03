# KIẾN TRÚC TỔNG THỂ HỆ THỐNG (SYSTEM ARCHITECTURE)
## DỰ ÁN: VIETLOTT DATA ANALYTICS & LIVE EXPLORER

---

## 1. TỔNG QUAN HỆ THỐNG (HIGH-LEVEL OVERVIEW)

Hệ thống **Vietlott Analytics Hub** là nền tảng khai phá dữ liệu, phân tích xác suất thống kê và hỗ trợ chiến lược chọn số thông minh cho các loại hình xổ số ma trận của Vietlott (**Power 6/55, Mega 6/45, Power 5/35**).

Hệ thống được thiết kế theo kiến trúc **Serverless JAMstack & Hybrid Synchronization**:
1. **Data Ingestion Layer (Python Crawler):** Tự động thu thập dữ liệu kết quả từ cổng API chính thức của Vietlott qua các tác vụ định kỳ (GitHub Actions Cron).
2. **Analytical & Processing Engine (Python Data Pipeline):** Làm sạch, chuẩn hóa, phân tích chu kỳ nhịp, số gan, phân phối tổng, chuỗi Markov và kết xuất file tổng hợp siêu nhẹ (`docs/data/vietlott_summary.json`).
3. **Presentation Layer (Modern SPA & PWA):** Ứng dụng web đơn trang (Single Page Application) không phụ thuộc framework nặng, tích hợp Progressive Web App (PWA) để cài đặt toàn màn hình trên điện thoại.
4. **Hybrid Persistence & Synchronization Layer:** Kết hợp giữa `localStorage` trên máy người dùng, đồng bộ qua liên kết URL 1-chạm (`?sync=`) và kho lưu trữ tập trung trên Git (`data/saved_tickets.json`).

---

## 2. BIỂU ĐỒ LUỒNG DỮ LIỆU (DATA FLOW DIAGRAM)

```mermaid
flowchart TD
    subgraph "1. Data Acquisition (Cào dữ liệu)"
        A[Vietlott Official Servers] -->|AjaxPro POST Endpoints| B[src/vietlott/sync_live_data.py]
        B -->|Ghi nối tiếp JSON Lines| C[(data/*.jsonl)]
    end

    subgraph "2. Analytics Engine (Xử lý toán học)"
        C --> D[src/vietlott/render_web_data.py]
        D -->|Tính Gap, Pairs, Sum, Markov| E[docs/data/vietlott_summary.json]
        D -->|Đối soát kết quả vé Git| F[docs/data/saved_tickets.json]
    end

    subgraph "3. CI/CD & Automation (Tự động hóa)"
        G[.github/workflows/crawl.yaml] -->|Chạy 13:35, 18:45, 21:35 VN| B
        G --> D
        G -->|Git Commit & Push| H[GitHub Repository]
        H -->|Auto Deploy| I[GitHub Pages Hosting]
    end

    subgraph "4. User Interface & PWA (Phía Client)"
        I --> J[docs/index.html SPA]
        J -->|PWA Manifest + Service Worker| K[Mobile Home Screen Standalone App]
        J -->|Đọc kết quả| E
        J -->|Đọc vé Git| F
        J -->|Lưu sổ tay cá nhân| L[(Browser LocalStorage)]
        L -->|1-Click Sync URL / JSON| M[Thiết bị khác PC / Laptop]
    end
```

---

## 3. CẤU TRÚC THƯ MỤC CHI TIẾT (DIRECTORY TREE & RESPONSIBILITY)

```text
vietlott-data-master/
├── .agents/                        # Bộ kỹ năng AI chuyên sâu phục vụ phát triển & audit
│   └── skills/
│       ├── production-code-audit/  # Rà soát mã nguồn doanh nghiệp, tối ưu hiệu năng
│       ├── progressive-web-app/    # Hướng dẫn & cấu hình PWA, Service Worker, Manifest
│       ├── quant-analyst/          # Mô hình toán học định lượng, kiểm định giả thuyết
│       ├── ui-ux-pro-max/          # Thiết kế UI/UX mobile-first, hệ thống màu sắc
│       └── web-scraper/            # Kỹ thuật cào dữ liệu bền bỉ & chống nghẽn
│
├── .github/
│   └── workflows/
│       └── crawl.yaml              # Workflow GitHub Actions tự động hóa 4 khung giờ mỗi ngày
│
├── bin/
│   └── github_data.sh              # Bash script điều phối quy trình cào & xuất file trên CI runner
│
├── data/                           # Kho dữ liệu gốc dạng JSON Lines (Raw Historical Datasets)
│   ├── power655.jsonl              # Toàn bộ lịch sử quay thưởng Power 6/55 (từ kỳ 00001)
│   ├── power645.jsonl              # Toàn bộ lịch sử quay thưởng Mega 6/45 (từ kỳ 00001)
│   ├── power535.jsonl              # Lịch sử quay thưởng Power 5/35 (13h và 21h hàng ngày)
│   ├── 3d.jsonl                    # Dữ liệu Max 3D
│   ├── 3d_pro.jsonl                # Dữ liệu Max 3D Pro
│   └── saved_tickets.json          # Sổ tay vé được đồng bộ và lưu trữ trực tiếp trên Git
│
├── docs/                           # Thư mục xuất bản GitHub Pages (Web Root)
│   ├── data/
│   │   ├── vietlott_summary.json   # File JSON tổng hợp phân tích (360KB) nạp vào Web UI
│   │   └── saved_tickets.json      # File vé đồng bộ từ Git nạp vào Sổ Tay Web UI
│   ├── architecture/               # Hệ thống tài liệu kiến trúc & tham chiếu chi tiết
│   │   ├── SYSTEM_ARCHITECTURE.md  # File này
│   │   ├── DATA_PIPELINE_REFERENCE.md
│   │   ├── FRONTEND_COMPONENT_MAP.md
│   │   └── MATHEMATICAL_MODELS.md
│   ├── apple-touch-icon.png        # Icon Retina chuẩn 180x180 cho iPhone/iPad Standalone
│   ├── icon-192.png & icon-512.png # Icon PWA chuẩn cho Android / Desktop
│   ├── manifest.json               # Cấu hình PWA Web App Manifest
│   ├── sw.js                       # Service Worker xử lý Cache-first và Offline mode
│   └── index.html                  # Mã nguồn giao diện chính (SPA >5.100 dòng)
│
├── src/                            # Mã nguồn lõi Python
│   ├── vietlott/
│   │   ├── sync_live_data.py       # Script chính cào trực tiếp kết quả mới nhất từ Vietlott
│   │   ├── render_web_data.py      # Script tính toán phân tích toán học & kết xuất JSON
│   │   ├── crawler/                # Các lớp crawler module hóa cho từng sản phẩm
│   │   └── model/                  # Các module thuật toán & chiến lược dự đoán
│   └── render_readme.py            # Cập nhật README.md tự động
│
├── index.html                      # Bản sao của docs/index.html phục vụ root server
├── manifest.json & sw.js           # Bản sao PWA phục vụ root server
└── requirements.txt                # Danh sách thư viện phụ thuộc Python
```

---

## 4. BẢNG TIÊU CHUẨN CÔNG NGHỆ (TECH STACK)

| Tầng (Layer) | Công nghệ | Mục đích |
|---|---|---|
| **Crawler Engine** | Python 3.11+, `requests`, `beautifulsoup4` | Gọi API AjaxPro và bóc tách dữ liệu lồng cầu Vietlott |
| **Data Processing** | Python standard (`json`, `collections`, `itertools`, `math`) | Tính toán tần suất, ma trận nhịp gan, chuỗi Markov với độ phức tạp $O(N)$ |
| **CI/CD Automation** | GitHub Actions (`ubuntu-latest`) | Lên lịch chạy tự động 4 lần/ngày hoàn toàn miễn phí |
| **Web Presentation** | Pure Vanilla JavaScript ES6+, HTML5 | Hiệu năng render tối đa, không phát sinh overhead từ React/Vue |
| **CSS Framework** | Tailwind CSS (JIT Engine via CDN) | Giao diện tối hiện đại (Dark Theme) tối ưu cho màn hình OLED |
| **Data Visualization** | Chart.js 4.x + Lucide Icons + Canvas Confetti | Biểu đồ chuông Gaussian, đường xu hướng tổng, pháo hoa khi trúng |
| **PWA Standalone** | Service Worker Cache API + Web App Manifest | Cài đặt trực tiếp lên iPhone/Android, chạy tràn viền không URL bar |
| **Persistence** | HTML5 `localStorage` + URL Base64 Sync + Git JSON | Lưu trữ vé cá nhân, chuyển vé sang máy tính 1-chạm, backup JSON |
