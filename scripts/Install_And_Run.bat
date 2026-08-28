@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo   MediAssist Pro - First-run setup
echo ==================================================

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11 is required and was not found on PATH.
    echo Install it from https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing dependencies (first run only, a few minutes)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" -m pip install "sse-starlette==2.1.3" "starlette>=0.37.2,<0.39.0"
".venv\Scripts\python.exe" -m pip install --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu llama-cpp-python
".venv\Scripts\python.exe" -m pip install onnxruntime

if not exist "models_local\gemma-4-E4B-it-Q4_K_M.gguf" (
    echo.
    echo [ACTION NEEDED] Place a GGUF chat model at:
    echo     models_local\gemma-4-E4B-it-Q4_K_M.gguf
    echo or edit start_local_llm.bat to point at your model, then re-run.
    echo (You can also run: .venv\Scripts\python.exe scripts\download_model.py)
    pause
)

call Run_MediAssist_Dev.bat
