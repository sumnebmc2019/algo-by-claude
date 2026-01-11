# strategies/ema5_power_of_stocks.py
"""
5 EMA Strategy - Power of Stocks
High Probability Intraday Trading Strategy

Entry Rules:
1. Price crosses above 5 EMA → BUY signal
2. Price crosses below 5 EMA → SELL signal

Exit Rules:
1. Stop Loss: Previous swing low/high
2. Target: 1.5x Risk-Reward ratio
3. Trail stop loss when favorable

Additional Filters:
- Only trade in trending market
- Avoid choppy/sideways markets
- Use higher timeframe trend confirmation
"""

from strategies.base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class EMA5PowerOfStocks(BaseStrategy):
    """5 EMA Strategy from Power of Stocks"""
    
    def __init__(self):
        super().__init__(name="5EMA_PowerOfStocks")
        
        # Strategy parameters
        self.parameters = {
            'ema_period': 5,
            'risk_reward_ratio': 1.5,
            'swing_lookback': 5,  # Candles to look back for swing points
            'min_candles': 20,     # Minimum candles needed
            'use_trend_filter': True,
            'trend_ema': 50,       # Higher timeframe trend EMA
        }
    
    def generate_signals(self, data: pd.DataFrame, 
                        symbol_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate trading signals based on 5 EMA crossover
        
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
        if len(data) < self.parameters['min_candles']:
            return None
        
        # Calculate 5 EMA
        data['ema5'] = data['close'].ewm(
            span=self.parameters['ema_period'],
            adjust=False
        ).mean()
        
        # Calculate trend EMA if filter is enabled
        if self.parameters['use_trend_filter']:
            data['ema_trend'] = data['close'].ewm(
                span=self.parameters['trend_ema'],
                adjust=False
            ).mean()
        
        # Get last few candles
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Detect EMA crossovers
        signal = None
        
        # BULLISH CROSSOVER - Price crosses above 5 EMA
        if (previous['close'] <= previous['ema5'] and 
            current['close'] > current['ema5']):
            
            # Trend filter - only buy in uptrend
            if self.parameters['use_trend_filter']:
                if current['close'] < current['ema_trend']:
                    return None  # Skip if not in uptrend
            
            # Find swing low for stop loss
            swing_low = self._find_swing_low(data, self.parameters['swing_lookback'])
            
            if swing_low is None:
                return None
            
            # Calculate stop loss and target
            entry_price = current['close']
            stop_loss = swing_low
            risk = entry_price - stop_loss
            
            # Skip if risk is too small
            if risk <= 0 or risk < (entry_price * 0.002):  # Min 0.2% risk
                return None
            
            target = entry_price + (risk * self.parameters['risk_reward_ratio'])
            
            signal = {
                'action': 'BUY',
                'order_type': 'MARKET',
                'price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'reason': f"Price crossed above 5EMA at {entry_price:.2f}, SL: {stop_loss:.2f}, Target: {target:.2f}"
            }
        
        # BEARISH CROSSOVER - Price crosses below 5 EMA
        elif (previous['close'] >= previous['ema5'] and 
              current['close'] < current['ema5']):
            
            # Trend filter - only sell in downtrend
            if self.parameters['use_trend_filter']:
                if current['close'] > current['ema_trend']:
                    return None  # Skip if not in downtrend
            
            # Find swing high for stop loss
            swing_high = self._find_swing_high(data, self.parameters['swing_lookback'])
            
            if swing_high is None:
                return None
            
            # Calculate stop loss and target
            entry_price = current['close']
            stop_loss = swing_high
            risk = stop_loss - entry_price
            
            # Skip if risk is too small
            if risk <= 0 or risk < (entry_price * 0.002):  # Min 0.2% risk
                return None
            
            target = entry_price - (risk * self.parameters['risk_reward_ratio'])
            
            signal = {
                'action': 'SELL',
                'order_type': 'MARKET',
                'price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'reason': f"Price crossed below 5EMA at {entry_price:.2f}, SL: {stop_loss:.2f}, Target: {target:.2f}"
            }
        
        return signal
    
    def _find_swing_low(self, data: pd.DataFrame, lookback: int) -> Optional[float]:
        """
        Find recent swing low for stop loss
        
        Args:
            data: OHLCV dataframe
            lookback: Number of candles to look back
        
        Returns:
            Swing low price or None
        """
        if len(data) < lookback + 1:
            return None
        
        recent_data = data.iloc[-(lookback + 1):-1]
        swing_low = recent_data['low'].min()
        
        return swing_low
    
    def _find_swing_high(self, data: pd.DataFrame, lookback: int) -> Optional[float]:
        """
        Find recent swing high for stop loss
        
        Args:
            data: OHLCV dataframe
            lookback: Number of candles to look back
        
        Returns:
            Swing high price or None
        """
        if len(data) < lookback + 1:
            return None
        
        recent_data = data.iloc[-(lookback + 1):-1]
        swing_high = recent_data['high'].max()
        
        return swing_high
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return self.parameters


# Strategy Usage Notes:
# ----------------------
# 1. This is a trend-following strategy best suited for intraday trading
# 2. Works best in trending markets (avoid choppy/ranging conditions)
# 3. Use on 5-minute or 15-minute timeframes
# 4. The trend filter (50 EMA) helps avoid counter-trend trades
# 5. Always respect the stop loss - no averaging down
# 6. Book partial profits at 1:1 and trail the rest
# 7. Close all positions by market close (no overnight positions)
#
# Risk Management:
# ----------------
# - Never risk more than 2% of capital per trade
# - Maximum 3-5 simultaneous positions
# - If 2 consecutive losses, reduce position size by 50%
# - If 3 consecutive losses, stop trading for the day
#
# Best Markets:
# -------------
# - NIFTY, BANKNIFTY (highly liquid)
# - Major stocks with good volume
# - Avoid illiquid options/stocks
#
# Power of Stocks recommendations:
# - Use strict discipline
# - Journal all trades
# - Review performance weekly
# - Adjust parameters based on market conditions