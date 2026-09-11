#!/usr/bin/env python
"""
local_server.py
===============
Máy chủ Web Local tích hợp API Cào Dữ Liệu & Phân Tích Định Lượng Tự Động.

Tính năng:
1. Phục vụ giao diện tĩnh (Static Web Server) từ thư mục docs/ (Port 8088 mặc định).
2. API POST /api/crawl:
   - Kích hoạt crawler trực tiếp theo từng sản phẩm (Bingo 18, 5/35, 6/55, 6/45, Keno, 3D).
   - Tự động chạy ngay các thuật toán dự đoán, động lực học và Walk-Forward backtest.
   - Cập nhật tức thì file data/vietlott_summary.json và docs/data/vietlott_summary.json.
3. API GET /api/status:
   - Trả về thời gian cập nhật gần nhất và số lượng kỳ quay của từng sản phẩm.
"""

import json
import os
import sys
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Thiết lập đường dẫn thư mục gốc
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DATA_DIR = DOCS_DIR / "data"

if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))


class LocalVietlottHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS_DIR), **kwargs)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Cache-Control")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.handle_api_status()
        else:
            # Phục vụ file tĩnh từ thư mục docs
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/crawl":
            self.handle_api_crawl(parsed)
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def handle_api_status(self):
        summary_path = DOCS_DATA_DIR / "vietlott_summary.json"
        status_info = {
            "server": "Vietlott Local Analytics Server",
            "status": "running",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary_exists": summary_path.exists(),
        }
        if summary_path.exists():
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                status_info["last_generated"] = data.get("meta", {}).get("generated_at")
                products_summary = {}
                for k, v in data.get("products", {}).items():
                    products_summary[k] = {
                        "name": v.get("name"),
                        "total_draws": v.get("total_draws"),
                        "latest_id": (v.get("latest") or {}).get("id"),
                    }
                status_info["products"] = products_summary
            except Exception as e:
                status_info["error"] = str(e)

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(status_info, ensure_ascii=False).encode("utf-8"))

    def handle_api_crawl(self, parsed_url):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else b""
        
        # Parse params từ query hoặc body
        params = parse_qs(parsed_url.query)
        if post_body:
            try:
                body_json = json.loads(post_body.decode("utf-8"))
                for k, v in body_json.items():
                    params[k] = [v] if not isinstance(v, list) else v
            except Exception:
                pass

        product_key = params.get("product", ["bingo18"])[0]

        start_time = time.time()
        print(f"\n[API CRAWL] Nhận yêu cầu cào & phân tích cho sản phẩm: {product_key}")

        try:
            crawl_result = self._execute_live_crawl(product_key)
            elapsed = round(time.time() - start_time, 2)
            
            response_data = {
                "success": True,
                "product": product_key,
                "elapsed_seconds": elapsed,
                "message": crawl_result.get("message", "Đã cập nhật dữ liệu và tái tính toán dự đoán thành công!"),
                "details": crawl_result,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            status_code = 200
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            print(f"[API CRAWL ERROR] Lỗi khi cào dữ liệu: {e}")
            response_data = {
                "success": False,
                "product": product_key,
                "elapsed_seconds": elapsed,
                "error": str(e),
                "message": f"Không thể hoàn tất cào dữ liệu: {e}",
            }
            status_code = 500

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

    def _execute_live_crawl(self, product_key: str) -> dict:
        """Thực thi cào dữ liệu và tính toán lại dự đoán cho sản phẩm chỉ định."""
        import importlib
        from vietlott.render_web_data import read_jsonl

        if product_key in ["bingo18", "bingo"]:
            import vietlott.sync_bingo18
            importlib.reload(vietlott.sync_bingo18)
            from vietlott.sync_bingo18 import sync_bingo18

            import vietlott.render_web_data
            importlib.reload(vietlott.render_web_data)
            from vietlott.render_web_data import process_bingo18

            # 1. Cào dữ liệu mới nhất (siêu tốc, dừng sớm sau 1 request nếu đã mới nhất)
            added_count = sync_bingo18(DATA_DIR / "bingo18.jsonl")

            # 2. Đọc lại dữ liệu đầy đủ
            records = read_jsonl(DATA_DIR / "bingo18.jsonl")
            latest_id = records[-1].get("id") if records else "N/A"

            # 3. Phân tích định lượng chuyên sâu + Dự đoán 3 trạng thái + Song thủ + Walk-Forward
            bingo_data = {
                "name": "Bingo 18",
                "description": "Quay 5 phút/kỳ. Quay 3 số từ 1 đến 6.",
                "type": "bingo18",
                **process_bingo18(records)
            }

            # 4. Cập nhật file vietlott_summary.json trong data/ và docs/data/
            for path_str in [DATA_DIR / "vietlott_summary.json", DOCS_DATA_DIR / "vietlott_summary.json"]:
                if path_str.exists():
                    with open(path_str, "r", encoding="utf-8") as f:
                        summary = json.load(f)
                    summary["products"]["bingo18"] = bingo_data
                    summary["meta"]["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    tmp_p = path_str.with_suffix(".json.tmp")
                    with open(tmp_p, "w", encoding="utf-8") as f:
                        json.dump(summary, f, ensure_ascii=False, indent=2)
                    tmp_p.replace(path_str)

            return {
                "product": "Bingo 18",
                "added_draws": added_count,
                "latest_id": latest_id,
                "total_draws": len(records),
                "message": f"Bingo 18: Đã đồng bộ thêm {added_count} kỳ mới (Kỳ mới nhất #{latest_id}). Dự đoán đã cập nhật!",
            }

        else:
            # Với các sản phẩm khác hoặc "all", chạy đồng bộ live data
            from vietlott.sync_live_data import main as sync_live
            sync_live(trigger_render=False)

            # Chạy render cập nhật
            from vietlott.render_web_data import main as render_main
            render_main()

            return {
                "product": product_key,
                "message": f"Đã cào dữ liệu và tính toán phân tích hoàn tất cho {product_key}!",
            }


def run_server(port: int = 8088):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, LocalVietlottHandler)
    print(f"============================================================")
    print(f"  VIETLOTT LOCAL WEB & ANALYTICS API SERVER ĐANG CHẠY")
    print(f"  URL giao diện Web : http://localhost:{port}")
    print(f"  API Cào Dữ Liệu   : POST http://localhost:{port}/api/crawl?product=bingo18")
    print(f"  API Trạng Thái    : GET http://localhost:{port}/api/status")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang dừng máy chủ...")
        httpd.shutdown()


if __name__ == "__main__":
    port = 8088
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
