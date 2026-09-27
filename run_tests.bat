@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest tests
pause
