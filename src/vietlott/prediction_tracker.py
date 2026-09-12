"""
Module: prediction_tracker.py
Bộ điều phối sổ nhật ký lưu vết và đối soát dự đoán thời gian thực (Real-time Prediction Ledger)
cho Power 6/55, Mega 6/45 và Power 5/35.

Chức năng:
- Lưu vết và niêm phong (Snapshot) bộ số dự đoán cho kỳ tiếp theo trước giờ quay (status="pending").
- Tự động mở niêm phong đối soát (Verify) và tính thưởng chuẩn Vietlott khi cào kết quả mới (status="verified").
- Hỗ trợ gieo mầm dữ liệu lịch sử bằng Walk-Forward Backtest 100% khách quan (Zero Mock Data, Zero Look-Ahead Bias).
- Xuất bản dữ liệu tổng hợp hiệu suất (Web Summary KPI) cho giao diện Web GUI.
- Ghi tệp nguyên tử (Atomic Write qua file .tmp) chống hỏng hóc dữ liệu.
"""

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from vietlott.model.prediction_evaluator import (
    evaluate_ticket,
    evaluate_bao7,
    evaluate_banker_wheeling,
)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def normalize_game_key(game_key: str) -> str:
    """Chuẩn hóa mã sản phẩm Vietlott về key tiêu chuẩn: power655, power645, power535."""
    k = game_key.lower().replace("-", "").replace("_", "").replace(" ", "").replace("/", "")
    if "655" in k:
        return "power655"
    if "645" in k:
        return "power645"
    if "535" in k:
        return "power535"
    return k


def _norm_draw_id(draw_id: Any) -> str:
    """Chuẩn hóa ID kỳ quay: loại bỏ dấu # và chuẩn hóa 5 chữ số."""
    raw = str(draw_id).replace("#", "").strip()
    return raw.zfill(5) if raw.isdigit() else raw


def get_ledger_path(game_key: str, data_dir: Optional[Path] = None) -> Path:
    """Lấy đường dẫn tệp JSONL lưu sổ nhật ký đối soát của sản phẩm."""
    base_dir = Path(data_dir) if data_dir else DATA_DIR
    norm_key = normalize_game_key(game_key)
    return base_dir / f"prediction_ledger_{norm_key}.jsonl"


def load_ledger_records(file_path: Path) -> List[Dict[str, Any]]:
    """Đọc an toàn danh sách các bản ghi từ tệp JSONL của sổ nhật ký."""
    if not file_path.exists():
        return []
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                try:
                    r = json.loads(line_str)
                    records.append(r)
                except json.JSONDecodeError:
                    continue
    return records


