@echo off
title EchoBridge
cd /d "%~dp0"
echo ========================================================
echo         EchoBridge - Baslatiliyor
echo ========================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Uygulama baslatilamadi! Python yuklu oldugundan
    echo ve gereksinimlerin kurulu oldugundan emin olun.
    echo Gereksinimleri yuklemek icin: pip install -r requirements.txt
    pause
)

