# config/secrets.yaml
"""
Common utility functions
"""

import yaml
from datetime import datetime
import pytz
from typing import Dict, Any

def load_secrets() -> Dict[str, Any]:
    """Load secrets from YAML file"""
    with open('config/secrets.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_settings() -> Dict[str, Any]:
    """Load settings from YAML file"""
    with open('config/settings.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_ist_time() -> datetime:
    """Get current time in IST timezone"""
    settings = load_settings()
    tz = pytz.timezone(settings['timezone'])
    return datetime.now(tz)

def is_market_hours(bot_type: str = "realtime") -> bool:
    """
    Check if current time is within market hours
    
    Args:
        bot_type: 'backtest' or 'realtime'
    
    Returns:
        True if within market hours, False otherwise
    """
    settings = load_settings()
    current_time = get_ist_time()
    
    if bot_type == "backtest":
        schedule = settings['backtest_bot']['schedule']
    else:
        schedule = settings['realtime_bot']['schedule']
        # Check if weekday only mode is enabled
        if schedule.get('weekdays_only', False) and current_time.weekday() >= 5:
            return False
    
    start_time = datetime.strptime(schedule['start_time'], '%H:%M').time()
    end_time = datetime.strptime(schedule['end_time'], '%H:%M').time()
    current = current_time.time()
    
    return start_time <= current <= end_time

def calculate_quantity(capital: float, risk_percent: float, 
                       price: float, lot_size: int = 1) -> int:
    """
    Calculate position quantity based on risk management
    
    Args:
        capital: Available capital
        risk_percent: Risk percentage per trade
        price: Current price of instrument
        lot_size: Lot size of the instrument
    
    Returns:
        Calculated quantity in lots
    """
    risk_amount = capital * (risk_percent / 100)
    max_quantity = int(risk_amount / price)
    
    # Adjust for lot size
    lots = max(1, max_quantity // lot_size)
    
    return lots * lot_size

def format_pnl(pnl: float) -> str:
    """Format PnL with color emoji"""
    if pnl > 0:
        return f"🟢 +₹{pnl:,.2f}"
    elif pnl < 0:
        return f"🔴 ₹{pnl:,.2f}"
    else:
        return f"⚪ ₹{pnl:,.2f}"

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with Indian comma notation"""
    return f"₹{num:,.{decimals}f}"

def get_symbol_filter_key(symbol: str) -> str:
    """
    Get filter key for symbol (starting character)
    
    Args:
        symbol: Symbol name
    
    Returns:
        Filter key (A-Z or 0-9)
    """
    first_char = symbol[0].upper()
    if first_char.isdigit():
        return "0-9"
    elif first_char.isalpha():
        return first_char
    else:
        return "OTHER"