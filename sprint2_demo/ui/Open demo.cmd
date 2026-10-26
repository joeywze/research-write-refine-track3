@echo off
setlocal
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
if not exist ".venv\Scripts\python.exe" (
  echo Create the UI environment using the commands in README.md first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" launch.py
pause
