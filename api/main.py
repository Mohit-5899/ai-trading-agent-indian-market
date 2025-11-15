"""
FastAPI Main Application
Equivalent to crypto system's backend.ts Express server
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text

from models.database import (
    TradingAccount, Trade, Invocation, PortfolioSnapshot, 
    TradingSignal, Stock, Strategy, get_session,
    create_database_engine, create_session_factory
)
from api.schemas import (
    TradeRequest, TradeResponse, PortfolioResponse, 
    InvocationResponse, SystemStatusResponse
)
from config.settings import get_settings

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Trading System - Indian Market",
    description="Automated AI trading system for Indian stock market using multiple LLMs and strategies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (equivalent to crypto system's cors setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
settings = get_settings()
engine = create_database_engine(settings.database_url)
SessionLocal = create_session_factory(engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global caching (equivalent to crypto system's caching)
performance_cache = {"data": None, "last_updated": None}
invocations_cache = {"data": None, "last_updated": None}

# === PORTFOLIO ENDPOINTS (equivalent to crypto system's /performance) ===

@app.get("/api/portfolio/performance", response_model=List[Dict[str, Any]])
async def get_portfolio_performance(
    account_id: Optional[str] = Query(None, description="Specific account ID"),
    days: int = Query(30, description="Number of days to fetch", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get portfolio performance timeseries data
    Equivalent to crypto system's /performance endpoint with 5-min cache
    """
    global performance_cache
    
    # Check cache (5 minutes like crypto system)
    cache_key = f"{account_id}_{days}"
    now = datetime.utcnow()
    
    if (performance_cache["data"] and 
        performance_cache["last_updated"] and 
        (now - performance_cache["last_updated"]).total_seconds() < 300):  # 5 minutes
        
        return performance_cache["data"]
    
    try:
        # Calculate date range
        start_date = now - timedelta(days=days)
        
        # Query portfolio snapshots
        query = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.created_at >= start_date
        ).order_by(PortfolioSnapshot.created_at)
        
        if account_id:
            query = query.filter(PortfolioSnapshot.account_id == account_id)
        
        snapshots = query.all()
        
        # Format response
        performance_data = [
            {
                "timestamp": snapshot.created_at.isoformat(),
                "account_id": snapshot.account_id,
                "total_value": float(snapshot.total_value),
                "available_cash": float(snapshot.available_cash),
                "invested_amount": float(snapshot.invested_amount),
                "day_pnl": float(snapshot.day_pnl or 0),
                "total_pnl": float(snapshot.total_pnl or 0),
                "return_percentage": float(snapshot.return_percentage or 0),
                "positions_count": len(json.loads(snapshot.positions or "[]"))
            }
            for snapshot in snapshots
        ]
        
        # Update cache
        performance_cache["data"] = performance_data
        performance_cache["last_updated"] = now
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Error fetching performance data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching performance data")

