#Requires -Version 5.1
<#
.SYNOPSIS
    Official local release pipeline for Redemption Chronicle Maker.

.DESCRIPTION
    Builds, audits, stages and (only on explicit request) publishes Windows
    releases from this machine. GitHub is used exclusively for repository,
    tags and release storage through the authenticated GitHub CLI; no GitHub
    Actions minutes are consumed by this flow.

    The default invocation (no mode switch) prints help and publishes nothing.
    Publishing requires -Publish plus a human confirmation: the tool asks for
    the exact tag name unless -ConfirmTag supplies it.

.EXAMPLE
    .\tools\release_local.ps1 -Check        # environment diagnostics
    .\tools\release_local.ps1 -Build        # full suite + staged artifacts
    .\tools\release_local.ps1 -DryRun       # remote-readiness plan, no writes
    .\tools\release_local.ps1 -Publish      # draft -> verify -> publish
    .\tools\release_local.ps1 -Verify       # re-check what GitHub stored
    .\tools\release_local.ps1 -Notes        # draft release notes from git log
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Prepare,
    [switch]$Build,
    [switch]$DryRun,
    [switch]$Publish,
    [switch]$Verify,
    [switch]$Notes,
    [string]$Tag,
    [string]$ConfirmTag,
    [switch]$Stable,
    [switch]$SkipQuality,
    [string]$Python
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$tool = Join-Path $PSScriptRoot 'release_local.py'

$modes = @(
    if ($Check)   { 'check' }
    if ($Prepare) { 'prepare' }
    if ($Build)   { 'build' }
    if ($DryRun)  { 'plan' }
    if ($Publish) { 'publish' }
    if ($Verify)  { 'verify' }
    if ($Notes)   { 'notes' }
)

if ($modes.Count -eq 0 -or $modes.Count -gt 1) {
    Write-Host 'Redemption Chronicle Maker - local release tool' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Choose exactly one mode:'
    Write-Host '  -Check    diagnose this machine (python, jdk, ecj, git, gh, auth)'
    Write-Host '  -Prepare  validate version, notes and git state'
    Write-Host '  -Build    full quality suite + audited staging build (no upload)'
    Write-Host '  -DryRun   verify remote readiness; shows the plan; no remote writes'
    Write-Host '  -Publish  tag, draft, verify, then publish (asks for confirmation)'
    Write-Host '  -Verify   re-download and verify the published assets'
    Write-Host '  -Notes    draft release notes from commits since the last tag'
    Write-Host ''
    Write-Host 'Options: -Tag <vX> for -Verify, -ConfirmTag <vX>, -Stable for final versions,'
    Write-Host '         -SkipQuality (diagnostic builds only, never publishable), -Python <exe>'
    exit 2
}

$pythonExe = if ($Python) { $Python }
             elseif ($env:RCM_PYTHON) { $env:RCM_PYTHON }
             else { 'python' }

$arguments = @($tool, $modes[0])
if ($SkipQuality -and $modes[0] -eq 'build') { $arguments += '--skip-quality' }
if ($ConfirmTag) { $arguments += @('--confirm-tag', $ConfirmTag) }
if ($Stable -and $modes[0] -eq 'publish')    { $arguments += '--stable' }
if ($Tag -and $modes[0] -eq 'verify')        { $arguments += $Tag }

Push-Location $root
try {
    Write-Host "RCM release $($modes[0]) - repo $root" -ForegroundColor Cyan
    & $pythonExe @arguments
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($code -ne 0) { exit $code }
