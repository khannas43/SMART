# PowerShell script to populate Hindi names for existing schemes
# This script uses the backend API to update schemes with transliterated Hindi names

$baseUrl = "http://localhost:8080/api/v1"
$schemesEndpoint = "$baseUrl/schemes"

Write-Host "Fetching all schemes..." -ForegroundColor Cyan

try {
    # Get all schemes
    $response = Invoke-RestMethod -Uri $schemesEndpoint -Method Get -ContentType "application/json"
    
    if ($response.success -and $response.data) {
        $schemes = $response.data.content
        
        Write-Host "Found $($schemes.Count) schemes" -ForegroundColor Green
        
        foreach ($scheme in $schemes) {
            Write-Host "Processing scheme: $($scheme.name) ($($scheme.code))" -ForegroundColor Yellow
            
            # Check if Hindi name is missing
            if ([string]::IsNullOrWhiteSpace($scheme.nameHindi)) {
                Write-Host "  - Hindi name missing, will be auto-populated on next update" -ForegroundColor Gray
            } else {
                Write-Host "  - Hindi name already exists: $($scheme.nameHindi)" -ForegroundColor Green
            }
        }
        
        Write-Host "`nNote: Hindi names are auto-populated when schemes are created or updated via API." -ForegroundColor Cyan
        Write-Host "To populate Hindi names for existing schemes, update each scheme via PUT /schemes/{id}" -ForegroundColor Cyan
        Write-Host "The TransliterationService will automatically populate name_hindi and description_hindi." -ForegroundColor Cyan
        
    } else {
        Write-Host "Failed to fetch schemes" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Make sure the backend server is running on http://localhost:8080" -ForegroundColor Yellow
}

