# Golden Record Use Case - Setup Guide

## Virtual Environment Setup

The SMART AI/ML project uses a dedicated virtual environment. **Always activate it before working!**

### Activate Virtual Environment

```bash
# Navigate to ai-ml directory
cd /mnt/c/Projects/SMART/ai-ml

# Activate virtual environment
source .venv/bin/activate

# You should see (.venv) in your prompt
```

### Install Dependencies

```bash
# Make sure venv is activated (you should see (.venv) in prompt)
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check if packages are installed
pip list | grep -E "pandas|numpy|mlflow|xgboost|scikit-learn"

# Should show installed versions
```

## Running Notebooks

### Install Jupyter (First Time Only)

```bash
# From ai-ml directory with venv activated
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
pip install jupyter jupyterlab ipykernel
```

### Start Jupyter

```bash
# From ai-ml directory with venv activated
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate

# Option 1: Jupyter Notebook
jupyter notebook

# Option 2: JupyterLab (recommended)
jupyter lab
```

**Note:** If `jupyter notebook` command not found, use `jupyter-lab` or install it:
```bash
pip install jupyter jupyterlab ipykernel
```

### Open Data Exploration Notebook

Navigate to: `use-cases/01_golden_record/notebooks/01_data_exploration.ipynb`

## Running Training Script

```bash
# Make sure venv is activated
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate

# Run training
cd use-cases/golden_record
python src/train.py
```

## Troubleshooting

### If packages fail to install

1. **Make sure venv is activated** - you should see `(.venv)` in your prompt
2. **Upgrade pip first:**
   ```bash
   pip install --upgrade pip
   ```
3. **Install packages individually** if needed:
   ```bash
   pip install pandas numpy scikit-learn xgboost mlflow psycopg2-binary pyyaml
   ```

### Optional Packages (for better performance)

These have fallback implementations, but install for better performance:

```bash
pip install rapidfuzz phonetics geopy
```

### Database Connection

Make sure PostgreSQL is accessible:
- Host: `172.17.16.1`
- Port: `5432`
- Database: `smart_warehouse`
- User: `sameer`

Test connection:
```bash
python -c "from shared.utils.db_connector import DBConnector; db = DBConnector(database='smart_warehouse'); db.connect(); print('✅ Connected')"
```

## Quick Start

```bash
# 1. Activate venv
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate

# 2. Install dependencies (first time only)
cd use-cases/golden_record
pip install -r requirements.txt

# 3. Start Jupyter
cd ../..
jupyter notebook

# 4. Open notebook: use-cases/golden_record/notebooks/01_data_exploration.ipynb
```

