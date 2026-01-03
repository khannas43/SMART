# Quick Database Cleanup Script for Citizen Service
# This will drop all tables and let Flyway recreate them

Write-Host "=== Database Cleanup for Citizen Service ===" -ForegroundColor Cyan
Write-Host ""

# Set password (adjust if needed)
$env:PGPASSWORD = "anjali143"

# Drop and recreate public schema
Write-Host "Dropping public schema..." -ForegroundColor Yellow
psql -U sameer -d smart_citizen -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO sameer; GRANT ALL ON SCHEMA public TO public;"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Database cleaned successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now you can run:" -ForegroundColor Cyan
    Write-Host "  mvn spring-boot:run" -ForegroundColor White
    Write-Host ""
    Write-Host "Flyway will automatically create all tables from migrations." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Error cleaning database. Please check your PostgreSQL connection." -ForegroundColor Red
    Write-Host "Make sure PostgreSQL is running and credentials are correct." -ForegroundColor Yellow
}

# Clear password from environment
Remove-Item Env:\PGPASSWORD

