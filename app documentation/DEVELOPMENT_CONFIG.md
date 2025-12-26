# SMART Platform - Development Configuration

This document contains the development environment configuration details for the SMART Platform.

## Database Configuration

### PostgreSQL Connection Details

**Host:** `localhost`  
**Port:** `5432`  
**Database:** `smart`  
**Username:** `sameer`  
**Password:** `anjali143`

### Connection String Format

**JDBC URL (for Spring Boot):**
```
jdbc:postgresql://localhost:5432/smart
```

**Connection String (for general use):**
```
postgresql://sameer:anjali143@localhost:5432/smart
```

**Spring Boot application.yml example:**
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/smart
    username: sameer
    password: anjali143
    driver-class-name: org.postgresql.Driver
```

### Database Setup

The main database is `smart`. Individual portals may use separate schemas or databases:
- **Citizen Portal**: Schema or database `smart_citizen`
- **Dept Portal**: Schema or database `smart_dept`
- **AIML Portal**: Schema or database `smart_aiml`
- **Monitor Portal**: Schema or database `smart_monitor`

---

## MLflow Configuration

### MLflow Tracking Server

**URI:** `http://127.0.0.1:5000/`

**Python Configuration:**
```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("smart-hello")
```

**Start MLflow UI:**
```bash
# From WSL terminal in ai-ml directory
mlflow ui --host 0.0.0.0 --port 5000
```

**Access MLflow UI:**
- From Windows: `http://localhost:5000`
- From WSL: `http://127.0.0.1:5000`

---

## AI/ML Environment Configuration

### WSL2 Setup

**Operating System:** Windows 11 with WSL2 (Ubuntu 24.04)

**Project Paths:**
- **Windows:** `C:\Projects\SMART\ai-ml`
- **WSL:** `/mnt/c/Projects/SMART/ai-ml`

### Python Virtual Environment

**Virtual Environment Location:**
```
/mnt/c/Projects/SMART/ai-ml/.venv
```

**Python Interpreter:**
```
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python
```

**Pip Executable:**
```
/mnt/c/Projects/SMART/ai-ml/.venv/bin/pip
```

### Installed Packages (in venv)

The following packages are already installed in the virtual environment:

- **PyTorch (CPU builds):**
  - `torch`
  - `torchvision`
  - `torchaudio`

- **Data Processing:**
  - `pandas`
  - `numpy`
  - `scikit-learn`
  - `pyarrow`

- **MLOps:**
  - `mlflow[extras]` (MLflow UI at `http://127.0.0.1:5000`)

- **Development:**
  - `jupyterlab`

- **Database:**
  - `neo4j` Python driver

### Using the Virtual Environment

**Activate the venv (from WSL terminal):**
```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
```

**Run Python scripts:**
```bash
# Activate venv first
source .venv/bin/activate

# Then run Python
python script.py

# Or use full path
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python script.py
```

**Install additional packages:**
```bash
source .venv/bin/activate
pip install <package-name>
```

---

## Cursor IDE Configuration

### Python Interpreter Setup

When working with Python files or Jupyter notebooks in Cursor:

1. **Use the WSL Python interpreter:**
   - Path: `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`
   - Do NOT use the Windows global Python installation
   - All Python work should run via WSL and this venv

2. **Setting Python Interpreter in Cursor:**
   - Open a Python file
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose the interpreter at: `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`

### Workspace Configuration

**Open this folder in Cursor:**
- Windows: `C:\Projects\SMART\ai-ml`
- WSL path: `/mnt/c/Projects/SMART/ai-ml`

**Expected Behavior:**
- Cursor should automatically detect and use the WSL Python interpreter
- When creating Python files or notebooks, use the venv interpreter
- Do not attempt to use Windows global Python

---

## Environment Variables

### For Backend Services (Spring Boot)

Create `.env` file or set environment variables:

```bash
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart
DB_USERNAME=sameer
DB_PASSWORD=anjali143

# MLflow (for AIML service)
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```

### For Python/AI-ML Scripts

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export PYTHONPATH=/mnt/c/Projects/SMART/ai-ml:$PYTHONPATH
```

---

## Quick Reference Commands

### Database Connection (from WSL/Windows)

```bash
# Connect to PostgreSQL
psql -h localhost -p 5432 -U sameer -d smart

# From Windows PowerShell
psql -h localhost -p 5432 -U sameer -d smart

# Enter password when prompted: anjali143
```

### MLflow Commands

```bash
# Start MLflow UI (from WSL in ai-ml directory)
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000

# Or use full path
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python -m mlflow ui --host 0.0.0.0 --port 5000
```

### Python Script Execution

```bash
# Activate venv and run
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
python scripts/hello_mlflow.py

# Or use full path (no activation needed)
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python scripts/hello_mlflow.py
```

---

## Verification

### Test Database Connection

```bash
# Test connection
psql -h localhost -p 5432 -U sameer -d smart -c "SELECT version();"
```

### Test MLflow Connection

```python
# From Python (using venv)
import mlflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
print(mlflow.get_tracking_uri())
```

### Test Python Environment

```bash
# Check Python version
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python --version

# Check installed packages
/mnt/c/Projects/SMART/ai-ml/.venv/bin/pip list

# Test PyTorch
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python -c "import torch; print(torch.__version__)"

# Test MLflow
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python -c "import mlflow; print(mlflow.__version__)"
```

---

## Notes

- **WSL vs Windows:** Always use WSL Python for AI/ML work, not Windows global Python
- **Database:** PostgreSQL should be accessible from both Windows and WSL (localhost)
- **MLflow:** Make sure MLflow UI is running before running training scripts
- **Virtual Environment:** Always activate the venv or use full path when running Python scripts

