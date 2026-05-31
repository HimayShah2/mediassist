@echo off
echo Installing Aider (AI Coding Assistant) in the virtual environment...
call c:\mediassist\.venv\Scripts\activate.bat
pip install aider-chat

echo ========================================================
echo Installation complete! 
echo You can now run "start_nim_agent.bat" to launch the agent.
echo ========================================================
pause
