#!/usr/bin/env python
"""
sync_live_data.py
Synchronizes Vietlott lottery data directly from www.vietlott.vn to data/*.jsonl.
Automatically detects and backfills all missing draws from the latest file ID up to today.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Content-Type": "text/plain; charset=utf-8",
    "X-AjaxPro-Method": "ServerSideDrawResult",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.vietlott.vn",
}


def load_existing_data(file_path: Path) -> Dict[str, Dict]:
    if not file_path.exists():
        return {}
    res = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    d = json.loads(line)
                    raw_id = str(d.get("id", "")).replace("#", "").strip()
                    clean_id = str(int(raw_id)) if raw_id.isdigit() else raw_id
                    res[clean_id] = d
                except Exception:
                    continue
    return res


def save_data(file_path: Path, records_dict: Dict[str, Dict]):
    def sort_key(x):
        d_val = x.get("date", "")
        id_val = str(x.get("id", "")).replace("#", "").strip()
        num_id = int(id_val) if id_val.isdigit() else 0
        return (d_val, num_id)

    sorted_records = sorted(records_dict.values(), key=sort_key)
    with open(file_path, "w", encoding="utf-8") as f:
        for r in sorted_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def sync_power(name: str, url: str, key: str, file_path: Path, array_len: int = 5, max_pages: int = 35):
    print(f"\n=== Syncing {name} ===")
    existing = load_existing_data(file_path)
    latest_local_id = int(max(existing.keys(), key=lambda x: int(x))) if existing else 0
    print(f"Latest local draw: #{latest_local_id} (Total: {len(existing)})")

    new_draws = 0
    stop = False

    for page in range(0, max_pages):
        body = {
            "ORenderInfo": {"SiteId": "main.frontend.vi", "SiteAlias": "main.vi", "SiteLang": "vi"},
            "Key": key,
            "GameDrawId": "",
            "ArrayNumbers": [["" for _ in range(18)] for _ in range(array_len)],
            "CheckMulti": False,
            "PageIndex": page,
        }
        try:
            res = requests.post(url, headers=HEADERS, json=body, timeout=12)
            if not res.ok:
                print(f"Page {page} request failed: {res.status_code}")
                break
            data = res.json()
            html = data.get("value", {}).get("HtmlContent", "")
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select("table tr")[1:]
            if not rows:
                break

            for tr in rows:
                tds = tr.find_all("td")
                if len(tds) < 3:
                    continue
                d_str = datetime.strptime(tds[0].text.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
                draw_id = str(int(tds[1].text.strip())).zfill(5)
                clean_id = str(int(draw_id))

                nums = [int(s.text.strip()) for s in tds[2].find_all("span") if s.text.strip() != "|"]

                if clean_id not in existing:
                    existing[clean_id] = {
                        "date": d_str,
                        "id": draw_id,
                        "result": nums,
                        "page": page,
                        "process_time": datetime.now().isoformat(),
                    }
                    new_draws += 1
                elif int(clean_id) <= latest_local_id:
                    # Overlapped with existing historical data
                    stop = True

            print(f"Page {page}: processed {len(rows)} draws (latest on page: #{rows[0].find_all('td')[1].text.strip()})")
            if stop:
                print(f"Reached existing data overlap at page {page}.")
                break
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    save_data(file_path, existing)
    print(f"[OK] {name} synced: +{new_draws} new draws. Total now: {len(existing)} draws.")


def sync_max3d(name: str, url: str, game_id: str, file_path: Path, max_pages: int = 35):
    print(f"\n=== Syncing {name} ===")
    existing = load_existing_data(file_path)
    latest_local_id = int(max(existing.keys(), key=lambda x: int(x))) if existing else 0
    print(f"Latest local draw: #{latest_local_id} (Total: {len(existing)})")

    new_draws = 0
    stop = False

    for page in range(1, max_pages + 1):
        body = {
            "CheckMulti": 0,
            "GameDrawId": "",
            "GameId": game_id,
            "ORenderInfo": {"SiteId": "main.frontend.vi", "SiteAlias": "main.vi", "SiteLang": "vi"},
            "PageIndex": page,
            "number01": "123",
            "number02": "321",
        }
        try:
            res = requests.post(url, headers=HEADERS, json=body, timeout=12)
            if not res.ok:
                break
            data = res.json()
            html = data.get("value", {}).get("HtmlContent", "")
            soup = BeautifulSoup(html, "html.parser")

            for tr in soup.select("table tr"):
                tds = tr.find_all("td")
                if not tds:
                    continue
                divs = tr.find_all("div")
                if not divs:
                    continue
                div_0_text = divs[0].get_text()
                if "Ngày:" not in div_0_text:
                    continue
                date_str = div_0_text.split("Ngày:")[1].strip()
                try:
                    d_str = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                except Exception:
                    continue

                td_a = tds[0].find_all("a")
                if not td_a:
                    continue
                draw_id = str(int(td_a[0].text.strip())).zfill(5)
                clean_id = str(int(draw_id))

                div_result = tr.find("div", class_="tong_day_so_ket_qua")
                if not div_result:
                    continue
                all_spans = div_result.find_all("span", class_="bong_tron")
                if len(all_spans) < 60:
                    continue

                prizes = [
                    {"name": "Giải Đặc biệt", "count": 6},
                    {"name": "Giải Nhất", "count": 12},
                    {"name": "Giải Nhì", "count": 18},
                    {"name": "Giải ba", "count": 24},
                ]
                results = {}
                cur_idx = 0
                for prize in prizes:
                    ball_texts = [all_spans[cur_idx + i].get_text().strip() for i in range(prize["count"])]
                    results[prize["name"]] = ["".join(ball_texts[j:j+3]) for j in range(0, len(ball_texts), 3)]
                    cur_idx += prize["count"]

                if clean_id not in existing:
                    existing[clean_id] = {
                        "date": d_str,
                        "id": draw_id,
                        "result": results,
                        "page": page,
                        "process_time": datetime.now().isoformat(),
                    }
                    new_draws += 1
                elif int(clean_id) <= latest_local_id:
                    stop = True

            print(f"Page {page} processed.")
            if stop:
                print(f"Reached existing data overlap at page {page}.")
                break
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    save_data(file_path, existing)
    print(f"[OK] {name} synced: +{new_draws} new draws. Total now: {len(existing)} draws.")


def sync_power535(file_path: Path, max_pages: int = 40):
    print(f"\n=== Syncing Power 5/35 ===")
    existing = load_existing_data(file_path)
    latest_local_id = int(max(existing.keys(), key=lambda x: int(x))) if existing else 0
    print(f"Latest local draw: #{latest_local_id} (Total: {len(existing)})")

    headers_info = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "text/plain; charset=utf-8",
        "X-AjaxPro-Method": "ServerSideFrontEndCreateRenderInfo",
        "Origin": "https://vietlott.vn",
    }
    try:
        r1 = requests.post(
            "https://vietlott.vn/ajaxpro/Vietlott.Utility.WebEnvironments,Vietlott.Utility.ashx",
            headers=headers_info,
            data=json.dumps({"SiteId": "main.frontend.vi"}),
            timeout=15,
        )
        render_info = r1.json().get("value")
        render_info["SiteLang"] = "vi"
    except Exception as e:
        print(f"Failed to get RenderInfo for 5/35: {e}")
        return

    headers_draw = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "text/plain; charset=utf-8",
        "X-AjaxPro-Method": "ServerSideDrawResult",
        "Origin": "https://vietlott.vn",
    }

    new_draws = 0
    stop = False
    for page in range(max_pages):
        body = {
            "ORenderInfo": render_info,
            "Key": "8a8d9359",
            "GameDrawId": "",
            "ArrayNumbers": [["" for _ in range(35)] for _ in range(5)],
            "CheckMulti": False,
            "PageIndex": page,
        }
        try:
            r2 = requests.post(
                "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game535CompareWebPart,Vietlott.PlugIn.WebParts.ashx",
                headers=headers_draw,
                data=json.dumps(body),
                timeout=15,
            )
            val = r2.json().get("value", {})
            if val.get("Error"):
                break
            html = val.get("HtmlContent", "")
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.find_all("tr")
            page_items = 0
            for tr in rows:
                tds = [td.text.strip() for td in tr.find_all("td")]
                if len(tds) >= 3 and "|" in tds[2]:
                    date_str, draw_id_raw, nums_str = tds[0], tds[1], tds[2]
                    draw_id = str(draw_id_raw).replace("#", "").strip().zfill(5)
                    clean_id = str(int(draw_id))
                    parts = nums_str.split("|")
                    main_str = parts[0]
                    spec_str = parts[1]
                    main_nums = [int(main_str[i : i + 2]) for i in range(0, len(main_str), 2)]
                    spec_num = int(spec_str)
                    all_nums = main_nums + [spec_num]
                    dt = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

                    if clean_id not in existing:
                        existing[clean_id] = {
                            "date": dt,
                            "id": draw_id,
                            "result": all_nums,
                            "page": page,
                            "process_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        new_draws += 1
                        page_items += 1
                    else:
                        page_items += 1
                        if int(clean_id) <= latest_local_id:
                            stop = True

            if stop or page_items == 0:
                print(f"Reached existing data overlap at page {page}.")
                break
        except Exception as e:
            print(f"Error on 5/35 page {page}: {e}")
            break

    save_data(file_path, existing)
    print(f"[OK] Power 5/35 synced: +{new_draws} new draws. Total now: {len(existing)} draws.")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Power 6/55
    sync_power(
        name="Power 6/55",
        url="https://www.vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game655CompareWebPart,Vietlott.PlugIn.WebParts.ashx",
        key="23bbd667",
        file_path=DATA_DIR / "power655.jsonl",
        array_len=5,
        max_pages=35,
    )

    # 2. Mega 6/45
    sync_power(
        name="Mega 6/45",
        url="https://www.vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game645CompareWebPart,Vietlott.PlugIn.WebParts.ashx",
        key="785cdae0",
        file_path=DATA_DIR / "power645.jsonl",
        array_len=6,
        max_pages=35,
    )

    # 3. Power 5/35
    sync_power535(
        file_path=DATA_DIR / "power535.jsonl",
        max_pages=35,
    )

    # 4. Max 3D
    sync_max3d(
        name="Max 3D",
        url="https://www.vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.GameMax3DCompareWebPart,Vietlott.PlugIn.WebParts.ashx",
        game_id="5",
        file_path=DATA_DIR / "3d.jsonl",
        max_pages=35,
    )

    # 5. Max 3D Pro
    sync_max3d(
        name="Max 3D Pro",
        url="https://www.vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.GameMax3DProCompareWebPart,Vietlott.PlugIn.WebParts.ashx",
        game_id="6",
        file_path=DATA_DIR / "3d_pro.jsonl",
        max_pages=35,
    )

    print("\n=== Live Sync Complete! Regenerating Web Data ===")
    try:
        from vietlott.render_web_data import main as render_web
    except ModuleNotFoundError:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from render_web_data import main as render_web
    render_web()


if __name__ == "__main__":
    main()
