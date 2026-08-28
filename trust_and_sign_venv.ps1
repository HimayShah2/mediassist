param()
$ErrorActionPreference = "Stop"
$Thumbprint = "DA7B803B220B462AC6A3817D781A7994BB9F7032"

Write-Host "=== Step 1: Trusting MediAssist Publisher in LocalMachine Root ===" -ForegroundColor Cyan
$cert = Get-Item "Cert:\CurrentUser\My\$Thumbprint"
$lmRoot = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
$lmRoot.Open("ReadWrite")
$lmRoot.Add($cert)
$lmRoot.Close()
Write-Host "[OK] Certificate trusted in LocalMachine Root" -ForegroundColor Green

Write-Host "`n=== Step 2: Signing all DLLs/PYDs in the venv ===" -ForegroundColor Cyan
$venvPath = "C:\mediassist\.venv\Lib\site-packages"
$files = Get-ChildItem $venvPath -Recurse -Include "*.dll","*.pyd" -ErrorAction SilentlyContinue
$count = 0
foreach ($f in $files) {
    $sig = Get-AuthenticodeSignature $f.FullName
    if ($sig.Status -ne "Valid") {
        Set-AuthenticodeSignature -FilePath $f.FullName -Certificate $cert -ErrorAction SilentlyContinue | Out-Null
        $count++
    }
}
Write-Host "[OK] Signed $count files" -ForegroundColor Green
Write-Host "`nDone! You can now run main.py." -ForegroundColor Green
