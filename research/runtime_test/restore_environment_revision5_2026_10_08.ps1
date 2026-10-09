# Corrective deployment, scoped to the user's explicitly authorized RCM folder.
$ErrorActionPreference = 'Stop'
if (Get-Process -Name Vampire -ErrorAction SilentlyContinue) { throw 'Close Vampire before updating the package' }
$rcmWorkspace = 'H:\Repositorios\RedemptionChronicleMaker'
$rcmAllowed = [IO.Path]::GetFullPath('H:\GOG\Vampire The Masquerade - Redemption\RCM')
$rcmTarget = [IO.Path]::GetFullPath((Join-Path $rcmAllowed 'east_demo'))
$rcmSource = Join-Path $rcmWorkspace 'build\east_demo\bundle'
$rcmBackup = Join-Path $rcmWorkspace ('research\runtime_test\backups\' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
function Assert-RcmPath([string] $candidate) {
    $full = [IO.Path]::GetFullPath($candidate)
    if (!$full.StartsWith($rcmAllowed + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside authorized RCM' }
    $node = $full
    while ($node.Length -ge $rcmAllowed.Length) {
        if (Test-Path -LiteralPath $node) {
            if ((Get-Item -LiteralPath $node).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point refused' }
        }
        $node = [IO.Path]::GetDirectoryName($node)
    }
    return $full
}
$null = Assert-RcmPath $rcmTarget
$rcmReport = Get-Content -LiteralPath (Join-Path $rcmWorkspace 'build\east_demo\build_report.json') -Raw | ConvertFrom-Json
$rcmTests = Get-Content -LiteralPath (Join-Path $rcmWorkspace 'build\tests\test_report.json') -Raw | ConvertFrom-Json
if ($rcmReport.status -ne 'compiled-unverified-in-game' -or !$rcmTests.successful) { throw 'Build or checks incomplete' }
$rcmFiles = @('east_demo.nob', 'codex\R_east_demo_Scene.class', 'codex\R_east_demo_Passive.class')
foreach ($relative in $rcmFiles) {
    $key = $relative.Replace('\', '/')
    $actual = (Get-FileHash -LiteralPath (Join-Path $rcmSource $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $rcmReport.distribution_files.$key.sha256) { throw 'Source hash mismatch' }
}
# Preserve every existing file before replacing or retiring managed resources.
$existing = @(Get-ChildItem -LiteralPath $rcmTarget -Recurse -Force)
foreach ($item in $existing) { $null = Assert-RcmPath $item.FullName }
foreach ($item in $existing | Where-Object { !$_.PSIsContainer }) {
    $relative = $item.FullName.Substring($rcmTarget.Length + 1)
    $backupFile = Join-Path $rcmBackup $relative
    $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backupFile)) -Force
    Copy-Item -LiteralPath $item.FullName -Destination $backupFile
    if ((Get-FileHash -LiteralPath $backupFile).Hash -ne (Get-FileHash -LiteralPath $item.FullName).Hash) { throw 'Backup mismatch' }
}
foreach ($relative in $rcmFiles) {
    $destination = Assert-RcmPath (Join-Path $rcmTarget $relative)
    $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force
    Copy-Item -LiteralPath (Join-Path $rcmSource $relative) -Destination $destination -Force
}
# Old loose resources take precedence over the archive; remove only our known files.
$obsolete = @('chronicles\east_demo.nsc','chronicles\R_east_demo.nmf',
    'conversations\R_east_demo_intro.nco','conversations\R_east_demo_ally.nco',
    'misc\templates\R_east_demo.not','scenes\R_east_demo.nsd',
    'sounds\voice\R_east_demo_silence.wav','strings\chronicles.nls',
    'strings\R_east_demo.nls','strings\R_east_demo.nvo')
$removed = @()
foreach ($relative in $obsolete) {
    $destination = Assert-RcmPath (Join-Path $rcmTarget $relative)
    if (Test-Path -LiteralPath $destination -PathType Leaf) {
        Remove-Item -LiteralPath $destination
        $removed += $relative
    }
}
$verified = @()
foreach ($relative in $rcmFiles) {
    $destination = Assert-RcmPath (Join-Path $rcmTarget $relative)
    $hash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    $key = $relative.Replace('\', '/')
    if ($hash -ne $rcmReport.distribution_files.$key.sha256) { throw 'Deployed hash mismatch' }
    $verified += @{path=$relative; sha256=$hash}
}
$record = @{date=(Get-Date -Format o); revision=5; destination=$rcmTarget; backup=$rcmBackup; files=$verified;
    retired_loose_files=$removed; native_test='User confirms both original comparison cases show grey background; revision 5 removes added sky and awaits visual confirmation of demo';
    original_files_modified=$false; game_process_absent=$true}
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $rcmWorkspace 'research\runtime_test\deployment_revision5_2026_10_08.json') -Encoding utf8
Write-Output ('Updated 3 distribution files; preserved backup; retired ' + $removed.Count + ' old loose resources.')
