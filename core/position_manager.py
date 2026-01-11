# config/secrets.yaml
"""
Position Manager - Track and manage open positions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

# Lazy logger initialization
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        from utils.logger import setup_logger
        _logger = setup_logger(__name__)
    return _logger

class Position:
    """Represent a single position"""
    
    def __init__(self, symbol: str, strategy: str, action: str,
                 quantity: int, entry_price: float, 
                 stop_loss: Optional[float] = None,
                 target: Optional[float] = None):
        """
        Initialize position
        
        Args:
            symbol: Symbol name
            strategy: Strategy name
            action: BUY or SELL
            quantity: Position quantity
            entry_price: Entry price
            stop_loss: Stop loss price (optional)
            target: Target price (optional)
        """
        self.symbol = symbol
        self.strategy = strategy
        self.action = action
        self.quantity = quantity
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.target = target
        self.entry_time = datetime.now()
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0.0
        self.status = "OPEN"
    
    def calculate_pnl(self, current_price: float) -> float:
        """
        Calculate current PnL
        
        Args:
            current_price: Current market price
        
        Returns:
            PnL value
        """
        if self.action == "BUY":
            pnl = (current_price - self.entry_price) * self.quantity
        else:  # SELL
            pnl = (self.entry_price - current_price) * self.quantity
        
        return pnl
    
    def close_position(self, exit_price: float):
        """
        Close the position
        
        Args:
            exit_price: Exit price
        """
        self.exit_price = exit_price
        self.exit_time = datetime.now()
        self.pnl = self.calculate_pnl(exit_price)
        self.status = "CLOSED"
    
    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop loss is hit"""
        if not self.stop_loss:
            return False
        
        if self.action == "BUY":
            return current_price <= self.stop_loss
        else:  # SELL
            return current_price >= self.stop_loss
    
    def check_target(self, current_price: float) -> bool:
        """Check if target is hit"""
        if not self.target:
            return False
        
        if self.action == "BUY":
            return current_price >= self.target
        else:  # SELL
            return current_price <= self.target
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary"""
        return {
            'symbol': self.symbol,
            'strategy': self.strategy,
            'action': self.action,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time.isoformat(),
            'exit_price': self.exit_price,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'stop_loss': self.stop_loss,
            'target': self.target,
            'pnl': self.pnl,
            'status': self.status
        }


class PositionManager:
    """Manage all positions"""
    
    def __init__(self):
        self.positions: List[Position] = []
        self.logger = get_logger()
    
    def open_position(self, symbol: str, strategy: str, action: str,
                     quantity: int, entry_price: float,
                     stop_loss: Optional[float] = None,
                     target: Optional[float] = None) -> Position:
        """
        Open a new position
        
        Returns:
            Position object
        """
        position = Position(
            symbol=symbol,
            strategy=strategy,
            action=action,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target
        )
        
        self.positions.append(position)
        self.logger.info(f"Opened {action} position: {symbol} @ {entry_price} x {quantity}")
        
        return position
    
    def close_position(self, position: Position, exit_price: float):
        """
        Close a position
        
        Args:
            position: Position object
            exit_price: Exit price
        """
        position.close_position(exit_price)
        self.logger.info(f"Closed position: {position.symbol} @ {exit_price}, PnL: {position.pnl}")
    
    def close_all_positions(self, exit_prices: Dict[str, float]):
        """
        Close all open positions
        
        Args:
            exit_prices: Dictionary mapping symbol to exit price
        """
        for position in self.get_open_positions():
            if position.symbol in exit_prices:
                self.close_position(position, exit_prices[position.symbol])
            else:
                self.logger.warning(f"No exit price for {position.symbol}")
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return [p for p in self.positions if p.status == "OPEN"]
    
    def get_closed_positions(self) -> List[Position]:
        """Get all closed positions"""
        return [p for p in self.positions if p.status == "CLOSED"]
    
    def get_positions_by_symbol(self, symbol: str) -> List[Position]:
        """Get all positions for a symbol"""
        return [p for p in self.positions if p.symbol == symbol]
    
    def get_position_count(self) -> int:
        """Get count of open positions"""
        return len(self.get_open_positions())
    
    def calculate_total_pnl(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total PnL across all positions
        
        Args:
            current_prices: Dictionary mapping symbol to current price
        
        Returns:
            Total PnL
        """
        total_pnl = 0.0
        
        # Closed positions
        for position in self.get_closed_positions():
            total_pnl += position.pnl
        
        # Open positions (unrealized)
        for position in self.get_open_positions():
            if position.symbol in current_prices:
                total_pnl += position.calculate_pnl(current_prices[position.symbol])
        
        return total_pnl
    
    def get_summary(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Get positions summary
        
        Args:
            current_prices: Dictionary mapping symbol to current price
        
        Returns:
            Summary dictionary
        """
        open_positions = self.get_open_positions()
        closed_positions = self.get_closed_positions()
        
        # Calculate realized PnL
        realized_pnl = sum(p.pnl for p in closed_positions)
        
        # Calculate unrealized PnL
        unrealized_pnl = sum(
            p.calculate_pnl(current_prices.get(p.symbol, p.entry_price))
            for p in open_positions
        )
        
        # Calculate win rate
        winning_trades = len([p for p in closed_positions if p.pnl > 0])
        total_trades = len(closed_positions)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'open_positions': len(open_positions),
            'closed_positions': len(closed_positions),
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': realized_pnl + unrealized_pnl,
            'win_rate': win_rate,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades
        }