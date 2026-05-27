$ErrorActionPreference = "Stop"

$webRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$repoRoot = Resolve-Path -LiteralPath (Join-Path $webRoot "..\..")
$apiRoot = Join-Path $repoRoot "services\api"
$python = Join-Path $apiRoot ".venv\Scripts\python.exe"
$apiPort = "8015"
$webPort = "3227"
$apiUrl = "http://127.0.0.1:$apiPort"

if (-not (Test-Path -LiteralPath $python)) {
  throw "API virtual environment was not found at $python"
}

$apiProcess = Start-Process `
  -FilePath $python `
  -ArgumentList @("-m", "uvicorn", "return_play.api:app", "--host", "127.0.0.1", "--port", $apiPort) `
  -WorkingDirectory $apiRoot `
  -PassThru `
  -WindowStyle Hidden

try {
  $ready = $false
  for ($i = 0; $i -lt 40; $i++) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri "$apiUrl/health" -TimeoutSec 1
      if ($response.StatusCode -eq 200) {
        $ready = $true
        break
      }
    } catch {
      Start-Sleep -Milliseconds 250
    }
  }
  if (-not $ready) {
    throw "API server did not become ready at $apiUrl"
  }

  $env:RETURN_PLAY_DATA_MODE = "api-demo"
  $env:RETURN_PLAY_API_BASE_URL = $apiUrl
  $env:RETURN_PLAY_ACTOR_ID = "clinician_demo"
  $env:RETURN_PLAY_ACTOR_ROLE = "clinician"
  $env:RETURN_PLAY_ORGANIZATION_ID = "org_demo"

  Push-Location $webRoot
  try {
    & npx next dev --hostname 127.0.0.1 --port $webPort
  } finally {
    Pop-Location
  }
} finally {
  if ($apiProcess -and -not $apiProcess.HasExited) {
    Stop-Process -Id $apiProcess.Id -Force
  }
}
