# SMART Platform - Environment Verification Script
# PowerShell script to verify all installations and connections

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SMART Platform - Environment Verification" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Function to test command availability
function Test-Command {
    param($Command, $Name, $Required)
    
    Write-Host "Testing $Name..." -NoNewline
    try {
        $version = & $Command --version 2>&1
        if ($LASTEXITCODE -eq 0 -or $version) {
            Write-Host " ✅ PASSED" -ForegroundColor Green
            Write-Host "   $version" -ForegroundColor Gray
            return $true
        } else {
            Write-Host " ❌ FAILED" -ForegroundColor Red
            if ($Required) {
                Write-Host "   Required component missing!" -ForegroundColor Yellow
                $script:allPassed = $false
            }
            return $false
        }
    } catch {
        Write-Host " ❌ NOT FOUND" -ForegroundColor Red
        if ($Required) {
            Write-Host "   Required component missing!" -ForegroundColor Yellow
            $script:allPassed = $false
        }
        return $false
    }
}

# Test Java
Write-Host "`n--- Java Development Kit ---" -ForegroundColor Yellow
Test-Command "java" "Java JDK" $true | Out-Null
Test-Command "javac" "Java Compiler" $true | Out-Null

# Test Node.js and npm
Write-Host "`n--- Node.js & npm ---" -ForegroundColor Yellow
$nodeOk = Test-Command "node" "Node.js" $true
$npmOk = Test-Command "npm" "npm" $true

# Test Maven
Write-Host "`n--- Maven ---" -ForegroundColor Yellow
$mavenOk = Test-Command "mvn" "Maven" $true

# Test Git
Write-Host "`n--- Git ---" -ForegroundColor Yellow
$gitOk = Test-Command "git" "Git" $true

# Test Docker
Write-Host "`n--- Docker ---" -ForegroundColor Yellow
$dockerOk = Test-Command "docker" "Docker" $false
if ($dockerOk) {
    Test-Command "docker-compose" "Docker Compose" $false | Out-Null
}

# Test PostgreSQL
Write-Host "`n--- PostgreSQL ---" -ForegroundColor Yellow
$pgOk = Test-Command "psql" "PostgreSQL Client" $false
if ($pgOk) {
    Write-Host "`nTesting PostgreSQL connection..." -NoNewline
    try {
        $env:PGPASSWORD = "anjali143"
        $result = & psql -h localhost -p 5432 -U sameer -d smart -c "SELECT version();" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅ CONNECTED" -ForegroundColor Green
            Write-Host "   Database: smart" -ForegroundColor Gray
            Write-Host "   User: sameer" -ForegroundColor Gray
        } else {
            Write-Host " ❌ CONNECTION FAILED" -ForegroundColor Red
            Write-Host "   Check if PostgreSQL is running" -ForegroundColor Yellow
        }
    } catch {
        Write-Host " ❌ CONNECTION FAILED" -ForegroundColor Red
    }
    $env:PGPASSWORD = ""
} else {
    Write-Host "   PostgreSQL client not found. Connection test skipped." -ForegroundColor Gray
}

# Test Python (WSL)
Write-Host "`n--- Python (WSL) ---" -ForegroundColor Yellow
Write-Host "Testing WSL Python venv..." -NoNewline
try {
    $pythonVersion = wsl bash -c "/mnt/c/Projects/SMART/ai-ml/.venv/bin/python --version 2>&1"
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ PASSED" -ForegroundColor Green
        Write-Host "   $pythonVersion" -ForegroundColor Gray
        Write-Host "   Location: /mnt/c/Projects/SMART/ai-ml/.venv/bin/python" -ForegroundColor Gray
    } else {
        Write-Host " ⚠️  VENV NOT FOUND" -ForegroundColor Yellow
        Write-Host "   Expected at: /mnt/c/Projects/SMART/ai-ml/.venv" -ForegroundColor Gray
    }
} catch {
    Write-Host " ⚠️  WSL NOT AVAILABLE" -ForegroundColor Yellow
    Write-Host "   Python venv check skipped" -ForegroundColor Gray
}

# Test MLflow
Write-Host "`n--- MLflow ---" -ForegroundColor Yellow
Write-Host "Testing MLflow connection..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅ CONNECTED" -ForegroundColor Green
        Write-Host "   URI: http://127.0.0.1:5000" -ForegroundColor Gray
    }
} catch {
    Write-Host " ❌ NOT RUNNING" -ForegroundColor Red
    Write-Host "   Start MLflow with:" -ForegroundColor Yellow
    Write-Host "   wsl bash -c 'cd /mnt/c/Projects/SMART/ai-ml && source .venv/bin/activate && mlflow ui --host 0.0.0.0 --port 5000'" -ForegroundColor Gray
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "✅ All required components are installed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some required components are missing" -ForegroundColor Yellow
    Write-Host "   See INSTALLATION_STATUS.md for installation instructions" -ForegroundColor Gray
}
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $allPassed) {
    exit 1
}

