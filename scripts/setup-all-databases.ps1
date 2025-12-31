# Setup All SMART Platform Databases
# Creates all databases and executes schema files

param(
    [string]$Host = "localhost",
    [int]$Port = 5432,
    [string]$User = "sameer",
    [string]$Password = "anjali143",
    [string]$SuperUser = "postgres",
    [string]$SuperPassword = ""
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SMART Platform - Database Setup Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $Password

$databases = @(
    @{
        Name = "smart_citizen"
        SchemaFile = "portals\citizen\database\schemas\01_citizen_schema.sql"
        Description = "Citizen Portal Database"
    },
    @{
        Name = "smart_dept"
        SchemaFile = "portals\dept\database\schemas\01_dept_schema.sql"
        Description = "Department Portal Database"
    },
    @{
        Name = "smart_aiml"
        SchemaFile = "portals\aiml\database\schemas\01_aiml_schema.sql"
        Description = "AIML Portal Database"
    },
    @{
        Name = "smart_monitor"
        SchemaFile = "portals\monitor\database\schemas\01_monitor_schema.sql"
        Description = "Monitor Portal Database"
    },
    @{
        Name = "smart_warehouse"
        SchemaFile = "ai-ml\pipelines\warehouse\schemas\01_warehouse_schema.sql"
        Description = "AIML Data Warehouse Database"
    }
)

$projectRoot = $PSScriptRoot

# Check if psql is available
try {
    $psqlVersion = psql --version 2>&1
    Write-Host "✅ PostgreSQL client found: $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL client (psql) not found in PATH" -ForegroundColor Red
    Write-Host "Please install PostgreSQL client or add it to PATH" -ForegroundColor Yellow
    exit 1
}

# Function to check if database exists
function Test-DatabaseExists {
    param($DbName, $Host, $Port, $User)
    
    $query = "SELECT 1 FROM pg_database WHERE datname = '$DbName'"
    $result = psql -h $Host -p $Port -U $User -d postgres -tAc $query 2>&1
    return ($result -eq "1")
}

# Function to create database
function New-Database {
    param($DbName, $Host, $Port, $SuperUser, $SuperPassword)
    
    Write-Host "  Creating database..." -NoNewline
    $createDbQuery = "CREATE DATABASE $DbName WITH OWNER = sameer ENCODING = 'UTF8';"
    
    if ($SuperPassword) {
        $env:PGPASSWORD = $SuperPassword
    }
    
    try {
        psql -h $Host -p $Port -U $SuperUser -d postgres -c $createDbQuery 2>&1 | Out-Null
        Write-Host " ✅" -ForegroundColor Green
        return $true
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        return $false
    }
    finally {
        $env:PGPASSWORD = $Password
    }
}

# Function to execute schema file
function Invoke-SchemaFile {
    param($DbName, $SchemaFile, $Host, $Port, $User, $Password)
    
    $fullPath = Join-Path $projectRoot $SchemaFile
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "    ⚠️  Schema file not found: $SchemaFile" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "  Executing schema file..." -NoNewline
    
    # Convert Windows path to WSL path if needed
    $wslPath = $fullPath -replace 'C:', '/mnt/c' -replace '\\', '/'
    
    try {
        # Use psql to execute schema file
        $env:PGPASSWORD = $Password
        $result = psql -h $Host -p $Port -U $User -d $DbName -f $fullPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅" -ForegroundColor Green
            return $true
        } else {
            Write-Host " ❌" -ForegroundColor Red
            Write-Host "    Error: $result" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        return $false
    }
}

# Process each database
$successCount = 0
$failCount = 0

foreach ($db in $databases) {
    Write-Host ""
    Write-Host "Processing: $($db.Description) ($($db.Name))" -ForegroundColor Yellow
    Write-Host "  Schema: $($db.SchemaFile)" -ForegroundColor Gray
    
    # Check if database exists
    $exists = Test-DatabaseExists -DbName $db.Name -Host $Host -Port $Port -User $User
    
    if ($exists) {
        Write-Host "  Database already exists" -ForegroundColor Cyan
        
        # Ask if user wants to recreate
        $response = Read-Host "  Recreate database? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host "  Dropping existing database..." -NoNewline
            $env:PGPASSWORD = $SuperPassword
            psql -h $Host -p $Port -U $SuperUser -d postgres -c "DROP DATABASE IF EXISTS $($db.Name);" 2>&1 | Out-Null
            $env:PGPASSWORD = $Password
            Write-Host " ✅" -ForegroundColor Green
            
            $created = New-Database -DbName $db.Name -Host $Host -Port $Port -SuperUser $SuperUser -SuperPassword $SuperPassword
            if (-not $created) {
                $failCount++
                continue
            }
        } else {
            Write-Host "  Skipping database creation" -ForegroundColor Cyan
        }
    } else {
        $created = New-Database -DbName $db.Name -Host $Host -Port $Port -SuperUser $SuperUser -SuperPassword $SuperPassword
        if (-not $created) {
            $failCount++
            continue
        }
    }
    
    # Execute schema file
    $schemaSuccess = Invoke-SchemaFile -DbName $db.Name -SchemaFile $db.SchemaFile -Host $Host -Port $Port -User $User -Password $Password
    
    if ($schemaSuccess) {
        $successCount++
        Write-Host "  ✅ Database setup completed successfully" -ForegroundColor Green
    } else {
        $failCount++
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Successfully setup: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "✅ All databases setup successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Some databases failed to setup" -ForegroundColor Yellow
    exit 1
}

