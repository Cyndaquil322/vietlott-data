#!/usr/bin/env python
"""
auto_draw_monitor.py
====================
Hệ thống Giám sát & Đối soát Tự động Kết quả Vietlott (Auto-Draw Monitor & Audit).

Tính năng:
1. Lịch mở thưởng chuẩn xác:
   - Power 6/55: Thứ 3, Thứ 5, Thứ 7 (18:10 - 18:35)
   - Mega 6/45:  Thứ 4, Thứ 6, Chủ Nhật (18:10 - 18:35)
   - Power 5/35: Hàng ngày (21:10 - 21:35)
2. Tự động cào kết quả trực tiếp ngay khi Vietlott phát hành.
3. Đối soát tức thì (Instant Post-Draw Audit):
   - So khớp kết quả thực tế với Bộ 3 Kiềng 3 Chân (Triad), Top 5 Ngũ Thủ,
     Dàn Bao Thu Gọn 4 Vé (Wheeling 4 tickets) và Vé Đơn Consensus.
   - Xuất bảng đối soát trực quan ra Terminal và lưu vào logs/auto_draw_audit.log.
4. Tự động Render lại giao diện web (render_web_data.py).
5. Tùy chọn tự động Git Commit & Push cập nhật GitHub Pages (--git-push).
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure UTF-8 stdout on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vietlott.sync_live_data import main as sync_all_data
from vietlott.render_web_data import main as render_web_data


def setup_logger():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "auto_draw_audit.log"
    return log_file


def log_message(msg: str, to_console: bool = True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    if to_console:
        print(formatted)
    try:
        log_file = setup_logger()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"Warning: could not write to log file: {e}")


def load_json_summary() -> Optional[Dict[str, Any]]:
    summary_path = DATA_DIR / "vietlott_summary.json"
    if not summary_path.exists():
        return None
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Error loading summary JSON: {e}")
        return None


def audit_game_predictions(game_key: str, game_data: Dict[str, Any]) -> str:
    game_title = game_data.get("name", game_key.upper())
    hub = game_data.get("consensus_hub", {})
    history = hub.get("history_walk_forward", [])
    next_draw_id = hub.get("next_draw_id", "N/A")
    upcoming_tickets = hub.get("tickets", {})

    if not history:
        return f"\n[AUDIT] {game_title}: Chưa có dữ liệu đối soát Walk-Forward."

    # Lấy kỳ đối soát mới nhất
    latest_audit = history[0]
    draw_id = latest_audit.get("drawId", "N/A")
    draw_date = latest_audit.get("date", "N/A")
    actual = latest_audit.get("actual", [])
    matched_consensus = latest_audit.get("matched", [])
    consensus_hit_count = latest_audit.get("matchCount", len(matched_consensus))

    triad = latest_audit.get("triad", [])
    triad_matched = latest_audit.get("triadMatched", [])
    triad_count = latest_audit.get("triadMatchCount", len(triad_matched))

    key5 = latest_audit.get("key5", [])
    key5_matched = latest_audit.get("key5Matched", [])
    key5_count = latest_audit.get("key5MatchCount", len(key5_matched))

    wheel4 = latest_audit.get("wheel4", {})
    wheel_hits = wheel4.get("ticketHits", [])
    wheel_max = wheel4.get("maxHit", 0)
    wheel_prize = wheel4.get("wonPrize", False)

    actual_str = " - ".join(f"{x:02d}" for x in actual)
    triad_str = " - ".join(f"{x:02d}" for x in triad)
    triad_hit_str = " - ".join(f"{x:02d}" for x in triad_matched) if triad_matched else "0 số"
    key5_str = " - ".join(f"{x:02d}" for x in key5)
    key5_hit_str = " - ".join(f"{x:02d}" for x in key5_matched) if key5_matched else "0 số"

    # Vé chuẩn bị cho kỳ tiếp theo
    clean_next_id = next_draw_id.lstrip("#")
    next_triad = upcoming_tickets.get("key_balls", [])
    next_key5 = upcoming_tickets.get("key_5_balls", [])
    next_triad_str = " - ".join(f"{x:02d}" for x in next_triad) if next_triad else "Đang tính"
    next_key5_str = " - ".join(f"{x:02d}" for x in next_key5) if next_key5 else "Đang tính"

    border = "=" * 74
    sub_border = "-" * 74
    audit_report = [
        border,
        f" ĐỐI SOÁT CHUẨN XÁC: {game_title.upper()} - KỲ #{draw_id} ({draw_date})",
        border,
        f" Kết Quả Thực Tế           : [ {actual_str} ]",
        sub_border,
        f" • Kiềng 3 Chân (Triad)    : [ {triad_str} ]",
        f"   -> Khớp {triad_count}/3 bóng: [ {triad_hit_str} ] {'(ĐẠT CHỈ TIÊU)' if triad_count >= 1 else '(TRƯỢT)'}",
        sub_border,
        f" • Top 5 Ngũ Thủ (Key 5)   : [ {key5_str} ]",
        f"   -> Khớp {key5_count}/5 bóng: [ {key5_hit_str} ] {'(TRÚNG LỚN)' if key5_count >= 2 else ('(ĐẠT CHỈ TIÊU)' if key5_count == 1 else '(TRƯỢT)')}",
        sub_border,
        f" • Dàn Bao 4 Vé (Wheel 4)  : Max Hit = {wheel_max} bóng | {'CÓ TRÚNG GIẢI' if wheel_prize else 'Không có giải'}",
        f"   -> Điểm trúng 4 vé      : {wheel_hits}",
        sub_border,
        f" • Vé Consensus 6 số       : Khớp {consensus_hit_count} bóng",
        border,
        f" DỰ BÁO KỲ TIẾP THEO #{clean_next_id}:",
        f"   - Kiềng 3 Chân : [ {next_triad_str} ]",
        f"   - Top 5 Ngũ Thủ: [ {next_key5_str} ]",
        border,
    ]

    return "\n".join(audit_report)


def execute_audit_and_report():
    summary = load_json_summary()
    if not summary or "products" not in summary:
        log_message("Chưa tìm thấy dữ liệu vietlott_summary.json để đối soát.")
        return

    log_message("\n" + "#" * 74)
    log_message("# BẢNG TỔNG HỢP ĐỐI SOÁT CÁC KỲ QUAY VIETLOTT MỚI NHẤT (WALK-FORWARD)")
    log_message("#" * 74)

    products = summary.get("products", {})
    for game_key in ["power_655", "power_645", "power_535"]:
        if game_key in products:
            report = audit_game_predictions(game_key, products[game_key])
            log_message(report)


def is_near_draw_time() -> Tuple[bool, str, int]:
    now = datetime.now()
    t_18_10 = now.replace(hour=18, minute=10, second=0, microsecond=0)
    t_18_45 = now.replace(hour=18, minute=45, second=0, microsecond=0)

    t_21_10 = now.replace(hour=21, minute=10, second=0, microsecond=0)
    t_21_45 = now.replace(hour=21, minute=45, second=0, microsecond=0)

    if t_18_10 <= now <= t_18_45:
        return True, "Khung giờ quay 18:10 - 18:45 (Power 6/55, Mega 6/45, Max 3D)", 120
    if t_21_10 <= now <= t_21_45:
        return True, "Khung giờ quay 21:10 - 21:45 (Power 5/35)", 120

    next_slots = []
    if now < t_18_10:
        next_slots.append(t_18_10)
    if now < t_21_10:
        next_slots.append(t_21_10)

    tomorrow_18_10 = t_18_10 + timedelta(days=1)
    next_slots.append(tomorrow_18_10)

    closest_slot = min(next_slots)
    delta_seconds = int((closest_slot - now).total_seconds())

    sleep_time = min(delta_seconds, 600)
    return False, f"Chờ phiên quay tiếp theo lúc {closest_slot.strftime('%H:%M %d/%m/%Y')} ({delta_seconds // 60} phút nữa)", sleep_time


def trigger_git_sync():
    log_message("[GIT] Đang tiến hành commit & push dữ liệu mới lên GitHub...")
    try:
        subprocess.run(["git", "add", "data/", "docs/"], cwd=str(PROJECT_ROOT), check=True)
        commit_msg = f"chore(auto-draw): update Vietlott draw results & audit logs at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
            log_message("[GIT] Không có thay đổi nào mới để commit.")
            return

        push_res = subprocess.run(["git", "push"], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        if push_res.returncode == 0:
            log_message("[GIT] Push thành công lên repository!")
        else:
            log_message(f"[GIT] Push gặp lỗi: {push_res.stderr.strip()}")
    except Exception as e:
        log_message(f"[GIT] Lỗi khi thực thi git sync: {e}")


def check_and_sync_once(auto_push: bool = False) -> int:
    log_message("[MONITOR] Đang kiểm tra kỳ quay mới từ máy chủ Vietlott...")
    sync_results = sync_all_data(trigger_render=True)
    total_new = sum(sync_results.values()) if sync_results else 0

    if total_new > 0:
        log_message(f"[MONITOR] PHÁT HIỆN {total_new} KỲ QUAY MỚI! Chi tiết: {sync_results}")
        execute_audit_and_report()
        if auto_push:
            trigger_git_sync()
    else:
        log_message("[MONITOR] Dữ liệu hiện tại đã là mới nhất. Không có kỳ quay mới.")

    return total_new


def run_watch_loop(auto_push: bool = False):
    log_message("[DAEMON] Khởi động chế độ Giám sát Tự động (Auto-Draw Watch Daemon). Nhấn Ctrl+C để dừng.")
    try:
        while True:
            in_draw_window, status_desc, sleep_sec = is_near_draw_time()
            log_message(f"[STATUS] {status_desc}")

            if in_draw_window:
                log_message("[POLL] Đang trong khung giờ quay! Kiểm tra dữ liệu mỗi 2 phút...")
                new_draws = check_and_sync_once(auto_push=auto_push)
                if new_draws > 0:
                    log_message("[SUCCESS] Đã bắt thành công kết quả kỳ mới! Nghỉ 10 phút trước phiên tiếp theo...")
                    time.sleep(600)
                    continue

            time.sleep(sleep_sec)
    except KeyboardInterrupt:
        log_message("[DAEMON] Đã nhận tín hiệu dừng từ người dùng. Tạm biệt!")


def main():
    parser = argparse.ArgumentParser(description="Vietlott Auto-Draw Monitor & Instant Audit")
    parser.add_argument("--once", action="store_true", help="Kiểm tra và đồng bộ ngay 1 lần rồi kết thúc")
    parser.add_argument("--audit-latest", action="store_true", help="Chỉ hiển thị bảng đối soát các kỳ mới nhất hiện có")
    parser.add_argument("--watch", action="store_true", help="Chạy chế độ daemon tự động canh giờ mở thưởng")
    parser.add_argument("--git-push", action="store_true", help="Tự động git commit và push khi có kỳ quay mới")

    args = parser.parse_args()

    if getattr(args, "audit_latest", False):
        execute_audit_and_report()
        return

    if args.watch:
        run_watch_loop(auto_push=args.git_push)
    else:
        check_and_sync_once(auto_push=args.git_push)
        execute_audit_and_report()


if __name__ == "__main__":
    main()
