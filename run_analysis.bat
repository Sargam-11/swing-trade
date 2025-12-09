@echo off
echo ============================================
echo   Running Daily Stock Analysis
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run analysis
python scheduler.py now

echo.
echo Analysis complete! Check the dashboard to view results.
pause
