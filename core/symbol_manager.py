# core/symbol_manager.py
"""
Symbol management - loading master lists, filtering, active symbol tracking
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.logger import setup_logger

class SymbolManager:
    """Manages symbol lists, filtering, and active symbols"""
    
    def __init__(self, broker: str = "angelone"):
        self.logger = setup_logger("symbol_manager", "realtime")
        self.broker = broker
        self.master_lists: Dict[str, List[Dict]] = {}
        self.active_symbols: List[Dict[str, Any]] = []
        
    def load_master_list(self, segment: str, broker: str = None) -> bool:
        """
        Load master symbol list from JSON file
        
        Args:
            segment: NSE_EQ, NSE_FO, BSE_EQ, MCX_FO, CDS_FO
            broker: Broker name (default: self.broker)
            
        Returns:
            bool: Success status
        """
        current_broker = broker or self.broker
        cache_key = f"{current_broker}_{segment}"
        
        # Return if already loaded
        if cache_key in self.master_lists:
            return True
            
        file_path = Path(f"data/master_lists/{current_broker}_{segment}.json")
        
        if not file_path.exists():
            self.logger.error(f"Master list not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.master_lists[cache_key] = data
            self.logger.info(f"✅ Loaded {len(data)} {current_broker} symbols from {segment}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading master list {file_path}: {e}")
            return False
    
    def search_symbols(self, segment: str, query: str, 
                      broker: str = None, limit: int = 20) -> List[Dict]:
        """
        Search symbols by name/token
        
        Args:
            segment: NSE_EQ, NSE_FO, etc.
            query: Search string
            broker: Broker name
            limit: Max results
            
        Returns:
            List of matching symbols
        """
        current_broker = broker or self.broker
        cache_key = f"{current_broker}_{segment}"
        
        if not self.load_master_list(segment, current_broker):
            return []
            
        query_lower = query.lower()
        results = []
        
        for symbol_data in self.master_lists[cache_key]:
            symbol_name = symbol_data.get('symbol', '').lower()
            if query_lower in symbol_name:
                results.append(symbol_data)
                if len(results) >= limit:
                    break
                    
        return results
    
    def get_symbol_details(self, segment: str, symbol: str, 
                          broker: str = None) -> Optional[Dict]:
        """
        Get full details for a specific symbol
        
        Args:
            segment: NSE_EQ, NSE_FO, etc.
            symbol: Symbol name
            broker: Broker name
            
        Returns:
            Symbol details dict or None
        """
        current_broker = broker or self.broker
        
        if not self.load_master_list(segment, broker):
            return None
            
        cache_key = f"{current_broker}_{segment}"
        
        for symbol_data in self.master_lists[cache_key]:
            if symbol_data.get('symbol', '').upper() == symbol.upper():
                return symbol_data
                
        return None
    
    def add_active_symbol(self, segment: str, symbol: str, 
                         broker: str = None) -> bool:
        """
        Add symbol to active trading list
        
        Args:
            segment: NSE_EQ, NSE_FO, etc.
            symbol: Symbol name
            broker: Broker name
            
        Returns:
            bool: Success status
        """
        current_broker = broker or self.broker
        
        # Check if already active
        for active in self.active_symbols:
            if (active['symbol'] == symbol and 
                active['segment'] == segment and 
                active.get('broker', self.broker) == current_broker):
                self.logger.warning(f"Symbol already active: {symbol}")
                return False
        
        # Get symbol details
        details = self.get_symbol_details(segment, symbol, current_broker)
        if not details:
            self.logger.error(f"Symbol not found: {symbol} in {segment}")
            return False
        
        # Add to active list
        active_symbol = {
            'symbol': symbol,
            'segment': segment,
            'broker': current_broker,
            'details': details,
            'ltp': None
        }
        
        self.active_symbols.append(active_symbol)
        self.logger.info(f"Added active symbol: {symbol} ({segment})")
        return True
    
    def remove_active_symbol(self, symbol: str, segment: str = None) -> bool:
        """
        Remove symbol from active list
        
        Args:
            symbol: Symbol name
            segment: Optional segment filter
            
        Returns:
            bool: Success status
        """
        original_count = len(self.active_symbols)
        
        self.active_symbols = [
            s for s in self.active_symbols
            if not (s['symbol'] == symbol and 
                   (segment is None or s['segment'] == segment))
        ]
        
        removed = original_count - len(self.active_symbols)
        if removed > 0:
            self.logger.info(f"Removed {removed} active symbol(s): {symbol}")
            return True
        return False
    
    def get_active_symbols(self, segment: str = None) -> List[Dict]:
        """
        Get list of active symbols, optionally filtered by segment
        
        Args:
            segment: Optional segment filter
            
        Returns:
            List of active symbols
        """
        if segment:
            return [s for s in self.active_symbols if s['segment'] == segment]
        return self.active_symbols
    
    def clear_active_symbols(self):
        """Clear all active symbols"""
        count = len(self.active_symbols)
        self.active_symbols.clear()
        self.logger.info(f"Cleared {count} active symbols")
    
    def update_ltp(self, symbol: str, segment: str, ltp: float):
        """
        Update LTP for an active symbol
        
        Args:
            symbol: Symbol name
            segment: Segment
            ltp: Last traded price
        """
        for active_sym in self.active_symbols:
            if (active_sym['symbol'] == symbol and 
                active_sym['segment'] == segment):
                active_sym['ltp'] = ltp
                break
    
    def filter_by_criteria(self, segment: str, criteria: Dict[str, Any],
                          broker: str = None, limit: int = 50) -> List[Dict]:
        """
        Filter symbols by various criteria
        
        Args:
            segment: NSE_EQ, NSE_FO, etc.
            criteria: Dict with filters like {'expiry': '2024-01-25', 'strike': 21500}
            broker: Broker name
            limit: Max results
            
        Returns:
            List of filtered symbols
        """
        current_broker = broker or self.broker
        
        if not self.load_master_list(segment, current_broker):
            return []
            
        cache_key = f"{current_broker}_{segment}"
        results = []
        
        for symbol_data in self.master_lists[cache_key]:
            match = True
            for key, value in criteria.items():
                if symbol_data.get(key) != value:
                    match = False
                    break
            
            if match:
                results.append(symbol_data)
                if len(results) >= limit:
                    break
                    
        return results