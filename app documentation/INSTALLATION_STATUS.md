# SMART Platform - Installation Status

**Verification Date:** Generated on verification

## ✅ Installed Software

| Software | Status | Version | Notes |
|----------|--------|---------|-------|
| **Java JDK** | ✅ Installed | 21.0.9 (OpenJDK) | Exceeds requirement (17+). JAVA_HOME is set correctly. |
| **Node.js** | ✅ Installed | v24.12.0 | Exceeds requirement (18+). Ready for React development. |
| **npm** | ✅ Installed | 11.6.2 | Latest version. Ready for package management. |
| **Docker** | ✅ Installed | 29.1.3 | Latest version. Ready for containerization. |
| **Docker Compose** | ✅ Installed | v2.40.3 | Latest version. Ready for multi-container setups. |

## ❌ Missing Software

| Software | Status | Priority | Required For |
|----------|--------|----------|--------------|
| **Maven** | ❌ Not Installed | **HIGH** | Backend Java build tool - **Required** |
| **Git** | ❌ Not Installed | **HIGH** | Version control - **Required** |
| **PostgreSQL** | ✅ Installed | **HIGH** | Database - Configured and running (see DEVELOPMENT_CONFIG.md) |
| **Python** | ✅ Installed (WSL venv) | **MEDIUM** | AI/ML components - Using WSL2 venv at `/mnt/c/Projects/SMART/ai-ml/.venv` |
| **pip** | ✅ Installed (WSL venv) | **MEDIUM** | Python package manager - Available in venv |

## 📋 Installation Priority

### Priority 1: Critical (Must Install)
These are required to start development:

1. **Maven** - Build Java/Spring Boot services
2. **Git** - Version control and clone repositories
3. **PostgreSQL** - Database for all portals

### Priority 2: Important (Should Install)
For AI/ML development:

4. **Python 3.8+** - Required for AI/ML use cases
5. **pip** - Python package manager

## 🔧 Next Steps

### 1. Install Maven
**Windows:**
1. Download from: https://maven.apache.org/download.cgi
2. Extract to: `C:\Program Files\Apache\maven`
3. Set environment variables:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("MAVEN_HOME", "C:\Program Files\Apache\maven", "Machine")
   [System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\Apache\maven\bin", "Machine")
   ```
4. Verify: `mvn --version`

**Alternative:** Use Chocolatey (if installed):
```powershell
choco install maven
```

### 2. Install Git
**Windows:**
1. Download from: https://git-scm.com/download/win
2. Run installer (use default options)
3. Verify: `git --version`

**Alternative:** Use Chocolatey:
```powershell
choco install git
```

### 3. PostgreSQL Status
**✅ PostgreSQL is already installed and configured!**

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `smart`
- Username: `sameer`
- Password: `anjali143`

See `app documentation/DEVELOPMENT_CONFIG.md` for connection details.
**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer:
   - Choose PostgreSQL version 14 or higher
   - Remember the postgres user password you set
   - Install PostgreSQL service to run automatically
3. Add PostgreSQL bin to PATH:
   ```powershell
   # Usually: C:\Program Files\PostgreSQL\14\bin
   [System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\PostgreSQL\14\bin", "Machine")
   ```
4. Verify: `psql --version`
5. Create databases (after installation):
   ```sql
   CREATE DATABASE smart_citizen;
   CREATE DATABASE smart_dept;
   CREATE DATABASE smart_aiml;
   CREATE DATABASE smart_monitor;
   ```

**Alternative:** Use Docker (if you prefer):
```powershell
docker run --name postgres-smart -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:14
```

### 4. Python Status (for AI/ML)
**✅ Python environment is set up via WSL2!**

**Configuration:**
- **Environment:** WSL2 (Ubuntu 24.04) with Python virtual environment
- **Location:** `/mnt/c/Projects/SMART/ai-ml/.venv`
- **Interpreter:** `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`
- **Packages:** PyTorch, MLflow, pandas, numpy, scikit-learn, jupyterlab, etc.

**Usage:**
```bash
# From WSL terminal
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
python scripts/hello_mlflow.py
```

**MLflow Tracking:** `http://127.0.0.1:5000/`

See `app documentation/DEVELOPMENT_CONFIG.md` for detailed setup.

## ✅ Current Configuration

### Environment Variables Set:
- ✅ `JAVA_HOME` = `C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot\`
- ❌ `MAVEN_HOME` = Not set
- ✅ Java is in PATH

### Ready for Development:
- ✅ Frontend development (React) - Node.js and npm are ready
- ✅ Docker containerization - Docker Desktop is ready
- ✅ Database operations - PostgreSQL is configured and ready
- ✅ AI/ML development - Python venv is set up with all packages
- ❌ Backend development (Java/Spring Boot) - Need Maven
- ❌ Version control - Need Git

## 🚀 Quick Install Commands (Using Chocolatey)

If you have Chocolatey package manager installed, you can install everything at once:

```powershell
# Install Maven
choco install maven -y

# Install Git
choco install git -y

# Install PostgreSQL
choco install postgresql14 -y

# Install Python
choco install python -y
```

## 📝 Verification Commands

After installing missing software, run these to verify:

```powershell
# Verify all installations
java -version          # ✅ Already working
node --version         # ✅ Already working
npm --version          # ✅ Already working
mvn --version          # ❌ Install Maven
git --version          # ❌ Install Git
psql --version         # ❌ Install PostgreSQL
docker --version       # ✅ Already working
docker-compose --version # ✅ Already working
python --version       # ❌ Install Python (optional)
pip --version          # ❌ Install Python (optional)
```

## 🎯 Recommended Installation Order

1. **Git** - Install first (needed for cloning repos if starting fresh)
2. **Maven** - Install second (needed for building backend services)
3. ✅ **PostgreSQL** - Already installed and configured
4. ✅ **Python** - Already set up via WSL2 venv

**All remaining:** Install Maven and Git to complete the setup.

