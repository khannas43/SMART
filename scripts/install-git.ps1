# Install Git on Windows
# Downloads and runs Git installer

Write-Host "Installing Git..." -ForegroundColor Cyan

$gitInstallerUrl = "https://github.com/git-for-windows/git/releases/download/v2.46.0.windows.1/Git-2.46.0-64-bit.exe"
$tempFile = "$env:TEMP\Git-Installer.exe"

# Download Git installer
Write-Host "Downloading Git installer..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $gitInstallerUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "Failed to download Git: $_" -ForegroundColor Red
    Write-Host "Alternative: Download manually from https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nStarting Git installer..." -ForegroundColor Yellow
Write-Host "Please complete the installation wizard." -ForegroundColor Yellow
Write-Host "After installation, restart your terminal and run the Git setup script." -ForegroundColor Yellow

# Run installer silently
Start-Process -FilePath $tempFile -ArgumentList "/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS" -Wait

Write-Host "`nGit installation completed!" -ForegroundColor Green
Write-Host "Please restart your terminal for Git to be available." -ForegroundColor Yellow

