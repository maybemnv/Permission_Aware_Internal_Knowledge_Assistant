[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it from https://docs.astral.sh/uv/"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js and npm are required."
}

& uv sync
if (-not (Test-Path -LiteralPath (Join-Path $Root "apps\web\node_modules"))) {
    & npm.cmd --prefix (Join-Path $Root "apps\web") ci
}

function Start-Terminal {
    param([string]$Title, [string]$WorkingDirectory, [string]$Command)
    $safeTitle = $Title.Replace("'", "''")
    $safeDirectory = $WorkingDirectory.Replace("'", "''")
    $script = "`$Host.UI.RawUI.WindowTitle = '$safeTitle'; Set-Location -LiteralPath '$safeDirectory'; $Command"
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $script
    )
}

$apiCommand = "`$env:APP_MODE = 'fixture'; `$env:SEARCH_PROVIDER = 'fixture'; `$env:QUEUE_PROVIDER = 'inline'; `$env:MODEL_PROVIDER = 'fixture'; uv run uvicorn apps.api.main:app --host 127.0.0.1 --port 8102"
$webDirectory = Join-Path $Root "apps\web"
Start-Terminal "Knowledge Assistant API" $Root $apiCommand
Start-Terminal "Knowledge Assistant Web" $webDirectory "npm.cmd run dev -- --hostname 127.0.0.1 --port 3102"

Write-Host "Knowledge Assistant starting at http://127.0.0.1:3102"
Write-Host "API health: http://127.0.0.1:8102/health/ready"
