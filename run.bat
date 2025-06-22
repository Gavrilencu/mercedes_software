@echo off
echo ========================================
echo OBD2 Diagnostic Tool - Mercedes Software
echo ========================================
echo.
echo Pornesc aplicația OBD2 Diagnostic...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo EROARE: Python nu este instalat!
    echo Te rog instalează Python 3.8+ de la https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import customtkinter, serial, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo EROARE: Dependențele nu sunt instalate!
    echo Rulează install.bat pentru a instala dependențele.
    pause
    exit /b 1
)

REM Run the application
python obd2_diagnostic.py

if errorlevel 1 (
    echo.
    echo EROARE: Aplicația s-a închis cu o eroare!
    echo Verifică că adaptorul OBD2 este conectat corect.
    pause
) 