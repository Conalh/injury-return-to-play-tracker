param(
  [string]$BackupDirectory = "backups/drill",
  [string]$DatabaseService = "db",
  [string]$DatabaseName = "return_play",
  [string]$DatabaseUser = "postgres"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
$backupScript = Join-Path $PSScriptRoot "backup-postgres.ps1"
$restoreScript = Join-Path $PSScriptRoot "restore-postgres.ps1"

Push-Location $repoRoot
try {
  docker compose up -d $DatabaseService | Out-Null

  $ready = $false
  for ($i = 0; $i -lt 30; $i++) {
    docker compose exec -T $DatabaseService pg_isready `
      --username $DatabaseUser `
      --dbname $DatabaseName | Out-Null
    if ($LASTEXITCODE -eq 0) {
      $ready = $true
      break
    }
    Start-Sleep -Seconds 2
  }
  if (-not $ready) {
    throw "Postgres service did not become ready."
  }

  docker compose exec -T $DatabaseService psql `
    --username $DatabaseUser `
    --dbname $DatabaseName `
    --command "DROP TABLE IF EXISTS restore_drill_marker; CREATE TABLE restore_drill_marker (id integer PRIMARY KEY, value text NOT NULL); INSERT INTO restore_drill_marker VALUES (1, 'before-restore');"

  $backupPath = & $backupScript `
    -OutputDirectory $BackupDirectory `
    -DatabaseService $DatabaseService `
    -DatabaseName $DatabaseName `
    -DatabaseUser $DatabaseUser

  docker compose exec -T $DatabaseService psql `
    --username $DatabaseUser `
    --dbname $DatabaseName `
    --command "UPDATE restore_drill_marker SET value = 'after-backup' WHERE id = 1;"

  & $restoreScript `
    -BackupPath $backupPath `
    -ConfirmRestore "RESTORE return_play" `
    -DatabaseService $DatabaseService `
    -DatabaseName $DatabaseName `
    -DatabaseUser $DatabaseUser

  $restoredValue = docker compose exec -T $DatabaseService psql `
    --username $DatabaseUser `
    --dbname $DatabaseName `
    --tuples-only `
    --no-align `
    --command "SELECT value FROM restore_drill_marker WHERE id = 1;"

  if ($restoredValue.Trim() -ne "before-restore") {
    throw "Restore drill failed. Expected before-restore, got '$restoredValue'."
  }
} finally {
  Pop-Location
}

Write-Host "Restore drill passed."
