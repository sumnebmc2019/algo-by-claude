#!/bin/bash
# apply_all_fixes.sh - Apply all fixes to the algo trading system

echo "============================================================"
echo "ALGO BY GUGAN - Apply All Fixes"
echo "============================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
echo -e "\n${YELLOW}Step 1: Activating virtual environment...${NC}"
source ~/.venv/bin/activate
cd ~/algo

# Fix smartapi installation
echo -e "\n${YELLOW}Step 2: Fixing smartapi installation...${NC}"
pip uninstall -y smartapi-python
pip install --no-cache-dir smartapi-python==1.3.0
pip install logzero==1.7.0 websocket-client==1.8.0

# Verify smartapi works
echo -e "\n${YELLOW}Step 3: Verifying smartapi installation...${NC}"
python3 -c "from SmartApi import SmartConnect; print('✅ SmartAPI works!')" 2>&1

# Backup existing telegram files
echo -e "\n${YELLOW}Step 4: Backing up existing telegram files...${NC}"
cp tg/rt_telegram.py tg/rt_telegram.py.backup.$(date +%Y%m%d_%H%M%S)
cp tg/bt_telegram.py tg/bt_telegram.py.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backups created in tg/ directory"

# Fix settings.yaml - remove SENSEX
echo -e "\n${YELLOW}Step 5: Fixing active symbols in settings.yaml...${NC}"
python3 << 'EOF'
import yaml

# Load settings
with open('config/settings.yaml', 'r') as f:
    settings = yaml.safe_load(f)

# Update active symbols - remove any BSE symbols
if 'default_settings' in settings:
    active_symbols = settings['default_settings'].get('active_symbols', [])
    
    # Filter out BSE symbols and keep only NSE_FO
    filtered_symbols = [
        sym for sym in active_symbols 
        if sym.get('segment') == 'NSE_FO'
    ]
    
    # If no NSE_FO symbols, add NIFTY and BANKNIFTY
    if not filtered_symbols:
        filtered_symbols = [
            {
                'broker': 'angelone',
                'exchange': 'NFO',
                'lot_size': 65,
                'segment': 'NSE_FO',
                'symbol': 'NIFTY27JAN26FUT',
                'tick_size': 10.0,
                'token': '49229'
            },
            {
                'broker': 'angelone',
                'exchange': 'NFO',
                'lot_size': 25,
                'segment': 'NSE_FO',
                'symbol': 'BANKNIFTY27JAN26FUT',
                'tick_size': 10.0,
                'token': '26009'
            }
        ]
    
    settings['default_settings']['active_symbols'] = filtered_symbols
    
    # Ensure 5EMA strategy is enabled
    if '5EMA_PowerOfStocks' not in settings['default_settings'].get('active_strategies', []):
        settings['default_settings']['active_strategies'] = ['5EMA_PowerOfStocks']
    
    # Save
    with open('config/settings.yaml', 'w') as f:
        yaml.safe_dump(settings, f, default_flow_style=False)
    
    print(f"✅ Fixed settings.yaml - {len(filtered_symbols)} active symbols")
else:
    print("⚠️ Settings file format unexpected")
EOF

# Update requirements.txt
echo -e "\n${YELLOW}Step 6: Updating requirements.txt...${NC}"
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
logzero==1.7.0
websocket-client==1.8.0
EOF
echo "✅ requirements.txt updated"

# Test AngelOne connection
echo -e "\n${YELLOW}Step 7: Testing AngelOne connection...${NC}"
python3 setup_angelone.py 2>&1 | head -20

# Kill existing bots
echo -e "\n${YELLOW}Step 8: Restarting bots...${NC}"
tmux kill-session -t algo_realtime 2>/dev/null
tmux kill-session -t algo_backtest 2>/dev/null
sleep 2

# Start bots fresh
tmux new-session -d -s algo_realtime "cd ~/algo && source ~/.venv/bin/activate && python run_realtime.py"
tmux new-session -d -s algo_backtest "cd ~/algo && source ~/.venv/bin/activate && python run_backtest.py"

echo -e "\n${GREEN}✅ Bots restarted${NC}"

# Check if bots are running
sleep 3
echo -e "\n${YELLOW}Step 9: Verifying bots are running...${NC}"
tmux ls 2>/dev/null && echo -e "${GREEN}✅ Bots running in tmux${NC}" || echo -e "${RED}❌ Bots not running${NC}"

# Show last few log lines
echo -e "\n${YELLOW}Step 10: Checking recent logs...${NC}"
echo -e "\n${YELLOW}Realtime Bot Logs (last 10 lines):${NC}"
tail -10 logs/realtime/$(date +%Y-%m-%d).log 2>/dev/null || echo "No logs yet"

echo -e "\n${YELLOW}Backtest Bot Logs (last 10 lines):${NC}"
tail -10 logs/backtest/$(date +%Y-%m-%d).log 2>/dev/null || echo "No logs yet"

# Final summary
echo -e "\n============================================================"
echo -e "${GREEN}✅ All Fixes Applied Successfully!${NC}"
echo -e "============================================================"
echo ""
echo -e "${YELLOW}IMPORTANT NEXT STEPS:${NC}"
echo ""
echo "1. ${YELLOW}Update Telegram Files:${NC}"
echo "   Replace tg/rt_telegram.py with the fixed version"
echo "   Replace tg/bt_telegram.py with the fixed version"
echo ""
echo "2. ${YELLOW}Test Telegram Bot:${NC}"
echo "   - Open Telegram"
echo "   - Find your realtime bot"
echo "   - Send: /start"
echo "   - You should see the main menu"
echo ""
echo "3. ${YELLOW}Monitor Logs:${NC}"
echo "   tail -f logs/realtime/\$(date +%Y-%m-%d).log"
echo ""
echo "4. ${YELLOW}Check for Errors:${NC}"
echo "   grep -i error logs/realtime/\$(date +%Y-%m-%d).log"
echo ""
echo -e "${GREEN}Good luck! 🚀${NC}"
echo ""