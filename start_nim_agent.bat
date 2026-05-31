@echo off
echo ========================================================
echo Starting NVIDIA NIM Agent (Aider) powered by Qwen2.5-Coder
echo ========================================================

:: Activate the virtual environment where aider is installed
call c:\mediassist\.venv\Scripts\activate.bat

:: Configure Aider to use the NVIDIA NIM API endpoints
set OPENAI_API_BASE=https://integrate.api.nvidia.com/v1

:: Using one of the 7 provided NIM keys
set OPENAI_API_KEY=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

:: Launch Aider with the Qwen2.5-Coder-32B model (best for coding)
:: You can change this to "openai/z-ai/glm-5.1" or "openai/minimaxai/minimax-m2.1"
aider --model openai/qwen/qwen2.5-coder-32b-instruct
