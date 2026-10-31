@echo off
title EchoBridge - EXE Derleyici
cd /d "%~dp0"
echo ========================================================
echo       EchoBridge - EXE Derleniyor
echo ========================================================
echo.
echo Gerekli kutuphaneler kontrol ediliyor...
pip install -r requirements.txt

echo.
echo PyInstaller ile hafif ve bagimsiz calistirilabilir dosya olusturuluyor...
pyinstaller --noconfirm --onedir --windowed ^
    --name "EchoBridge" ^
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
echo Derleme tamamlandi! Cikti: dist\EchoBridge\
echo ========================================================
pause

