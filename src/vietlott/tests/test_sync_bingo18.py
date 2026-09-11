import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from vietlott.sync_bingo18 import (
    parse_bingo18_html,
    load_existing_bingo18,
    save_bingo18_data,
    sync_bingo18,
    get_robust_session,
    URL_BINGO18,
)

SAMPLE_BINGO18_HTML = """
<table class="table">
    <thead>
        <tr>
            <th>Kỳ quay / Ngày</th>
            <th>Kết quả</th>
            <th>Tổng</th>
            <th>Lớn / Nhỏ</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <a href="/vi/trung-thuong/ket-qua-trung-thuong/bingo18?id=0185891">10/09/2026</a>
                <a href="/vi/trung-thuong/ket-qua-trung-thuong/bingo18?id=0185891">#0185891</a>
            </td>
            <td>
                <span class="dice">1</span>
                <span class="dice">4</span>
                <span class="dice">5</span>
            </td>
            <td>10</td>
            <td>Hòa</td>
        </tr>
        <tr>
            <td>
                <a href="/vi/trung-thuong/ket-qua-trung-thuong/bingo18?id=0185878">10/09/2026</a>
                <a href="/vi/trung-thuong/ket-qua-trung-thuong/bingo18?id=0185878">#0185878</a>
            </td>
            <td>
                <span class="dice">3</span>
                <span class="dice">3</span>
                <span class="dice">3</span>
            </td>
            <td>9</td>
            <td>Nhỏ</td>
        </tr>
        <tr>
            <td>
                <a href="/vi/trung-thuong/ket-qua-trung-thuong/bingo18?id=0185875">10/09/2026</a>
                <a href="/vi/trung-thuong/ket-qua-trung-thuong/bingo18?id=0185875">#0185875</a>
            </td>
            <td>
                <span class="dice">6</span>
                <span class="dice">6</span>
                <span class="dice">6</span>
            </td>
            <td>18</td>
            <td>Lớn</td>
        </tr>
    </tbody>
</table>
"""


def test_parse_bingo18_html_standard_and_triple():
    """Kiểm tra parse_bingo18_html bóc tách chính xác chuẩn cả bão và thường."""
    records = parse_bingo18_html(SAMPLE_BINGO18_HTML)
    assert len(records) == 3

    # Row 1: normal [1, 4, 5]
    r1 = records[0]
    assert r1["date"] == "2026-09-10"
    assert r1["id"] == "0185891"
    assert r1["result"] == [1, 4, 5]
    assert r1["total"] == 10
    assert r1["large_small"] == "Hòa"
    assert r1["is_triple"] is False

    # Row 2: triple [3, 3, 3]
    r2 = records[1]
    assert r2["date"] == "2026-09-10"
    assert r2["id"] == "0185878"
    assert r2["result"] == [3, 3, 3]
    assert r2["total"] == 9
    assert r2["large_small"] == "Nhỏ"
    assert r2["is_triple"] is True

    # Row 3: triple [6, 6, 6]
    r3 = records[2]
    assert r3["date"] == "2026-09-10"
    assert r3["id"] == "0185875"
    assert r3["result"] == [6, 6, 6]
    assert r3["total"] == 18
    assert r3["large_small"] == "Lớn"
    assert r3["is_triple"] is True


def test_parse_bingo18_html_malformed_and_empty():
    """Kiểm tra xử lý các dòng trống, lỗi format hoặc thiếu dữ liệu."""
    empty_res = parse_bingo18_html("")
    assert empty_res == []

    malformed_html = """
    <table>
        <tr><th>Header</th></tr>
        <tr><td>Only one td</td></tr>
        <tr>
            <td><a href="#">invalid-date</a><a href="#">#123</a></td>
            <td><span>1</span><span>2</span><span>3</span></td>
            <td>6</td>
            <td>Nhỏ</td>
        </tr>
        <tr>
            <td><a href="#">10/09/2026</a><a href="#">#0185800</a></td>
            <td><span>99</span></td> <!-- Invalid numbers length -->
            <td>99</td>
            <td>Lớn</td>
        </tr>
    </table>
    """
    records = parse_bingo18_html(malformed_html)
    assert len(records) == 0


def test_is_triple_flag_and_rules():
    """Kiểm tra cờ is_triple và logic tổng/lớn nhỏ."""
    html = """
    <table>
        <tr>
            <td><a>01/01/2026</a><a>#0100001</a></td>
            <td><span>1</span><span>1</span><span>1</span></td>
            <td>3</td>
            <td>Nhỏ</td>
        </tr>
        <tr>
            <td><a>01/01/2026</a><a>#0100002</a></td>
            <td><span>2</span><span>2</span><span>3</span></td>
            <td>7</td>
            <td>Nhỏ</td>
        </tr>
    </table>
    """
    records = parse_bingo18_html(html)
    assert len(records) == 2
    assert records[0]["is_triple"] is True
    assert records[0]["result"] == [1, 1, 1]
    assert records[1]["is_triple"] is False
    assert records[1]["result"] == [2, 2, 3]


