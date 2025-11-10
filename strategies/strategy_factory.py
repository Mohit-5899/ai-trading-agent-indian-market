"""
Strategy Factory
Creates and manages trading strategy instances
"""

import logging
from typing import Dict, Optional, Any
from strategies.base_strategy import BaseStrategy
from strategies.vwap_strategy import VWAPStrategy
from config.settings import STRATEGY_PARAMETERS

logger = logging.getLogger(__name__)

class StrategyFactory:
    """
    Factory for creating trading strategy instances
    Manages the creation and configuration of all available strategies
    """
    
    def __init__(self):
        self.strategy_classes = {
            'vwap': VWAPStrategy,
            # Other strategies will be added here
            # 'ema': EMAStrategy,
            # 'rsi': RSIStrategy, 
            # 'smc': SMCStrategy
        }
        
        self.default_parameters = STRATEGY_PARAMETERS
    
    def create_strategy(self, strategy_name: str, custom_parameters: Optional[Dict[str, Any]] = None) -> Optional[BaseStrategy]:
        """
        Create a strategy instance
        
        Args:
            strategy_name: Name of the strategy to create
            custom_parameters: Optional custom parameters to override defaults
            
        Returns:
            Strategy instance or None if strategy not found
        """
        try:
            strategy_name = strategy_name.lower()
            
            if strategy_name not in self.strategy_classes:
                logger.error(f"Strategy '{strategy_name}' not found in available strategies")
                return None
            
            # Get default parameters for this strategy
            default_params = self.default_parameters.get(strategy_name, {})
            
            # Merge with custom parameters if provided
            if custom_parameters:
                parameters = {**default_params, **custom_parameters}
            else:
                parameters = default_params
            
            # Create strategy instance
            strategy_class = self.strategy_classes[strategy_name]
            strategy_instance = strategy_class(parameters)
            
            logger.info(f"Created {strategy_name} strategy with parameters: {parameters}")
            
            return strategy_instance
            
        except Exception as e:
            logger.error(f"Error creating strategy '{strategy_name}': {e}")
            return None
    
    def get_available_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available strategies and their default parameters"""
        return {
            name: {
                'class': strategy_class.__name__,
                'default_parameters': self.default_parameters.get(name, {})
            }
            for name, strategy_class in self.strategy_classes.items()
        }
    
    def validate_strategy_parameters(self, strategy_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate strategy parameters"""
        try:
            # Basic validation - can be extended per strategy
            required_params = ['risk_per_trade', 'risk_reward_ratio', 'timeframe']
            
            for param in required_params:
                if param not in parameters:
                    logger.error(f"Missing required parameter '{param}' for strategy '{strategy_name}'")
                    return False
            
            # Validate risk_per_trade
            risk_per_trade = parameters.get('risk_per_trade', 0)
            if not (0.1 <= risk_per_trade <= 10.0):
                logger.error(f"risk_per_trade must be between 0.1 and 10.0, got {risk_per_trade}")
                return False
            
            # Validate risk_reward_ratio
            risk_reward = parameters.get('risk_reward_ratio', 0)
            if not (1.0 <= risk_reward <= 10.0):
                logger.error(f"risk_reward_ratio must be between 1.0 and 10.0, got {risk_reward}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating parameters for strategy '{strategy_name}': {e}")
            return False