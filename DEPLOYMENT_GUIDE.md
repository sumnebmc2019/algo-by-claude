# ALGO BY GUGAN - Algorithmic Trading System

A professional, scalable algorithmic trading system built with Python for backtesting and live trading with multiple brokers.

## 🌟 Features

- **Dual Bot Architecture**: Separate bots for backtesting and realtime trading
- **Paper & Live Trading**: Safe paper trading mode before going live
- **Multi-Broker Support**: Easily integrate multiple brokers via APIs
- **Multi-Segment Trading**: Support for NSE_EQ, NSE_FO, BSE_EQ, MCX_FO, CDS_FO
- **Plug-and-Play Strategies**: Add new strategies without modifying core code
- **Telegram Control Panel**: Full control and monitoring via Telegram
- **Automated Backtesting**: Progressive historical data testing with state tracking
- **Risk Management**: Built-in position sizing and risk controls
- **Comprehensive Logging**: Date-wise logs with auto-cleanup
- **Trade Tracking**: CSV-based trade logs for Excel/Sheets analysis

## 📋 Prerequisites

- Ubuntu (Azure VM or local)
- Python 3.8+
- tmux
- Telegram account and bot tokens

## 🚀 Quick Setup

### 1. Initial Setup

```bash
# SSH into your Azure VM
ssh username@your-vm-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv tmux -y

# Create virtual environment
cd ~
python3 -m venv .venv
source .venv/bin/activate

# Clone or create project directory
mkdir -p algo_by_gugan
cd algo_by_gugan
```

### 2. Project Structure Setup

```bash
# Create directory structure
mkdir -p config core strategies bots telegram utils data/{master_lists,historical,backtest_state} logs/{backtest,realtime} trades

# Create __init__.py files
touch core/__init__.py strategies/__init__.py bots/__init__.py telegram/__init__.py utils/__init__.py
```

### 3. Install Dependencies

Create `requirements.txt`:
```
python-telegram-bot==20.7
pyyaml==6.0.1
pandas==2.1.4
numpy==1.26.2
pytz==2023.3
requests==2.31.0
python-dotenv==1.0.0
schedule==1.2.0
```

Install:
```bash
pip install -r requirements.txt
```

### 4. Configuration

#### Create Telegram Bots
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create two bots:
   - `/newbot` for Backtest Bot
   - `/newbot` for Realtime Bot
3. Save the bot tokens
4. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

#### Configure secrets.yaml
```yaml
telegram:
  backtest:
    bot_token: "YOUR_BACKTEST_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  realtime:
    bot_token: "YOUR_REALTIME_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"

brokers:
  zerodha:
    api_key: "YOUR_ZERODHA_API_KEY"
    api_secret: "YOUR_ZERODHA_API_SECRET"
    enabled: true
```

### 5. Prepare Master Lists

Download master symbol lists from your broker and save as JSON in `data/master_lists/`:

Example format:
```json
[
  {
    "symbol": "NIFTY24JANFUT",
    "token": "12345",
    "lot_size": 50,
    "tick_size": 0.05,
    "exchange": "NSE"
  }
]
```

Save as: `data/master_lists/zerodha_NSE_FO.json`

### 6. Prepare Historical Data

For backtesting, download historical data and save as CSV in `data/historical/`:

Format:
```csv
timestamp,open,high,low,close,volume
2024-01-01 09:15:00,21500,21550,21480,21530,1000000
```

Save as: `data/historical/NSE_FO_NIFTY24JANFUT.csv`

## 🎮 Running the Bots

### Using tmux (Recommended)

```bash
# Start Backtest Bot
tmux new-session -d -s algo_backtest 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_backtest.py'

# Start Realtime Bot
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
```

### Direct Execution

```bash
# Backtest Bot
source ~/.venv/bin/activate
python run_backtest.py

# Realtime Bot (in another terminal)
source ~/.venv/bin/activate
python run_realtime.py
```

## 📱 Using Telegram Interface

