@echo off
setlocal
cd /d "%~dp0"
title MarketDEX M37.B1 Launcher
set "LOG=%~dp0M37_STARTUP_LOG.txt"
echo MarketDEX M37.B1 startup > "%LOG%"
echo Folder: %CD% >> "%LOG%"
if exist ".venv\Scripts\python.exe" goto RUN
where py >nul 2>&1
if not errorlevel 1 (py -m venv .venv >> "%LOG%" 2>&1 & goto INSTALL)
where python >nul 2>&1
if not errorlevel 1 (python -m venv .venv >> "%LOG%" 2>&1 & goto INSTALL)
echo ERROR: No usable Python launcher found. >> "%LOG%"
echo M37 STARTUP BLOCKED & echo Send Mark/Jarvis M37_STARTUP_LOG.txt & pause & exit /b 1
:INSTALL
if not exist ".venv\Scripts\python.exe" (echo ERROR: Virtual environment creation failed. >> "%LOG%" & echo M37 STARTUP BLOCKED & pause & exit /b 1)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 (echo ERROR: Dependency installation failed. >> "%LOG%" & echo M37 STARTUP BLOCKED & echo Send Mark/Jarvis M37_STARTUP_LOG.txt & pause & exit /b 1)
:RUN
".venv\Scripts\python.exe" launcher.py >> "%LOG%" 2>&1
if errorlevel 1 (echo ERROR: MarketDEX startup failed. >> "%LOG%" & echo M37 STARTUP BLOCKED & echo Send Mark/Jarvis M37_STARTUP_LOG.txt & pause & exit /b 1)
endlocal
