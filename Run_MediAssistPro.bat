@echo off
setlocal
cd /d "%~dp0"

rem MediAssist Pro — just run it. The app loads its own AI model in-process;
rem there is no server to start. First run downloads a ~0.9 GB model (one time).

if exist "dist\MediAssistPro\MediAssistPro.exe" (
    start "" "dist\MediAssistPro\MediAssistPro.exe"
) else if exist "MediAssistPro.exe" (
    start "" "MediAssistPro.exe"
) else (
    echo [ERROR] MediAssistPro.exe not found next to this script.
    pause
)
