#!/bin/bash
echo "Starting 2D System Applications..."
echo ""

echo "1. Starting Admin Panel on port 8501..."
streamlit run admin_panel.py --server.port 8501 &
sleep 3

echo "2. Starting 2D App on port 8502..."
streamlit run 2d_app.py --server.port 8502 &

echo ""
echo "Applications started successfully!"
echo ""
echo "Admin Panel: http://localhost:8501"
echo "2D App: http://localhost:8502"
echo ""
echo "Press Ctrl+C to stop all applications"
wait
