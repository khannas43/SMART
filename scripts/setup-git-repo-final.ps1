# Setup Git Repository for SMART Platform
# Initializes Git repository and connects to GitHub

Write-Host "Setting up Git repository..." -ForegroundColor Cyan

$repoUrl = "https://github.com/khannas43/SMART.git"
$currentDir = Get-Location

# Check if Git is installed
Write-Host "Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "✅ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "  Download from: https://git-scm.com/download/win" -ForegroundColor Cyan
    exit 1
}

# Check if already a git repository
if (Test-Path ".git") {
    Write-Host "`n⚠️  This directory is already a Git repository" -ForegroundColor Yellow
    Write-Host "Checking remote configuration..." -ForegroundColor Yellow
    
    try {
        $remoteUrl = git remote get-url origin 2>&1
        Write-Host "Current remote: $remoteUrl" -ForegroundColor Gray
        
        if ($remoteUrl -like "*khannas43/SMART*") {
            Write-Host "✅ Remote is already configured correctly!" -ForegroundColor Green
        } else {
            Write-Host "Updating remote URL..." -ForegroundColor Yellow
            git remote set-url origin $repoUrl
            Write-Host "✅ Remote URL updated!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Adding remote origin..." -ForegroundColor Yellow
        git remote add origin $repoUrl
        Write-Host "✅ Remote added!" -ForegroundColor Green
    }
} else {
    Write-Host "`nInitializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Repository initialized!" -ForegroundColor Green
    
    Write-Host "Adding remote origin..." -ForegroundColor Yellow
    git remote add origin $repoUrl
    Write-Host "✅ Remote added: $repoUrl" -ForegroundColor Green
}

# Check if .gitignore exists
if (-not (Test-Path ".gitignore")) {
    Write-Host "`n⚠️  .gitignore not found. Creating default .gitignore..." -ForegroundColor Yellow
    # Basic .gitignore content
    $gitignoreContent = @"
# Dependencies
node_modules/
target/
build/
dist/

# IDE
.idea/
.vscode/
*.iml

# Environment
.env
.env.local

# Logs
*.log
"@
    $gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore created!" -ForegroundColor Green
}

Write-Host "`n📋 Git Repository Status:" -ForegroundColor Cyan
Write-Host "  Repository: $repoUrl" -ForegroundColor Gray
Write-Host "  Location: $currentDir" -ForegroundColor Gray

Write-Host "`n✅ Git repository setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure Git user (if not already)" -ForegroundColor Gray
Write-Host "  2. Stage files: git add ." -ForegroundColor Gray
Write-Host "  3. Commit: git commit -m Initial-commit" -ForegroundColor Gray
Write-Host "  4. Push: git push -u origin main" -ForegroundColor Gray

