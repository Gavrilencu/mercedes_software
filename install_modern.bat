@echo off
echo ========================================
echo    OBD2 Diagnostic Tool - Modern UI
echo    Instalare Dependente
echo ========================================
echo.

echo Actualizare setuptools...
python -m pip install --upgrade setuptools wheel

echo.
echo Instalare dependente moderne...
pip install -r requirements.txt

echo.
echo Verificare instalare...
python -c "import customtkinter; import matplotlib; import PIL; print('✅ Toate dependentele au fost instalate cu succes!')"

echo.
echo ========================================
echo    Instalare completata!
echo ========================================
echo.
echo Pentru a porni aplicatia moderna:
echo   run_modern.bat
echo.
echo Pentru a porni aplicatia clasica:
echo   run.bat
echo.

pause 