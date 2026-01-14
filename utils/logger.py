# utils/logger.py
"""
Logging configuration with auto-cleanup and UTF-8 support
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import os

def setup_logger(name: str, bot_type: str = "backtest", level: str = "INFO") -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        bot_type: 'backtest' or 'realtime'
        level: Logging level
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create logs directory
    log_dir = Path(f"logs/{bot_type}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file path with date
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Set encoding for Windows console
    if sys.platform == 'win32':
        try:
            # Try to set UTF-8 encoding for Windows console
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    # Format without emojis for better compatibility
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Cleanup old logs
    cleanup_old_logs(log_dir, retention_days=15)
    
    return logger


def cleanup_old_logs(log_dir: Path, retention_days: int = 15):
    """
    Remove log files older than retention_days
    
    Args:
        log_dir: Directory containing log files
        retention_days: Number of days to keep logs
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for log_file in log_dir.glob("*.log"):
            file_date = datetime.strptime(log_file.stem, '%Y-%m-%d')
            if file_date < cutoff_date:
                log_file.unlink()
                
    except Exception as e:
        # Don't fail if cleanup fails
        pass