# Create All Databases and Execute Schemas
# Bypasses execution policy issues

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SMART Platform - Create Databases and Schemas" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$dbHost = "172.17.16.1"
$port = 5432
$user = "sameer"
$password = "anjali143"
$env:PGPASSWORD = $password

$projectRoot = $PSScriptRoot
$schemas = @(
    @{ Database = "smart_citizen"; File = "portals\citizen\database\schemas\01_citizen_schema.sql"; Desc = "Citizen Portal" },
    @{ Database = "smart_dept"; File = "portals\dept\database\schemas\01_dept_schema.sql"; Desc = "Department Portal" },
    @{ Database = "smart_aiml"; File = "portals\aiml\database\schemas\01_aiml_schema.sql"; Desc = "AIML Portal" },
    @{ Database = "smart_monitor"; File = "portals\monitor\database\schemas\01_monitor_schema.sql"; Desc = "Monitor Portal" },
    @{ Database = "smart_warehouse"; File = "ai-ml\pipelines\warehouse\schemas\01_warehouse_schema.sql"; Desc = "AIML Warehouse" }
)

$successCount = 0
$failCount = 0

foreach ($schema in $schemas) {
    Write-Host ""
    Write-Host "Processing: $($schema.Desc) ($($schema.Database))" -ForegroundColor Yellow
    
    $schemaPath = Join-Path $projectRoot "..\$($schema.File)"
    
    if (-not (Test-Path $schemaPath)) {
        Write-Host "  ❌ Schema file not found: $($schema.File)" -ForegroundColor Red
        $failCount++
        continue
    }
    
    Write-Host "  Schema file: $($schema.File)" -ForegroundColor Gray
    
    # Check if database exists
    $dbCheck = psql -h $dbHost -p $port -U $user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$($schema.Database)'" 2>&1
    
    if ($dbCheck -ne "1") {
        Write-Host "  Database does not exist. Creating..." -ForegroundColor Yellow
        # Note: This requires superuser - skip if not available
        Write-Host "  ⚠️  Please create database manually or run as postgres superuser" -ForegroundColor Yellow
        Write-Host "  SQL: CREATE DATABASE $($schema.Database) WITH OWNER = $user ENCODING = 'UTF8';" -ForegroundColor Cyan
    } else {
        Write-Host "  ✅ Database exists" -ForegroundColor Green
    }
    
    # Grant privileges
    Write-Host "  Granting privileges..." -NoNewline
    $grantResult = psql -h $dbHost -p $port -U $user -d $schema.Database -c "GRANT ALL ON SCHEMA public TO $user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $user;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ⚠️" -ForegroundColor Yellow
    }
    
    if ($schema.Database -eq "smart_warehouse") {
        psql -h $dbHost -p $port -U $user -d $schema.Database -c "CREATE SCHEMA IF NOT EXISTS staging; GRANT ALL ON SCHEMA staging TO $user;" 2>&1 | Out-Null
    }
    
    # Execute schema
    Write-Host "  Executing schema..." -NoNewline
    $result = psql -h $dbHost -p $port -U $user -d $schema.Database -f $schemaPath 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
        
        # Verify tables created
        $tableCount = psql -h $dbHost -p $port -U $user -d $schema.Database -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>&1
        Write-Host "  ✅ Tables created: $tableCount" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "  Error output:" -ForegroundColor Red
        $result | Select-Object -First 10 | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        $failCount++
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Success: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "✅ All schemas executed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some schemas failed" -ForegroundColor Yellow
}

