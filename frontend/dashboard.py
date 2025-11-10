"""
AI Trading System - Streamlit Dashboard
Main dashboard for monitoring the Indian market trading system
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="AI Trading System - Indian Market",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .positive {
        color: #10b981;
    }
    .negative {
        color: #ef4444;
    }
    .neutral {
        color: #6b7280;
    }
    .trading-signal {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    .signal-buy {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
    }
    .signal-sell {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
    }
    .signal-hold {
        background-color: #f3f4f6;
        border-left: 4px solid #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"  # FastAPI backend URL

class TradingDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        self.api_base = API_BASE_URL
    
    def make_api_request(self, endpoint, params=None):
        """Make API request with error handling"""
        try:
            url = f"{self.api_base}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def get_system_status(self):
        """Get system status"""
        return self.make_api_request("/api/system/status")
    
    def get_portfolio_performance(self, days=30):
        """Get portfolio performance data"""
        return self.make_api_request("/api/portfolio/performance", {"days": days})
    
    def get_recent_invocations(self, limit=10):
        """Get recent LLM invocations"""
        return self.make_api_request("/api/invocations", {"limit": limit})
    
    def get_trades(self, limit=50):
        """Get recent trades"""
        return self.make_api_request("/api/trades", {"limit": limit})
    
    def get_accounts(self):
        """Get trading accounts"""
        return self.make_api_request("/api/accounts")

def main():
    """Main dashboard function"""
    
    # Initialize dashboard
    dashboard = TradingDashboard()
    
    # Auto-refresh every 30 seconds
    st_autorefresh(interval=30000, key="dashboard_refresh")
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🤖 AI Trading System - Indian Market</h1>
        <p style="color: #d1d5db; margin: 0;">Multi-LLM Automated Trading Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1f2937/ffffff?text=AI+Trading", width=200)
        
        selected = option_menu(
            "Navigation",
            ["Dashboard", "Portfolio", "Trades", "LLM Decisions", "System Control"],
            icons=["speedometer2", "pie-chart", "arrow-left-right", "cpu", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )
        
        # System status in sidebar
        st.subheader("System Status")
        status_data = dashboard.get_system_status()
        
        if status_data:
            if status_data.get("status") == "healthy":
                st.success("🟢 System Healthy")
            else:
                st.error("🔴 System Issues")
            
            st.metric("Active Accounts", status_data.get("active_accounts", 0))
            st.metric("Today's Trades", status_data.get("today_trades", 0))
            
            market_status = "🟢 Open" if status_data.get("market_open") else "🔴 Closed"
            st.write(f"Market: {market_status}")
            
            trading_status = "🟢 Enabled" if status_data.get("trading_enabled") else "🔴 Disabled"
            st.write(f"Trading: {trading_status}")
        else:
            st.error("Unable to connect to backend")
    
    # Main content based on selection
    if selected == "Dashboard":
        show_dashboard(dashboard)
    elif selected == "Portfolio":
        show_portfolio(dashboard)
    elif selected == "Trades":
        show_trades(dashboard)
    elif selected == "LLM Decisions":
        show_llm_decisions(dashboard)
    elif selected == "System Control":
        show_system_control(dashboard)

def show_dashboard(dashboard):
    """Show main dashboard overview"""
    st.header("📊 Trading Overview")
    
    # Get data
    accounts = dashboard.get_accounts()
    performance_data = dashboard.get_portfolio_performance(days=7)  # Last 7 days
    recent_invocations = dashboard.get_recent_invocations(limit=5)
    
    if not accounts:
        st.error("No trading accounts found")
        return
    
    # Account metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_capital = sum(float(acc.get("capital_allocation", 0)) for acc in accounts)
    active_accounts = len(accounts)
    
    with col1:
        st.metric("Total Capital", f"₹{total_capital:,.0f}")
    
    with col2:
        st.metric("Active Accounts", active_accounts)
    
    with col3:
        if performance_data and len(performance_data) > 1:
            latest_value = performance_data[-1]["total_value"]
            previous_value = performance_data[0]["total_value"]
            change = latest_value - previous_value
            change_pct = (change / previous_value) * 100 if previous_value > 0 else 0
            st.metric("7-Day P&L", f"₹{change:,.2f}", f"{change_pct:+.2f}%")
        else:
            st.metric("7-Day P&L", "₹0.00", "0.00%")
    
    with col4:
        total_invocations = sum(acc.get("invocation_count", 0) for acc in accounts)
        st.metric("Total Invocations", total_invocations)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Portfolio Performance (7 Days)")
        if performance_data and len(performance_data) > 1:
            df = pd.DataFrame(performance_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = px.line(
                df, 
                x='timestamp', 
                y='total_value',
                title="Portfolio Value Over Time"
            )
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Portfolio Value (₹)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance data available")
    
    with col2:
        st.subheader("🧠 Recent LLM Decisions")
        if recent_invocations:
            for invocation in recent_invocations[:3]:
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0;">
                        <strong>{invocation['account_name']}</strong><br>
                        <small>{invocation['created_at']}</small><br>
                        Tool calls: {len(invocation.get('tool_calls', []))}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No recent LLM decisions")
    
    # Account overview
    st.subheader("💼 Account Overview")
    if accounts:
        account_df = pd.DataFrame(accounts)
        account_df = account_df[['name', 'model_name', 'capital_allocation', 'allocation_percentage', 'invocation_count']]
        account_df.columns = ['Account', 'LLM Model', 'Capital (₹)', 'Allocation %', 'Invocations']
        st.dataframe(account_df, use_container_width=True)

def show_portfolio(dashboard):
    """Show portfolio performance details"""
    st.header("💼 Portfolio Performance")
    
    # Time period selector
    time_period = st.selectbox(
        "Select time period",
        ["7 Days", "30 Days", "90 Days"],
        index=1
    )
    
    days_map = {"7 Days": 7, "30 Days": 30, "90 Days": 90}
    days = days_map[time_period]
    
    # Get performance data
    performance_data = dashboard.get_portfolio_performance(days=days)
    
    if not performance_data:
        st.error("No portfolio data available")
        return
    
    df = pd.DataFrame(performance_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Performance metrics
    latest = df.iloc[-1]
    first = df.iloc[0]
    
    total_return = latest['total_value'] - first['total_value']
    return_pct = (total_return / first['total_value']) * 100 if first['total_value'] > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Value", f"₹{latest['total_value']:,.2f}")
    
    with col2:
        st.metric("Total Return", f"₹{total_return:,.2f}", f"{return_pct:+.2f}%")
    
    with col3:
        st.metric("Available Cash", f"₹{latest['available_cash']:,.2f}")
    
    with col4:
        st.metric("Invested Amount", f"₹{latest['invested_amount']:,.2f}")
    
    # Performance chart
    st.subheader("📊 Portfolio Value Over Time")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['total_value'],
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.update_layout(
        title=f"Portfolio Performance - {time_period}",
        xaxis_title="Date",
        yaxis_title="Value (₹)",
        hovermode='x unified',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # P&L Chart
    if 'day_pnl' in df.columns:
        st.subheader("📈 Daily P&L")
        
        fig_pnl = px.bar(
            df,
            x='timestamp',
            y='day_pnl',
            title="Daily Profit & Loss",
            color='day_pnl',
            color_continuous_scale=['red', 'gray', 'green']
        )
        
        st.plotly_chart(fig_pnl, use_container_width=True)

def show_trades(dashboard):
    """Show trading history"""
    st.header("💹 Trading History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "OPEN", "CLOSED", "CANCELLED"]
        )
    
    with col2:
        limit = st.number_input("Number of trades", min_value=10, max_value=200, value=50)
    
    with col3:
        if st.button("Refresh Trades"):
            st.rerun()
    
    # Get trades data
    params = {"limit": limit}
    if status_filter != "All":
        params["status"] = status_filter
    
    trades_data = dashboard.make_api_request("/api/trades", params)
    
    if not trades_data:
        st.warning("No trades found")
        return
    
    df = pd.DataFrame(trades_data)
    
    # Summary metrics
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(df))
        
        with col2:
            closed_trades = df[df['status'] == 'CLOSED']
            profitable = len(closed_trades[closed_trades['net_pnl'] > 0]) if not closed_trades.empty else 0
            win_rate = (profitable / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col3:
            total_pnl = closed_trades['net_pnl'].sum() if not closed_trades.empty else 0
            st.metric("Total P&L", f"₹{total_pnl:,.2f}")
        
        with col4:
            open_trades = len(df[df['status'] == 'OPEN'])
            st.metric("Open Positions", open_trades)
    
    # Trades table
    st.subheader("📋 Trades")
    
    if not df.empty:
        # Format the dataframe for display
        display_df = df.copy()
        display_df['executed_at'] = pd.to_datetime(display_df['executed_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Select columns for display
        columns_to_show = ['executed_at', 'account_name', 'stock_symbol', 'strategy_name', 
                          'side', 'quantity', 'entry_price', 'net_pnl', 'status']
        display_df = display_df[columns_to_show]
        
        # Style the dataframe
        def style_pnl(val):
            if pd.isna(val) or val == 0:
                return 'color: gray'
            elif val > 0:
                return 'color: green; font-weight: bold'
            else:
                return 'color: red; font-weight: bold'
        
        styled_df = display_df.style.applymap(style_pnl, subset=['net_pnl'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No trades to display")

def show_llm_decisions(dashboard):
    """Show LLM decision history"""
    st.header("🧠 LLM Decision History")
    
    # Controls
    col1, col2 = st.columns(2)
    
    with col1:
        limit = st.number_input("Number of decisions", min_value=5, max_value=50, value=20)
    
    with col2:
        if st.button("Refresh Decisions"):
            st.rerun()
    
    # Get invocations data
    invocations_data = dashboard.get_recent_invocations(limit=limit)
    
    if not invocations_data:
        st.warning("No LLM decisions found")
        return
    
    # Display invocations
    for i, invocation in enumerate(invocations_data):
        with st.expander(f"Decision #{i+1} - {invocation['account_name']} - {invocation['created_at'][:19]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Account Info:**")
                st.write(f"Account: {invocation['account_name']}")
                st.write(f"Execution Time: {invocation.get('execution_time_ms', 0)} ms")
                st.write(f"Tokens Used: {invocation.get('tokens_used', 0)}")
            
            with col2:
                st.markdown("**Tool Calls:**")
                tool_calls = invocation.get('tool_calls', [])
                if tool_calls:
                    for tool_call in tool_calls:
                        tool_name = tool_call.get('tool_name', 'Unknown')
                        result = tool_call.get('result', 'No result')
                        
                        # Style based on tool type
                        if 'buy' in tool_name.lower():
                            st.markdown(f"""
                            <div class="trading-signal signal-buy">
                                <strong>🟢 {tool_name}</strong><br>
                                {result}
                            </div>
                            """, unsafe_allow_html=True)
                        elif 'sell' in tool_name.lower():
                            st.markdown(f"""
                            <div class="trading-signal signal-sell">
                                <strong>🔴 {tool_name}</strong><br>
                                {result}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="trading-signal signal-hold">
                                <strong>⚪ {tool_name}</strong><br>
                                {result}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("No tool calls made")
            
            # LLM Response
            if invocation.get('llm_response'):
                st.markdown("**LLM Response:**")
                st.text_area("", value=invocation['llm_response'], height=100, disabled=True, key=f"response_{i}")

