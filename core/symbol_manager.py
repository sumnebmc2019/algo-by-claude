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
from utils.logger import setup_logger

logger = setup_logger(__name__)

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
        
        # Create master list directory
        Path(self.master_list_dir).mkdir(parents=True, exist_ok=True)
    
    def load_master_list(self, segment: str) -> bool:
        """
        Load master list for broker and segment
        
        Args:
            segment: Segment name (NSE_EQ, NSE_FO, etc.)
        
        Returns:
            True if loaded successfully
        """
        master_file = os.path.join(
            self.master_list_dir,
            f"{self.broker}_{segment}.json"
        )
        
        if not os.path.exists(master_file):
            logger.warning(f"Master list not found: {master_file}")
            logger.info("Please download master list from broker and save as JSON")
            return False
        
        try:
            with open(master_file, 'r') as f:
                data = json.load(f)
                self.master_data[segment] = data
                logger.info(f"Loaded {len(data)} symbols from {segment}")
                return True
        except Exception as e:
            logger.error(f"Error loading master list: {e}")
            return False
    
    def get_symbols_by_segment(self, segment: str) -> List[str]:
        """
        Get all symbols for a segment
        
        Args:
            segment: Segment name
        
        Returns:
            List of symbol names
        """
        if segment not in self.master_data:
            if not self.load_master_list(segment):
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
        all_symbols = self.get_symbols_by_segment(segment)
        
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
        all_symbols = self.get_symbols_by_segment(segment)
        query_upper = query.upper()
        
        return [s for s in all_symbols if query_upper in s]
    
    def get_symbol_details(self, segment: str, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get complete details for a symbol
        
        Args:
            segment: Segment name
            symbol: Symbol name
        
        Returns:
            Dictionary with symbol details (token, lot_size, etc.)
        """
        if segment not in self.master_data:
            if not self.load_master_list(segment):
                return None
        
        for item in self.master_data.get(segment, []):
            if item['symbol'] == symbol:
                return item
        
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
        details = self.get_symbol_details(segment, symbol)
        
        if not details:
            logger.error(f"Symbol {symbol} not found in {segment}")
            return False
        
        symbol_data = {
            'segment': segment,
            'symbol': symbol,
            'token': details.get('token', ''),
            'lot_size': details.get('lot_size', 1),
            'tick_size': details.get('tick_size', 0.05),
            'exchange': details.get('exchange', ''),
        }
        
        # Check if already active
        if any(s['symbol'] == symbol for s in self.active_symbols):
            logger.warning(f"Symbol {symbol} already active")
            return False
        
        self.active_symbols.append(symbol_data)
        logger.info(f"Added active symbol: {symbol}")
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
            logger.info(f"Removed active symbol: {symbol}")
            return True
        else:
            logger.warning(f"Symbol {symbol} not found in active list")
            return False
    
    def get_active_symbols(self) -> List[Dict[str, Any]]:
        """Get list of all active symbols with details"""
        return self.active_symbols
    
    def clear_active_symbols(self):
        """Clear all active symbols"""
        self.active_symbols = []
        logger.info("Cleared all active symbols")