def save_all_ledger_records_atomic(file_path: Path, records: List[Dict[str, Any]]) -> None:
    """
    Ghi toàn bộ bản ghi ra tệp JSONL bằng cơ chế Atomic Write (.tmp -> rename)
    đảm bảo an toàn 100% trước sự cố đứt gãy tiến trình.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    tmp_path.replace(file_path)


def save_ledger_record_atomic(file_path: Path, record: Dict[str, Any]) -> None:
    """Ghi bổ sung hoặc cập nhật 1 bản ghi vào sổ nhật ký theo cơ chế Atomic Write."""
    records = load_ledger_records(file_path)
    rec_id = _norm_draw_id(record.get("draw_id") or record.get("target_draw_id", ""))

    found = False
    new_records = []
    for r in records:
        curr_id = _norm_draw_id(r.get("draw_id") or r.get("target_draw_id", ""))
        if curr_id == rec_id:
            new_records.append(record)
            found = True
        else:
            new_records.append(r)

    if not found:
        new_records.append(record)

    save_all_ledger_records_atomic(file_path, new_records)


def _format_predictions_input(predictions_data: Dict[str, Any], game_key: str) -> Dict[str, Any]:
    """Chuẩn hóa dữ liệu dự đoán đầu vào sang cấu trúc lưu trữ chuẩn của sổ nhật ký."""
    norm_game = normalize_game_key(game_key)
    is_535 = (norm_game == "power535")

    # 1. Golden Ticket (Vé Vàng đơn)
    gt_src = predictions_data.get("golden_ticket") or predictions_data.get("golden") or {}
    if isinstance(gt_src, list):
        gt_nums = gt_src
        gt_cost = 10000
    elif isinstance(gt_src, dict):
        gt_nums = gt_src.get("numbers", [])
        gt_cost = gt_src.get("cost_vnd", 10000)
    else:
        gt_nums = []
        gt_cost = 10000

    golden_ticket = {
        "numbers": gt_nums,
        "cost_vnd": gt_cost,
        "hits": 0,
        "matched_balls": [],
        "prize_tier": "Chờ mở thưởng",
        "prize_vnd": 0,
    }

    # 2. Septet Bao 7 (hoặc Bao 6 cho 5/35)
    bao7_src = predictions_data.get("septet_bao7") or predictions_data.get("bao7") or predictions_data.get("optimal_septet") or {}
    if isinstance(bao7_src, list):
        bao7_nums = bao7_src
        bao7_cost = 60000 if is_535 else 70000
    elif isinstance(bao7_src, dict):
        bao7_nums = bao7_src.get("numbers", [])
        bao7_cost = bao7_src.get("cost_vnd", (60000 if is_535 else 70000))
    else:
        bao7_nums = []
        bao7_cost = 60000 if is_535 else 70000

    septet_bao7 = {
        "numbers": bao7_nums,
        "cost_vnd": bao7_cost,
        "hits": 0,
        "matched_balls": [],
        "prize_tier": "Chờ mở thưởng",
        "prize_vnd": 0,
    }

    # 3. Banker Wheeling (Dàn bọc lót Bạch Thủ)
    bw_src = predictions_data.get("banker_wheeling") or {}
    if isinstance(bw_src, dict):
        banker_val = bw_src.get("banker")
        bw_tickets = bw_src.get("tickets", [])
        bw_count = bw_src.get("tickets_count", len(bw_tickets))
        bw_cost = bw_src.get("cost_vnd", bw_count * 10000)
    else:
        banker_val = None
        bw_tickets = []
        bw_count = 0
        bw_cost = 0

    banker_wheeling = {
        "banker": banker_val,
        "tickets": bw_tickets,
        "tickets_count": bw_count,
        "cost_vnd": bw_cost,
        "best_hits": 0,
        "winning_tickets_count": 0,
        "total_prize_vnd": 0,
    }

    # 4. Core Pool (Dàn hạt nhân)
    cp_src = predictions_data.get("core_pool") or []
    if isinstance(cp_src, list):
        cp_nums = cp_src
    elif isinstance(cp_src, dict):
        cp_nums = cp_src.get("numbers", [])
    else:
        cp_nums = []

    core_pool = {
        "pool_size": len(cp_nums),
        "numbers": cp_nums,
        "hits": 0,
        "matched_balls": [],
    }

    return {
        "golden_ticket": golden_ticket,
        "septet_bao7": septet_bao7,
        "banker_wheeling": banker_wheeling,
        "core_pool": core_pool,
    }


def snapshot_next_prediction(
    game_key: str,
    target_draw_id: str,
    predictions_data: Dict[str, Any],
    draw_date: Optional[str] = None,
    data_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Niêm phong bộ vé dự đoán cho kỳ tiếp theo ở trạng thái 'pending' trước giờ quay.
    Nếu kỳ này đã được niêm phong hoặc đã có kết quả kiểm định, bảo tồn và không ghi đè mất mát.
    """
    ledger_path = get_ledger_path(game_key, data_dir=data_dir)
    existing_records = load_ledger_records(ledger_path)
    clean_id = _norm_draw_id(target_draw_id)

    # Kiểm tra xem kỳ này đã tồn tại chưa
    for r in existing_records:
        if _norm_draw_id(r.get("draw_id") or r.get("target_draw_id", "")) == clean_id:
            return r

    norm_preds = _format_predictions_input(predictions_data, game_key)
    total_invest = (
        norm_preds["golden_ticket"]["cost_vnd"]
        + norm_preds["septet_bao7"]["cost_vnd"]
        + norm_preds["banker_wheeling"]["cost_vnd"]
    )

    new_record: Dict[str, Any] = {
        "draw_id": clean_id,
        "draw_date": draw_date or "",
        "target_draw_id": clean_id,
        "created_at": datetime.now().isoformat(),
        "verified_at": None,
        "status": "pending",
        "actual_result": None,
        "special_ball": None,
        "predictions": norm_preds,
        "summary_metrics": {
            "total_investment_vnd": total_invest,
            "total_return_vnd": 0,
            "net_profit_vnd": 0,
            "roi_pct": 0.0,
            "has_winning_prize": False,
        },
    }

    save_ledger_record_atomic(ledger_path, new_record)
    return new_record


