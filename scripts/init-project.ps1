<#
.SYNOPSIS
  One-time setup after creating a repo from this template.
.EXAMPLE
  ./scripts/init-project.ps1 -Name "RoleSync"
#>
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [switch]$SkipPlugin
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$today = Get-Date -Format "yyyy-MM-dd"

Write-Host "Filling placeholders for '$Name'..."
$files = @(
    "CLAUDE.md", "docs/prd.md", "docs/architecture.md", "docs/state.md",
    "docs/adr/README.md", "docs/adr/0001-record-architecture-decisions.md",
    ".specify/memory/constitution.md"
)
foreach ($f in $files) {
    $text = Get-Content $f -Raw
    $text = $text.Replace("[PROJECT_NAME]", $Name).Replace("[DATE]", $today)
    $text = $text.Replace("[RATIFICATION_DATE]", $today).Replace("[LAST_AMENDED_DATE]", $today)
    Set-Content -Path $f -Value $text -NoNewline -Encoding utf8
}

Write-Host "Checking tools..."
foreach ($tool in @("git", "claude", "specify")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Warning "$tool not found on PATH."
    }
}
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Warning "python3 not found. Spec Kit skills call 'python3'. Install Python or add a python3 alias."
}

if (-not $SkipPlugin -and (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Superpowers plugin (user scope)..."
    claude plugin install superpowers@claude-plugins-official
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  1. Fill in docs/prd.md (problem, users, goals, non-goals)"
Write-Host "  2. Open Claude Code and run /speckit-constitution to tailor the constitution"
Write-Host "  3. Fill in the Commands and Stack sections of CLAUDE.md"
Write-Host "  4. First feature: /speckit-specify"
