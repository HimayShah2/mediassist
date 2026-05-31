@echo off
echo =========================================
echo MediAssist Pro - Phase 0 Verification
echo =========================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in .venv!
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [INFO] Installing dev requirements...
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo.
echo [INFO] Running initialization tests...
python -m pytest tests/unit/test_phase0_init.py -v

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Phase 0 verification failed!
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Phase 0 verification passed!
exit /b 0
