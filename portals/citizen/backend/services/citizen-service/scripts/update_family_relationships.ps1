# PowerShell script to update family relationships in PostgreSQL
# Usage: .\update_family_relationships.ps1

$env:PGPASSWORD = "anjali143"
$dbHost = "localhost"
$dbPort = "5432"
$dbName = "smart_citizen"
$dbUser = "sameer"

$sqlFile = Join-Path $PSScriptRoot "update_family_relationships_simple.sql"

Write-Host "Updating family relationships for seed Aadhaar: 387193279353..." -ForegroundColor Cyan

try {
    $result = & psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -f $sqlFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Family relationships updated successfully!" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "❌ Error updating family relationships:" -ForegroundColor Red
        Write-Host $result
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
} finally {
    $env:PGPASSWORD = $null
}

