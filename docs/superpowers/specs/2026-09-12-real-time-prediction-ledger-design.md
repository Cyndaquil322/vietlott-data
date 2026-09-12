# ĐẶC TẢ THIẾT KẾ KỸ THUẬT: BỘ NHỚ LƯU TRỮ & ĐỐI SOÁT DỰ ĐOÁN THỰC TẾ (REAL-TIME PREDICTION LEDGER)

**Mã thiết kế:** `SPEC-PREDICTION-LEDGER-20260912`  
**Ngày lập:** 12/09/2026  
**Tác giả:** Antigravity / DeepSeek Harness  
**Trạng thái:** Approved / Ready for Implementation  

---

## 1. MỤC TIÊU & BỐI CẢNH (OBJECTIVES & CONTEXT)

### 1.1. Vấn đề hiện tại
Hiện tại hệ thống Vietlott Analytics & Live Explorer đã sở hữu các mô hình định lượng cao cấp (Markov PPMI, Bayesian Hazard, Wavelet Spectral, Louvain Graph, ML Ranker) và backtest giả lập 100 kỳ quá khứ (`history_walk_forward`). Tuy nhiên, người dùng cần một **bộ nhớ lưu vết thực tế ngoài đời thực (Out-of-sample Real-time Ledger)**:
- Mỗi khi có kết quả mới và hệ thống sinh dự đoán cho kỳ kế tiếp, bộ số đó phải được **"niêm phong" (Snapshot)** vào một tệp dữ liệu lưu trữ cố định trước giờ quay.
- Khi kỳ quay thực tế diễn ra, hệ thống tự động mở niêm phong đối soát xem dự đoán chính xác bao nhiêu phần trăm, trúng bao nhiêu bóng, đạt giải thưởng gì theo luật Vietlott.
- Toàn bộ lịch sử đối soát phải được hiển thị minh bạch 100% trên Web GUI để người dùng thẩm định hiệu quả thực tế của từng phương pháp đánh (Vé Vàng 6 số, Bao 7, Dàn Banker Wheeling).

### 1.2. Nguyên tắc bất di bất dịch
- **Không Look-Ahead Bias:** Tuyệt đối không dùng dữ liệu tương lai để dự đoán quá khứ.
- **Không Mock Data:** Toàn bộ lịch sử đối soát và P&L phải xuất phát từ thuật toán thật và kết quả cào thật.
- **Deterministic Seeding:** Dự đoán của mỗi kỳ là hàm đơn ánh (deterministic) theo lịch sử tại thời điểm đó.
- **Zero Data Loss:** Cơ chế ghi tệp nguyên tử (Atomic Write) bảo vệ toàn vẹn dữ liệu.

---

## 2. KIẾN TRÚC PHÂN TẦNG DỮ LIỆU (DATA ARCHITECTURE)

### 2.1. Tệp dữ liệu gốc (Raw Data Layer)
Mỗi game ma trận có một tệp JSONL độc lập trong thư mục `data/`:
- `data/prediction_ledger_power655.jsonl`
- `data/prediction_ledger_power645.jsonl`
- `data/prediction_ledger_power535.jsonl`

### 2.2. Schema bản ghi theo kỳ (Record Schema)
```json
{
  "draw_id": "01397",
  "draw_date": "2026-09-12",
  "target_draw_id": "01397",
  "created_at": "2026-09-10T20:00:00",
  "verified_at": "2026-09-12T18:45:00",
  "status": "verified",
  "actual_result": [7, 24, 31, 43, 47, 54],
  "special_ball": 22,
  "predictions": {
    "golden_ticket": {
      "numbers": [1, 5, 9, 11, 47, 53],
      "cost_vnd": 10000,
      "hits": 2,
      "matched_balls": [47, 53],
      "prize_tier": "Không trúng",
      "prize_vnd": 0
    },
    "septet_bao7": {
      "numbers": [1, 8, 11, 14, 40, 54, 55],
      "cost_vnd": 70000,
      "hits": 3,
      "matched_balls": [14, 54, 55],
      "prize_tier": "Giải Ba (Bao 7: 4 giải)",
      "prize_vnd": 200000
    },
    "banker_wheeling": {
      "banker": 11,
      "tickets_count": 6,
      "cost_vnd": 60000,
      "best_hits": 3,
      "winning_tickets_count": 1,
      "total_prize_vnd": 50000
    },
    "core_pool": {
      "pool_size": 12,
      "numbers": [11, 1, 5, 8, 55, 53, 47, 9, 54, 14, 40, 7],
      "hits": 4,
      "matched_balls": [7, 14, 47, 54]
    }
  },
  "summary_metrics": {
    "total_investment_vnd": 140000,
    "total_return_vnd": 250000,
    "net_profit_vnd": 110000,
    "roi_pct": 78.57,
    "has_winning_prize": true
  }
}
```

---

## 3. THUẬT TOÁN ĐỐI SOÁT & TÍNH THƯỞNG (SCORING ENGINE)

Module trung tâm: `src/vietlott/model/prediction_evaluator.py`

### 3.1. Luật tính thưởng Power 6/55
- Trúng 3 bóng: 50.000 VNĐ (Giải Ba)
- Trúng 4 bóng: 500.000 VNĐ (Giải Nhì)
- Trúng 5 bóng: 40.000.000 VNĐ (Giải Nhất)
- Trúng 5 bóng + Trúng bóng đặc biệt: Jackpot 2 (Ước tính quy đổi tối thiểu 3.000.000.000 VNĐ)
- Trúng 6 bóng: Jackpot 1 (Ước tính quy đổi tối thiểu 30.000.000.000 VNĐ)

