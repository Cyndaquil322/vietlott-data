# Dedicated Bingo 18 Crawler & Sicbo Quantitative Analytics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng module crawler chuyên biệt siêu tốc `sync_bingo18.py` đồng bộ kết quả Bingo 18 (xúc xắc 10 phút/kỳ), xây dựng động cơ phân tích định lượng `bingo18_engine.py` (Cầu Lớn/Nhỏ, Chuông tổng Gaussian 3–18, Radar săn bão 1 ăn 120), và thiết kế giao diện web trực quan 3D trên điện thoại, với 100% Zero Mock Data.

**Architecture:**
- `src/vietlott/sync_bingo18.py`: Crawler chuyên biệt độc lập sử dụng `requests.Session` với retry và atomic write, cào trọn kết quả mới nhất trong $0.3$ giây bằng cơ chế so khớp `latest_id`.
- `src/vietlott/model/bingo18_engine.py`: Động cơ toán học Sicbo định lượng:
  - Phân tích chuỗi bệt Lớn/Nhỏ (Markov Streaks) và xác suất gãy cầu (Mean-Reversion).
  - Phân phối chuông tổng Gaussian $3 \dots 18$ ($\mu = 10.5, \sigma = 2.96$).
  - Radar cảnh báo điểm rơi Bão (Triple/Storm Hazard Density — chu kỳ lý thuyết 36 kỳ).
  - Tần suất 6 mặt xúc xắc và ma trận cặp đôi.
- `src/vietlott/render_web_data.py`: Tích hợp `process_bingo18` xuất dữ liệu chuẩn vào `vietlott_summary.json`.
- `docs/assets/js/`: Render giao diện trực quan xúc xắc 3D, roadmap chấm Lớn/Nhỏ, biểu đồ chuông tổng và cảnh báo bão.

**Tech Stack:** Python 3.11+, NumPy, BeautifulSoup4, pytest, vanilla JS, HTML/CSS 3D dice.

**Spec:** `docs/architecture/MATHEMATICAL_MODELS.md` (Mục Bingo 18 Sicbo Analytics).

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md Non-Negotiable Law).
- 100% số liệu được tính từ $36.000+$ kỳ quay thật trong `data/bingo18.jsonl`.
- Bảo toàn 100% tính tương thích ngược của schema JSON (`vietlott_summary.json`).
- Không thêm dependency bên ngoài mới.

---

### Task 1: Xây dựng Module Crawler Chuyên Biệt `src/vietlott/sync_bingo18.py` & Unit Tests

**Files:**
- Create: `src/vietlott/sync_bingo18.py`
- Create: `src/vietlott/tests/test_sync_bingo18.py`

**Interfaces:**
- Produces:
  - `sync_bingo18(file_path: Path = None, max_pages: int = 5) -> int`
  - `fetch_latest_bingo18_draws(session: requests.Session = None, page: int = 1) -> List[Dict[str, Any]]`

- [ ] **Step 1: Viết test TDD trong `test_sync_bingo18.py`**
  - Kiểm tra hàm bóc tách HTML trích xuất chính xác: ngày, mã kỳ (`#0185891`), 3 số xúc xắc $[X_1, X_2, X_3]$, tổng điểm, thế Lớn/Nhỏ/Hòa, và cờ bão (`is_triple`).
  - Kiểm tra cơ chế dừng sớm khi gặp `latest_id` đã có trong file.
  - Kiểm tra ghi file nguyên tử (`.tmp` $\to$ `.jsonl`).

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_sync_bingo18.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/sync_bingo18.py`**
  - Hiện thực `get_robust_session`, `load_existing_bingo18`, `save_bingo18_data`.
  - Gửi request đến `GameBingoCompareWebPart` với `GameId=8`.
  - Parse HTML bảng kết quả Vietlott.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_sync_bingo18.py -v`

---

### Task 2: Xây dựng Module Phân Tích Định Lượng Bingo 18 (`bingo18_engine.py`) & Unit Tests

**Files:**
- Create: `src/vietlott/model/bingo18_engine.py`
- Create: `src/vietlott/tests/test_bingo18_engine.py`

**Interfaces:**
- Produces:
  - `analyze_bingo18_streaks(records: List[Dict], window_len: int = 100) -> Dict[str, Any]`
  - `analyze_bingo18_sum_distribution(records: List[Dict], window_len: int = 1000) -> Dict[str, Any]`
  - `analyze_bingo18_storm_radar(records: List[Dict]) -> Dict[str, Any]`
  - `analyze_bingo18_dice_frequencies(records: List[Dict], window_len: int = 500) -> Dict[str, Any]`
  - `generate_bingo18_comprehensive_analytics(records: List[Dict]) -> Dict[str, Any]`

