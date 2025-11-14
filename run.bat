@echo off
chcp 65001 > nul
echo ========================================
echo TechScout - LM Studio Edition
echo 東洋電機製造株式会社
echo 開発センター基盤技術部
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set encoding
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

REM Run app
echo [INFO] Starting application...
echo [INFO] URL: http://localhost:7861
echo [INFO] Login: admin / password123
echo.
python app_lmstudio.py

pause

