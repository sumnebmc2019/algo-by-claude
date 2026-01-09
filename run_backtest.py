# config/secrets.yaml
"""
Backtest Bot Launcher
"""

import sys
import signal
from bots.backtest_bot import BacktestBot
from utils.logger import setup_logger

logger = setup_logger("launcher", "backtest")

# Global bot instance
backtest_bot = None

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    if backtest_bot:
        backtest_bot.is_running = False
    sys.exit(0)

def main():
    """Main entry point"""
    global backtest_bot
    
    logger.info("=" * 60)
    logger.info("ALGO BY GUGAN - Backtest Bot")
    logger.info("=" * 60)
    
    try:
        # Initialize bot
        logger.info("Initializing Backtest Bot...")
        backtest_bot = BacktestBot()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
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