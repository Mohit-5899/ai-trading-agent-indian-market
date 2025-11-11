"""
Pydantic schemas for API request/response models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

# === REQUEST SCHEMAS ===

class TradeRequest(BaseModel):
    """Trade execution request"""
    account_id: str
    symbol: str
    side: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: int = Field(..., gt=0)
    strategy: str
    order_type: str = Field(default="MARKET", pattern="^(MARKET|LIMIT)$")
    price: Optional[float] = None

class AccountCreateRequest(BaseModel):
    """Create new trading account request"""
    name: str
    model_name: str
    dhan_client_id: str
    dhan_access_token: str
    capital_allocation: float = Field(..., gt=0)
    allocation_percentage: float = Field(..., gt=0, le=100)
    risk_per_trade: float = Field(default=2.0, gt=0, le=10)

# === RESPONSE SCHEMAS ===

class TradeResponse(BaseModel):
    """Trade information response"""
    id: str
    account_name: str
    stock_symbol: str
    strategy_name: str
    side: str
    quantity: int
    entry_price: float
    exit_price: Optional[float] = None
    net_pnl: Optional[float] = None
    status: str
    executed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    """Portfolio information response"""
    account_id: str
    total_value: float
    available_cash: float
    invested_amount: float
    day_pnl: float
    total_pnl: float
    return_percentage: float
    positions: List[Dict[str, Any]]
    open_trades_count: int
    last_updated: datetime

class InvocationResponse(BaseModel):
    """LLM invocation response"""
    id: str
    account_id: str
    account_name: str
    llm_response: Optional[str] = None
    execution_time_ms: int
    tokens_used: int
    created_at: str
    tool_calls: List[Dict[str, Any]]

class SystemStatusResponse(BaseModel):
    """System status response"""
    status: str
    active_accounts: Optional[int] = None
    today_trades: Optional[int] = None
    last_invocation: Optional[datetime] = None
    trading_enabled: Optional[bool] = None
    market_open: Optional[bool] = None
    error_message: Optional[str] = None
    timestamp: datetime

class MarketDataResponse(BaseModel):
    """Market data response"""
    symbol: str
    timeframe: str
    data: List[Dict[str, Any]]
    timestamp: datetime

class IndicatorResponse(BaseModel):
    """Technical indicators response"""
    symbol: str
    indicators: Dict[str, Any]
    timestamp: datetime

class SignalResponse(BaseModel):
    """Trading signal response"""
    id: str
    stock_symbol: str
    strategy_name: str
    signal_type: str
    strength: float
    confidence: float
    price: float
    reasoning: Optional[str] = None
    created_at: datetime

# === UTILITY SCHEMAS ===

class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    total_return: float
    total_return_percentage: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    total_trades: int
    winning_trades: int
    losing_trades: int

class RiskMetrics(BaseModel):
    """Risk management metrics"""
    daily_pnl: float
    max_daily_loss: float
    current_positions: int
    max_positions: int
    capital_utilization: float