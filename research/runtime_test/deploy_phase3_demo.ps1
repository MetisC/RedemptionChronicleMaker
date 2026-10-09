# One authorized deployment operation, not an editor installer or game launcher.
$ErrorActionPreference = 'Stop'
$expectedWorkspace = 'H:\Repositorios\RedemptionChronicleMaker'
$expectedRcm = 'H:\GOG\Vampire The Masquerade - Redemption\RCM'
$planPath = Join-Path $expectedWorkspace 'research\runtime_test\phase3_deployment_plan.json'
$plan = Get-Content -LiteralPath $planPath -Raw -Encoding utf8 | ConvertFrom-Json
$rcmPath = (Resolve-Path -LiteralPath $expectedRcm).Path
if ($plan.rcm_root -ne $expectedRcm -or $rcmPath -ne $expectedRcm) { throw 'Unexpected RCM root' }
if (Get-Process -Name Vampire -ErrorAction SilentlyContinue) { throw 'Vampire is running; close it before replacing packages.' }

function Assert-RcmTarget([string]$targetPath) {
    $absolute = [IO.Path]::GetFullPath($targetPath)
    if (-not $absolute.StartsWith($rcmPath + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Outside RCM: $absolute" }
    $cursor = $absolute
    while ($cursor -and $cursor -ne $rcmPath) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $item.LinkType) { throw "Link rejected: $cursor" }
        }
        $cursor = Split-Path -Path $cursor -Parent
    }
    $rootItem = Get-Item -LiteralPath $rcmPath -Force
    if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $rootItem.LinkType) { throw 'RCM root is a link' }
    return $absolute
}

# Check every source, target and previous hash before any mutation.
if (-not $plan.backup.StartsWith($expectedWorkspace + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Backup outside workspace' }
if ((Get-FileHash -LiteralPath $plan.backup -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.backup_sha256) { throw 'Backup hash mismatch' }
foreach ($operation in $plan.operations) {
    $null = Assert-RcmTarget $operation.destination
    $source = (Resolve-Path -LiteralPath $operation.source).Path
    if (-not $source.StartsWith($expectedWorkspace + '\build\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Source outside workspace build' }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $operation.sha256) { throw "Source hash mismatch: $source" }
    if (Test-Path -LiteralPath $operation.destination) {
        $current = (Get-FileHash -LiteralPath $operation.destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($current -ne $operation.before_sha256) { throw "Target changed after backup: $($operation.destination)" }
    } elseif ($operation.before_sha256) { throw 'A backed-up target has disappeared' }
}
$tracePath = Assert-RcmTarget $plan.trace_directory
foreach ($operation in $plan.operations) {
    $destination = Assert-RcmTarget $operation.destination
    $parent = Split-Path -Path $destination -Parent
    $null = New-Item -ItemType Directory -Path $parent -Force
    Copy-Item -LiteralPath $operation.source -Destination $destination -Force
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $operation.sha256) { throw "Deployed hash mismatch: $destination" }
}
# Generated Java writes its diagnostic log here; resources remain in east_demo.
$null = New-Item -ItemType Directory -Path $tracePath -Force
[pscustomobject]@{
    status = 'deployed-and-hash-verified'
    rcm_root = $rcmPath
    deployed_files = $plan.operations
    trace_directory = $tracePath
    backup = $plan.backup
    launch_arguments = $plan.launch_arguments
    chronicle_name = $plan.chronicle_name
    native_engine_test = $false
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $expectedWorkspace 'research\runtime_test\deployment_phase3_demo.json') -Encoding utf8
Write-Output 'Added three Phase3 files exclusively in RCM; hashes verified. Use the existing -user RCM\east_demo shortcut.'
