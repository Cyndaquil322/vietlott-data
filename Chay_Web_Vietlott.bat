@echo off
chcp 65001 > nul
title VIETLOTT ANALYTICS & LIVE EXPLORER LOCAL SERVER
echo ============================================================
echo   ĐANG KHỞI ĐỘNG MÁY CHỦ VIETLOTT LOCAL & ANALYTICS API...
echo   Địa chỉ truy cập: http://localhost:8088
echo ============================================================
cd /d "%~dp0"
set PYTHONPATH=src
set PYTHONIOENCODING=utf-8

:: Tự động mở trình duyệt sau 1 giây
start "" "http://localhost:8088"

:: Chạy máy chủ API & Web
python src/vietlott/local_server.py 8088

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [LỖI] Máy chủ bị ngắt. Nhấn phím bất kỳ để thoát.
    pause > nul
)
