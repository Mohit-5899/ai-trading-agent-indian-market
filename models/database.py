"""
Database models for AI Trading System
SQLAlchemy models equivalent to the crypto system's Prisma schema
"""

from datetime import datetime
import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Column, String, Integer, DateTime, Text, DECIMAL, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TradingAccount(Base):
    """Trading accounts - equivalent to Models table in crypto system"""
    __tablename__ = "trading_accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    # LLM Configuration
    model_name = Column(String(100), nullable=False)  # claude-3-5-sonnet, gpt-4-turbo
    openrouter_api_key = Column(String(255))
    
    # Dhan API Configuration  
    dhan_client_id = Column(String(100), nullable=False)
    dhan_access_token = Column(String(255), nullable=False)
    account_id = Column(String(100), nullable=False)
    
    # Trading Configuration
    capital_allocation = Column(DECIMAL(15, 2), nullable=False)  # Allocated capital
    allocation_percentage = Column(DECIMAL(5, 2), nullable=False)  # % of total capital
    risk_per_trade = Column(DECIMAL(5, 2), default=2.0)  # Risk percentage per trade
    max_positions = Column(Integer, default=3)  # Max simultaneous positions
    
    # System State
    invocation_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    last_executed = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invocations = relationship("Invocation", back_populates="account", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="account", cascade="all, delete-orphan")
    portfolio_snapshots = relationship("PortfolioSnapshot", back_populates="account", cascade="all, delete-orphan")
    strategy_assignments = relationship("StrategyAssignment", back_populates="account", cascade="all, delete-orphan")

class Strategy(Base):
    """Trading strategies configuration"""
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False, index=True)  # vwap, ema, rsi, smc
    description = Column(Text)
    
    # Strategy Parameters (JSON)
    parameters = Column(JSON)  # Strategy-specific parameters
    
    # Configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    strategy_assignments = relationship("StrategyAssignment", back_populates="strategy")
    trades = relationship("Trade", back_populates="strategy")
    signals = relationship("TradingSignal", back_populates="strategy")

class StrategyAssignment(Base):
    """Assignment of strategies to LLM accounts"""
    __tablename__ = "strategy_assignments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("trading_accounts.id"), nullable=False)
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False)
    
    # Configuration
    weight = Column(DECIMAL(5, 2), default=100.0)  # Strategy weight/priority
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="strategy_assignments")
    strategy = relationship("Strategy", back_populates="strategy_assignments")
    
    # Ensure unique assignment per account-strategy
    __table_args__ = (
        {"schema": None},
    )

class Stock(Base):
    """Indian stock information"""
    __tablename__ = "stocks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), unique=True, nullable=False, index=True)  # RELIANCE, TCS, etc.
    name = Column(String(200), nullable=False)
    
    # Dhan API Configuration
    security_id = Column(String(20), nullable=False, unique=True)
    exchange = Column(String(10), default="NSE_EQ")
    
    # Trading Configuration
    lot_size = Column(Integer, default=1)
    tick_size = Column(DECIMAL(10, 4), default=0.05)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="stock")
    signals = relationship("TradingSignal", back_populates="stock")
    market_data = relationship("MarketData", back_populates="stock")

class Invocation(Base):
    """LLM invocations - equivalent to crypto system's Invocations"""
    __tablename__ = "invocations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("trading_accounts.id"), nullable=False)
    
    # LLM Response
    llm_response = Column(Text)
    prompt_used = Column(Text)
    
    # Context Data
    market_data_context = Column(JSON)  # Market data at time of invocation
    portfolio_context = Column(JSON)    # Portfolio state at invocation
    
    # Execution Info
    execution_time_ms = Column(Integer)  # How long LLM took to respond
    tokens_used = Column(Integer)       # Tokens consumed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="invocations")
    tool_calls = relationship("ToolCall", back_populates="invocation", cascade="all, delete-orphan")

class ToolCall(Base):
    """Tool calls made by LLM - equivalent to crypto system's ToolCalls"""
    __tablename__ = "tool_calls"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invocation_id = Column(String, ForeignKey("invocations.id"), nullable=False)
    
    # Tool Information
    tool_name = Column(String(50), nullable=False)  # buy_stock, sell_stock, close_all_positions
    parameters = Column(JSON)                       # Tool parameters as JSON
    result = Column(Text)                          # Tool execution result
    
    # Execution Status
    status = Column(String(20), default="PENDING")  # PENDING, SUCCESS, FAILED
    error_message = Column(Text)                    # Error details if failed
    execution_time_ms = Column(Integer)             # Execution time
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invocation = relationship("Invocation", back_populates="tool_calls")

