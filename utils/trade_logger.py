# utils/trade_logger.py
"""
CSV Trade Logger for recording all trades
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import yaml

def load_settings():
    with open('config/settings.yaml', 'r') as f:
        return yaml.safe_load(f)

class TradeLogger:
    """Log trades to CSV file"""
    
    HEADERS = [
        'timestamp', 'date', 'time', 'symbol', 'segment', 
        'strategy', 'action', 'order_type', 'quantity', 
        'price', 'broker', 'mode', 'order_id', 
        'status', 'pnl', 'capital', 'remarks'
    ]
    
    def __init__(self, bot_type: str = "realtime"):
        """
        Initialize trade logger
        
        Args:
            bot_type: 'backtest' or 'realtime'
        """
        settings = load_settings()
        
        if bot_type == "backtest":
            self.csv_file = settings['paths']['trades_backtest']
        else:
            self.csv_file = settings['paths']['trades_realtime']
        
        # Create trades directory if it doesn't exist
        Path(self.csv_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create CSV with headers if it doesn't exist
        if not os.path.exists(self.csv_file):
            self._create_csv()
    
    def _create_csv(self):
        """Create CSV file with headers"""
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
    
    def log_trade(self, trade_data: Dict[str, Any]):
        """
        Log a trade to CSV
        
        Args:
            trade_data: Dictionary containing trade information
        """
        now = datetime.now()
        
        # Prepare trade record
        record = {
            'timestamp': now.isoformat(),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'symbol': trade_data.get('symbol', ''),
            'segment': trade_data.get('segment', ''),
            'strategy': trade_data.get('strategy', ''),
            'action': trade_data.get('action', ''),  # BUY/SELL
            'order_type': trade_data.get('order_type', ''),  # MARKET/LIMIT
            'quantity': trade_data.get('quantity', 0),
            'price': trade_data.get('price', 0.0),
            'broker': trade_data.get('broker', ''),
            'mode': trade_data.get('mode', ''),  # paper/live
            'order_id': trade_data.get('order_id', ''),
            'status': trade_data.get('status', ''),  # SUCCESS/FAILED
            'pnl': trade_data.get('pnl', 0.0),
            'capital': trade_data.get('capital', 0.0),
            'remarks': trade_data.get('remarks', '')
        }
        
        # Append to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(record)
    
    def get_recent_trades(self, limit: int = 10) -> list:
        """
        Get recent trades from CSV
        
        Args:
            limit: Number of recent trades to retrieve
        
        Returns:
            List of trade dictionaries
        """
        if not os.path.exists(self.csv_file):
            return []
        
        trades = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            trades = list(reader)
        
        return trades[-limit:] if trades else []