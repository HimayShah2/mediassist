param (
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$CertThumbprint = "DA7B803B220B462AC6A3817D781A7994BB9F7032"
$ExePath = "c:\mediassist\dist\MediAssistPro\MediAssistPro.exe"

if (-not $SkipBuild) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host " 1. Building MediAssist Pro (PyInstaller) " -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    .venv\Scripts\python -m PyInstaller -y MediAssistPro.spec
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host " 2. Signing Executable with Local Cert    " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if (Test-Path $ExePath) {
    $cert = Get-Item "Cert:\CurrentUser\My\$CertThumbprint"
    Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert
    Write-Host "`n[SUCCESS] Build and Sign Complete!" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Executable not found at $ExePath" -ForegroundColor Red
}
