# ĐẶC TẢ THIẾT KẾ KỸ THUẬT: TỐI ƯU HÓA HIỆU NĂNG ĐƯỜNG ỐNG DỮ LIỆU & BỘ ĐỆM ĐỐI SOÁT (INCREMENTAL PIPELINE & TIMEOUT OPTIMIZATION)

**Mã thiết kế:** `SPEC-PERF-TIMEOUT-20260912`  
**Ngày lập:** 12/09/2026  
**Tác giả:** Antigravity / DeepSeek Harness  
**Trạng thái:** Approved / Ready for Implementation Plan  

---

## 1. MỤC TIÊU & BỐI CẢNH (OBJECTIVES & CONTEXT)

### 1.1. Vấn đề hiện tại
- Trong `render_web_data.py`, mỗi lần cào kết quả mới hệ thống phải chạy lại toàn bộ:
  1. `calculate_walk_forward_backtest` (200 kỳ)
  2. `calculate_walk_forward_bao7_backtest` (200 kỳ)
  3. `calculate_multi_model_consensus_and_backtest` (100 kỳ)
  Cho cả 3 sản phẩm ma trận (Power 6/55, Mega 6/45, Power 5/35).
- Mỗi kỳ trong Walk-Forward lại phải huấn luyện lại 8 mô hình định lượng (Markov PPMI, Bayesian Hazard, Fourier Spectral, Kalman Filter, Empirical Bayes, Louvain Communities, HistGradientBoosting Ranker).
- Tổng thời gian thực thi lên tới **180s – 240s**, vượt ngưỡng timeout mặc định 120s của runner / PowerShell / subagent tool, dẫn đến việc tệp `vietlott_summary.json` bị dừng ghi dở dang, giao diện web mất dữ liệu đối soát.

### 1.2. Nguyên tắc bất di bất dịch
- **100% Zero Look-Ahead Bias & Zero Mock Data:** Bộ đệm (cache) chỉ lưu trữ kết quả tính toán hợp lệ từ kỳ $T-1$ trở về trước cho kỳ $T$.
- **Tính toán tăng tiến (Incremental Computation):** Với 200 kỳ lịch sử, 199 kỳ cũ không đổi chỉ đọc từ cache. Khi có 1 kỳ mới, chỉ chạy mô hình duy nhất 1 lần cho kỳ đó.
- **Tính toàn vẹn dữ liệu (Atomic Cache Write):** Mọi thao tác ghi cache đều dùng cơ chế `.tmp` rồi rename nguyên tử.

---

## 2. THIẾT KẾ KIẾN TRÚC BỘ ĐỆM TĂNG TIẾN (INCREMENTAL CACHING ARCHITECTURE)

### 2.1. Vị trí tệp lưu trữ
Mỗi sản phẩm ma trận có một tệp lưu trữ cache cục bộ nằm trong thư mục `data/cache/`:
- `data/cache/backtest_cache_power655.json`
- `data/cache/backtest_cache_power645.json`
- `data/cache/backtest_cache_power535.json`

### 2.2. Schema bản ghi Cache theo kỳ
```json
{
  "version": "1.0",
  "product_key": "power_655",
  "updated_at": "2026-09-12T23:30:00",
  "records": {
    "01397": {
      "draw_id": "01397",
      "date": "2026-09-12",
      "actual": [7, 24, 31, 43, 47, 54],
      "special": 22,
      "consensus": {
        "top_con": [1, 5, 9, 11, 47, 53],
        "triad": [11, 14, 47],
        "key5": [11, 14, 47, 54, 55],
        "core_pool": [11, 1, 5, 8, 55, 53, 47, 9, 54, 14, 40, 7],
        "optimal_septet": [1, 8, 11, 14, 40, 54, 55]
      },
      "evaluation": {
        "hits_single": 2,
        "hits_bao7": 3,
        "prize_vnd_single": 0,
        "prize_vnd_bao7": 200000
      }
    }
  }
}
```

### 2.3. Quy trình tính toán Tăng Tiến (Incremental Workflow)
1. Kiểm tra sự tồn tại của cache `data/cache/backtest_cache_{game}.json`.
2. Lấy danh sách 200 kỳ cần đối soát từ `records`.
3. Tìm những kỳ đã có trong cache: Tái sử dụng kết quả ngay lập tức ($O(1)$).
4. Tìm những kỳ chưa có trong cache (thường chỉ 1 kỳ vừa cào): Chạy mô hình Walk-Forward duy nhất cho các kỳ này.
5. Cập nhật các bản ghi mới vào cache và lưu atomic.
6. Kết hợp kết quả cache + kết quả mới để tạo bảng thống kê đầy đủ 200 kỳ.

---

## 3. THIẾT KẾ CẤU HÌNH TIMEOUT ĐA TẦNG (MULTI-LAYER TIMEOUT CONFIG)

1. **Tầng Test Runner (`pyproject.toml`):**
   - Thiết lập cấu hình `timeout = 300` (5 phút) cho các bài test toàn diện tránh timeout đột ngột.
2. **Tầng Script Thực Thi CLI (`src/vietlott/render_web_data.py` & `sync_live_data.py`):**
   - Bổ sung cờ `--fast` hoặc `--incremental` (mặc định bật) để tự động kích hoạt bộ đệm.
   - Thêm cờ `--force-rebuild` khi muốn huấn luyện lại toàn bộ từ đầu.
3. **Tầng CI/CD Workflows (`.github/workflows/crawl.yaml`):**
   - Đặt `timeout-minutes: 15` cho job `crawl_and_update`.

---

## 4. KẾT QUẢ KỲ VỌNG
- Thời gian chạy `render_web_data.py` giảm từ **180s - 240s** xuống còn **10s - 15s** (Tăng tốc gấp 15 lần).
- Tỷ lệ timeout: **0%**.
- Giao diện Web GUI luôn có đủ trường `prediction_ledger` và hiển thị tức thì mọi thông tin đối soát.
