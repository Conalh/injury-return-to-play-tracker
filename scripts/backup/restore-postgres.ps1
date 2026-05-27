param(
  [Parameter(Mandatory = $true)]
  [string]$BackupPath,
  [Parameter(Mandatory = $true)]
  [string]$ConfirmRestore,
  [string]$DatabaseService = "db",
  [string]$DatabaseName = "return_play",
  [string]$DatabaseUser = "postgres"
)

$ErrorActionPreference = "Stop"

if ($ConfirmRestore -ne "RESTORE return_play") {
  throw "Refusing to restore without ConfirmRestore='RESTORE return_play'."
}

$resolvedBackup = (Resolve-Path -LiteralPath $BackupPath).Path
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")

Push-Location $repoRoot
try {
  docker compose up -d $DatabaseService | Out-Null
  $containerId = docker compose ps -q $DatabaseService
  if (-not $containerId) {
    throw "Could not resolve compose container for service '$DatabaseService'."
  }

  docker cp $resolvedBackup "${containerId}:/tmp/return-play-restore.sql"
  docker compose exec -T $DatabaseService psql `
    --username $DatabaseUser `
    --dbname $DatabaseName `
    --command "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
  docker compose exec -T $DatabaseService psql `
    --username $DatabaseUser `
    --dbname $DatabaseName `
    --file "/tmp/return-play-restore.sql"
  docker compose exec -T $DatabaseService rm -f /tmp/return-play-restore.sql
} finally {
  Pop-Location
}

Write-Host "Restore completed from $resolvedBackup"
