@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo   MediAssist Pro
echo ==================================================

rem 1. Start the local LLM server (needs the .venv + model)
if exist ".venv\Scripts\python.exe" (
    if exist "models_local\gemma-4-E4B-it-Q4_K_M.gguf" (
        echo Starting local LLM server...
        start "MediAssist LLM Server" cmd /c start_local_llm.bat
        echo Waiting for the LLM server (http://127.0.0.1:1234) ...
        :wait
        timeout /t 3 /nobreak >nul
        ".venv\Scripts\python.exe" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:1234/v1/models', timeout=2)" 2>nul
        if errorlevel 1 goto wait
        echo LLM server is up.
    ) else (
        echo [WARN] Model not found at models_local\gemma-4-E4B-it-Q4_K_M.gguf
        echo        The app will open but AI features will not work until a server
        echo        is running on http://127.0.0.1:1234/v1
    )
) else (
    echo [WARN] .venv not found - start your own LLM server on port 1234.
)

rem 2. Launch the packaged app
if exist "dist\MediAssistPro\MediAssistPro.exe" (
    start "" "dist\MediAssistPro\MediAssistPro.exe"
) else if exist "MediAssistPro.exe" (
    start "" "MediAssistPro.exe"
) else (
    echo [ERROR] MediAssistPro.exe not found. Build it with:
    echo     .venv\Scripts\python.exe -m PyInstaller --noconfirm MediAssistPro.spec
    pause
)
