@echo off
setlocal
cd /d "%~dp0"
if not exist .venv (
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Failed to create Python 3.12 virtual environment.
    pause
    exit /b 1
  )
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
