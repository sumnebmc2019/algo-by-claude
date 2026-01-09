# config/secrets.yaml
"""
Example Strategy - Simple Moving Average Crossover
This is a template for creating new strategies
"""

from strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Dict, Any, Optional

class SMAStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def __init__(self):
        super().__init__(name="SMA_Crossover")
        
        # Default parameters
        self.parameters = {
            'short_period': 10,
            'long_period': 20,
            'stop_loss_pct': 2.0,
            'target_pct': 4.0
        }
    
    def generate_signals(self, data: pd.DataFrame, 
                        symbol_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate signals based on SMA crossover
        
        Args:
            data: OHLCV dataframe
            symbol_info: Symbol details
        
        Returns:
            Signal dictionary or None
        """
        # Validate data
        if not self.validate_data(data):
            return None
        
        # Check if we have enough data
        if len(data) < self.parameters['long_period']:
            return None
        
        # Calculate SMAs
        data['sma_short'] = data['close'].rolling(
            window=self.parameters['short_period']
        ).mean()
        data['sma_long'] = data['close'].rolling(
            window=self.parameters['long_period']
        ).mean()
        
        # Get last two rows
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Check for crossover
        signal = None
        
        # Bullish crossover - short SMA crosses above long SMA
        if (previous['sma_short'] <= previous['sma_long'] and 
            current['sma_short'] > current['sma_long']):
            
            stop_loss = current['close'] * (1 - self.parameters['stop_loss_pct'] / 100)
            target = current['close'] * (1 + self.parameters['target_pct'] / 100)
            
            signal = {
                'action': 'BUY',
                'order_type': 'MARKET',
                'price': current['close'],
                'stop_loss': stop_loss,
                'target': target,
                'reason': f"SMA bullish crossover: {self.parameters['short_period']}/{self.parameters['long_period']}"
            }
        
        # Bearish crossover - short SMA crosses below long SMA
        elif (previous['sma_short'] >= previous['sma_long'] and 
              current['sma_short'] < current['sma_long']):
            
            stop_loss = current['close'] * (1 + self.parameters['stop_loss_pct'] / 100)
            target = current['close'] * (1 - self.parameters['target_pct'] / 100)
            
            signal = {
                'action': 'SELL',
                'order_type': 'MARKET',
                'price': current['close'],
                'stop_loss': stop_loss,
                'target': target,
                'reason': f"SMA bearish crossover: {self.parameters['short_period']}/{self.parameters['long_period']}"
            }
        
        return signal
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return self.parameters


# To create a new strategy:
# 1. Copy this file and rename it (e.g., rsi_strategy.py)
# 2. Change the class name (e.g., RSIStrategy)
# 3. Update the __init__ with your strategy name and parameters
# 4. Implement your logic in generate_signals()
# 5. Save the file in the strategies/ folder
# 6. The bot will automatically load it on next run!