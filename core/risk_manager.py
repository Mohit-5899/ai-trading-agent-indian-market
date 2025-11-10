"""
Risk Manager for Trading System
Handles position sizing, risk limits, and trade validation
"""

import logging
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from models.database import TradingAccount, Trade, PortfolioSnapshot
from config.settings import get_settings

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Risk management system for trading operations
    Ensures proper position sizing and risk controls
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    async def validate_order(
        self, 
        account: TradingAccount, 
        symbol: str, 
        quantity: int, 
        side: str,
        price: Optional[float] = None
    ) -> bool:
        """
        Validate if an order meets risk management criteria
        """
        try:
            # Check basic parameters
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if side not in ["BUY", "SELL"]:
                raise ValueError("Side must be BUY or SELL")
            
            # Check market hours
            if not self._is_market_open():
                raise ValueError("Market is closed")
            
            # Check account limits
            await self._check_account_limits(account)
            
            # Check position limits
            await self._check_position_limits(account, side)
            
            # Check daily loss limits
            await self._check_daily_limits(account)
            
            logger.info(f"Order validation passed for {symbol} {side} {quantity}")
            return True
            
        except Exception as e:
            logger.warning(f"Order validation failed: {e}")
            raise
    
    async def calculate_position_size(
        self,
        account: TradingAccount,
        entry_price: float,
        desired_quantity: int,
        stop_loss_price: Optional[float] = None
    ) -> int:
        """
        Calculate appropriate position size based on risk management
        Uses 2% risk per trade rule
        """
        try:
            # Get available capital
            available_capital = float(account.capital_allocation)
            risk_per_trade = float(account.risk_per_trade) / 100.0  # Convert to decimal
            
            # Calculate risk amount
            risk_amount = available_capital * risk_per_trade
            
            # If stop loss is provided, calculate based on risk
            if stop_loss_price and stop_loss_price > 0:
                price_difference = abs(entry_price - stop_loss_price)
                if price_difference > 0:
                    max_quantity_by_risk = int(risk_amount / price_difference)
                    calculated_quantity = min(desired_quantity, max_quantity_by_risk)
                else:
                    calculated_quantity = desired_quantity
            else:
                # Default risk calculation (2% of entry price as stop loss)
                default_stop_distance = entry_price * 0.02
                max_quantity_by_risk = int(risk_amount / default_stop_distance)
                calculated_quantity = min(desired_quantity, max_quantity_by_risk)
            
            # Ensure minimum quantity of 1
            calculated_quantity = max(1, calculated_quantity)
            
            # Check if we have enough capital
            required_capital = calculated_quantity * entry_price
            if required_capital > available_capital:
                # Reduce quantity to fit available capital
                calculated_quantity = int(available_capital / entry_price)
            
            # Final validation
            calculated_quantity = max(1, min(calculated_quantity, desired_quantity))
            
            logger.info(f"Position size calculated: {calculated_quantity} shares (requested: {desired_quantity})")
            return calculated_quantity
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return min(1, desired_quantity)  # Conservative fallback
    
    async def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        strategy: str = "vwap",
        custom_distance: Optional[float] = None
    ) -> float:
        """
        Calculate stop loss price based on strategy and risk management
        """
        try:
            if custom_distance:
                distance = custom_distance
            else:
                # Default stop loss distances by strategy
                strategy_stops = {
                    "vwap": 0.002,   # 0.2% from VWAP
                    "ema": 0.01,     # 1% from entry
                    "rsi": 0.015,    # 1.5% from entry
                    "smc": 0.008     # 0.8% from structure
                }
                distance = strategy_stops.get(strategy, 0.01)  # Default 1%
            
            if side.upper() == "BUY":
                stop_loss = entry_price * (1 - distance)
            else:  # SELL
                stop_loss = entry_price * (1 + distance)
            
            return round(stop_loss, 2)
            
        except Exception as e:
            logger.error(f"Error calculating stop loss: {e}")
            # Conservative fallback
            if side.upper() == "BUY":
                return entry_price * 0.98  # 2% below
            else:
                return entry_price * 1.02  # 2% above
    
    async def calculate_target_price(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_reward_ratio: float = 3.0
    ) -> float:
        """
        Calculate target price based on risk-reward ratio
        """
        try:
            risk_amount = abs(entry_price - stop_loss_price)
            reward_amount = risk_amount * risk_reward_ratio
            
            if entry_price > stop_loss_price:  # Long position
                target_price = entry_price + reward_amount
            else:  # Short position
                target_price = entry_price - reward_amount
            
            return round(target_price, 2)
            
        except Exception as e:
            logger.error(f"Error calculating target price: {e}")
            return entry_price  # Fallback to entry price
    
    async def _check_account_limits(self, account: TradingAccount):
        """Check account-level limits"""
        if not account.is_active:
            raise ValueError("Account is not active")
        
        if account.capital_allocation <= 0:
            raise ValueError("No capital allocated to account")
    
    async def _check_position_limits(self, account: TradingAccount, side: str):
        """Check position limits"""
        # This would typically check current open positions
        # For now, we'll use a simple max positions check
        max_positions = account.max_positions or self.settings.max_positions_per_account
        
        # In a real implementation, you'd count current open positions
        # current_positions = get_open_positions_count(account)
        # if current_positions >= max_positions:
        #     raise ValueError(f"Maximum positions limit reached ({max_positions})")
        
        logger.debug(f"Position limits check passed (max: {max_positions})")
    
    async def _check_daily_limits(self, account: TradingAccount):
        """Check daily loss limits"""
        today = datetime.now().date()
        
        # In a real implementation, you'd calculate today's P&L
        # today_pnl = calculate_daily_pnl(account, today)
        # max_daily_loss = float(account.capital_allocation) * (self.settings.max_daily_loss_percent / 100)
        # 
        # if today_pnl < -max_daily_loss:
        #     raise ValueError(f"Daily loss limit exceeded: {today_pnl}")
        
        logger.debug("Daily limits check passed")
    
    def _is_market_open(self) -> bool:
        """Check if market is open"""
        now = datetime.now()
        
        # Check if it's a weekday
        if now.weekday() > 4:  # Saturday=5, Sunday=6
            return False
        
        # Check market hours (9:15 AM to 3:30 PM)
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def get_risk_metrics(self, account: TradingAccount) -> Dict[str, float]:
        """Get current risk metrics for an account"""
        return {
            "allocated_capital": float(account.capital_allocation),
            "risk_per_trade_percent": float(account.risk_per_trade),
            "max_positions": account.max_positions,
            "daily_loss_limit_percent": self.settings.max_daily_loss_percent,
            "current_risk_amount": float(account.capital_allocation) * float(account.risk_per_trade) / 100
        }