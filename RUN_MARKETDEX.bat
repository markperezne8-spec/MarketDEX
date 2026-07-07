@echo off
setlocal
cd /d "%~dp0"
title MarketDEX M34.B1 Launcher
set "LOG=%~dp0M34_STARTUP_LOG.txt"
echo MarketDEX M34.B1 startup > "%LOG%"
echo Folder: %CD% >> "%LOG%"

if exist ".venv\Scripts\python.exe" goto RUN

where py >nul 2>&1
if not errorlevel 1 (
  echo Creating runtime with py... >> "%LOG%"
  py -m venv .venv >> "%LOG%" 2>&1
  goto INSTALL
)

where python >nul 2>&1
if not errorlevel 1 (
  echo Creating runtime with python... >> "%LOG%"
  python -m venv .venv >> "%LOG%" 2>&1
  goto INSTALL
)

echo ERROR: No usable Python launcher found. >> "%LOG%"
echo.
echo M34 STARTUP BLOCKED
 echo Send Mark/Jarvis M34_STARTUP_LOG.txt
pause
exit /b 1

:INSTALL
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Virtual environment creation failed. >> "%LOG%"
  echo.
  echo M34 STARTUP BLOCKED
  echo Send Mark/Jarvis M34_STARTUP_LOG.txt
  pause
  exit /b 1
)
echo Installing PySide6... >> "%LOG%"
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: Dependency installation failed. >> "%LOG%"
  echo.
  echo M34 STARTUP BLOCKED
  echo Send Mark/Jarvis M34_STARTUP_LOG.txt
  pause
  exit /b 1
)

:RUN
echo Launching MarketDEX... >> "%LOG%"
".venv\Scripts\python.exe" launcher.py >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: MarketDEX startup failed. >> "%LOG%"
  echo.
  echo M34 STARTUP BLOCKED
  echo Send Mark/Jarvis M34_STARTUP_LOG.txt
  pause
  exit /b 1
)
endlocal
