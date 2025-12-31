#!/bin/bash
# Setup Script for Eligibility Scoring & 360° Profiles
# Execute steps 1-4 of the setup process

set -e  # Exit on error

# Get script directory and ai-ml root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Go up: scripts -> eligibility_scoring_360_profile -> use-cases -> ai-ml
AI_ML_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VENV_PATH="$AI_ML_ROOT/.venv"

echo "=========================================="
echo "Eligibility Scoring & 360° Profiles Setup"
echo "=========================================="

# Activate virtual environment
if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment from $VENV_PATH..."
    source "$VENV_PATH/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Warning: Virtual environment not found at $VENV_PATH"
    echo "   Please ensure venv is created: cd $AI_ML_ROOT && python -m venv .venv"
    echo "   Or activate manually: source $VENV_PATH/bin/activate"
fi

# Step 1: Create Database Schema
echo ""
echo "Step 1: Creating database schema..."
cd "$SCRIPT_DIR/../database"
export PGPASSWORD='anjali143'
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f smart_warehouse.sql
echo "✅ Database schema created"

# Step 2: Generate Synthetic Data (45K records)
echo ""
echo "Step 2: Generating synthetic data (45K records)..."
cd "$SCRIPT_DIR/../data"
python generate_synthetic.py
echo "✅ Synthetic data generated"

# Step 3: Train Income Band Model
echo ""
echo "Step 3: Training income band model..."
cd "$SCRIPT_DIR/../src"
python income_band_train.py
echo "✅ Income band model trained"

# Step 4: Run Graph Clustering (Neo4j)
echo ""
echo "Step 4: Running graph clustering (Neo4j)..."
# Check if Neo4j is enabled
python -c "
import yaml
from pathlib import Path
config = yaml.safe_load(open(Path('$SCRIPT_DIR/../config/db_config.yaml')))
if config.get('neo4j', {}).get('enabled', False):
    print('Using Neo4j for graph clustering')
    exit(0)
else:
    print('Neo4j not enabled, using NetworkX fallback')
    exit(1)
" && python graph_clustering_neo4j.py || python graph_clustering.py
echo "✅ Graph clustering completed"

echo ""
echo "=========================================="
echo "✅ Setup Steps 1-4 Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  - Run anomaly detection: cd src && python anomaly_detection.py"
echo "  - Train eligibility scoring: python eligibility_scoring_train.py"
echo "  - Run notebooks: cd ../notebooks && jupyter lab"

