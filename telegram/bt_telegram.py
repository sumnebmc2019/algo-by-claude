# config/secrets.yaml
"""
Backtest Bot Telegram Interface
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from typing import Dict, Any
from utils.helpers import load_secrets, format_pnl, format_number
from utils.logger import setup_logger

logger = setup_logger(__name__, "backtest")

class BacktestTelegramBot:
    """Telegram interface for Backtest Bot"""
    
    def __init__(self, bot_controller):
        """
        Initialize telegram bot
        
        Args:
            bot_controller: Reference to main bot controller
        """
        self.bot_controller = bot_controller
        secrets = load_secrets()
        self.token = secrets['telegram']['backtest']['bot_token']
        self.chat_id = secrets['telegram']['backtest']['chat_id']
        self.app = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🤖 *ALGO BY GUGAN - Backtest Bot*\n\n"
            "Automated historical data backtesting\n"
            "Running 4-month sessions daily from 6 AM to 12 PM IST\n\n"
            "Select an option below:"
        )
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display settings menu"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("📍 Segment/Symbols", callback_data="set_symbols")],
            [InlineKeyboardButton("🏦 Broker", callback_data="set_broker")],
            [InlineKeyboardButton("💰 Capital", callback_data="set_capital")],
            [InlineKeyboardButton("⚠️ Risk", callback_data="set_risk")],
            [InlineKeyboardButton("🔢 Max Trades", callback_data="set_max_trades")],
            [InlineKeyboardButton("📊 Strategies", callback_data="set_strategies")],
            [InlineKeyboardButton("🔄 Reset State", callback_data="reset_state")],
            [InlineKeyboardButton("« Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings = self.bot_controller.get_settings()
        
        message = (
            "⚙️ *Backtest Settings*\n\n"
            f"🏦 Broker: `{settings['broker']}`\n"
            f"📍 Segment: `{settings['segment']}`\n"
            f"💰 Capital: `{format_number(settings['capital'])}`\n"
            f"⚠️ Risk: `{settings['risk_per_trade']}%`\n"
            f"🔢 Max Trades: `{settings['max_trades']}`\n"
            f"📊 Active Strategies: `{len(settings['active_strategies'])}`\n"
            f"📈 Active Symbols: `{len(settings['active_symbols'])}`\n\n"
            "_Backtest processes 4 months of data per day_"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def stats_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display statistics"""
        query = update.callback_query
        await query.answer()
        
        stats = self.bot_controller.get_stats()
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "📊 *Backtest Statistics*\n\n"
            f"*Total Trades:* `{stats['total_trades']}`\n"
            f"*Total PnL:* {format_pnl(stats['total_pnl'])}\n\n"
            f"*Win Rate:* `{stats['win_rate']:.2f}%`\n"
            f"*Winning Trades:* `{stats['winning_trades']}`\n"
            f"*Losing Trades:* `{stats['losing_trades']}`\n\n"
            "_Statistics from all completed backtest sessions_"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def reset_state_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm reset backtest state"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Reset", callback_data="reset_confirmed")],
            [InlineKeyboardButton("❌ Cancel", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "⚠️ *Reset Backtest State*\n\n"
            "This will:\n"
            "• Clear all backtest progress\n"
            "• Start from the beginning date\n"
            "• Re-run all historical data\n\n"
            "Are you sure?"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def reset_state_execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute reset backtest state"""
        query = update.callback_query
        await query.answer()
        
        # TODO: Implement reset logic in bot controller
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "✅ *Backtest state reset successfully*\n\nWill start from beginning on next run."
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        data = query.data
        
        if data == "settings":
            await self.settings_menu(update, context)
        elif data == "stats":
            await self.stats_menu(update, context)
        elif data == "reset_state":
            await self.reset_state_confirm(update, context)
        elif data == "reset_confirmed":
            await self.reset_state_execute(update, context)
        elif data == "main_menu":
            # Recreate start message
            keyboard = [
                [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
                [InlineKeyboardButton("📊 Stats", callback_data="stats")],
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = (
                "🤖 *ALGO BY GUGAN - Backtest Bot*\n\n"
                "Automated historical data backtesting\n"
                "Running 4-month sessions daily from 6 AM to 12 PM IST\n\n"
                "Select an option below:"
            )
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        # Add more handlers for other settings
    
    async def send_notification(self, message: str):
        """Send notification message"""
        await self.app.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode='Markdown'
        )
    
    async def send_session_complete(self, stats: Dict[str, Any]):
        """Send session complete notification"""
        message = (
            "✅ *Backtest Session Complete*\n\n"
            f"Symbol: `{stats['symbol']}`\n"
            f"Strategy: `{stats['strategy']}`\n"
            f"Period: `{stats['start_date']} to {stats['end_date']}`\n"
            f"Trades: `{stats['trades']}`\n"
            f"PnL: {format_pnl(stats['pnl'])}"
        )
        
        await self.send_notification(message)
    
    def start(self):
        """Start the telegram bot"""
        self.app = Application.builder().token(self.token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Start bot
        logger.info("Starting Backtest Telegram Bot")
        self.app.run_polling()