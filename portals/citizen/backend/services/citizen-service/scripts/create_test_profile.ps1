# PowerShell script to create a test citizen profile
# Usage: .\create_test_profile.ps1

$env:PGPASSWORD = 'anjali143'

Write-Host "Creating test citizen profile..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Profile Details:" -ForegroundColor Yellow
Write-Host "  Aadhaar Number: 123456789012" -ForegroundColor White
Write-Host "  Mobile Number: 9876543210" -ForegroundColor White
Write-Host "  Name: Test Citizen" -ForegroundColor White
Write-Host "  Email: test.citizen@example.com" -ForegroundColor White
Write-Host ""

$sqlFile = Join-Path $PSScriptRoot "create_test_profile.sql"

if (-not (Test-Path $sqlFile)) {
    Write-Host "Error: SQL file not found at $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "Executing SQL script..." -ForegroundColor Cyan

psql -U sameer -d smart_citizen -f $sqlFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Test profile created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now login with:" -ForegroundColor Yellow
    Write-Host "  Jan Aadhaar ID: 123456789012" -ForegroundColor White
    Write-Host "  Mobile Number: 9876543210" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to create test profile. Check the error above." -ForegroundColor Red
    exit 1
}

