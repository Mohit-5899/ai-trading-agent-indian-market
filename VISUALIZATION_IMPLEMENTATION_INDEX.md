# Graph Visualization Feature - Implementation Index

## Overview

This is a complete codebase exploration guide for implementing trading graph visualization features in the AI Trading Agent system. Three comprehensive documents have been created to support implementation.

---

## Documentation Files

### 1. CODEBASE_STRUCTURE_FOR_VISUALIZATION.md (20 KB)

**Most Comprehensive Guide - Start Here First**

This is the primary reference document covering everything about the codebase structure.

**Contents:**
1. Overall project structure and technology stack
2. Existing visualization and graphing libraries
3. Main application/frontend code locations
4. Existing code for displaying trading data
5. Data sources available (5 detailed subsections)
6. Framework being used (Streamlit)
7. Comprehensive architecture diagram
8. Data flow examples
9. Available data for visualization
10. Integration points for graph visualization
11. Implementation recommendations (short, medium, long term)
12. File paths for implementation

**Best For:**
- Understanding the complete system architecture
- Finding all relevant code locations
- Learning about available data sources
- Planning implementation strategy

**Key Sections:**
- Lines 1-130: Technology stack breakdown
- Lines 131-220: Current vs missing visualizations
- Lines 221-350: Frontend structure details
- Lines 351-550: Backend endpoints documentation
- Lines 551-750: Database models and data schema
- Lines 751-900: Market data manager and data sources
- Lines 901-1100: Implementation recommendations and roadmap

---

### 2. VISUALIZATION_QUICK_REFERENCE.md (10 KB)

**Developer-Focused Quick Start Guide**

Concise reference for developers implementing features. Less explanatory, more actionable.

**Contents:**
1. Quick summary of current state
2. Key data sources for visualization (with endpoints)
3. Frontend code locations
4. Implementation checklist (4 phases)
5. Code examples (ready to use)
6. Database structure reference
7. Testing guide
8. Performance considerations
9. Available libraries checklist
10. Useful API endpoints
11. Docker deployment setup
12. Troubleshooting guide

**Best For:**
- Quick lookup of endpoints
- Code examples to copy/paste
- Implementation checklists
- Testing procedures
- Troubleshooting issues

**Code Examples Included:**
- Candlestick chart implementation
- VWAP overlay addition
- Volume subplot creation
- Market data endpoint enhancement

**Useful Checklists:**
- Phase 1: Candlestick Charts (1-2 hours)
- Phase 2: Technical Indicators (1-2 hours)
- Phase 3: Trade Analytics (2-3 hours)
- Phase 4: Real-time Updates (3-4 hours)

---

### 3. ARCHITECTURE_DIAGRAM.txt (25 KB)

**Visual System Architecture and Data Flow**

ASCII diagrams and visual representation of the system architecture.

**Contents:**
1. Overall architecture diagram with layers
2. Component relationships and data flow
3. Frontend layer details
4. Backend layer endpoints
5. Database and cache infrastructure
6. External data sources
7. Data flow for specific visualization examples
8. Key files for implementation (organized by function)
9. Development workflow steps
10. Quick fact sheet (all important info)

**Best For:**
- Visual learners
- Understanding system relationships
- Identifying data sources
- Planning implementation order
- Finding the right files to modify

**Visual Elements:**
- ASCII box diagrams of layers
- Data flow visualization
- Component relationship diagram
- File structure trees
- Development workflow chart

---

## Quick Navigation

### Finding Specific Information

**Q: Where is the frontend code?**
→ CODEBASE_STRUCTURE_FOR_VISUALIZATION.md Section 3
→ VISUALIZATION_QUICK_REFERENCE.md "Frontend Code Locations"
→ ARCHITECTURE_DIAGRAM.txt File paths section

