#!/bin/bash
# SMART Platform - Environment Verification Script
# Bash script for WSL/Linux to verify all installations and connections

echo "============================================================"
echo "SMART Platform - Environment Verification"
echo "============================================================"
echo ""

all_passed=true

# Function to test command availability
test_command() {
    local cmd=$1
    local name=$2
    local required=${3:-true}
    
    echo -n "Testing $name... "
    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n 1)
        echo "✅ PASSED"
        echo "   $version"
        return 0
    else
        echo "❌ NOT FOUND"
        if [ "$required" = true ]; then
            echo "   Required component missing!"
            all_passed=false
        fi
        return 1
    fi
}

# Test Java
echo "--- Java Development Kit ---"
test_command "java" "Java JDK" true
test_command "javac" "Java Compiler" true

# Test Node.js and npm
echo ""
echo "--- Node.js & npm ---"
test_command "node" "Node.js" true
test_command "npm" "npm" true

# Test Maven
echo ""
echo "--- Maven ---"
test_command "mvn" "Maven" true

# Test Git
echo ""
echo "--- Git ---"
test_command "git" "Git" true

# Test Docker
echo ""
echo "--- Docker ---"
if test_command "docker" "Docker" false; then
    test_command "docker-compose" "Docker Compose" false
fi

# Test PostgreSQL
echo ""
echo "--- PostgreSQL ---"
if test_command "psql" "PostgreSQL Client" false; then
    echo -n "Testing PostgreSQL connection... "
    export PGPASSWORD="anjali143"
    if psql -h localhost -p 5432 -U sameer -d smart -c "SELECT version();" &> /dev/null; then
        echo "✅ CONNECTED"
        echo "   Database: smart"
        echo "   User: sameer"
    else
        echo "❌ CONNECTION FAILED"
        echo "   Check if PostgreSQL is running"
    fi
    unset PGPASSWORD
else
    echo "   PostgreSQL client not found. Connection test skipped."
fi

# Test Python venv
echo ""
echo "--- Python (venv) ---"
venv_python="/mnt/c/Projects/SMART/ai-ml/.venv/bin/python"
if [ -f "$venv_python" ]; then
    echo -n "Testing Python venv... "
    version=$($venv_python --version 2>&1)
    echo "✅ PASSED"
    echo "   $version"
    echo "   Location: $venv_python"
else
    echo "⚠️  VENV NOT FOUND"
    echo "   Expected at: $venv_python"
fi

# Test MLflow
echo ""
echo "--- MLflow ---"
echo -n "Testing MLflow connection... "
if curl -s -f http://127.0.0.1:5000 > /dev/null 2>&1; then
    echo "✅ CONNECTED"
    echo "   URI: http://127.0.0.1:5000"
else
    echo "❌ NOT RUNNING"
    echo "   Start MLflow with:"
    echo "   cd /mnt/c/Projects/SMART/ai-ml && source .venv/bin/activate && mlflow ui --host 0.0.0.0 --port 5000"
fi

# Summary
echo ""
echo "============================================================"
if [ "$all_passed" = true ]; then
    echo "✅ All required components are installed!"
else
    echo "⚠️  Some required components are missing"
    echo "   See INSTALLATION_STATUS.md for installation instructions"
fi
echo "============================================================"
echo ""

if [ "$all_passed" = false ]; then
    exit 1
fi