def _extract_draw_actual(latest_draw: Dict[str, Any], norm_game: str) -> tuple[List[int], Optional[int]]:
    """Trích xuất bóng chính và bóng đặc biệt từ kết quả mở thưởng cào về."""
    raw_res = latest_draw.get("result", [])
    special = latest_draw.get("special_ball") or latest_draw.get("special")

    if isinstance(raw_res, list):
        if norm_game == "power655":
            if special is None and len(raw_res) >= 7:
                special = raw_res[6]
                main_balls = raw_res[:6]
            else:
                main_balls = raw_res[:6]
        elif norm_game == "power535":
            if special is None and len(raw_res) >= 6:
                special = raw_res[5]
                main_balls = raw_res[:5]
            else:
                main_balls = raw_res[:5]
        else:  # power645
            main_balls = raw_res[:6]
            special = None
    else:
        main_balls = []

    return [int(x) for x in main_balls], (int(special) if special is not None else None)


def verify_and_update_ledger(
    game_key: str,
    latest_draw: Dict[str, Any],
    data_dir: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Đối soát kết quả kỳ quay thực tế với bản ghi dự đoán đã niêm phong trong sổ nhật ký.
    Tính toán chi tiết số bóng trúng, cơ cấu giải thưởng và P&L, cập nhật status từ 'pending' -> 'verified'.
    """
    ledger_path = get_ledger_path(game_key, data_dir=data_dir)
    records = load_ledger_records(ledger_path)
    if not records:
        return None

    clean_id = _norm_draw_id(latest_draw.get("id", ""))
    target_record: Optional[Dict[str, Any]] = None
    target_idx = -1

    for idx, r in enumerate(records):
        curr_id = _norm_draw_id(r.get("draw_id") or r.get("target_draw_id", ""))
        if curr_id == clean_id:
            target_record = r
            target_idx = idx
            break

    if target_record is None:
        return None

    norm_game = normalize_game_key(game_key)
    actual_main, special_ball = _extract_draw_actual(latest_draw, norm_game)

    preds = target_record.get("predictions", {})

    # 1. Chấm điểm Golden Ticket
    gt = preds.get("golden_ticket", {})
    gt_nums = gt.get("numbers", [])
    gt_eval = evaluate_ticket(norm_game, gt_nums, actual_main, special_ball)
    gt["hits"] = gt_eval["hits"]
    gt["matched_balls"] = gt_eval["matched_balls"]
    gt["prize_tier"] = gt_eval["prize_tier"]
    gt["prize_vnd"] = gt_eval["prize_vnd"]

    # 2. Chấm điểm Septet Bao 7
    bao7 = preds.get("septet_bao7", {})
    bao7_nums = bao7.get("numbers", [])
    bao7_eval = evaluate_bao7(norm_game, bao7_nums, actual_main, special_ball)
    bao7["hits"] = bao7_eval["hits"]
    bao7["matched_balls"] = bao7_eval["matched_balls"]
    bao7["cost_vnd"] = bao7_eval["cost_vnd"]
    bao7["prize_vnd"] = bao7_eval["prize_vnd"]
    bao7["winning_combinations_count"] = bao7_eval["winning_combinations_count"]
    if bao7_eval["prize_vnd"] > 0:
        winning_subs = [t for t in bao7_eval.get("sub_tickets", []) if t.get("prize_vnd", 0) > 0]
        best_tier = winning_subs[0]["prize_tier"] if winning_subs else "Trúng giải"
        cnt = bao7_eval["winning_combinations_count"]
        bao7["prize_tier"] = f"{best_tier} (Bao 7: {cnt} giải)" if cnt > 1 else best_tier
    else:
        bao7["prize_tier"] = "Không trúng"

    # 3. Chấm điểm Banker Wheeling
    bw = preds.get("banker_wheeling", {})
    bw_tickets = bw.get("tickets", [])
    bw_eval = evaluate_banker_wheeling(norm_game, bw_tickets, actual_main, special_ball)
    bw["tickets_count"] = bw_eval["tickets_count"]
    bw["cost_vnd"] = bw_eval["cost_vnd"]
    bw["best_hits"] = bw_eval["best_hits"]
    bw["winning_tickets_count"] = bw_eval["winning_tickets_count"]
    bw["total_prize_vnd"] = bw_eval["total_prize_vnd"]

    # 4. Chấm điểm Core Pool
    cp = preds.get("core_pool", {})
    cp_nums = cp.get("numbers", [])
    cp_matched = sorted(list(set(cp_nums) & set(actual_main)))
    cp["pool_size"] = len(cp_nums)
    cp["hits"] = len(cp_matched)
    cp["matched_balls"] = cp_matched

    # 5. Tổng kết hiệu quả tài chính P&L
    total_investment = gt.get("cost_vnd", 10000) + bao7.get("cost_vnd", 70000) + bw.get("cost_vnd", 0)
    total_return = gt["prize_vnd"] + bao7["prize_vnd"] + bw["total_prize_vnd"]
    net_profit = total_return - total_investment
    roi_pct = round((net_profit / total_investment) * 100, 2) if total_investment > 0 else 0.0
    has_win = (total_return > 0)

    # Cập nhật bản ghi
    target_record["actual_result"] = actual_main
    target_record["special_ball"] = special_ball
    target_record["status"] = "verified"
    target_record["verified_at"] = datetime.now().isoformat()
    if latest_draw.get("date") and not target_record.get("draw_date"):
        target_record["draw_date"] = latest_draw["date"]

    target_record["summary_metrics"] = {
        "total_investment_vnd": total_investment,
        "total_return_vnd": total_return,
        "net_profit_vnd": net_profit,
        "roi_pct": roi_pct,
        "has_winning_prize": has_win,
    }

    records[target_idx] = target_record
    save_all_ledger_records_atomic(ledger_path, records)
    return target_record


def get_ledger_web_summary(
    game_key: str,
    limit: int = 50,
    data_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Trích xuất báo cáo tổng hợp hiệu suất đối soát để phục vụ render Web GUI:
    - total_tracked_draws: Tổng số kỳ đã hoàn tất mở thưởng & đối soát.
    - overall_win_rate_pct: Tỷ lệ % các kỳ có tiền thưởng trúng giải.
    - golden_ticket_avg_hits: Số bóng trúng trung bình của Vé Vàng.
    - septet_avg_hits: Số bóng trúng trung bình của Bao 7.
    - cumulative_pnl: Tổng tiền đầu tư, tổng tiền trúng, lợi nhuận ròng và ROI %.
    - current_pending_draw: Thông tin kỳ tiếp theo đang niêm phong chờ quay.
    - history: Lịch sử đối soát chi tiết từng kỳ (sắp xếp giảm dần từ kỳ mới nhất).
    """
    ledger_path = get_ledger_path(game_key, data_dir=data_dir)
    records = load_ledger_records(ledger_path)

    verified_records = [r for r in records if r.get("status") == "verified"]
    pending_records = [r for r in records if r.get("status") == "pending"]
    current_pending = pending_records[-1] if pending_records else None

    if not verified_records:
        return {
            "total_tracked_draws": 0,
            "overall_win_rate_pct": 0.0,
            "golden_ticket_avg_hits": 0.0,
            "septet_avg_hits": 0.0,
            "cumulative_pnl": {
                "total_spent": 0,
                "total_won": 0,
                "net_profit": 0,
                "roi_pct": 0.0,
            },
            "current_pending_draw": current_pending,
            "history": [],
        }

    total_tracked = len(verified_records)
    winning_count = sum(1 for r in verified_records if r.get("summary_metrics", {}).get("has_winning_prize", False))
    win_rate = round((winning_count / total_tracked) * 100, 1)

    gt_hits = [r.get("predictions", {}).get("golden_ticket", {}).get("hits", 0) for r in verified_records]
    avg_gt_hits = round(sum(gt_hits) / max(1, len(gt_hits)), 2)

    bao7_hits = [r.get("predictions", {}).get("septet_bao7", {}).get("hits", 0) for r in verified_records]
    avg_bao7_hits = round(sum(bao7_hits) / max(1, len(bao7_hits)), 2)

    total_spent = sum(r.get("summary_metrics", {}).get("total_investment_vnd", 0) for r in verified_records)
    total_won = sum(r.get("summary_metrics", {}).get("total_return_vnd", 0) for r in verified_records)
    net_profit = total_won - total_spent
    roi_pct = round((net_profit / total_spent) * 100, 2) if total_spent > 0 else 0.0

    history = list(reversed(verified_records))[:limit]

    return {
        "total_tracked_draws": total_tracked,
        "overall_win_rate_pct": win_rate,
        "golden_ticket_avg_hits": avg_gt_hits,
        "septet_avg_hits": avg_bao7_hits,
        "cumulative_pnl": {
            "total_spent": total_spent,
            "total_won": total_won,
            "net_profit": net_profit,
            "roi_pct": roi_pct,
        },
        "current_pending_draw": current_pending,
        "history": history,
    }


def seed_historical_ledger(
    game_key: str,
    count: int = 35,
    data_dir: Optional[Path] = None,
) -> int:
    """
    Gieo mầm dữ liệu lịch sử đối soát bằng mô hình Walk-Forward nghiêm ngặt:
    - Với mỗi kỳ T trong 'count' kỳ gần nhất, chỉ sử dụng dữ liệu từ kỳ T-1 trở về trước để dự đoán.
    - Chấm điểm bằng prediction_evaluator và lưu vào sổ nhật ký dưới dạng 'verified'.
    - Tạo bản ghi 'pending' niêm phong cho kỳ quay sắp tới.
    - 100% Zero Mock Data & Zero Look-Ahead Bias.
    """
    base_dir = Path(data_dir) if data_dir else DATA_DIR
    norm_game = normalize_game_key(game_key)

    # Đọc tệp dữ liệu cào thực tế
    raw_path = base_dir / f"{norm_game}.jsonl"
    if not raw_path.exists():
        return 0

    all_raw_records = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            l = line.strip()
            if l:
                try:
                    all_raw_records.append(json.loads(l))
                except Exception:
                    continue

    if len(all_raw_records) < 15:
        return 0

    from vietlott.model.ensemble_engine import calculate_multi_model_consensus_and_backtest
    from vietlott.model.banker_wheeling import generate_key_banker_tickets

    if norm_game == "power655":
        p_key = "power_655"
        max_v = 55
        num_b = 6
        is_two_m = False
    elif norm_game == "power645":
        p_key = "power_645"
        max_v = 45
        num_b = 6
        is_two_m = False
    else:  # power535
        p_key = "power_535"
        max_v = 35
        num_b = 5
        is_two_m = True

    eval_count = min(count, len(all_raw_records) - 10)
    # Lấy đủ cửa sổ lịch sử cần thiết để chạy
    sample_records = all_raw_records[-(eval_count + 80):]

    res = calculate_multi_model_consensus_and_backtest(
        sample_records,
        product_key=p_key,
        max_val=max_v,
        num_balls=num_b,
        is_two_matrix=is_two_m,
        num_draws=eval_count,
        display_draws=eval_count,
    )

    if not res:
        return 0

    hw_logs = res.get("history_walk_forward", [])

    # Map tra cứu draw gốc để lấy special ball chuẩn
    raw_by_id = {}
    for r in sample_records:
        cid = _norm_draw_id(r.get("id", ""))
        raw_by_id[cid] = r

    ledger_records: List[Dict[str, Any]] = []

    for item in hw_logs:
        draw_id = _norm_draw_id(item.get("drawId", ""))
        date_str = item.get("date", "")
        raw_draw = raw_by_id.get(draw_id, {})
        actual_main, special_ball = _extract_draw_actual(raw_draw, norm_game)
        if not actual_main:
            actual_main = item.get("actual", [])

        # Vé Vàng (Golden ticket từ top_con)
        pred_golden = item.get("predicted", [])
        # Bao 7
        septet_data = item.get("optimalSeptet", {})
        pred_septet = septet_data.get("numbers", [])
        # Core Pool
        core_pool_nums = item.get("corePool", [])
        # Banker Wheeling: lấy triad[0] làm banker, satellite từ corePool
        triad_nums = item.get("triad", [])
        banker_num = triad_nums[0] if triad_nums else (core_pool_nums[0] if core_pool_nums else 1)
        satellite = [b for b in core_pool_nums if b != banker_num][:10]
        seed_val = int(draw_id) if draw_id.isdigit() else 42
        bw_res = generate_key_banker_tickets(
            banker=banker_num,
            satellite_pool=satellite,
            product_key=p_key,
            max_val=max_v,
            num_balls=num_b,
            num_tickets=6,
            seed=seed_val,
        )

        preds_input = {
            "golden_ticket": {"numbers": pred_golden, "cost_vnd": 10000},
            "septet_bao7": {"numbers": pred_septet, "cost_vnd": (60000 if is_two_m else 70000)},
            "banker_wheeling": {
                "banker": banker_num,
                "tickets": bw_res.get("tickets", []),
                "tickets_count": bw_res.get("total_tickets", 6),
                "cost_vnd": bw_res.get("total_cost", 60000),
            },
            "core_pool": {"numbers": core_pool_nums},
        }

        formatted_preds = _format_predictions_input(preds_input, norm_game)

        # Chấm điểm
        eval_gt = evaluate_ticket(norm_game, pred_golden, actual_main, special_ball)
        formatted_preds["golden_ticket"]["hits"] = eval_gt["hits"]
        formatted_preds["golden_ticket"]["matched_balls"] = eval_gt["matched_balls"]
        formatted_preds["golden_ticket"]["prize_tier"] = eval_gt["prize_tier"]
        formatted_preds["golden_ticket"]["prize_vnd"] = eval_gt["prize_vnd"]

        eval_bao7 = evaluate_bao7(norm_game, pred_septet, actual_main, special_ball)
        formatted_preds["septet_bao7"]["hits"] = eval_bao7["hits"]
        formatted_preds["septet_bao7"]["matched_balls"] = eval_bao7["matched_balls"]
        formatted_preds["septet_bao7"]["prize_vnd"] = eval_bao7["prize_vnd"]
        formatted_preds["septet_bao7"]["winning_combinations_count"] = eval_bao7["winning_combinations_count"]
        if eval_bao7["prize_vnd"] > 0:
            winning_subs = [t for t in eval_bao7.get("sub_tickets", []) if t.get("prize_vnd", 0) > 0]
            best_tier = winning_subs[0]["prize_tier"] if winning_subs else "Trúng giải"
            cnt = eval_bao7["winning_combinations_count"]
            formatted_preds["septet_bao7"]["prize_tier"] = f"{best_tier} (Bao 7: {cnt} giải)" if cnt > 1 else best_tier
        else:
            formatted_preds["septet_bao7"]["prize_tier"] = "Không trúng"

        eval_bw = evaluate_banker_wheeling(norm_game, bw_res.get("tickets", []), actual_main, special_ball)
        formatted_preds["banker_wheeling"]["best_hits"] = eval_bw["best_hits"]
        formatted_preds["banker_wheeling"]["winning_tickets_count"] = eval_bw["winning_tickets_count"]
        formatted_preds["banker_wheeling"]["total_prize_vnd"] = eval_bw["total_prize_vnd"]

        matched_cp = sorted(list(set(core_pool_nums) & set(actual_main)))
        formatted_preds["core_pool"]["hits"] = len(matched_cp)
        formatted_preds["core_pool"]["matched_balls"] = matched_cp

        # Metrics
        tot_invest = (
            formatted_preds["golden_ticket"]["cost_vnd"]
            + formatted_preds["septet_bao7"]["cost_vnd"]
            + formatted_preds["banker_wheeling"]["cost_vnd"]
        )
        tot_return = (
            formatted_preds["golden_ticket"]["prize_vnd"]
            + formatted_preds["septet_bao7"]["prize_vnd"]
            + formatted_preds["banker_wheeling"]["total_prize_vnd"]
        )
        net_prof = tot_return - tot_invest
        roi = round((net_prof / tot_invest) * 100, 2) if tot_invest > 0 else 0.0

        rec = {
            "draw_id": draw_id,
            "draw_date": date_str,
            "target_draw_id": draw_id,
            "created_at": datetime.now().isoformat(),
            "verified_at": datetime.now().isoformat(),
            "status": "verified",
            "actual_result": actual_main,
            "special_ball": special_ball,
            "predictions": formatted_preds,
            "summary_metrics": {
                "total_investment_vnd": tot_invest,
                "total_return_vnd": tot_return,
                "net_profit_vnd": net_prof,
                "roi_pct": roi,
                "has_winning_prize": (tot_return > 0),
            },
        }
        ledger_records.append(rec)

    # Tạo bản ghi pending cho kỳ quay tiếp theo
    next_raw_id = res.get("next_draw_id", "")
    next_clean_id = _norm_draw_id(next_raw_id)
    next_tickets = res.get("tickets", {})

    pending_rec_preds = _format_predictions_input(next_tickets, norm_game)
    next_invest = (
        pending_rec_preds["golden_ticket"]["cost_vnd"]
        + pending_rec_preds["septet_bao7"]["cost_vnd"]
        + pending_rec_preds["banker_wheeling"]["cost_vnd"]
    )

    pending_rec = {
        "draw_id": next_clean_id,
        "draw_date": "",
        "target_draw_id": next_clean_id,
        "created_at": datetime.now().isoformat(),
        "verified_at": None,
        "status": "pending",
        "actual_result": None,
        "special_ball": None,
        "predictions": pending_rec_preds,
        "summary_metrics": {
            "total_investment_vnd": next_invest,
            "total_return_vnd": 0,
            "net_profit_vnd": 0,
            "roi_pct": 0.0,
            "has_winning_prize": False,
        },
    }
    ledger_records.append(pending_rec)

    # Lưu toàn bộ vào file ledger
    ledger_path = get_ledger_path(norm_game, data_dir=base_dir)
    save_all_ledger_records_atomic(ledger_path, ledger_records)
    return len(hw_logs)


__all__ = [
    "normalize_game_key",
    "get_ledger_path",
    "load_ledger_records",
    "save_all_ledger_records_atomic",
    "save_ledger_record_atomic",
    "snapshot_next_prediction",
    "verify_and_update_ledger",
    "get_ledger_web_summary",
    "seed_historical_ledger",
]