def test_load_and_save_bingo18_data_atomic(tmp_path: Path):
    """Kiểm tra load_existing_bingo18 và save_bingo18_data ghi file nguyên tử."""
    target_file = tmp_path / "bingo18.jsonl"
    
    # Load from non-existent file
    initial = load_existing_bingo18(target_file)
    assert initial == {}

    data_to_save = {
        "185871": {
            "date": "2026-09-10",
            "id": "0185871",
            "result": [1, 4, 5],
            "total": 10,
            "large_small": "Hòa",
            "is_triple": False,
        },
        "185872": {
            "date": "2026-09-10",
            "id": "0185872",
            "result": [3, 3, 3],
            "total": 9,
            "large_small": "Nhỏ",
            "is_triple": True,
        },
        "83123": {
            "date": "2024-12-03",
            "id": "0083123",
            "result": [2, 6, 1],
            "total": 9,
            "large_small": "Nhỏ",
            "is_triple": False,
        },
    }

    save_bingo18_data(target_file, data_to_save)
    assert target_file.exists()
    assert not target_file.with_suffix(".tmp").exists()

    # Verify loaded back
    loaded = load_existing_bingo18(target_file)
    assert len(loaded) == 3
    assert "185871" in loaded
    assert loaded["185872"]["is_triple"] is True

    # Verify sort order: date ascending, id ascending
    lines = [json.loads(line) for line in target_file.read_text(encoding="utf-8").splitlines() if line]
    assert lines[0]["id"] == "0083123"
    assert lines[1]["id"] == "0185871"
    assert lines[2]["id"] == "0185872"


def test_sync_bingo18_early_stopping(tmp_path: Path):
    """Kiểm tra cơ chế dừng sớm khi gặp draw_id đã tồn tại trong local database."""
    target_file = tmp_path / "bingo18.jsonl"
    existing_data = {
        "185870": {
            "date": "2026-09-10",
            "id": "0185870",
            "result": [2, 4, 4],
            "total": 10,
            "large_small": "Hòa",
            "is_triple": False,
        }
    }
    save_bingo18_data(target_file, existing_data)

    # Page 1 has 2 draws: 0185872, 0185871 (both > 185870)
    page1_html = """
    <table>
        <tr><th>H</th></tr>
        <tr>
            <td><a>10/09/2026</a><a>#0185872</a></td>
            <td><span>3</span><span>3</span><span>3</span></td>
            <td>9</td><td>Nhỏ</td>
        </tr>
        <tr>
            <td><a>10/09/2026</a><a>#0185871</a></td>
            <td><span>1</span><span>4</span><span>5</span></td>
            <td>10</td><td>Hòa</td>
        </tr>
    </table>
    """
    # Page 2 has 0185870 (already exists <= 185870) -> Should stop immediately
    page2_html = """
    <table>
        <tr><th>H</th></tr>
        <tr>
            <td><a>10/09/2026</a><a>#0185870</a></td>
            <td><span>2</span><span>4</span><span>4</span></td>
            <td>10</td><td>Hòa</td>
        </tr>
        <tr>
            <td><a>10/09/2026</a><a>#0185869</a></td>
            <td><span>1</span><span>1</span><span>1</span></td>
            <td>3</td><td>Nhỏ</td>
        </tr>
    </table>
    """

    mock_session = MagicMock()
    
    def fake_post(url, *args, **kwargs):
        json_data = kwargs.get("json", {})
        page_idx = json_data.get("PageIndex", 1)
        mock_resp = MagicMock()
        mock_resp.ok = True
        if page_idx == 1:
            mock_resp.json.return_value = {"value": {"HtmlContent": page1_html}}
        elif page_idx == 2:
            mock_resp.json.return_value = {"value": {"HtmlContent": page2_html}}
        else:
            mock_resp.json.return_value = {"value": {"HtmlContent": ""}}
        return mock_resp

    mock_session.post.side_effect = fake_post

    with patch("vietlott.sync_bingo18.get_robust_session", return_value=mock_session):
        new_draws = sync_bingo18(file_path=target_file, max_pages=5)

    assert new_draws == 2
    # Page 1 made request, page 2 encountered 185870 and stopped. Page 3 should NOT be requested.
    assert mock_session.post.call_count == 2

    # Check updated database
    loaded = load_existing_bingo18(target_file)
    assert len(loaded) == 3
    assert "185871" in loaded
    assert "185872" in loaded
    assert "185869" not in loaded


def test_get_robust_session_configuration():
    """Kiểm tra session HTTP được cấu hình retry đầy đủ."""
    session = get_robust_session()
    adapter = session.adapters.get("https://")
    assert adapter is not None
    assert adapter.max_retries.total == 3
    assert 500 in adapter.max_retries.status_forcelist