**Q: What data can I visualize?**
→ CODEBASE_STRUCTURE_FOR_VISUALIZATION.md Section 5
→ VISUALIZATION_QUICK_REFERENCE.md "Key Data Sources"
→ ARCHITECTURE_DIAGRAM.txt Data sources section

**Q: How do I add a candlestick chart?**
→ VISUALIZATION_QUICK_REFERENCE.md "Code Examples"
→ Copy/paste code and adapt to your needs

**Q: What libraries are available?**
→ CODEBASE_STRUCTURE_FOR_VISUALIZATION.md Section 2
→ VISUALIZATION_QUICK_REFERENCE.md "Libraries Already Available"

**Q: What are the API endpoints?**
→ CODEBASE_STRUCTURE_FOR_VISUALIZATION.md Section 5
→ VISUALIZATION_QUICK_REFERENCE.md "Useful API Endpoints"
→ ARCHITECTURE_DIAGRAM.txt Backend layer section

**Q: How do I test my implementation?**
→ VISUALIZATION_QUICK_REFERENCE.md "Testing Your Visualization"
→ Includes manual testing and Postman/Insomnia instructions

---

## Implementation Roadmap

### Phase 1: Foundation (1-2 hours)
- Enhance `/api/main.py` endpoints (lines 349-388)
- Integrate `EnhancedMarketDataManager.get_timeframe_data()`
- Return OHLCV + technical indicators

**Files to modify:**
- `/api/main.py` (market data endpoints)
- `/api/schemas.py` (add response schemas if needed)

### Phase 2: Frontend Candlestick Chart (1-2 hours)
- Create `show_market_analysis()` function
- Use `go.Candlestick()` from Plotly
- Add VWAP overlay
- Add volume subplot

**Files to modify:**
- `/frontend/dashboard.py` (add new visualization function)

### Phase 3: Technical Indicators (1-2 hours)
- Get VWAP bands from `VWAPCalculator`
- Add Bollinger Bands (TA-Lib)
- Moving averages (5, 20, 50 period)

**Files to modify:**
- `/frontend/dashboard.py` (add indicators to chart)

### Phase 4: Trading Analytics (2-3 hours)
- Plot entry/exit points on chart
- Color-code by profit/loss
- Add trade statistics

**Files to modify:**
- `/frontend/dashboard.py` (integrate trade data)
- `/api/main.py` (if needed, enhance trade endpoints)

### Phase 5: Real-time Updates (3-4 hours)
- Implement WebSocket or faster polling
- Use Streamlit `session_state`
- Live price ticker

**Files to modify:**
- `/frontend/dashboard.py` (update refresh logic)
- `/api/main.py` (add WebSocket endpoint if desired)

---

## Key Data Points

### Technology Stack
```
Frontend:  Streamlit 1.28.1 + Plotly 5.17.0
Backend:   FastAPI 0.104.1 + PostgreSQL + Redis
Data:      Dhan API (Indian stocks) + TA-Lib 0.4.32
Deploy:    Docker + Docker Compose
```

### Ports
```
Frontend:  8501 (Streamlit)
Backend:   8000 (FastAPI)
Database:  5432 (PostgreSQL)
Cache:     6379 (Redis)
```

### Current Performance
```
VWAP Strategy: 39.74% return (90 days)
Win Rate: 51.8%
Profit Factor: 1.44
Max Drawdown: 10.07%
```

### Trading Hours
```
NSE Market: 09:15 - 15:30 IST
Strategy: 5-minute candles
Risk: 2% per trade
Reward/Risk: 1:3 ratio
```

---

## Critical File Locations

### Frontend
- `/frontend/dashboard.py` (main app, 589 lines)
  - Lines 223-241: Portfolio chart example
  - Lines 315-332: Alternative chart syntax
  - Lines 339-347: P&L bar chart
  - **Add new charts after line 587**

### Backend APIs
- `/api/main.py` (FastAPI app, 532 lines)
  - Lines 67-127: Portfolio endpoints
  - Lines 168-246: Invocation endpoints
  - Lines 250-296: Trade endpoints
  - **Lines 349-388: Market data (ENHANCE)**
  - Lines 392-432: System endpoints

