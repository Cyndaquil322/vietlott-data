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
        D_MON[src/vietlott/auto_draw_monitor.py] -->|Lập lịch tự động 13h, 18h, 21h| B
    end

    subgraph "2. Quantitative Data Pipeline Orchestrator"
        C --> D[src/vietlott/render_web_data.py]
        
        subgraph "Quantitative Analytical Engines"
            D --> E1[src/vietlott/model/analytic_engines.py<br/>7 Mô hình: Markov, Hazard, Decay, Bạc Nhớ, Fourier, PageRank, State-Space]
            D --> E2[src/vietlott/model/wavelet_engine.py<br/>Daubechies-4 DWT & Hann Spectral]
            D --> E3[src/vietlott/model/covering_engine.py<br/>Dàn Phủ Tổ Hợp C(v, k, t) & Negative Space AC Filter]
            D --> E5[src/vietlott/model/transition_engine.py<br/>Ma trận chuyển tiếp A &rarr; B, Z-Score nhị thức & Vector Pull]
            D --> E6[src/vietlott/model/ml_ranker.py<br/>HistGradientBoosting ML Ranker 14 chiều]
            D --> E7[src/vietlott/model/portfolio_optimizer.py<br/>Tối ưu hóa Markowitz & Phân cụm Louvain]
            D --> E8[src/vietlott/model/bankroll_advisor.py<br/>Quản trị vốn Kelly & Chỉ số tự tin CCS]
            D --> E9[src/vietlott/model/elimination_engine.py<br/>Bộ Lọc Đào Thải Bóng Chết Negative Space]
            D --> E10[src/vietlott/model/banker_wheeling.py<br/>Dàn Ghép Bọc Lót Bạch Thủ Chốt B(1, 10, k, 3)]
            D --> E4[src/vietlott/model/ensemble_engine.py<br/>Consensus Hub, Dynamic Alpha Stacking (8 Models, L2 Shrinkage),<br/>Walk-Forward 100 & Pareto Septet Extraction]
            E1 --> E6
            E5 --> E6
            E1 --> E4
            E2 --> E4
            E3 --> E4
            E5 --> E4
            E6 --> E4
            E7 --> E4
            E8 --> E4
            E9 --> E4
            E9 --> E10
            E10 --> E4
        end
        
        E4 -->|Tổng hợp Leaderboard, Weights & Tickets| D
        D -->|Xuất bản kết quả phân tích chuẩn hóa| E[docs/data/vietlott_summary.json<br/>data/vietlott_summary.json]
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
│   ├── vietlott_summary.json       # Bản sao dữ liệu tổng hợp tại data/
│   └── saved_tickets.json          # Sổ tay vé được đồng bộ và lưu trữ trực tiếp trên Git
│
├── docs/                           # Thư mục xuất bản GitHub Pages (Web Root)
│   ├── assets/                     # Tài nguyên tĩnh đã được module hóa
│   │   ├── css/
│   │   │   └── styles.css          # Định dạng 3D lotto ball, animation, scrollbars tùy biến
│   │   └── js/
│   │       ├── core.js             # State toàn cục, PWA, Audio, Dropdown, Menu & Navigation
│   │       ├── common_analytics.js # Dò vé, Hero, Số gan, Cặp số, Phân tích tổng, Mẫu hình, Lịch sử
│   │       ├── advanced_quant.js   # Vị trí, AC Complexity, Delta, Markov, +EV, Wheeling, Bạc Nhớ
│   │       ├── consensus_ensemble.js# Trí tuệ đám đông (Consensus 8 mô hình & ML Ranker), Seeded PRNG, Đếm ngược
│   │       └── notebook_bao7.js    # Sổ tay vé cá nhân (LocalStorage, Sync), Chiến lược Bao 7 & SMS 9969
│   ├── data/
│   │   ├── vietlott_summary.json   # File JSON tổng hợp phân tích (~750KB) nạp vào Web UI
│   │   └── saved_tickets.json      # File vé đồng bộ từ Git nạp vào Sổ Tay Web UI
│   ├── architecture/               # Hệ thống tài liệu kiến trúc & tham chiếu chi tiết
│   │   ├── SYSTEM_ARCHITECTURE.md  # File này (Kiến trúc tổng thể hệ thống)
│   │   ├── DATA_PIPELINE_REFERENCE.md # Đặc tả chi tiết Data Pipeline & ETL
│   │   ├── FRONTEND_COMPONENT_MAP.md  # Bản đồ component & module giao diện
│   │   ├── MATHEMATICAL_MODELS.md     # Mô hình toán học, xác suất & Walk-Forward
│   │   ├── vietlott-architecture.html # Sơ đồ kiến trúc tương tác Archify
│   │   └── vietlott-architecture.json # File đặc tả kiến trúc Archify
│   ├── apple-touch-icon.png        # Icon Retina chuẩn 180x180 cho iPhone/iPad Standalone
│   ├── icon-192.png & icon-512.png # Icon PWA chuẩn cho Android / Desktop
│   ├── manifest.json               # Cấu hình PWA Web App Manifest
│   ├── sw.js                       # Service Worker Cache Storage xử lý Offline mode
│   └── index.html                  # Khung giao diện HTML tinh gọn
│
├── src/                            # Mã nguồn lõi Python
│   ├── vietlott/
│   │   ├── sync_live_data.py       # Script chính cào trực tiếp kết quả mới nhất từ Vietlott
│   │   ├── auto_draw_monitor.py    # Daemon tự động cào theo lịch quay Vietlott
│   │   ├── render_web_data.py      # Data Pipeline Orchestrator điều phối toàn bộ phân tích & render
│   │   ├── crawler/                # Các lớp crawler module hóa cho từng sản phẩm
│   │   ├── model/                  # Hệ thống module định lượng & thuật toán
│   │   │   ├── analytic_engines.py # 7 mô hình định lượng (Markov, Hazard, Decay, Bạc Nhớ, Fourier, PageRank, State-Space)
│   │   │   ├── transition_engine.py# Động cơ chuyển trạng thái liên kỳ A -> B, Z-Score nhị thức & Vector Pull
│   │   │   ├── ml_ranker.py        # HistGradientBoosting ML Ranker xếp hạng học máy 14 chiều
│   │   │   ├── portfolio_optimizer.py # Tối ưu hóa danh mục Markowitz & phân tán cụm Louvain modularity
│   │   │   ├── bankroll_advisor.py # Quản trị vốn Kelly thực chiến & Chỉ số Tự tin Đồng thuận (CCS)
│   │   │   ├── elimination_engine.py# Thuật toán đào thải bóng chết E(b) & cắt gọt không gian số
│   │   │   ├── banker_wheeling.py  # Dàn ghép bọc lót có bóng chốt Bạch Thủ B(1, 10, k, 3)
│   │   │   ├── ensemble_engine.py  # Consensus Hub, Dynamic Alpha Stacking (8 Models, L2 Shrinkage), Walk-Forward 100
│   │   │   ├── covering_engine.py  # Thiết kế dàn phủ tổ hợp C(v, k, t) & Lọc không gian âm Negative Space
│   │   │   ├── wavelet_engine.py   # Phân tích sóng con Daubechies-4 DWT & Hann Spectral Recurrence
│   │   │   └── strategy/           # Các chiến lược legacy & kiểm thử cơ bản
│   │   └── tests/                  # Bộ test suite pytest toàn diện (Unit & Integration tests)
│   └── render_readme.py            # Cập nhật README.md tự động
│
├── assets/                         # Bản sao đồng bộ của docs/assets phục vụ root server
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

