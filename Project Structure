# ALGO BY GUGAN - Project Structure

"""
Directory Structure:
--------------------
algo_by_gugan/
├── config/
│   ├── secrets.yaml              # All API keys, tokens, credentials
│   └── settings.yaml             # Bot settings, timings, paths
├── core/
│   ├── __init__.py
│   ├── broker_manager.py         # Broker API integration hub
│   ├── symbol_manager.py         # Symbol selection, filtering, master lists
│   ├── position_manager.py       # Position tracking & management
│   ├── order_executor.py         # Order placement & execution
│   └── data_manager.py           # Historical & live data handling
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py          # Base class for all strategies
│   ├── strategy_loader.py        # Dynamic strategy loading
│   └── example_strategy.py       # Example strategy template
├── bots/
│   ├── __init__.py
│   ├── backtest_bot.py           # Backtest bot logic
│   └── realtime_bot.py           # Realtime bot logic
├── telegram/
│   ├── __init__.py
│   ├── bt_telegram.py            # Backtest telegram interface
│   ├── rt_telegram.py            # Realtime telegram interface
│   └── telegram_base.py          # Shared telegram utilities
├── utils/
│   ├── __init__.py
│   ├── logger.py                 # Logging configuration
│   ├── scheduler.py              # Time-based execution
│   ├── trade_logger.py           # CSV trade logging
│   └── helpers.py                # Common utilities
├── data/
│   ├── master_lists/             # Broker master symbol lists
│   ├── historical/               # Historical data cache
│   └── backtest_state/           # Backtest progress tracking
├── logs/
│   ├── backtest/                 # Backtest debug logs
│   └── realtime/                 # Realtime debug logs
├── trades/
│   ├── backtest_trades.csv       # Backtest trade log
│   └── realtime_trades.csv       # Realtime trade log
├── requirements.txt
├── run_backtest.py               # Backtest bot launcher
└── run_realtime.py               # Realtime bot launcher

Installation Commands:
----------------------
# On your Azure Ubuntu VM
cd ~
python3 -m venv .venv
source .venv/bin/activate

# Create project structure
mkdir -p algo_by_gugan/{config,core,strategies,bots,telegram,utils,data/{master_lists,historical,backtest_state},logs/{backtest,realtime},trades}

# Navigate to project
cd algo_by_gugan

# Create __init__.py files
touch core/__init__.py strategies/__init__.py bots/__init__.py telegram/__init__.py utils/__init__.py

# Install dependencies (requirements.txt content below)
pip install -r requirements.txt
"""

# requirements.txt content:
REQUIREMENTS = """
python-telegram-bot==20.7
pyyaml==6.0.1
pandas==2.1.4
numpy==1.26.2
pytz==2023.3
requests==2.31.0
python-dotenv==1.0.0
schedule==1.2.0
smartapi-python==1.3.0
pyotp==2.9.0
"""

# Save requirements.txt:
# echo "python-telegram-bot==20.7
# pyyaml==6.0.1
# pandas==2.1.4
# numpy==1.26.2
# pytz==2023.3
# requests==2.31.0
# python-dotenv==1.0.0
# schedule==1.2.0" > requirements.txt

TMUX_COMMANDS = """
# Running the bots in tmux sessions:

# Start backtest bot
tmux new-session -d -s algo_backtest 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_backtest.py'

# Start realtime bot
tmux new-session -d -s algo_realtime 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_realtime.py'

# View running sessions
tmux ls

# Attach to backtest session
tmux attach -t algo_backtest

# Attach to realtime session
tmux attach -t algo_realtime

# Detach from session: Ctrl+B then D

# Kill sessions
tmux kill-session -t algo_backtest
tmux kill-session -t algo_realtime
"""

print(__doc__)
print("\nREQUIREMENTS.TXT:")
print(REQUIREMENTS)
print("\nTMUX COMMANDS:")
print(TMUX_COMMANDS)