@echo off
echo ============================================
echo   Starting Swing Trade Analyzer Dashboard
echo ============================================
echo.

REM Use venv Python directly to avoid PATH issues
echo Starting dashboard at http://localhost:8501
echo Press Ctrl+C to stop
echo.
venv\Scripts\python.exe -m streamlit run app.py

pause