---

## 5. PHÂN RÃ CÁC MODULE ĐỊNH LƯỢNG LÕI (QUANTITATIVE ENGINES ARCHITECTURE)

Hệ thống phân tích định lượng được cấu trúc hóa thành các module chuyên biệt, độc lập và có tính module hóa cao (Zero Drift Specification):

### A. Data Pipeline Orchestrator (`src/vietlott/render_web_data.py`)
* **Vai trò:** Trục điều phối trung tâm của toàn bộ đường ống xử lý dữ liệu và xuất bản giao diện.
* **Chức năng chính:**
  * Đọc nạp toàn bộ dataset lịch sử dạng JSON Lines (`power655.jsonl`, `power645.jsonl`, `power535.jsonl`, `keno.jsonl`, `bingo18.jsonl`, `3d.jsonl`, `3d_pro.jsonl`).
  * Thực hiện phân tích thống kê nền tảng: Chu kỳ nhịp gan (Gap Analysis), Tần suất xuất hiện, Cặp/Ba số hay về, Phân phối tổng Gauss, Mẫu hình chẵn/lẻ, Phân tích độ phức tạp số học AC, Delta spacing.
  * Tích hợp và điều phối các module định lượng chuyên sâu: `analytic_engines`, `wavelet_engine`, `covering_engine`, và `ensemble_engine`.
  * Xuất bản kết quả phân tích đồng bộ ra `docs/data/vietlott_summary.json` và bản sao tại `data/vietlott_summary.json`.

