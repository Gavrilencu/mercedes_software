@echo off
echo ========================================
echo OBD2 Diagnostic Tool - Mercedes Software
echo ========================================
echo.
echo Instalare aplicație OBD2 Diagnostic...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo EROARE: Python nu este instalat!
    echo Te rog instalează Python 3.8+ de la https://python.org
    pause
    exit /b 1
)

echo Python detectat. Instalez dependențele...
echo.

REM Install requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo EROARE: Nu s-au putut instala dependențele!
    echo Verifică că ai conexiune la internet și încearcă din nou.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalare completă cu succes!
echo ========================================
echo.
echo Pentru a rula aplicația:
echo 1. Conectează adaptorul OBD2 USB
echo 2. Conectează-l la mașină
echo 3. Rulează: python obd2_diagnostic.py
echo.
echo Sau dublu-click pe run.bat
echo.
pause 