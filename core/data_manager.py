# config/secrets.yaml
"""
Data Manager - Handle historical data and backtest state tracking
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pandas as pd
from utils.helpers import load_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BacktestStateManager:
    """Track backtest progress for each symbol-strategy combination"""
    
    def __init__(self):
        settings = load_settings()
        self.state_dir = settings['paths']['backtest_state']
        Path(self.state_dir).mkdir(parents=True, exist_ok=True)
    
    def get_state_file(self, symbol: str, strategy: str) -> str:
        """Get state file path for symbol-strategy combination"""
        safe_name = f"{symbol}_{strategy}".replace("/", "_")
        return os.path.join(self.state_dir, f"{safe_name}.json")
    
    def load_state(self, symbol: str, strategy: str) -> Optional[Dict[str, Any]]:
        """
        Load backtest state for symbol-strategy combination
        
        Returns:
            State dictionary with last_end_date, completed_sessions, etc.
        """
        state_file = self.get_state_file(symbol, strategy)
        
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading state for {symbol}-{strategy}: {e}")
            return None
    
    def save_state(self, symbol: str, strategy: str, state: Dict[str, Any]):
        """Save backtest state for symbol-strategy combination"""
        state_file = self.get_state_file(symbol, strategy)
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.debug(f"Saved state for {symbol}-{strategy}")
        except Exception as e:
            logger.error(f"Error saving state for {symbol}-{strategy}: {e}")
    
    def get_next_date_range(self, symbol: str, strategy: str, 
                           duration_months: int = 4) -> tuple:
        """
        Get next date range for backtest
        
        Args:
            symbol: Symbol name
            strategy: Strategy name
            duration_months: Duration in months
        
        Returns:
            Tuple of (start_date, end_date) as datetime objects
        """
        state = self.load_state(symbol, strategy)
        settings = load_settings()
        
        if state and 'last_end_date' in state:
            # Continue from where we left off
            start_date = datetime.fromisoformat(state['last_end_date']) + timedelta(days=1)
        else:
            # Start from global start date
            start_date = datetime.fromisoformat(
                settings['backtest_bot']['start_date']
            )
        
        # Calculate end date
        end_date = start_date + timedelta(days=duration_months * 30)
        
        # Don't go beyond today
        today = datetime.now()
        if end_date > today:
            end_date = today
        
        return start_date, end_date
    
    def mark_session_complete(self, symbol: str, strategy: str, 
                             end_date: datetime, stats: Dict[str, Any]):
        """
        Mark a backtest session as complete
        
        Args:
            symbol: Symbol name
            strategy: Strategy name
            end_date: End date of completed session
            stats: Session statistics
        """
        state = self.load_state(symbol, strategy) or {
            'symbol': symbol,
            'strategy': strategy,
            'completed_sessions': []
        }
        
        session_record = {
            'end_date': end_date.isoformat(),
            'completed_at': datetime.now().isoformat(),
            'stats': stats
        }
        
        state['last_end_date'] = end_date.isoformat()
        state['completed_sessions'].append(session_record)
        
        self.save_state(symbol, strategy, state)
    
    def reset_state(self, symbol: str, strategy: str):
        """Reset backtest state for symbol-strategy combination"""
        state_file = self.get_state_file(symbol, strategy)
        if os.path.exists(state_file):
            os.remove(state_file)
            logger.info(f"Reset state for {symbol}-{strategy}")


class DataManager:
    """Manage historical and live data"""
    
    def __init__(self):
        settings = load_settings()
        self.data_dir = settings['paths']['historical_data']
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        self.backtest_state = BacktestStateManager()
    
    def get_data_file(self, symbol: str, segment: str) -> str:
        """Get data file path for symbol"""
        safe_name = f"{segment}_{symbol}".replace("/", "_")
        return os.path.join(self.data_dir, f"{safe_name}.csv")
    
    def load_historical_data(self, symbol: str, segment: str,
                           start_date: datetime, 
                           end_date: datetime) -> Optional[pd.DataFrame]:
        """
        Load historical data for symbol and date range
        
        Args:
            symbol: Symbol name
            segment: Segment name
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with OHLCV data
        """
        data_file = self.get_data_file(symbol, segment)
        
        if not os.path.exists(data_file):
            logger.warning(f"Data file not found: {data_file}")
            logger.info("Please download historical data")
            return None
        
        try:
            # Load data
            df = pd.read_csv(data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter by date range
            mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
            filtered_df = df[mask].copy()
            
            logger.info(f"Loaded {len(filtered_df)} bars for {symbol}")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def save_historical_data(self, symbol: str, segment: str, 
                           data: pd.DataFrame):
        """
        Save historical data for symbol
        
        Args:
            symbol: Symbol name
            segment: Segment name
            data: DataFrame with OHLCV data
        """
        data_file = self.get_data_file(symbol, segment)
        
        try:
            data.to_csv(data_file, index=False)
            logger.info(f"Saved data for {symbol}")
        except Exception as e:
            logger.error(f"Error saving data for {symbol}: {e}")