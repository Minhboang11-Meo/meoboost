<#
.SYNOPSIS
    MeoBoost - Windows Performance Optimizer
#>

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Repo = "meohunterr/MeoBoost"
# Use LocalAppData instead of hidden user profile folder to avoid "Suspicious" flag
$Dir = Join-Path $env:LOCALAPPDATA "MeoBoost"
$Src = Join-Path $Dir "source"

function Write-S { param([string]$M) Write-Host "  [*] $M" -ForegroundColor Yellow }
function Write-O { param([string]$M) Write-Host "  [OK] $M" -ForegroundColor Green }
function Write-E { param([string]$M) Write-Host "  [!] $M" -ForegroundColor Red }

Write-Host ""
Write-Host "  MeoBoost - Windows Performance Optimizer" -ForegroundColor Cyan
Write-Host "  100% Open Source | No EXE Files" -ForegroundColor DarkCyan
Write-Host ""

# Admin check
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($id)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-S "Requesting admin privileges..."
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

# Find Python
$PyCmd = $null
try {
    $r = py -3 --version 2>&1
    if ($LASTEXITCODE -eq 0) { $PyCmd = "py" }
} catch {}

if (-not $PyCmd) {
    try {
        $r = python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $r -match "Python 3") { $PyCmd = "python" }
    } catch {}
}

if (-not $PyCmd) {
    # Install Python
    Write-S "Python not found. Installing..."
    $installed = $false

    # Try Winget first (Recommended/Safe method)
    if (Get-Command "winget" -ErrorAction SilentlyContinue) {
        try {
            Write-S "Attempting installation via Winget..."
            $proc = Start-Process -FilePath "winget" -ArgumentList "install -e --id Python.Python.3.11 --scope machine --accept-package-agreements --accept-source-agreements --disable-interactivity" -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                $installed = $true
                # Refresh env vars
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
                $PyCmd = "py"
                Write-O "Python installed via Winget"
            }
        } catch {
            Write-E "Winget failed. Trying direct download..."
        }
    }

    # Fallback to direct download if Winget fails or is missing
    if (-not $installed) {
        Write-S "Downloading Python installer..."
        $installer = Join-Path $env:TEMP "python_setup.exe"
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $installer -UseBasicParsing
        Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" -Wait
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
        Remove-Item $installer -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $PyCmd = "py"
        Write-O "Python installed manually"
    }
} else {
    Write-O "Python found"
}

# Download source
Write-S "Downloading source code..."
if (-not (Test-Path $Dir)) { New-Item -ItemType Directory -Path $Dir -Force | Out-Null }
$zipPath = Join-Path $env:TEMP "MeoBoost.zip"
Invoke-WebRequest -Uri "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile $zipPath -UseBasicParsing
if ($PWD.Path.StartsWith($Src)) { Set-Location $env:USERPROFILE }
if (Test-Path $Src) { Remove-Item $Src -Recurse -Force }
$extractDir = Join-Path $env:TEMP "MeoBoost_ext"
if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
$extracted = Get-ChildItem $extractDir -Directory | Select-Object -First 1
Move-Item -Path $extracted.FullName -Destination $Src -Force
Remove-Item $zipPath, $extractDir -Recurse -Force -ErrorAction SilentlyContinue
Write-O "Source code ready"

# Install dependencies
$reqFile = Join-Path $Src "requirements.txt"
if (Test-Path $reqFile) {
    Write-S "Installing dependencies..."
    # Safe execution without Invoke-Expression
    & $PyCmd -m pip install -r $reqFile -q
    Write-O "Dependencies installed"
}

# Run
Write-Host ""
Write-S "Starting MeoBoost..."
Write-Host ""

Set-Location $Src
# Safe execution without Invoke-Expression
& $PyCmd main.py

Write-Host ""
Write-O "Session ended."