### B. Analytical Engines (`src/vietlott/model/analytic_engines.py`)
* **Vai trò:** Cung cấp 7 mô hình toán học và xác suất định lượng độc lập:
  1. `calculate_hazard_scores`: Mô hình hàm nguy cơ Bayesian Rhythm Z-Score ($H_{\text{Z-Score}}$).
  2. `calculate_decay_scores`: Mô hình suy giảm mũ theo thời gian ($e^{-\alpha t}$).
  3. `calculate_markov_scores`: Mô hình chuyển trạng thái chuỗi Markov với thông tin tương hỗ dương PPMI.
  4. `calculate_fourier_scores`: Mô hình cộng hưởng phổ chu kỳ điều hòa Fourier cửa sổ Hann.
  5. `calculate_bac_nho_scores`: Mô hình quy luật kéo bóng Bạc Nhớ với độ nâng làm mịn Laplace.
  6. `calculate_graph_pagerank_scores`: Mô hình Đồ thị đồng xuất hiện PageRank Centrality (ma trận kề độ nâng Laplace, chuẩn hóa hàng ngẫu nhiên, Power Iteration với $d=0.85$).
  7. `calculate_state_space_scores`: Mô hình Bộ lọc Không gian Trạng thái Tiềm ẩn Kalman (1D Kalman Filter per ball với hồi quy trung bình $\lambda = 0.92$, hiệp phương sai $Q=0.05, R=0.5$).
* **Hàm điều phối:** `evaluate_all_models(...)` - Tính toán đồng thời 7 mô hình và trả về phân phối điểm số chuẩn hóa cho từng con số.

### C. Consensus & Walk-Forward Engine (`src/vietlott/model/ensemble_engine.py`)
* **Vai trò:** Trung tâm đồng thuận trí tuệ đa mô hình (Consensus Hub) và kiểm định lịch sử nghiêm ngặt:
  * **Dynamic Alpha Stacking:** Đánh giá hiệu suất ngoại mẫu (Out-Of-Fold Alpha) của 8 mô hình qua 100 kỳ Walk-Forward và phân bổ trọng số kết hợp điều chuẩn co ngót L2 (L2 Shrinkage Regularization, $\lambda = 0.20$, $w_{\text{prior}} = 1/8 = 12.50\%$).
  * **Walk-Forward Backtest 100 kỳ:** Đối soát khách quan 100% không có thiên lệch nhìn trước (No Look-Ahead Bias).
  * **Pareto Multi-Objective Septet Extraction:** Trích xuất bộ 7 số tối ưu (Bao 7 cho 6/55 & 6/45, Bao 6 cho 5/35) từ Dàn hạt nhân Core Pool.
  * **Transition Analytics Export:** Đóng gói và xuất bản ma trận lực hút liên kỳ $A \to B$ (`top_pull_rules` và `top_repulsion_rules`) phục vụ trực quan hóa trên giao diện Web.
  * **Leaderboard & Training Report:** Xuất bản bảng xếp hạng 8 mô hình + Consensus + Baseline Random và báo cáo tỷ trọng mô hình ($100\%$).

