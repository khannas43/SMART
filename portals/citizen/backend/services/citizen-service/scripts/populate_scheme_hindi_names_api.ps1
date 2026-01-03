# PowerShell script to populate Hindi names for existing schemes via API
# This calls the backend endpoint to transliterate all schemes

$baseUrl = "http://localhost:8081/citizen/api/v1"
$endpoint = "$baseUrl/schemes/populate-hindi-names"

Write-Host "Populating Hindi names for existing schemes..." -ForegroundColor Cyan
Write-Host "Endpoint: $endpoint" -ForegroundColor Gray

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri $endpoint -Method Post -Headers $headers
    
    if ($response.success) {
        $updatedCount = $response.data
        Write-Host "Success! Updated $updatedCount schemes with Hindi names." -ForegroundColor Green
        Write-Host "Message: $($response.message)" -ForegroundColor Green
    } else {
        Write-Host "Failed: $($response.message)" -ForegroundColor Red
    }
} catch {
    $errorMessage = $_.Exception.Message
    Write-Host "Error: $errorMessage" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status: $statusCode" -ForegroundColor Yellow
        
        if ($statusCode -eq 401) {
            Write-Host "`nNote: The endpoint requires authentication or needs to be added to SecurityConfig." -ForegroundColor Yellow
            Write-Host "Please restart the backend server after updating SecurityConfig." -ForegroundColor Yellow
        }
    }
    
    Write-Host "`nMake sure:" -ForegroundColor Yellow
    Write-Host "1. Backend server is running on http://localhost:8081" -ForegroundColor Yellow
    Write-Host "2. The endpoint is accessible at: $endpoint" -ForegroundColor Yellow
    Write-Host "3. SecurityConfig allows access to /schemes/populate-hindi-names" -ForegroundColor Yellow
}

