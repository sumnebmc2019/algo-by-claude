# config/secrets.yaml
"""
Symbol management - filtering, selection, master list handling
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from utils.helpers import load_settings, get_symbol_filter_key

# Lazy logger initialization - only when actually used
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        from utils.logger import setup_logger
        _logger = setup_logger(__name__)
    return _logger

class SymbolManager:
    """Manage symbols, master lists, and filtering"""
    
    def __init__(self, broker: str):
        """
        Initialize symbol manager
        
        Args:
            broker: Broker name
        """
        self.broker = broker
        self.settings = load_settings()
        self.master_list_dir = self.settings['paths']['master_lists']
        self.master_data = {}
        self.active_symbols = []
        self.logger = get_logger()
        
        # Create master list directory
        Path(self.master_list_dir).mkdir(parents=True, exist_ok=True)
    
    def load_master_list(self, segment: str, broker: Optional[str] = None) -> bool:
        """
        Load master list for SPECIFIED broker and segment
        
        Args:
            segment: Segment name (NSE_EQ, NSE_FO, etc.)
            broker: Broker name (overrides self.broker if provided)
            
        Returns:
            True if loaded successfully
        """
        # Use provided broker OR current broker
        current_broker = broker or self.broker
        master_file = os.path.join(
            self.master_list_dir,
            f"{current_broker}_{segment}.json"
        )
        
        if not os.path.exists(master_file):
            self.logger.warning(f"Master list not found: {master_file}")
            self.logger.info(f"Please download {current_broker}_{segment}.json")
            return False
        
        try:
            with open(master_file, 'r') as f:
                data = json.load(f)
                self.master_data[segment] = data
                self.logger.info(f"✅ Loaded {len(data)} {current_broker} symbols from {segment}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Error loading {current_broker} master list: {e}")
            return False
    
    def get_symbols_by_segment(self, segment: str, broker: Optional[str] = None) -> List[str]:
        """Get all symbols for a segment"""
        if segment not in self.master_data:
            if not self.load_master_list(segment, broker):
                return []
        return [item['symbol'] for item in self.master_data.get(segment, [])]
    
    def filter_symbols(self, segment: str, filter_key: str) -> List[str]:
        """
        Filter symbols by starting character/number
        
        Args:
            segment: Segment name
            filter_key: Filter key (A-Z or 0-9)
        
        Returns:
            Filtered list of symbols
        """
        all_symbols = self.get_symbols_by_segment(segment, broker=self.broker)
    
        if filter_key == "0-9":
            return [s for s in all_symbols if s[0].isdigit()]
        else:
            return [s for s in all_symbols if s.startswith(filter_key.upper())]
    
    def search_symbols(self, segment: str, query: str) -> List[str]:
        """
        Search symbols by query string
        
        Args:
            segment: Segment name
            query: Search query
        
        Returns:
            List of matching symbols
        """
        all_symbols = self.get_symbols_by_segment(segment, broker=self.broker)
        query_upper = query.upper()
        
        return [s for s in all_symbols if query_upper in s]
    
    def get_symbol_details(self, segment: str, symbol: str, broker: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get complete details for a symbol"""
        if segment not in self.master_data:
            if not self.load_master_list(segment, broker):
                return None
        
        for item in self.master_data.get(segment, []):
            if item.get('symbol') == symbol or item.get('tradingsymbol', '').upper() == symbol.upper():
                return {
                    'symbol': item.get('symbol', item.get('tradingsymbol', '')),
                    'token': item.get('token', item.get('symboltoken', '')),
                    'lot_size': int(item.get('lot_size', item.get('lotsize', 1))),
                    'tick_size': float(item.get('tick_size', 0.05)),
                    'exchange': item.get('exchange', item.get('exch_seg', '')),
                    'name': item.get('name', ''),
                }
        self.logger.warning(f"Symbol {symbol} not found in {segment}")
        return None
    
    def add_active_symbol(self, segment: str, symbol: str) -> bool:
        """
        Add symbol to active symbols list
        
        Args:
            segment: Segment name
            symbol: Symbol name
        
        Returns:
            True if added successfully
        """
        details = self.get_symbol_details(segment, symbol, broker=self.broker)
    
        if not details:
            self.logger.error(f"Symbol {symbol} not found in {segment} for {self.broker}")
            self.logger.info(f"Available files: {os.listdir(self.master_list_dir)}")
            return False
        
        symbol_data = {
            'segment': segment,
            'symbol': details['symbol'],
            'token': details['token'],
            'lot_size': details['lot_size'],
            'tick_size': details['tick_size'],
            'exchange': details['exchange'],
            'broker': self.broker
        }
        
        # Check if already active
        if any(s['symbol'] == symbol for s in self.active_symbols):
            self.logger.warning(f"Symbol {symbol} already active")
            return False
        
        self.active_symbols.append(symbol_data)
        self.logger.info(f"✅ Added {self.broker} symbol: {symbol} (token: {symbol_data['token']})")
        return True
    
    def remove_active_symbol(self, symbol: str) -> bool:
        """
        Remove symbol from active symbols list
        
        Args:
            symbol: Symbol name
        
        Returns:
            True if removed successfully
        """
        initial_length = len(self.active_symbols)
        self.active_symbols = [s for s in self.active_symbols if s['symbol'] != symbol]
        
        if len(self.active_symbols) < initial_length:
            self.logger.info(f"Removed active symbol: {symbol}")
            return True
        else:
            self.logger.warning(f"Symbol {symbol} not found in active list")
            return False
    
    def get_active_symbols(self) -> List[Dict[str, Any]]:
        """Get list of all active symbols with details"""
        return self.active_symbols
    
    def clear_active_symbols(self):
        """Clear all active symbols"""
        self.active_symbols = []
        self.logger.info("Cleared all active symbols")
    
    def refresh_broker(self, new_broker: str):
        """Refresh broker and clear cached data"""
        self.broker = new_broker
        self.master_data.clear()
        self.logger.info(f"🔄 SymbolManager refreshed: {new_broker}")