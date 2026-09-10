"""
Machine Learning Ranker (ml_ranker.py)
======================================
Trích xuất vector đặc trưng 14 chiều cho từng quả bóng b in [1, max_val],
huấn luyện mô hình HistGradientBoostingClassifier từ scikit-learn theo
cơ chế Walk-Forward Rolling Window, và xuất điểm dự báo xác suất chuẩn hóa [0.0, 3.0].

Tuân thủ nghiêm ngặt:
1. Walk-Forward Temporal Safety (Tuyệt đối không sử dụng dữ liệu từ t trở đi để trích xuất đặc trưng cho t).
2. Zero Mock Data (100% huấn luyện và dự báo từ dữ liệu thực tế).
3. Deterministic Seeding & Numerical Stability (Không phát sinh NaN/Inf, random_state=42).
"""

from typing import Any, Dict, List, Optional
import numpy as np
import joblib.parallel
from sklearn.ensemble import HistGradientBoostingClassifier

# Ensure joblib uses sequential backend instead of thread pool with named pipes (which are blocked in sandboxed environments)
try:
    joblib.parallel.BACKENDS["threading"] = joblib.parallel.BACKENDS["sequential"]
except Exception:
    pass

try:
    from vietlott.model.analytic_engines import evaluate_all_models
    from vietlott.model.transition_engine import calculate_vector_field_pull
except ImportError:
    try:
        from src.vietlott.model.analytic_engines import evaluate_all_models
        from src.vietlott.model.transition_engine import calculate_vector_field_pull
    except ImportError:
        evaluate_all_models = None
        calculate_vector_field_pull = None

_FEATURE_CACHE: Dict[tuple, np.ndarray] = {}


def extract_feature_matrix_for_draw(
    sub_records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    opt_alpha: float = 0.035,
    is_two_matrix: bool = False,
) -> np.ndarray:
    """
    Trích xuất ma trận đặc trưng 14 chiều cho toàn bộ các bóng b in [1, max_val].

    Args:
        sub_records: Danh sách các bản ghi kỳ quay lịch sử (chỉ chứa các kỳ t <= T-1).
        max_val: Giá trị bóng lớn nhất (55, 45, 35).
        num_balls: Số bóng chính trong 1 kỳ quay.
        opt_alpha: Hệ số suy giảm thời gian alpha.
        is_two_matrix: Cờ cho sản phẩm có ma trận đôi.

    Returns:
        np.ndarray: Ma trận kích thước (max_val, 14), mỗi hàng b - 1 là vector đặc trưng.
    """
    if max_val <= 0:
        return np.zeros((0, 14), dtype=np.float64)

    if sub_records:
        last = sub_records[-1]
        cache_key = (
            str(last.get("id", last.get("draw_id", ""))),
            tuple(last.get("result", [])),
            len(sub_records),
            max_val,
            num_balls,
            round(opt_alpha, 6),
            is_two_matrix,
        )
    else:
        cache_key = ("__empty__", (), 0, max_val, num_balls, round(opt_alpha, 6), is_two_matrix)

    if cache_key in _FEATURE_CACHE:
        return _FEATURE_CACHE[cache_key].copy()

    m_eval = evaluate_all_models(
        sub_records,
        max_val=max_val,
        num_balls=num_balls,
        opt_alpha=opt_alpha,
        is_two_matrix=is_two_matrix,
    ) if evaluate_all_models else {}

    pull = calculate_vector_field_pull(
        sub_records,
        max_val=max_val,
        num_balls=num_balls,
    ) if calculate_vector_field_pull else {}

    hazard = m_eval.get("hazard", {})
    decay = m_eval.get("decay", {})
    markov = m_eval.get("markov", {})
    fourier = m_eval.get("fourier", {})
    bac_nho = m_eval.get("bac_nho", {})
    graph_pagerank = m_eval.get("graph_pagerank", {})
    state_space = m_eval.get("state_space", {})
    cur_gap = m_eval.get("cur_gap", {})

    X = np.zeros((max_val, 14), dtype=np.float64)

    for b in range(1, max_val + 1):
        idx = b - 1
        pull_b = pull.get(b, {})

        X[idx, 0] = float(hazard.get(b, 0.0))
        X[idx, 1] = float(decay.get(b, 0.0))
        X[idx, 2] = float(markov.get(b, 0.0))
        X[idx, 3] = float(fourier.get(b, 0.0))
        X[idx, 4] = float(bac_nho.get(b, 0.0))
        X[idx, 5] = float(graph_pagerank.get(b, 0.0))
        X[idx, 6] = float(state_space.get(b, 0.0))
        X[idx, 7] = float(pull_b.get("max_pull_lift", 1.0))
        X[idx, 8] = float(pull_b.get("sum_z_score", 0.0))
        X[idx, 9] = float(pull_b.get("repulsion_penalty", 1.0))
        X[idx, 10] = float(pull_b.get("repeat_momentum", 0.0))
        X[idx, 11] = float(cur_gap.get(b, 0.0))
        X[idx, 12] = float(b % 3)
        X[idx, 13] = float(b / max_val)

    # Clean any abnormal numerical values (NaN, Inf)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    if len(_FEATURE_CACHE) > 5000:
        _FEATURE_CACHE.clear()
    _FEATURE_CACHE[cache_key] = X.copy()

    return X


