# Install Maven on Windows
# Downloads and installs Apache Maven

Write-Host "Installing Apache Maven..." -ForegroundColor Cyan

$mavenVersion = "3.9.9"
$mavenUrl = "https://downloads.apache.org/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip"
$installDir = "C:\Program Files\Apache\maven"
$tempFile = "$env:TEMP\apache-maven-$mavenVersion-bin.zip"

# Create install directory
Write-Host "Creating installation directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

# Download Maven
Write-Host "Downloading Maven $mavenVersion..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $mavenUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "Failed to download Maven: $_" -ForegroundColor Red
    exit 1
}

# Extract Maven
Write-Host "Extracting Maven..." -ForegroundColor Yellow
Expand-Archive -Path $tempFile -DestinationPath "$env:TEMP\maven-extract" -Force
$extractedDir = Get-ChildItem "$env:TEMP\maven-extract" | Where-Object { $_.Name -like "apache-maven-*" } | Select-Object -First 1
Copy-Item -Path "$($extractedDir.FullName)\*" -Destination $installDir -Recurse -Force

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable("MAVEN_HOME", $installDir, [System.EnvironmentVariableTarget]::Machine)
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
if ($currentPath -notlike "*$installDir\bin*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir\bin", [System.EnvironmentVariableTarget]::Machine)
}

Write-Host "Maven installed successfully!" -ForegroundColor Green
Write-Host "Installation directory: $installDir" -ForegroundColor Gray
Write-Host "Please restart your terminal/PowerShell for changes to take effect." -ForegroundColor Yellow
Write-Host "Or run: `$env:Path += ';$installDir\bin'" -ForegroundColor Yellow

# Cleanup
Remove-Item -Path $tempFile -Force
Remove-Item -Path "$env:TEMP\maven-extract" -Recurse -Force

Write-Host "`nVerifying installation..." -ForegroundColor Cyan
$env:Path += ";$installDir\bin"
$mvnVersion = & "$installDir\bin\mvn.cmd" --version 2>&1 | Select-Object -First 1
if ($mvnVersion) {
    Write-Host "✅ $mvnVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Maven installed but not in current session PATH" -ForegroundColor Yellow
}

