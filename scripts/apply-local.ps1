# Ejecuta la configuración de Vercel sin prompts.
# Crea en la raíz del repo un archivo .vercel-token con DOS líneas:
#   línea 1: token de https://vercel.com/account/tokens
#   línea 2: API_URL (ej. https://xxxx.onrender.com/api)
#
# Luego:  powershell -ExecutionPolicy Bypass -File scripts/apply-local.ps1

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$tokenPath = Join-Path $root ".vercel-token"

if (-not (Test-Path $tokenPath)) {
  Write-Host "Falta $tokenPath (dos lineas: token, luego API_URL)" -ForegroundColor Red
  exit 1
}

$lines = Get-Content $tokenPath -Encoding UTF8 | Where-Object { $_.Trim() -ne "" }
if ($lines.Count -lt 2) {
  Write-Host "El archivo debe tener 2 lineas: token y API_URL" -ForegroundColor Red
  exit 1
}

$env:VERCEL_TOKEN = $lines[0].Trim()
$env:API_URL = $lines[1].Trim()

Set-Location $root
node scripts/vercel-apply-config.mjs
exit $LASTEXITCODE
