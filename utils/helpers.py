# utils/helpers.py
"""
Common utility functions with separate bot settings support
"""

import yaml
import os
from datetime import datetime
import pytz
from typing import Dict, Any, List, Union
from pathlib import Path

def load_secrets() -> Dict[str, Any]:
    """Load secrets from environment variables or YAML file"""
    # Check for environment variables (production)
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
    
    # Local development - use YAML
    try:
        secrets_file = Path('config/secrets.yaml')
        if not secrets_file.exists():
            print("⚠️ config/secrets.yaml not found. Creating template...")
            create_secrets_template()
            return get_default_secrets()
        
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = yaml.safe_load(f)
        
        # Normalize chat_id/chat_ids format
        for bot_type in ['backtest', 'realtime']:
            if bot_type in secrets.get('telegram', {}):
                tg_config = secrets['telegram'][bot_type]
                if 'chat_id' in tg_config and 'chat_ids' not in tg_config:
                    tg_config['chat_ids'] = [tg_config['chat_id']]
                elif 'chat_ids' in tg_config and isinstance(tg_config['chat_ids'], str):
                    tg_config['chat_ids'] = [tg_config['chat_ids']]
        
        return secrets
        
    except Exception as e:
        print(f"❌ Error loading secrets.yaml: {e}")
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
    """Create template secrets.yaml"""
    template = """# ALGO BY GUGAN - Secrets Configuration

telegram:
  backtest:
    bot_token: "YOUR_BACKTEST_BOT_TOKEN"
    chat_ids:
      - "YOUR_CHAT_ID"
  
  realtime:
    bot_token: "YOUR_REALTIME_BOT_TOKEN"
    chat_ids:
      - "YOUR_CHAT_ID"

brokers:
  angelone:
    api_key: "your_api_key"
    client_id: "your_client_id"
    password: "your_password"
    totp_secret: "your_totp_secret"
    enabled: true
  
  zerodha:
    api_key: ""
    api_secret: ""
    enabled: false
"""
    
    os.makedirs('config', exist_ok=True)
    with open('config/secrets.yaml', 'w', encoding='utf-8') as f:
        f.write(template)
    print("✅ Created config/secrets.yaml template")

def load_settings() -> Dict[str, Any]:
    """Load settings with separate bot configurations"""
    default_config = {
        'timezone': 'Asia/Kolkata',
        'backtest_bot': {
            'schedule': {
                'start_time': '06:00',
                'end_time': '12:00',
                'all_days': True
            },
            'session_duration_months': 4,
            'start_date': '2010-01-01',
            'trading': {
                'broker': 'angelone',
                'segment': 'NSE_FO',
                'capital': 100000,
                'risk_per_trade': 2.0,
                'max_trades': 5,
                'mode': 'paper',
                'active_strategies': ['5EMA_PowerOfStocks'],
                'active_symbols': []
            }
        },
        'realtime_bot': {
            'schedule': {
                'start_time': '08:55',
                'end_time': '16:05',
                'weekdays_only': True
            },
            'ltp_update_interval': 600,
            'trading': {
                'broker': 'angelone',
                'segment': 'NSE_FO',
                'capital': 100000,
                'risk_per_trade': 2.0,
                'max_trades': 5,
                'mode': 'paper',
                'active_strategies': ['5EMA_PowerOfStocks'],
                'active_symbols': []
            }
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
        settings_file = Path('config/settings.yaml')
        
        if not settings_file.exists():
            print("⚠️ config/settings.yaml not found. Creating...")
            create_settings_file(default_config)
            return default_config
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
        
        if not loaded_config:
            return default_config
        
        return merge_configs(default_config, loaded_config)
        
    except Exception as e:
        print(f"❌ Error loading settings.yaml: {e}")
        return default_config

def merge_configs(default: Dict, loaded: Dict) -> Dict:
    """Deep merge configurations"""
    result = default.copy()
    
    for key, value in loaded.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def create_settings_file(config: Dict[str, Any]):
    """Create settings.yaml"""
    os.makedirs('config', exist_ok=True)
    with open('config/settings.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ Created config/settings.yaml")

def get_bot_settings(bot_type: str) -> Dict[str, Any]:
    """
    Get settings for specific bot type
    
    Args:
        bot_type: 'backtest' or 'realtime'
    
    Returns:
        Bot-specific settings dictionary
    """
    settings = load_settings()
    bot_key = f'{bot_type}_bot'
    
    if bot_key in settings:
        # Return separate bot settings
        bot_settings = settings[bot_key].copy()
        
        # Merge in trading settings as top-level for backward compatibility
        if 'trading' in bot_settings:
            trading = bot_settings.pop('trading')
            bot_settings.update(trading)
        
        return bot_settings
    else:
        # Fallback to default_settings
        return settings.get('default_settings', {})

def get_ist_time() -> datetime:
    """Get current time in IST"""
    settings = load_settings()
    tz = pytz.timezone(settings.get('timezone', 'Asia/Kolkata'))
    return datetime.now(tz)

def is_market_hours(bot_type: str = "realtime") -> bool:
    """Check if within market hours for specific bot"""
    bot_settings = get_bot_settings(bot_type)
    current_time = get_ist_time()
    
    try:
        if 'schedule' not in bot_settings:
            return True
        
        schedule = bot_settings['schedule']
        
        # Check weekday restriction (only for realtime)
        if schedule.get('weekdays_only', False) and current_time.weekday() >= 5:
            return False
        
        start_time = datetime.strptime(schedule['start_time'], '%H:%M').time()
        end_time = datetime.strptime(schedule['end_time'], '%H:%M').time()
        current = current_time.time()
        
        return start_time <= current <= end_time
    except Exception as e:
        print(f"❌ Error checking market hours: {e}")
        return True

def calculate_quantity(capital: float, risk_percent: float, 
                       price: float, stop_loss: float, 
                       lot_size: int = 1) -> int:
    """Calculate position quantity based on risk"""
    try:
        risk_per_unit = abs(price - stop_loss)
        
        if risk_per_unit <= 0:
            return lot_size
        
        risk_amount = capital * (risk_percent / 100)
        max_quantity = int(risk_amount / risk_per_unit)
        
        if max_quantity < lot_size:
            return lot_size
        
        lots = max_quantity // lot_size
        return max(1, lots) * lot_size
        
    except Exception as e:
        print(f"❌ Error calculating quantity: {e}")
        return lot_size

def format_pnl(pnl: float) -> str:
    """Format PnL with emoji"""
    try:
        if pnl > 0:
            return f"🟢 +₹{pnl:,.2f}"
        elif pnl < 0:
            return f"🔴 ₹{pnl:,.2f}"
        else:
            return f"⚪ ₹{pnl:,.2f}"
    except:
        return "⚪ ₹0.00"

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with rupee symbol"""
    try:
        return f"₹{num:,.{decimals}f}"
    except:
        return "₹0.00"

def get_authorized_chat_ids(bot_type: str = 'realtime') -> List[str]:
    """Get authorized chat IDs for a bot"""
    try:
        secrets = load_secrets()
        tg_config = secrets.get('telegram', {}).get(bot_type, {})
        chat_ids = tg_config.get('chat_ids', [])
        return [str(cid) for cid in chat_ids]
    except:
        return []

def is_authorized_user(chat_id: Union[str, int], bot_type: str = 'realtime') -> bool:
    """Check if chat ID is authorized"""
    authorized_ids = get_authorized_chat_ids(bot_type)
    return str(chat_id) in authorized_ids

def ensure_directories():
    """Create all required directories"""
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

# Initialize on import
ensure_directories()