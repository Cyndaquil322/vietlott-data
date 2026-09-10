"""
Wavelet Engine: Discrete Wavelet Transform (DWT) Multi-Resolution Analysis
==========================================================================
Pure NumPy implementation of Daubechies 4 (db4) Wavelet Multi-Resolution
Analysis (MRA) for non-stationary lottery hit recurrence time series.

Key Capabilities:
- Daubechies 4 orthogonal filter bank (low-pass scaling & high-pass wavelet).
- 1D DWT step with periodic wrap boundary padding to prevent edge truncation.
- Mallat pyramidal multi-level decomposition (Levels = 2: A2, D1, D2).
- Multi-scale wavelet energy & scale-gap resonance scoring for lottery numbers.
"""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np

_sqrt3 = math.sqrt(3)
_denom = 4 * math.sqrt(2)

DB4_LP: List[float] = [
    (1 + _sqrt3) / _denom,
    (3 + _sqrt3) / _denom,
    (3 - _sqrt3) / _denom,
    (1 - _sqrt3) / _denom,
]

DB4_HP: List[float] = [
    (1 - _sqrt3) / _denom,
    -(3 - _sqrt3) / _denom,
    (3 + _sqrt3) / _denom,
    -(1 + _sqrt3) / _denom,
]


class WaveletAnalyzer:
    """Pure NumPy implementation of Discrete Wavelet Transform (DWT) Multi-Resolution Analysis.

    Triển khai thuần NumPy không phụ thuộc scipy hay pywt.
    Sử dụng bộ lọc trực giao Daubechies 4 (db4) theo thuật toán tháp Mallat.
    """

    DB4_LP = DB4_LP
    DB4_HP = DB4_HP

    @staticmethod
    def dwt_step(
        signal: np.ndarray,
        lp_filter: Optional[np.ndarray] = None,
        hp_filter: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Thực hiện một bước biến đổi sóng con rời rạc (1D DWT step).

        Áp dụng periodic wrap padding để không làm cụt biên tín hiệu,
        tích chập với bộ lọc và downsample bước 2 ([::2]).

        Args:
            signal: Mảng 1D tín hiệu đầu vào.
            lp_filter: Bộ lọc thông thấp (mặc định Daubechies 4 LP).
            hp_filter: Bộ lọc thông cao (mặc định Daubechies 4 HP).

        Returns:
            Tuple (approx, detail) đều có kích thước len(signal) // 2.
        """
        sig = np.asarray(signal, dtype=float)
        n = len(sig)
        out_len = n // 2
        if out_len == 0:
            return np.array([], dtype=float), np.array([], dtype=float)

        h0 = np.asarray(lp_filter if lp_filter is not None else WaveletAnalyzer.DB4_LP, dtype=float)
        h1 = np.asarray(hp_filter if hp_filter is not None else WaveletAnalyzer.DB4_HP, dtype=float)

        pad_len = len(h0) - 1
        padded = np.pad(sig, (0, pad_len), mode="wrap")

        approx_conv = np.convolve(padded, h0, mode="valid")
        detail_conv = np.convolve(padded, h1, mode="valid")

        approx = approx_conv[: 2 * out_len][::2]
        detail = detail_conv[: 2 * out_len][::2]

        return approx, detail

    @staticmethod
    def decompose_signal(
        signal: np.ndarray,
        levels: int = 2,
        lp_filter: Optional[np.ndarray] = None,
        hp_filter: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Phân rã đa tỷ lệ Mallat (Multi-Resolution Analysis).

        Args:
            signal: Mảng 1D tín hiệu thời gian.
            levels: Số cấp độ phân rã (mặc định: 2).
            lp_filter: Bộ lọc thông thấp (tùy chọn).
            hp_filter: Bộ lọc thông cao (tùy chọn).

        Returns:
            Tuple (A_levels, [D_1, D_2, ..., D_levels]).
        """
        current_approx = np.asarray(signal, dtype=float)
        details: List[np.ndarray] = []

        for _ in range(levels):
            if len(current_approx) < 2:
                break
            approx, detail = WaveletAnalyzer.dwt_step(
                current_approx,
                lp_filter=lp_filter,
                hp_filter=hp_filter,
            )
            details.append(detail)
            current_approx = approx

        return current_approx, details


def calculate_wavelet_spectral_scores(
    sub_records: List[Dict],
    max_val: int,
    num_balls: int,
    window_len: int = 64,
) -> Dict[int, float]:
    """Tính điểm phổ năng lượng sóng con Daubechies kết hợp cộng hưởng nhịp gan.

    Phân rã đa tỷ lệ tín hiệu xuất hiện nhị phân trên cửa sổ window_len:
    - D1: Nhịp vi mô ngắn hạn (2-4 kỳ).
    - D2: Nhịp điều hòa trung hạn (5-12 kỳ).
    - Năng lượng bùng phát gần nhất E_recent.
    - Ước lượng bước sóng chủ đạo dominant_scale từ tỷ lệ năng lượng D1/D2.
    - Điểm cộng hưởng nhịp gan Resonance và điểm tổng hợp Wavelet.

    Args:
        sub_records: Danh sách các bản ghi kỳ quay lịch sử.
        max_val: Số lớn nhất trong tập bóng (ví dụ 45, 55, 35).
        num_balls: Số lượng bóng trúng chính trong mỗi kỳ (ví dụ 6 hoặc 5).
        window_len: Độ rộng cửa sổ phân tích (mặc định: 64).

    Returns:
        Dict {ball: score} chuẩn hóa làm tròn 3 chữ số thập phân cho mọi b in [1, max_val].
    """
    scores: Dict[int, float] = {b: 0.0 for b in range(1, max_val + 1)}
    if not sub_records:
        return scores

    window_records = sub_records[-window_len:] if len(sub_records) >= window_len else sub_records

    # Tính nhịp gan hiện tại (cur_gap) cho từng số từ 1 đến max_val
    cur_gap: Dict[int, int] = {}
    for t, r in enumerate(reversed(sub_records)):
        res = r.get("result", [])[:num_balls]
        for b in res:
            if 1 <= b <= max_val and b not in cur_gap:
                cur_gap[b] = t

    for b in range(1, max_val + 1):
        # Chuỗi tín hiệu nhị phân x_b[t] trên cửa sổ
        sig = np.array(
            [1.0 if b in r.get("result", [])[:num_balls] else 0.0 for r in window_records],
            dtype=float,
        )

        # Nếu bóng chưa từng xuất hiện trên cửa sổ, điểm = 0.0
        if np.sum(sig) == 0.0:
            scores[b] = 0.0
            continue

        # Đảm bảo độ dài cửa sổ nhất quán nếu dữ liệu ít hơn window_len
        if len(sig) < window_len:
            sig = np.pad(sig, (window_len - len(sig), 0), mode="constant")

        # Phân rã đa tỷ lệ Mallat với levels=2
        _, details = WaveletAnalyzer.decompose_signal(sig, levels=2)
        d1 = details[0] if len(details) > 0 else np.array([], dtype=float)
        d2 = details[1] if len(details) > 1 else np.array([], dtype=float)

        # Năng lượng cục bộ gần nhất (Recent Burst Energy)
        # E_recent = sum(D_1[-4:]^2) * 2.0 + sum(D_2[-2:]^2) * 1.0
        e_recent_d1 = float(np.sum(d1[-4:] ** 2)) if len(d1) > 0 else 0.0
        e_recent_d2 = float(np.sum(d2[-2:] ** 2)) if len(d2) > 0 else 0.0
        e_recent = e_recent_d1 * 2.0 + e_recent_d2 * 1.0

        # Ước lượng bước sóng chủ đạo dominant_scale từ tỷ lệ năng lượng D1 và D2
        e_d1 = float(np.sum(d1 ** 2)) if len(d1) > 0 else 0.0
        e_d2 = float(np.sum(d2 ** 2)) if len(d2) > 0 else 0.0
        dominant_scale = 3.5 if e_d1 > e_d2 else 8.5

        # Điểm cộng hưởng nhịp gan: Resonance = exp(-0.25 * |cur_gap - dominant_scale|)
        gb = float(cur_gap.get(b, len(window_records)))
        resonance = math.exp(-0.25 * abs(gb - dominant_scale))

        # Điểm tổng hợp Wavelet: Score(b) = Resonance * 1.5 + E_recent
        raw_score = resonance * 1.5 + e_recent
        scores[b] = round(float(raw_score), 3)

    return scores
