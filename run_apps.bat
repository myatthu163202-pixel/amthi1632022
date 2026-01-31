@echo off
echo Starting 2D System Applications...
echo.

echo 1. Starting Admin Panel on port 8501...
start cmd /k "streamlit run admin_panel.py --server.port 8501"

timeout /t 3 /nobreak >nul

echo 2. Starting 2D App on port 8502...
start cmd /k "streamlit run 2d_app.py --server.port 8502"

echo.
echo Applications started successfully!
echo.
echo Admin Panel: http://localhost:8501
echo 2D App: http://localhost:8502
echo.
pause
