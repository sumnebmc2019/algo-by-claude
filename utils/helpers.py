# utils/helpers.py
"""
Common utility functions - Optimized version
"""

import yaml
import os
from datetime import datetime
import pytz
from typing import Dict, Any, List, Union
from pathlib import Path

def load_secrets() -> Dict[str, Any]:
    """
    Load secrets from environment variables (production) or YAML file (local)
    
    Priority:
    1. Environment variables (Railway, Oracle Cloud, etc.)
    2. config/secrets.yaml (local development)
    """
    # Check if running in production (Railway, Oracle Cloud, etc.)
    if os.getenv('TELEGRAM_REALTIME_TOKEN') or os.getenv('RAILWAY_ENVIRONMENT'):
        return {
            'telegram': {
                'backtest': {
                    'bot_token': os.getenv('TELEGRAM_BACKTEST_TOKEN', ''),
                    'chat_ids': os.getenv('TELEGRAM_BACKTEST_CHAT_IDS', '').split(',') if os.getenv('TELEGRAM_BACKTEST_CHAT_IDS') else []
                },
                'realtime': {
                    'bot_token': os.getenv('TELEGRAM_REALTIME_TOKEN', ''),
                    'chat_ids': os.getenv('TELEGRAM_REALTIME_CHAT_IDS', '').split(',') if os.getenv('TELEGRAM_REALTIME_CHAT_IDS') else []
                }
            },
            'brokers': {
                'angelone': {
                    'api_key': os.getenv('ANGELONE_API_KEY', ''),
                    'client_id': os.getenv('ANGELONE_CLIENT_ID', ''),
                    'password': os.getenv('ANGELONE_PASSWORD', ''),
                    'totp_secret': os.getenv('ANGELONE_TOTP_SECRET', ''),
                    'enabled': os.getenv('ANGELONE_ENABLED', 'true').lower() == 'true'
                },
                'zerodha': {
                    'api_key': os.getenv('ZERODHA_API_KEY', ''),
                    'api_secret': os.getenv('ZERODHA_API_SECRET', ''),
                    'enabled': os.getenv('ZERODHA_ENABLED', 'false').lower() == 'true'
                }
            }
        }
    
    # Local development - use YAML file
    try:
        secrets_file = Path('config/secrets.yaml')
        if not secrets_file.exists():
            print("[WARNING] config/secrets.yaml not found. Creating template...")
            create_secrets_template()
            return get_default_secrets()
        
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = yaml.safe_load(f)
        
        # Normalize chat_id/chat_ids format
        for bot_type in ['backtest', 'realtime']:
            if bot_type in secrets.get('telegram', {}):
                tg_config = secrets['telegram'][bot_type]
                
                # Convert single chat_id to chat_ids list
                if 'chat_id' in tg_config and 'chat_ids' not in tg_config:
                    tg_config['chat_ids'] = [tg_config['chat_id']]
                elif 'chat_ids' in tg_config:
                    # Ensure it's a list
                    if isinstance(tg_config['chat_ids'], str):
                        tg_config['chat_ids'] = [tg_config['chat_ids']]
        
        return secrets
        
    except FileNotFoundError:
        print("[ERROR] config/secrets.yaml not found. Please create it.")
        return get_default_secrets()
    except Exception as e:
        print(f"[ERROR] Error loading secrets.yaml: {e}")
        return get_default_secrets()

def get_default_secrets() -> Dict[str, Any]:
    """Return default secrets structure"""
    return {
        'telegram': {
            'backtest': {'bot_token': '', 'chat_ids': []},
            'realtime': {'bot_token': '', 'chat_ids': []}
        },
        'brokers': {
            'angelone': {'enabled': False},
            'zerodha': {'enabled': False}
        }
    }

def create_secrets_template():
    """Create a template secrets.yaml file"""
    template = """# ALGO BY GUGAN - Secrets Configuration
# IMPORTANT: Never commit this file to git!

telegram:
  backtest:
    bot_token: "YOUR_BACKTEST_BOT_TOKEN_FROM_BOTFATHER"
    chat_ids:
      - "YOUR_CHAT_ID_FROM_USERINFOBOT"
      # Add more chat IDs for multiple users:
      # - "123456789"
      # - "987654321"
  
  realtime:
    bot_token: "YOUR_REALTIME_BOT_TOKEN_FROM_BOTFATHER"
    chat_ids:
      - "YOUR_CHAT_ID_FROM_USERINFOBOT"

brokers:
  zerodha:
    api_key: "your_zerodha_api_key"
    api_secret: "your_zerodha_api_secret"
    enabled: false
  
  angelone:
    api_key: "your_angelone_api_key"
    client_id: "your_angelone_client_id"
    password: "your_angelone_password"
    totp_secret: "your_angelone_totp_secret"
    enabled: true

# How to get these values:
# 1. Telegram Bot Token: Message @BotFather on Telegram, create bot, copy token
# 2. Chat ID: Message @userinfobot on Telegram, copy your ID
# 3. AngelOne: Register at smartapi.angelbroking.com
# 4. TOTP Secret: Run: python -c "import pyotp; print(pyotp.random_base32())"
"""
    
    os.makedirs('config', exist_ok=True)
    with open('config/secrets.yaml', 'w', encoding='utf-8') as f:
        f.write(template)
    print("[OK] Created config/secrets.yaml template")

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
            'active_strategies': ['5EMA_PowerOfStocks'],
            'active_symbols': []
        }
    }
    
    try:
        settings_file = Path('config/settings.yaml')
        
        if not settings_file.exists():
            print("[WARNING] config/settings.yaml not found. Creating with defaults...")
            create_settings_file(default_config)
            return default_config
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
        
        if not loaded_config:
            return default_config
        
        # Deep merge with defaults
        merged_config = merge_configs(default_config, loaded_config)
        return merged_config
        
    except Exception as e:
        print(f"[ERROR] Error loading settings.yaml: {e}. Using defaults.")
        return default_config

