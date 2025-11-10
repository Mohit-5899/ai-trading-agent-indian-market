"""
Base Strategy Class
Abstract base class for all trading strategies
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    Defines the interface that all strategies must implement
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        
        # Default parameters that all strategies share
        self.risk_per_trade = self.parameters.get('risk_per_trade', 2.0)
        self.risk_reward_ratio = self.parameters.get('risk_reward_ratio', 3.0)
        self.timeframe = self.parameters.get('timeframe', '5m')
        
    @abstractmethod
    async def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signals based on market data
        
        Args:
            market_data: Dictionary containing OHLCV data and indicators
            
        Returns:
            Dictionary containing signal information:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'strength': float,  # 0-100
                'confidence': float,  # 0-100
                'entry_price': float,
                'stop_loss': float,
                'target': float,
                'reasoning': str
            }
        """
        pass
    
    @abstractmethod
    async def calculate_position_size(
        self, 
        signal: Dict[str, Any], 
        account_value: float,
        current_price: float
    ) -> int:
        """
        Calculate position size based on risk management
        
        Args:
            signal: Signal dictionary from generate_signals
            account_value: Current account value
            current_price: Current stock price
            
        Returns:
            Position size (number of shares)
        """
        pass
    
    @abstractmethod
    async def validate_entry(
        self, 
        signal: Dict[str, Any], 
        market_data: Dict[str, Any],
        current_positions: List[Dict[str, Any]]
    ) -> bool:
        """
        Validate if entry conditions are met
        
        Args:
            signal: Generated signal
            market_data: Current market data
            current_positions: Existing positions
            
        Returns:
            True if entry is valid, False otherwise
        """
        pass
    
    async def validate_exit(
        self,
        position: Dict[str, Any],
        current_price: float,
        market_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Check if position should be exited
        
        Args:
            position: Current position information
            current_price: Current market price
            market_data: Current market data
            
        Returns:
            Dictionary with exit decision:
            {
                'action': 'HOLD' | 'EXIT',
                'reason': str
            }
        """
        try:
            entry_price = float(position.get('average_price', 0))
            stop_loss = float(position.get('stop_loss', 0))
            target = float(position.get('target', 0))
            position_type = position.get('position_type', 'LONG')
            
            if position_type == 'LONG':
                # Check stop loss
                if stop_loss > 0 and current_price <= stop_loss:
                    return {'action': 'EXIT', 'reason': 'Stop loss hit'}
                
                # Check target
                if target > 0 and current_price >= target:
                    return {'action': 'EXIT', 'reason': 'Target reached'}
                    
            else:  # SHORT
                # Check stop loss
                if stop_loss > 0 and current_price >= stop_loss:
                    return {'action': 'EXIT', 'reason': 'Stop loss hit'}
                
                # Check target  
                if target > 0 and current_price <= target:
                    return {'action': 'EXIT', 'reason': 'Target reached'}
            
            return {'action': 'HOLD', 'reason': 'No exit condition met'}
            
        except Exception as e:
            return {'action': 'HOLD', 'reason': f'Error in exit validation: {str(e)}'}
    
    def calculate_stop_loss(
        self, 
        entry_price: float, 
        position_type: str,
        atr: Optional[float] = None
    ) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price of position
            position_type: 'LONG' or 'SHORT'
            atr: Average True Range (optional)
            
        Returns:
            Stop loss price
        """
        # Default stop loss distance (can be overridden in child classes)
        default_distance = 0.02  # 2%
        
        if position_type == 'LONG':
            return entry_price * (1 - default_distance)
        else:
            return entry_price * (1 + default_distance)
    
    def calculate_target(
        self, 
        entry_price: float, 
        stop_loss: float, 
        position_type: str
    ) -> float:
        """
        Calculate target price based on risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            position_type: 'LONG' or 'SHORT'
            
        Returns:
            Target price
        """
        risk_amount = abs(entry_price - stop_loss)
        reward_amount = risk_amount * self.risk_reward_ratio
        
        if position_type == 'LONG':
            return entry_price + reward_amount
        else:
            return entry_price - reward_amount
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            'name': self.name,
            'parameters': self.parameters,
            'risk_per_trade': self.risk_per_trade,
            'risk_reward_ratio': self.risk_reward_ratio,
            'timeframe': self.timeframe
        }