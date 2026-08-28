@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo   MediAssist Pro - Dev Launcher
echo ==================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv
    pause
    exit /b 1
)

echo Starting local LLM server in a new window...
start "MediAssist LLM Server" cmd /c start_local_llm.bat

echo Waiting for the LLM server to come online (http://127.0.0.1:1234) ...
:waitloop
timeout /t 3 /nobreak >nul
".venv\Scripts\python.exe" -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:1234/v1/models', timeout=2)" 2>nul
if errorlevel 1 goto waitloop

echo LLM server is up. Launching MediAssist Pro...
".venv\Scripts\python.exe" main.py

pause
