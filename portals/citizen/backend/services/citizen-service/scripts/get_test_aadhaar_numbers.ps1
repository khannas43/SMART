# PowerShell script to get top 25 Aadhaar numbers with maximum data
# This script queries the smart_citizen database and returns Aadhaar numbers with the most complete profiles

param(
    [string]$DatabaseHost = "localhost",
    [int]$DatabasePort = 5432,
    [string]$DatabaseName = "smart_citizen",
    [string]$DatabaseUser = "sameer",
    [string]$DatabasePassword = "anjali143"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Get Test Aadhaar Numbers with Maximum Data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable for password
$env:PGPASSWORD = $DatabasePassword

# SQL query to find top 25 citizens with maximum data
$query = @"
WITH citizen_scores AS (
    SELECT 
        c.id,
        c.aadhaar_number,
        c.mobile_number,
        c.full_name,
        c.email,
        c.date_of_birth,
        c.gender,
        c.address_line1,
        c.city,
        c.district,
        c.pincode,
        -- Calculate completeness score
        (
            CASE WHEN c.aadhaar_number IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.mobile_number IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.email IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.full_name IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.date_of_birth IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.gender IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.address_line1 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.city IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.district IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.pincode IS NOT NULL THEN 1 ELSE 0 END
        ) AS profile_score,
        -- Count related data
        (SELECT COUNT(*) FROM documents d WHERE d.citizen_id = c.id) AS document_count,
        (SELECT COUNT(*) FROM service_applications sa WHERE sa.citizen_id = c.id) AS application_count
    FROM citizens c
    WHERE c.aadhaar_number IS NOT NULL 
      AND c.aadhaar_number != ''
      AND c.mobile_number IS NOT NULL
      AND c.status = 'ACTIVE'
),
ranked_citizens AS (
    SELECT 
        *,
        -- Total score = profile score + bonus for documents and applications
        (profile_score + 
         CASE WHEN document_count > 0 THEN 2 ELSE 0 END +
         CASE WHEN application_count > 0 THEN 2 ELSE 0 END
        ) AS total_score,
        ROW_NUMBER() OVER (ORDER BY 
            (profile_score + 
             CASE WHEN document_count > 0 THEN 2 ELSE 0 END +
             CASE WHEN application_count > 0 THEN 2 ELSE 0 END
            ) DESC,
            document_count DESC,
            application_count DESC
        ) AS rank
    FROM citizen_scores
)
SELECT 
    rank,
    aadhaar_number,
    mobile_number,
    full_name,
    COALESCE(email, 'N/A') as email,
    district,
    profile_score,
    document_count,
    application_count,
    total_score
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;
"@

Write-Host "Querying database for top 25 citizens with maximum data..." -ForegroundColor Yellow
Write-Host ""

try {
    # Execute query and get results
    $results = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d $DatabaseName -t -A -F "|" -c $query
    
    if ($results) {
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Top 25 Aadhaar Numbers for Testing" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "OTP for all accounts: 123456" -ForegroundColor Yellow
        Write-Host ""
        Write-Host ("{0,-5} {1,-15} {2,-15} {3,-30} {4,-15} {5,-5} {6,-5} {7,-5}" -f "Rank", "Aadhaar", "Mobile", "Name", "District", "Score", "Docs", "Apps") -ForegroundColor Cyan
        Write-Host ("-" * 120) -ForegroundColor Gray
        
        $aadhaarList = @()
        $results | ForEach-Object {
            if ($_ -match '^\s*\d+') {
                $fields = $_ -split '\|'
                if ($fields.Length -ge 10) {
                    $rank = $fields[0].Trim()
                    $aadhaar = $fields[1].Trim()
                    $mobile = $fields[2].Trim()
                    $name = if ($fields[3].Length -gt 28) { $fields[3].Substring(0, 25) + "..." } else { $fields[3] }
                    $email = $fields[4].Trim()
                    $district = if ($fields[5].Length -gt 13) { $fields[5].Substring(0, 10) + "..." } else { $fields[5] }
                    $profileScore = $fields[6].Trim()
                    $docCount = $fields[7].Trim()
                    $appCount = $fields[8].Trim()
                    $totalScore = $fields[9].Trim()
                    
                    Write-Host ("{0,-5} {1,-15} {2,-15} {3,-30} {4,-15} {5,-5} {6,-5} {7,-5}" -f $rank, $aadhaar, $mobile, $name, $district, $totalScore, $docCount, $appCount) -ForegroundColor White
                    
                    $aadhaarList += $aadhaar
                }
            }
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Aadhaar Numbers List (for easy copy)" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        
        for ($i = 0; $i -lt $aadhaarList.Length; $i++) {
            Write-Host "$($i + 1). $($aadhaarList[$i])" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Summary" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Total Aadhaar numbers found: $($aadhaarList.Length)" -ForegroundColor White
        Write-Host "OTP for all: 123456" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Use these Aadhaar numbers to test the application." -ForegroundColor Green
        Write-Host "All accounts accept OTP: 123456" -ForegroundColor Yellow
        
    } else {
        Write-Host "No citizens found with Aadhaar numbers." -ForegroundColor Red
        Write-Host "Make sure the data migration has been completed." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error querying database: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. PostgreSQL is running" -ForegroundColor White
    Write-Host "2. Database 'smart_citizen' exists" -ForegroundColor White
    Write-Host "3. User '$DatabaseUser' has access" -ForegroundColor White
    Write-Host "4. Data migration has been completed" -ForegroundColor White
    exit 1
}

Write-Host ""

