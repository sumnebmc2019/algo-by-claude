# config/secrets.yaml
"""
Common utility functions
"""

import yaml
from datetime import datetime
import pytz
from typing import Dict, Any

def load_secrets() -> Dict[str, Any]:
    """Load secrets from YAML file with error handling"""
    try:
        with open('config/secrets.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("⚠️ config/secrets.yaml not found. Please create it.")
        return {
            'telegram': {
                'backtest': {'bot_token': '', 'chat_id': ''},
                'realtime': {'bot_token': '', 'chat_id': ''}
            },
            'brokers': {
                'angelone': {'enabled': False},
                'zerodha': {'enabled': False}
            }
        }
    except Exception as e:
        print(f"⚠️ Error loading secrets.yaml: {e}")
        return {'telegram': {}, 'brokers': {}}

def load_settings() -> Dict[str, Any]:
    """Load settings from YAML file with comprehensive error handling"""
    default_config = {
        'timezone': 'Asia/Kolkata',
        'realtime_bot': {
            'schedule': {
                'start_time': '08:55',
                'end_time': '16:05',
                'weekdays_only': True
            },
            'ltp_update_interval': 600
        },
        'backtest_bot': {
            'schedule': {
                'start_time': '06:00',
                'end_time': '12:00',
                'all_days': True
            },
            'session_duration_months': 4,
            'start_date': '2010-01-01'
        },
        'logging': {
            'retention_days': 15,
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'paths': {
            'master_lists': 'data/master_lists',
            'historical_data': 'data/historical',
            'backtest_state': 'data/backtest_state',
            'logs_backtest': 'logs/backtest',
            'logs_realtime': 'logs/realtime',
            'trades_backtest': 'trades/backtest_trades.csv',
            'trades_realtime': 'trades/realtime_trades.csv'
        },
        'segments': ['NSE_EQ', 'NSE_FO', 'BSE_EQ', 'MCX_FO', 'CDS_FO'],
        'default_settings': {
            'broker': 'angelone',
            'segment': 'NSE_FO',
            'capital': 100000,
            'risk_per_trade': 2.0,
            'max_trades': 5,
            'mode': 'paper',
            'active_strategies': [],
            'active_symbols': []
        }
    }
    
    try:
        with open('config/settings.yaml', 'r') as f:
            loaded_config = yaml.safe_load(f)
            
        # Merge loaded config with defaults (defaults as fallback)
        if loaded_config:
            # Deep merge default_settings if it exists
            if 'default_settings' in loaded_config:
                for key, value in default_config['default_settings'].items():
                    if key not in loaded_config['default_settings']:
                        loaded_config['default_settings'][key] = value
            else:
                loaded_config['default_settings'] = default_config['default_settings']
            
            # Ensure other required keys exist
            for key, value in default_config.items():
                if key not in loaded_config:
                    loaded_config[key] = value
            
            return loaded_config
        else:
            return default_config
            
    except FileNotFoundError:
        print("⚠️ config/settings.yaml not found. Using defaults.")
        # Create the file with defaults
        try:
            import os
            os.makedirs('config', exist_ok=True)
            with open('config/settings.yaml', 'w') as f:
                yaml.safe_dump(default_config, f, default_flow_style=False)
            print("✅ Created config/settings.yaml with default settings")
        except Exception as e:
            print(f"⚠️ Could not create config/settings.yaml: {e}")
        return default_config
        
    except Exception as e:
        print(f"⚠️ Error loading settings.yaml: {e}. Using defaults.")
        return default_config

def get_ist_time() -> datetime:
    """Get current time in IST timezone"""
    settings = load_settings()
    tz = pytz.timezone(settings.get('timezone', 'Asia/Kolkata'))
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
    
    try:
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
    except Exception as e:
        print(f"⚠️ Error checking market hours: {e}")
        return True  # Default to allowing operation

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
    try:
        risk_amount = capital * (risk_percent / 100)
        max_quantity = int(risk_amount / price)
        
        # Adjust for lot size
        lots = max(1, max_quantity // lot_size)
        
        return lots * lot_size
    except Exception as e:
        print(f"⚠️ Error calculating quantity: {e}")
        return lot_size  # Return minimum quantity

def format_pnl(pnl: float) -> str:
    """Format PnL with color emoji"""
    try:
        if pnl > 0:
            return f"🟢 +₹{pnl:,.2f}"
        elif pnl < 0:
            return f"🔴 ₹{pnl:,.2f}"
        else:
            return f"⚪ ₹{pnl:,.2f}"
    except:
        return f"⚪ ₹0.00"

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with Indian comma notation"""
    try:
        return f"₹{num:,.{decimals}f}"
    except:
        return "₹0.00"

def get_symbol_filter_key(symbol: str) -> str:
    """
    Get filter key for symbol (starting character)
    
    Args:
        symbol: Symbol name
    
    Returns:
        Filter key (A-Z or 0-9)
    """
    try:
        first_char = symbol[0].upper()
        if first_char.isdigit():
            return "0-9"
        elif first_char.isalpha():
            return first_char
        else:
            return "OTHER"
    except:
        return "OTHER"