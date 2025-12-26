# SMART AI/ML Module

This directory contains the AI/ML use cases, models, and training pipelines for the SMART Platform.

## Environment Setup

### WSL2 Configuration

This project uses **WSL2 (Ubuntu 24.04)** on Windows 11.

**Paths:**
- Windows: `C:\Projects\SMART\ai-ml`
- WSL: `/mnt/c/Projects/SMART/ai-ml`

### Python Virtual Environment

**Location:** `.venv/` in this directory

**Python Interpreter:**
```
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python
```

**Activate the venv:**
```bash
source .venv/bin/activate
```

### Installed Packages

The virtual environment includes:

- **PyTorch (CPU builds):** `torch`, `torchvision`, `torchaudio`
- **Data Processing:** `pandas`, `numpy`, `scikit-learn`, `pyarrow`
- **MLOps:** `mlflow[extras]`
- **Development:** `jupyterlab`
- **Database:** `neo4j` Python driver

## Configuration

### MLflow Tracking

**MLflow URI:** `http://127.0.0.1:5000/`

**Start MLflow UI:**
```bash
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

**Access MLflow:**
- Browser: `http://localhost:5000`

### Database Connection

**PostgreSQL:**
- Host: `localhost`
- Port: `5432`
- Database: `smart`
- Username: `sameer`
- Password: `anjali143`

## Usage

### Running Scripts

```bash
# Activate venv
source .venv/bin/activate

# Run a script
python scripts/hello_mlflow.py

# Or use full path (no activation needed)
.venv/bin/python scripts/hello_mlflow.py
```

### Jupyter Lab

```bash
source .venv/bin/activate
jupyter lab
```

### Installing Additional Packages

```bash
source .venv/bin/activate
pip install <package-name>
```

## Project Structure

```
ai-ml/
├── data/              # Data files
├── models/            # Trained model files
├── notebooks/         # Jupyter notebooks
├── pipelines/         # ML pipelines
├── scripts/           # Python scripts
├── training/          # Training scripts
├── use-cases/         # 27 AI/ML use cases
└── .venv/             # Python virtual environment
```

## Important Notes

- **Always use WSL Python**, not Windows global Python
- Use the venv interpreter: `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`
- Cursor IDE should be configured to use this interpreter automatically
- MLflow UI must be running before training scripts

## Cursor IDE Setup

The `.vscode/settings.json` file configures Cursor to:
- Use the WSL Python interpreter automatically
- Activate the venv in terminals
- Set up Jupyter kernels correctly

See [Development Configuration](../../app%20documentation/DEVELOPMENT_CONFIG.md) for detailed setup instructions.

