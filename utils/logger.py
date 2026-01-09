# config/secrets.yaml
"""
Logging utility with automatic old log deletion
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
import yaml

def load_settings():
    with open('config/settings.yaml', 'r') as f:
        return yaml.safe_load(f)

def cleanup_old_logs(log_dir: str, retention_days: int = 15):
    """Delete log files older than retention_days"""
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
    
    # Determine log directory
    if bot_type == "backtest":
        log_dir = settings['paths']['logs_backtest']
    else:
        log_dir = settings['paths']['logs_realtime']
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Cleanup old logs
    cleanup_old_logs(log_dir, settings['logging']['retention_days'])
    
    # Create date-wise log file
    log_file = os.path.join(
        log_dir,
        f"{datetime.now().strftime('%Y-%m-%d')}.log"
    )
    
    # Setup logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings['logging']['level']))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(settings['logging']['format'])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger