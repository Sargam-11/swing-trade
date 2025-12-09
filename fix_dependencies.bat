@echo off
echo ============================================
echo   Fixing numpy/pandas compatibility issue
echo ============================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Uninstalling numpy and pandas...
pip uninstall -y numpy pandas

echo.
echo Installing numpy first...
pip install numpy==1.26.4

echo.
echo Installing pandas...
pip install pandas==2.1.3

echo.
echo Reinstalling all requirements...
pip install -r requirements.txt

echo.
echo ============================================
echo   Fix complete! Try running the app now.
echo ============================================
echo.
pause
