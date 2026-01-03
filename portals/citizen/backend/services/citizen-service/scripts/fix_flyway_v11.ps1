# Fix Flyway V11 Migration Status
# This script removes the failed V11 migration entry from Flyway schema history
# so that Flyway can re-run it on the next startup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Flyway V11 Migration Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set PostgreSQL password
$env:PGPASSWORD = 'anjali143'

Write-Host "Checking Flyway schema history..." -ForegroundColor Yellow

# Check current Flyway status
$checkQuery = @"
SELECT version, description, type, installed_on, success 
FROM flyway_schema_history 
WHERE version = '11' 
ORDER BY installed_rank DESC 
LIMIT 1;
"@

$result = psql -h localhost -U sameer -d smart_citizen -t -A -F "|" -c $checkQuery

if ($result) {
    Write-Host "Found V11 entry in Flyway history:" -ForegroundColor Yellow
    Write-Host $result -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Removing failed V11 entry..." -ForegroundColor Yellow
    
    # Delete the failed V11 entry
    $deleteQuery = "DELETE FROM flyway_schema_history WHERE version = '11';"
    psql -h localhost -U sameer -d smart_citizen -c $deleteQuery
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully removed V11 entry from Flyway history" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Restart the citizen-service" -ForegroundColor White
        Write-Host "2. Flyway will detect V11 and run it again" -ForegroundColor White
        Write-Host ""
        Write-Host "Command to restart:" -ForegroundColor Yellow
        Write-Host "  mvn spring-boot:run" -ForegroundColor Gray
    } else {
        Write-Host "❌ Failed to remove V11 entry" -ForegroundColor Red
        Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Red
    }
} else {
    Write-Host "No V11 entry found in Flyway history." -ForegroundColor Yellow
    Write-Host "This means V11 hasn't been attempted yet, or was already cleaned." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can proceed to restart the service - Flyway will run V11." -ForegroundColor Green
}

Write-Host ""
Write-Host "Current Flyway version status:" -ForegroundColor Cyan
$versionQuery = "SELECT MAX(version) as current_version FROM flyway_schema_history WHERE success = true;"
psql -h localhost -U sameer -d smart_citizen -c $versionQuery