class Trade(Base):
    """Individual trades executed"""
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # References
    account_id = Column(String, ForeignKey("trading_accounts.id"), nullable=False)
    stock_id = Column(String, ForeignKey("stocks.id"), nullable=False) 
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False)
    
    # Order Information
    dhan_order_id = Column(String(50), unique=True)  # Dhan order ID
    side = Column(String(10), nullable=False)         # BUY, SELL
    quantity = Column(Integer, nullable=False)
    
    # Pricing
    entry_price = Column(DECIMAL(10, 4))
    exit_price = Column(DECIMAL(10, 4))
    stop_loss = Column(DECIMAL(10, 4))
    target_price = Column(DECIMAL(10, 4))
    
    # P&L
    gross_pnl = Column(DECIMAL(15, 4))      # Before commissions
    commission = Column(DECIMAL(10, 4))     # Trading fees
    net_pnl = Column(DECIMAL(15, 4))        # After commissions
    
    # Status and Timing
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, CANCELLED
    executed_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Risk Management
    risk_amount = Column(DECIMAL(15, 4))    # Amount at risk
    risk_reward_ratio = Column(DECIMAL(5, 2))  # Planned R:R
    
    # Metadata
    notes = Column(Text)                    # Additional notes
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="trades")
    stock = relationship("Stock", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")

class TradingSignal(Base):
    """Trading signals generated by strategies"""
    __tablename__ = "trading_signals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # References
    account_id = Column(String, ForeignKey("trading_accounts.id"), nullable=False)
    stock_id = Column(String, ForeignKey("stocks.id"), nullable=False)
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False)
    
    # Signal Information
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    strength = Column(DECIMAL(5, 2))                  # Signal strength 0-100
    confidence = Column(DECIMAL(5, 2))                # LLM confidence 0-100
    
    # Market Context
    price = Column(DECIMAL(10, 4), nullable=False)
    volume = Column(Integer)
    
    # Technical Indicators (JSON)
    indicators = Column(JSON)                         # Technical indicators at signal time
    
    # LLM Reasoning
    reasoning = Column(Text)                          # LLM explanation for signal
    
    # Status
    is_acted_upon = Column(Boolean, default=False)   # Whether signal was traded
    related_trade_id = Column(String)                 # If traded, link to trade
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    account = relationship("TradingAccount")
    stock = relationship("Stock", back_populates="signals")
    strategy = relationship("Strategy", back_populates="signals")

class PortfolioSnapshot(Base):
    """Portfolio snapshots for performance tracking"""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("trading_accounts.id"), nullable=False)
    
    # Portfolio Values
    total_value = Column(DECIMAL(15, 4), nullable=False)
    available_cash = Column(DECIMAL(15, 4), nullable=False)
    invested_amount = Column(DECIMAL(15, 4), nullable=False)
    
    # P&L Tracking
    day_pnl = Column(DECIMAL(15, 4))         # Day's P&L
    total_pnl = Column(DECIMAL(15, 4))       # Total P&L since start
    realized_pnl = Column(DECIMAL(15, 4))    # From closed trades
    unrealized_pnl = Column(DECIMAL(15, 4))  # From open positions
    
    # Positions (JSON array of current positions)
    positions = Column(JSON)
    
    # Performance Metrics
    return_percentage = Column(DECIMAL(8, 4))    # % return
    sharpe_ratio = Column(DECIMAL(8, 4))         # Risk-adjusted return
    max_drawdown = Column(DECIMAL(8, 4))         # Maximum drawdown %
    
    # Market Context
    market_session = Column(String(20))          # PREMARKET, REGULAR, POSTMARKET
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="portfolio_snapshots")

class MarketData(Base):
    """Market data cache for faster access"""
    __tablename__ = "market_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id = Column(String, ForeignKey("stocks.id"), nullable=False)
    
    # Timeframe and Data
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 15m, 1h, 1d
    timestamp = Column(DateTime, nullable=False)
    
    # OHLCV Data
    open_price = Column(DECIMAL(10, 4))
    high_price = Column(DECIMAL(10, 4))
    low_price = Column(DECIMAL(10, 4))
    close_price = Column(DECIMAL(10, 4))
    volume = Column(Integer)
    
    # Additional Data
    typical_price = Column(DECIMAL(10, 4))       # (H+L+C)/3
    vwap = Column(DECIMAL(10, 4))                # VWAP if calculated
    
    # Cache Management
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="market_data")
    
    # Ensure unique data per stock-timeframe-timestamp
    __table_args__ = (
        {"schema": None},
    )

# Database connection and session management
def create_database_engine(database_url: str):
    """Create database engine"""
    return create_engine(database_url, echo=False)

def create_session_factory(engine):
    """Create session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session(session_factory):
    """Get database session"""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()

def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)