- [ ] **Step 1: Viết test TDD trong `test_bingo18_engine.py`**
  - Kiểm tra phân tích chuỗi bệt Lớn/Nhỏ: độ dài chuỗi hiện tại, xác suất bẻ cầu.
  - Kiểm tra phân phối tổng $3 \dots 18$: tổng đối xứng qua 10 và 11.
  - Kiểm tra radar bão: đếm số kỳ vắng bóng bão gần nhất (`current_storm_gap`), chu kỳ trung bình (~36 kỳ), mức độ cảnh báo.
  - Kiểm tra tần suất 6 mặt xúc xắc và các cặp nổ chung.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
  `pytest src/vietlott/tests/test_bingo18_engine.py -v`

- [ ] **Step 3: Triển khai mã nguồn `src/vietlott/model/bingo18_engine.py`**
  - Hiện thực các hàm giải tích thuần NumPy / Counter.
  - Xây dựng roadmap Lớn/Nhỏ (chuỗi chấm đỏ/xanh) cho 100 kỳ gần nhất.

- [ ] **Step 4: Chạy test để xác nhận PASS**
  `pytest src/vietlott/tests/test_bingo18_engine.py -v`

---

### Task 3: Tích Hợp Vào `render_web_data.py` và Pipeline `bin/github_data.sh`

**Files:**
- Modify: `src/vietlott/render_web_data.py` (Hàm `process_bingo18`)
- Modify: `src/vietlott/sync_live_data.py` (Thêm gọi `sync_bingo18`)
- Modify: `bin/github_data.sh`
- Create: `src/vietlott/tests/test_bingo18_integration.py`

**Interfaces:**
- Consumes: `generate_bingo18_comprehensive_analytics` từ `bingo18_engine`.
- Produces: Xuất cấu trúc dữ liệu giàu tính năng cho `products.bingo18` trong `vietlott_summary.json`.

- [ ] **Step 1: Viết test kiểm thử tích hợp trong `test_bingo18_integration.py`**
  - Kiểm tra `process_bingo18` xuất đầy đủ `streak_analytics`, `sum_distribution`, `storm_radar`, `dice_frequencies`.
  - Kiểm tra tính tương thích ngược của các trường cũ (`total_draws`, `latest`, `history`).

- [ ] **Step 2: Cập nhật `render_web_data.py`**
  - Nâng cấp `process_bingo18` gọi `generate_bingo18_comprehensive_analytics`.
- [ ] **Step 3: Cập nhật `sync_live_data.py` & `bin/github_data.sh`**
  - Tích hợp `sync_bingo18` vào luồng live sync chính.
- [ ] **Step 4: Chạy test tích hợp**
  `pytest src/vietlott/tests/test_bingo18_integration.py -v`

---

### Task 4: Thiết Kế Giao Diện Web Soi Cầu Bingo 18 3D & Đồng Bộ Tài Liệu

**Files:**
- Modify: `docs/assets/js/common_analytics.js` (và `assets/js/common_analytics.js`)
- Modify: `docs/assets/css/styles.css` (và `assets/css/styles.css`)
- Run: `python -m src.vietlott.render_web_data`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/SYSTEM_ARCHITECTURE.md`

- [ ] **Step 1: Cập nhật giao diện Web hiển thị Bingo 18**
  - Hiển thị 3 con xúc xắc 3D với các chấm đỏ/trắng chuẩn xúc xắc quốc tế.
  - Widget **"Bản Đồ Bắt Cầu Lớn / Nhỏ (Sicbo Roadmap)"**: Bảng ma trận chấm tròn trực quan (Đỏ = Lớn, Xanh = Nhỏ, Vàng = Bão).
  - Widget **"Biểu Đồ Chuông Tổng Gaussian 3–18"**: Thanh tiến trình tỷ lệ phần trăm phân bố tổng.
  - Widget **"Radar Cảnh Báo Săn Bão (Triple / Storm Alert)"**: Đồng hồ đo số kỳ chưa nổ bão và mức độ cảnh báo (Bình thường / Đang tích lũy / Điểm rơi cực đại).
  - Đồng bộ song song `docs/` và root.

- [ ] **Step 2: Chạy pipeline render dữ liệu thực tế**
  - Chạy `python -m src.vietlott.render_web_data`.
  - Xác nhận tạo thành công `vietlott_summary.json` với dữ liệu Bingo 18 phân tích sâu.

- [ ] **Step 3: Đồng bộ tài liệu kỹ thuật**
  - Bổ sung Mục 19 vào `docs/architecture/MATHEMATICAL_MODELS.md` (Đặc tả toán học Bingo 18 Sicbo Analytics).
  - Cập nhật `SYSTEM_ARCHITECTURE.md`.

- [ ] **Step 4: Chạy toàn bộ pytest suite**
  `pytest src/vietlott/tests/ -v` (Đảm bảo 150+ bài test PASS 100%).
