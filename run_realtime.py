# run_realtime.py
"""
Realtime Bot Launcher with Health Endpoint for Render.com
"""

import sys
import signal
import threading
from bots.realtime_bot import RealtimeBot
from tg.rt_telegram import RealtimeTelegramBot
from utils.logger import setup_logger

logger = setup_logger("launcher", "realtime")

# Global bot instances
realtime_bot = None
telegram_bot = None

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Shutdown signal received")
    if realtime_bot:
        realtime_bot.is_running = False
    sys.exit(0)

def start_health_server():
    """Start simple HTTP server for Render.com health checks"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                
                # Check bot status
                status = "healthy" if realtime_bot and realtime_bot.is_running else "starting"
                self.wfile.write(status.encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # Suppress default logging
            pass
    
    try:
        server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
        logger.info("✅ Health check server started on port 8080")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Health server error: {e}")

def main():
    """Main entry point"""
    global realtime_bot, telegram_bot
    
    logger.info("="*60)
    logger.info("🚀 ALGO BY GUGAN - Realtime Bot")
    logger.info("="*60)
    
    try:
        # Start health check server in background (for Render.com)
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        logger.info("✅ Health check endpoint: /health")
        
        # Initialize bots
        logger.info("🔧 Initializing Realtime Bot...")
        realtime_bot = RealtimeBot()
        
        logger.info("📱 Initializing Telegram Interface...")
        telegram_bot = RealtimeTelegramBot(realtime_bot)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start telegram bot in separate thread
        telegram_thread = threading.Thread(target=telegram_bot.start, daemon=True)
        telegram_thread.start()
        logger.info("✅ Telegram bot started")
        
        # Start realtime bot (blocking)
        logger.info("🚀 Starting trading bot...")
        realtime_bot.start()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()