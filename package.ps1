$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

& powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'build.ps1') -Package
