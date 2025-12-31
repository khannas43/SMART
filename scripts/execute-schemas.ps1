# Execute Schema Files for All Databases
# Run this after databases are created

param(
    [string]$DbHost = "172.17.16.1",
    [int]$Port = 5432,
    [string]$User = "sameer",
    [string]$Password = "anjali143"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SMART Platform - Execute Schema Files" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
$env:PGPASSWORD = $Password

$schemas = @(
    @{
        Database = "smart_citizen"
        SchemaFile = "portals\citizen\database\schemas\01_citizen_schema.sql"
        Description = "Citizen Portal"
    },
    @{
        Database = "smart_dept"
        SchemaFile = "portals\dept\database\schemas\01_dept_schema.sql"
        Description = "Department Portal"
    },
    @{
        Database = "smart_aiml"
        SchemaFile = "portals\aiml\database\schemas\01_aiml_schema.sql"
        Description = "AIML Portal"
    },
    @{
        Database = "smart_monitor"
        SchemaFile = "portals\monitor\database\schemas\01_monitor_schema.sql"
        Description = "Monitor Portal"
    },
    @{
        Database = "smart_warehouse"
        SchemaFile = "ai-ml\pipelines\warehouse\schemas\01_warehouse_schema.sql"
        Description = "AIML Warehouse"
    }
)

$successCount = 0
$failCount = 0

foreach ($schema in $schemas) {
    Write-Host "Processing: $($schema.Description) ($($schema.Database))" -ForegroundColor Yellow
    
    $schemaPath = Join-Path $projectRoot $schema.SchemaFile
    
    if (-not (Test-Path $schemaPath)) {
        Write-Host "  ❌ Schema file not found: $($schema.SchemaFile)" -ForegroundColor Red
        $failCount++
        continue
    }
    
    Write-Host "  Executing: $($schema.SchemaFile)" -ForegroundColor Gray
    
    try {
        # Grant schema privileges first
        $grantQuery = @"
GRANT ALL ON SCHEMA public TO $User;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $User;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $User;
"@
        
        psql -h $DbHost -p $Port -U $User -d $schema.Database -c $grantQuery 2>&1 | Out-Null
        
        if ($schema.Database -eq "smart_warehouse") {
            psql -h $DbHost -p $Port -U $User -d $schema.Database -c "CREATE SCHEMA IF NOT EXISTS staging; GRANT ALL ON SCHEMA staging TO $User;" 2>&1 | Out-Null
        }
        
        # Execute schema file
        $result = psql -h $DbHost -p $Port -U $User -d $schema.Database -f $schemaPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Schema executed successfully" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ❌ Schema execution failed" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "  ❌ Error: $_" -ForegroundColor Red
        $failCount++
    }
    
    Write-Host ""
}

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

