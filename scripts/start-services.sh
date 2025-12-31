#!/bin/bash
# Start SMART Platform Services (WSL/Linux)
# Run this after computer restart

set -e

echo "============================================================"
echo "Starting SMART Platform Services"
echo "============================================================"
echo ""

# Activate venv
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate

# 1. Check PostgreSQL
echo "1. Checking PostgreSQL connection..."
if PGPASSWORD='anjali143' psql -h 172.17.16.1 -p 5432 -U sameer -d smart -c '\q' 2>/dev/null; then
    echo "   ✅ PostgreSQL is accessible"
else
    echo "   ⚠️  PostgreSQL connection failed!"
    echo "   Make sure PostgreSQL is running on Windows"
    exit 1
fi
echo ""

# 2. Start MLflow UI (background)
echo "2. Starting MLflow UI..."
if pgrep -f "mlflow ui" > /dev/null; then
    echo "   ⚠️  MLflow UI is already running"
else
    cd /mnt/c/Projects/SMART/ai-ml
    nohup mlflow ui --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &
    MLFLOW_PID=$!
    echo "   ✅ MLflow UI starting (PID: $MLFLOW_PID)"
    echo "   Access at: http://127.0.0.1:5000"
    echo "   Logs: tail -f /mnt/c/Projects/SMART/ai-ml/mlflow.log"
    sleep 3
fi
echo ""

# 3. Optional: JupyterLab
echo "3. JupyterLab (optional)..."
echo "   To start JupyterLab, run:"
echo "   cd /mnt/c/Projects/SMART/ai-ml"
echo "   source .venv/bin/activate"
echo "   jupyter lab --no-browser"
echo ""

# Summary
echo "============================================================"
echo "Services Status:"
echo "  ✅ PostgreSQL: Connected"
echo "  ✅ MLflow UI: Running (http://127.0.0.1:5000)"
echo "  ⚪ JupyterLab: Manual start required"
echo "============================================================"
echo ""
echo "To stop MLflow: pkill -f 'mlflow ui'"

