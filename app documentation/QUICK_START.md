# SMART Platform - Quick Start Guide

Quick reference for getting started with SMART Platform development.

## 🔧 Environment Status

✅ **Installed & Configured:**
- Java JDK 21
- Node.js v24.12.0 & npm 11.6.2
- Docker & Docker Compose
- PostgreSQL (configured)
- Python (WSL2 venv with all packages)

❌ **Still Needed:**
- Maven (for Java builds)
- Git (for version control)

## 📋 Quick Configuration Reference

### Database Connection

```bash
Host: localhost
Port: 5432
Database: smart
Username: sameer
Password: anjali143
```

**JDBC URL:**
```
jdbc:postgresql://localhost:5432/smart
```

**Test Connection:**
```bash
psql -h localhost -p 5432 -U sameer -d smart
```

### MLflow

**URI:** `http://127.0.0.1:5000/`

**Start MLflow UI:**
```bash
# From WSL terminal in ai-ml directory
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

### Python / AI-ML

**WSL2 Environment:**
- Project: `/mnt/c/Projects/SMART/ai-ml` (Windows: `C:\Projects\SMART\ai-ml`)
- Python: `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`
- Pip: `/mnt/c/Projects/SMART/ai-ml/.venv/bin/pip`

**Activate venv:**
```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
```

**Installed Packages:**
- PyTorch (CPU): torch, torchvision, torchaudio
- Data: pandas, numpy, scikit-learn, pyarrow
- MLflow, JupyterLab, Neo4j driver

## 🚀 Starting Development

### Frontend (React)

```bash
cd portals/citizen/frontend  # or dept, aiml, monitor
npm install
npm start
```

### Backend (Spring Boot)

```bash
cd portals/citizen/backend/services/citizen-service
mvn clean install  # Need Maven first!
mvn spring-boot:run
```

### AI/ML (Python)

```bash
# From WSL terminal
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
python scripts/hello_mlflow.py
```

### Jupyter Lab

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
jupyter lab
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION.md)** - Complete installation instructions
- **[Installation Status](INSTALLATION_STATUS.md)** - Current environment status
- **[Development Config](DEVELOPMENT_CONFIG.md)** - Detailed configuration reference
- **[Architecture](ARCHITECTURE.md)** - System architecture overview
- **[Deployment Guide](DEPLOYMENT.md)** - Deployment instructions

## 🔑 Key Files

- `.env.example` - Environment variable template
- `.vscode/settings.json` - Cursor/VS Code Python interpreter settings
- `ai-ml/.vscode/settings.json` - AI/ML specific settings
- `ai-ml/README.md` - AI/ML module documentation

## ⚡ Next Steps

1. **Install Maven** (if not done)
   ```powershell
   choco install maven
   # Or download from https://maven.apache.org/
   ```

2. **Install Git** (if not done)
   ```powershell
   choco install git
   # Or download from https://git-scm.com/
   ```

3. **Start Development:**
   - Frontend: Open a portal's frontend folder
   - Backend: Open a portal's backend service folder
   - AI/ML: Open `ai-ml` folder (use WSL Python)

## 🎯 Cursor IDE Setup

Cursor should automatically:
- Use WSL Python interpreter: `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`
- Activate venv in terminals
- Configure Jupyter kernels

**Verify:** Open a Python file and check the interpreter in bottom-right corner.

---

**Need Help?** Check the detailed documentation files listed above.

