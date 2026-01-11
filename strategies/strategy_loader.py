# config/secrets.yaml
"""
Dynamic Strategy Loader - Load strategies as plug-and-play modules
"""

import os
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional
from strategies.base_strategy import BaseStrategy

# Lazy logger initialization
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        from utils.logger import setup_logger
        _logger = setup_logger(__name__)
    return _logger

class StrategyLoader:
    """Load and manage trading strategies dynamically"""
    
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategies_dir = Path(__file__).parent
        self.logger = get_logger()
    
    def load_all_strategies(self) -> int:
        """
        Load all strategy files from strategies directory
        
        Returns:
            Number of strategies loaded
        """
        count = 0
        
        # Get all Python files except base and loader
        strategy_files = [
            f for f in self.strategies_dir.glob("*.py")
            if f.stem not in ['__init__', 'base_strategy', 'strategy_loader']
        ]
        
        for strategy_file in strategy_files:
            try:
                if self.load_strategy(strategy_file.stem):
                    count += 1
            except Exception as e:
                self.logger.error(f"Error loading strategy {strategy_file.stem}: {e}")
        
        self.logger.info(f"Loaded {count} strategies")
        return count
    
    def load_strategy(self, strategy_name: str) -> bool:
        """
        Load a specific strategy by name
        
        Args:
            strategy_name: Name of the strategy file (without .py)
        
        Returns:
            True if loaded successfully
        """
        strategy_file = self.strategies_dir / f"{strategy_name}.py"
        
        if not strategy_file.exists():
            self.logger.error(f"Strategy file not found: {strategy_file}")
            return False
        
        try:
            # Import module dynamically
            spec = importlib.util.spec_from_file_location(strategy_name, strategy_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find BaseStrategy subclass
            strategy_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, BaseStrategy) and 
                    item is not BaseStrategy):
                    strategy_class = item
                    break
            
            if not strategy_class:
                self.logger.error(f"No BaseStrategy subclass found in {strategy_name}")
                return False
            
            # Instantiate strategy
            strategy_instance = strategy_class()
            self.strategies[strategy_instance.name] = strategy_instance
            
            self.logger.info(f"Loaded strategy: {strategy_instance.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading strategy {strategy_name}: {e}")
            return False
    
    def get_strategy(self, strategy_name: str) -> Optional[BaseStrategy]:
        """
        Get strategy instance by name
        
        Args:
            strategy_name: Name of the strategy
        
        Returns:
            Strategy instance or None
        """
        return self.strategies.get(strategy_name)
    
    def get_all_strategies(self) -> Dict[str, BaseStrategy]:
        """Get all loaded strategies"""
        return self.strategies
    
    def get_strategy_names(self) -> List[str]:
        """Get list of all loaded strategy names"""
        return list(self.strategies.keys())
    
    def reload_strategy(self, strategy_name: str) -> bool:
        """
        Reload a strategy (useful for development)
        
        Args:
            strategy_name: Name of the strategy
        
        Returns:
            True if reloaded successfully
        """
        # Find the file name
        for file_name, strategy in self.strategies.items():
            if strategy.name == strategy_name:
                del self.strategies[strategy_name]
                return self.load_strategy(file_name)
        
        self.logger.warning(f"Strategy {strategy_name} not found for reload")
        return False