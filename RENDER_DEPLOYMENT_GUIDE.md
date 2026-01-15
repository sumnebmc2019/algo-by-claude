# Render.com Deployment Guide - ALGO BY GUGAN

## Why Render.com?

- ✅ **Free tier available** (750 hours/month)
- ✅ **Auto-sleep after 15 mins** (but works for scheduled bots)
- ✅ **Easy GitHub integration**
- ✅ **No credit card required** for free tier
- ✅ **Better than Heroku** (which removed free tier)
- ✅ **Background workers** support
- ✅ **Environment variables** built-in

---

## Issues Fixed

### 1. **Pandas + Python 3.13 Incompatibility** ✅ FIXED

**Problem:** `pandas==2.1.4` doesn't compile on Python 3.13

**Solution:**
- Changed to `pandas==2.2.0` (Python 3.13 compatible)
- Updated `numpy==1.26.4` (compatible with pandas 2.2.0)
- Set `runtime.txt` to `python-3.11.0` for Render.com

### 2. **Separate Bot Settings Not Working** ✅ FIXED

**Problem:** Backtest bot wasn't loading separate settings

**Solution:**
- Updated `backtest_bot.py` to use `get_bot_settings('backtest')`
- Added `_load_backtest_specific_settings()` method
- Properly loads `session_duration_months` and `start_date`

### 3. **Emojis Not Displaying** ✅ FIXED

**Problem:** Emojis removed but you want them back

**Solution:**
- Restored ALL emojis (✅❌⚠️🚀📊💰🟢🔴⚪)
- Proper UTF-8 encoding in logger
- Works on Ubuntu/Oracle Cloud

### 4. **Health Endpoint Missing** ✅ ADDED

**Problem:** Render.com needs health checks for web services

**Solution:**
- Added HTTP server on port 8080
- Endpoint: `/health`
- Returns "healthy" or "starting"

---

## Step-by-Step Deployment

### Step 1: Prepare Repository

```bash
# Update files
cd ~/algo

# Replace requirements.txt
# (Use the fixed version from artifact)

# Update runtime.txt
echo "python-3.11.0" > runtime.txt

# Update run_realtime.py
# (Use version with health endpoint)

# Update backtest_bot.py
# (Use version with separate settings)

# Commit changes
git add .
git commit -m "Fix Python 3.13 compatibility and add Render support"
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (free, no credit card)
3. Connect your GitHub account

### Step 3: Deploy Realtime Bot (Web Service)

1. **New Web Service**:
   - Dashboard → "New" → "Web Service"
   - Connect repository: `algo-by-claude`
   - Branch: `main`

2. **Configure Service**:
   - Name: `algo-realtime-bot`
   - Region: Singapore (or nearest)
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command:
     ```
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - Start Command:
     ```
     python run_realtime.py
     ```

3. **Select Plan**:
   - Free (750 hours/month, sleeps after 15 mins)
   - OR Starter ($7/month, always on) - Recommended

4. **Add Environment Variables**:
   Click "Environment" → "Add Environment Variable"
   
   ```
   TELEGRAM_REALTIME_TOKEN=your_token_here
   TELEGRAM_REALTIME_CHAT_IDS=id1,id2,id3
   TELEGRAM_BACKTEST_TOKEN=your_token_here
   TELEGRAM_BACKTEST_CHAT_IDS=id1,id2,id3
   ANGELONE_API_KEY=your_key
   ANGELONE_CLIENT_ID=your_id
   ANGELONE_PASSWORD=your_password
   ANGELONE_TOTP_SECRET=your_secret
   ANGELONE_ENABLED=true
   RENDER_ENVIRONMENT=production
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for first build

### Step 4: Deploy Backtest Bot (Background Worker)

1. **New Background Worker**:
   - Dashboard → "New" → "Background Worker"
   - Same repository: `algo-by-claude`

2. **Configure Worker**:
   - Name: `algo-backtest-bot`
   - Region: Same as realtime bot
   - Runtime: `Python 3`
   - Build Command: (same as above)
   - Start Command:
     ```
     python run_backtest.py
     ```

3. **Environment Variables**:
   - Same as realtime bot (copy them)

4. **Deploy**:
   - Click "Create Background Worker"

### Step 5: Alternative - Use render.yaml (Automated)

Create `render.yaml` in repo root (use artifact version), then:

1. Dashboard → "New" → "Blueprint"
2. Connect repo
3. Render auto-deploys both services!

---

## Monitoring

### View Logs:

1. Go to Render Dashboard
2. Click on service name
3. Click "Logs" tab
4. Watch real-time logs

**Look for:**
- ✅ "AngelOne authentication successful"
- ✅ "Telegram bot started"
- ✅ "Loaded X symbols"
- ✅ No errors

### Health Check:

Visit: `https://your-service.onrender.com/health`

