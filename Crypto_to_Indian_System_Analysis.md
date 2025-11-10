# Crypto Trading Agent → Indian Market Python System Analysis

## Current Crypto System Architecture (TypeScript/Bun)

### Core Components Analysis

#### 1. **Main Trading Engine** (`index.ts`)
**Function**: 
- Runs every 5 minutes via `setInterval`
- Fetches technical indicators for BTC/ETH/SOL (5m & 4h candles)
- Invokes LLM with enriched prompt containing market data + portfolio state
- Executes trades via tool calling (`createPosition`, `closeAllPosition`)

**Key Features**:
- Multi-market support (3 crypto markets)
- Multi-timeframe analysis (5m intraday, 4h long-term)
- LLM-driven decision making
- Database logging of all actions

#### 2. **Markets Configuration** (`markets.ts`)
```typescript
MARKETS = {
    "BTC": { marketId: 1, priceDecimals: 10, qtyDecimals: 100000 },
    "ETH": { marketId: 0, priceDecimals: 100, qtyDecimals: 10000 },
    "SOL": { marketId: 2, priceDecimals: 1000, qtyDecimals: 1000 }
}
```

#### 3. **Trading Operations**
- `createPosition.ts`: Opens leveraged positions (LONG/SHORT, 10x leverage)
- `cancelOrder.ts`: Closes ALL positions at once
- `getPortfolio.ts`: Fetches portfolio value + available cash
- `openPositions.ts`: Gets current positions

#### 4. **Technical Analysis** (`indicators.ts`, `stockData.ts`)
- **Indicators**: EMA20, MACD
- **Timeframes**: 5m (intraday), 4h (long-term)
- **Data Source**: Lighter Protocol API

#### 5. **Database Schema** (PostgreSQL + Prisma)
```sql
Models: Trading accounts with API keys, model names
Invocations: Each LLM execution with response
ToolCalls: Position create/close logs
PortfolioSize: Portfolio value timeseries
```

#### 6. **LLM Integration**
- **Provider**: OpenRouter API
- **Tool Calling**: 2 tools (createPosition, closeAllPosition)
- **Prompt**: Dynamic prompt with market data, positions, portfolio value
- **Constraints**: Only 1 position at a time, must close all to modify

#### 7. **Backend API** (`backend.ts`)
- Express server on port 3000
- `/performance`: Portfolio timeseries (5-min cache)
- `/invocations`: Recent LLM decisions (2-min cache)

#### 8. **Frontend** (React + TypeScript)
- Performance visualization (Recharts)
- Live trade monitoring
- Recent invocations display

---

## Python Equivalent for Indian Market

### Core Mapping: Crypto → Indian

| Crypto Component | Indian Market Equivalent |
|-----------------|-------------------------|
| **Lighter Protocol API** | **Dhan API** (NSE stocks) |
| **BTC/ETH/SOL** | **RELIANCE/TCS/INFY/HDFCBANK/ICICIBANK** |
| **10x Leverage** | **No leverage (cash market)** |
| **EMA20 + MACD** | **VWAP + EMA + RSI + SMC** |
| **TypeScript/Bun** | **Python/FastAPI** |
| **Prisma ORM** | **SQLAlchemy ORM** |
| **Express API** | **FastAPI REST API** |
| **Tool Calling** | **MCP Protocol** |

---

## Python Implementation Structure

### 1. **Main Trading Engine** (Python equivalent of `index.ts`)

```python
# main.py - Core trading engine
import asyncio
from datetime import datetime, timedelta
import schedule
from core.trading_engine import TradingEngine
from core.llm_manager import LLMManager
from data.market_data_manager import MarketDataManager
from models.database import get_session

class IndianMarketTradingEngine:
    def __init__(self):
        self.market_data = MarketDataManager()
        self.llm_manager = LLMManager()
        self.trading_engine = TradingEngine()
        
    async def invoke_agent(self, account):
        """Equivalent of invokeAgent() function"""
        # 1. Fetch market data for 5 stocks, multiple timeframes
        market_data = await self.collect_market_data()
        
        # 2. Get portfolio status
        portfolio = await self.trading_engine.get_portfolio(account)
        
        # 3. Get open positions  
        positions = await self.trading_engine.get_positions(account)
        
        # 4. Create enriched prompt
        prompt = self.create_prompt(market_data, portfolio, positions, account)
        
        # 5. Get LLM decision with tool calling
        response = await self.llm_manager.get_decision(
            model=account.model_name,
            prompt=prompt,
            tools=self.get_trading_tools(account)
        )
        
        # 6. Log invocation to database
        await self.log_invocation(account, response)
        
    async def collect_market_data(self):
        """Collect multi-timeframe data for all stocks"""
        stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        data = {}
        
        for stock in stocks:
            data[stock] = {
                "5m": await self.market_data.get_5min_data(stock),
                "15m": await self.market_data.get_15min_data(stock),
                "1h": await self.market_data.get_1h_data(stock),
                "daily": await self.market_data.get_daily_data(stock)
            }
            
            # Calculate indicators
            data[stock]["indicators"] = {
                "vwap": self.calculate_vwap(data[stock]["5m"]),
                "ema20": self.calculate_ema(data[stock]["15m"], 20),
                "rsi": self.calculate_rsi(data[stock]["5m"], 14),
                "smc_signals": self.detect_smc_patterns(data[stock])
            }
            
        return data
        
    def get_trading_tools(self, account):
        """Trading tools for LLM (MCP protocol)"""
        return {
            "buy_stock": self.create_buy_tool(account),
            "sell_stock": self.create_sell_tool(account),
            "close_all_positions": self.create_close_all_tool(account),
            "get_portfolio": self.create_portfolio_tool(account)
        }
        
    async def run_trading_loop(self):
        """Main trading loop - runs every 5 minutes"""
        while True:
            try:
                # Get all active accounts
                accounts = await self.get_active_accounts()
                
                # Process each account
                for account in accounts:
                    await self.invoke_agent(account)
                    
            except Exception as e:
                print(f"Trading loop error: {e}")
                
            # Wait 5 minutes
            await asyncio.sleep(300)

# Run the system
if __name__ == "__main__":
    engine = IndianMarketTradingEngine()
    asyncio.run(engine.run_trading_loop())
```

