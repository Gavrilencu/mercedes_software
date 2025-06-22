@echo off
echo ========================================
echo    OBD2 Diagnostic Tool - Advanced
echo    Instalare Dependente Avansate
echo ========================================
echo.

echo Actualizare setuptools...
python -m pip install --upgrade setuptools wheel

echo.
echo Instalare dependente avansate...
pip install -r requirements_advanced.txt

echo.
echo Verificare instalare...
python -c "import customtkinter; import matplotlib; import numpy; import pandas; import jinja2; print('✅ Toate dependentele avansate au fost instalate cu succes!')"

echo.
echo ========================================
echo    Instalare completata!
echo ========================================
echo.
echo Pentru a porni aplicatia avansata:
echo   run_advanced.bat
echo.
echo Pentru a porni aplicatia moderna:
echo   run_modern.bat
echo.
echo Pentru a porni aplicatia clasica:
echo   run.bat
echo.

pause 