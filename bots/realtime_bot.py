# bots/realtime_bot.py
"""
Realtime Trading Bot - Updated for separate settings
"""

import time
import schedule
from datetime import datetime
from typing import Dict, Any, List
from core.symbol_manager import SymbolManager
from core.position_manager import PositionManager
from strategies.strategy_loader import StrategyLoader
from utils.helpers import get_bot_settings, is_market_hours, calculate_quantity
from utils.logger import setup_logger
from utils.trade_logger import TradeLogger
import pandas as pd
import yaml

logger = setup_logger(__name__, "realtime")

class RealtimeBot:
    """Realtime trading bot with separate settings support"""
    
    def __init__(self):
        # Load bot-specific settings
        self.settings = get_bot_settings('realtime')
        
        logger.info("="*60)
        logger.info("🚀 Initializing Realtime Bot with separate settings")
        logger.info("="*60)
        logger.info(f"📊 Broker: {self.settings['broker']}")
        logger.info(f"📊 Segment: {self.settings['segment']}")
        logger.info(f"💰 Capital: ₹{self.settings['capital']:,}")
        logger.info(f"⚠️ Risk per trade: {self.settings['risk_per_trade']}%")
        logger.info(f"🔢 Max trades: {self.settings['max_trades']}")
        logger.info(f"📝 Mode: {self.settings['mode'].upper()}")
        logger.info(f"🎯 Strategies: {', '.join(self.settings['active_strategies'])}")
        logger.info(f"📈 Active symbols: {len(self.settings['active_symbols'])}")
        logger.info("="*60)
        
        self.symbol_manager = SymbolManager(self.settings['broker'])
        self.position_manager = PositionManager()
        self.strategy_loader = StrategyLoader()
        self.trade_logger = TradeLogger("realtime")
        
        # Load strategies
        self.strategy_loader.load_all_strategies()
        
        # Load active symbols from settings
        if self.settings.get('active_symbols'):
            self.symbol_manager.active_symbols = self.settings['active_symbols']
            logger.info(f"✅ Loaded {len(self.settings['active_symbols'])} active symbols")
        
        # LTP cache
        self.ltp_cache: Dict[str, float] = {}
        
        # Running state
        self.is_running = False
        
        # Telegram bot reference
        self.telegram_bot = None
        
        # Cached broker manager
        self.broker_manager = None
        self.cached_broker = None
        
        logger.info("✅ Realtime Bot initialized successfully")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings.copy()
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            # Load full config
            with open('config/settings.yaml', 'r') as f:
                full_config = yaml.safe_load(f)
            
            # Update realtime_bot.trading section
            if 'realtime_bot' not in full_config:
                full_config['realtime_bot'] = {}
            if 'trading' not in full_config['realtime_bot']:
                full_config['realtime_bot']['trading'] = {}
            
            # Update trading settings
            full_config['realtime_bot']['trading'].update(self.settings)
            
            # Save back
            with open('config/settings.yaml', 'w') as f:
                yaml.safe_dump(full_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info("✅ Settings saved to config/settings.yaml")
        except Exception as e:
            logger.error(f"❌ Failed to save settings: {e}")

    def update_settings(self, key: str, value: Any):
        """Update a setting"""
        self.settings[key] = value
        logger.info(f"✅ Updated setting: {key} = {value}")
        
        # Recreate SymbolManager if broker changed
        if key == 'broker':
            self.symbol_manager = SymbolManager(value)
            logger.info(f"🔄 SymbolManager refreshed for broker: {value}")
        
        # Save settings
        self.save_settings()
    
    def get_broker(self):
        """Get or create broker instance"""
        try:
            from core.broker_manager import BrokerManager
            
            if not self.broker_manager:
                self.broker_manager = BrokerManager()
                
                if self.broker_manager.set_active_broker(self.settings['broker']):
                    self.cached_broker = self.broker_manager.get_active_broker()
                    logger.info(f"✅ Broker authenticated: {self.settings['broker']}")
                else:
                    logger.error("❌ Failed to authenticate broker")
                    return None
            
            return self.cached_broker
            
        except Exception as e:
            logger.error(f"❌ Error getting broker: {e}")
            return None
    
    def get_ltp(self, symbol: str) -> float:
        """Get Last Traded Price"""
        return self.ltp_cache.get(symbol, 0.0)
    
    def update_ltp_all_symbols(self):
        """Update LTP for all active symbols"""
        try:
            active_symbols = self.symbol_manager.get_active_symbols()
            
            if not active_symbols:
                return
            
            broker = self.get_broker()
            if not broker:
                logger.error("❌ No broker available")
                return
            
            for symbol_info in active_symbols:
                try:
                    ltp = broker.get_ltp(
                        symbol=symbol_info['symbol'],
                        exchange=symbol_info.get('exchange', 'NSE')
                    )
                    
                    if ltp is not None:
                        self.ltp_cache[symbol_info['symbol']] = ltp
                except Exception as e:
                    logger.error(f"❌ Error fetching LTP for {symbol_info['symbol']}: {e}")
            
            logger.info(f"✅ Updated LTP for {len(active_symbols)} symbols")
            
        except Exception as e:
            logger.error(f"❌ Error in update_ltp_all_symbols: {e}")
    
    def fetch_live_data(self, symbol_info: Dict[str, Any], timeframe: str = "1min") -> pd.DataFrame:
        """Fetch live market data"""
        try:
            from datetime import timedelta
            
            broker = self.get_broker()
            if not broker:
                return pd.DataFrame()
            
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            data = broker.get_historical_data(
                symbol=symbol_info['symbol'],
                exchange=symbol_info.get('exchange', 'NSE'),
                from_date=from_date,
                to_date=to_date,
                interval=timeframe
            )
            
            return data if data is not None else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Error fetching live data: {e}")
            return pd.DataFrame()
    
    def execute_trade(self, signal: Dict[str, Any], symbol_info: Dict[str, Any]):
        """Execute trade based on signal"""
        if self.position_manager.get_position_count() >= self.settings['max_trades']:
            logger.warning("⚠️ Max trades limit reached")
            return
        
        # Calculate quantity
        quantity = calculate_quantity(
            capital=self.settings['capital'],
            risk_percent=self.settings['risk_per_trade'],
            price=signal['price'],
            stop_loss=signal.get('stop_loss', signal['price'] * 0.98),
            lot_size=symbol_info['lot_size']
        )
        
        # Prepare trade data
        trade_data = {
            'symbol': symbol_info['symbol'],
            'segment': symbol_info['segment'],
            'strategy': signal.get('strategy', 'Unknown'),
            'action': signal['action'],
            'order_type': signal['order_type'],
            'quantity': quantity,
            'price': signal['price'],
            'broker': self.settings['broker'],
            'mode': self.settings['mode'],
            'status': 'SUCCESS',
            'capital': self.settings['capital'],
            'remarks': signal.get('reason', '')
        }
        
        # Execute based on mode
        if self.settings['mode'] == 'paper':
            logger.info(f"📝 Paper Trade: {signal['action']} {symbol_info['symbol']} @ ₹{signal['price']}")
            
            self.position_manager.open_position(
                symbol=symbol_info['symbol'],
                strategy=trade_data['strategy'],
                action=signal['action'],
                quantity=quantity,
                entry_price=signal['price'],
                stop_loss=signal.get('stop_loss'),
                target=signal.get('target')
            )
            
            # Send telegram notification
            if self.telegram_bot:
                try:
                    import asyncio
                    asyncio.create_task(self.telegram_bot.send_trade_notification(trade_data))
                except Exception as e:
                    logger.error(f"❌ Failed to send telegram: {e}")
        else:
            logger.info(f"🔴 Live Trade: {signal['action']} {symbol_info['symbol']} @ ₹{signal['price']}")
            # TODO: Implement live order placement
        
        # Log trade
        self.trade_logger.log_trade(trade_data)
    
    def check_positions(self):
        """Check positions for stop loss and targets"""
        open_positions = self.position_manager.get_open_positions()
        
        for position in open_positions:
            ltp = self.get_ltp(position.symbol)
            
            if position.check_stop_loss(ltp):
                logger.info(f"🛑 Stop loss hit for {position.symbol}")
                self.position_manager.close_position(position, ltp)
                
                self.trade_logger.log_trade({
                    'symbol': position.symbol,
                    'strategy': position.strategy,
                    'action': 'EXIT',
                    'quantity': position.quantity,
                    'price': ltp,
                    'broker': self.settings['broker'],
                    'mode': self.settings['mode'],
                    'pnl': position.pnl,
                    'status': 'SUCCESS',
                    'remarks': 'Stop loss hit'
                })
            
            elif position.check_target(ltp):
                logger.info(f"🎯 Target hit for {position.symbol}")
                self.position_manager.close_position(position, ltp)
                
                self.trade_logger.log_trade({
                    'symbol': position.symbol,
                    'strategy': position.strategy,
                    'action': 'EXIT',
                    'quantity': position.quantity,
                    'price': ltp,
                    'broker': self.settings['broker'],
                    'mode': self.settings['mode'],
                    'pnl': position.pnl,
                    'status': 'SUCCESS',
                    'remarks': 'Target hit'
                })
    
    def scan_and_trade(self):
        """Main scanning and trading logic"""
        if not is_market_hours("realtime"):
            logger.debug("⏸️ Outside market hours")
            return
        
        logger.info("🔍 Scanning for trading opportunities...")
        
        active_symbols = self.symbol_manager.get_active_symbols()
        active_strategies = [
            self.strategy_loader.get_strategy(name) 
            for name in self.settings['active_strategies']
        ]
        
        if not active_symbols:
            logger.debug("⚠️ No active symbols")
            return
        
        if not active_strategies:
            logger.debug("⚠️ No active strategies")
            return
        
        for symbol_info in active_symbols:
            data = self.fetch_live_data(symbol_info)
            
            if data.empty:
                logger.debug(f"⚠️ No data for {symbol_info['symbol']}")
                continue
            
            for strategy in active_strategies:
                if not strategy:
                    continue
                
                try:
                    signal = strategy.generate_signals(data, symbol_info)
                    
                    if signal:
                        signal['strategy'] = strategy.name
                        logger.info(f"📊 Signal: {signal['action']} {symbol_info['symbol']} - {signal['reason']}")
                        self.execute_trade(signal, symbol_info)
                except Exception as e:
                    logger.error(f"❌ Error running strategy {strategy.name}: {e}")
    
    def run_cycle(self):
        """Run one complete cycle"""
        try:
            self.update_ltp_all_symbols()
            self.check_positions()
            self.scan_and_trade()
        except Exception as e:
            logger.error(f"❌ Error in run cycle: {e}", exc_info=True)
    
    def close_all_positions(self) -> Dict[str, Any]:
        """Close all open positions"""
        open_positions = self.position_manager.get_open_positions()
        
        if not open_positions:
            return {'count': 0, 'total_pnl': 0.0}
        
        exit_prices = {pos.symbol: self.get_ltp(pos.symbol) for pos in open_positions}
        self.position_manager.close_all_positions(exit_prices)
        total_pnl = sum(pos.pnl for pos in open_positions)
        
        logger.info(f"✅ Closed {len(open_positions)} positions, PnL: ₹{total_pnl:,.2f}")
        
        return {'count': len(open_positions), 'total_pnl': total_pnl}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        current_prices = {
            symbol: self.get_ltp(symbol)
            for symbol in [pos.symbol for pos in self.position_manager.get_open_positions()]
        }
        
        return self.position_manager.get_summary(current_prices)
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        return [pos.to_dict() for pos in self.position_manager.get_open_positions()]
    
    def calculate_position_pnl(self, position: Dict[str, Any], ltp: float) -> float:
        """Calculate PnL for position"""
        if position['action'] == 'BUY':
            return (ltp - position['entry_price']) * position['quantity']
        else:
            return (position['entry_price'] - ltp) * position['quantity']
    
    def start(self):
        """Start the bot"""
        logger.info("🚀 Starting Realtime Bot")
        self.is_running = True
        
        # Schedule LTP updates
        schedule.every(10).minutes.do(self.update_ltp_all_symbols)
        
        # Schedule main cycle
        schedule.every(1).minutes.do(self.run_cycle)
        
        # Run continuously
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    bot = RealtimeBot()
    bot.start()