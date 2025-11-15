# AI Trading Agent - Codebase Structure & Analysis

## Project Overview

An automated trading system for the Indian stock market (NSE) using multiple LLMs and AI-driven strategies. Built with Python backend (FastAPI) and Streamlit frontend, integrated with Dhan API for live market data and trading execution.

**Key Performance:** VWAP Breakout/Retest strategy achieved 39.74% return in 90-day backtest with 51.8% win rate on RELIANCE stock.

---

## Technology Stack

### Core Framework
- **FastAPI** (v0.104.1) - RESTful API backend
- **Streamlit** (v1.28.1) - Real-time dashboard frontend
- **SQLAlchemy** (v2.0.23) - ORM for database operations
- **PostgreSQL** - Primary database for persistent storage
- **Redis** (v4.6.0) - Caching and task queue
- **Celery** (v5.3.4) - Background task processing

### Data & Market Integration
- **Dhan API** (dhanhq v2.0.2) - Indian broker API for market data and trading
- **Pandas** (v2.1.3) - Data manipulation and analysis
- **NumPy** (v1.25.2) - Numerical computations
- **TA-Lib** (v0.4.32) - Technical analysis indicators

### LLM Integration
- **OpenAI** (v1.6.1) - GPT-4 Turbo integration via OpenRouter
- **Anthropic** (v0.7.8) - Claude 3.5 Sonnet integration
- **OpenRouter API** - Unified LLM provider endpoint

### Visualization & Charting
- **Plotly** (v5.17.0) - Interactive charts and graphs
- **Altair** (v5.1.2) - Declarative visualization
- **Streamlit-aggrid** (v0.3.4) - Advanced data tables

### Development & DevOps
- **Docker** & **Docker Compose** - Containerization
- **APScheduler** (v3.10.4) - Job scheduling
- **Python-dotenv** - Environment variable management
- **Pytest** - Testing framework (configured but minimal)

---

## Project Structure

```
ai-trading-agent-indian-market/
│
├── 📊 Frontend (Streamlit Dashboard)
│   ├── frontend/
│   │   ├── dashboard.py              # Main Streamlit dashboard (5 tabs)
│   │   ├── run_dashboard.py          # Dashboard launch script
│   │   └── requirements.txt          # Frontend dependencies
│   │
├── 🔧 API Backend (FastAPI)
│   ├── api/
│   │   ├── main.py                  # FastAPI application (32 endpoints)
│   │   └── schemas.py               # Pydantic request/response models
│   │
├── 💾 Database & Models
│   ├── models/
│   │   └── database.py              # SQLAlchemy models (10 tables)
│   │
├── 📈 Trading Core
│   ├── core/
│   │   ├── trading_engine.py        # Main orchestrator
│   │   ├── llm_manager.py           # LLM integration and decision making
│   │   └── risk_manager.py          # Position sizing and risk controls
│   │
├── 📊 Market Data
│   ├── data/
│   │   ├── enhanced_market_data_manager.py  # Async data fetching
│   │   ├── dhan_client.py                   # Dhan API wrapper
│   │   └── market_data_manager.py           # (Original) multi-timeframe caching
│   │
├── 🎯 Strategies
│   ├── strategies/
│   │   ├── base_strategy.py         # Abstract strategy class
│   │   ├── strategy_factory.py      # Strategy instantiation
│   │   ├── vwap_strategy.py         # VWAP breakout/retest (primary)
│   │   ├── ema_strategy.py          # EMA crossover (untested)
│   │   └── rsi_strategy.py          # RSI momentum (untested)
│   │
├── ⚙️ Configuration
│   ├── config/
│   │   ├── settings.py              # App settings + stock/LLM configs
│   │   └── __init__.py
│   │
├── 🛠️ Utilities & Setup
│   ├── setup_database.py            # Database initialization
│   ├── main.py                      # Entry point (placeholder)
│   ├── backtest_vwap.py             # VWAP strategy backtest engine
│   ├── vwap_calculator.py           # VWAP math utilities
│   ├── market_data_manager.py       # Original data manager
│   │
├── 🐳 Docker & Infrastructure
│   ├── Dockerfile                   # Container definition
│   ├── docker-compose.yml           # Multi-container orchestration
│   ├── DOCKER_SETUP.md              # Docker setup guide
│   │
├── 📚 Documentation
│   ├── README.md                    # Project overview
│   ├── SETUP_GUIDE.md               # Installation instructions
│   ├── Python_AI_Trading_System_Architecture.md
│   ├── Crypto_to_Indian_System_Analysis.md
│   │
├── 📋 Configuration Files
│   ├── requirements.txt              # Python dependencies
│   ├── .env                         # Environment variables (not in git)
│   ├── .gitignore
│   └── .dockerignore
```

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                      │
│                     (Port 8501)                              │
│  - Portfolio Performance  - Trading History                  │
│  - Account Overview       - LLM Decisions                    │
│  - System Control         - Real-time Metrics                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Requests
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                            │
│                  (Port 8000)                                 │
│                                                              │
│  Endpoints:                                                 │
│  ├── /api/portfolio/* - Portfolio management               │
│  ├── /api/trades/* - Trade history                         │
│  ├── /api/invocations/* - LLM decisions                    │
│  ├── /api/market-data/* - Market data                      │
│  ├── /api/accounts/* - Account management                  │
│  ├── /api/system/* - System control                        │
│  └── /api/health - Health check                            │
└──────────┬──────────────────────────┬──────────────────────┘
           │                          │
      ┌────▼──────────────┐      ┌────▼──────────────┐
      │   TRADING ENGINE  │      │   CORE SERVICES  │
      │                  │      │                  │
      │ ├─ Orchestrator  │      │ ├─ LLM Manager   │
      │ ├─ Scheduler     │      │ ├─ Risk Manager  │
      │ ├─ Account Loop  │      │ └─ Strategy Mgr  │
      │ └─ 5-min cycle   │      └──────────────────┘
      └──────────┬────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼──┐   ┌───▼────┐  ┌───▼─────┐
│ Dhan  │   │ Market │  │   LLM   │
│ API   │   │ Data   │  │ Providers
│       │   │Manager │  │
└───────┘   └────────┘  └─────────┘
     │           │           │
     └───────────┼───────────┘
                 │
          ┌──────▼──────────────┐
          │   PostgreSQL DB     │
          │                     │
          │ ├─ Trades           │
          │ ├─ Invocations      │
          │ ├─ Portfolio        │
          │ ├─ Market Data      │
          │ ├─ Accounts         │
          │ ├─ Strategies       │
          │ └─ Signals          │
          └─────────────────────┘
                 │
          ┌──────▼──────┐
          │    Redis    │
          │  Caching    │
          └─────────────┘
```

---

## Database Schema (SQLAlchemy Models)

### Core Tables

#### 1. **TradingAccount** (trading_accounts)
```
- id (PK)
- name (unique)
- model_name (Claude, GPT-4, etc)
- dhan credentials (client_id, access_token)
- capital_allocation, allocation_percentage
- risk_per_trade, max_positions
- invocation_count, is_active
- timestamps
```

#### 2. **Strategy** (strategies)
```
- id (PK)
- name (vwap, ema, rsi, smc)
- description
- parameters (JSON) - Strategy-specific config
- is_active
```

#### 3. **Stock** (stocks)
```
- id (PK)
- symbol (RELIANCE, TCS, etc)
- name, security_id
- exchange, lot_size, tick_size
- is_active
```

#### 4. **Trade** (trades) - Core trading record
```
- id, account_id (FK), stock_id (FK), strategy_id (FK)
- dhan_order_id (unique)
- side (BUY/SELL), quantity
- entry_price, exit_price
- stop_loss, target_price
- gross_pnl, commission, net_pnl
- status (OPEN/CLOSED/CANCELLED)
- executed_at, closed_at
- risk_amount, risk_reward_ratio
```

#### 5. **Invocation** (invocations) - LLM decision log
```
- id, account_id (FK)
- llm_response (text), prompt_used
- market_data_context (JSON)
- portfolio_context (JSON)
- execution_time_ms, tokens_used
- created_at, updated_at
```

#### 6. **ToolCall** (tool_calls) - LLM tool executions
```
- id, invocation_id (FK)
- tool_name, parameters (JSON)
- result, status
- error_message, execution_time_ms
```

#### 7. **TradingSignal** (trading_signals)
```
- id, account_id, stock_id, strategy_id (FKs)
- signal_type (BUY/SELL/HOLD)
- strength, confidence
- price, volume
- indicators (JSON), reasoning
- is_acted_upon, related_trade_id
```

#### 8. **PortfolioSnapshot** (portfolio_snapshots) - Performance tracking
```
- id, account_id (FK)
- total_value, available_cash, invested_amount
- day_pnl, total_pnl, realized_pnl, unrealized_pnl
- positions (JSON array)
- return_percentage, sharpe_ratio, max_drawdown
- market_session, created_at
```

#### 9. **MarketData** (market_data) - Data cache
```
- id, stock_id (FK)
- timeframe, open, high, low, close
- volume, vwap
- timestamp, created_at
```

#### 10. **StrategyAssignment** (strategy_assignments)
```
- id, account_id (FK), strategy_id (FK)
- weight, is_active
```

---

## Frontend: Streamlit Dashboard

**Location:** `/frontend/dashboard.py`
**Port:** 8501
**Launch:** `python /frontend/run_dashboard.py`

### Dashboard Tabs (5 Views)

1. **Dashboard Tab**
   - Portfolio metrics (total capital, 7-day P&L, invocations)
   - Portfolio value chart (Plotly line chart)
   - Recent LLM decisions display
   - Account overview table

2. **Portfolio Tab**
   - Time period selector (7/30/90 days)
   - Performance metrics (current value, total return, cash, invested)
   - Portfolio value over time (Plotly interactive)
   - Daily P&L bar chart

3. **Trades Tab**
   - Trade filters (status, limit)
   - Summary metrics (total trades, win rate, P&L, open positions)
   - Trades table with styling (profit/loss colors)
   - Status tracking

4. **LLM Decisions Tab**
   - Decision history with expanders
   - Account info, execution metrics
   - Tool calls display with color coding
   - LLM response text
   - Token usage tracking

5. **System Control Tab**
   - System health, market status, trading status
   - Start/Stop trading buttons
   - System information table
   - Emergency controls

### Visualization Libraries Used
- **Plotly** - Interactive line/bar charts
- **Pandas DataFrames** - Tabular display
- **Streamlit metrics** - KPI cards
- **Custom CSS** - Styling and colors

### API Integration
```python
API_BASE_URL = "http://localhost:8000"

Key Endpoints Called:
- GET /api/system/status
- GET /api/portfolio/performance
- GET /api/invocations
- GET /api/trades
- GET /api/accounts
```

---

## API Backend: FastAPI (32 Endpoints)

**Location:** `/api/main.py`
**Port:** 8000
**Database:** PostgreSQL with SQLAlchemy ORM

### Endpoint Groups

#### Portfolio Endpoints
- `GET /api/portfolio/performance` - Performance timeseries (cached 5 min)
- `GET /api/portfolio/{account_id}` - Current portfolio for account

#### Invocations Endpoints
- `GET /api/invocations` - LLM invocation history (cached 2 min)

#### Trading Endpoints
- `GET /api/trades` - Trade history with filters
- `GET /api/trades/{trade_id}` - Detailed trade info

#### Market Data Endpoints
- `GET /api/market-data/{symbol}` - Candle data (5m, 15m, 1h, daily)
- `GET /api/market-data/{symbol}/indicators` - Technical indicators

#### System Endpoints
- `GET /api/system/status` - Health check
- `POST /api/system/start-trading` - Start trading
- `POST /api/system/stop-trading` - Stop trading

#### Account Endpoints
- `GET /api/accounts` - All trading accounts

#### Health Endpoint
- `GET /api/health` - Service health

### Caching Strategy
- Portfolio data: 5-minute cache
- Invocations: 2-minute cache
- Market data: Timeframe-dependent (5m=fresh, 1h=1hour cache)

---

## Core Trading Components

### 1. Trading Engine (`core/trading_engine.py`)

**Orchestrator pattern** - Main controller for the trading system

Key Methods:
- `initialize()` - Setup database, market data, LLM, risk manager
- `_load_initial_data()` - Load accounts, strategies, stocks
- `process_accounts()` - Main trading loop (async)
- `_process_account()` - Per-account logic
- `_get_market_context()` - Gather market data
- `_invoke_llm()` - Call LLM for decision
- `shutdown()` - Cleanup

**Execution Flow:**
1. Every 5 minutes (configurable)
2. For each active account:
   - Fetch market data for assigned stocks
   - Get portfolio state
   - Invoke LLM with context
   - Execute tool calls (buy/sell/close)
   - Record invocation and trades
   - Take portfolio snapshot

### 2. Market Data Manager (`data/enhanced_market_data_manager.py`)

Extends base `MarketDataManager` with async support

**Timeframes Supported:**
- 5m (always fresh) - Entry signals
- 15m (15 min cache) - Trend context
- 1h (1 hour cache) - Longer-term view
- Daily (24 hour cache) - Context

**Data Structure:**
```python
{
    "timestamp": [unix_timestamps...],
    "open": [prices...],
    "high": [prices...],
    "low": [prices...],
    "close": [prices...],
    "volume": [volumes...],
    "vwap": [vwap_values...]  # Pre-calculated
}
```

**Cache Durations:**
- 5m: Always refresh
- 15m: 15 minutes
- 1h: 60 minutes
- Daily: 24 hours

### 3. LLM Manager (`core/llm_manager.py`)

Handles integration with multiple LLM providers

**Supported Models:**
- Claude 3.5 Sonnet (Anthropic)
- GPT-4 Turbo (OpenAI via OpenRouter)

**Prompt Structure:**
- Market context (5m, 15m, 1h, daily data)
- Technical indicators (VWAP, EMA, RSI)
- Portfolio state (cash, positions, P&L)
- Recent trades (last 5 trades)
- Strategy instructions

**Tools Available to LLM:**
1. `buy_stock(symbol, quantity, price)` - Open long position
2. `sell_stock(symbol, quantity, price)` - Open short position
3. `close_position(symbol, qty)` - Close existing position
4. `set_stop_loss(trade_id, price)` - Update SL
5. `set_target(trade_id, price)` - Update TP

### 4. Risk Manager (`core/risk_manager.py`)

Position sizing and risk controls

**Calculations:**
- Position size based on risk % and stop loss
- Account drawdown tracking
- Max positions enforcement
- Daily loss limits
- Risk-reward ratio validation

**Formula:**
```
Position Size = (Account Value × Risk %) / (Entry Price - Stop Loss Price)
```

### 5. Strategy Factory (`strategies/strategy_factory.py`)

Creates and manages strategy instances

**Implemented Strategies:**
- `VWAPStrategy` - Breakout/retest (LIVE - 39.74% backtest)
- `EMAStrategy` - Crossover (defined, untested)
- `RSIStrategy` - Momentum (defined, untested)

**Strategy Interface:**
```python
class BaseStrategy:
    def analyze(self, market_data: Dict) -> Dict:
        # Returns:
        # {
        #     "signal": "BUY/SELL/HOLD",
        #     "strength": 0-100,
        #     "entry_price": float,
        #     "stop_loss": float,
        #     "target": float,
        #     "reasoning": str
        # }
        pass
```

---

## Data Flow: From Market to Trade

```
1. MARKET DATA FETCH (Every 5 min)
   └─> Dhan API ──> Enhanced Market Data Manager
                     ├─ Cache 5m data (always fresh)
                     ├─ Cache 15m data
                     ├─ Cache 1h data
                     └─ Cache daily data

2. STRATEGY ANALYSIS
   └─> VWAP Calculator
       ├─ Calculate VWAP from price + volume
       ├─ Detect breakout signals
       ├─ Calculate bands (std dev)
       └─ Generate trading signals

3. LLM DECISION
   └─> LLM Manager (Claude/GPT-4)
       ├─ Receives: Market data + Portfolio + Recent trades
       ├─ Processes with technical indicators
       └─ Returns: Trading decision + Tool calls

4. TRADE EXECUTION
   └─> Tool calls executed
       ├─ Buy/Sell orders to Dhan API
       ├─ Risk management checks
       ├─ Position sizing
       └─ Stop loss/target setup

5. PERSISTENCE
   ├─> Trade record saved to DB
   ├─> Invocation logged
   ├─> Portfolio snapshot taken
   └─> Metrics calculated
```

---

## Visualization Features Available

### Current Charting (Existing)

1. **Plotly Charts in Dashboard**
   - Line chart: Portfolio value over time
   - Bar chart: Daily P&L
   - These are 2D time-series visualizations

2. **Data Tables**
   - Trades with sortable columns
   - Account overview
   - Portfolio positions

### Current Technical Data Available

From market data manager (not yet visualized):
- OHLCV data (Open, High, Low, Close, Volume)
- VWAP values (pre-calculated)
- Technical indicators: EMA, RSI, Bollinger Bands
- Multi-timeframe data (5m, 15m, 1h, daily)

---

## Configuration & Stocks

### Configured Indian Stocks (`config/settings.py`)

| Symbol | Security ID | Exchange | Strategies | Tick Size | Lot |
|--------|-----------|----------|-----------|-----------|-----|
| RELIANCE | 2885 | NSE_EQ | vwap, smc | 0.05 | 1 |
| TCS | 11536 | NSE_EQ | ema, rsi | 0.05 | 1 |
| INFY | 1594 | NSE_EQ | vwap, ema | 0.05 | 1 |
| HDFCBANK | 1333 | NSE_EQ | rsi, smc | 0.05 | 1 |
| ICICIBANK | 4963 | NSE_EQ | vwap, rsi | 0.05 | 1 |
| SBIN | 3045 | NSE_EQ | - | 0.05 | 1 |
| BHARTIARTL | 3677 | NSE_EQ | - | 0.05 | 1 |

### LLM Models Configuration

```python
MODELS = {
    "primary": {
        "name": "claude-3-5-sonnet",
        "provider": "openrouter",
        "allocation": 60%,
        "stocks": ["RELIANCE", "TCS", "INFY"]
    },
    "secondary": {
        "name": "gpt-4-turbo",
        "provider": "openrouter",
        "allocation": 40%,
        "stocks": ["HDFCBANK", "ICICIBANK"]
    }
}
```

---

## Key Files for Graph Visualization Implementation

### For Real-time Candlestick Charts
- `/data/enhanced_market_data_manager.py` - Has OHLCV data structure
- `/backtest_vwap.py` - Shows how data is structured and used

### For Trading Signals Display
- `/vwap_calculator.py` - Signal generation logic
- `/strategies/vwap_strategy.py` - Strategy analysis

### For Performance Charts (Already Have)
- `/frontend/dashboard.py` - Uses Plotly for existing charts
- `/api/main.py` - Portfolio performance endpoint

### For Technical Analysis
- `/core/trading_engine.py` - Has market context building
- `config/settings.py` - Strategy parameters

### Database Access
- `/models/database.py` - All table definitions
- `/api/main.py` - Example queries for API

---

## Docker Deployment

**Containers:**
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI app (port 8000)

**Environment Variables Needed:**
```bash
DHAN_CLIENT_ID=your_client_id
DHAN_ACCESS_TOKEN=your_access_token
OPENROUTER_API_KEY=your_api_key
DATABASE_URL=postgresql://username:password@postgres:5432/ai_trading
REDIS_URL=redis://redis:6379/0
```

**Launch:**
```bash
docker-compose up --build
```

---

## Data Sources Summary

1. **Real-time Market Data**
   - Source: Dhan API
   - Timeframes: 5m, 15m, 1h, daily
   - Symbols: 5 configured + easily expandable
   - Fields: OHLCV + calculated VWAP

2. **Trading Data**
   - Source: Database (trades, invocations, signals)
   - Updated: Real-time as trades execute
   - History: Full persistence since launch

3. **Portfolio Data**
   - Source: Database snapshots
   - Frequency: Every market event + periodic
   - Includes: Value, cash, positions, P&L

4. **Technical Indicators**
   - VWAP: Calculated from price × volume
   - EMA: Exponential moving averages
   - RSI: Relative strength index
   - Bollinger Bands: Price deviation bands

---

## Summary for Graph Visualization Feature

**Current State:**
- Basic line/bar charts for portfolio performance
- No candlestick charts
- No technical indicator overlays
- No signal markers
- No real-time market depth

**Available Data to Visualize:**
- Candlestick charts (OHLCV data ready)
- VWAP overlay on candles
- Buy/Sell signal markers
- Technical indicators (EMA, RSI, BB)
- Portfolio value progression
- Trade entry/exit points
- P&L timeline

**Data Flow Ready:**
- Market data fetching: READY (5m, 15m, 1h, daily)
- Technical calculations: READY (VWAP, EMA, RSI)
- Database schema: READY (all data persisted)
- API endpoints: PARTIALLY READY (market data endpoint needs implementation)

**Recommended Charting Libraries:**
- Plotly (already in use - supports candlesticks)
- Lightweight Charts (TradingView charting library)
- Apache ECharts (open source, rich features)

