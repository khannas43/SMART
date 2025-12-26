# SMART Platform - Test Scripts

This directory contains test scripts to verify the SMART Platform development environment.

## Available Scripts

### 1. `test-database-connection.py`
Tests PostgreSQL database connection and displays database information.

**Usage:**
```bash
# From WSL (recommended)
cd /mnt/c/Projects/SMART
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python scripts/test-database-connection.py

# Or activate venv first
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test-database-connection.py
```

**Requirements:**
- Python with `psycopg2-binary` package
- PostgreSQL running on localhost:5432
- Database credentials configured

**Install psycopg2 if needed:**
```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
pip install psycopg2-binary
```

### 2. `test-mlflow-connection.py`
Tests MLflow tracking server connection and creates a test run.

**Usage:**
```bash
# From WSL (recommended)
cd /mnt/c/Projects/SMART
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python scripts/test-mlflow-connection.py

# Or activate venv first
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test-mlflow-connection.py
```

**Requirements:**
- Python with `mlflow` package (already installed in venv)
- MLflow UI running on http://127.0.0.1:5000

**Start MLflow UI:**
```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

### 3. `test-environment.ps1`
Comprehensive environment verification script for Windows PowerShell.

**Usage:**
```powershell
cd C:\Projects\SMART
.\scripts\test-environment.ps1
```

**Tests:**
- Java JDK and compiler
- Node.js and npm
- Maven
- Git
- Docker and Docker Compose
- PostgreSQL connection
- Python venv (via WSL)
- MLflow connection

### 4. `test-environment.sh`
Comprehensive environment verification script for WSL/Linux.

**Usage:**
```bash
cd /mnt/c/Projects/SMART
chmod +x scripts/test-environment.sh
./scripts/test-environment.sh
```

**Tests:**
- Java JDK and compiler
- Node.js and npm
- Maven
- Git
- Docker and Docker Compose
- PostgreSQL connection
- Python venv
- MLflow connection

## Running All Tests

### Windows PowerShell
```powershell
cd C:\Projects\SMART

# Run environment check
.\scripts\test-environment.ps1

# Run database test (via WSL)
wsl bash -c "cd /mnt/c/Projects/SMART && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/test-database-connection.py"

# Run MLflow test (via WSL)
wsl bash -c "cd /mnt/c/Projects/SMART && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/test-mlflow-connection.py"
```

### WSL/Linux
```bash
cd /mnt/c/Projects/SMART

# Run environment check
./scripts/test-environment.sh

# Activate venv
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Run database test
python scripts/test-database-connection.py

# Run MLflow test
python scripts/test-mlflow-connection.py
```

## Expected Results

All tests should pass if:
- ✅ All required software is installed (see INSTALLATION_STATUS.md)
- ✅ PostgreSQL is running and accessible
- ✅ MLflow UI is running (for MLflow test)
- ✅ Database credentials are correct
- ✅ Network connectivity is working

## Troubleshooting

### Database Connection Failed
1. Ensure PostgreSQL service is running
2. Check if port 5432 is accessible
3. Verify credentials in `app documentation/DEVELOPMENT_CONFIG.md`
4. Test connection manually:
   ```bash
   psql -h localhost -p 5432 -U sameer -d smart
   ```

### MLflow Connection Failed
1. Start MLflow UI:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml
   source .venv/bin/activate
   mlflow ui --host 0.0.0.0 --port 5000
   ```
2. Verify it's accessible: http://localhost:5000
3. Check firewall settings

### Python Module Not Found
1. Activate the venv:
   ```bash
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   ```
2. Install missing packages:
   ```bash
   pip install psycopg2-binary  # For database test
   pip install mlflow           # For MLflow test (should already be installed)
   ```

## Notes

- Database tests require `psycopg2-binary` (install if needed)
- MLflow tests require MLflow UI to be running
- Use WSL Python venv for Python scripts
- PowerShell script tests WSL Python via `wsl` command
- Bash script can run directly in WSL/Linux

