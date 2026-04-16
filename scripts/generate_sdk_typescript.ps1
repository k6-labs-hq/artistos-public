# PowerShell script to generate TypeScript SDK from OpenAPI spec
$ErrorActionPreference = "Stop"

$ROOT_DIR = (Get-Item $PSScriptRoot).Parent.FullName
$SPEC_PATH = Join-Path $ROOT_DIR "openapi\openapi.json"
$OUT_DIR = Join-Path $ROOT_DIR "sdk\typescript"

if (-not (Test-Path $SPEC_PATH)) {
    Write-Error "OpenAPI spec not found at $SPEC_PATH. Run: python scripts\export_openapi.py"
    exit 1
}

New-Item -ItemType Directory -Force -Path $OUT_DIR | Out-Null

Write-Host "Generating TypeScript SDK from $SPEC_PATH..." -ForegroundColor Cyan

# Use Node.js from standard Windows install location
$nodeHome = "C:\Program Files\nodejs"
$npmCmd = Join-Path $nodeHome "npm.cmd"

if (-not (Test-Path $npmCmd)) {
    Write-Error "npm not found at $npmCmd. Please install Node.js LTS."
    exit 1
}

$env:Path += ";$nodeHome"

Write-Host "Using npm to run openapi-generator-cli..." -ForegroundColor Yellow
& $npmCmd exec -y -- @openapitools/openapi-generator-cli generate `
    -i $SPEC_PATH `
    -g typescript-fetch `
    -o $OUT_DIR `
    --additional-properties=npmName=@xr7/sdk,npmVersion=2.0.0,supportsES6=true

Write-Host "✅ Generated TypeScript SDK at $OUT_DIR" -ForegroundColor Green
