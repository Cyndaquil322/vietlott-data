#!/usr/bin/env python
"""
sync_bingo18.py
Module crawler chuyên biệt siêu tốc cho Bingo 18 (quay 10 phút/lần).
Bóc tách chính xác 3 số xúc xắc, tổng, Lớn/Nhỏ/Hòa, và cờ Bão (Triple),
có cơ chế dừng sớm khi gặp latest_local_id và ghi file nguyên tử.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DATA_DIR = PROJECT_ROOT / "data"

URL_BINGO18 = (
    "https://www.vietlott.vn/ajaxpro/"
    "Vietlott.PlugIn.WebParts.GameBingoCompareWebPart,Vietlott.PlugIn.WebParts.ashx"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Content-Type": "text/plain; charset=utf-8",
    "X-AjaxPro-Method": "ServerSideDrawResult",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.vietlott.vn",
}


def get_robust_session() -> requests.Session:
    """Tạo session HTTP có cơ chế tự động thử lại (Retry & Exponential Backoff)."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def load_existing_bingo18(file_path: Path) -> Dict[str, Dict[str, Any]]:
    """Đọc dữ liệu hiện có từ file JSONL, trả về dict index bởi clean_id."""
    if not file_path.exists():
        return {}
    res: Dict[str, Dict[str, Any]] = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                raw_id = str(d.get("id", "")).replace("#", "").strip()
                clean_id = str(int(raw_id)) if raw_id.isdigit() else raw_id
                if "is_triple" not in d and isinstance(d.get("result"), list) and len(d["result"]) == 3:
                    d["is_triple"] = (d["result"][0] == d["result"][1] == d["result"][2])
                res[clean_id] = d
            except Exception:
                continue
    return res


def save_bingo18_data(file_path: Path, records_dict: Dict[str, Dict[str, Any]]) -> None:
    """Ghi file dữ liệu nguyên tử (Atomic Write) chống hỏng dữ liệu khi bị ngắt."""
    def sort_key(x: Dict[str, Any]):
        d_val = x.get("date", "")
        id_val = str(x.get("id", "")).replace("#", "").strip()
        num_id = int(id_val) if id_val.isdigit() else 0
        return (d_val, num_id)

    sorted_records = sorted(records_dict.values(), key=sort_key)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = file_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for r in sorted_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp_path.replace(file_path)


