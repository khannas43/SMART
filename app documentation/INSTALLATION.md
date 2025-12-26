# SMART Platform - Installation Guide

This document outlines all the software and tools required to set up a development environment for the SMART Platform.

## Prerequisites Overview

The SMART Platform requires the following software stack:

### Required Software

1. **Java Development Kit (JDK)** - Version 17 or higher
2. **Node.js and npm** - For frontend development
3. **Maven** - Java build tool
4. **PostgreSQL** - Database (Version 14 or higher)
5. **Git** - Version control
6. **Docker & Docker Compose** - For containerized development/deployment
7. **Python** - For AI/ML components (Version 3.8 or higher)

### Optional Software

1. **Kubernetes (kubectl)** - For Kubernetes deployment
2. **Nginx** - Web server (can use Docker container)
3. **IDE** - IntelliJ IDEA, Eclipse, or VS Code recommended

---

## Detailed Installation Instructions

### 1. Java Development Kit (JDK) 17+

The backend services use Spring Boot 3.x which requires Java 17 or higher.

#### Windows:
1. Download JDK 17+ from [Oracle](https://www.oracle.com/java/technologies/downloads/#java17) or [OpenJDK](https://adoptium.net/)
2. Install the JDK
3. Set `JAVA_HOME` environment variable:
   - Go to System Properties → Environment Variables
   - Add `JAVA_HOME` pointing to JDK installation directory (e.g., `C:\Program Files\Java\jdk-17`)
   - Add `%JAVA_HOME%\bin` to `PATH`
4. Verify installation:
   ```bash
   java -version
   javac -version
   ```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-17-jdk

# macOS (using Homebrew)
brew install openjdk@17

# Verify
java -version
javac -version
```

---

### 2. Node.js and npm

Required for React frontend development.

#### Windows:
1. Download and install Node.js LTS from [nodejs.org](https://nodejs.org/)
2. Verify installation:
   ```bash
   node --version
   npm --version
   ```

#### Linux:
```bash
# Using Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts

# Or using package manager
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### macOS:
```bash
# Using Homebrew
brew install node

# Or using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

**Verify installation:**
```bash
node --version  # Should show v18.x or higher
npm --version   # Should show 9.x or higher
```

---

### 3. Maven

Java build tool for Spring Boot microservices.

#### Windows:
1. Download Maven from [maven.apache.org](https://maven.apache.org/download.cgi)
2. Extract to a directory (e.g., `C:\Program Files\Apache\maven`)
3. Set environment variables:
   - `MAVEN_HOME` = `C:\Program Files\Apache\maven`
   - Add `%MAVEN_HOME%\bin` to `PATH`
4. Verify:
   ```bash
   mvn --version
   ```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt install maven

# macOS
brew install maven

# Verify
mvn --version
```

---

### 4. PostgreSQL

Database for all portals.

#### Windows:
1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Remember the postgres user password you set
4. PostgreSQL service should start automatically
5. Verify:
   ```bash
   psql --version
   ```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Set up postgres user password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'your_password';
\q
```

#### macOS:
```bash
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb smart_dev
```

**Post-installation steps:**
1. Create databases for each portal (optional, can be created during setup):
   ```sql
   CREATE DATABASE smart_citizen;
   CREATE DATABASE smart_dept;
   CREATE DATABASE smart_aiml;
   CREATE DATABASE smart_monitor;
   ```

---

### 5. Git

Version control system.

#### Windows:
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer
3. Verify:
   ```bash
   git --version
   ```

#### Linux/Mac:
```bash
# Linux
sudo apt install git

# macOS
brew install git

# Verify
git --version
```

---

### 6. Docker & Docker Compose

For containerized development and deployment.

#### Windows:
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install Docker Desktop (includes Docker Compose)
3. Start Docker Desktop
4. Verify:
   ```bash
   docker --version
   docker-compose --version
   ```

#### Linux:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify (may need to log out and back in)
docker --version
docker-compose --version
```

#### macOS:
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop from docker.com
# Docker Desktop includes Docker Compose

# Verify
docker --version
docker-compose --version
```

---

### 7. Python (for AI/ML Components)

Required for AI/ML use cases.

#### Windows:
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify:
   ```bash
   python --version
   pip --version
   ```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Verify
python3 --version
pip3 --version
```

#### macOS:
```bash
brew install python3

# Verify
python3 --version
pip3 --version
```

**Install Python ML dependencies:**
```bash
pip install torch mlflow numpy pandas scikit-learn

# Or create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install torch mlflow numpy pandas scikit-learn
```

---

### 8. Kubernetes (Optional)

Only needed if deploying to Kubernetes.

#### Windows:
1. Install kubectl:
   ```bash
   # Using Chocolatey
   choco install kubernetes-cli
   
   # Or download from https://kubernetes.io/docs/tasks/tools/
   ```

#### Linux:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
```

#### macOS:
```bash
brew install kubectl

# Verify
kubectl version --client
```

---

## IDE Setup (Recommended)

### IntelliJ IDEA (Java Development)
1. Download IntelliJ IDEA Community or Ultimate from [jetbrains.com](https://www.jetbrains.com/idea/)
2. Install Maven plugin (usually included)
3. Install Lombok plugin (if used)
4. Configure JDK: File → Project Structure → Project SDK → Select JDK 17

### VS Code (Frontend Development)
1. Download VS Code from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install extensions:
   - ES7+ React/Redux/React-Native snippets
   - ESLint
   - Prettier
   - TypeScript and JavaScript Language Features
   - Auto Rename Tag
   - GitLens

---

## Verification Checklist

After installation, verify everything is set up correctly:

```bash
# Java
java -version          # Should show 17 or higher
javac -version         # Should show 17 or higher

# Node.js
node --version         # Should show v18.x or higher
npm --version          # Should show 9.x or higher

# Maven
mvn --version          # Should show 3.8.x or higher

# PostgreSQL
psql --version         # Should show 14.x or higher

# Git
git --version          # Any recent version

# Docker
docker --version       # Should show 20.x or higher
docker-compose --version  # Should show 2.x or higher

# Python (for AI/ML)
python --version       # Should show 3.8 or higher (use python3 on Linux/Mac)
pip --version          # Should show 23.x or higher (use pip3 on Linux/Mac)
```

---

## Environment Variables Setup

### Windows (PowerShell)
```powershell
# Java
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:PATH += ";$env:JAVA_HOME\bin"

# Maven
$env:MAVEN_HOME = "C:\Program Files\Apache\maven"
$env:PATH += ";$env:MAVEN_HOME\bin"

# PostgreSQL (if not in PATH)
$env:PATH += ";C:\Program Files\PostgreSQL\14\bin"
```

### Linux/Mac (Bash)
Add to `~/.bashrc` or `~/.zshrc`:
```bash
# Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Maven
export MAVEN_HOME=/usr/share/maven
export PATH=$MAVEN_HOME/bin:$PATH

# PostgreSQL (usually already in PATH)
export PATH=/usr/lib/postgresql/14/bin:$PATH
```

---

## Quick Start Verification

After completing installations, test with these commands:

```bash
# Test Java/Maven build
cd portals/citizen/backend/services/citizen-service
mvn clean compile

# Test Node.js
cd portals/citizen/frontend
npm install

# Test PostgreSQL connection
psql -U postgres -c "SELECT version();"

# Test Docker
docker run hello-world

# Test Python
python --version
python -c "import torch; print('PyTorch installed successfully')"
```

---

## Troubleshooting

### Common Issues

1. **Java version mismatch**: Ensure JAVA_HOME points to JDK 17+, not an older version
2. **Maven not found**: Verify MAVEN_HOME is set and added to PATH
3. **PostgreSQL connection refused**: Ensure PostgreSQL service is running
4. **Docker daemon not running**: Start Docker Desktop (Windows/Mac) or `sudo systemctl start docker` (Linux)
5. **Python not found**: Use `python3` on Linux/Mac, ensure Python is in PATH on Windows

---

## Next Steps

After completing the installation:

1. Clone the repository (if not already done)
2. Follow portal-specific setup instructions:
   - [Citizen Portal Setup](portals/citizen/README.md)
   - [Department Portal Setup](portals/dept/README.md)
   - [AI/ML Portal Setup](portals/aiml/README.md)
   - [Monitor Portal Setup](portals/monitor/README.md)
3. Review the [Architecture Documentation](ARCHITECTURE.md)
4. Check the [Deployment Guide](DEPLOYMENT.md) for deployment instructions

---

## Additional Resources

- [Java Documentation](https://docs.oracle.com/en/java/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Maven Documentation](https://maven.apache.org/guides/)

