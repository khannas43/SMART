#!/bin/bash
# Quick script to open the data exploration notebook in JupyterLab

cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate

echo "Opening JupyterLab..."
echo "Navigate to: use-cases/01_golden_record/notebooks/01_data_exploration.ipynb"
echo ""

jupyter lab use-cases/01_golden_record/notebooks/01_data_exploration.ipynb