### 2. **Stock Configuration** (Python equivalent of `markets.ts`)

```python
# config/stocks.py
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
```

### 3. **Trading Operations** (Python equivalent of trading files)

```python
# core/trading_engine.py
from data.dhan_client import DhanClient
from typing import Dict, List

class TradingEngine:
    def __init__(self):
        self.dhan = DhanClient()
        
    async def buy_stock(self, account, symbol: str, quantity: int, strategy: str):
        """Equivalent of createPosition.ts"""
        try:
            # Calculate position size based on 2% risk
            position_size = self.calculate_position_size(
                account_value=account.portfolio_value,
                risk_percent=2.0,
                entry_price=await self.get_current_price(symbol)
            )
            
            # Place buy order via Dhan API
            order = await self.dhan.place_order(
                symbol=symbol,
                side="BUY", 
                quantity=min(quantity, position_size),
                order_type="MARKET"
            )
            
            # Log to database
            await self.log_trade(account, order, strategy)
            
            return f"Bought {quantity} shares of {symbol}"
            
        except Exception as e:
            return f"Error buying {symbol}: {str(e)}"
            
    async def sell_stock(self, account, symbol: str, quantity: int, strategy: str):
        """Sell specific stock position"""
        # Similar to buy_stock but for selling
        pass
        
    async def close_all_positions(self, account):
        """Equivalent of cancelAllOrders.ts"""
        try:
            positions = await self.dhan.get_positions(account.account_id)
            
            for position in positions:
                if position.quantity > 0:
                    await self.dhan.place_order(
                        symbol=position.symbol,
                        side="SELL",
                        quantity=position.quantity,
                        order_type="MARKET"
                    )
                    
            return "All positions closed successfully"
            
        except Exception as e:
            return f"Error closing positions: {str(e)}"
            
    async def get_portfolio(self, account):
        """Equivalent of getPortfolio.ts"""
        return await self.dhan.get_portfolio(account.account_id)
        
    async def get_positions(self, account):
        """Equivalent of openPositions.ts"""
        return await self.dhan.get_positions(account.account_id)
```

### 4. **Database Models** (SQLAlchemy equivalent of Prisma schema)

```python
# models/database.py
from sqlalchemy import Column, String, Integer, DateTime, Text, DECIMAL, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class TradingAccount(Base):
    __tablename__ = "trading_accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=False)  # LLM model
    dhan_api_key = Column(String, nullable=False)
    dhan_client_id = Column(String, nullable=False) 
    invocation_count = Column(Integer, default=0)
    capital_allocation = Column(DECIMAL(15, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invocations = relationship("Invocation", back_populates="account")
    trades = relationship("Trade", back_populates="account")
    portfolio_snapshots = relationship("PortfolioSnapshot", back_populates="account")

class Invocation(Base):
    __tablename__ = "invocations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("trading_accounts.id"))
    llm_response = Column(Text)
    market_data_context = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="invocations")
    tool_calls = relationship("ToolCall", back_populates="invocation")

class ToolCall(Base):
    __tablename__ = "tool_calls"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invocation_id = Column(String, ForeignKey("invocations.id"))
    tool_name = Column(String)  # buy_stock, sell_stock, close_all_positions
    parameters = Column(Text)   # JSON string of tool parameters
    result = Column(Text)       # Tool execution result
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships  
    invocation = relationship("Invocation", back_populates="tool_calls")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("trading_accounts.id"))
    symbol = Column(String, nullable=False)
    side = Column(String)  # BUY, SELL
    quantity = Column(Integer)
    entry_price = Column(DECIMAL(10, 4))
    exit_price = Column(DECIMAL(10, 4))
    strategy_used = Column(String)  # vwap, ema, rsi, smc
    pnl = Column(DECIMAL(15, 4))
    status = Column(String, default="OPEN")  # OPEN, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="trades")

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("trading_accounts.id"))
    total_value = Column(DECIMAL(15, 4))
    available_cash = Column(DECIMAL(15, 4)) 
    invested_amount = Column(DECIMAL(15, 4))
    day_pnl = Column(DECIMAL(15, 4))
    total_pnl = Column(DECIMAL(15, 4))
    positions_json = Column(Text)  # JSON string of current positions
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="portfolio_snapshots")
```

