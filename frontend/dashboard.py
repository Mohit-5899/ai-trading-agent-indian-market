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
    
    # Auto-refresh every 5 seconds for live trading
    st_autorefresh(interval=5000, key="dashboard_refresh")
    
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
                "icon": {"color": "#1f2937", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#e5e7eb", "color": "#374151"},
                "nav-link-selected": {"background-color": "#3b82f6", "color": "white"},
            }
        )
        
        # System status in sidebar
        st.markdown("<h3 style='color: #1f2937;'>System Status</h3>", unsafe_allow_html=True)
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
    """Live Trading Dashboard - Alpha Arena Style"""
    
    # Current time and countdown
    current_time = datetime.now()
    market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # Calculate time to market close
    if current_time < market_open:
        time_to_open = market_open - current_time
        countdown_text = f"Market opens in: {str(time_to_open).split('.')[0]}"
        market_status = "🔴 PRE-MARKET"
    elif current_time > market_close:
        time_to_next_open = (market_open + timedelta(days=1)) - current_time
        countdown_text = f"Market opens in: {str(time_to_next_open).split('.')[0]}"
        market_status = "🔴 CLOSED"
    else:
        time_to_close = market_close - current_time
        countdown_text = f"Market closes in: {str(time_to_close).split('.')[0]}"
        market_status = "🟢 LIVE"
    
    # Header with live status
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <h1 style="color: #1f2937; margin: 0;">🤖 AI Trading Arena - Indian Market</h1>
        <p style="color: #6b7280; margin: 0;">Multi-LLM Live Trading Competition</p>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f3f4f6; border-radius: 0.5rem;">
            <h3 style="margin: 0; color: #374151;">{market_status}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #fef3c7; border-radius: 0.5rem;">
            <h4 style="margin: 0; color: #92400e;">COUNTDOWN</h4>
            <p style="margin: 0; color: #92400e; font-weight: bold;">{countdown_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get live data
    accounts = dashboard.get_accounts()
    performance_data = dashboard.get_portfolio_performance(days=7)
    system_status = dashboard.get_system_status()
    
    if not accounts:
        st.error("⚠️ No trading accounts found")
        return
    
    # Live metrics bar
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate live metrics
    qwen_account = next((acc for acc in accounts if 'qwen' in acc.get('name', '').lower()), None)
    deepseek_account = next((acc for acc in accounts if 'deepseek' in acc.get('name', '').lower()), None)
    
    with col1:
        btc_style = "color: #1f2937; font-weight: bold; font-size: 1.2em;"
        st.markdown(f'<p style="{btc_style}">🤖 QWN</p>', unsafe_allow_html=True)
        if qwen_account:
            st.markdown(f"<h3 style='margin: 0; color: #374151;'>₹{qwen_account['capital_allocation']:,.0f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='margin: 0; color: #374151;'>₹10,000</h3>", unsafe_allow_html=True)
    
    with col2:
        eth_style = "color: #1f2937; font-weight: bold; font-size: 1.2em;"
        st.markdown(f'<p style="{eth_style}">🧠 DPK</p>', unsafe_allow_html=True)
        if deepseek_account:
            st.markdown(f"<h3 style='margin: 0; color: #374151;'>₹{deepseek_account['capital_allocation']:,.0f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='margin: 0; color: #374151;'>₹10,000</h3>", unsafe_allow_html=True)
    
    with col3:
        rel_style = "color: #1f2937; font-weight: bold; font-size: 1.2em;"
        st.markdown(f'<p style="{rel_style}">📈 REL</p>', unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0; color: #374151;'>₹2,400</h3>", unsafe_allow_html=True)
    
    with col4:
        tcs_style = "color: #1f2937; font-weight: bold; font-size: 1.2em;"
        st.markdown(f'<p style="{tcs_style}">💼 TCS</p>', unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0; color: #374151;'>₹3,200</h3>", unsafe_allow_html=True)
    
    with col5:
        infy_style = "color: #1f2937; font-weight: bold; font-size: 1.2em;"
        st.markdown(f'<p style="{infy_style}">🔮 INFY</p>', unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0; color: #374151;'>₹1,800</h3>", unsafe_allow_html=True)
    
    # Main portfolio chart - Alpha Arena style
    st.markdown("<h3 style='color: #1f2937;'>📊 LIVE PORTFOLIO PERFORMANCE</h3>", unsafe_allow_html=True)
    
    if performance_data and len(performance_data) > 1:
        df = pd.DataFrame(performance_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create multi-line chart like Alpha Arena
        fig = go.Figure()
        
        # Add Qwen portfolio line
        qwen_data = [row for row in performance_data if 'qwen' in row.get('account_id', '').lower()]
        if qwen_data:
            qwen_df = pd.DataFrame(qwen_data)
            qwen_df['timestamp'] = pd.to_datetime(qwen_df['timestamp'])
            fig.add_trace(go.Scatter(
                x=qwen_df['timestamp'],
                y=qwen_df['total_value'],
                mode='lines',
                name='Qwen 3 235B',
                line=dict(color='#f97316', width=3),
                hovertemplate='<b>Qwen</b><br>Time: %{x}<br>Value: ₹%{y:,.2f}<extra></extra>'
            ))
        
        # Add DeepSeek portfolio line
        deepseek_data = [row for row in performance_data if 'deepseek' in row.get('account_id', '').lower()]
        if deepseek_data:
            deepseek_df = pd.DataFrame(deepseek_data)
            deepseek_df['timestamp'] = pd.to_datetime(deepseek_df['timestamp'])
            fig.add_trace(go.Scatter(
                x=deepseek_df['timestamp'],
                y=deepseek_df['total_value'],
                mode='lines',
                name='DeepSeek v3.2',
                line=dict(color='#8b5cf6', width=3),
                hovertemplate='<b>DeepSeek</b><br>Time: %{x}<br>Value: ₹%{y:,.2f}<extra></extra>'
            ))
        
        # Add combined portfolio line if no individual data
        if not qwen_data and not deepseek_data:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['total_value'],
                mode='lines',
                name='Combined Portfolio',
                line=dict(color='#10b981', width=3),
                hovertemplate='<b>Total</b><br>Time: %{x}<br>Value: ₹%{y:,.2f}<extra></extra>'
            ))
        
        # Style like Alpha Arena
        fig.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title="Time",
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title="Portfolio Value (₹)",
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                zeroline=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Show placeholder chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[datetime.now() - timedelta(hours=6), datetime.now()],
            y=[10000, 10000],
            mode='lines',
            name='Waiting for data...',
            line=dict(color='gray', width=2, dash='dash')
        ))
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Time"),
            yaxis=dict(title="Portfolio Value (₹)"),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Live trading status and activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h3 style='color: #1f2937;'>⚡ LIVE TRADING ACTIVITY</h3>", unsafe_allow_html=True)
        recent_trades = dashboard.get_trades(limit=10)
        
        if recent_trades:
            for i, trade in enumerate(recent_trades[:5]):
                trade_time = pd.to_datetime(trade['executed_at']).strftime('%H:%M:%S')
                side_color = '#10b981' if trade['side'] == 'BUY' else '#ef4444'
                model_name = 'QWN' if 'qwen' in trade.get('account_name', '').lower() else 'DPK'
                
                st.markdown(f"""
                <div style="padding: 0.5rem; margin: 0.25rem 0; border-left: 4px solid {side_color}; background: #f9fafb;">
                    <strong style="color: {side_color};">{trade['side']}</strong> 
                    <span style="color: #374151;">{trade['stock_symbol']} x{trade['quantity']} 
                    @ ₹{trade['entry_price']:.2f}</span> 
                    <small style="color: #6b7280;">({model_name} - {trade_time})</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent trading activity")
    
    with col2:
        st.markdown("<h3 style='color: #1f2937;'>🏆 LEADERBOARD</h3>", unsafe_allow_html=True)
        
        # Model performance comparison
        qwen_pnl = 0
        deepseek_pnl = 0
        
        if performance_data:
            for row in performance_data[-5:]:  # Last 5 data points
                if 'qwen' in row.get('account_id', '').lower():
                    qwen_pnl = row.get('total_pnl', 0)
                elif 'deepseek' in row.get('account_id', '').lower():
                    deepseek_pnl = row.get('total_pnl', 0)
        
        models = [
            ("🥇 Qwen 3 235B", qwen_pnl, '#f97316'),
            ("🥈 DeepSeek v3.2", deepseek_pnl, '#8b5cf6')
        ]
        
        # Sort by performance
        models.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (name, pnl, color) in enumerate(models):
            pnl_pct = (pnl / 10000) * 100 if pnl != 0 else 0
            st.markdown(f"""
            <div style="padding: 1rem; margin: 0.5rem 0; border: 2px solid {color}; border-radius: 0.5rem;">
                <h4 style="margin: 0; color: {color};">{name}</h4>
                <p style="margin: 0; color: #374151;">P&L: ₹{pnl:,.2f}</p>
                <p style="margin: 0; color: #374151;">Return: {pnl_pct:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Market status footer
    status_text = "🟢 All systems operational" if system_status and system_status.get("status") == "healthy" else "⚠️ System issues detected"
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; background: #f3f4f6; border-radius: 0.5rem;">
        <p style="margin: 0; color: #6b7280;">
            {status_text} | Live data updates every 5 seconds | 
            Trading Session: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_portfolio(dashboard):
    """Show portfolio performance details"""
    st.markdown("<h1 style='color: #1f2937;'>💼 Portfolio Performance</h1>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color: #1f2937;'>📊 Portfolio Value Over Time</h3>", unsafe_allow_html=True)
    
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
        st.markdown("<h3 style='color: #1f2937;'>📈 Daily P&L</h3>", unsafe_allow_html=True)
        
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
    st.markdown("<h1 style='color: #1f2937;'>💹 Trading History</h1>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color: #1f2937;'>📋 Trades</h3>", unsafe_allow_html=True)
    
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
    st.markdown("<h1 style='color: #1f2937;'>🧠 LLM Decision History</h1>", unsafe_allow_html=True)
    
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
    st.markdown("<h1 style='color: #1f2937;'>⚙️ System Control</h1>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color: #1f2937;'>🎮 Trading Controls</h3>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color: #1f2937;'>📊 System Information</h3>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color: #dc2626;'>⚠️ Danger Zone</h3>", unsafe_allow_html=True)
    
    with st.expander("Emergency Controls"):
        st.warning("These actions are irreversible. Use with caution!")
        
        if st.button("🛑 Emergency Stop All Trading", type="secondary"):
            # This would call the close all positions endpoint
            st.error("Emergency stop activated! (Feature not implemented yet)")
        
        st.markdown("---")
        st.markdown("**Note:** Always monitor the system during trading hours and have manual controls ready.")

if __name__ == "__main__":
    main()