### Data Sources
- `/data/enhanced_market_data_manager.py` (data fetching)
  - `get_timeframe_data()` - fetches OHLCV
  - `get_all_timeframes()` - concurrent fetch
  - `get_multiple_symbols_data()` - bulk fetch

### Indicators
- `/vwap_calculator.py` (VWAP calculation)
  - `calculate_vwap()` - VWAP values
  - `calculate_vwap_bands()` - bands

### Database
- `/models/database.py` (data models)
  - `PortfolioSnapshot` - portfolio history
  - `Trade` - executed trades
  - `TradingSignal` - trading signals

---

## Testing Strategy

### 1. Manual Testing
```bash
# Start backend
python /path/to/main.py

# Start frontend  
streamlit run /path/to/frontend/dashboard.py

# Test endpoints
curl http://localhost:8000/api/market-data/RELIANCE?timeframe=5m
curl http://localhost:8000/api/portfolio/performance?days=7
```

### 2. API Testing (Postman/Insomnia)
- Test market-data endpoint structure
- Verify OHLCV data format
- Check trades endpoint response
- Validate portfolio performance format

### 3. Frontend Testing
- Chart renders without errors
- Data loads correctly
- Interactive features work (zoom, pan, hover)
- Performance acceptable with large datasets

### 4. Data Flow Testing
```
Browser → Streamlit → FastAPI → Database → Response → Chart
```

---

## Troubleshooting

### Chart Not Rendering
- Check browser console (F12) for errors
- Verify API returns valid JSON
- Ensure Plotly in requirements.txt
- Test API endpoint with curl first

### Data Not Loading
- Check backend logs: `docker-compose logs app`
- Verify database connection
- Test API directly with curl
- Check for CORS issues

### Performance Issues
- Reduce data points (limit candles)
- Increase cache duration
- Use `scattergl` for large datasets
- Profile with `streamlit run --logger.level=debug`

---

## Resources

- **Plotly Docs**: https://plotly.com/python/
- **Streamlit Docs**: https://docs.streamlit.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **TA-Lib Docs**: https://github.com/mrjbq7/ta-lib
- **Dhan API**: https://dhanhq.co/docs/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## Next Steps

1. **Read** CODEBASE_STRUCTURE_FOR_VISUALIZATION.md (understanding)
2. **Scan** VISUALIZATION_QUICK_REFERENCE.md (quick reference)
3. **Review** ARCHITECTURE_DIAGRAM.txt (visual understanding)
4. **Start** with Phase 1 (enhance backend endpoints)
5. **Test** API responses before frontend
6. **Implement** frontend visualization (Phase 2)
7. **Iterate** through remaining phases

---

## Document Summary Table

| Document | Size | Best For | Read Time |
|----------|------|----------|-----------|
| CODEBASE_STRUCTURE_FOR_VISUALIZATION.md | 20 KB | Complete understanding | 30-45 min |
| VISUALIZATION_QUICK_REFERENCE.md | 10 KB | Quick implementation | 15-20 min |
| ARCHITECTURE_DIAGRAM.txt | 25 KB | Visual learning | 20-30 min |

---

## Questions?

All questions should be answerable from these three documents. Use the Quick Navigation section above to find specific information.

---

**Created**: November 2025
**Project**: AI Trading Agent - Indian Stock Market
**Scope**: Graph Visualization Feature Implementation
**Status**: Documentation Complete, Ready for Implementation

---

## File Locations (Absolute Paths)

- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/CODEBASE_STRUCTURE_FOR_VISUALIZATION.md`
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/VISUALIZATION_QUICK_REFERENCE.md`
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/ARCHITECTURE_DIAGRAM.txt`
- `/Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market/VISUALIZATION_IMPLEMENTATION_INDEX.md` (this file)

