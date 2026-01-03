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

### 2. Neo4j (Required for Family Tree Graph Visualization)

Neo4j is used for family relationship graph queries in the Citizen Portal.

**Option A: Neo4j Desktop (Recommended - GUI Application)**
1. Open Neo4j Desktop application
2. Find your database (e.g., "smartgraphdb")
3. Click "Start" button
4. Wait for status to show "Running"

**Option B: Neo4j Community Edition (Command Line)**

**Windows PowerShell:**
```powershell
# Navigate to Neo4j installation directory (adjust path as needed)
cd "C:\Program Files\Neo4j\neo4j-community-*\bin"

# Start Neo4j
.\neo4j.bat start

# Check status
.\neo4j.bat status
```

**WSL/Linux:**
```bash
# Navigate to Neo4j installation directory (adjust path as needed)
cd /path/to/neo4j/bin

# Start Neo4j
./neo4j start

# Check status
./neo4j status
```

**Option C: Docker (If using Docker)**
```bash
# Start Neo4j container
docker start neo4j

# Or if not created yet
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/anjali143 \
  neo4j:latest
```

**Verify Connection:**
```bash
# Check if Neo4j is running
# Windows PowerShell
netstat -an | findstr 7687

# WSL/Linux
netstat -an | grep 7687 || ss -tuln | grep 7687

# Test connection (requires cypher-shell or Python driver)
# From WSL with Python venv
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://172.17.16.1:7687', auth=('neo4j', 'anjali143')); driver.verify_connectivity(); print('✅ Neo4j connected'); driver.close()"
```

**Access URLs:**
- Neo4j Browser: http://172.17.16.1:7474 (or http://localhost:7474 if running locally)
- Bolt Protocol: bolt://172.17.16.1:7687

**Configuration:**
- URI: `bolt://172.17.16.1:7687`
- Username: `neo4j`
- Password: `anjali143`
- Database: `smartgraphdb`

### 3. MLflow UI (Required for ML tracking)

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

### 4. JupyterLab (Optional - for notebooks)

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
jupyter lab --no-browser
```

### 5. Citizen Portal - Backend Service (Spring Boot)

**Option A: Foreground Start (Windows PowerShell)**
```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
mvn clean spring-boot:run
```

**Option B: Background Start (Windows PowerShell)**
```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "mvn clean spring-boot:run"
```

**Option C: Foreground Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service
mvn clean spring-boot:run
```

**Option D: Background Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service
nohup mvn clean spring-boot:run > citizen-backend.log 2>&1 &
```

**Access URLs:**
- Backend API: http://localhost:8081
- Swagger UI: http://localhost:8081/swagger-ui.html
- API Docs: http://localhost:8081/v3/api-docs

### 6. Citizen Portal - Frontend Service (React + Vite)

**Option A: Foreground Start (Windows PowerShell)**
```powershell
cd C:\Projects\SMART\portals\citizen\frontend
npm run dev
```

**Option B: Background Start (Windows PowerShell)**
```powershell
cd C:\Projects\SMART\portals\citizen\frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
```

**Option C: Foreground Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/portals/citizen/frontend
npm run dev
```

**Option D: Background Start (WSL)**
```bash
cd /mnt/c/Projects/SMART/portals/citizen/frontend
nohup npm run dev > citizen-frontend.log 2>&1 &
```

**Access URLs:**
- Frontend App: http://localhost:5173 (Vite default) or http://localhost:3000
- Login Page: http://localhost:5173/login

**Note:** Make sure to install dependencies first if needed:
```bash
cd /mnt/c/Projects/SMART/portals/citizen/frontend
npm install
```

### 7. Web Viewers (Multi-Use Case Interface)

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

### Check Neo4j
Open browser: http://172.17.16.1:7474 (or http://localhost:7474)

Or check if process is running:
```bash
# WSL
pgrep -f "neo4j" || netstat -an | grep 7687

# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*neo4j*"}
netstat -an | findstr 7687
```

