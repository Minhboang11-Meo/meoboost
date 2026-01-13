<#
.SYNOPSIS
    MeoBoost - Windows Performance Optimizer
    Official launcher script for downloading and running MeoBoost

.DESCRIPTION
    This script downloads the latest MeoBoost release from GitHub
    and runs it with appropriate permissions.
    
    MeoBoost is an open-source Windows optimization tool.
    Source code: https://github.com/Minhboang11-Meo/meoboost

.NOTES
    - Requires Windows 10/11
    - Administrator privileges required for system tweaks
    - All downloads are from official GitHub releases only

.LINK
    https://github.com/Minhboang11-Meo/meoboost
#>

# ============================================
#  MeoBoost Launcher Script
#  Version: 1.1.0
#  License: MIT
# ============================================

# Strict mode for safety
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Application Configuration
$script:AppName = "MeoBoost"
$script:GitHubOwner = "Minhboang11-Meo"
$script:GitHubRepo = "meoboost"
$script:InstallDirectory = Join-Path $env:USERPROFILE ".meoboost"
$script:ExecutablePath = Join-Path $script:InstallDirectory "MeoBoost.exe"
$script:VersionFilePath = Join-Path $script:InstallDirectory "version.txt"

# Display branded header
function Show-ApplicationHeader {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║           MeoBoost - Windows Performance Optimizer       ║" -ForegroundColor Cyan
    Write-Host "  ║              https://github.com/$script:GitHubOwner/$script:GitHubRepo            ║" -ForegroundColor DarkCyan
    Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# Output helper functions
function Write-StatusMessage {
    param([string]$Message)
    Write-Host "  [*] $Message" -ForegroundColor Yellow
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "  [ERROR] $Message" -ForegroundColor Red
}

# Check if current session has administrator privileges
function Test-AdministratorPrivileges {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Fetch latest release information from GitHub API
function Get-LatestReleaseInfo {
    Write-StatusMessage "Checking for latest release..."
    
    $apiEndpoint = "https://api.github.com/repos/$script:GitHubOwner/$script:GitHubRepo/releases/latest"
    
    $response = Invoke-RestMethod -Uri $apiEndpoint -Method Get -Headers @{
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "MeoBoost-Launcher/1.1"
    }
    
    # Find the executable asset in the release
    $executableAsset = $response.assets | Where-Object { $_.name -match '\.exe$' } | Select-Object -First 1
    
    if ($null -eq $executableAsset) {
        throw "No executable file found in the latest release"
    }
    
    return @{
        TagName = $response.tag_name
        DownloadUrl = $executableAsset.browser_download_url
        AssetName = $executableAsset.name
        AssetSize = $executableAsset.size
    }
}

# Download MeoBoost executable from GitHub
function Install-MeoBoostExecutable {
    param(
        [Parameter(Mandatory)]
        [string]$DownloadUrl,
        
        [Parameter(Mandatory)]
        [string]$Version
    )
    
    Write-StatusMessage "Downloading MeoBoost $Version..."
    
    # Ensure install directory exists
    if (-not (Test-Path $script:InstallDirectory)) {
        New-Item -ItemType Directory -Path $script:InstallDirectory -Force | Out-Null
        Write-StatusMessage "Created directory: $script:InstallDirectory"
    }
    
    # Download the executable
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $script:ExecutablePath -UseBasicParsing
    
    # Verify file was downloaded
    if (-not (Test-Path $script:ExecutablePath)) {
        throw "Download failed - file not found after download"
    }
    
    $fileInfo = Get-Item $script:ExecutablePath
    Write-SuccessMessage "Downloaded successfully ($([math]::Round($fileInfo.Length / 1MB, 2)) MB)"
}

# Check if an update is available
function Test-UpdateAvailable {
    param(
        [Parameter(Mandatory)]
        [string]$LatestVersion
    )
    
    # Check if executable exists
    if (-not (Test-Path $script:ExecutablePath)) {
        return $true
    }
    
    # Check if version file exists
    if (-not (Test-Path $script:VersionFilePath)) {
        return $true
    }
    
    # Compare versions
    $installedVersion = (Get-Content $script:VersionFilePath -Raw).Trim()
    return $installedVersion -ne $LatestVersion
}

# Save installed version to file
function Save-InstalledVersion {
    param(
        [Parameter(Mandatory)]
        [string]$Version
    )
    Set-Content -Path $script:VersionFilePath -Value $Version -NoNewline
}

# Launch MeoBoost application
function Start-MeoBoostApplication {
    Write-StatusMessage "Launching MeoBoost..."
    
    if (-not (Test-Path $script:ExecutablePath)) {
        throw "Application not found at: $script:ExecutablePath"
    }
    
    # Launch with appropriate privileges
    if (Test-AdministratorPrivileges) {
        # Already running as admin
        Start-Process -FilePath $script:ExecutablePath -Wait
    }
    else {
        # Request elevation
        Write-StatusMessage "Requesting administrator privileges..."
        Start-Process -FilePath $script:ExecutablePath -Verb RunAs -Wait
    }
}

# Main entry point
function Invoke-MeoBoostLauncher {
    Show-ApplicationHeader
    
    try {
        # Fetch latest release from GitHub
        $releaseInfo = Get-LatestReleaseInfo
        
        # Download if update available or not installed
        if (Test-UpdateAvailable -LatestVersion $releaseInfo.TagName) {
            Install-MeoBoostExecutable -DownloadUrl $releaseInfo.DownloadUrl -Version $releaseInfo.TagName
            Save-InstalledVersion -Version $releaseInfo.TagName
            Write-SuccessMessage "Installed version: $($releaseInfo.TagName)"
        }
        else {
            Write-SuccessMessage "Already running latest version ($($releaseInfo.TagName))"
        }
        
        # Launch the application
        Start-MeoBoostApplication
        
        Write-Host ""
        Write-SuccessMessage "MeoBoost session ended."
        Write-Host ""
    }
    catch {
        Write-ErrorMessage $_.Exception.Message
        Write-Host ""
        Write-Host "  For support, please visit:" -ForegroundColor Gray
        Write-Host "  https://github.com/$script:GitHubOwner/$script:GitHubRepo/issues" -ForegroundColor Cyan
        Write-Host ""
        exit 1
    }
}

# Execute the launcher
Invoke-MeoBoostLauncher
