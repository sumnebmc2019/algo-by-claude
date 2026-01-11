# run_backtest.py
"""
Backtest Bot Launcher
"""

import sys
import signal
import asyncio
import threading
from bots.backtest_bot import BacktestBot
from tg.bt_telegram import BacktestTelegramBot
from utils.logger import setup_logger

logger = setup_logger("launcher", "backtest")

# Global bot instance
backtest_bot = None
telegram_bot = None

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    if backtest_bot:
        backtest_bot.is_running = False
    sys.exit(0)

async def run_telegram_bot(telegram_bot):
    """Run telegram bot in async context"""
    try:
        await telegram_bot.start_async()
    except Exception as e:
        logger.error(f"Telegram bot error: {e}", exc_info=True)

def telegram_thread_func(telegram_bot):
    """Thread function to run telegram bot"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run telegram bot
        loop.run_until_complete(run_telegram_bot(telegram_bot))
    except Exception as e:
        logger.error(f"Telegram thread error: {e}", exc_info=True)

def main():
    """Main entry point"""
    global backtest_bot, telegram_bot
    
    logger.info("=" * 60)
    logger.info("ALGO BY GUGAN - Backtest Bot")
    logger.info("=" * 60)
    
    try:
        # Initialize bot
        logger.info("Initializing Backtest Bot...")
        backtest_bot = BacktestBot()
        
        # Initialize telegram bot
        logger.info("Initializing Telegram Interface...")
        telegram_bot = BacktestTelegramBot(backtest_bot)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start telegram bot in separate thread with its own event loop
        telegram_thread = threading.Thread(
            target=telegram_thread_func,
            args=(telegram_bot,),
            daemon=True
        )
        telegram_thread.start()
        
        logger.info("Telegram bot started")
        
        # Start bot (blocking)
        logger.info("Starting backtest bot...")
        backtest_bot.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()