Should return: `healthy`

### Telegram:

Send `/start` to your bot - should work immediately!

---

## Free Tier Limitations

### What You Get:
- ✅ 750 hours/month per service
- ✅ Automatic SSL
- ✅ GitHub auto-deploy
- ✅ Environment variables
- ✅ Logs

### Limitations:
- ⚠️ **Sleeps after 15 mins** of inactivity
- ⚠️ **Slower builds** than paid tier
- ⚠️ **Limited CPU/RAM**

### Workaround for Sleep:

**Option A: Upgrade to Starter ($7/month)**
- Always on
- Faster builds
- More resources

**Option B: Keep Awake (Free)**

Create a simple cron-job.org or UptimeRobot to ping:
```
https://your-service.onrender.com/health
```
Every 10 minutes.

**Option C: Use for Scheduled Tasks Only**
- Backtest bot runs at 6 AM daily
- Realtime bot during market hours (8:55 AM - 4:05 PM)
- Sleep doesn't matter outside these times!

---

## Comparison: Render vs Others

| Platform | Cost | Always On | Setup Time | Best For |
|----------|------|-----------|------------|----------|
| **Render** | Free/\$7 | No/Yes | 10 min | Easy start |
| Railway | \$5 credit | Yes | 5 min | Simple apps |
| Oracle Cloud | FREE | Yes | 30 min | Production |
| Google Cloud | $300/90d | Yes | 30 min | Testing |
| Heroku | Paid only | Yes | - | Not recommended |

---

## Troubleshooting

### Build Fails: "Pandas compilation error"

**Solution:**
- Ensure `runtime.txt` has `python-3.11.0`
- Ensure `requirements.txt` has `pandas==2.2.0`

### Service Won't Start

**Check logs for:**
- Missing environment variables
- AngelOne auth failure
- Telegram token issues

**Fix:**
- Add all environment variables
- Test locally first

### Bot Sleeping Too Often

**Solutions:**
1. Upgrade to Starter plan ($7/month)
2. Use UptimeRobot to ping /health
3. Accept it (works for scheduled bots)

### Telegram Not Working

**Check:**
- Environment variables set correctly
- Bot tokens valid
- Chat IDs correct
- Logs for errors

**Test locally first:**
```bash
python test_telegram.py
```

---

## Cost Analysis

### Free Tier:
- **Cost:** $0
- **Services:** 2 (realtime + backtest)
- **Hours:** 750/month each = 1500 total
- **Good for:** Testing, development, scheduled tasks

### Starter Plan:
- **Cost:** $7/month per service = $14/month total
- **Services:** Both always on
- **Hours:** Unlimited
- **Good for:** Production, live trading

### Recommendation:

**For Paper Trading:** Free tier is perfect!
- Bot only needs to run during market hours
- Sleep doesn't matter outside trading time

**For Live Trading:** Upgrade to Starter
- Always on = no missed signals
- Faster builds
- More reliable

---

## Deploy Checklist

- [ ] Fixed `requirements.txt` (pandas 2.2.0)
- [ ] Added `runtime.txt` (python-3.11.0)
- [ ] Updated `run_realtime.py` (health endpoint)
- [ ] Updated `backtest_bot.py` (separate settings)
- [ ] Created `render.yaml` (optional but recommended)
- [ ] Pushed to GitHub
- [ ] Created Render account
- [ ] Deployed realtime bot
- [ ] Deployed backtest bot
- [ ] Added environment variables
- [ ] Checked logs for errors
- [ ] Tested /health endpoint
- [ ] Tested Telegram bot

---

## Quick Commands

### Local Testing:
```bash
# Test locally first
python test_telegram.py
python setup_angelone.py
python run_realtime.py
```

### Git Commands:
```bash
# Update and push
git add .
git commit -m "Add Render support"
git push origin main
# Render auto-deploys!
```

### Check Status:
```bash
# Health check
curl https://your-service.onrender.com/health

# Should return: "healthy"
```

---

## Next Steps After Deployment

1. **Monitor First Day:**
   - Watch logs continuously
   - Verify trades in Telegram
   - Check no errors

2. **Test Paper Trading:**
   - Run for 1 week minimum
   - Analyze performance
   - Verify strategy works

3. **Optimize Settings:**
   - Adjust symbols if needed
   - Tune risk parameters
   - Test different strategies

4. **Consider Upgrade:**
   - If profitable, upgrade to Starter
   - Always-on for live trading
   - Better performance

---

## Support Resources

- **Render Docs:** [render.com/docs](https://render.com/docs)
- **Render Status:** [status.render.com](https://status.render.com)
- **Community:** [community.render.com](https://community.render.com)
- **Support:** [help.render.com](https://help.render.com)

---

**Your bot is now ready to deploy on Render.com! 🚀**

Start with free tier, test thoroughly, then upgrade if needed.