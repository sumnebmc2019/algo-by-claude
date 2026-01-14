#!/bin/bash
# ALGO BY GUGAN - Quick Start Script

echo "Starting ALGO BY GUGAN..."

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run setup
python setup_angelone.py

# Start both bots in tmux
tmux new-session -d -s algo_realtime 'python run_realtime.py'
tmux new-session -d -s algo_backtest 'python run_backtest.py'

echo "Bots started!"
echo "View realtime: tmux attach -t algo_realtime"
echo "View backtest: tmux attach -t algo_backtest"
echo "Detach from tmux: Ctrl+B then D"
