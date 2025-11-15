# Graph Visualization Feature - Quick Reference

## Quick Summary

You're building a **trading graph visualization feature** for an **AI-powered Indian stock trading system**.

### Current State
- **Frontend**: Streamlit (Python) at port 8501
- **Backend**: FastAPI at port 8000
- **Current Charts**: Basic line/bar charts with Plotly
- **Missing**: Candlestick charts, technical indicator overlays, real-time updates

---

## Key Data Sources for Visualization

### 1. Real-time Price Data
```
Endpoint: GET /api/market-data/{symbol}?timeframe=5m&limit=100
Response: OHLCV data (Open, High, Low, Close, Volume)
Use for: Candlestick charts, price action analysis
```

### 2. Technical Indicators
```
Source: VWAPCalculator class
Data: VWAP, VWAP bands (standard deviation)
Available: Through /api/market-data/{symbol}/indicators
Integration: Already calculated, just needs visualization
```

### 3. Portfolio Performance
```
Endpoint: GET /api/portfolio/performance?days=30
Response: Timeseries of portfolio value
Fields: total_value, available_cash, invested_amount, day_pnl, return_percentage
Refresh: Every 5 minutes (cached)
```

### 4. Trading History
```
Endpoint: GET /api/trades?limit=100
Response: Historical trades with entry/exit prices
Fields: entry_price, exit_price, net_pnl, executed_at, closed_at, status
Use for: Trade execution marks on charts, P&L analysis
```

---

## Frontend Code Locations

### Charts Currently in `frontend/dashboard.py`

**Line 223-241**: Portfolio Value Chart
```python
fig = px.line(df, x='timestamp', y='total_value', title="Portfolio Value")
```

**Line 315-332**: Alternative with go.Scatter()
```python
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['total_value']))
```

**Line 339-347**: Daily P&L Bar Chart
```python
fig_pnl = px.bar(df, x='timestamp', y='day_pnl', color='day_pnl')
```

### Where to Add New Visualizations
- **New page**: Add to navigation menu (line 134-146)
- **New chart function**: Create `show_market_analysis()` function
- **New endpoint call**: Use `dashboard.make_api_request()` pattern

---

## Implementation Checklist

### Phase 1: Candlestick Charts (1-2 hours)
- [ ] Create market data endpoint integration
- [ ] Fetch OHLCV data for selected symbol
- [ ] Render candlestick chart using `go.Candlestick()`
- [ ] Add VWAP overlay as line
- [ ] Add volume subplot below

### Phase 2: Technical Indicators (1-2 hours)
- [ ] Get VWAP bands from VWAPCalculator
- [ ] Add Bollinger Bands (TA-Lib already installed)
- [ ] Plot on secondary y-axis
- [ ] Add moving averages (5, 20, 50 period)
- [ ] Color code based on trend

### Phase 3: Trade Analytics (2-3 hours)
- [ ] Fetch historical trades
- [ ] Plot entry/exit points on chart
- [ ] Color: Green (winning), Red (losing)
- [ ] Add trade statistics (win rate, avg P&L)
- [ ] Show equity curve with drawdown

### Phase 4: Real-time Updates (3-4 hours)
- [ ] Implement WebSocket or faster polling
- [ ] Use Streamlit session_state for caching
- [ ] Reduce refresh interval to 1-5 seconds
- [ ] Add live market ticker
- [ ] Update title with current price

---

## Code Examples

### Add Candlestick Chart
```python
import plotly.graph_objects as go

# In api/main.py, enhance market-data endpoint:
@app.get("/api/market-data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "5m"):
    data = EnhancedMarketDataManager.get_timeframe_data(symbol, timeframe)
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "ohlcv": {
            "timestamp": data['timestamp'],
            "open": data['open'],
            "high": data['high'],
            "low": data['low'],
            "close": data['close'],
            "volume": data['volume']
        }
    }

# In frontend/dashboard.py:
def show_price_chart(dashboard, symbol="RELIANCE"):
    # Fetch data
    market_data = dashboard.make_api_request(f"/api/market-data/{symbol}?timeframe=5m")
    
    if not market_data:
        st.error("No market data available")
        return
    
    ohlcv = market_data['ohlcv']
    
    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=ohlcv['timestamp'],
        open=ohlcv['open'],
        high=ohlcv['high'],
        low=ohlcv['low'],
        close=ohlcv['close']
    )])
    
    # Add VWAP overlay
    # TODO: Fetch VWAP data
    
    fig.update_layout(
        title=f"{symbol} - 5 Minute Chart",
        yaxis_title="Price (₹)",
        xaxis_title="Time",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

### Add VWAP Overlay
```python
# Fetch VWAP data (already calculated)
vwap_data = VWAPCalculator.calculate_vwap(market_data)

# Add to chart
fig.add_trace(go.Scatter(
    x=ohlcv['timestamp'],
    y=vwap_data,
    mode='lines',
    name='VWAP',
    line=dict(color='blue', width=2)
))
```

### Add Volume Subplot
```python
from plotly.subplots import make_subplots

