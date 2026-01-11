# Deployment Checklist - ALGO BY GUGAN

## Pre-Deployment Checklist

### Prerequisites
- [ ] Azure Ubuntu VM is ready and accessible
- [ ] AngelOne trading account is active
- [ ] AngelOne API access is enabled
- [ ] Telegram account is ready
- [ ] You have 1-2 hours of uninterrupted time

### Account Setup
- [ ] AngelOne API Key obtained
- [ ] AngelOne Client ID noted
- [ ] AngelOne password ready
- [ ] TOTP secret generated or obtained
- [ ] Two Telegram bots created via @BotFather
- [ ] Telegram Chat ID obtained from @userinfobot

## Deployment Checklist

### Phase 1: VM Setup
- [ ] Connected to VM via SSH
- [ ] System packages updated (`sudo apt update && upgrade`)
- [ ] Python 3.8+ installed
- [ ] pip installed
- [ ] venv installed
- [ ] tmux installed

### Phase 2: Project Setup
- [ ] Virtual environment created (`python3 -m venv .venv`)
- [ ] Virtual environment activated
- [ ] Project directory created (`algo_by_gugan`)
- [ ] All subdirectories created
- [ ] `__init__.py` files created in module directories

### Phase 3: Dependencies
- [ ] `requirements.txt` created with all packages
- [ ] All packages installed successfully
- [ ] Installation verified (`pip list`)
- [ ] No installation errors

### Phase 4: Configuration Files
- [ ] `config/secrets.yaml` created
- [ ] Backtest bot token added
- [ ] Realtime bot token added
- [ ] Chat ID added
- [ ] AngelOne API key added
- [ ] AngelOne client ID added
- [ ] AngelOne password added
- [ ] AngelOne TOTP secret added
- [ ] Broker enabled flag set to `true`
- [ ] `config/settings.yaml` created
- [ ] Timezone set to Asia/Kolkata
- [ ] Bot schedules configured
- [ ] Default broker set to `angelone`
- [ ] 5EMA strategy enabled in active_strategies

### Phase 5: Python Files
- [ ] All utils files copied (`logger.py`, `trade_logger.py`, `helpers.py`)
- [ ] All core files copied (4 files)
- [ ] All strategy files copied (4 files)
- [ ] Both bot files copied (2 files)
- [ ] Both telegram files copied (2 files)
- [ ] `run_backtest.py` copied
- [ ] `run_realtime.py` copied
- [ ] `setup_angelone.py` copied
- [ ] All files have correct permissions

### Phase 6: AngelOne Setup
- [ ] `setup_angelone.py` executed successfully
- [ ] Login successful message received
- [ ] Master contracts downloaded for NSE_EQ
- [ ] Master contracts downloaded for NSE_FO
- [ ] Master contracts downloaded for BSE_EQ
- [ ] Master contracts downloaded for MCX_FO
- [ ] Master contracts downloaded for CDS_FO
- [ ] LTP test passed
- [ ] Files exist in `data/master_lists/`

### Phase 7: Testing
- [ ] `run_realtime.py` starts without errors
- [ ] Logs are being created in `logs/realtime/`
- [ ] No Python import errors
- [ ] No configuration errors
- [ ] Bot stops cleanly with Ctrl+C

### Phase 8: Telegram Setup
- [ ] Messaged realtime bot on Telegram
- [ ] `/start` command works
- [ ] Main menu displays correctly
- [ ] Settings menu accessible
- [ ] Stats menu accessible
- [ ] All buttons respond

## Post-Deployment Checklist

### Day 1: Initial Setup
- [ ] Bot running in tmux session
- [ ] tmux session verified (`tmux ls`)
- [ ] Logs are updating
- [ ] Active symbols configured via Telegram
- [ ] 5EMA strategy is enabled
- [ ] Paper trading mode confirmed
- [ ] First LTP update successful
- [ ] No error messages in logs

### Day 2-7: Paper Trading
- [ ] Bot runs for full market hours
- [ ] LTP updates every 10 minutes
- [ ] Trade signals being generated
- [ ] Trades logged to CSV
- [ ] Telegram notifications working
- [ ] Position tracking working
- [ ] Stop loss calculations correct
- [ ] Target calculations correct

### Week 2: Performance Review
- [ ] At least 10 paper trades executed
- [ ] Trade CSV downloaded and analyzed
- [ ] Win rate calculated
- [ ] Average profit per trade calculated
- [ ] Strategy performance reviewed
- [ ] Risk management verified
- [ ] No system errors occurred
- [ ] Logs reviewed for issues

### Week 3: Optimization
- [ ] Strategy parameters reviewed
- [ ] Symbol selection optimized
- [ ] Risk percentage adjusted if needed
- [ ] Maximum trades limit reviewed
- [ ] Performance improving or stable
- [ ] System running smoothly

### Week 4: Live Trading Prep
- [ ] Consistent paper trading profits
- [ ] Win rate acceptable (>45%)
- [ ] Risk management tested
- [ ] Emergency procedures tested
- [ ] Backup systems in place
- [ ] Starting capital decided
- [ ] Mental preparation complete

