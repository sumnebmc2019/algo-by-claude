@echo off
REM ALGO BY GUGAN - Quick Start Script (Windows)

echo Starting ALGO BY GUGAN...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/update dependencies
pip install -r requirements.txt

REM Run setup
python setup_angelone.py

REM Start realtime bot
start "Realtime Bot" python run_realtime.py

REM Start backtest bot
start "Backtest Bot" python run_backtest.py

echo Bots started in separate windows!
pause
