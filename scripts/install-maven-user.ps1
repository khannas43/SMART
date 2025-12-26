# Install Maven on Windows (User Installation - No Admin Required)
# Downloads and installs Apache Maven to user directory

Write-Host "Installing Apache Maven (User Installation)..." -ForegroundColor Cyan

$mavenVersion = "3.9.9"
# Try multiple mirror URLs
$mavenUrls = @(
    "https://archive.apache.org/dist/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip",
    "https://dlcdn.apache.org/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip",
    "https://downloads.apache.org/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip"
)

$installDir = "$env:USERPROFILE\Apache\maven"
$tempFile = "$env:TEMP\apache-maven-$mavenVersion-bin.zip"

# Create install directory
Write-Host "Creating installation directory: $installDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

# Download Maven
Write-Host "Downloading Maven $mavenVersion..." -ForegroundColor Yellow
$downloadSuccess = $false
foreach ($mavenUrl in $mavenUrls) {
    try {
        Write-Host "  Trying: $mavenUrl" -ForegroundColor Gray
        Invoke-WebRequest -Uri $mavenUrl -OutFile $tempFile -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✅ Download complete!" -ForegroundColor Green
        $downloadSuccess = $true
        break
    } catch {
        Write-Host "  ❌ Failed: $_" -ForegroundColor Red
        continue
    }
}

if (-not $downloadSuccess) {
    Write-Host "`n❌ Failed to download Maven from all mirrors" -ForegroundColor Red
    Write-Host "Please download manually from:" -ForegroundColor Yellow
    Write-Host "https://maven.apache.org/download.cgi" -ForegroundColor Cyan
    Write-Host "`nExtract to: $installDir" -ForegroundColor Yellow
    exit 1
}

# Extract Maven
Write-Host "Extracting Maven..." -ForegroundColor Yellow
$extractDir = "$env:TEMP\maven-extract"
Remove-Item -Path $extractDir -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -Path $tempFile -DestinationPath $extractDir -Force
$extractedDir = Get-ChildItem $extractDir | Where-Object { $_.Name -like "apache-maven-*" } | Select-Object -First 1

if (-not $extractedDir) {
    Write-Host "❌ Failed to extract Maven" -ForegroundColor Red
    exit 1
}

Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item -Path "$($extractedDir.FullName)\*" -Destination $installDir -Recurse -Force

# Set user environment variables
Write-Host "Setting user environment variables..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable("MAVEN_HOME", $installDir, [System.EnvironmentVariableTarget]::User)
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)
if ($currentPath -notlike "*$installDir\bin*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir\bin", [System.EnvironmentVariableTarget]::User)
}

Write-Host "`n✅ Maven installed successfully!" -ForegroundColor Green
Write-Host "Installation directory: $installDir" -ForegroundColor Gray

# Add to current session
$env:MAVEN_HOME = $installDir
$env:Path += ";$installDir\bin"

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Cyan
try {
    $mvnVersion = & "$installDir\bin\mvn.cmd" --version 2>&1 | Select-Object -First 1
    if ($mvnVersion) {
        Write-Host "✅ $mvnVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Maven installed but verification failed" -ForegroundColor Yellow
}

Write-Host "`n⚠️  Please restart your terminal for Maven to be available in new sessions." -ForegroundColor Yellow
Write-Host "For current session, Maven is now available." -ForegroundColor Green

# Cleanup
Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
Remove-Item -Path $extractDir -Recurse -Force -ErrorAction SilentlyContinue

