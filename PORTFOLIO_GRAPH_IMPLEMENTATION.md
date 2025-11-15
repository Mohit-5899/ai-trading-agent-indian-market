# Portfolio Graph Visualization Implementation

## Overview
This document describes the implementation of a multi-asset portfolio performance graph similar to the Alpha Arena screenshot, showing total account value with individual asset performance lines.

## Implementation Summary

### ✅ Completed Features

1. **Backend API Endpoint** (`api/main.py:392-485`)
   - New endpoint: `/api/portfolio/multi-asset-performance`
   - Supports time range filtering: 24h, 72h, all-time
   - Returns time-series data for total portfolio value + individual assets
   - Includes metadata (change %, data points, etc.)

2. **Frontend Chart Component** (`frontend/dashboard.py:274-368`)
   - Function: `create_multi_asset_chart(data)`
   - Multi-line Plotly chart with color-coded assets
   - Matches Alpha Arena aesthetic with:
     - White background with grid lines
     - Professional color palette (blue, purple, orange, cyan, red)
     - Interactive hover tooltips showing values
     - Centered title "TOTAL ACCOUNT VALUE"
     - Legend positioned on the right side

3. **Dashboard Integration** (`frontend/dashboard.py`)
   - Added to main Dashboard view (line 228-258)
   - Added to Portfolio page with time filters (line 370-433)
   - Time range selector buttons: ALL, 72h, 24h

4. **Interactive Features**
   - Hover tooltips with formatted currency values
   - Unified hover mode (shows all assets at once)
   - Time range filtering
   - Responsive layout

## Technical Details

### API Response Format

```json
{
  "timestamps": ["2025-01-01T00:00:00", ...],
  "total_value": [100000.0, 105000.0, ...],
  "assets": {
    "RELIANCE": [50000.0, 52000.0, ...],
    "TCS": [30000.0, 31000.0, ...],
    "INFY": [20000.0, 22000.0, ...]
  },
  "metadata": {
    "start_date": "2025-01-01T00:00:00",
    "end_date": "2025-01-31T00:00:00",
    "data_points": 120,
    "latest_value": 105000.0,
    "first_value": 100000.0,
    "total_change": 5000.0,
    "change_percentage": 5.0,
    "time_range": "30d"
  }
}
```

### Color Palette

- **Total Portfolio**: `#5B8FF9` (Blue)
- **Asset 1**: `#9270CA` (Purple)
- **Asset 2**: `#FF9D4E` (Orange)
- **Asset 3**: `#61DDAA` (Cyan/Green)
- **Asset 4**: `#F76560` (Red)
- **Asset 5**: `#7262FD` (Indigo)
- **Asset 6**: `#78D3F8` (Light Blue)

### Chart Specifications

- **Height**: 500px
- **Margins**: Left 60px, Right 150px, Top 80px, Bottom 60px
- **Grid**: Light gray (#E5E5E5) lines
- **Background**: White
- **Line Width**: 2px for assets, 3px for total value
- **Y-axis Format**: ₹ currency format with thousands separator

## File Changes

1. **api/main.py**
   - Added: `/api/portfolio/multi-asset-performance` endpoint (lines 392-485)

2. **frontend/dashboard.py**
   - Added: `get_multi_asset_performance()` method (lines 113-118)
   - Added: `create_multi_asset_chart()` function (lines 274-368)
   - Modified: `show_dashboard()` to include multi-asset chart (lines 228-258)
   - Modified: `show_portfolio()` to feature multi-asset chart prominently (lines 370-499)

## How to Use

### 1. Start the Backend API

```bash
cd /Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market
python -m uvicorn api.main:app --reload --port 8000
```

### 2. Start the Streamlit Dashboard

```bash
streamlit run frontend/dashboard.py
```

### 3. Navigate to Portfolio Section

- Click "Portfolio" in the sidebar navigation
- The multi-asset chart will display at the top
- Use time range buttons (ALL, 72h, 24h) to filter data

## Testing Checklist

- [ ] Backend API responds correctly to `/api/portfolio/multi-asset-performance`
- [ ] Time range filters work (24h, 72h, all)
- [ ] Chart displays with multiple asset lines
- [ ] Hover tooltips show correct values
- [ ] Legend displays all assets properly
- [ ] Chart is responsive to screen size
- [ ] Colors match the screenshot aesthetic
- [ ] Y-axis shows proper currency formatting
- [ ] X-axis shows proper date/time formatting

## Data Requirements

For the chart to work properly, ensure:

1. **Portfolio Snapshots** exist in database
2. **Positions JSON** in each snapshot contains:
   ```json
   [
     {
       "symbol": "RELIANCE",
       "quantity": 100,
       "current_price": 2500.50
     }
   ]
   ```

3. **Minimum Data**: At least 2 snapshots for meaningful visualization

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data
2. **Zoom Controls**: Allow users to zoom into specific time periods
3. **Export**: Download chart as PNG/SVG
4. **Comparison**: Compare against benchmark indices (NIFTY 50, SENSEX)
5. **Annotations**: Mark trading events on the chart
6. **Technical Indicators**: Overlay moving averages, Bollinger bands
7. **Volume Chart**: Add volume bars below the main chart
8. **Asset Toggles**: Click legend to hide/show specific assets

## Troubleshooting

### Issue: No data displayed
- **Solution**: Check if portfolio snapshots exist in database
- **Command**: Query `portfolio_snapshots` table

### Issue: Assets not showing individual lines
- **Solution**: Verify positions JSON format in snapshots
- **Check**: Each position has `symbol`, `quantity`, `current_price`

### Issue: Time range filters not working
- **Solution**: Check API endpoint parameters
- **Debug**: Add logging to see which time_range is being used

### Issue: Chart styling doesn't match screenshot
- **Solution**: Review color palette and layout settings
- **Adjust**: Modify colors dict in `create_multi_asset_chart()`

## Performance Considerations

1. **Caching**: Backend implements 5-minute cache for performance data
2. **Data Limits**: API limits to 365 days max to prevent excessive queries
3. **Frontend**: Chart renders efficiently with Plotly (handles 1000+ points)
4. **Database**: Ensure index on `portfolio_snapshots.created_at`

## Dependencies

All required dependencies are already in the project:

- `plotly==5.17.0` ✅
- `streamlit==1.28.1` ✅
- `pandas` ✅
- `fastapi==0.104.1` ✅
- `sqlalchemy` ✅

No additional installations required!

## API Documentation

Access full API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Look for the "Portfolio Visualization" section with the new endpoint.

---

**Implementation Date**: 2025-11-11
**Status**: ✅ Complete and Ready for Testing
**Next Step**: Test with real trading data
