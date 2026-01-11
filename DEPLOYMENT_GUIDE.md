# Complete Deployment Guide - ALGO BY GUGAN

## Step-by-Step Deployment on Azure Ubuntu VM

### Phase 1: VM Setup (5 minutes)

```bash
# 1. SSH into your Azure VM
ssh your-username@your-vm-ip

# 2. Update system packages
sudo apt update && sudo apt upgrade -y

# 3. Install required system packages
sudo apt install -y python3 python3-pip python3-venv tmux git nano
```

### Phase 2: Project Setup (10 minutes)

```bash
# 1. Create virtual environment in home directory
cd ~
python3 -m venv .venv
source .venv/bin/activate

# 2. Create project directory
mkdir -p algo_by_gugan
cd algo_by_gugan

# 3. Create directory structure
mkdir -p config
mkdir -p core
mkdir -p strategies
mkdir -p bots
mkdir -p telegram
mkdir -p utils
mkdir -p data/master_lists
mkdir -p data/historical
mkdir -p data/backtest_state
mkdir -p logs/backtest
mkdir -p logs/realtime
mkdir -p trades

# 4. Create __init__.py files
touch core/__init__.py
touch strategies/__init__.py
touch bots/__init__.py
touch telegram/__init__.py
touch utils/__init__.py

# 5. Verify structure
tree -L 2  # or: ls -R
```

### Phase 3: Install Dependencies (5 minutes)

```bash
# 1. Create requirements.txt
cat > requirements.txt << 'EOF'
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
EOF

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
pip list | grep -E "telegram|smartapi|pyotp|pandas|yaml"
```

### Phase 4: Telegram Bot Setup (10 minutes)

```bash
# 1. Open Telegram and message @BotFather
# 2. Create two bots:

# For Backtest Bot:
/newbot
# Name: ALGO Backtest
# Username: your_algo_backtest_bot
# Save the TOKEN

# For Realtime Bot:
/newbot
# Name: ALGO Realtime
# Username: your_algo_realtime_bot
# Save the TOKEN

# 3. Get your Chat ID
# Message @userinfobot on Telegram
# Save your CHAT_ID
```

### Phase 5: Configuration Files (15 minutes)

```bash
# 1. Create secrets.yaml
nano config/secrets.yaml
```

Paste and modify:
```yaml
telegram:
  backtest:
    bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    chat_id: "987654321"
  realtime:
    bot_token: "987654321:XYZabcDEFghiJKLmnoPQRstuVW"
    chat_id: "987654321"

brokers:
  zerodha:
    api_key: "your_zerodha_api_key"
    api_secret: "your_zerodha_api_secret"
    enabled: false
  
  angelone:
    api_key: "SmGlKZoq"
    client_id: "A123456"
    password: "1234"
    totp_secret: "ABCDEFGHIJKLMNOP"
    enabled: true
```

**For AngelOne TOTP Setup:**
```python
# Run this once to generate TOTP secret
python3 -c "import pyotp; print('TOTP Secret:', pyotp.random_base32())"
# Use the generated secret in secrets.yaml
```

```bash
# 2. Create settings.yaml
nano config/settings.yaml
```

Paste:
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

logging:
  retention_days: 15
  level: "DEBUG"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

paths:
  master_lists: "data/master_lists"
  historical_data: "data/historical"
  backtest_state: "data/backtest_state"
  logs_backtest: "logs/backtest"
  logs_realtime: "logs/realtime"
  trades_backtest: "trades/backtest_trades.csv"
  trades_realtime: "trades/realtime_trades.csv"

segments:
  - "NSE_EQ"
  - "NSE_FO"
  - "BSE_EQ"
  - "MCX_FO"
  - "CDS_FO"

default_settings:
  broker: "angelone"
  segment: "NSE_FO"
  capital: 100000
  risk_per_trade: 2.0
  max_trades: 5
  mode: "paper"
  active_strategies: ["5EMA_PowerOfStocks"]
  active_symbols: []
```

### Phase 6: Setup AngelOne Connection (10 minutes)

```bash
# 1. Copy the setup script (setup_angelone.py)
nano setup_angelone.py
# Paste the setup_angelone.py content

