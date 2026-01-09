# config/secrets.yaml
"""
Realtime Bot Launcher
"""

import sys
import signal
from bots.realtime_bot import RealtimeBot
from telegram.rt_telegram import RealtimeTelegramBot
from utils.logger import setup_logger
import threading

logger = setup_logger("launcher", "realtime")

# Global bot instances
realtime_bot = None
telegram_bot = None

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    if realtime_bot:
        realtime_bot.is_running = False
    sys.exit(0)

def main():
    """Main entry point"""
    global realtime_bot, telegram_bot
    
    logger.info("=" * 60)
    logger.info("ALGO BY GUGAN - Realtime Bot")
    logger.info("=" * 60)
    
    try:
        # Initialize bots
        logger.info("Initializing Realtime Bot...")
        realtime_bot = RealtimeBot()
        
        logger.info("Initializing Telegram Interface...")
        telegram_bot = RealtimeTelegramBot(realtime_bot)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start telegram bot in separate thread
        telegram_thread = threading.Thread(target=telegram_bot.start, daemon=True)
        telegram_thread.start()
        
        logger.info("Telegram bot started")
        
        # Start realtime bot (blocking)
        logger.info("Starting trading bot...")
        realtime_bot.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()