def parse_bingo18_html(html: str) -> List[Dict[str, Any]]:
    """
    Phân tích bảng kết quả HTML của Bingo 18:
      - date: YYYY-MM-DD
      - id: mã kỳ 7 chữ số (ví dụ '0185891')
      - result: danh sách 3 số nguyên [X1, X2, X3], X_i in [1, 6]
      - total: tổng điểm trong khoảng [3, 18]
      - large_small: 'Lớn', 'Nhỏ', hoặc 'Hòa'
      - is_triple: True nếu X1 == X2 == X3
    """
    if not html or not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    records: List[Dict[str, Any]] = []

    for tr in soup.select("table tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        # 1. Trích xuất Date và ID
        links = tds[0].find_all("a")
        date_str = None
        draw_id = None
        if len(links) >= 2:
            date_raw = links[0].get_text(strip=True)
            id_raw = links[1].get_text(strip=True)
            try:
                date_str = datetime.strptime(date_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
                draw_id = id_raw.replace("#", "").strip().zfill(7)
            except Exception:
                pass

        if not date_str or not draw_id:
            text_col0 = tds[0].get_text()
            m_date = re.search(r"(\d{2}/\d{2}/\d{4})", text_col0)
            m_id = re.search(r"#?(\d+)", text_col0)
            if m_date and m_id:
                try:
                    date_str = datetime.strptime(m_date.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
                    draw_id = m_id.group(1).zfill(7)
                except Exception:
                    continue
            else:
                continue

        # 2. Trích xuất kết quả 3 viên xúc xắc [1..6]
        result_spans = tds[1].find_all("span")
        result = [
            int(span.get_text(strip=True))
            for span in result_spans
            if span.get_text(strip=True).isdigit()
        ]
        if len(result) != 3 or not all(1 <= x <= 6 for x in result):
            nums = [int(x) for x in re.findall(r"\b[1-6]\b", tds[1].get_text())]
            if len(nums) >= 3:
                result = nums[:3]
            else:
                continue

        if len(result) != 3 or not all(1 <= x <= 6 for x in result):
            continue

        # 3. Trích xuất Tổng điểm [3..18]
        total = None
        if len(tds) > 2:
            t_text = tds[2].get_text(strip=True)
            if t_text.isdigit():
                total = int(t_text)
        if total is None or not (3 <= total <= 18):
            total = sum(result)

        # 4. Trích xuất Lớn / Nhỏ / Hòa
        large_small = ""
        if len(tds) > 3:
            ls_text = tds[3].get_text(strip=True)
            if ls_text in ("Lớn", "Nhỏ", "Hòa"):
                large_small = ls_text
        if not large_small:
            if total in (10, 11):
                large_small = "Hòa"
            elif total >= 12:
                large_small = "Lớn"
            else:
                large_small = "Nhỏ"

        # 5. Cờ Bão (Triple: 3 số bằng nhau)
        is_triple = (result[0] == result[1] == result[2])

        records.append({
            "date": date_str,
            "id": draw_id,
            "result": result,
            "total": total,
            "large_small": large_small,
            "is_triple": is_triple,
        })

    return records


def parse_bingo18_direct_page(html: str) -> List[Dict[str, Any]]:
    """
    Phân tích bảng kết quả HTML trực tiếp từ trang web chính của Vietlott
    (luôn chứa các kỳ mới nhất theo thời gian thực).
    """
    if not html or not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    records: List[Dict[str, Any]] = []

    for tr in soup.select("table tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        col0 = tds[0].get_text(strip=True)
        m_date = re.search(r"(\d{2}/\d{2}/\d{4})", col0)
        m_id = re.search(r"#(\d+)", col0)
        if not (m_date and m_id):
            continue

        d_str = datetime.strptime(m_date.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
        draw_id = m_id.group(1).zfill(7)

        spans = tds[1].find_all("span")
        if spans:
            nums = [int(s.get_text(strip=True)) for s in spans if s.get_text(strip=True).isdigit()]
        else:
            nums = [int(x) for x in re.findall(r"\b[1-6]\b", tds[1].get_text(strip=True))]

        if not nums:
            txt = tds[1].get_text(strip=True)
            if len(txt) == 3 and all(c in "123456" for c in txt):
                nums = [int(c) for c in txt]

        if len(nums) != 3 or not all(1 <= x <= 6 for x in nums):
            continue

        tot_txt = tds[2].get_text(strip=True)
        tot = int(tot_txt) if tot_txt.isdigit() else sum(nums)

        ls_type = tds[3].get_text(strip=True)
        if ls_type not in ["Lớn", "Nhỏ", "Hòa"]:
            ls_type = "Lớn" if tot >= 12 else ("Nhỏ" if tot <= 9 else "Hòa")

        is_triple = (nums[0] == nums[1] == nums[2])

        records.append({
            "date": d_str,
            "id": draw_id,
            "result": nums,
            "total": tot,
            "large_small": ls_type,
            "is_triple": is_triple,
        })

    return records


def sync_bingo18(file_path: Optional[Path] = None, max_pages: int = 25) -> int:
    """
    Đồng bộ dữ liệu Bingo 18 từ Vietlott:
      - BƯỚC 1: Cào trực tiếp trang live web để lấy ngay các kỳ mới nhất thời gian thực.
      - BƯỚC 2: Gửi POST AjaxPro từng trang để backfill toàn bộ khoảng trống lịch sử (gap) về tận initial_latest_id.
      - Ghi file nguyên tử ra data/bingo18.jsonl.
      - Trả về số kỳ mới cào được.
    """
    if file_path is None:
        file_path = DATA_DIR / "bingo18.jsonl"

    print(f"\n=== Syncing Bingo 18 ===")
    existing = load_existing_bingo18(file_path)
    initial_latest_id = max((int(k) for k in existing.keys() if k.isdigit()), default=0)
    print(f"Latest local draw before sync: #{initial_latest_id:07d} (Total: {len(existing)})")

    session = get_robust_session()
    new_draws = 0

    # BƯỚC 1: Cào trực tiếp trang live web (thời gian thực, không bị trễ cache)
    live_url = "https://www.vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-bingo18?nocatche=1"
    try:
        live_headers = dict(HEADERS)
        live_headers["Cache-Control"] = "no-cache"
        live_headers["Pragma"] = "no-cache"
        live_res = session.get(live_url, headers=live_headers, timeout=12)
        if live_res.ok:
            live_records = parse_bingo18_direct_page(live_res.text)
            live_added = 0
            for r in live_records:
                clean_id = str(int(r["id"]))
                if clean_id not in existing:
                    r_with_meta = dict(r)
                    r_with_meta["page"] = 0
                    r_with_meta["process_time"] = datetime.now().isoformat()
                    existing[clean_id] = r_with_meta
                    new_draws += 1
                    live_added += 1
            if live_records:
                print(f"Live Page: parsed {len(live_records)} real-time draws, +{live_added} new (latest: #{live_records[0]['id']})")
    except Exception as e:
        print(f"Warning: could not fetch live page: {e}")

    # BƯỚC 2: Backfill từ AjaxPro để bù đắp bất kỳ khoảng trống (gap) nào
    stop = False
    consecutive_existing = 0

    for page in range(1, max_pages + 1):
        body = {
            "ORenderInfo": {
                "SiteId": "main.frontend.vi",
                "SiteAlias": "main.vi",
                "SiteLang": "vi",
            },
            "GameId": "8",
            "GameDrawNo": "",
            "number": "",
            "DrawDate": "",
            "PageIndex": page,
            "TotalRow": 0,
        }

        try:
            res = session.post(URL_BINGO18, headers=HEADERS, json=body, timeout=12)
            if not res.ok:
                print(f"Page {page} request failed: {res.status_code}")
                break

            data = res.json()
            html_content = ""
            val = data.get("value")
            if isinstance(val, dict):
                html_content = val.get("HtmlContent", "")
            elif isinstance(val, str):
                html_content = val

            records = parse_bingo18_html(html_content)
            if not records:
                print(f"Page {page}: no records found or empty page.")
                break

            page_new = 0
            for r in records:
                clean_id = str(int(r["id"]))
                if clean_id in existing:
                    consecutive_existing += 1
                    if consecutive_existing >= 12:  # Đã gặp 2 trang đầy đủ kỳ cũ liên tiếp
                        stop = True
                        break
                else:
                    consecutive_existing = 0
                    r_with_meta = dict(r)
                    r_with_meta["page"] = page
                    r_with_meta["process_time"] = datetime.now().isoformat()
                    existing[clean_id] = r_with_meta
                    new_draws += 1
                    page_new += 1

            print(f"Page {page}: parsed {len(records)} draws, +{page_new} new (latest on page: #{records[0]['id']})")
            if stop:
                print(f"Reached solid existing historical data (overlap >= 12 consecutive draws) at page {page}.")
                break
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    save_bingo18_data(file_path, existing)
    print(f"[OK] Bingo 18 synced: +{new_draws} new draws. Total now: {len(existing)} draws.")
    return new_draws


if __name__ == "__main__":
    sync_bingo18()
