$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path $PSScriptRoot).Path
Set-Location $repoRoot

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating .venv..."
    py -3.13 -m venv .venv
}

Write-Host "Ensuring Python dependencies are installed..."
& $venvPython -m pip install -r requirements.txt

$nodeHome = "C:\Program Files\nodejs"
$nodeExe = Join-Path $nodeHome "node.exe"
$npmCmd = Join-Path $nodeHome "npm.cmd"

if (-not (Test-Path $nodeExe)) {
    Write-Error "Node.js is not installed at C:\Program Files\nodejs. Install Node LTS first."
    exit 1
}

$backendCmd = "Set-Location '$repoRoot'; `$env:DATABASE_URL='sqlite:///./XR7.db'; `$env:REDIS_URL='redis://localhost:6379/0'; & '$venvPython' -m uvicorn XR7.api.app:app --host 127.0.0.1 --port 8000"
$frontendCmd = "`$env:Path += ';$nodeHome'; Set-Location '$repoRoot\frontend'; & '$npmCmd' run dev"

Write-Host "Starting backend in a new terminal..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Write-Host "Starting frontend in a new terminal..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Opening UI in your browser..."
Start-Process "http://localhost:5173/"

Write-Host "Done."
Write-Host "UI:   http://localhost:5173/"
Write-Host "API:  http://127.0.0.1:8000/docs"
