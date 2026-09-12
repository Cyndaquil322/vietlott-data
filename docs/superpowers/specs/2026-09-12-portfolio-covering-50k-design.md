# ĐẶC TẢ THIẾT KẾ KỸ THUẬT: BỘ 5 VÉ TỐI ƯU BỌC LÓT DANH MỤC 50K (PORTFOLIO COMBINATORIAL COVERING 50K)

**Mã thiết kế:** `SPEC-PORTFOLIO-COVERING-50K-20260912`  
**Ngày lập:** 12/09/2026  
**Tác giả:** Antigravity / DeepSeek Harness  
**Trạng thái:** Approved / Ready for Implementation  

---

## 1. MỤC TIÊU & BỐI CẢNH (OBJECTIVES & CONTEXT)

### 1.1. Vấn đề thực tế
- Người chơi thường có ngân sách cố định mỗi ngày/kỳ là **50.000 VNĐ** (tương đương 5 vé đơn Vietlott).
- Trước đây, hệ thống sinh ra 5 vé tương đối rời rạc (1 Vé Vàng Markowitz, 1 vé Momentum, 1 vé Breakout, 2 vé thủ công). Khi Dàn Hạt Nhân (Core Pool 10–12 số) đoán trúng 3 đến 4 con số, các con số trúng lại bị rải rác mỗi vé dính 1 hoặc 2 con $\to$ Người chơi đoán trúng nhiều bóng nhưng không có vé nào đạt ngưỡng $\ge 3$ bóng để lĩnh tiền thưởng.

### 1.2. Mục tiêu kỹ thuật
- Xây dựng thuật toán **Tối ưu hóa Danh mục Tổ hợp Bọc lót (Portfolio Combinatorial Covering)**:
  - Đầu vào: Dàn Hạt Nhân (Core Pool 10–12 bóng) + Điểm số đồng thuận Consensus.
  - Bộ lọc: Áp dụng **Bộ lọc Không Gian Âm (Negative Space Filter)**:
    1. $AC \ge 7$ (Power 6/55, Mega 6/45) hoặc $AC \ge 4$ (Power 5/35).
    2. Phân bổ Chẵn/Lẻ cân bằng: $2:4, 3:3, 4:2$ (Mega 6/45, Power 6/55) hoặc $2:3, 3:2$ (Power 5/35).
    3. Trải rộng đầu số (Decade spread): Tối thiểu 4 đầu số khác nhau.
    4. Dải tổng chuẩn Gaussian: Nằm trong $[\mu - 1.5\sigma, \mu + 1.5\sigma]$.
  - Tối ưu hóa: Dùng thuật toán **Greedy Triplet & Pair Max-Coverage** chọn ra đúng **5 vé** sao cho:
    - Tối đa hóa số lượng cặp đôi $(i, j)$ và bộ ba $(i, j, k)$ được bao phủ.
    - Hễ Dàn Hạt Nhân trúng $\ge 3$ bóng thì xác suất có ít nhất 1 vé gom trọn $\ge 3$ bóng là cao nhất.
  - Tích hợp vào Web GUI: Hiển thị Khối Card **"Bộ 5 Vé Tối Ưu Bọc Lót 50k"** với các nút tiện ích: Lưu cả 5 vé, Sao chép SMS 9969 cả 5 vé, và Thống kê độ bao phủ.

---

## 2. KIẾN TRÚC & PHÂN TẦNG DỮ LIỆU

### 2.1. Module cốt lõi: `src/vietlott/model/portfolio_covering_engine.py`
Cung cấp các hàm API chính:
1. `filter_negative_space(combos: List[Tuple[int, ...]], max_val: int, num_balls: int) -> List[Tuple[int, ...]]`
2. `generate_portfolio_50k(core_pool: List[int], candidate_scores: Dict[int, float], max_val: int, num_balls: int, num_tickets: int = 5, seed: int = 42) -> Dict[str, Any]`

### 2.2. Schema đầu ra của Bộ 5 Vé:
```json
{
  "total_tickets": 5,
  "total_cost_vnd": 50000,
  "core_pool_size": 12,
  "pairs_coverage_pct": 74.2,
  "triplets_coverage_count": 38,
  "tickets": [
    {
      "id": "portfolio_ticket_1",
      "ticketIndex": 1,
      "numbers": [5, 11, 24, 31, 47, 54],
      "sum": 172,
      "ac": 8,
      "odds": 3,
      "evens": 3,
      "decades_count": 4,
      "tag": "Trục Lực Hút"
    },
    ...
  ]
}
```

### 2.3. Tích hợp vào `render_web_data.py` & Web GUI
- Nhúng kết quả vào `consensus_hub.tickets.portfolio_50k`.
- Thêm card giao diện trong tab Consensus của `docs/index.html` và hiển thị bằng JS trong `docs/assets/js/consensus_ensemble.js`.
