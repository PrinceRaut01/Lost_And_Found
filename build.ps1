param(
    [switch]$Package
)

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$AssetsDir = Join-Path $Root 'assets'
$IconPath = Join-Path $AssetsDir 'icon.ico'
$BuildDir = Join-Path $Root 'build'
$DistDir = Join-Path $Root 'dist'
$ReleaseDir = Join-Path $Root 'release'
$InstallerDir = Join-Path $Root 'installer'
$Generator = Join-Path $Root 'scripts\generate_icon.py'
$MainScript = Join-Path $Root 'main.py'
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)
if (-not $PythonExe) {
    $PythonExe = 'C:\Users\princ\AppData\Local\Programs\Python\Python311\python.exe'
}

New-Item -ItemType Directory -Force -Path $AssetsDir, $BuildDir, $DistDir, $ReleaseDir, $InstallerDir | Out-Null

if (-not (Test-Path $IconPath) -or ((Get-Item $IconPath).Length -eq 0)) {
    & $PythonExe $Generator
}

$VersionFile = Join-Path $Root 'version_info.txt'

$PyInstallerArgs = @(
    '--noconfirm',
    '--clean',
    '--onefile',
    '--windowed',
    '--name', 'LostAndFoundDesk',
    '--icon', $IconPath,
    '--add-data', "$IconPath;assets",
    '--hidden-import', 'admin_page',
    '--hidden-import', 'user_page',
    '--version-file', $VersionFile,
    '--distpath', $DistDir,
    '--workpath', $BuildDir,
    '--specpath', $BuildDir,
    $MainScript
)

& pyinstaller @PyInstallerArgs

$ExePath = Join-Path $DistDir 'LostAndFoundDesk.exe'
if (Test-Path $ExePath) {
    Copy-Item $ExePath (Join-Path $ReleaseDir 'LostAndFoundDesk.exe') -Force
}

if ($Package) {
    $InstallerScript = Join-Path $InstallerDir 'LostAndFoundDesk.iss'
    if (-not (Test-Path $InstallerScript)) {
        throw "Installer script not found: $InstallerScript"
    }

    $Iscc = (Get-Command iscc -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)
    if (-not $Iscc) {
        $CommonIsccPaths = @(
            (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'),
            'C:\Program Files\Inno Setup 6\ISCC.exe',
            'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
        )
        $Iscc = $CommonIsccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
    }

    if (-not $Iscc) {
        throw 'Inno Setup compiler not found. Install Inno Setup to create the installer.'
    }

    & $Iscc $InstallerScript
}

Write-Host "Build complete: $ExePath"
