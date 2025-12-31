# Restart Services After Computer Restart

After restarting your computer, you need to restart these services:

## Required Services

### 1. PostgreSQL ✅ (Already Restarted)
PostgreSQL should be running as a Windows service.

**Verify:**
```powershell
Get-Service -Name "*postgresql*"
```

Or check connection:
```bash
# From WSL
PGPASSWORD='anjali143' psql -h 172.17.16.1 -p 5432 -U sameer -d smart -c '\q'
```

### 2. MLflow UI (Required for ML tracking)

**Option A: Using PowerShell Script (Windows)**
```powershell
cd C:\Projects\SMART
.\scripts\start-services.ps1
```

**Option B: Manual Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

**Option C: Background Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
nohup mlflow ui --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &
```

Access: http://127.0.0.1:5000

### 3. JupyterLab (Optional - for notebooks)

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
jupyter lab --no-browser
```

### 4. Web Viewers (Multi-Use Case Interface)

Web interface for viewing:
- Eligibility Rules (AI-PLATFORM-03)
- Campaign Results (AI-PLATFORM-04)
- Application Submission (AI-PLATFORM-05)
- Decision Evaluation (AI-PLATFORM-06)

**Option A: Foreground Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/view_rules_web.py
```

**Option B: Background Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
nohup python scripts/view_rules_web.py > viewer.log 2>&1 &
```

**Access URLs:**
- Eligibility Rules Viewer: http://localhost:5001/
- Campaign Results Viewer: http://localhost:5001/ai04
- Application Submission Viewer: http://localhost:5001/ai05
- Decision Evaluation Viewer: http://localhost:5001/ai06
- Beneficiary Detection Viewer: http://localhost:5001/ai07
- Eligibility Checker Viewer: http://localhost:5001/ai08
- Proactive Inclusion Viewer: http://localhost:5001/ai09
- Benefit Forecast Viewer: http://localhost:5001/ai10
- Nudge Management Viewer: http://localhost:5001/ai11

## Quick Commands

### Windows PowerShell
```powershell
# Start all services
.\scripts\start-services.ps1

# Or manually start MLflow in WSL (run from PowerShell, not from within WSL)
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml && source .venv/bin/activate && mlflow ui --host 0.0.0.0 --port 5000"
```

**Note:** The `wsl` command only works from Windows PowerShell, not from within WSL itself. If you're already in WSL, just use the WSL/Linux commands below.

### WSL/Linux
```bash
# Quick start script
bash /mnt/c/Projects/SMART/scripts/start-services.sh

# Or manually:
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000 &
```

## Verify Services

### Check PostgreSQL
```bash
PGPASSWORD='anjali143' psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "SELECT 1;"
```

### Check MLflow
Open browser: http://127.0.0.1:5000

Or check if process is running:
```bash
# WSL
pgrep -f "mlflow ui"

# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*mlflow*"}
```

### Check Eligibility Rules Viewer
Open browser: http://localhost:5001/ or http://localhost:5001/ai04 or http://localhost:5001/ai05 or http://localhost:5001/ai06 or http://localhost:5001/ai07 or http://localhost:5001/ai08 or http://localhost:5001/ai09 or http://localhost:5001/ai10 or http://localhost:5001/ai11

Or check if process is running:
```bash
# WSL
pgrep -f "view_rules_web.py"
```

## Stop Services

### Stop MLflow
```bash
# WSL
pkill -f "mlflow ui"

# Or if started in PowerShell job
Get-Job | Stop-Job | Remove-Job
```

### Stop Eligibility Rules Viewer
```bash
# WSL
pkill -f "view_rules_web.py"
```

## Restart Services

### Restart MLflow (if already running)
If you get "Address already in use" error, stop MLflow first, then start it again:

```bash
# From WSL
# 1. Stop existing MLflow
pkill -f "mlflow ui"

# 2. Wait a moment
sleep 2

# 3. Start MLflow again
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
nohup mlflow ui --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &

# 4. Verify it's running
pgrep -f "mlflow ui" && echo "✅ MLflow is running" || echo "❌ MLflow failed to start"
```

### Quick Restart Script
```bash
# From WSL
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
pkill -f "mlflow ui" 2>/dev/null; sleep 2; nohup mlflow ui --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 & echo "✅ MLflow restarted"
```

### Restart Eligibility Rules Viewer (if already running)
```bash
# From WSL
# 1. Stop existing viewer
pkill -f "view_rules_web.py"

# 2. Wait a moment
sleep 2

# 3. Start viewer again
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
nohup python scripts/view_rules_web.py > viewer.log 2>&1 &

# 4. Verify it's running
pgrep -f "view_rules_web.py" && echo "✅ Viewer is running" || echo "❌ Viewer failed to start"
```

### Quick Restart Viewer Script
```bash
# From WSL
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
pkill -f "view_rules_web.py" 2>/dev/null; sleep 2; nohup python scripts/view_rules_web.py > viewer.log 2>&1 & echo "✅ Viewer restarted"
```

## Troubleshooting

### "Address already in use" Error
This means MLflow is already running. You don't need to start it again.

**To verify:**
```bash
# Check if MLflow is running
pgrep -f "mlflow ui" && echo "MLflow is running" || echo "MLflow is not running"

# Check port 5000
netstat -tuln | grep 5000 || ss -tuln | grep 5000
```

**If you need to restart:**
1. Stop MLflow: `pkill -f "mlflow ui"`
2. Wait 2-3 seconds
3. Start MLflow again using one of the start methods above

## Service Ports

- **PostgreSQL**: 5432
- **MLflow UI**: 5000
- **JupyterLab**: 8888 (default)
- **Eligibility Rules Viewer**: 5001

