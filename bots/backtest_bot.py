# config/secrets.yaml
"""
Backtest Trading Bot - Historical Data Testing
"""

import time
import schedule
from datetime import datetime
from typing import Dict, Any
from core.symbol_manager import SymbolManager
from core.position_manager import PositionManager
from core.data_manager import DataManager
from strategies.strategy_loader import StrategyLoader
from utils.helpers import load_settings, is_market_hours, calculate_quantity
from utils.logger import setup_logger
from utils.trade_logger import TradeLogger

logger = setup_logger(__name__, "backtest")

class BacktestBot:
    """Backtest bot for historical data testing"""
    
    def __init__(self):
        self.settings = load_settings()['default_settings']
        self.backtest_settings = load_settings()['backtest_bot']
        self.symbol_manager = SymbolManager(self.settings['broker'])
        self.data_manager = DataManager()
        self.strategy_loader = StrategyLoader()
        self.trade_logger = TradeLogger("backtest")
        
        # Load strategies
        self.strategy_loader.load_all_strategies()
        
        # Running state
        self.is_running = False
        
        logger.info("Backtest Bot initialized")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings.copy()
    
    def update_settings(self, key: str, value: Any):
        """Update a setting"""
        self.settings[key] = value
        logger.info(f"Updated setting: {key} = {value}")
    
    def run_backtest_session(self, symbol_info: Dict[str, Any], strategy_name: str):
        """
        Run one backtest session for symbol-strategy combination
        
        Args:
            symbol_info: Symbol information dictionary
            strategy_name: Strategy name
        """
        strategy = self.strategy_loader.get_strategy(strategy_name)
        if not strategy:
            logger.error(f"Strategy {strategy_name} not found")
            return
        
        symbol = symbol_info['symbol']
        segment = symbol_info['segment']
        
        # Get next date range to backtest
        start_date, end_date = self.data_manager.backtest_state.get_next_date_range(
            symbol=symbol,
            strategy=strategy_name,
            duration_months=self.backtest_settings['session_duration_months']
        )
        
        # Check if we've reached current date
        if start_date >= datetime.now():
            logger.info(f"Backtest complete for {symbol}-{strategy_name}")
            return
        
        logger.info(f"Backtesting {symbol} with {strategy_name} from {start_date.date()} to {end_date.date()}")
        
        # Load historical data
        data = self.data_manager.load_historical_data(symbol, segment, start_date, end_date)
        
        if data is None or data.empty:
            logger.warning(f"No data available for {symbol}")
            return
        
        # Initialize position manager for this session
        position_manager = PositionManager()
        
        # Session stats
        session_stats = {
            'symbol': symbol,
            'strategy': strategy_name,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'trades': 0,
            'pnl': 0.0
        }
        
        # Iterate through each candle
        for i in range(len(data)):
            # Get data up to current point
            current_data = data.iloc[:i+1].copy()
            
            if len(current_data) < 2:
                continue
            
            current_price = current_data.iloc[-1]['close']
            
            # Check existing positions for exit conditions
            for position in position_manager.get_open_positions():
                # Check stop loss
                if position.check_stop_loss(current_price):
                    position_manager.close_position(position, current_price)
                    
                    # Log trade
                    self.trade_logger.log_trade({
                        'symbol': symbol,
                        'segment': segment,
                        'strategy': strategy_name,
                        'action': 'EXIT',
                        'quantity': position.quantity,
                        'price': current_price,
                        'broker': self.settings['broker'],
                        'mode': 'backtest',
                        'pnl': position.pnl,
                        'status': 'SUCCESS',
                        'capital': self.settings['capital'],
                        'remarks': 'Stop loss hit (BT)'
                    })
                    
                    session_stats['trades'] += 1
                    session_stats['pnl'] += position.pnl
                
                # Check target
                elif position.check_target(current_price):
                    position_manager.close_position(position, current_price)
                    
                    # Log trade
                    self.trade_logger.log_trade({
                        'symbol': symbol,
                        'segment': segment,
                        'strategy': strategy_name,
                        'action': 'EXIT',
                        'quantity': position.quantity,
                        'price': current_price,
                        'broker': self.settings['broker'],
                        'mode': 'backtest',
                        'pnl': position.pnl,
                        'status': 'SUCCESS',
                        'capital': self.settings['capital'],
                        'remarks': 'Target hit (BT)'
                    })
                    
                    session_stats['trades'] += 1
                    session_stats['pnl'] += position.pnl
            
            # Check for new signals
            if position_manager.get_position_count() < self.settings['max_trades']:
                signal = strategy.generate_signals(current_data, symbol_info)
                
                if signal:
                    # Calculate quantity
                    quantity = calculate_quantity(
                        capital=self.settings['capital'],
                        risk_percent=self.settings['risk_per_trade'],
                        price=signal['price'],
                        lot_size=symbol_info['lot_size']
                    )
                    
                    # Open position
                    position_manager.open_position(
                        symbol=symbol,
                        strategy=strategy_name,
                        action=signal['action'],
                        quantity=quantity,
                        entry_price=signal['price'],
                        stop_loss=signal.get('stop_loss'),
                        target=signal.get('target')
                    )
                    
                    # Log trade
                    self.trade_logger.log_trade({
                        'symbol': symbol,
                        'segment': segment,
                        'strategy': strategy_name,
                        'action': signal['action'],
                        'order_type': signal['order_type'],
                        'quantity': quantity,
                        'price': signal['price'],
                        'broker': self.settings['broker'],
                        'mode': 'backtest',
                        'status': 'SUCCESS',
                        'capital': self.settings['capital'],
                        'remarks': signal.get('reason', '')
                    })
                    
                    session_stats['trades'] += 1
        
        # Close any remaining positions at end of session
        for position in position_manager.get_open_positions():
            final_price = data.iloc[-1]['close']
            position_manager.close_position(position, final_price)
            session_stats['pnl'] += position.pnl
        
        # Mark session complete
        self.data_manager.backtest_state.mark_session_complete(
            symbol=symbol,
            strategy=strategy_name,
            end_date=end_date,
            stats=session_stats
        )
        
        logger.info(f"Session complete: {session_stats['trades']} trades, PnL: {session_stats['pnl']:.2f}")
    
    def run_daily_backtest(self):
        """Run backtest for all active symbol-strategy combinations"""
        if not is_market_hours("backtest"):
            logger.info("Outside backtest hours")
            return
        
        logger.info("Starting daily backtest session")
        
        active_symbols = self.symbol_manager.get_active_symbols()
        active_strategies = self.settings['active_strategies']
        
        if not active_symbols:
            logger.warning("No active symbols configured")
            return
        
        if not active_strategies:
            logger.warning("No active strategies configured")
            return
        
        # Run backtest for each combination
        for symbol_info in active_symbols:
            for strategy_name in active_strategies:
                try:
                    self.run_backtest_session(symbol_info, strategy_name)
                except Exception as e:
                    logger.error(f"Error in backtest session: {e}", exc_info=True)
        
        logger.info("Daily backtest session complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get backtest statistics"""
        # Load all trades and calculate stats
        trades = self.trade_logger.get_recent_trades(limit=1000)
        
        if not trades:
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'winning_trades': 0,
                'losing_trades': 0
            }
        
        total_trades = len(trades)
        total_pnl = sum(float(t.get('pnl', 0)) for t in trades)
        winning_trades = len([t for t in trades if float(t.get('pnl', 0)) > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades
        }
    
    def start(self):
        """Start the bot"""
        logger.info("Starting Backtest Bot")
        self.is_running = True
        
        # Get backtest schedule
        start_time = self.backtest_settings['schedule']['start_time']
        
        # Schedule daily backtest at start time
        schedule.every().day.at(start_time).do(self.run_daily_backtest)
        
        logger.info(f"Scheduled daily backtest at {start_time}")
        
        # Run continuously
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    bot = BacktestBot()
    bot.start()