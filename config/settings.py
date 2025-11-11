"""
Application settings and configuration
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AI Trading System - Indian Market"
    debug: bool = False
    version: str = "1.0.0"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/ai_trading"
    
    # Dhan API Configuration
    dhan_client_id: str
    dhan_access_token: str
    dhan_base_url: str = "https://api.dhan.co/v2/"
    
    # OpenRouter API Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Trading Configuration
    trading_enabled: bool = True
    trading_interval_seconds: int = 300  # 5 minutes
    market_open_time: str = "09:15"
    market_close_time: str = "15:30"
    
    # Risk Management
    default_risk_per_trade: float = 2.0  # 2% risk per trade
    max_daily_loss_percent: float = 10.0  # 10% max daily loss
    max_positions_per_account: int = 3
    
    # Redis Configuration (for caching and Celery)
    redis_url: str = "redis://localhost:6379/0"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "trading_system.log"
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("database_url")
    def validate_database_url(cls, v):
        if not v or not v.startswith(("postgresql://", "sqlite://")):
            raise ValueError("Invalid database URL")
        return v
    
    @validator("trading_interval_seconds")
    def validate_trading_interval(cls, v):
        if v < 60:  # Minimum 1 minute
            raise ValueError("Trading interval must be at least 60 seconds")
        return v

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()

# Market Configuration
INDIAN_STOCKS = {
    "RELIANCE": {
        "security_id": "2885",
        "name": "Reliance Industries Ltd",
        "exchange": "NSE_EQ",
        "lot_size": 1,
        "tick_size": 0.05,
        "strategies": ["vwap", "smc"]
    },
    "TCS": {
        "security_id": "11536", 
        "name": "Tata Consultancy Services Ltd",
        "exchange": "NSE_EQ",
        "lot_size": 1,
        "tick_size": 0.05,
        "strategies": ["ema", "rsi"]
    },
    "INFY": {
        "security_id": "1594",
        "name": "Infosys Ltd", 
        "exchange": "NSE_EQ",
        "lot_size": 1,
        "tick_size": 0.05,
        "strategies": ["vwap", "ema"]
    },
    "HDFCBANK": {
        "security_id": "1333",
        "name": "HDFC Bank Ltd",
        "exchange": "NSE_EQ", 
        "lot_size": 1,
        "tick_size": 0.05,
        "strategies": ["rsi", "smc"]
    },
    "ICICIBANK": {
        "security_id": "4963",
        "name": "ICICI Bank Ltd",
        "exchange": "NSE_EQ",
        "lot_size": 1, 
        "tick_size": 0.05,
        "strategies": ["vwap", "rsi"]
    }
}

# LLM Models Configuration
LLM_MODELS = {
    "primary": {
        "name": "claude-3-5-sonnet",
        "provider": "openrouter", 
        "stocks": ["RELIANCE", "TCS", "INFY"],
        "capital_allocation": 60,  # 60% of total capital
        "strategies": ["vwap", "ema"]
    },
    "secondary": {
        "name": "gpt-4-turbo",
        "provider": "openrouter",
        "stocks": ["HDFCBANK", "ICICIBANK"], 
        "capital_allocation": 40,  # 40% of total capital
        "strategies": ["rsi", "smc"]
    }
}

# Strategy Parameters
STRATEGY_PARAMETERS = {
    "vwap": {
        "risk_per_trade": 2.0,
        "risk_reward_ratio": 3.0,
        "timeframe": "5m",
        "momentum_threshold": 0.5,
        "retest_tolerance": 0.1
    },
    "ema": {
        "risk_per_trade": 1.5,
        "risk_reward_ratio": 2.5,
        "timeframe": "15m",
        "fast_period": 9,
        "slow_period": 21
    },
    "rsi": {
        "risk_per_trade": 1.0,
        "risk_reward_ratio": 2.0,
        "timeframe": "5m",
        "period": 14,
        "overbought": 70,
        "oversold": 30
    },
    "smc": {
        "risk_per_trade": 2.5,
        "risk_reward_ratio": 4.0,
        "timeframe": "15m",
        "order_block_strength": 3,
        "fvg_threshold": 0.5
    }
}