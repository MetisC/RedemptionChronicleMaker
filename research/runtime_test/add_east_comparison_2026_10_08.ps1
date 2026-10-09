# Add comparison resources only within the explicitly authorized RCM directory.
$ErrorActionPreference = 'Stop'
if (Get-Process -Name Vampire -ErrorAction SilentlyContinue) { throw 'Close Vampire before adding comparison package' }
$rcmWorkspace = 'H:\Repositorios\RedemptionChronicleMaker'
$rcmAllowed = [IO.Path]::GetFullPath('H:\GOG\Vampire The Masquerade - Redemption\RCM')
$rcmTarget = [IO.Path]::GetFullPath((Join-Path $rcmAllowed 'east_demo\east_compare.nob'))
if (!$rcmTarget.StartsWith($rcmAllowed + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target outside RCM' }
$rcmNode = $rcmTarget
while ($rcmNode.Length -ge $rcmAllowed.Length) {
    if (Test-Path -LiteralPath $rcmNode) {
        if ((Get-Item -LiteralPath $rcmNode).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point refused' }
    }
    $rcmNode = [IO.Path]::GetDirectoryName($rcmNode)
}
$rcmSource = Join-Path $rcmWorkspace 'build\diagnostics\east_compare\east_compare.nob'
$rcmReport = Get-Content -LiteralPath (Join-Path $rcmWorkspace 'build\diagnostics\east_compare\report.json') -Raw | ConvertFrom-Json
$rcmExpected = (Get-FileHash -LiteralPath $rcmSource -Algorithm SHA256).Hash.ToLowerInvariant()
if ($rcmExpected -ne $rcmReport.sha256) { throw 'Comparison package source hash mismatch' }
$rcmDemo = Join-Path $rcmAllowed 'east_demo\east_demo.nob'
$rcmDemoBefore = (Get-FileHash -LiteralPath $rcmDemo -Algorithm SHA256).Hash
$rcmBackup = $null
if (Test-Path -LiteralPath $rcmTarget -PathType Leaf) {
    $rcmBackup = Join-Path $rcmWorkspace ('research\runtime_test\backups\comparison_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff') + '\east_compare.nob')
    $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($rcmBackup)) -Force
    Copy-Item -LiteralPath $rcmTarget -Destination $rcmBackup
    if ((Get-FileHash -LiteralPath $rcmBackup).Hash -ne (Get-FileHash -LiteralPath $rcmTarget).Hash) { throw 'Backup mismatch' }
}
Copy-Item -LiteralPath $rcmSource -Destination $rcmTarget -Force
$rcmAfter = (Get-FileHash -LiteralPath $rcmTarget -Algorithm SHA256).Hash.ToLowerInvariant()
if ($rcmAfter -ne $rcmExpected) { throw 'Deployed comparison hash mismatch' }
if ((Get-FileHash -LiteralPath $rcmDemo -Algorithm SHA256).Hash -ne $rcmDemoBefore) { throw 'Working demo changed unexpectedly' }
$rcmRecord = @{date=(Get-Date -Format o); destination=$rcmTarget; sha256=$rcmAfter;
    backup=$rcmBackup; original_files_modified=$false; game_process_absent=$true;
    demo_unchanged=$true; native_comparison='Pending user: direct EastLondon entry, base vs original scene vs custom demo'}
$rcmRecord | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $rcmWorkspace 'research\runtime_test\deployment_east_comparison_2026_10_08.json') -Encoding utf8
Write-Output 'Added one comparison NOB; working demo unchanged; deployed hash verified.'
