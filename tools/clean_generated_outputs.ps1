param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ((Get-Item -LiteralPath $taskRoot).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'La raíz del proyecto es un enlace.' }
$buildRoot = Join-Path $taskRoot 'build'
$keepBuild = @('portable', 'rcm_tutor', 'rcm_mini')
$portableWorkspace = Join-Path $buildRoot 'portable\RedemptionChronicleMaker\workspace'
$reportRoot = Join-Path $taskRoot 'research\round0\notes_motion'
New-Item -ItemType Directory -Path $reportRoot -Force | Out-Null

function Check-Tree([string]$taskPath) {
    $absolute = [IO.Path]::GetFullPath($taskPath)
    if (-not $absolute.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Fuera del proyecto: $absolute" }
    if (-not (Test-Path -LiteralPath $absolute)) { throw "Ruta inexistente: $absolute" }
    $parent = $absolute
    while ($parent -ne $taskRoot) {
        $item = Get-Item -LiteralPath $parent -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Enlace: $parent" }
        $parent = [IO.Path]::GetDirectoryName($parent)
    }
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($absolute)
    $bytes = [int64]0
    $files = 0
    while ($pending.Count -gt 0) {
        $current = $pending.Pop()
        $item = Get-Item -LiteralPath $current -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Enlace dentro de salida: $current" }
        if ($item.PSIsContainer) {
            foreach ($child in [IO.Directory]::EnumerateFileSystemEntries($current)) { $pending.Push($child) }
        } else {
            if ($item.LinkType) { throw "Enlace de fichero: $current" }
            $bytes += $item.Length; $files++
        }
    }
    [pscustomobject]@{path=$absolute;bytes=$bytes;files=$files}
}

$targets = [Collections.Generic.List[string]]::new()
foreach ($item in Get-ChildItem -LiteralPath $buildRoot -Force) {
    if ($keepBuild -notcontains $item.Name) { $targets.Add($item.FullName) }
}
# Portable keeps the user's current projects/settings. Only intermediate builds
# and diagnostics are removed; finished bundles remain usable for Deploy.
$portableBuild = Join-Path $portableWorkspace 'build'
if (Test-Path -LiteralPath $portableBuild) {
    foreach ($item in Get-ChildItem -LiteralPath $portableBuild -Force) {
        if (@('rcm_tutor','rcm_mini') -notcontains $item.Name) { $targets.Add($item.FullName) }
    }
}
$generatedBackups = @('research\checkpoints','research\package_backups','research\build_backups','research\runtime_test\backups')
foreach ($relative in $generatedBackups) {
    $path = Join-Path $taskRoot $relative
    if (Test-Path -LiteralPath $path) { $targets.Add($path) }
}
$round0 = Join-Path $taskRoot 'research\round0'
foreach ($file in Get-ChildItem -LiteralPath $round0 -Recurse -File -Filter '*.zip') {
    # Explicit authoring/deployment snapshots; never SDK archives or fixtures.
    if ($file.Name -match '^(sources_before_|examples_refresh_|retired_user_projects|before_|backup)') { $targets.Add($file.FullName) }
}
foreach ($relative in @('research\phase9','research\runtime_test\lan_crash')) {
    $snapshotRoot = Join-Path $taskRoot $relative
    if (Test-Path -LiteralPath $snapshotRoot) {
        foreach ($file in Get-ChildItem -LiteralPath $snapshotRoot -Recurse -File -Filter '*.zip') {
            if ($file.Name -match '^(before_|after_|retired_|sources_\d+\.\d+\.\d+\.zip$)') { $targets.Add($file.FullName) }
        }
    }
}
$inventory = @($targets | ForEach-Object { Check-Tree $_ })
$total = ($inventory | Measure-Object -Property bytes -Sum).Sum
if ($Apply) {
    if (Get-Process -Name RedemptionChronicleMaker -ErrorAction SilentlyContinue) { throw 'Cierra el editor antes de limpiar.' }
    foreach ($row in $inventory) {
        # Re-check each resolved target immediately before deletion, using only
        # native PowerShell operations and no second shell or string commands.
        Check-Tree $row.path | Out-Null
        Remove-Item -LiteralPath $row.path -Recurse -Force
    }
}
$report = [pscustomobject]@{applied=[bool]$Apply;paths=$inventory;removed_bytes=if($Apply){$total}else{0};planned_bytes=$total;retained_build=$keepBuild;user_projects_and_settings_preserved=$true;original_game_modified=$false}
$name = if($Apply){'cleanup.json'}else{'cleanup_plan.json'}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $reportRoot $name) -Encoding utf8
[pscustomobject]@{applied=[bool]$Apply;paths=$inventory.Count;GiB=[math]::Round($total/1GB,2);retained=$keepBuild} | ConvertTo-Json
