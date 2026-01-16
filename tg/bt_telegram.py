# tg/bt_telegram.py
"""
Backtest Bot Telegram Interface - FIXED VERSION
"""

import asyncio
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
        self.chat_ids = secrets['telegram']['backtest']['chat_ids']
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
            [InlineKeyboardButton("📝 Segment/Symbols", callback_data="set_symbols")],
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
            f"📝 Segment: `{settings['segment']}`\n"
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
        
        # Reset state for all symbols and strategies
        try:
            import shutil
            from pathlib import Path
            
            state_dir = Path('data/backtest_state')
            if state_dir.exists():
                shutil.rmtree(state_dir)
                state_dir.mkdir(parents=True, exist_ok=True)
                
            keyboard = [[InlineKeyboardButton("« Back", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = "✅ *Backtest state reset successfully*\n\nWill start from beginning on next run."
        except Exception as e:
            keyboard = [[InlineKeyboardButton("« Back", callback_data="settings")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"❌ *Failed to reset state*\n\nError: {str(e)}"
        
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
        elif data == "main_menu" or data == "refresh":
            await self.show_main_menu(update, context)
        elif data == "set_symbols":
            await self.set_symbols_menu(update, context)
        elif data == "set_broker":
            await self.set_broker_menu(update, context)
        elif data == "set_capital":
            await self.set_capital_menu(update, context)
        elif data == "set_risk":
            await self.set_risk_menu(update, context)
        elif data == "set_max_trades":
            await self.set_max_trades_menu(update, context)
        elif data == "set_strategies":
            await self.set_strategies_menu(update, context)
        elif data.startswith("risk_"):
            risk_value = data.split("_")[1]
            self.bot_controller.update_settings('risk_per_trade', float(risk_value))
            await query.answer(f"Risk set to {risk_value}%", show_alert=True)
            await self.settings_menu(update, context)
        elif data.startswith("maxtrades_"):
            max_trades = int(data.split("_")[1])
            self.bot_controller.update_settings('max_trades', max_trades)
            await query.answer(f"Max trades set to {max_trades}", show_alert=True)
            await self.settings_menu(update, context)
        elif data.startswith("broker_"):
            broker = data.split("_")[1]
            self.bot_controller.update_settings('broker', broker)
            await query.answer(f"Broker set to {broker}", show_alert=True)
            await self.settings_menu(update, context)
        elif data.startswith("strategy_"):
            strategy_name = "5EMA_PowerOfStocks" if data == "strategy_5ema" else "SMA_Crossover"
            current_strategies = self.bot_controller.get_settings()['active_strategies']
            if strategy_name in current_strategies:
                current_strategies.remove(strategy_name)
                await query.answer(f"Disabled {strategy_name}", show_alert=False)
            else:
                current_strategies.append(strategy_name)
                await query.answer(f"Enabled {strategy_name}", show_alert=False)
            self.bot_controller.update_settings('active_strategies', current_strategies)
            await self.set_strategies_menu(update, context)
        else:
            await query.answer("Feature coming soon!", show_alert=True)
    
    async def set_symbols_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Symbol selection menu"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "📝 *Symbol Selection*\n\n"
            "To add symbols:\n"
            "1. Use command: `/addsymbol SEGMENT SYMBOL`\n"
            "   Example: `/addsymbol NSE_FO NIFTY24JANFUT`\n\n"
            "2. To remove: `/removesymbol SYMBOL`\n"
            "   Example: `/removesymbol NIFTY24JANFUT`\n\n"
            "3. To list active: `/listsymbols`\n\n"
            f"Currently active symbols: {len(self.bot_controller.get_settings()['active_symbols'])}"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def set_broker_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broker selection menu"""
        query = update.callback_query
        await query.answer()
        
        settings = self.bot_controller.get_settings()
        
        keyboard = [
            [InlineKeyboardButton("AngelOne", callback_data="broker_angelone")],
            [InlineKeyboardButton("Zerodha", callback_data="broker_zerodha")],
            [InlineKeyboardButton("« Back", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"🏦 *Broker Selection*\n\n"
            f"Current broker: `{settings['broker']}`\n\n"
            "Select a broker:"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def set_capital_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Capital setting menu"""
        query = update.callback_query
        await query.answer()
        
        settings = self.bot_controller.get_settings()
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"💰 *Capital Setting*\n\n"
            f"Current capital: {format_number(settings['capital'])}\n\n"
            "To change capital, use command:\n"
            "`/setcapital AMOUNT`\n\n"
            "Example: `/setcapital 100000`"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def set_risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Risk setting menu"""
        query = update.callback_query
        await query.answer()
        
        settings = self.bot_controller.get_settings()
        
        keyboard = [
            [InlineKeyboardButton("1%", callback_data="risk_1")],
            [InlineKeyboardButton("2%", callback_data="risk_2")],
            [InlineKeyboardButton("3%", callback_data="risk_3")],
            [InlineKeyboardButton("5%", callback_data="risk_5")],
            [InlineKeyboardButton("« Back", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"⚠️ *Risk per Trade*\n\n"
            f"Current risk: `{settings['risk_per_trade']}%`\n\n"
            "Select risk percentage:"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def set_max_trades_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Max trades setting menu"""
        query = update.callback_query
        await query.answer()
        
        settings = self.bot_controller.get_settings()
        
        keyboard = [
            [InlineKeyboardButton("3", callback_data="maxtrades_3")],
            [InlineKeyboardButton("5", callback_data="maxtrades_5")],
            [InlineKeyboardButton("8", callback_data="maxtrades_8")],
            [InlineKeyboardButton("10", callback_data="maxtrades_10")],
            [InlineKeyboardButton("« Back", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"🔢 *Maximum Trades*\n\n"
            f"Current limit: `{settings['max_trades']}`\n\n"
            "Select maximum simultaneous trades:"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def set_strategies_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Strategy selection menu"""
        query = update.callback_query
        await query.answer()
        
        settings = self.bot_controller.get_settings()
        active_strategies = settings['active_strategies']
        
        keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if '5EMA_PowerOfStocks' in active_strategies else '☐'} 5 EMA Power of Stocks",
                callback_data="strategy_5ema"
            )],
            [InlineKeyboardButton(
                f"{'✅' if 'SMA_Crossover' in active_strategies else '☐'} SMA Crossover",
                callback_data="strategy_sma"
            )],
            [InlineKeyboardButton("« Back", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📊 *Strategy Selection*\n\n"
            f"Active strategies: {len(active_strategies)}\n\n"
            "Click to toggle strategies:"
        )
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu (for callback queries)"""
        query = update.callback_query
        await query.answer()
        
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
    
    async def send_notification(self, message: str):
        """Send notification message"""
        try:
            await self.app.bot.send_message(
                chat_ids=self.chat_ids,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
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
        """Start the telegram bot (deprecated - use start_async)"""
        import asyncio
        asyncio.run(self.start_async())
    
    async def start_async(self):
        """Start the telegram bot asynchronously"""
        from telegram.ext import ApplicationBuilder
        from telegram.request import HTTPXRequest
        
        # Create custom request with longer timeout
        request = HTTPXRequest(
            connection_pool_size=8,
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0
        )
        
        self.app = ApplicationBuilder().token(self.token).request(request).build()
        
        # Add error handler
        self.app.add_error_handler(self.error_handler)
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Add command handlers for settings
        self.app.add_handler(CommandHandler("addsymbol", self.add_symbol_command))
        self.app.add_handler(CommandHandler("removesymbol", self.remove_symbol_command))
        self.app.add_handler(CommandHandler("listsymbols", self.list_symbols_command))
        self.app.add_handler(CommandHandler("setcapital", self.set_capital_command))
        
        # Start bot
        logger.info("Starting Backtest Telegram Bot")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Telegram bot stopping...")
        finally:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Telegram error: {context.error}", exc_info=context.error)
        
        # Try to notify user
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "⚠️ An error occurred. Please try again."
                )
        except Exception as e:
            logger.error(f"Could not send error message: {e}")
    
    async def add_symbol_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addsymbol command"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Usage: `/addsymbol SEGMENT SYMBOL`\n"
                "Example: `/addsymbol NSE_FO NIFTY24JANFUT`",
                parse_mode='Markdown'
            )
            return
        
        segment = context.args[0]
        symbol = context.args[1]
        
        # Add symbol via bot controller
        success = self.bot_controller.symbol_manager.add_active_symbol(segment, symbol)
        
        if success:
            # Update settings
            active_symbols = self.bot_controller.symbol_manager.get_active_symbols()
            self.bot_controller.update_settings('active_symbols', active_symbols)
            
            await update.message.reply_text(
                f"✅ Added symbol: `{symbol}` from `{segment}`\n"
                f"Total active symbols: {len(active_symbols)}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to add symbol: `{symbol}`\n"
                "Make sure the segment and symbol are correct.",
                parse_mode='Markdown'
            )
    
    async def remove_symbol_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removesymbol command"""
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "Usage: `/removesymbol SYMBOL`\n"
                "Example: `/removesymbol NIFTY24JANFUT`",
                parse_mode='Markdown'
            )
            return
        
        symbol = context.args[0]
        
        # Remove symbol
        success = self.bot_controller.symbol_manager.remove_active_symbol(symbol)
        
        if success:
            # Update settings
            active_symbols = self.bot_controller.symbol_manager.get_active_symbols()
            self.bot_controller.update_settings('active_symbols', active_symbols)
            
            await update.message.reply_text(
                f"✅ Removed symbol: `{symbol}`\n"
                f"Total active symbols: {len(active_symbols)}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Symbol not found: `{symbol}`",
                parse_mode='Markdown'
            )
    
    async def list_symbols_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listsymbols command - FIXED"""
        active_symbols = self.bot_controller.symbol_manager.get_active_symbols()
        
        if not active_symbols:
            await update.message.reply_text(
                "📝 *Active Symbols*\n\n"
                "No symbols configured yet.\n\n"
                "Add symbols using:\n"
                "`/addsymbol SEGMENT SYMBOL`",
                parse_mode='Markdown'
            )
            return
        
        message = "📝 *Active Symbols*\n\n"
        for sym in active_symbols:
            # Handle both old and new symbol structure
            lot_size = sym.get('lot_size') or sym.get('details', {}).get('lotsize', 'N/A')
            token = sym.get('token') or sym.get('details', {}).get('token', 'N/A')
            
            message += (
                f"• `{sym['symbol']}` ({sym['segment']})\n"
                f"  Lot Size: {lot_size}, Token: {token}\n"
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def set_capital_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setcapital command"""
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "Usage: `/setcapital AMOUNT`\n"
                "Example: `/setcapital 100000`",
                parse_mode='Markdown'
            )
            return
        
        try:
            capital = float(context.args[0])
            self.bot_controller.update_settings('capital', capital)
            
            await update.message.reply_text(
                f"✅ Capital set to: {format_number(capital)}",
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount. Please provide a number.",
                parse_mode='Markdown'
            )