def show_system_control(dashboard):
    """Show system control panel"""
    st.header("⚙️ System Control")
    
    # System status
    status_data = dashboard.get_system_status()
    
    if not status_data:
        st.error("Unable to connect to system")
        return
    
    # Status overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status_data.get("status") == "healthy":
            st.success("✅ System Health: Good")
        else:
            st.error("❌ System Health: Issues")
    
    with col2:
        market_status = status_data.get("market_open", False)
        if market_status:
            st.success("🟢 Market: Open")
        else:
            st.info("🔴 Market: Closed")
    
    with col3:
        trading_enabled = status_data.get("trading_enabled", False)
        if trading_enabled:
            st.success("▶️ Trading: Enabled")
        else:
            st.warning("⏸️ Trading: Disabled")
    
    # Control buttons
    st.subheader("🎮 Trading Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Trading", type="primary"):
            response = requests.post(f"{dashboard.api_base}/api/system/start-trading")
            if response.status_code == 200:
                st.success("Trading started successfully!")
            else:
                st.error("Failed to start trading")
    
    with col2:
        if st.button("⏹️ Stop Trading", type="secondary"):
            response = requests.post(f"{dashboard.api_base}/api/system/stop-trading")
            if response.status_code == 200:
                st.success("Trading stopped successfully!")
            else:
                st.error("Failed to stop trading")
    
    with col3:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # System information
    st.subheader("📊 System Information")
    
    if status_data:
        info_df = pd.DataFrame([
            ["System Status", status_data.get("status", "Unknown")],
            ["Active Accounts", status_data.get("active_accounts", 0)],
            ["Today's Trades", status_data.get("today_trades", 0)],
            ["Trading Enabled", status_data.get("trading_enabled", False)],
            ["Market Open", status_data.get("market_open", False)],
            ["Last Updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ], columns=["Metric", "Value"])
        
        st.dataframe(info_df, use_container_width=True, hide_index=True)
    
    # Danger zone
    st.subheader("⚠️ Danger Zone")
    
    with st.expander("Emergency Controls"):
        st.warning("These actions are irreversible. Use with caution!")
        
        if st.button("🛑 Emergency Stop All Trading", type="secondary"):
            # This would call the close all positions endpoint
            st.error("Emergency stop activated! (Feature not implemented yet)")
        
        st.markdown("---")
        st.markdown("**Note:** Always monitor the system during trading hours and have manual controls ready.")

if __name__ == "__main__":
    main()