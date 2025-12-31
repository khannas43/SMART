#!/bin/bash
# Quick start script for AI-PLATFORM-10 Forecast Viewer
# Run this script to start the enhanced viewer

cd "$(dirname "$0")"
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

echo "================================================================================"
echo "Enhanced Benefit Forecast Viewer - AI-PLATFORM-10"
echo "================================================================================"
echo ""
echo "Starting web server..."
echo "📊 View forecasts at: http://localhost:5001/ai10"
echo ""
echo "✨ New Features Available:"
echo "   - ML Probability Estimation"
echo "   - Aggregate Forecasting"
echo "   - Event-Driven Refresh"
echo "   - Time-Series Models"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python scripts/view_forecast_web.py

