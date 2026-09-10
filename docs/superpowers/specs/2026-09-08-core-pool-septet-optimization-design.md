# Core Pool Optimal Septet Optimization & 100-Draw Walk-Forward Backtest Design Spec

## 1. Executive Summary
- **Mục tiêu**: Từ dàn hạt nhân (Core Pool 10-12 số) đã được ensemble chọn lọc, thiết kế thuật toán tối ưu toán học để rút trích ra **Bộ 7 số tối ưu (Bao 7 cho Power 6/55 & Mega 6/45; Bao 6 cho Power 5/35)** có xác suất bao phủ và tỷ lệ trúng cao nhất.
- **Phạm vi kiểm định**: Thực hiện Walk-Forward Backtest độc lập 100 kỳ gần nhất cho cả 3 loại hình xổ số (Power 6/55, Mega 6/45, Power 5/35).
- **Cam kết khoa học**: 100% dữ liệu thật, strictly walk-forward (tại kỳ T chỉ dùng dữ liệu <= T-1), seeded deterministic (cố định theo Draw ID), không mock data.

## 2. Mathematical Optimization Model (Hybrid Multi-Objective Pareto)
Cho Dàn hạt nhân $P = \{s_1, s_2, ..., s_m\}$ với $m = 12$ (cho 6/55, 6/45) hoặc $m = 10$ (cho 5/35).
Không gian tìm kiếm:
- Với 6/55 và 6/45: Rút $k = 7$ số từ $m = 12$ số -> $C(12, 7) = 792$ tổ hợp con.
- Với 5/35: Rút $k = 6$ số chính từ $m = 10$ số -> $C(10, 6) = 210$ tổ hợp con (ghép với số đặc biệt 01-12 có score cao nhất).

Mỗi tổ hợp con $S_7 = \{b_1, ..., b_7\} \subset P$ được chấm điểm qua hàm mục tiêu đa tiêu chí:
$$\text{Fitness}(S_7) = \sum_{b \in S_7} \text{Alpha}(b) + \gamma \sum_{1 \le i < j \le 7} \text{Lift}^*(b_i, b_j) + \lambda_{\text{state}} \Psi_{\text{state}}(S_7) - \text{Penalties}(S_7)$$

### 2.1 Thành phần hàm điểm
1. **Univariate Alpha Score**:
   $$\text{Alpha}(b) = w_1 \cdot \text{Score}_{\text{ensemble}}(b) + w_2 \cdot \text{MarkovTransition}(b)$$
2. **Pairwise Co-occurrence Lift**:
   $$\text{Lift}^*(b_i, b_j) = \frac{P(b_i, b_j)}{P(b_i) \cdot P(b_j)}$$
   Được chuẩn hóa min-max trên toàn bộ các cặp số trong kỳ xét.
3. **State/Gap Distribution Harmonic Score**:
   $$\Psi_{\text{state}}(S_7) = 1.0 - \text{KL}\left( \text{Hist}_{\text{actual}}(S_7) \parallel \text{TargetRatio}(H:W:C = 3:2:2) \right)$$
   Tối ưu hóa phân bổ tỷ lệ Nóng - Ấm - Lạnh hài hòa theo phân phối thực tế của Vietlott.
4. **Negative Space Hard & Soft Penalties**:
   - Arithmetic Complexity ($AC$): $AC_7 = \Delta_{\text{unique}} - (7 - 1) \ge 12$. Nếu $AC_7 < 12$ -> Trừ điểm phạt nặng.
   - Gaussian Sum Range: $\sum_{b \in S_7} b \in [\mu_7 - 1.5\sigma_7, \mu_7 + 1.5\sigma_7]$. Phạt khoảng cách nếu lệch chuẩn.
   - Span (Max - Min) $\ge 30$.
   - Consecutive Run: Chuỗi liên tiếp $\le 2$ số (phạt nếu có 3 số liên tiếp trở lên như 12-13-14).
   - Decade Coverage: Bao phủ tối thiểu $\ge 4$ khoảng chục (0x, 1x, 2x, 3x, 4x, 5x).

## 3. Data Pipeline & Walk-Forward Protocol
1. **Walk-Forward Loop**:
   - Lặp qua 100 kỳ gần nhất: $t \in [T - 99, T]$.
   - Tại mỗi bước $t$:
     - Huấn luyện / tính toán ensemble models chỉ trên tập $[1, t-1]$.
     - Trích xuất Core Pool $P_t$.
     - Chạy Pareto Optimization trên $C(|P_t|, 7)$ với Seed = `draw_id` để chọn $S_7^*(t)$.
     - Đối soát với kết quả thực tế của kỳ $t$: Đếm số lượng bóng trùng khớp $H(t) = |S_7^*(t) \cap \text{DrawResults}(t)|$.
     - Phân loại: Trúng $\ge 3$, trúng $\ge 4$, trúng $\ge 5$, trúng 6 (Jackpot 2 / Giải Nhất), trúng 7 (Jackpot 1).
     - Tính P&L mô phỏng theo biểu phí cơ cấu giải thưởng Bao 7 của Vietlott.
2. **Output Schema**:
   - `optimal_septet`: { numbers: [7 số], alpha_score, lift_score, ac_score, sum, state_composition }
   - `septet_backtest_100`: {
       total_draws: 100,
       match_ge3_count, match_ge3_pct,
       match_ge4_count, match_ge4_pct,
       match_ge5_count, match_ge5_pct,
       match_6_count, match_7_count,
       total_cost_vnd, total_prize_vnd, net_profit_vnd, roi_pct,
       history: [ { draw_id, date, septet: [], hits: int, matched_numbers: [], prize_vnd: int } ]
     }

## 4. UI/UX Integration
- Hiển thị Vé Bao 7 tối ưu nổi bật tại tab Bao 7 / Dàn hạt nhân với nhãn **"Bộ 7 Số Tối Ưu Toán Học (Pareto Co-occurrence)"**.
- Bảng đối soát 100 kỳ Walk-Forward với bộ lọc trực quan: Tỷ lệ trúng $\ge 3$ số, $\ge 4$ số, P&L mô phỏng.