## Live Trading Checklist (Only After Successful Paper Trading!)

### Pre-Live
- [ ] At least 2 weeks of profitable paper trading
- [ ] System stability verified
- [ ] All safety features tested
- [ ] Starting with minimum capital
- [ ] Emergency stop procedures ready
- [ ] Broker account funded
- [ ] All risks understood

### Go-Live
- [ ] Switch to live mode via Telegram
- [ ] Verify mode is "LIVE" in settings
- [ ] First trade monitored manually
- [ ] Order execution verified in broker app
- [ ] Position tracking accurate
- [ ] Stop loss placement verified
- [ ] Telegram notifications working

### First Day Live
- [ ] Monitor ALL trades in real-time
- [ ] Verify each order in broker app
- [ ] Check position updates
- [ ] Monitor PnL accuracy
- [ ] Test emergency close all
- [ ] Keep manual override ready
- [ ] Stay alert throughout market hours

### First Week Live
- [ ] Daily performance review
- [ ] Compare with paper trading results
- [ ] Verify all trades logged correctly
- [ ] Check slippage is acceptable
- [ ] Monitor system performance
- [ ] Review and adjust if needed
- [ ] Keep detailed notes

## Maintenance Checklist

### Daily
- [ ] Check bot is running (`tmux ls`)
- [ ] Review today's trades
- [ ] Check for errors in logs
- [ ] Verify LTP updates
- [ ] Telegram bot responding
- [ ] Disk space sufficient
- [ ] No unusual activity

### Weekly
- [ ] Download and backup trade CSV
- [ ] Calculate weekly performance
- [ ] Review win rate and profit
- [ ] Check system resource usage
- [ ] Update strategies if needed
- [ ] Review logs for warnings
- [ ] Test telegram controls

### Monthly
- [ ] Full performance analysis
- [ ] Strategy optimization review
- [ ] System updates check
- [ ] Credential rotation
- [ ] Backup all data
- [ ] Infrastructure review
- [ ] Cost analysis (if applicable)

## Emergency Procedures Checklist

### System Issues
- [ ] Know how to stop bot immediately (`tmux kill-session`)
- [ ] Know how to close all positions (Telegram button)
- [ ] Have broker app installed on phone
- [ ] Can place manual orders if needed
- [ ] Have support contacts ready
- [ ] Know how to check logs quickly

### Market Issues
- [ ] Know when to stop trading (3 losses rule)
- [ ] Have daily loss limit defined
- [ ] Know how to switch to paper mode
- [ ] Can disable strategies quickly
- [ ] Have exit plan prepared

### Account Issues
- [ ] Broker support contact ready
- [ ] API limits understood
- [ ] Know how to check order status
- [ ] Have backup broker configured
- [ ] Account details accessible

## Success Criteria

### Technical Success
- [ ] Bot runs 99%+ uptime during market hours
- [ ] No system crashes
- [ ] All trades executed as planned
- [ ] Accurate position tracking
- [ ] Reliable logging
- [ ] Fast response times

### Trading Success (Paper Mode)
- [ ] Win rate > 45%
- [ ] Positive net profit
- [ ] Controlled drawdown
- [ ] Consistent strategy execution
- [ ] Risk management working
- [ ] No manual intervention needed

### Trading Success (Live Mode)
- [ ] Profitable after 1 month
- [ ] Risk-adjusted returns positive
- [ ] Psychology manageable
- [ ] Execution quality good
- [ ] Slippage acceptable
- [ ] Consistent with paper trading

## Red Flags - Stop and Review

### Stop Immediately If:
- [ ] 3 consecutive losses
- [ ] Daily loss exceeds 5% of capital
- [ ] System errors occurring frequently
- [ ] Orders not executing properly
- [ ] Position tracking incorrect
- [ ] Unusual broker behavior
- [ ] Telegram bot not responding
- [ ] Feeling emotional about trades

### Review and Adjust If:
- [ ] Win rate dropping below 40%
- [ ] Average loss increasing
- [ ] Strategy signals too frequent/rare
- [ ] System running slowly
- [ ] Logs showing warnings
- [ ] Telegram delays
- [ ] Trade execution delays

## Completion Sign-Off

I confirm that I have:
- [ ] Completed all pre-deployment steps
- [ ] Successfully deployed the system
- [ ] Tested all functionality
- [ ] Understood all risks
- [ ] Prepared emergency procedures
- [ ] Started in paper trading mode
- [ ] Will monitor actively
- [ ] Will review performance regularly
- [ ] Will not rush to live trading
- [ ] Will seek help if needed

**Signature**: ________________
**Date**: ________________
**Mode**: [ ] Paper  [ ] Live

---

## Notes Section

Use this space to track important information:

**Deployment Date**: ________________
**First Trade Date**: ________________
**Live Trading Date**: ________________

**Initial Capital**: ₹________________
**Risk per Trade**: ________________%
**Max Positions**: ________________

**Important Observations**:
_____________________________________________
_____________________________________________
_____________________________________________

**Issues Encountered**:
_____________________________________________
_____________________________________________
_____________________________________________

**Performance Notes**:
_____________________________________________
_____________________________________________
_____________________________________________