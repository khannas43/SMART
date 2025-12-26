# SMART Platform - Setup Summary

**Date:** Setup completed

## ✅ Completed Tasks

### 1. Maven Installation ✅
**Status:** Successfully Installed
- **Version:** Apache Maven 3.9.9
- **Location:** `C:\Users\admin\Apache\maven`
- **Verification:**
  ```powershell
  $env:Path += ";C:\Users\admin\Apache\maven\bin"
  mvn --version
  ```
- **Note:** Add to PATH permanently or restart terminal

### 2. MLflow Connection ✅
**Status:** Working
- **URI:** http://127.0.0.1:5000
- **Test Result:** ✅ Connection successful
- **Experiments:** Default experiment available
- **Test Run:** Created successfully

### 3. Git Repository Setup ⚠️
**Status:** Needs Manual Setup
- **Repository URL:** https://github.com/khannas43/SMART.git
- **Action Required:** Install Git first, then run setup

**Steps to complete:**
1. Install Git from: https://git-scm.com/download/win
2. After installation, run:
   ```powershell
   git init
   git remote add origin https://github.com/khannas43/SMART.git
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git push -u origin main
   ```

### 4. PostgreSQL Connection ⚠️
**Status:** Needs Configuration for WSL
- **Windows Connection:** ✅ Port 5432 accessible
- **WSL Connection:** ❌ Connection refused
- **Issue:** PostgreSQL not accessible from WSL

**Solutions:**
See `POSTGRESQL_WSL_SETUP.md` for detailed instructions.

**Quick Fix:**
1. Edit PostgreSQL config: `postgresql.conf`
   - Change `listen_addresses = 'localhost'` to `listen_addresses = '*'`
2. Restart PostgreSQL service
3. Test from WSL using Windows hostname:
   ```bash
   psql -h DESKTOP-BTUEFC0 -p 5432 -U sameer -d smart
   ```

## Current Environment Status

### ✅ Working
- Java JDK 21.0.9
- Node.js v24.12.0 & npm 11.6.2
- Docker & Docker Compose
- Python venv (WSL) with all packages
- MLflow UI (running and accessible)
- Maven 3.9.9 (installed, needs PATH update)

### ⚠️ Needs Attention
- Git (not installed - download and install manually)
- PostgreSQL WSL connectivity (needs configuration)
- Maven PATH (add to system PATH or restart terminal)

## Quick Verification Commands

### Test Maven
```powershell
$env:Path += ";C:\Users\admin\Apache\maven\bin"
mvn --version
```

### Test MLflow
```bash
cd /mnt/c/Projects/SMART
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test-mlflow-connection.py
```

### Test Database (from Windows)
```powershell
$env:PGPASSWORD="anjali143"
psql -h localhost -p 5432 -U sameer -d smart -c "SELECT version();"
```

### Test Database (from WSL - after config)
```bash
export PGPASSWORD="anjali143"
psql -h DESKTOP-BTUEFC0 -p 5432 -U sameer -d smart -c "SELECT version();"
```

## Next Steps

1. **Install Git:**
   - Download from: https://git-scm.com/download/win
   - Run installer
   - Restart terminal
   - Run Git setup commands above

2. **Configure PostgreSQL for WSL:**
   - Follow instructions in `POSTGRESQL_WSL_SETUP.md`
   - Or install PostgreSQL in WSL as alternative

3. **Update PATH for Maven:**
   - Add `C:\Users\admin\Apache\maven\bin` to system PATH
   - Or restart terminal (user PATH should already include it)

4. **Run Full Environment Test:**
   ```powershell
   .\scripts\test-environment.ps1
   ```

## Configuration Files Created

All Spring Boot configuration templates have been created with correct database credentials:
- Portal configs: `portals/{portal}/config/`
- Service configs: `portals/{portal}/backend/services/{service}/src/main/resources/`

All configurations are ready to use once PostgreSQL WSL connectivity is fixed.

