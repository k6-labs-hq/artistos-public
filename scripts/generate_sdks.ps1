# PowerShell script to generate both SDKs
$ErrorActionPreference = "Stop"

$ROOT_DIR = (Get-Item $PSScriptRoot).Parent.FullName

Write-Host "🚀 Generating all SDKs..." -ForegroundColor Cyan

# Export OpenAPI spec first
Write-Host "`n1️⃣ Exporting OpenAPI spec..." -ForegroundColor Yellow
& "$ROOT_DIR\.venv\Scripts\python.exe" "$ROOT_DIR\scripts\export_openapi.py"

# Add examples to the spec
Write-Host "`n2️⃣ Adding examples to OpenAPI spec..." -ForegroundColor Yellow
& "$ROOT_DIR\.venv\Scripts\python.exe" "$ROOT_DIR\scripts\add_openapi_examples.py"

# Generate Python SDK
Write-Host "`n3️⃣ Generating Python SDK..." -ForegroundColor Yellow
& "$ROOT_DIR\scripts\generate_sdk_python.ps1"

# Generate TypeScript SDK
Write-Host "`n4️⃣ Generating TypeScript SDK..." -ForegroundColor Yellow
& "$ROOT_DIR\scripts\generate_sdk_typescript.ps1"

Write-Host "`n✅ All SDKs generated under $ROOT_DIR\sdk" -ForegroundColor Green
