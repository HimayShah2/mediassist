@echo off
echo =======================================================
echo Starting 18 Automated UI Tests for MediAssistPro
echo =======================================================
echo The AI will take control of the app and run the tests.
echo Please do not close this window until the tests finish.
echo.

call .venv\Scripts\activate.bat
python tests\run_18_tests.py
pause