Or test connection:
```bash
# From WSL with Python venv
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://172.17.16.1:7687', auth=('neo4j', 'anjali143')); driver.verify_connectivity(); print('✅ Neo4j connected'); driver.close()"
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

### Check Citizen Portal Backend
Open browser: http://localhost:8081/swagger-ui.html

Or check if process is running:
```bash
# WSL
pgrep -f "spring-boot:run"

# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*java*" -and $_.CommandLine -like "*citizen-service*"}
```

### Check Citizen Portal Frontend
Open browser: http://localhost:5173 or http://localhost:3000

Or check if process is running:
```bash
# WSL
pgrep -f "npm run dev" || pgrep -f "vite"

# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*node*"}
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

### Stop Citizen Portal Backend
```bash
# WSL
pkill -f "spring-boot:run"

# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*java*" -and $_.CommandLine -like "*citizen-service*"} | Stop-Process
```

### Stop Citizen Portal Frontend
```bash
# WSL
pkill -f "npm run dev" || pkill -f "vite"

# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process
```

### Stop Eligibility Rules Viewer
```bash
# WSL
pkill -f "view_rules_web.py"
```

### Stop Neo4j
```bash
# Neo4j Desktop: Click "Stop" button in GUI

# Command Line (Windows PowerShell)
cd "C:\Program Files\Neo4j\neo4j-community-*\bin"
.\neo4j.bat stop

# Command Line (WSL/Linux)
cd /path/to/neo4j/bin
./neo4j stop

# Docker
docker stop neo4j
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

### Restart Citizen Portal Backend (if already running)
```bash
# From WSL
# 1. Stop existing backend
pkill -f "spring-boot:run"

# 2. Wait a moment
sleep 2

# 3. Start backend again
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service
nohup mvn clean spring-boot:run > citizen-backend.log 2>&1 &

# 4. Verify it's running
pgrep -f "spring-boot:run" && echo "✅ Backend is running" || echo "❌ Backend failed to start"
```

### Quick Restart Backend Script
```bash
# From WSL
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service
pkill -f "spring-boot:run" 2>/dev/null; sleep 2; nohup mvn clean spring-boot:run > citizen-backend.log 2>&1 & echo "✅ Backend restarted"
```

### Restart Citizen Portal Frontend (if already running)
```bash
# From WSL
# 1. Stop existing frontend
pkill -f "npm run dev" || pkill -f "vite"

# 2. Wait a moment
sleep 2

# 3. Start frontend again
cd /mnt/c/Projects/SMART/portals/citizen/frontend
nohup npm run dev > citizen-frontend.log 2>&1 &

# 4. Verify it's running
pgrep -f "npm run dev" && echo "✅ Frontend is running" || echo "❌ Frontend failed to start"
```

### Quick Restart Frontend Script
```bash
# From WSL
cd /mnt/c/Projects/SMART/portals/citizen/frontend
pkill -f "npm run dev" 2>/dev/null || pkill -f "vite" 2>/dev/null; sleep 2; nohup npm run dev > citizen-frontend.log 2>&1 & echo "✅ Frontend restarted"
```

### Restart Neo4j (if already running)
```bash
# Neo4j Desktop: Click "Stop" then "Start" in GUI

# Command Line (Windows PowerShell)
cd "C:\Program Files\Neo4j\neo4j-community-*\bin"
.\neo4j.bat stop
sleep 2
.\neo4j.bat start

# Command Line (WSL/Linux)
cd /path/to/neo4j/bin
./neo4j stop
sleep 2
./neo4j start

# Docker
docker restart neo4j
```

### Quick Restart Neo4j Script
```bash
# From WSL (if Neo4j is installed in WSL)
cd /path/to/neo4j/bin
./neo4j stop 2>/dev/null; sleep 2; ./neo4j start && echo "✅ Neo4j restarted" || echo "❌ Neo4j failed to start"
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
- **Neo4j Browser**: 7474 (HTTP)
- **Neo4j Bolt**: 7687 (Bolt protocol)
- **MLflow UI**: 5000
- **JupyterLab**: 8888 (default)
- **Eligibility Rules Viewer**: 5001
- **Citizen Portal Backend**: 8081
- **Citizen Portal Frontend**: 5173 (Vite default) or 3000

