param(
  [string]$OutputDirectory = "backups",
  [string]$DatabaseService = "db",
  [string]$DatabaseName = "return_play",
  [string]$DatabaseUser = "postgres"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
$absoluteOutput = Join-Path $repoRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $absoluteOutput | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = Join-Path $absoluteOutput "return-play-$timestamp.sql"

Push-Location $repoRoot
try {
  docker compose up -d $DatabaseService | Out-Null
  docker compose exec -T $DatabaseService pg_dump `
    --username $DatabaseUser `
    --dbname $DatabaseName `
    --format plain `
    --no-owner `
    --no-privileges `
    --clean `
    --if-exists `
    > $backupPath
} finally {
  Pop-Location
}

if (-not (Test-Path -LiteralPath $backupPath) -or (Get-Item -LiteralPath $backupPath).Length -eq 0) {
  throw "Backup was not created at $backupPath"
}

Write-Output $backupPath
