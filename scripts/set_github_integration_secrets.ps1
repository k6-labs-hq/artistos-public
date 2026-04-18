$ErrorActionPreference = "Stop"

param(
    [string]$Repo = "k6-labs-hq/ArtistOS",
    [string]$EnvFile,
    [switch]$DryRun
)

$secretNames = @(
    "ASCAP_API_KEY",
    "BMI_API_KEY",
    "SESAC_API_KEY",
    "APRA_AMCOS_API_KEY",
    "JASRAC_API_KEY",
    "KOMCA_API_KEY",
    "SACEM_API_KEY",
    "MLC_API_KEY",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "YOUTUBE_API_KEY",
    "TICKETMASTER_API_KEY",
    "TROLLEY_SANDBOX_API_KEY",
    "TROLLEY_SANDBOX_SECRET_KEY"
)

function ConvertTo-PlainText {
    param([Security.SecureString]$SecureValue)

    if ($null -eq $SecureValue) {
        return ""
    }

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

function Get-EnvFileSecrets {
    param([string]$Path)

    $values = @{}
    if (-not $Path) {
        return $values
    }

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Env file not found: $Path"
    }

    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $parts = $trimmed -split '=', 2
        if ($parts.Count -ne 2) {
            continue
        }

        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        $values[$name] = $value
    }

    return $values
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI 'gh' is required but was not found in PATH."
}

$null = gh auth status
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated. Run 'gh auth login' first."
}

$envSecrets = Get-EnvFileSecrets -Path $EnvFile

Write-Host "Setting integration secrets for $Repo" -ForegroundColor Cyan
if ($EnvFile) {
    Write-Host "Using values from $EnvFile when present; missing values will be prompted." -ForegroundColor Yellow
}

foreach ($secretName in $secretNames) {
    $value = ""

    if ($envSecrets.ContainsKey($secretName) -and -not [string]::IsNullOrWhiteSpace($envSecrets[$secretName])) {
        $value = $envSecrets[$secretName]
        Write-Host "Loaded $secretName from env file." -ForegroundColor DarkYellow
    }
    else {
        $secureValue = Read-Host -AsSecureString -Prompt "$secretName (leave empty to skip)"
        $value = ConvertTo-PlainText -SecureValue $secureValue
    }

    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "Skipping $secretName" -ForegroundColor DarkGray
        continue
    }

    if ($DryRun) {
        Write-Host "[dry-run] Would set $secretName in $Repo" -ForegroundColor Yellow
        continue
    }

    $value | gh secret set $secretName -R $Repo --body -
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set $secretName"
    }

    Write-Host "Set $secretName" -ForegroundColor Green
}

Write-Host "Finished processing integration secrets for $Repo" -ForegroundColor Green