### 3.2. Luật tính thưởng Mega 6/45
- Trúng 3 bóng: 30.000 VNĐ (Giải Ba)
- Trúng 4 bóng: 300.000 VNĐ (Giải Nhì)
- Trúng 5 bóng: 10.000.000 VNĐ (Giải Nhất)
- Trúng 6 bóng: Jackpot (Tối thiểu 12.000.000.000 VNĐ)

### 3.3. Luật tính thưởng Power 5/35
- Khớp chính xác ma trận 5 bóng chính + bóng đặc biệt theo quy định Vietlott.

### 3.4. Cơ chế tính thưởng vé Bao 7
- Áp dụng đúng công thức tổ hợp $C_7^6$:
  - Trúng 3 số: Được tính là 4 giải Ba ($4 \times 50.000 = 200.000$ VNĐ đối với 6/55).
  - Trúng 4 số: Được tính là 3 giải Nhì + 4 giải Ba ($3 \times 500.000 + 4 \times 50.000 = 1.700.000$ VNĐ).
  - Trúng 5 số: Được tính là 2 giải Nhất + 5 giải Nhì ($2 \times 40.000.000 + 5 \times 500.000 = 82.500.000$ VNĐ).
  - Trúng 6 số: Được tính là 1 Jackpot + 6 giải Nhất.

---

## 4. TÍCH HỢP ĐƯỜNG ỐNG TỰ ĐỘNG (PIPELINE HOOKS)

### 4.1. Module điều phối: `src/vietlott/prediction_tracker.py`
Cung cấp các hàm API chính:
1. `seed_historical_ledger(game_key, draws_count=35)`: Chạy Walk-Forward nghiêm ngặt từ 35 kỳ trước để dựng sẵn lịch sử đối soát.
2. `verify_and_update_ledger(game_key, latest_draw)`: Mở niêm phong kỳ vừa cào, tính toán số trúng và tiền thưởng.
3. `snapshot_next_prediction(game_key, target_draw_id, predicted_tickets)`: Chốt bộ số cho kỳ sắp tới ở trạng thái `pending`.
4. `get_ledger_summary_for_web(game_key, limit=50)`: Trích xuất lịch sử và tính toán KPI tổng hợp đưa vào web data.

### 4.2. Móc nối vào `sync_live_data.py`
- Ngay sau khi cào xong từng game, gọi `verify_and_update_ledger()` để đối soát nếu kỳ đó vừa có kết quả.
- Sau đó gọi `snapshot_next_prediction()` để niêm phong kỳ tiếp theo.

### 4.3. Móc nối vào `render_web_data.py`
- Nhúng toàn bộ kết quả tổng hợp vào `docs/data/vietlott_summary.json` dưới key `prediction_ledger` cho mỗi sản phẩm:
  ```json
  "prediction_ledger": {
    "total_tracked_draws": 35,
    "overall_win_rate_pct": 42.8,
    "golden_ticket_avg_hits": 1.15,
    "septet_avg_hits": 1.48,
    "cumulative_pnl": {
      "total_spent": 4900000,
      "total_won": 3200000,
      "net_profit": -1700000,
      "roi_pct": -34.7
    },
    "current_pending_draw": {
      "draw_id": "01398",
      "status": "pending",
      "tickets": { ... }
    },
    "history": [ ... ]
  }
  ```

---

## 5. THIẾT KẾ GIAO DIỆN WEB GUI (FRONTEND COMPONENT)

### 5.1. Vị trí hiển thị
Thêm một section chuyên biệt trong `docs/index.html`:
`#prediction-ledger-section` (Thẻ Card: **📋 Nhật Ký Đối Soát Dự Đoán Thực Tế**).

### 5.2. Các thành phần giao diện
1. **Khối Thống kê Hiệu suất (Metric Cards)**:
   - Tỷ lệ có giải thưởng thực tế (Win Rate %).
   - Tỷ lệ hoàn vốn (ROI %) và Tổng P&L (VNĐ).
   - Chuỗi trúng thưởng gần nhất (Winning Streak).
2. **Kỳ sắp quay (Pending Draw Hero Box)**:
   - Thông báo bộ số đã niêm phong chốt chặn cho kỳ sắp tới.
   - Đồng hồ đếm ngược đến giờ quay thưởng.
3. **Bảng Lịch sử Đối soát (Interactive Verification Table)**:
   - Phân màu trực quan: Bóng trúng sáng viền vàng/xanh lục, bóng trượt mờ.
   - Hiển thị rõ số bóng trúng: `2/6`, `3/6 (Giải Ba)`, v.v.
   - Cột P&L trực tiếp từng kỳ với màu xanh/đỏ.
4. **Bộ lọc Tab**: Xem Vé Vàng / Xem Bao 7 / Xem Dàn Banker / Chỉ xem kỳ trúng.

---

## 6. KẾ HOẠCH KIỂM THỬ (TESTING & VERIFICATION)

1. **Unit Test (`tests/test_prediction_evaluator.py`)**:
   - Kiểm tra tính đúng đắn của hàm tính giải thưởng (Power 6/55, Mega 6/45, Power 5/35, Bao 7).
   - Kiểm tra cơ chế chống Look-ahead Bias khi sinh vé Walk-Forward.
2. **Integration Test (`tests/test_prediction_tracker.py`)**:
   - Kiểm tra quy trình Seed $\rightarrow$ Snapshot Pending $\rightarrow$ Verify Actual $\rightarrow$ Compute KPI.
   - Kiểm tra tính toàn vẹn của tệp JSONL khi ghi đồng thời (Atomic write).
3. **Web Data Verification**:
   - Chạy `render_web_data.py` và xác minh cấu trúc JSON trong `docs/data/vietlott_summary.json`.
   - Kiểm tra trực quan bảng đối soát trên trình duyệt.
