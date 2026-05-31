@echo off
setlocal

:: MediAssist Pro - Open Source Launcher
:: This script bypasses Smart App Control by programmatically unblocking the application files.

echo --------------------------------------------------
echo MediAssist Pro - Initializing Trusted Environment
echo --------------------------------------------------

:: Use PowerShell to unblock all files in the application directory
:: This is the "manual unblock" that Smart App Control requires for unsigned apps.
powershell.exe -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File"

echo Launching MediAssist Pro...
echo (You may close this window once the app opens)

:: Launch the portable executable
if exist "%~dp0MediAssistPro.exe" (
    start "" "%~dp0MediAssistPro.exe"
) else if exist "%~dp0dist\MediAssistPro\MediAssistPro.exe" (
    start "" "%~dp0dist\MediAssistPro\MediAssistPro.exe"
) else (
    echo [ERROR] Application binary not found. 
    echo Please ensure you are running this script from the extracted folder.
    pause
)

exit