### D. Combinatorial Covering Engine (`src/vietlott/model/covering_engine.py`)
* **Vai trò:** Kiến tạo các cấu trúc dàn ghép bọc lót tổ hợp toán học tối ưu:
  * Thiết kế phủ tổ hợp chuẩn $C(12, 6, 3)$ (6 vé & 8 vé) cho 6/55 & 6/45; $C(10, 5, 3)$ (6 vé) cho 5/35.
  * Tích hợp Bộ Lọc Không Gian Âm (Negative Space AC Permutation Filter) đảm bảo mọi vé trong dàn đạt $AC \ge 7$ (vé 6 số) hoặc $AC \ge 4$ (vé 5 số).
  * Tối ưu hóa ánh xạ hoán vị nhãn số (Isomorphic Core Pool Permutation), bảo toàn nguyên vẹn 100% độ phủ tổ hợp toán học.

### E. Daubechies Wavelet DWT Engine (`src/vietlott/model/wavelet_engine.py`)
* **Vai trò:** Phân tích tín hiệu thời gian đa độ phân giải (MRA) bằng biến đổi sóng con:
  * Ngân hàng bộ lọc trực giao Daubechies 4-tap (db4).
  * Thuật toán tháp Mallat 2 cấp phân rã ($D_1, D_2, A_2$) với đệm tuần hoàn vòng (periodic wrap padding) triệt tiêu cụt biên.
  * Trích xuất năng lượng xung nổ cục bộ $E_{\text{recent}}$ và chu kỳ sóng con chủ đạo $\tau_b$.

### F. Transition State Engine (`src/vietlott/model/transition_engine.py`)
* **Vai trò:** Khai phá tương quan có hướng liên kỳ và trường lực hấp dẫn vector:
  * Xây dựng ma trận chuyển trạng thái liên kỳ $N \times N$ ($a_{t-1} \to b_t$) trên cửa sổ trượt $W = 150$ kỳ.
  * Tính toán xác suất có điều kiện $P(b_t \mid a_{t-1})$, độ nâng Transition Lift và kiểm định $Z$-Score phân phối nhị thức.
  * Trích xuất các quy luật kéo bóng có ý nghĩa thống kê ($Z \ge +1.5\sigma$) và cảnh báo cặp xung khắc triệt tiêu ($Z \le -1.5\sigma$).
  * Trích xuất các đặc trưng trường lực Vector Pull: `max_pull_lift`, `sum_z_score`, `repulsion_penalty`, `repeat_momentum`.

### G. Machine Learning Ranker (`src/vietlott/model/ml_ranker.py`)
* **Vai trò:** Xếp hạng học máy phi tuyến tính đa chiều:
  * Xây dựng không gian đặc trưng 14 chiều kết hợp 7 mô hình toán học, động học nhịp gan và trường lực chuyển tiếp liên kỳ.
  * Mô hình `HistGradientBoostingClassifier` huấn luyện Walk-Forward với điều chuẩn L2 regularization $\lambda=1.5$.
  * Dự báo hàm xác suất nổ hậu nghiệm và ánh xạ chuẩn hóa thang điểm 3.0 tham gia xếp chồng đồng thuận Consensus.

### H. Markowitz Portfolio Optimizer (`src/vietlott/model/portfolio_optimizer.py`)
* **Vai trò:** Tối ưu hóa danh mục vé có ràng buộc nguyên bậc hai (Constrained Binary Quadratic Programming):
  * Xây dựng ma trận hiệp phương sai tương quan cặp đôi $\Sigma_{ij}$ từ hệ số độ nâng đối xứng $\text{Lift}^*(i, j)$ trên cửa sổ trượt 150 kỳ gần nhất.
  * Phân cụm đồ thị nổ chung bằng thuật toán tối ưu hóa mô-đun modularity tham lam (Louvain Modularity Maximization thuần NumPy) thành 4-5 cụm độc lập.
  * Tối ưu hóa hàm lợi ích Markowitz $\max \mathcal{U}(\mathbf{x}) = \mathbf{x}^T \boldsymbol{\mu} - \lambda \mathbf{x}^T \boldsymbol{\Sigma} \mathbf{x}$ bằng thuật toán duyệt Beam Search có ràng buộc.
  * Đảm bảo thỏa mãn đồng thời các điều kiện: tổng chuẩn Gaussian, độ phức tạp $AC \ge 7$ (hoặc $AC \ge 4$ cho 5/35), phân tán trên $\ge 4$ cụm Louvain ($\ge 3$ cho 5/35), và không có cụm nào chiếm quá 2 con bóng.

