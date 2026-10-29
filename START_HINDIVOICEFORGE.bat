@echo off
setlocal
title HindiVoiceForge - Local Wi-Fi Server
cd /d "%~dp0"

echo.
echo  ==========================================
echo       HindiVoiceForge - One-click starter
echo  ==========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found.
  echo Install Python 3.11 from https://www.python.org/downloads/windows/
  echo During installation, enable "Add python.exe to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating the local Python environment...
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo ERROR: Could not create the environment. Make sure Python 3.11 is installed.
    pause
    exit /b 1
  )
)

echo [2/3] Checking/installing required packages. First run may take a few minutes...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 (
  echo ERROR: pip could not be upgraded. Check your internet connection and retry.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo ERROR: Package installation failed. Check your internet connection and retry.
  pause
  exit /b 1
)

set "HINDIVOICEFORGE_PORT=7860"
for /f "usebackq delims=" %%I in (`.venv\Scripts\python.exe -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2^>nul`) do set "LAN_IP=%%I"

echo.
echo [3/3] Starting HindiVoiceForge...
echo.
echo  This computer: http://127.0.0.1:%HINDIVOICEFORGE_PORT%
if defined LAN_IP (
  echo  Network URL:  http://%LAN_IP%:%HINDIVOICEFORGE_PORT%
) else (
  echo  Network URL:  Find this PC's IPv4 address with ipconfig, then open http://YOUR-IP:%HINDIVOICEFORGE_PORT%
)
echo.
echo  Keep this window open while using the website.
echo  If Windows Firewall prompts, allow Python on Private networks only.
echo  Press Ctrl+C to stop the website.
echo.

".venv\Scripts\python.exe" app.py
if errorlevel 1 (
  echo.
  echo HindiVoiceForge stopped with an error. Read the message above.
  pause
)
endlocal