def merge_configs(default: Dict, loaded: Dict) -> Dict:
    """Deep merge two configuration dictionaries"""
    result = default.copy()
    
    for key, value in loaded.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def create_settings_file(config: Dict[str, Any]):
    """Create settings.yaml file"""
    os.makedirs('config', exist_ok=True)
    with open('config/settings.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("[OK] Created config/settings.yaml")

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
        print(f"[ERROR] Error checking market hours: {e}")
        return True  # Default to allowing operation

def calculate_quantity(capital: float, risk_percent: float, 
                       price: float, stop_loss: float, 
                       lot_size: int = 1) -> int:
    """
    Calculate position quantity based on risk management
    
    Args:
        capital: Available capital
        risk_percent: Risk percentage per trade
        price: Current price of instrument
        stop_loss: Stop loss price
        lot_size: Lot size of the instrument
    
    Returns:
        Calculated quantity in lots
    """
    try:
        # Calculate risk per unit
        risk_per_unit = abs(price - stop_loss)
        
        if risk_per_unit <= 0:
            print("[WARNING] Invalid stop loss, using default lot size")
            return lot_size
        
        # Calculate maximum risk amount
        risk_amount = capital * (risk_percent / 100)
        
        # Calculate quantity based on risk
        max_quantity = int(risk_amount / risk_per_unit)
        
        # Ensure at least 1 lot
        if max_quantity < lot_size:
            return lot_size
        
        # Adjust for lot size
        lots = max_quantity // lot_size
        
        return max(1, lots) * lot_size
        
    except Exception as e:
        print(f"[ERROR] Error calculating quantity: {e}")
        return lot_size  # Return minimum quantity

def format_pnl(pnl: float) -> str:
    """Format PnL with color indicator (no emoji for Windows compatibility)"""
    try:
        if pnl > 0:
            return f"[+] Rs.{pnl:,.2f}"
        elif pnl < 0:
            return f"[-] Rs.{pnl:,.2f}"
        else:
            return f"[=] Rs.{pnl:,.2f}"
    except:
        return "[=] Rs.0.00"

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with Indian comma notation"""
    try:
        return f"Rs.{num:,.{decimals}f}"
    except:
        return "Rs.0.00"

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

def validate_telegram_config() -> bool:
    """
    Validate telegram configuration
    
    Returns:
        True if valid, False otherwise
    """
    try:
        secrets = load_secrets()
        
        for bot_type in ['backtest', 'realtime']:
            tg_config = secrets.get('telegram', {}).get(bot_type, {})
            
            if not tg_config.get('bot_token'):
                print(f"[ERROR] Missing bot_token for {bot_type} bot")
                return False
            
            chat_ids = tg_config.get('chat_ids', [])
            if not chat_ids:
                print(f"[ERROR] Missing chat_ids for {bot_type} bot")
                return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error validating telegram config: {e}")
        return False

def get_authorized_chat_ids(bot_type: str = 'realtime') -> List[str]:
    """
    Get list of authorized chat IDs for a bot
    
    Args:
        bot_type: 'realtime' or 'backtest'
    
    Returns:
        List of chat IDs as strings
    """
    try:
        secrets = load_secrets()
        tg_config = secrets.get('telegram', {}).get(bot_type, {})
        chat_ids = tg_config.get('chat_ids', [])
        
        # Ensure all are strings
        return [str(cid) for cid in chat_ids]
    except:
        return []

def is_authorized_user(chat_id: Union[str, int], bot_type: str = 'realtime') -> bool:
    """
    Check if a chat ID is authorized to use the bot
    
    Args:
        chat_id: Telegram chat ID
        bot_type: 'realtime' or 'backtest'
    
    Returns:
        True if authorized
    """
    authorized_ids = get_authorized_chat_ids(bot_type)
    return str(chat_id) in authorized_ids

def ensure_directories():
    """Create all required directories if they don't exist"""
    directories = [
        'config',
        'data/master_lists',
        'data/historical',
        'data/backtest_state',
        'logs/backtest',
        'logs/realtime',
        'trades'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories()