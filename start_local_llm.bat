@echo off
setlocal
cd /d "%~dp0"

set MODEL_PATH=models_local\gemma-4-E4B-it-Q4_K_M.gguf

if not exist "%MODEL_PATH%" (
    echo [ERROR] Model file not found: %MODEL_PATH%
    pause
    exit /b 1
)

echo Starting local Gemma server on http://127.0.0.1:1234 ...
echo (Leave this window open while using MediAssist Pro)

".venv\Scripts\python.exe" -m llama_cpp.server ^
    --model "%MODEL_PATH%" ^
    --model_alias google/gemma-4-e4b ^
    --host 127.0.0.1 ^
    --port 1234 ^
    --n_ctx 4096 ^
    --n_threads 12 ^
    --n_threads_batch 12 ^
    --n_batch 512 ^
    --logits_all false

pause
