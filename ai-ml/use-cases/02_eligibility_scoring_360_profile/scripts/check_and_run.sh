#!/bin/bash
# Check configuration and validate data with venv activation

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Go up: scripts -> eligibility_scoring_360_profile -> use-cases -> ai-ml
AI_ML_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VENV_PATH="$AI_ML_ROOT/.venv"

# Activate virtual environment
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "✅ Virtual environment activated from $VENV_PATH"
else
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Please create venv first: cd $AI_ML_ROOT && python -m venv .venv"
    echo "   Or activate manually: source $AI_ML_ROOT/.venv/bin/activate"
    exit 1
fi

# Run checks
echo ""
echo "Running configuration check..."
cd "$SCRIPT_DIR/.."
python scripts/check_config.py

echo ""
echo "Running data validation..."
python scripts/validate_data.py

