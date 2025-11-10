# AI Trading System - Streamlit Dashboard

A modern web dashboard for monitoring and controlling the AI Trading System for Indian markets.

## 🎯 Features

### 📊 **Dashboard Overview**
- Real-time system status
- Portfolio performance charts
- Recent LLM decisions
- Account overview with capital allocation

### 💼 **Portfolio Performance**
- Interactive performance charts with Plotly
- Multi-timeframe analysis (7, 30, 90 days)
- P&L tracking and metrics
- Return calculations

### 💹 **Trading History**
- Complete trade history with filtering
- Win rate and profit metrics
- Real-time trade status
- Export capabilities

### 🧠 **LLM Decisions**
- Recent AI model decisions
- Tool call tracking (buy/sell/hold actions)
- Execution time and token usage
- Decision reasoning display

### ⚙️ **System Control**
- Start/stop trading controls
- System health monitoring
- Emergency controls
- Real-time status updates

## 🚀 Quick Start

### Prerequisites

1. **Backend Running**: Make sure your FastAPI backend is running at `http://localhost:8000`
2. **Python Environment**: Use the same virtual environment as your trading system

### Installation

```bash
# Navigate to frontend directory
cd /Users/mohitmandawat/Coding/CodeTrading/ai-trading-agent-indian-market/frontend

# Install frontend dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Method 1: Use the launch script
python run_dashboard.py

# Method 2: Direct streamlit command
streamlit run dashboard.py --server.port 8501
```

### Access the Dashboard

- **URL**: http://localhost:8501
- **Auto-refresh**: Dashboard refreshes every 30 seconds
- **Backend API**: Connects to http://localhost:8000

## 📱 Dashboard Pages

### 1. **Dashboard** (Home)
- System overview with key metrics
- 7-day portfolio performance chart
- Recent LLM decisions summary
- Account allocation display

### 2. **Portfolio**
- Detailed portfolio performance
- Multi-timeframe charts (7/30/90 days)
- Return calculations and metrics
- Daily P&L visualization

### 3. **Trades**
- Complete trading history
- Filter by status (OPEN/CLOSED/CANCELLED)
- Win rate and profit metrics
- Individual trade details

### 4. **LLM Decisions**
- Recent AI model invocations
- Tool calls with results
- Token usage and execution time
- Model reasoning display

### 5. **System Control**
- Trading start/stop controls
- System health monitoring
- Market status display
- Emergency controls

## 🎨 Visual Features

### **Real-time Updates**
- Auto-refresh every 30 seconds
- Manual refresh buttons
- Live status indicators

### **Interactive Charts**
- Plotly-powered visualizations
- Zoom, pan, and hover features
- Multi-timeframe analysis
- Color-coded P&L displays

### **Status Indicators**
- 🟢 Green: Positive/Active/Healthy
- 🔴 Red: Negative/Inactive/Issues
- ⚪ Gray: Neutral/Unknown

### **Trading Signals Display**
- 🟢 BUY signals with green background
- 🔴 SELL signals with red background
- ⚪ HOLD signals with gray background

## 🔧 Configuration

### **API Connection**
The dashboard connects to your FastAPI backend. Update the API base URL if needed:

```python
# In dashboard.py, line 67
API_BASE_URL = "http://localhost:8000"  # Change if backend runs elsewhere
```

### **Refresh Intervals**
Auto-refresh can be customized:

```python
# In dashboard.py, line 156
st_autorefresh(interval=30000, key="dashboard_refresh")  # 30 seconds
```

### **Chart Styling**
Charts use Plotly with customizable themes. Modify the chart configurations in the respective functions.

## 📊 Data Sources

The dashboard pulls data from these FastAPI endpoints:

- `/api/system/status` - System health and status
- `/api/portfolio/performance` - Portfolio timeseries data
- `/api/invocations` - LLM decision history
- `/api/trades` - Trading history
- `/api/accounts` - Account information

## 🎮 Usage Guide

### **Starting the System**
1. Start the FastAPI backend: `python main.py`
2. Start the dashboard: `python frontend/run_dashboard.py`
3. Open http://localhost:8501 in your browser

### **Monitoring Trading**
1. Check **Dashboard** for system overview
2. Monitor **Portfolio** for performance
3. Review **Trades** for execution details
4. Watch **LLM Decisions** for AI reasoning

### **Controlling Trading**
1. Go to **System Control** page
2. Use Start/Stop buttons to control trading
3. Monitor system status in real-time
4. Use emergency controls if needed

## 🛡️ Safety Features

### **Real-time Monitoring**
- Live system status display
- Trading enable/disable controls
- Market hours awareness
- Error handling and display

### **Emergency Controls**
- Emergency stop functionality
- Manual trading override
- System health alerts
- Connection status monitoring

## 🔍 Troubleshooting

### **Common Issues**

1. **"Unable to connect to backend"**
   - Check if FastAPI server is running on port 8000
   - Verify API_BASE_URL in dashboard.py

2. **"No data available"**
   - Ensure trading system has been running and collecting data
   - Check if database is properly set up

3. **Charts not loading**
   - Verify Plotly installation: `pip install plotly`
   - Check browser JavaScript is enabled

4. **Auto-refresh not working**
   - Install streamlit-autorefresh: `pip install streamlit-autorefresh`
   - Clear browser cache

### **Performance Tips**

1. **Reduce refresh interval** for slower connections
2. **Limit data points** for large datasets
3. **Use filtering** to focus on specific data
4. **Close unused browser tabs** for better performance

## 🎯 Next Steps

### **Potential Enhancements**
1. **Real-time WebSocket updates** for instant data
2. **Mobile-responsive design** for phone access
3. **Custom chart themes** and styling options
4. **Data export functionality** (CSV, Excel)
5. **Alert notifications** for important events
6. **Strategy backtesting interface**
7. **Paper trading simulation**

### **Integration Options**
1. **Slack/Discord notifications** for trade alerts
2. **Email reports** for daily summaries
3. **SMS alerts** for critical events
4. **Telegram bot** for remote monitoring

---

## 📞 Support

If you encounter issues:
1. Check the backend logs for API errors
2. Verify all dependencies are installed
3. Ensure proper network connectivity
4. Review the troubleshooting section above

The dashboard is designed to be intuitive and user-friendly while providing comprehensive monitoring capabilities for your AI trading system.

---

**Dashboard Version**: 1.0.0  
**Last Updated**: November 2024  
**Compatible with**: AI Trading System v1.0.0