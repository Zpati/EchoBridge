@echo off
title VRChat AI Translator Pro - EXE Derleyici
cd /d "%~dp0"
echo ========================================================
echo       VRChat AI Translator Pro - EXE Derleniyor
echo ========================================================
echo.
echo Gerekli kutuphaneler kontrol ediliyor...
pip install -r requirements.txt

echo.
echo PyInstaller ile hafif ve bagimsiz calistirilabilir dosya olusturuluyor...
pyinstaller --noconfirm --onedir --windowed ^
    --name "VRChat_AI_Translator_Pro" ^
    --icon "assets\icon.ico" ^
    --add-data "src;src" ^
    --add-data "assets;assets" ^
    --collect-all "customtkinter" ^
    --collect-all "deep_translator" ^
    --collect-all "speech_recognition" ^
    --exclude-module "torch" ^
    --exclude-module "tensorflow" ^
    --exclude-module "scipy" ^
    --exclude-module "matplotlib" ^
    main.py

echo.
echo ========================================================
echo Derleme tamamlandi! Cikti: dist\VRChat_AI_Translator_Pro\
echo ========================================================
pause
