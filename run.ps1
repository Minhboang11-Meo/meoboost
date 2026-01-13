<#
.SYNOPSIS
    MeoBoost - Windows Performance Optimizer
    One-liner launcher script

.LINK
    https://github.com/Minhboang11-Meo/meoboost
#>

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Config
$script:Repo = "Minhboang11-Meo/meoboost"
$script:Dir = Join-Path $env:USERPROFILE ".meoboost"
$script:Src = Join-Path $script:Dir "source"

# Output helpers
function Write-S { param([string]$M) Write-Host "  [*] $M" -ForegroundColor Yellow }
function Write-O { param([string]$M) Write-Host "  [OK] $M" -ForegroundColor Green }
function Write-E { param([string]$M) Write-Host "  [!] $M" -ForegroundColor Red }

# Header
function Show-H {
    Write-Host ""
    Write-Host "  MeoBoost - Windows Performance Optimizer" -ForegroundColor Cyan
    Write-Host "  100% Open Source | No EXE Files" -ForegroundColor DarkCyan
    Write-Host ""
}

# Admin check
function Test-A {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Request admin
function Get-A {
    if (-not (Test-A)) {
        Write-S "Requesting admin privileges..."
        Start-Process powershell -Verb RunAs -ArgumentList @(
            "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            "irm https://raw.githubusercontent.com/$script:Repo/main/run.ps1 | iex"
        )
        exit
    }
}

# Find Python - returns path to python.exe or $null
function Find-Py {
    # Try py launcher first (most reliable)
    try {
        $r = py -3 --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $r -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 8 -and $minor -le 12) {
                return "py"
            }
        }
    } catch {}
    
    # Try python command
    try {
        $r = python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $r -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 8 -and $minor -le 12) {
                return "python"
            }
        }
    } catch {}
    
    # Check common paths
    $paths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Python311\python.exe",
        "C:\Python312\python.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    
    return $null
}

# Install Python
function Install-Py {
    Write-S "Python not found. Installing Python 3.11..."
    
    $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $ins = Join-Path $env:TEMP "py_setup.exe"
    
    Invoke-WebRequest -Uri $url -OutFile $ins -UseBasicParsing
    Write-O "Downloaded Python installer"
    
    Write-S "Installing Python..."
    Start-Process -FilePath $ins -ArgumentList @(
        "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1"
    ) -Wait
    
    # Refresh PATH
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + 
                [Environment]::GetEnvironmentVariable("Path", "User")
    
    Remove-Item $ins -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    $py = Find-Py
    if (-not $py) {
        throw "Python installed but not found. Restart PowerShell and try again."
    }
    
    Write-O "Python installed"
    return $py
}

# Download source
function Get-Src {
    Write-S "Downloading source code..."
    
    if (-not (Test-Path $script:Dir)) {
        New-Item -ItemType Directory -Path $script:Dir -Force | Out-Null
    }
    
    $zip = Join-Path $env:TEMP "meoboost.zip"
    $url = "https://github.com/$script:Repo/archive/refs/heads/main.zip"
    
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    
    if (Test-Path $script:Src) {
        Remove-Item $script:Src -Recurse -Force
    }
    
    $ext = Join-Path $env:TEMP "meoboost_ext"
    if (Test-Path $ext) { Remove-Item $ext -Recurse -Force }
    
    Expand-Archive -Path $zip -DestinationPath $ext -Force
    
    $folder = Get-ChildItem $ext -Directory | Select-Object -First 1
    Move-Item -Path $folder.FullName -Destination $script:Src -Force
    
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Remove-Item $ext -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-O "Source code ready"
}

# Install deps
function Install-Deps {
    param([string]$Py)
    
    $req = Join-Path $script:Src "requirements.txt"
    if (-not (Test-Path $req)) { return }
    
    Write-S "Installing dependencies..."
    
    if ($Py -eq "py") {
        & py -3 -m pip install -r $req -q 2>&1 | Out-Null
    } else {
        & $Py -m pip install -r $req -q 2>&1 | Out-Null
    }
    
    Write-O "Dependencies installed"
}

# Run app
function Start-App {
    param([string]$Py)
    
    $main = Join-Path $script:Src "main.py"
    if (-not (Test-Path $main)) {
        throw "main.py not found at $main"
    }
    
    Write-Host ""
    Write-S "Starting MeoBoost..."
    Write-Host ""
    
    Push-Location $script:Src
    try {
        if ($Py -eq "py") {
            & py -3 $main
        } else {
            & $Py $main
        }
    }
    finally {
        Pop-Location
    }
}

# Main
function Main {
    Show-H
    
    try {
        Get-A
        
        $py = Find-Py
        if (-not $py) {
            $py = Install-Py
        } else {
            Write-O "Python found"
        }
        
        Get-Src
        Install-Deps -Py $py
        Start-App -Py $py
        
        Write-Host ""
        Write-O "Session ended."
    }
    catch {
        Write-E $_.Exception.Message
        Write-Host ""
        Write-Host "  Support: https://github.com/$script:Repo/issues" -ForegroundColor Gray
        Read-Host "  Press Enter to exit"
        exit 1
    }
}

Main
