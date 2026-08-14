param(
    [string]$Message = "chore: update AI CV Analyzer"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "AI CV Analyzer - Portfolio Publisher" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Git repository not found." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py not found." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt not found." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".gitignore")) {
    Write-Host "ERROR: .gitignore not found." -ForegroundColor Red
    exit 1
}

Write-Host "[1/6] Checking sensitive files..." -ForegroundColor Yellow

$ignoredEnv = git check-ignore .env 2>$null

if ($ignoredEnv -ne ".env") {
    Write-Host "ERROR: .env is not protected by .gitignore." -ForegroundColor Red
    exit 1
}

$trackedSensitiveFiles = git ls-files |
    Where-Object {
        $_ -eq ".env" -or
        $_ -like "venv/*" -or
        $_ -like ".venv/*"
    }

if ($trackedSensitiveFiles) {
    Write-Host "ERROR: Sensitive files are tracked by Git:" -ForegroundColor Red
    $trackedSensitiveFiles | ForEach-Object {
        Write-Host " - $_" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Security check passed." -ForegroundColor Green

Write-Host "[2/6] Checking Python syntax..." -ForegroundColor Yellow
python -m py_compile app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python syntax check failed." -ForegroundColor Red
    exit 1
}

Write-Host "Python syntax check passed." -ForegroundColor Green

Write-Host "[3/6] Updating requirements.txt..." -ForegroundColor Yellow
python -m pip freeze | Set-Content requirements.txt

Write-Host "[4/6] Adding safe project files..." -ForegroundColor Yellow
git add .

$stagedFiles = git diff --cached --name-only

if (-not $stagedFiles) {
    Write-Host "No changes to publish." -ForegroundColor DarkYellow
    exit 0
}

Write-Host "Files ready for commit:" -ForegroundColor Cyan
$stagedFiles | ForEach-Object {
    Write-Host " - $_"
}

Write-Host "[5/6] Creating Git commit..." -ForegroundColor Yellow
git commit -m $Message

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Git commit failed." -ForegroundColor Red
    exit 1
}

Write-Host "[6/6] Pushing to GitHub..." -ForegroundColor Yellow

$remote = git remote get-url origin 2>$null

if (-not $remote) {
    Write-Host "Commit created locally." -ForegroundColor Green
    Write-Host "GitHub remote 'origin' is not configured yet." -ForegroundColor DarkYellow
    exit 0
}

git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: GitHub push failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Project published successfully." -ForegroundColor Green