1. Start a chat with your bot
2. Send `/start` command
3. Use the interactive menu to:
   - Configure settings
   - Select symbols and strategies
   - Switch between paper/live mode
   - Monitor positions and PnL
   - View statistics
   - Close all positions (realtime only)

## 📊 Creating New Strategies

1. Copy `strategies/example_strategy.py`
2. Rename it (e.g., `my_strategy.py`)
3. Modify the class name and implement your logic:

```python
from strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Dict, Any, Optional

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="My_Strategy")
        self.parameters = {
            'period': 14,
            'threshold': 70
        }
    
    def generate_signals(self, data: pd.DataFrame, 
                        symbol_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Your strategy logic here
        if condition_met:
            return {
                'action': 'BUY',
                'order_type': 'MARKET',
                'price': current_price,
                'stop_loss': sl_price,
                'target': target_price,
                'reason': 'Signal reason'
            }
        return None
    
    def get_parameters(self) -> Dict[str, Any]:
        return self.parameters
```

4. Save the file - bot will auto-load it on next run!

## 🔧 Configuration Options

### settings.yaml

```yaml
timezone: "Asia/Kolkata"

realtime_bot:
  schedule:
    start_time: "08:55"
    end_time: "16:05"
    weekdays_only: true
  ltp_update_interval: 600

backtest_bot:
  schedule:
    start_time: "06:00"
    end_time: "12:00"
    all_days: true
  session_duration_months: 4
  start_date: "2010-01-01"
```

## 📁 Project Structure

```
algo_by_gugan/
├── config/          # Configuration files
├── core/            # Core trading logic
├── strategies/      # Trading strategies
├── bots/            # Bot implementations
├── telegram/        # Telegram interfaces
├── utils/           # Utilities
├── data/            # Data storage
├── logs/            # Debug logs (auto-cleanup after 15 days)
└── trades/          # Trade CSV logs
```

## 📈 Trade Logs

Trade logs are saved as CSV files:
- `trades/backtest_trades.csv`
- `trades/realtime_trades.csv`

Import these directly into Excel/Google Sheets for analysis.

## 🔍 Monitoring

### View Logs
```bash
# Backtest logs
tail -f logs/backtest/$(date +%Y-%m-%d).log

# Realtime logs
tail -f logs/realtime/$(date +%Y-%m-%d).log
```

### Check Bot Status
```bash
# Check if bots are running
ps aux | grep python | grep run_

# Check tmux sessions
tmux ls
```

## 🛡️ Safety Features

1. **Paper Trading Mode**: Test strategies without real money
2. **Risk Management**: Automated position sizing based on capital and risk
3. **Max Trades Limit**: Prevent overtrading
4. **Stop Loss & Targets**: Built-in risk controls
5. **Telegram Alerts**: Real-time notifications for all trades

## 🔄 Backtest Carryover System

The backtest bot automatically:
1. Tracks progress for each symbol-strategy combination
2. Processes 4 months of data per day
3. Resumes from where it left off
4. Stores state in `data/backtest_state/`
5. Prevents duplicate processing

## 🎯 Broker Integration

To add a new broker:

1. Add credentials to `config/secrets.yaml`
2. Implement broker API calls in `core/broker_manager.py`
3. Download and save master lists

## ⚙️ Systemd Service (Optional)

For auto-start on VM boot:

```bash
# Create service file
sudo nano /etc/systemd/system/algo-realtime.service
```

```ini
[Unit]
Description=ALGO BY GUGAN Realtime Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/algo_by_gugan
ExecStart=/home/your-username/.venv/bin/python run_realtime.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable algo-realtime
sudo systemctl start algo-realtime
```

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `config/`
3. Ensure all dependencies are installed
4. Verify broker API credentials

## ⚠️ Disclaimer

This is trading software. Always:
- Test thoroughly in paper trading mode
- Understand your strategies
- Start with small capital
- Monitor actively
- Use proper risk management

Trading involves risk. Use at your own discretion.

---

Built with ❤️ for algorithmic traders