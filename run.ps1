<#
.SYNOPSIS
    MeoBoost - Windows Performance Optimizer
    One-liner launcher script (similar to WinUtil)

.DESCRIPTION
    Downloads and runs the latest MeoBoost release.
    Usage: irm https://raw.githubusercontent.com/Minhboang11-Meo/meoboost/main/run.ps1 | iex

.NOTES
    Requires Windows 10/11 and Administrator privileges
#>

# ============================================
#  MeoBoost Bootstrapper
# ============================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$AppName = "MeoBoost"
$RepoOwner = "Minhboang11-Meo"
$RepoName = "meoboost"
$InstallDir = "$env:USERPROFILE\.meoboost"
$ExePath = "$InstallDir\MeoBoost.exe"

# Colors
function Write-Header {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║           MeoBoost - Windows Performance Optimizer       ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "  [*] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [✓] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  [✗] $Message" -ForegroundColor Red
}

# Check if running as Administrator
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Get latest release from GitHub
function Get-LatestRelease {
    Write-Step "Fetching latest release..."
    
    $apiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
    
    try {
        $release = Invoke-RestMethod -Uri $apiUrl -Headers @{
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "MeoBoost-Bootstrapper"
        }
        
        $asset = $release.assets | Where-Object { $_.name -like "*.exe" } | Select-Object -First 1
        
        if (-not $asset) {
            throw "No executable found in latest release"
        }
        
        return @{
            Version = $release.tag_name
            DownloadUrl = $asset.browser_download_url
            FileName = $asset.name
        }
    }
    catch {
        throw "Failed to fetch release: $_"
    }
}

# Download the executable
function Get-MeoBoost {
    param([string]$Url, [string]$Version)
    
    Write-Step "Downloading MeoBoost $Version..."
    
    # Create install directory
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
    
    # Download
    try {
        Invoke-WebRequest -Uri $Url -OutFile $ExePath -UseBasicParsing
        Write-Success "Downloaded successfully"
    }
    catch {
        throw "Failed to download: $_"
    }
}

# Check if update is needed
function Test-UpdateRequired {
    param([string]$LatestVersion)
    
    if (-not (Test-Path $ExePath)) {
        return $true
    }
    
    $versionFile = "$InstallDir\version.txt"
    if (-not (Test-Path $versionFile)) {
        return $true
    }
    
    $currentVersion = Get-Content $versionFile -Raw
    return $currentVersion.Trim() -ne $LatestVersion
}

# Save version info
function Save-Version {
    param([string]$Version)
    Set-Content -Path "$InstallDir\version.txt" -Value $Version
}

# Run MeoBoost
function Start-MeoBoost {
    Write-Step "Starting MeoBoost..."
    
    if (-not (Test-Path $ExePath)) {
        throw "Executable not found at $ExePath"
    }
    
    # Run with admin privileges if not already admin
    if (-not (Test-Admin)) {
        Write-Step "Requesting Administrator privileges..."
        Start-Process -FilePath $ExePath -Verb RunAs -Wait
    }
    else {
        Start-Process -FilePath $ExePath -Wait
    }
}

# Main execution
function Main {
    Write-Header
    
    try {
        # Get latest release info
        $release = Get-LatestRelease
        
        # Check if update needed
        if (Test-UpdateRequired -LatestVersion $release.Version) {
            Get-MeoBoost -Url $release.DownloadUrl -Version $release.Version
            Save-Version -Version $release.Version
        }
        else {
            Write-Success "Already up to date ($($release.Version))"
        }
        
        # Run the app
        Start-MeoBoost
        
        Write-Host ""
        Write-Success "MeoBoost closed."
        Write-Host ""
    }
    catch {
        Write-Error $_.Exception.Message
        Write-Host ""
        Write-Host "  Need help? Visit: https://github.com/$RepoOwner/$RepoName/issues" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
}

# Execute
Main