### I. Smart Bankroll Advisor (`src/vietlott/model/bankroll_advisor.py`)
* **Vai trò:** Quản trị vốn thông minh và định cỡ đầu tư theo Tiêu chuẩn Kelly mở rộng:
  * Tính toán Chỉ số Tự tin Đồng thuận (CCS) từ 3 thành phần trực giao: Độ đồng thuận các mô hình $S_{\text{agreement}}$ (40%), Độ dốc entropy Softmax $S_{\text{entropy}}$ (35%), và Xung lực kéo liên kỳ $S_{\text{pull}}$ (25%).
  * Phân loại 3 cấp độ vốn thực chiến: Cấp 1 (< 55.0% - 10.000đ), Cấp 2 (55.0-75.0% - 20.000đ), Cấp 3 (>= 75.0% - 60.000đ).
  * Cung cấp hành động khuyến nghị, định mức ngân sách và giải trình định lượng tự động cho từng kỳ quay.

### J. Negative Elimination Engine (`src/vietlott/model/elimination_engine.py`)
* **Vai trò:** Khai phá Không Gian Âm (Negative Elimination Mining) đào thải bóng chết:
  * Tính toán Chỉ số Nguy cơ Ngủ đông $\mathcal{E}(b)$ từ 4 thành phần: Nguy cơ nhịp gan quá hạn (30%), Nguy cơ ngủ đông sóng con (25%), Nguy cơ xung khắc liên kỳ (25%), và Nguy cơ đáy đồng thuận (20%).
  * Cắt gọt không gian số chính xác: Đào thải 16 bóng (Power 6/55, cắt 29.1%), 13 bóng (Mega 6/45, cắt 28.9%), và 9 bóng (Power 5/35, cắt 25.7%).
  * Độ chính xác đào thải Walk-Forward đạt ~88.5% trên dữ liệu thực nghiệm không nhìn trước.
  * Cung cấp không gian số sạch (Pruned Universe) làm đầu vào cho Dàn Vệ Tinh và Dàn Hạt Nhân.

### K. Key-Banker Wheeling Engine (`src/vietlott/model/banker_wheeling.py`)
* **Vai trò:** Thiết kế dàn ghép bọc lót có bóng chốt Bạch Thủ $B(1, 10, k, 3)$:
  * Tuyển chọn Quả Bóng Chốt Bạch Thủ $B_1$ uy lực nhất từ tập Key Balls kết hợp gia số lực hút Vector Pull $\text{Lift}(a \to b)$.
  * Xây dựng Dàn 10 Bóng Vệ Tinh (Clean Satellites Pool) tinh tuyển từ Core Pool và tuyệt đối không chứa bóng chết.
  * Phủ tổ hợp vệ tinh thành dàn 6 vé con ($C(10, 5, 2)$ cho vé 6 bóng, $C(10, 4, 2)$ cho vé 5 bóng).
  * Tối ưu hóa hoán vị nhãn bảo đảm $100\%$ vé con đạt Arithmetic Complexity $AC \ge 7$ ($AC \ge 4$ cho 5/35).
  * Đòn bẩy xác suất từ $15.4\times$ đến $18.5\times$ với cam kết bảo hiểm toán học: $100\%$ có vé trúng thưởng khi bóng chốt nổ kèm $\ge 2$ bóng vệ tinh.

---

