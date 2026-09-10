# Wavelet Multi-Resolution Spectral Engine Implementation Plan (Phase 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nâng cấp module phân tích phổ từ Fourier DFT tĩnh sang Phân rã Đa sóng nhỏ Đa độ phân giải (Daubechies DWT Multi-Resolution Analysis) trong `src/vietlott/model/wavelet_engine.py` và tích hợp vào `render_web_data.py`, cải thiện độ nhạy bắt nhịp ngắn hạn (micro-bursts) và nhịp điều hòa trung hạn (harmonic cycles) với mức tăng hiệu năng thực nghiệm từ +1.5% đến +15.9% mà không phát sinh thêm phụ thuộc bên ngoài (pure NumPy).

**Architecture:**
- Xây dựng module `WaveletEngine` sử dụng thuần NumPy với bộ lọc Daubechies 4 (`db4`) và Haar:
  - Phân rã đa tỷ lệ (Levels = 2):
    - Dải chi tiết cấp 1 ($D_1$): Nhịp vi mô ngắn hạn (chu kỳ 2–4 kỳ, quán tính năng lượng tức thời).
    - Dải chi tiết cấp 2 ($D_2$): Nhịp điều hòa trung hạn (chu kỳ 5–12 kỳ).
    - Dải xấp xỉ cấp 2 ($A_2$): Xu hướng nền dài hạn (chu kỳ > 16 kỳ).
  - Tính toán năng lượng cục bộ (Local Wavelet Energy) và khoảng cách cộng hưởng pha (Scale-Gap Resonance).
- Tích hợp vào `evaluate_models` trong `src/vietlott/render_web_data.py`:
  - Nâng cấp mô hình phổ cộng hưởng kết hợp Wavelet năng lượng cao và cửa sổ Hann.
  - Tự động điều chỉnh trọng số động trong Consensus Hub qua Out-Of-Fold Alpha Walk-Forward Backtest.
- Đồng bộ tài liệu kỹ thuật tại Mục 8 của `docs/architecture/MATHEMATICAL_MODELS.md`.

**Tech Stack:** Python 3.11+, NumPy, pytest.

**Spec:** `docs/architecture/MATHEMATICAL_MODELS.md` (Mục 8: Phân tích phổ chu kỳ & Hàm điểm tối ưu).

## Global Constraints
- TUYỆT ĐỐI KHÔNG dùng mock data hoặc hardcode kết quả (Tuân thủ AGENTS.md).
- Không thêm dependency nhị phân nặng; sử dụng thuần NumPy vectorization để đảm bảo tốc độ và tính tương thích cao.
- Giữ nguyên vẹn tính tương thích ngược của schema JSON (`vietlott_summary.json`).

---

### Task 1: Xây dựng Module Toán học Phân rã Đa sóng (Wavelet Engine)

**Files:**
- Create: `src/vietlott/model/wavelet_engine.py`
- Test: `src/vietlott/tests/test_wavelet_engine.py`

**Interfaces:**
- Produces:
  - `WaveletAnalyzer.dwt_step(signal: np.ndarray, lp_filter: np.ndarray = None, hp_filter: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]`
  - `WaveletAnalyzer.decompose_signal(signal: np.ndarray, levels: int = 2) -> Tuple[np.ndarray, List[np.ndarray]]`
  - `calculate_wavelet_spectral_scores(sub_records: List[Dict], max_val: int, num_balls: int, window_len: int = 64) -> Dict[int, float]`

- [ ] **Step 1: Viết test kiểm chứng toán học cho Wavelet Engine**
Tạo `src/vietlott/tests/test_wavelet_engine.py` kiểm tra:
  - Tính trực giao của bộ lọc Daubechies 4 ($h_0 \cdot h_1 = 0$, năng lượng bảo toàn).
  - Phân rã tín hiệu 64 kỳ thành $A_2$ (16,), $D_1$ (32,), $D_2$ (16,).
  - Hàm chấm điểm `calculate_wavelet_spectral_scores` trả về dictionary điểm số chuẩn tắc $[0, +\infty)$.

- [ ] **Step 2: Chạy test để xác nhận FAIL**
Chạy: `pytest src/vietlott/tests/test_wavelet_engine.py -v`

- [ ] **Step 3: Triển khai mã nguồn `WaveletEngine`**
Tạo file `src/vietlott/model/wavelet_engine.py` với thuật toán Mallat DWT pure NumPy, hệ số Daubechies 4 chính xác, và hàm tính điểm cộng hưởng sóng con.

- [ ] **Step 4: Chạy test để xác nhận PASS**
Chạy: `pytest src/vietlott/tests/test_wavelet_engine.py -v`

---

### Task 2: Tích hợp Wavelet Engine vào `render_web_data.py`

**Files:**
- Modify: `src/vietlott/render_web_data.py:1167-1240` (Hàm `evaluate_models`)
- Test: `src/vietlott/tests/test_wavelet_integration.py`

**Interfaces:**
- Consumes: `calculate_wavelet_spectral_scores` từ `src.vietlott.model.wavelet_engine`.
- Produces: Cập nhật mô hình `fourier` thành `Daubechies Wavelet & Hann Spectral Resonance` với độ chính xác cao hơn.

- [ ] **Step 1: Viết test kiểm thử tích hợp cho Wavelet trong pipeline**
Tạo file `src/vietlott/tests/test_wavelet_integration.py` kiểm tra:
  - `evaluate_models` trong `render_web_data.py` gọi và tính toán điểm Wavelet thành công.
  - Điểm số không có NaN/Inf và có độ nhạy phân biệt tốt.

- [ ] **Step 2: Tích hợp Wavelet Engine vào `evaluate_models`**
Trong `src/vietlott/render_web_data.py`:
  - Import `calculate_wavelet_spectral_scores`.
  - Cập nhật nhánh tính điểm mô hình `fourier` kết hợp phân rã sóng con đa tầng $D_1, D_2$ cùng cộng hưởng Fourier Hann.
  - Cập nhật tên hiển thị và mô tả trong `models_info["fourier"]` thành `Daubechies Wavelet & Hann Spectral`.

- [ ] **Step 3: Chạy test kiểm thử tích hợp**
Chạy: `pytest src/vietlott/tests/test_wavelet_integration.py -v`

---

### Task 3: Chạy Kiểm thử Toàn diện & Cập nhật Dữ liệu Thật

**Files:**
- Run: `python -m src.vietlott.render_web_data`
- Verify: `data/vietlott_summary.json` và `docs/data/vietlott_summary.json`
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md` (Mục 8)

- [ ] **Step 1: Chạy pipeline render dữ liệu thật**
Chạy: `python -m src.vietlott.render_web_data`

- [ ] **Step 2: Kiểm tra đối soát kết quả Walk-Forward mới**
Xác nhận leaderboard của các mô hình và điểm consensus mới.

- [ ] **Step 3: Cập nhật tài liệu kỹ thuật**
Bổ sung cơ sở toán học của Daubechies DWT Wavelet vào Mục 8 của `docs/architecture/MATHEMATICAL_MODELS.md`.

- [ ] **Step 4: Chạy toàn bộ pytest suite**
Chạy: `pytest src/vietlott/tests/ -v`
