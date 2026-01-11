# strategies/base_strategy.py
"""
Base Strategy Class - All strategies must inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.parameters = {}
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, 
                        symbol_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate trading signals based on data
        
        Args:
            data: OHLCV dataframe with columns: timestamp, open, high, low, close, volume
            symbol_info: Dictionary with symbol details (symbol, lot_size, etc.)
        
        Returns:
            Signal dictionary or None:
            {
                'action': 'BUY' or 'SELL' or 'EXIT',
                'order_type': 'MARKET' or 'LIMIT',
                'price': float (for limit orders),
                'stop_loss': float (optional),
                'target': float (optional),
                'reason': str (signal reason)
            }
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters
        
        Returns:
            Dictionary of parameters
        """
        pass
    
    def set_parameters(self, params: Dict[str, Any]):
        """
        Set strategy parameters
        
        Args:
            params: Dictionary of parameters
        """
        self.parameters.update(params)
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate if data has required columns and sufficient rows
        
        Args:
            data: OHLCV dataframe
        
        Returns:
            True if data is valid
        """
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        if not all(col in data.columns for col in required_columns):
            return False
        
        if len(data) < 2:
            return False
        
        return True
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"<Strategy: {self.name}>"