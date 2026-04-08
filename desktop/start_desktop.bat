@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist venv_desktop (
    py -m venv venv_desktop  || python -m venv venv_desktop 
)

venv_desktop\Scripts\python.exe -m pip install -r requirements.txt
venv_desktop\Scripts\python.exe main.py