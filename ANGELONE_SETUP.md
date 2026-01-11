# AngelOne SmartAPI Setup Guide

## Complete Guide to Setup AngelOne with ALGO BY GUGAN

### Step 1: Get AngelOne API Credentials (5 minutes)

1. **Login to AngelOne Account**:
   - Go to [https://smartapi.angelbroking.com/](https://smartapi.angelbroking.com/)
   - Login with your AngelOne credentials

2. **Generate API Key**:
   - Navigate to "API" section
   - Click "Create App"
   - Fill in app details:
     - App Name: "ALGO BY GUGAN"
     - Redirect URL: https://127.0.0.1
   - Click "Create"
   - **Save the API Key** (looks like: SmGlKZoq)

3. **Note Your Details**:
   - Client ID: Your AngelOne client code (e.g., A123456)
   - Password: Your AngelOne login password

### Step 2: Setup TOTP (Two-Factor Authentication) (5 minutes)

AngelOne requires TOTP for API authentication. You have two options:

#### Option A: Use AngelOne Mobile App TOTP (Recommended)

1. **Get TOTP Secret from AngelOne App**:
   - Open AngelOne mobile app
   - Go to Settings → Two-Factor Authentication
   - Enable TOTP
   - You'll see a QR code and a secret key
   - **Copy the secret key** (format: ABCDEFGHIJKLMNOP)

2. **Update secrets.yaml**:
   ```yaml
   angelone:
     api_key: "SmGlKZoq"
     client_id: "A123456"
     password: "your_password"
     totp_secret: "ABCDEFGHIJKLMNOP"
     enabled: true
   ```

#### Option B: Generate New TOTP Secret

```bash
# Run this command to generate a new TOTP secret
python3 -c "import pyotp; print('TOTP Secret:', pyotp.random_base32())"

# Output: TOTP Secret: JBSWY3DPEHPK3PXP
# Use this in secrets.yaml
```

**Important**: If you generate a new TOTP secret, you need to set it up in your authenticator app (Google Authenticator, Authy, etc.) using the QR code or manual entry.

### Step 3: Update Configuration Files (3 minutes)

#### Update config/secrets.yaml:

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
    api_key: ""
    api_secret: ""
    enabled: false
  
  angelone:
    api_key: "SmGlKZoq"                    # Your API key
    client_id: "A123456"                   # Your client ID
    password: "your_password"              # Your password
    totp_secret: "ABCDEFGHIJKLMNOP"        # Your TOTP secret
    enabled: true
```

#### Update config/settings.yaml:

```yaml
default_settings:
  broker: "angelone"                       # Set as default broker
  segment: "NSE_FO"
  capital: 100000
  risk_per_trade: 2.0
  max_trades: 5
  mode: "paper"
  active_strategies: ["5EMA_PowerOfStocks"]  # Enable 5 EMA strategy
  active_symbols: []
```

### Step 4: Test Connection and Download Master Contracts (5 minutes)

```bash
# Activate virtual environment
source ~/.venv/bin/activate
cd ~/algo_by_gugan

# Run setup script
python setup_angelone.py
```

**Expected Output**:
```
============================================================
AngelOne SmartAPI Connection Test
============================================================

1. Initializing SmartAPI...
2. Generating TOTP...
   Current TOTP: 123456
3. Logging in...
✅ Login successful!
   User ID: A123456
   Name: YOUR NAME

============================================================
Downloading Master Contracts
============================================================

Downloading NSE (NSE_EQ)...
✅ Saved 2000 instruments to data/master_lists/angelone_NSE_EQ.json

Downloading NFO (NSE_FO)...
✅ Saved 15000 instruments to data/master_lists/angelone_NSE_FO.json

...

✅ Setup Complete!
```

### Step 5: Configure Active Symbols (10 minutes)

Now you need to activate symbols you want to trade.

#### Via Telegram Bot:

1. Start your bot: `/start`
2. Go to Settings → Segment/Symbols
3. Select "NSE_FO"
4. Search or filter symbols (e.g., "NIFTY", "BANKNIFTY")
5. Activate symbols you want to trade

#### Via Code (Temporary):

```python
# Add to run_realtime.py temporarily for setup
from core.symbol_manager import SymbolManager

symbol_manager = SymbolManager("angelone")
symbol_manager.load_master_list("NSE_FO")

# Add NIFTY Future
symbol_manager.add_active_symbol("NSE_FO", "NIFTY24JANFUT")

# Add BANKNIFTY Future
symbol_manager.add_active_symbol("NSE_FO", "BANKNIFTY24JANFUT")

# Check active symbols
print(symbol_manager.get_active_symbols())
```

### Step 6: Download Historical Data for Backtesting (Variable)

For the backtest bot to work, you need historical data.

#### Option A: Use AngelOne Historical API

```python
# Script to download historical data
from SmartApi import SmartConnect
import pyotp
import yaml
import pandas as pd
from datetime import datetime, timedelta

# Load config
with open('config/secrets.yaml', 'r') as f:
    secrets = yaml.safe_load(f)

# Login
smart_api = SmartConnect(api_key=secrets['brokers']['angelone']['api_key'])
totp = pyotp.TOTP(secrets['brokers']['angelone']['totp_secret']).now()
smart_api.generateSession(
    clientCode=secrets['brokers']['angelone']['client_id'],
    password=secrets['brokers']['angelone']['password'],
    totp=totp
)

# Download data for NIFTY (example)
params = {
    "exchange": "NFO",
    "symboltoken": "99926000",  # NIFTY token
    "interval": "FIVE_MINUTE",
    "fromdate": "2020-01-01 09:15",
    "todate": "2024-12-31 15:30"
}

hist_data = smart_api.getCandleData(params)

# Save to CSV
df = pd.DataFrame(
    hist_data['data'],
    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
)
df.to_csv('data/historical/NSE_FO_NIFTY24JANFUT.csv', index=False)
```

#### Option B: Use Third-Party Data Provider

- Download from NSE website
- Use paid data providers (TrueData, Upstox, etc.)
- Format as CSV with columns: timestamp, open, high, low, close, volume

### Step 7: Verify Setup (5 minutes)

```bash
# Test realtime bot
python run_realtime.py

# Check logs
tail -f logs/realtime/$(date +%Y-%m-%d).log

# Look for:
# - "AngelOne authentication successful"
# - "Loaded X symbols from NSE_FO"
# - "Loaded X strategies"
```

Press Ctrl+C to stop.

## Common Issues & Solutions

### Issue 1: TOTP Authentication Failed

**Error**: "Invalid TOTP" or "Authentication failed"

**Solution**:
1. Verify TOTP secret is correct in secrets.yaml
2. Check system time is synchronized:
   ```bash
   sudo ntpdate -s time.nist.gov
   ```
3. Generate new TOTP and update config
4. Make sure no extra spaces in secrets.yaml

### Issue 2: Rate Limit Exceeded

**Error**: "Rate limit exceeded"

**Solution**:
- AngelOne has API rate limits
- Reduce LTP update frequency in settings.yaml
- Don't make too many historical data requests

### Issue 3: Symbol Token Not Found

**Error**: "Token lookup not implemented"

**Solution**:
1. Make sure master contracts are downloaded
2. Check symbol name matches exactly with master list
3. Verify segment is correct (NSE_FO, not NSE)

### Issue 4: No Historical Data

**Error**: "No data available"

**Solution**:
1. Check date format: YYYY-MM-DD HH:MM
2. Don't request too old data (AngelOne limits: ~1 year)
3. Verify symbol token is correct
4. Check exchange is correct (NFO for futures)

## AngelOne API Limits

- **Rate Limits**: 
  - 3 API calls per second
  - 10,000 calls per day
  
- **Historical Data**:
  - Maximum 1 year of data per request
  - Only during market hours for some exchanges
  
- **Order Limits**:
  - Check your account limits
  - Different for different segments

## Testing Checklist

Before going live:

- [ ] Connection test successful
- [ ] Master contracts downloaded
- [ ] Active symbols configured
- [ ] Historical data available (for backtesting)
- [ ] 5 EMA strategy loaded
- [ ] Paper trading mode enabled
- [ ] Telegram bot responding
- [ ] LTP updates working
- [ ] Trade logging to CSV working
- [ ] Stop loss and targets configured

## Going Live

**Important**: Only after thorough testing in paper mode!

1. **Update settings via Telegram**:
   - Settings → Paper/Live → Switch to Live

2. **Start with small capital**:
   - Test with minimum capital first
   - Increase gradually after confidence

3. **Monitor actively**:
   - Watch first few trades closely
   - Check logs frequently
   - Verify orders in AngelOne app

4. **Set alerts**:
   - Enable Telegram notifications
   - Set up position alerts
   - Monitor system health

## Support Resources

- **AngelOne SmartAPI Docs**: [https://smartapi.angelbroking.com/docs](https://smartapi.angelbroking.com/docs)
- **SmartAPI GitHub**: [https://github.com/angel-one/smartapi-python](https://github.com/angel-one/smartapi-python)
- **Community**: AngelOne Telegram support group

---

**Ready to Trade!** 🚀

Your AngelOne integration is complete. Start with paper trading and monitor performance before going live.