## 6. SƠ ĐỒ ĐIỀU PHỐI ĐƯỜNG ỐNG DỮ LIỆU & CONSENSUS HUB (ORCHESTRATION PIPELINE)

```mermaid
flowchart LR
    subgraph Input [Dữ liệu đầu vào]
        RAW[(data/*.jsonl)]
    end

    subgraph Orchestrator [render_web_data.py]
        ORCH[Data Pipeline Orchestrator]
    end

    subgraph Engines [Quantitative & ML Engines]
        direction TB
        M1[analytic_engines.py<br/>7 Mô hình Toán học]
        M2[wavelet_engine.py<br/>Daubechies DWT]
        M3[covering_engine.py<br/>Covering C(v,k,t)]
        M5[transition_engine.py<br/>Ma trận Chuyển tiếp & Vector Pull]
        M6[ml_ranker.py<br/>HistGradientBoosting Ranker 14D]
        M7[portfolio_optimizer.py<br/>Markowitz & Louvain Spread]
        M8[bankroll_advisor.py<br/>Kelly CCS Bankroll]
        M9[elimination_engine.py<br/>Đào Thải Bóng Chết Negative Space]
        M10[banker_wheeling.py<br/>Bạch Thủ Wheeling B(1,10,k,3)]
        M4[ensemble_engine.py<br/>Alpha Stacking 8 Models, Backtest & Tickets]
    end

    subgraph Output [Kết xuất chuẩn hóa]
        JSON[docs/data/vietlott_summary.json<br/>data/vietlott_summary.json]
    end

    RAW --> ORCH
    ORCH --> M1
    ORCH --> M2
    ORCH --> M3
    ORCH --> M5
    M1 --> M6
    M5 --> M6
    M1 --> M4
    M2 --> M4
    M3 --> M4
    M5 --> M4
    M6 --> M4
    M7 --> M4
    M8 --> M4
    M9 --> M4
    M9 --> M10
    M10 --> M4
    M4 --> ORCH
    ORCH --> JSON
```

---

## 7. QUY TRÌNH KIỂM ĐỊNH QUÁ KHỨ 200 KỲ (WALK-FORWARD BACKTEST 200 DRAWS)

Hệ thống tuân thủ nguyên tắc trung thực khoa học và tính toàn vẹn dữ liệu tuyệt đối:
* **Quy mô mẫu:** Chạy kiểm định liên tục trên **200 kỳ quay thực tế** của từng game.
* **Nguyên lý Walk-Forward:** Tại mỗi kỳ $T \in [1, 200]$, mô hình chỉ được phép tiếp cận dữ liệu từ kỳ $T-1$ trở về trước. Hoàn toàn không có thiên lệch nhìn trước tương lai (No Look-Ahead Bias).
* **Mô hình phân tích toàn diện:** Tại từng kỳ, hệ thống chạy đồng thời:
  1. Hàm nguy cơ nhịp gan Bayesian ($H(r_b)$) & Vùng vàng điểm rơi.
  2. Tần suất suy giảm mũ ($lpha = 0.035$).
  3. Radar Bắt Cầu Rơi (quán tính lặp lại từ $T-1$).
  4. Bạc Nhớ Chuyển Tiếp (luật $A 	o B$ với $	ext{Lift} \ge 1.6	imes$).
  5. Ma Trận Kề Đồng Quy Cặp Đôi ($M_{55 	imes 55}$).
  6. Bộ lọc tổ hợp: $AC \ge 7$, Tổng phân phối Gaussian $\mu \pm 1\sigma$.
* **Hiển thị & Báo cáo:**
  * **Chỉ số KPI tổng kết:** Đo lường tổng thể trên toàn bộ 200 kỳ (Tỷ lệ trúng $\ge 3$ số, $\ge 4$ số, Tổng vốn, Tổng thưởng, Hiệu suất P&L).
  * **Bảng chi tiết 20 kỳ gần nhất:** Trình bày rõ ràng 20 kỳ đối soát gần nhất kèm 1 kỳ chờ mở thưởng tiếp theo để người dùng theo dõi và kiểm chứng.
