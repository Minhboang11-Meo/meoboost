<#
.SYNOPSIS
    MeoBoost - Windows Performance Optimizer
    Official launcher script for downloading and running MeoBoost from source

.DESCRIPTION
    This script:
    1. Checks if Python is installed, installs it automatically if not
    2. Downloads MeoBoost source code from GitHub
    3. Installs required dependencies
    4. Runs MeoBoost directly from Python source
    
    No compiled EXE files - 100% transparent, open-source code.

.LINK
    https://github.com/Minhboang11-Meo/meoboost
#>

# ============================================
#  MeoBoost Launcher Script
#  Version: 2.1.0
#  License: GPL-3.0
# ============================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$script:AppName = "MeoBoost"
$script:GitHubRepo = "Minhboang11-Meo/meoboost"
$script:InstallDir = Join-Path $env:USERPROFILE ".meoboost"
$script:SourceDir = Join-Path $script:InstallDir "source"
$script:VersionFile = Join-Path $script:InstallDir "version.txt"

# Display header
function Show-Header {
    Write-Host ""
    Write-Host "  MeoBoost - Windows Performance Optimizer" -ForegroundColor Cyan
    Write-Host "  100% Open Source | No EXE Files" -ForegroundColor DarkCyan
    Write-Host ""
}

function Write-Status { param([string]$M) Write-Host "  [*] $M" -ForegroundColor Yellow }
function Write-OK { param([string]$M) Write-Host "  [OK] $M" -ForegroundColor Green }
function Write-Err { param([string]$M) Write-Host "  [!] $M" -ForegroundColor Red }

# Check admin privileges
function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Request admin if needed
function Request-Admin {
    if (-not (Test-Admin)) {
        Write-Status "Requesting administrator privileges..."
        Start-Process powershell.exe -Verb RunAs -ArgumentList @(
            "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            "irm https://raw.githubusercontent.com/$script:GitHubRepo/main/run.ps1 | iex"
        )
        exit
    }
}

# Find Python installation
function Find-Python {
    # Method 1: Check py launcher (most reliable on Windows)
    try {
        $result = & py -3 --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 8 -and $minor -le 12) {
                return @{ Cmd = "py"; Args = @("-3"); Version = "$major.$minor" }
            }
        }
    } catch {}
    
    # Method 2: Check PATH
    $cmds = @("python3", "python")
    foreach ($cmd in $cmds) {
        try {
            $result = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $result -match "Python (\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -eq 3 -and $minor -ge 8 -and $minor -le 12) {
                    return @{ Cmd = $cmd; Args = @(); Version = "$major.$minor" }
                }
            }
        } catch {}
    }
    
    # Method 3: Check common install paths
    $paths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python38\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe"
    )
    
    foreach ($p in $paths) {
        if (Test-Path $p) {
            try {
                $result = & $p --version 2>&1
                if ($result -match "Python (\d+)\.(\d+)") {
                    return @{ Cmd = $p; Args = @(); Version = "$($Matches[1]).$($Matches[2])" }
                }
            } catch {}
        }
    }
    
    return $null
}

# Install Python
function Install-Python {
    Write-Status "Python 3.8-3.12 not found. Installing Python 3.11..."
    
    $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $installer = Join-Path $env:TEMP "python_setup.exe"
    
    # Download
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
    Write-OK "Downloaded Python installer"
    
    # Install silently with PATH
    Write-Status "Installing Python..."
    $proc = Start-Process -FilePath $installer -ArgumentList @(
        "/quiet", "InstallAllUsers=0", "PrependPath=1", 
        "Include_test=0", "Include_doc=0", "Include_pip=1"
    ) -Wait -PassThru
    
    if ($proc.ExitCode -ne 0) {
        throw "Python installation failed"
    }
    
    # Refresh PATH
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + 
                [Environment]::GetEnvironmentVariable("Path", "User")
    
    Remove-Item $installer -Force -ErrorAction SilentlyContinue
    
    # Wait and verify
    Start-Sleep -Seconds 2
    $py = Find-Python
    if ($null -eq $py) {
        throw "Python installed but not accessible. Please restart PowerShell."
    }
    
    Write-OK "Python $($py.Version) installed"
    return $py
}

# Download source code
function Get-Source {
    Write-Status "Downloading source code..."
    
    # Create directories
    if (-not (Test-Path $script:InstallDir)) {
        New-Item -ItemType Directory -Path $script:InstallDir -Force | Out-Null
    }
    
    # Download ZIP directly (not through API to avoid redirect)
    $zipUrl = "https://github.com/$script:GitHubRepo/archive/refs/heads/main.zip"
    $zipPath = Join-Path $env:TEMP "meoboost.zip"
    
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
    
    # Clean old source
    if (Test-Path $script:SourceDir) {
        Remove-Item $script:SourceDir -Recurse -Force
    }
    
    # Extract
    $extractDir = Join-Path $env:TEMP "meoboost_extract"
    if (Test-Path $extractDir) {
        Remove-Item $extractDir -Recurse -Force
    }
    
    Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
    
    # Move extracted folder
    $extracted = Get-ChildItem $extractDir -Directory | Select-Object -First 1
    Move-Item -Path $extracted.FullName -Destination $script:SourceDir -Force
    
    # Cleanup
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-OK "Source code ready"
}

# Install pip dependencies
function Install-Deps {
    param($Python)
    
    $req = Join-Path $script:SourceDir "requirements.txt"
    if (-not (Test-Path $req)) { return }
    
    Write-Status "Installing dependencies..."
    
    $allArgs = $Python.Args + @("-m", "pip", "install", "-r", $req, "-q")
    & $Python.Cmd @allArgs 2>&1 | Out-Null
    
    Write-OK "Dependencies installed"
}

# Run MeoBoost
function Start-MeoBoost {
    param($Python)
    
    $main = Join-Path $script:SourceDir "main.py"
    if (-not (Test-Path $main)) {
        throw "main.py not found"
    }
    
    Write-Host ""
    Write-Status "Starting MeoBoost..."
    Write-Host ""
    
    Push-Location $script:SourceDir
    try {
        $allArgs = $Python.Args + @($main)
        & $Python.Cmd @allArgs
    }
    finally {
        Pop-Location
    }
}

# Main
function Main {
    Show-Header
    
    try {
        Request-Admin
        
        # Find or install Python
        $py = Find-Python
        if ($null -eq $py) {
            $py = Install-Python
        } else {
            Write-OK "Python $($py.Version) found"
        }
        
        # Download source
        Get-Source
        
        # Install dependencies
        Install-Deps -Python $py
        
        # Run
        Start-MeoBoost -Python $py
        
        Write-Host ""
        Write-OK "MeoBoost session ended."
    }
    catch {
        Write-Err $_.Exception.Message
        Write-Host ""
        Write-Host "  Support: https://github.com/$script:GitHubRepo/issues" -ForegroundColor Gray
        Read-Host "  Press Enter to exit"
        exit 1
    }
}

Main
