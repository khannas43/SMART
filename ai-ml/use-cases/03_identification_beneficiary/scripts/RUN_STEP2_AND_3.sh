#!/bin/bash
# Step 2 & 3: Update Python Code and Test
# Run this script to verify Python code updates

set -e

echo "============================================================"
echo "Step 2 & 3: Python Code Updates and Testing"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
VENV_PATH="/mnt/c/Projects/SMART/ai-ml/.venv"
if [ -d "$VENV_PATH" ]; then
    echo "✅ Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR"

echo ""
echo "============================================================"
echo "Step 3: Running Tests"
echo "============================================================"
echo ""

# Run test script
python scripts/STEP3_TEST_UPDATES.py

TEST_EXIT_CODE=$?

echo ""
echo "============================================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "   Python code is ready to use with consolidated scheme_master"
else
    echo "❌ Some tests failed"
    echo "   Review the output above for details"
fi
echo "============================================================"

exit $TEST_EXIT_CODE