### 5. **FastAPI Backend** (Python equivalent of `backend.ts`)

```python
# api/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.database import get_session
from models import schemas
from core.trading_engine import TradingEngine
from data.market_data_manager import MarketDataManager
import asyncio
from typing import List

app = FastAPI(title="Indian Market AI Trading System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trading_engine = TradingEngine()
market_data_manager = MarketDataManager()

# Portfolio endpoints (equivalent to /performance)
@app.get("/api/portfolio/{account_id}/performance")
async def get_portfolio_performance(account_id: str, db: Session = Depends(get_session)):
    """Get portfolio performance timeseries"""
    snapshots = db.query(PortfolioSnapshot)\
                  .filter(PortfolioSnapshot.account_id == account_id)\
                  .order_by(PortfolioSnapshot.created_at)\
                  .all()
    
    return {
        "performance": [
            {
                "timestamp": snapshot.created_at,
                "total_value": float(snapshot.total_value),
                "day_pnl": float(snapshot.day_pnl),
                "total_pnl": float(snapshot.total_pnl)
            }
            for snapshot in snapshots
        ]
    }

# Invocations endpoint (equivalent to /invocations) 
@app.get("/api/invocations")
async def get_recent_invocations(limit: int = 30, db: Session = Depends(get_session)):
    """Get recent LLM invocations and decisions"""
    invocations = db.query(Invocation)\
                    .order_by(Invocation.created_at.desc())\
                    .limit(limit)\
                    .all()
    
    return {
        "invocations": [
            {
                "id": inv.id,
                "account_name": inv.account.name,
                "response": inv.llm_response,
                "created_at": inv.created_at,
                "tool_calls": [
                    {
                        "tool_name": tc.tool_name,
                        "parameters": tc.parameters,
                        "result": tc.result
                    }
                    for tc in inv.tool_calls
                ]
            }
            for inv in invocations
        ]
    }

# Market data endpoints
@app.get("/api/market-data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "5m"):
    """Get real-time market data for a stock"""
    if timeframe == "5m":
        data = await market_data_manager.get_5min_data(symbol)
    elif timeframe == "15m":
        data = await market_data_manager.get_15min_data(symbol)
    elif timeframe == "1h":
        data = await market_data_manager.get_1h_data(symbol)
    else:
        data = await market_data_manager.get_daily_data(symbol)
    
    return {"symbol": symbol, "timeframe": timeframe, "data": data}

# Trading endpoints  
@app.post("/api/trades/execute")
async def execute_trade(trade_request: schemas.TradeRequest):
    """Execute a manual trade"""
    return await trading_engine.execute_trade(trade_request)

@app.get("/api/trades/{account_id}")
async def get_trades(account_id: str, db: Session = Depends(get_session)):
    """Get trade history for account"""
    trades = db.query(Trade)\
               .filter(Trade.account_id == account_id)\
               .order_by(Trade.created_at.desc())\
               .all()
    
    return {"trades": trades}

# System control endpoints
@app.post("/api/system/start-trading")
async def start_trading():
    """Start the automated trading engine"""
    # This would start the main trading loop
    return {"status": "Trading started"}

@app.post("/api/system/stop-trading")  
async def stop_trading():
    """Stop the automated trading engine"""
    return {"status": "Trading stopped"}

# Health check
@app.get("/api/health")
async def health_check():
    """System health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

---

## Key Differences: Crypto vs Indian Market

| Aspect | Crypto System | Indian Market System |
|--------|---------------|---------------------|
| **Leverage** | 10x leverage | No leverage (cash market) |
| **Trading Hours** | 24/7 | 9:15 AM - 3:30 PM |
| **Position Limits** | 1 position at a time | Multiple positions allowed |
| **Settlement** | Instant | T+1 settlement |
| **Risk Management** | Leverage-based | 2% cash risk per trade |
| **Market Depth** | High liquidity | Variable liquidity |
| **Regulation** | Less regulated | SEBI regulated |

---

## Implementation Priority

### Phase 1: Core Engine ⭐
1. **Market Data Integration**: Port existing `market_data_manager.py` and `vwap_calculator.py`
2. **Database Setup**: SQLAlchemy models equivalent to Prisma schema
3. **Basic Trading Engine**: Dhan API integration for buy/sell/portfolio

### Phase 2: LLM Integration ⭐⭐
4. **Multi-LLM Manager**: Support 2 different models with strategy allocation
5. **MCP Tools**: Trading tools (buy_stock, sell_stock, close_all_positions)
6. **Prompt Engineering**: Dynamic prompts with Indian market context

### Phase 3: API & Frontend ⭐⭐⭐
7. **FastAPI Backend**: REST endpoints equivalent to Express server
8. **Frontend Integration**: Connect React frontend to Python backend
9. **Real-time Updates**: WebSocket support for live data

This analysis provides the exact mapping needed to recreate the crypto system's successful architecture for Indian markets using Python.