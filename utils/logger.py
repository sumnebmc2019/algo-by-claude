# config/secrets.yaml
"""
Logging utility with automatic old log deletion
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

def load_settings():
    """Load settings with error handling"""
    try:
        import yaml
        with open('config/settings.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        # Return minimal default settings if config can't be loaded
        return {
            'logging': {
                'retention_days': 15,
                'level': 'DEBUG',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'paths': {
                'logs_backtest': 'logs/backtest',
                'logs_realtime': 'logs/realtime'
            }
        }

def cleanup_old_logs(log_dir: str, retention_days: int = 15):
    """Delete log files older than retention_days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        log_path = Path(log_dir)
        
        if not log_path.exists():
            return
        
        for log_file in log_path.glob("*.log"):
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                try:
                    log_file.unlink()
                    print(f"Deleted old log: {log_file.name}")
                except Exception as e:
                    print(f"Error deleting {log_file.name}: {e}")
    except Exception as e:
        print(f"Error in cleanup_old_logs: {e}")

def setup_logger(name: str, bot_type: str = "realtime") -> logging.Logger:
    """
    Setup logger with date-wise file logging
    
    Args:
        name: Logger name
        bot_type: 'backtest' or 'realtime'
    
    Returns:
        Configured logger instance
    """
    settings = load_settings()
    
    # Determine log directory with fallback
    try:
        if bot_type == "backtest":
            log_dir = settings.get('paths', {}).get('logs_backtest', 'logs/backtest')
        else:
            log_dir = settings.get('paths', {}).get('logs_realtime', 'logs/realtime')
    except:
        log_dir = f'logs/{bot_type}'
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Cleanup old logs
    try:
        retention_days = settings.get('logging', {}).get('retention_days', 15)
        cleanup_old_logs(log_dir, retention_days)
    except:
        pass
    
    # Create date-wise log file
    log_file = os.path.join(
        log_dir,
        f"{datetime.now().strftime('%Y-%m-%d')}.log"
    )
    
    # Setup logger
    logger = logging.getLogger(name)
    
    # Get log level with fallback
    try:
        log_level = settings.get('logging', {}).get('level', 'DEBUG')
        logger.setLevel(getattr(logging, log_level))
    except:
        logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter with fallback
    try:
        log_format = settings.get('logging', {}).get('format', 
                                                      '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(log_format)
    except:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger