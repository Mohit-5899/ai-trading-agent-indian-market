# AI Trading Agent - Codebase Structure & Visualization Implementation Guide

## 1. Overall Project Structure & Technology Stack

### Architecture Overview
```
ai-trading-agent-indian-market/
├── Backend (FastAPI)
│   ├── API endpoints for trading data
│   ├── Database layer (PostgreSQL/SQLAlchemy)
│   └── Trading engine & LLM integration
├── Frontend (Streamlit)
│   ├── Dashboard for monitoring
│   ├── Portfolio visualization
│   └── Real-time trading controls
├── Data Management
│   ├── Market data fetching (Dhan API)
│   ├── VWAP calculation
│   └── Technical indicators
└── Strategies
    └── VWAP Breakout/Retest Strategy
```

### Technology Stack

#### Backend & Core
- **Framework**: FastAPI 0.104.1 (async Python web framework)
- **Server**: Uvicorn 0.24.0 (ASGI server)
- **Database**: PostgreSQL + SQLAlchemy 2.0.23 (ORM)
- **Port**: 8000

#### Frontend
- **Framework**: Streamlit 1.28.1 (Python-based interactive dashboard)
- **Port**: 8501
- **Charting Library**: Plotly 5.17.0 (interactive plots)
- **Data Handling**: Pandas 2.1.3, NumPy 1.25.2

#### Data & Trading
- **Market Data API**: Dhan API (Indian stock market)
- **Technical Analysis**: TA-Lib 0.4.32, custom VWAP calculator
- **Backtesting**: Custom VWAPBacktester class

#### LLM & AI
- **LLM Integration**: 
  - OpenAI 1.6.1
  - Anthropic 0.7.8
  - OpenRouter API support
- **Data Format**: Custom TOON format (Token-Oriented Object Notation - 84% token savings)

#### Infrastructure
- **Caching**: Redis 7-alpine
- **Background Tasks**: Celery 5.3.4 (Redis broker)
- **Task Scheduling**: APScheduler 3.10.4
- **Containerization**: Docker + Docker Compose

---

## 2. Existing Visualization & Graphing Libraries

### Currently Used
1. **Plotly 5.17.0** - Main charting library for interactive visualizations
   - Used in: `frontend/dashboard.py`
   - Capabilities:
     - Line charts (portfolio value over time)
     - Bar charts (daily P&L)
     - Scatter plots
     - Real-time hover information
   - CSS styling support
   - Responsive design

2. **Streamlit Native Components**
   - Metrics display
   - Tables (dataframes with styling)
   - Expanders for collapsible content
   - Columns for layout management

3. **Altair 5.1.2** - Declarative visualization (optional)

### Missing/Opportunity Gaps
- No candlestick charts (essential for trading)
- No technical indicator overlays (VWAP, moving averages)
- No real-time WebSocket updates for live charts
- No multi-timeframe synchronized displays
- Limited order book/depth visualization
- No heatmaps for market analysis
- No animated charts

---

## 3. Main Application/Frontend Code Location

### Frontend Directory Structure
```
frontend/
├── dashboard.py          # Main Streamlit app (20KB, 589 lines)
├── run_dashboard.py      # Launch script
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

### Key Frontend Files

#### `dashboard.py` - Main Application
- **Class**: `TradingDashboard`
- **Features**:
  - Navigation menu with 5 pages
  - Auto-refresh every 30 seconds
  - Real-time system status
  - API request handler with error handling
  - Custom CSS styling

#### Pages Available
1. **Dashboard** - Overview with 7-day performance
2. **Portfolio** - Detailed performance with multiple timeframes
3. **Trades** - Trading history with filters
4. **LLM Decisions** - AI decision tracking
5. **System Control** - Start/stop trading, emergency controls

### Frontend API Integration
- **Base URL**: `http://localhost:8000`
- **CORS**: Allows `localhost:3000`, `localhost:3001`
- **Connection Method**: REST API via `requests` library

---

## 4. Existing Code for Displaying Trading Data or Charts

### Current Chart Implementation in `dashboard.py`

#### Portfolio Performance Chart (Lines 223-241)
```python
fig = px.line(
    df, 
    x='timestamp', 
    y='total_value',
    title="Portfolio Value Over Time"
)
```
- **Data Source**: `/api/portfolio/performance`
- **Timeframes**: 7, 30, 90 days selectable
- **Metrics**: Total value, available cash, invested amount

#### Daily P&L Chart (Lines 336-348)
```python
fig_pnl = px.bar(
    df,
    x='timestamp',
    y='day_pnl',
    title="Daily Profit & Loss",
    color='day_pnl',
    color_continuous_scale=['red', 'gray', 'green']
)
```
- **Color Coding**: Red (loss), Gray (neutral), Green (profit)

#### Trades Table (Lines 350-429)
- Displays: Timestamp, account, symbol, strategy, side, quantity, entry price, P&L, status
- Filtering by: Status (OPEN, CLOSED, CANCELLED)
- Styling: Color-coded P&L (green for profit, red for loss)

### Data Display Components

#### Account Metrics (Lines 195-218)
- Columns: Total capital, active accounts, 7-day P&L, total invocations
- Real-time metric display

#### LLM Decisions (Lines 245-257)
- Shows: Account name, timestamp, tool call count
- Expandable for detailed view

#### System Status Sidebar (Lines 148-166)
- System health indicator
- Active accounts count
- Trading count
- Market open/close status
- Trading enabled/disabled status

---

## 5. Data Sources Available

### API Endpoints (`api/main.py`)

#### Portfolio Data
- `GET /api/portfolio/performance` - Timeseries portfolio value
  - Returns: List of snapshots with timestamps
  - Cache: 5 minutes
  - Includes: total_value, available_cash, invested_amount, day_pnl, total_pnl, return_percentage, positions_count

- `GET /api/portfolio/{account_id}` - Current portfolio
  - Latest snapshot + open trades count
  - Positions data in JSON format

#### Trading Data
- `GET /api/trades` - Trade history with filtering
  - Filters: account_id, status (OPEN/CLOSED/CANCELLED), limit
  - Returns: Trade details including entry/exit prices, P&L, execution time

- `GET /api/trades/{trade_id}` - Specific trade details
  - Includes: stock details, strategy details, entry/exit analysis

#### Market Data (Placeholder)
- `GET /api/market-data/{symbol}` - OHLCV data
- `GET /api/market-data/{symbol}/indicators` - Technical indicators
  - Currently returns mock data but structured for integration

#### LLM Invocations
- `GET /api/invocations` - Recent LLM decisions
  - Cache: 2 minutes
  - Includes: tool calls, execution time, tokens used, reasoning

#### System Data
- `GET /api/system/status` - System health
  - Returns: Status, active accounts, today's trades, market open, trading enabled
  - Checks: Database connection, last invocation time

- `GET /api/accounts` - Trading accounts
  - Returns: Active accounts with allocation details

### Database Models (`models/database.py`)

#### PortfolioSnapshot
- Fields: account_id, total_value, available_cash, invested_amount, day_pnl, total_pnl, return_percentage, positions (JSON), created_at
- Updated: Regularly to track portfolio history

#### Trade
- Fields: account_id, stock_id, strategy_id, side, quantity, entry_price, exit_price, net_pnl, status, executed_at, closed_at
- Related: Account, Stock, Strategy

#### Invocation (LLM)
- Fields: account_id, llm_response, execution_time_ms, tokens_used, created_at
- Related: Tool calls (ToolCall model)

#### Stock
- Fields: symbol, name, security_id, exchange
- Stores: Stock/symbol reference data

#### TradingSignal
- Fields: stock_id, strategy_id, signal_type, strength, confidence, price, reasoning, created_at
- Logs: All generated trading signals

### Market Data Manager

#### EnhancedMarketDataManager (`data/enhanced_market_data_manager.py`)
- **Methods**:
  - `get_timeframe_data(symbol, timeframe)` - 5m, 15m, 1h, daily
  - `get_current_price(symbol)` - Latest 5-minute close
  - `get_all_timeframes(symbol)` - Concurrent fetch all timeframes
  - `get_multiple_symbols_data(symbols, timeframes)` - Bulk data fetch
  - `format_for_llm(data, format_type)` - TOON or detailed format
  - `get_cache_status()` - Cache information
  - `warm_cache()` - Pre-load cache

#### Supported Timeframes & Cache
- **5-minute**: Always fresh (price action)
- **15-minute**: 15-min cache
- **Hourly**: 60-min cache
- **Daily**: Entire day cache

### VWAP Calculator Data (`vwap_calculator.py`)

#### Available Data
- Candle data: OHLCV (Open, High, Low, Close, Volume)
- Calculated: VWAP, VWAP bands, typical price
- Signals: Breakout, retest detection
- Position sizing based on risk parameters

### Historical Data Source

#### VWAPBacktester (`backtest_vwap.py`)
- **Data Fetcher**: Dhan API intraday_minute_data
- **Coverage**: 90 days of 5-minute candles
- **Format**: Dictionary with arrays: timestamp, open, high, low, close, volume
- **Aggregation**: Splits data by trading day for strategy evaluation

---

## 6. Framework Being Used

### Frontend Framework: Streamlit

#### Why Streamlit?
- **Python-native**: Full Python for both backend and frontend
- **Reactive**: Auto-refreshes on state changes
- **Built-in components**: Charts, tables, metrics, forms
- **Fast deployment**: No JavaScript/React needed
- **Dashboard-friendly**: Purpose-built for dashboards

#### Streamlit Architecture
1. **Script-based**: Reruns on every interaction
2. **State management**: `st.session_state` for persistent data
3. **Component system**: Pre-built widgets (buttons, sliders, selectors)
4. **Theming**: CSS customization via `st.markdown(unsafe_allow_html=True)`

#### Not using React/Vue
- The project uses **Streamlit for simplicity**
- No separate frontend build process
- All logic in Python
- Real-time data binding via FastAPI

---

## 7. Comprehensive Structure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   USER BROWSER (8501)                      │
│                    Streamlit Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Navigation Menu                                            │
│  ├─ Dashboard (Overview)                                    │
│  ├─ Portfolio (Performance Charts)                          │
│  ├─ Trades (Trading History)                                │
│  ├─ LLM Decisions (AI Reasoning)                            │
│  └─ System Control (Trading Controls)                       │
│                                                             │
│  Current Visualizations:                                    │
│  ├─ Plotly Line Chart (Portfolio Value)                     │
│  ├─ Plotly Bar Chart (Daily P&L)                            │
│  ├─ Pandas Dataframe Tables                                 │
│  └─ Streamlit Metrics Widgets                               │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON (requests library)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend (8000)                     │
│                  api/main.py                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  REST Endpoints:                                            │
│  ├─ /api/portfolio/performance          (Cache: 5 min)     │
│  ├─ /api/portfolio/{account_id}         (Latest snapshot)  │
│  ├─ /api/trades                         (Trade history)    │
│  ├─ /api/trades/{trade_id}              (Trade details)    │
│  ├─ /api/invocations                    (Cache: 2 min)     │
│  ├─ /api/system/status                  (Health check)     │
│  ├─ /api/accounts                       (Account list)     │
│  ├─ /api/market-data/{symbol}           (OHLCV data)       │
│  └─ /api/market-data/{symbol}/indicators (Tech indicators) │
│                                                             │
│  Core Components:                                           │
│  ├─ Database session management                            │
│  ├─ Caching layer (memory-based)                           │
│  ├─ Error handling & logging                               │
│  └─ Market hours detection                                 │
│                                                             │
└──────────────────┬─────────────────────┬───────────────────┘
                   │                     │
                   │                     │
         ┌─────────▼─────────┐  ┌──────▼──────────┐
         │  PostgreSQL (5432)│  │  Redis (6379)  │
         │                   │  │                │
         │  Tables:          │  │  Cache:        │
         │  - trades         │  │  - Performance │
         │  - accounts       │  │  - Invocations │
         │  - invocations    │  │  - Session     │
         │  - strategies     │  │  - Queue tasks │
         │  - signals        │  │                │
         │  - portfolio_snap │  │                │
         │  - stocks         │  │                │
         │                   │  │                │
         └───────────────────┘  └────────────────┘
                   ▲
                   │
        ┌──────────┴──────────┐
        │   Data Pipeline     │
        ├─────────────────────┤
        │                     │
        │ MarketDataManager   │
        │ ├─ Dhan API Client  │
        │ ├─ VWAP Calculator  │
        │ └─ Indicators       │
        │                     │
        │ VWAPBacktester      │
        │ (Backtesting)       │
        │                     │
        │ TradingEngine       │
        │ (Execution)         │
        │                     │
        └─────────────────────┘
```

---

## 8. Data Flow for Visualization

### Real-time Portfolio Chart
```
Streamlit (every 30s)
    ↓
requests.get("/api/portfolio/performance?days=30")
    ↓
FastAPI endpoint
    ↓
Check cache (5-min TTL)
    ↓
Database query (PortfolioSnapshot table)
    ↓
JSON response with timestamps and values
    ↓
Pandas DataFrame conversion
    ↓
Plotly line chart render
```

### Trading Data Display
```
Streamlit (on user interaction)
    ↓
requests.get("/api/trades?limit=50&status=CLOSED")
    ↓
FastAPI endpoint
    ↓
Database query joins (Trade + Stock + Strategy + Account)
    ↓
JSON response with enriched trade details
    ↓
Pandas DataFrame with styling
    ↓
Streamlit dataframe table display
```

---

## 9. Available Data for Graph Visualization

### Candle/OHLCV Data
- Source: `EnhancedMarketDataManager` → Dhan API
- Structure: Lists of open, high, low, close, volume, timestamp
- Format: Dictionary with arrays
- Timeframes: 5m, 15m, 1h, daily
- Latest: 100-1000 candles per timeframe

### Technical Indicators
- VWAP: From `VWAPCalculator` (cumulative calculation)
- VWAP Bands: Standard deviation bands around VWAP
- Potential: RSI, Moving Averages, Bollinger Bands (TA-Lib available)

### Trade Data
- Entry/Exit Prices
- Entry/Exit Times
- Quantity
- P&L
- Status (OPEN/CLOSED)

### Portfolio Metrics
- Total Value (timeseries)
- Available Cash
- Invested Amount
- Daily P&L
- Return Percentage
- Position Count

### Signal Data
- Signal Type (Breakout, Retest, etc.)
- Signal Strength (0-1)
- Confidence (0-1)
- Price at signal
- Timestamp
- Related stock and strategy

---

## 10. Integration Points for Graph Visualization

### API Integration Ready
All endpoints support JSON data needed for:
- Candlestick charts
- Moving averages and technical indicator overlays
- Real-time price tickers
- Portfolio equity curves
- P&L distributions
- Trade analytics

### Database Ready
PortfolioSnapshot and Trade tables have:
- Timestamped entries (every update)
- Complete OHLCV data
- Multiple accounts support
- Strategy association

### Frontend Ready
Streamlit + Plotly already installed and used:
- Just need candlestick chart library (plotly supports this)
- Additional indicator overlays (Plotly secondary y-axis)
- Animation support (Plotly frame-based)

---

## 11. Recommendations for Implementing Graph Visualization

### Short-term (Quick wins)
1. **Candlestick Charts** 
   - Use: `go.Candlestick()` from Plotly
   - Data source: `/api/market-data/{symbol}`
   - Add VWAP overlay on same chart

2. **Technical Indicator Overlays**
   - VWAP: Already calculated in VWAPCalculator
   - Bollinger Bands: From TA-Lib
   - Use secondary y-axis for volume

3. **Enhanced P&L Visualization**
   - Equity curve with drawdown bands
   - Win/loss scatter plot overlay
   - Trade execution markers on price chart

### Medium-term (Higher complexity)
1. **Real-time Updates**
   - WebSocket connection instead of HTTP polling
   - Streamlit session_state for live data caching
   - Reduce refresh interval to 1-5 seconds

2. **Multi-timeframe Synchronized Charts**
   - Higher timeframe as context
   - Current timeframe for entry points
   - Linked crosshair for time sync

3. **Order Book & Depth Charts**
   - Area chart for buy/sell pressure
   - Real-time depth changes
   - Volume profile

### Long-term (Architecture changes)
1. **Alternative Frontend** 
   - React with Recharts or Chart.js
   - Real-time WebSocket support
   - Mobile responsive design

2. **Advanced Analytics**
   - Heatmaps for timeframe analysis
   - 3D surface plots for strategy parameters
   - Machine learning predictions overlay

---

## 12. File Paths for Implementation

### Key Files to Modify/Reference

**Frontend:**
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/frontend/dashboard.py` (Lines 223-348 for charts)
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/frontend/requirements.txt` (Add charting libraries)

**Backend:**
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/api/main.py` (Lines 349-388 for market data endpoints)
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/data/enhanced_market_data_manager.py` (Data fetching)
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/vwap_calculator.py` (Indicator calculations)

**Data Models:**
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/models/database.py` (Data structure reference)

**Testing/Examples:**
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/backtest_vwap.py` (Data format examples)

---

## Summary

This is a complete **Python-based AI trading system** with:
- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: Streamlit with Plotly
- **Data**: Dhan API for Indian stocks + VWAP/TA-Lib indicators
- **Infrastructure**: Docker containerized with Docker Compose
- **LLM Integration**: Multiple LLMs via OpenRouter API

The codebase is **well-structured for visualization enhancements**. All necessary data is available through APIs, Plotly is already integrated, and the architecture supports adding candlestick charts, technical indicator overlays, and real-time updates without major refactoring.