class HistGradientBoostingRanker:
    """
    Bộ phân loại tăng cường độ dốc dạng histogram (HistGradientBoostingClassifier)
    tối ưu cho bài toán xếp hạng nhị phân xác suất trúng bóng.
    """

    def __init__(
        self,
        learning_rate: float = 0.05,
        max_iter: int = 50,
        max_depth: int = 3,
        min_samples_leaf: int = 15,
        l2_regularization: float = 1.5,
        random_state: int = 42,
    ) -> None:
        self.clf = HistGradientBoostingClassifier(
            learning_rate=learning_rate,
            max_iter=max_iter,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            l2_regularization=l2_regularization,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "HistGradientBoostingRanker":
        """
        Huấn luyện bộ phân loại với ma trận đặc trưng X và nhãn nhị phân y.
        """
        self.clf.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Dự báo xác suất xuất hiện (lớp 1) cho từng mẫu trong X.

        Returns:
            np.ndarray: Mảng 1 chiều chứa xác suất P(y=1) của từng mẫu.
        """
        proba = self.clf.predict_proba(X)
        classes = list(self.clf.classes_)
        if 1.0 in classes:
            idx = classes.index(1.0)
            return proba[:, idx]
        elif 1 in classes:
            idx = classes.index(1)
            return proba[:, idx]
        elif len(classes) >= 2:
            return proba[:, 1]
        elif len(classes) == 1:
            c = classes[0]
            val = 1.0 if (c == 1 or c == 1.0) else 0.0
            return np.full(X.shape[0], val, dtype=np.float64)
        return np.zeros(X.shape[0], dtype=np.float64)


def train_and_predict_ml_ranker(
    sub_records: List[Dict[str, Any]],
    max_val: int,
    num_balls: int,
    train_window: int = 50,
    opt_alpha: float = 0.035,
    is_two_matrix: bool = False,
) -> Dict[int, float]:
    """
    Huấn luyện mô hình HistGradientBoosting theo cơ chế Walk-Forward Rolling Window
    và trích xuất điểm xếp hạng chuẩn hóa [0.0, 3.0] cho kỳ kế tiếp.

    Args:
        sub_records: Danh sách các bản ghi lịch sử tính đến hiện tại.
        max_val: Giá trị bóng tối đa.
        num_balls: Số bóng chính.
        train_window: Kích thước cửa sổ trượt huấn luyện (mặc định 50).
        opt_alpha: Tham số alpha suy giảm mũ.
        is_two_matrix: Cờ ma trận đôi.

    Returns:
        Dict[int, float]: Điểm dự báo xác suất chuẩn hóa [0.0, 3.0] cho mọi b in [1, max_val].
    """
    # Safe fallback when historical data is too short
    if len(sub_records) < 20:
        if evaluate_all_models:
            m_eval = evaluate_all_models(
                sub_records,
                max_val=max_val,
                num_balls=num_balls,
                opt_alpha=opt_alpha,
                is_two_matrix=is_two_matrix,
            )
            model_keys = ["hazard", "decay", "markov", "fourier", "bac_nho", "graph_pagerank", "state_space"]
            raw_means = {}
            for b in range(1, max_val + 1):
                vals = [float(m_eval.get(k, {}).get(b, 0.0)) for k in model_keys]
                raw_means[b] = float(np.mean(vals)) if vals else 0.0
            min_s = min(raw_means.values()) if raw_means else 0.0
            max_s = max(raw_means.values()) if raw_means else 0.0
            diff = max_s - min_s
            if diff > 1e-9:
                return {
                    b: round(float((raw_means[b] - min_s) / (diff + 1e-9) * 3.0), 3)
                    for b in range(1, max_val + 1)
                }
            return {b: round(raw_means[b], 3) for b in range(1, max_val + 1)}
        return {b: 1.5 for b in range(1, max_val + 1)}

    L = len(sub_records)
    W = min(train_window, L - 5)
    if W <= 0:
        return {b: 1.5 for b in range(1, max_val + 1)}

    X_list = []
    y_list = []

    # Rolling window training: for each draw t in [L - W, L)
    for t in range(L - W, L):
        # Strict temporal guard: strictly past draws before t
        X_t = extract_feature_matrix_for_draw(
            sub_records[:t],
            max_val=max_val,
            num_balls=num_balls,
            opt_alpha=opt_alpha,
            is_two_matrix=is_two_matrix,
        )
        actual_result = set(sub_records[t].get("result", [])[:num_balls])
        y_t = np.array(
            [1.0 if b in actual_result else 0.0 for b in range(1, max_val + 1)],
            dtype=np.float64,
        )
        X_list.append(X_t)
        y_list.append(y_t)

    X_train = np.vstack(X_list)
    y_train = np.concatenate(y_list)

    # Train model
    ranker = HistGradientBoostingRanker()
    ranker.fit(X_train, y_train)

    # Predict target probabilities for next draw using full sub_records
    X_target = extract_feature_matrix_for_draw(
        sub_records,
        max_val=max_val,
        num_balls=num_balls,
        opt_alpha=opt_alpha,
        is_two_matrix=is_two_matrix,
    )
    p_hat = ranker.predict_proba(X_target)

    min_p = float(np.min(p_hat))
    max_p = float(np.max(p_hat))
    diff = max_p - min_p

    scores: Dict[int, float] = {}
    for b in range(1, max_val + 1):
        p_b = float(p_hat[b - 1])
        if diff > 1e-9:
            sc = round(((p_b - min_p) / (diff + 1e-9)) * 3.0, 3)
        else:
            sc = 1.5
        scores[b] = float(sc)

    return scores
