param([string]$Python = "python", [string]$Game = "H:\GOG\Vampire The Masquerade - Redemption")
$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$gameRoot = (Resolve-Path -LiteralPath $Game).Path
if ($projectRoot.StartsWith($gameRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or $projectRoot -eq $gameRoot) {
    throw "El proyecto debe estar fuera de la instalación original"
}
$compilerDir = Join-Path $projectRoot "cache\toolchain"
$vendorDir = Join-Path $projectRoot "cache\vendor"
New-Item -ItemType Directory -Force -Path $compilerDir,$vendorDir | Out-Null
$compilerPath = Join-Path $compilerDir "ecj-3.26.0.jar"
$compilerHash = "ac0ba5876eaf7ebb47749a0d1be179c51f194b9dd0b875d1c09e1b530f5a2db5"
if (-not (Test-Path -LiteralPath $compilerPath)) {
    Invoke-WebRequest -Uri "https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.26.0/ecj-3.26.0.jar" -OutFile $compilerPath
}
if ((Get-FileHash -LiteralPath $compilerPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $compilerHash) {
    throw "Hash incorrecto del compilador ECJ"
}
& $Python -m pip install --target $vendorDir -r (Join-Path $projectRoot "requirements.txt") --disable-pip-version-check --no-cache-dir
if ($LASTEXITCODE -ne 0) { throw "No se pudo preparar PyYAML" }
& $Python (Join-Path $PSScriptRoot "rcm.py") --game $Game scan
if ($LASTEXITCODE -ne 0) { throw "No se pudo analizar la instalación" }