# 2. Run the setup script to test connection and download master contracts
python setup_angelone.py

# 3. Verify master contracts are downloaded
ls -lh data/master_lists/

# You should see:
# angelone_NSE_EQ.json
# angelone_NSE_FO.json
# angelone_BSE_EQ.json
# angelone_MCX_FO.json
# angelone_CDS_FO.json
```

### Phase 7: Copy All Python Files (20 minutes)

Copy all the provided Python files into their respective directories:

```
utils/logger.py
utils/trade_logger.py
utils/helpers.py
core/symbol_manager.py
core/position_manager.py
core/data_manager.py
core/broker_manager.py
strategies/base_strategy.py
strategies/strategy_loader.py
strategies/example_strategy.py
strategies/ema5_power_of_stocks.py  ← NEW: 5 EMA Strategy
bots/backtest_bot.py
bots/realtime_bot.py
telegram/bt_telegram.py
telegram/rt_telegram.py
run_backtest.py
run_realtime.py
setup_angelone.py  ← NEW: AngelOne setup script
```

**Quick method using nano:**
```bash
# For each file:
nano utils/logger.py
# Paste content, Ctrl+X, Y, Enter

# Or use SCP from your local machine:
scp -r local_algo_project/* username@vm-ip:~/algo_by_gugan/
```

### Phase 7: Prepare Master Lists (Variable time)

```bash
# 1. Download master symbol list from your broker
# 2. Convert to JSON format if needed

# Example structure:
nano data/master_lists/zerodha_NSE_FO.json
```

```json
[
  {
    "symbol": "NIFTY24JANFUT",
    "token": "256265",
    "lot_size": 50,
    "tick_size": 0.05,
    "exchange": "NFO"
  },
  {
    "symbol": "BANKNIFTY24JANFUT",
    "token": "260105",
    "lot_size": 25,
    "tick_size": 0.05,
    "exchange": "NFO"
  }
]
```

### Phase 8: Historical Data Preparation (Variable time)

```bash
# 1. Download historical data from broker or data provider
# 2. Format as CSV

# Example:
nano data/historical/NSE_FO_NIFTY24JANFUT.csv
```

```csv
timestamp,open,high,low,close,volume
2024-01-01 09:15:00,21500.00,21550.00,21480.00,21530.00,1000000
2024-01-01 09:16:00,21530.00,21560.00,21520.00,21545.00,950000
```

### Phase 9: Test Run (10 minutes)

```bash
# 1. Activate virtual environment
source ~/.venv/bin/activate
cd ~/algo_by_gugan

# 2. Test backtest bot
python run_backtest.py
# Press Ctrl+C after verifying it starts

# 3. Test realtime bot
python run_realtime.py
# Press Ctrl+C after verifying it starts

# 4. Check for errors in logs
cat logs/backtest/$(date +%Y-%m-%d).log
cat logs/realtime/$(date +%Y-%m-%d).log
```

### Phase 10: Production Deployment with tmux (5 minutes)

```bash
# 1. Start backtest bot in tmux
tmux new-session -d -s algo_backtest 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_backtest.py'

# 2. Start realtime bot in tmux
tmux new-session -d -s algo_realtime 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_realtime.py'

# 3. Verify sessions are running
tmux ls

# 4. Test Telegram bots
# Open Telegram and message both bots with /start
```

### Phase 11: Monitoring Setup (5 minutes)

```bash
# 1. Create monitoring script
cat > ~/check_bots.sh << 'EOF'
#!/bin/bash
echo "=== ALGO BOT STATUS ==="
echo ""
echo "Tmux Sessions:"
tmux ls
echo ""
echo "Python Processes:"
ps aux | grep python | grep run_
echo ""
echo "Recent Backtest Logs:"
tail -5 ~/algo_by_gugan/logs/backtest/$(date +%Y-%m-%d).log
echo ""
echo "Recent Realtime Logs:"
tail -5 ~/algo_by_gugan/logs/realtime/$(date +%Y-%m-%d).log
EOF

chmod +x ~/check_bots.sh

# 2. Run monitoring
~/check_bots.sh
```

### Phase 12: Auto-Start on Boot (Optional)

```bash
# 1. Create systemd service for Realtime Bot
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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Create systemd service for Backtest Bot
sudo nano /etc/systemd/system/algo-backtest.service
```

```ini
[Unit]
Description=ALGO BY GUGAN Backtest Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/algo_by_gugan
ExecStart=/home/your-username/.venv/bin/python run_backtest.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 3. Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable algo-realtime
sudo systemctl enable algo-backtest
sudo systemctl start algo-realtime
sudo systemctl start algo-backtest

# 4. Check status
sudo systemctl status algo-realtime
sudo systemctl status algo-backtest
```

## Daily Operations

### Starting Bots
```bash
# Using tmux
tmux new-session -d -s algo_backtest 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_backtest.py'
tmux new-session -d -s algo_realtime 'cd ~/algo_by_gugan && source ~/.venv/bin/activate && python run_realtime.py'

# Using systemd
sudo systemctl start algo-backtest
sudo systemctl start algo-realtime
```

### Stopping Bots
```bash
# Using tmux
tmux kill-session -t algo_backtest
tmux kill-session -t algo_realtime

# Using systemd
sudo systemctl stop algo-backtest
sudo systemctl stop algo-realtime
```

### Viewing Logs
```bash
# Today's logs
tail -f logs/backtest/$(date +%Y-%m-%d).log
tail -f logs/realtime/$(date +%Y-%m-%d).log

# Specific date
tail -f logs/backtest/2024-01-15.log

# Last 100 lines
tail -100 logs/realtime/$(date +%Y-%m-%d).log
```

### Viewing Trade Logs
```bash
# Open in terminal
cat trades/realtime_trades.csv | column -t -s','

# Download to local machine
scp username@vm-ip:~/algo_by_gugan/trades/*.csv ./
```

### Attaching to Running Bots
```bash
# Attach to backtest bot
tmux attach -t algo_backtest
# Detach: Ctrl+B then D

# Attach to realtime bot
tmux attach -t algo_realtime
# Detach: Ctrl+B then D
```

## Troubleshooting

### Bot Not Starting
```bash
# Check Python errors
python run_realtime.py

# Check dependencies
pip list | grep -E "telegram|pandas|yaml"

# Check configuration
cat config/secrets.yaml
cat config/settings.yaml
```

### Telegram Not Working
```bash
# Test bot token
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Check logs
grep -i telegram logs/realtime/$(date +%Y-%m-%d).log
```

### Data Issues
```bash
# Check master lists
ls -lh data/master_lists/

# Check historical data
ls -lh data/historical/

# Verify CSV format
head -5 data/historical/NSE_FO_NIFTY24JANFUT.csv
```

### Performance Issues
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check CPU usage
top

# Check bot processes
ps aux | grep python
```

## Maintenance Tasks

### Weekly
- Review trade logs
- Check bot performance
- Verify log file sizes
- Update strategies if needed

### Monthly
- Backup trade logs
- Review and optimize strategies
- Update broker credentials if needed
- Check for Python package updates

### Quarterly
- Full system backup
- Performance analysis
- Strategy backtesting review
- Infrastructure assessment

## Security Best Practices

1. **Never commit secrets.yaml to git**
2. **Use strong passwords for VM access**
3. **Enable firewall on Azure**
4. **Regularly update system packages**
5. **Monitor unauthorized access attempts**
6. **Use SSH keys instead of passwords**
7. **Keep broker API keys secure**
8. **Regularly rotate credentials**

## Emergency Procedures

### Close All Positions Immediately
```bash
# Via Telegram: Use "Close All" button

# Via CLI:
python -c "
from bots.realtime_bot import RealtimeBot
bot = RealtimeBot()
bot.close_all_positions()
"
```

### Stop All Trading
```bash
# Kill all bots immediately
tmux kill-server

# Or
sudo systemctl stop algo-backtest
sudo systemctl stop algo-realtime
```

## Support Checklist

When seeking help, provide:
- [ ] Error logs from today
- [ ] Configuration files (without secrets)
- [ ] Bot version and Python version
- [ ] Steps to reproduce the issue
- [ ] Expected vs actual behavior

---

**Deployment Complete!** 🎉

Your algo trading system is now live. Monitor via Telegram and logs. Start with paper trading before going live.

Good luck with your trading! 📈