# Create subplots
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    row_heights=[0.7, 0.3]
)

# Candlesticks on row 1
fig.add_trace(go.Candlestick(...), row=1, col=1)

# Volume bars on row 2
fig.add_trace(go.Bar(
    x=ohlcv['timestamp'],
    y=ohlcv['volume'],
    name='Volume'
), row=2, col=1)

fig.update_yaxes(title_text="Price (₹)", row=1)
fig.update_yaxes(title_text="Volume", row=2)
```

---

## Database Structure for Reference

### PortfolioSnapshot Table
```
- id: UUID
- account_id: String
- total_value: Decimal
- available_cash: Decimal
- invested_amount: Decimal
- day_pnl: Decimal
- total_pnl: Decimal
- return_percentage: Decimal
- positions: JSON array
- created_at: DateTime
```

### Trade Table
```
- id: UUID
- account_id: String
- stock_id: String
- strategy_id: String
- side: String (BUY/SELL)
- quantity: Integer
- entry_price: Decimal
- exit_price: Decimal
- net_pnl: Decimal
- status: String (OPEN/CLOSED/CANCELLED)
- executed_at: DateTime
- closed_at: DateTime
```

### TradingSignal Table
```
- id: UUID
- stock_id: String
- strategy_id: String
- signal_type: String (BREAKOUT, RETEST, etc.)
- strength: Decimal (0-1)
- confidence: Decimal (0-1)
- price: Decimal
- reasoning: Text
- created_at: DateTime
```

---

## Testing Your Visualization

### Manual Testing
```bash
# Start backend
python /path/to/main.py

# Start frontend
streamlit run /path/to/frontend/dashboard.py

# Check data flow
curl http://localhost:8000/api/market-data/RELIANCE?timeframe=5m
curl http://localhost:8000/api/portfolio/performance?days=7
```

### Using Postman/Insomnia
1. Test `/api/market-data/RELIANCE` endpoint
2. Verify OHLCV data structure
3. Test `/api/trades` with filters
4. Check portfolio/performance response

---

## Performance Considerations

### Data Fetching
- Cache: 5-min for portfolio, 2-min for invocations
- Limit API calls: Use pagination (limit parameter)
- Background jobs: Use Celery for long-running tasks

### Chart Rendering
- Limit candles: Max 500-1000 for performance
- Use `scattergl` instead of `scatter` for >5000 points
- Downsample data for slower networks

### Update Frequency
- Portfolio: 30 seconds (current)
- Trades: 10 seconds (can be faster)
- Market data: 1-5 seconds for live trading

---

## Libraries Already Available

✅ **Plotly** - Interactive charts
✅ **Pandas** - Data manipulation
✅ **NumPy** - Array operations
✅ **TA-Lib** - Technical indicators
✅ **SQLAlchemy** - Database ORM
✅ **Streamlit** - UI framework

❌ **Not included** (but can add):
- `plotly-resampler` - Fast aggregation for big data
- `streamlit-plotly-events` - Click events on charts
- `websocket` - Real-time updates
- `dash` - Alternative to Streamlit (more customizable)

---

## Useful API Endpoints

### Get 5-minute candlestick data
```
GET /api/market-data/RELIANCE?timeframe=5m&limit=100
```

### Get portfolio performance
```
GET /api/portfolio/performance?days=30
```

### Get recent trades
```
GET /api/trades?limit=50&status=CLOSED
```

### Get technical indicators
```
GET /api/market-data/RELIANCE/indicators
```

### Get system status
```
GET /api/system/status
```

---

## Deployment

### Docker Setup (Already Available)
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Backend: `localhost:8000`
- Frontend: `localhost:8501`

### Docker Commands
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Access database
docker-compose exec postgres psql -U username -d ai_trading
```

---

## Next Steps for Implementation

1. **API Enhancement**: Integrate real market data into `/api/market-data/` endpoints
2. **Frontend Component**: Create `show_market_analysis()` function with candlestick chart
3. **Data Pipeline**: Ensure PortfolioSnapshot and Trade tables are being updated
4. **Testing**: Verify data flow from API → Frontend
5. **Styling**: Match existing dashboard theme (dark mode, color scheme)
6. **Performance**: Monitor CPU/memory with large datasets

---

## Troubleshooting

### Chart Not Rendering
- Check browser console (F12) for errors
- Verify API endpoint returns valid JSON
- Ensure Plotly is in requirements.txt

### Data Not Loading
- Check backend logs: `docker-compose logs app`
- Verify database connection
- Test API endpoint directly with curl

### Performance Issues
- Reduce number of candles/data points
- Increase cache duration
- Use `scattergl` for large datasets
- Profile with `streamlit run --logger.level=debug`

---

## Resources

- **Plotly Documentation**: https://plotly.com/python/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **TA-Lib Documentation**: https://github.com/mrjbq7/ta-lib
- **Dhan API Docs**: https://dhanhq.co/docs/

---

**File**: `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/VISUALIZATION_QUICK_REFERENCE.md`

Last Updated: November 2025