@app.get("/api/portfolio/{account_id}", response_model=PortfolioResponse)
async def get_account_portfolio(account_id: str, db: Session = Depends(get_db)):
    """Get current portfolio for specific account"""
    try:
        # Get latest portfolio snapshot
        latest_snapshot = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.account_id == account_id
        ).order_by(desc(PortfolioSnapshot.created_at)).first()
        
        if not latest_snapshot:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get open trades
        open_trades = db.query(Trade).filter(
            Trade.account_id == account_id,
            Trade.status == "OPEN"
        ).all()
        
        return PortfolioResponse(
            account_id=account_id,
            total_value=float(latest_snapshot.total_value),
            available_cash=float(latest_snapshot.available_cash),
            invested_amount=float(latest_snapshot.invested_amount),
            day_pnl=float(latest_snapshot.day_pnl or 0),
            total_pnl=float(latest_snapshot.total_pnl or 0),
            return_percentage=float(latest_snapshot.return_percentage or 0),
            positions=json.loads(latest_snapshot.positions or "[]"),
            open_trades_count=len(open_trades),
            last_updated=latest_snapshot.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio for {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching portfolio")

# === INVOCATIONS ENDPOINTS (equivalent to crypto system's /invocations) ===

@app.get("/api/invocations", response_model=List[InvocationResponse])
async def get_recent_invocations(
    limit: int = Query(30, description="Number of invocations to fetch", ge=1, le=200),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    db: Session = Depends(get_db)
):
    """
    Get recent LLM invocations with 2-minute cache
    Equivalent to crypto system's /invocations endpoint
    """
    global invocations_cache
    
    # Check cache (2 minutes like crypto system)
    cache_key = f"{limit}_{account_id}"
    now = datetime.utcnow()
    
    if (invocations_cache["data"] and 
        invocations_cache["last_updated"] and 
        (now - invocations_cache["last_updated"]).total_seconds() < 120):  # 2 minutes
        
        # Filter cached data if needed
        cached_data = invocations_cache["data"]
        if account_id:
            cached_data = [inv for inv in cached_data if inv["account_id"] == account_id]
        
        return cached_data[:limit]
    
    try:
        # Build query
        query = db.query(Invocation).order_by(desc(Invocation.created_at))
        
        if account_id:
            query = query.filter(Invocation.account_id == account_id)
        
        invocations = query.limit(limit).all()
        
        # Format response with tool calls
        invocations_data = []
        for invocation in invocations:
            # Get account name
            account = db.query(TradingAccount).filter(
                TradingAccount.id == invocation.account_id
            ).first()
            
            # Get tool calls
            tool_calls = db.query(ToolCall).filter(
                ToolCall.invocation_id == invocation.id
            ).order_by(ToolCall.created_at).all()
            
            invocations_data.append({
                "id": invocation.id,
                "account_id": invocation.account_id,
                "account_name": account.name if account else "Unknown",
                "llm_response": invocation.llm_response,
                "execution_time_ms": invocation.execution_time_ms or 0,
                "tokens_used": invocation.tokens_used or 0,
                "created_at": invocation.created_at.isoformat(),
                "tool_calls": [
                    {
                        "tool_name": tc.tool_name,
                        "parameters": json.loads(tc.parameters or "{}"),
                        "result": tc.result,
                        "status": tc.status,
                        "execution_time_ms": tc.execution_time_ms or 0,
                        "created_at": tc.created_at.isoformat()
                    }
                    for tc in tool_calls
                ]
            })
        
        # Update cache
        invocations_cache["data"] = invocations_data
        invocations_cache["last_updated"] = now
        
        return invocations_data
        
    except Exception as e:
        logger.error(f"Error fetching invocations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching invocations")

# === TRADING ENDPOINTS ===

@app.get("/api/trades", response_model=List[TradeResponse])
async def get_trades(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    status: Optional[str] = Query(None, description="Filter by status (OPEN, CLOSED, CANCELLED)"),
    limit: int = Query(100, description="Number of trades to fetch", ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get trade history"""
    try:
        query = db.query(Trade).order_by(desc(Trade.created_at))
        
        if account_id:
            query = query.filter(Trade.account_id == account_id)
        if status:
            query = query.filter(Trade.status == status.upper())
        
        trades = query.limit(limit).all()
        
        # Format response
        trades_data = []
        for trade in trades:
            # Get related data
            stock = db.query(Stock).filter(Stock.id == trade.stock_id).first()
            strategy = db.query(Strategy).filter(Strategy.id == trade.strategy_id).first()
            account = db.query(TradingAccount).filter(TradingAccount.id == trade.account_id).first()
            
            trades_data.append(TradeResponse(
                id=trade.id,
                account_name=account.name if account else "Unknown",
                stock_symbol=stock.symbol if stock else "Unknown",
                strategy_name=strategy.name if strategy else "Unknown",
                side=trade.side,
                quantity=trade.quantity,
                entry_price=float(trade.entry_price or 0),
                exit_price=float(trade.exit_price or 0) if trade.exit_price else None,
                net_pnl=float(trade.net_pnl or 0) if trade.net_pnl else None,
                status=trade.status,
                executed_at=trade.executed_at,
                closed_at=trade.closed_at,
                created_at=trade.created_at
            ))
        
        return trades_data
        
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail="Error fetching trades")

@app.get("/api/trades/{trade_id}")
async def get_trade_details(trade_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific trade"""
    try:
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        # Get related data
        stock = db.query(Stock).filter(Stock.id == trade.stock_id).first()
        strategy = db.query(Strategy).filter(Strategy.id == trade.strategy_id).first()
        account = db.query(TradingAccount).filter(TradingAccount.id == trade.account_id).first()
        
        return {
            "trade": TradeResponse(
                id=trade.id,
                account_name=account.name if account else "Unknown",
                stock_symbol=stock.symbol if stock else "Unknown",
                strategy_name=strategy.name if strategy else "Unknown",
                side=trade.side,
                quantity=trade.quantity,
                entry_price=float(trade.entry_price or 0),
                exit_price=float(trade.exit_price or 0) if trade.exit_price else None,
                net_pnl=float(trade.net_pnl or 0) if trade.net_pnl else None,
                status=trade.status,
                executed_at=trade.executed_at,
                closed_at=trade.closed_at,
                created_at=trade.created_at
            ),
            "stock_details": {
                "symbol": stock.symbol,
                "name": stock.name,
                "security_id": stock.security_id,
                "exchange": stock.exchange
            } if stock else None,
            "strategy_details": {
                "name": strategy.name,
                "description": strategy.description,
                "parameters": strategy.parameters
            } if strategy else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trade {trade_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching trade details")

# === MARKET DATA ENDPOINTS ===

@app.get("/api/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    timeframe: str = Query("5m", description="Timeframe (5m, 15m, 1h, daily)"),
    limit: int = Query(100, description="Number of candles", ge=1, le=1000)
):
    """Get market data for a specific symbol"""
    try:
        # This would integrate with your market_data_manager
        # For now, return a placeholder response
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "message": "Market data endpoint - integrate with EnhancedMarketDataManager",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching market data")

@app.get("/api/market-data/{symbol}/indicators")
async def get_technical_indicators(symbol: str):
    """Get technical indicators for a symbol"""
    try:
        return {
            "symbol": symbol.upper(),
            "indicators": {
                "vwap": {"current": 0, "signal": "HOLD"},
                "ema20": {"current": 0, "trend": "NEUTRAL"},
                "rsi": {"current": 50, "signal": "NEUTRAL"},
                "smc": {"order_blocks": [], "fvg": []}
            },
            "message": "Indicators endpoint - integrate with strategy calculations",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching indicators")

# === PORTFOLIO VISUALIZATION ENDPOINTS ===

@app.get("/api/portfolio/multi-asset-performance")
async def get_multi_asset_performance(
    days: int = Query(30, description="Number of days to fetch", ge=1, le=365),
    time_range: Optional[str] = Query(None, description="Time range filter (24h, 72h, all)"),
    db: Session = Depends(get_db)
):
    """
    Get multi-asset portfolio performance data for visualization
    Returns time-series data with total portfolio value and individual asset performance
    """
    try:
        # Calculate date range
        now = datetime.utcnow()

        # Apply time range filter
        if time_range == "24h":
            start_date = now - timedelta(hours=24)
        elif time_range == "72h":
            start_date = now - timedelta(hours=72)
        else:  # "all" or None
            start_date = now - timedelta(days=days)

        # Query portfolio snapshots with positions data
        snapshots = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.created_at >= start_date
        ).order_by(PortfolioSnapshot.created_at).all()

        if not snapshots:
            return {
                "timestamps": [],
                "total_value": [],
                "assets": {},
                "metadata": {
                    "start_date": start_date.isoformat(),
                    "end_date": now.isoformat(),
                    "data_points": 0
                }
            }

        # Process snapshots to extract multi-asset data
        timestamps = []
        total_values = []
        assets_data = {}  # {asset_symbol: [values]}

        for snapshot in snapshots:
            timestamps.append(snapshot.created_at.isoformat())
            total_values.append(float(snapshot.total_value))

            # Parse positions JSON to get individual asset values
            positions = json.loads(snapshot.positions or "[]")

            for position in positions:
                symbol = position.get("symbol", "UNKNOWN")
                # Calculate position value (quantity * current_price)
                quantity = position.get("quantity", 0)
                current_price = position.get("current_price", 0)
                position_value = quantity * current_price

                if symbol not in assets_data:
                    assets_data[symbol] = []

                assets_data[symbol].append(float(position_value))

        # Ensure all asset arrays have same length as timestamps
        # Fill missing values with 0 for assets that weren't held at certain times
        for symbol in assets_data:
            while len(assets_data[symbol]) < len(timestamps):
                assets_data[symbol].append(0.0)

        # Calculate statistics
        latest_value = total_values[-1] if total_values else 0
        first_value = total_values[0] if total_values else 0
        total_change = latest_value - first_value
        change_percentage = (total_change / first_value * 100) if first_value > 0 else 0

        return {
            "timestamps": timestamps,
            "total_value": total_values,
            "assets": assets_data,
            "metadata": {
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat(),
                "data_points": len(timestamps),
                "latest_value": latest_value,
                "first_value": first_value,
                "total_change": total_change,
                "change_percentage": change_percentage,
                "time_range": time_range or f"{days}d"
            }
        }

    except Exception as e:
        logger.error(f"Error fetching multi-asset performance: {e}")
        raise HTTPException(status_code=500, detail="Error fetching multi-asset performance data")

# === SYSTEM CONTROL ENDPOINTS ===

@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Get active accounts
        active_accounts = db.query(TradingAccount).filter(
            TradingAccount.is_active == True
        ).count()
        
        # Get today's trade count
        today = datetime.now().date()
        today_trades = db.query(Trade).filter(
            Trade.executed_at >= today
        ).count()
        
        # Check last invocation
        last_invocation = db.query(Invocation).order_by(
            desc(Invocation.created_at)
        ).first()
        
        return SystemStatusResponse(
            status="healthy",
            active_accounts=active_accounts,
            today_trades=today_trades,
            last_invocation=last_invocation.created_at if last_invocation else None,
            trading_enabled=settings.trading_enabled,
            market_open=_is_market_open(),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return SystemStatusResponse(
            status="unhealthy",
            error_message=str(e),
            timestamp=datetime.utcnow()
        )

@app.post("/api/system/start-trading")
async def start_trading():
    """Start automated trading (placeholder)"""
    return {
        "message": "Trading start command received",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/system/stop-trading")
async def stop_trading():
    """Stop automated trading (placeholder)"""
    return {
        "message": "Trading stop command received", 
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

# === ACCOUNTS ENDPOINTS ===

@app.get("/api/accounts")
async def get_accounts(db: Session = Depends(get_db)):
    """Get all trading accounts"""
    try:
        accounts = db.query(TradingAccount).filter(
            TradingAccount.is_active == True
        ).all()
        
        return [
            {
                "id": account.id,
                "name": account.name,
                "model_name": account.model_name,
                "capital_allocation": float(account.capital_allocation),
                "allocation_percentage": float(account.allocation_percentage),
                "invocation_count": account.invocation_count,
                "last_executed": account.last_executed.isoformat() if account.last_executed else None,
                "is_active": account.is_active
            }
            for account in accounts
        ]
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail="Error fetching accounts")

# === HEALTH CHECK ===

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Trading System - Indian Market",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# === HELPER FUNCTIONS ===

def _is_market_open() -> bool:
    """Check if Indian stock market is currently open"""
    now = datetime.now()
    
    # Check if it's a weekday (Monday=0, Friday=4)
    if now.weekday() > 4:  # Saturday=5, Sunday=6
        return False
    
    # Market hours: 9:15 AM to 3:30 PM
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_open <= now <= market_close

# === ERROR HANDLERS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )