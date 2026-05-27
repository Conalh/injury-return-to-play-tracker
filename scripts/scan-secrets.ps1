$ErrorActionPreference = "Stop"

$excludedPathFragments = @(
  "/.git/",
  "/.next/",
  "/.venv/",
  "/node_modules/",
  "/__pycache__/",
  "/test-results/",
  "/playwright-report/",
  "/scripts/scan-secrets.ps1"
)

$patterns = [ordered]@{
  "private_key" = "BEGIN PRIVATE KEY"
  "github_token" = "ghp_"
  "slack_token" = "xox[baprs]-"
  "aws_access_key" = "AKIA[0-9A-Z]{16}"
  "openai_key" = "sk-[A-Za-z0-9]{20,}"
}

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$findings = @()

Get-ChildItem -Path $root -Recurse -File -Force |
  Where-Object {
    $path = $_.FullName.Replace("\", "/")
    -not ($excludedPathFragments | Where-Object { $path.Contains($_) })
  } |
  ForEach-Object {
    $relativePath = Resolve-Path -Relative $_.FullName
    $content = Get-Content -LiteralPath $_.FullName -Raw -ErrorAction SilentlyContinue
    foreach ($patternName in $patterns.Keys) {
      if ($content -match $patterns[$patternName]) {
        $findings += "$relativePath matched $patternName"
      }
    }
  }

if ($findings.Count -gt 0) {
  $findings | ForEach-Object { Write-Error $_ }
  exit 1
}

Write-Host "Secret scan passed."
