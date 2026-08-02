@echo off
REM ---------------------------------------------------------------------------
REM GitGrind - development launcher.
REM
REM This is for running from source while you are changing the code. For daily
REM use, build the executable once and double-click that instead:
REM
REM     python tools\build_exe.py
REM     dist\GitGrind.exe
REM ---------------------------------------------------------------------------
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on your PATH.
  echo Install Python 3.8 or newer from python.org and tick "Add to PATH".
  pause
  exit /b 1
)

echo Starting GitGrind from source...
python app.py %*
if errorlevel 1 (
  echo.
  echo GitGrind exited with an error. The message above says why.
  pause
)
endlocal
