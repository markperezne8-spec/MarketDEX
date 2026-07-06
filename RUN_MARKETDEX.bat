@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv || goto :fail
  ".venv\Scripts\python.exe" -m pip install --upgrade pip || goto :fail
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail
)
".venv\Scripts\python.exe" launcher.py
exit /b %errorlevel%
:fail
echo.
echo MarketDEX setup failed. Screenshot this window for Debugging.
pause
exit /b 1
