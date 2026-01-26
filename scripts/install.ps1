# Kin Code Installation Script for Windows
# Usage: irm https://raw.githubusercontent.com/kinra-ai/kin-code/main/scripts/install.ps1 | iex

$ErrorActionPreference = "Stop"

function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Err { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warn { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }

function Show-Banner {
    Write-Host ""
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host "████  ██████  ████░░" -ForegroundColor Cyan
    Write-Host "████    ██    ████░░" -ForegroundColor Cyan
    Write-Host "████          ████░░" -ForegroundColor Cyan
    Write-Host "████  ██  ██  ████░░" -ForegroundColor Cyan
    Write-Host "██      ██      ██░░" -ForegroundColor Cyan
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Starting Kin Code installation..." -ForegroundColor Cyan
    Write-Host ""
}

function Test-UvInstalled {
    try {
        $null = Get-Command uv -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Install-Uv {
    Write-Info "Installing uv using the official Astral installer..."
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        # Refresh PATH for current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        if (-not (Test-UvInstalled)) {
            Write-Warn "uv was installed but not found in PATH for this session"
            Write-Warn "You may need to restart your terminal"
        } else {
            Write-Success "uv installed successfully"
        }
    } catch {
        Write-Err "Failed to install uv: $_"
        exit 1
    }
}

function Install-KinCode {
    Write-Info "Installing kin-code using uv..."
    try {
        uv tool install kin-code
        Write-Success "Kin Code installed successfully!"
    } catch {
        Write-Err "Failed to install kin-code: $_"
        exit 1
    }
}

function Test-KinInstalled {
    try {
        $null = Get-Command kin -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Main {
    Show-Banner

    # Check if uv is installed
    if (Test-UvInstalled) {
        $uvVersion = (uv --version) -join " "
        Write-Info "uv is already installed: $uvVersion"
    } else {
        Write-Info "uv is not installed"
        Install-Uv
    }

    # Install kin-code
    Install-KinCode

    # Refresh PATH again after tool install
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

    # Verify installation
    if (Test-KinInstalled) {
        Write-Success "Installation completed successfully!"
        Write-Host ""
        Write-Host "You can now run kin with:" -ForegroundColor Cyan
        Write-Host "  kin"
        Write-Host ""
        Write-Host "Or for ACP mode:" -ForegroundColor Cyan
        Write-Host "  kin-acp"
    } else {
        Write-Warn "Installation completed but 'kin' command not found in current session"
        Write-Warn "Please restart your terminal and try running 'kin'"
    }
}

Main
