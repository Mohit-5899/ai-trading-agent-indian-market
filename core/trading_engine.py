"""
Core Trading Engine
Main orchestrator for the AI trading system - equivalent to crypto system's index.ts
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from models.database import (
    TradingAccount, Stock, Strategy, Invocation, Trade, 
    TradingSignal, PortfolioSnapshot, ToolCall,
    create_database_engine, create_session_factory
)
from data.enhanced_market_data_manager import EnhancedMarketDataManager
from data.dhan_client import DhanClient
from core.llm_manager import LLMManager
from core.risk_manager import RiskManager
from strategies.strategy_factory import StrategyFactory
from config.settings import get_settings

logger = logging.getLogger(__name__)

class TradingEngine:
    """
    Main trading engine - equivalent to crypto system's main orchestrator
    Processes all accounts every 5 minutes with LLM decision making
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.session_factory = None
        
        # Core components
        self.market_data_manager = None
        self.dhan_client = None
        self.llm_manager = None
        self.risk_manager = None
        self.strategy_factory = None
        
        # State
        self.is_initialized = False
        self.active_accounts = []
        
    async def initialize(self):
        """Initialize the trading engine"""
        if self.is_initialized:
            return
            
        logger.info("Initializing trading engine")
        
        try:
            # Setup database
            self.engine = create_database_engine(self.settings.database_url)
            self.session_factory = create_session_factory(self.engine)
            
            # Initialize components
            self.market_data_manager = EnhancedMarketDataManager()
            self.dhan_client = DhanClient()
            self.llm_manager = LLMManager()
            self.risk_manager = RiskManager()
            self.strategy_factory = StrategyFactory()
            
            # Initialize subcomponents
            await self.market_data_manager.initialize()
            await self.dhan_client.initialize()
            await self.llm_manager.initialize()
            
            # Load initial data
            await self._load_initial_data()
            
            self.is_initialized = True
            logger.info("Trading engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize trading engine: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the trading engine"""
        logger.info("Shutting down trading engine")
        
        if self.market_data_manager:
            await self.market_data_manager.shutdown()
        if self.dhan_client:
            await self.dhan_client.shutdown()
        if self.llm_manager:
            await self.llm_manager.shutdown()
            
        self.is_initialized = False
        logger.info("Trading engine shutdown complete")
    
    async def get_active_accounts(self) -> List[TradingAccount]:
        """Get all active trading accounts"""
        session = self.session_factory()
        try:
            accounts = session.query(TradingAccount).filter(
                TradingAccount.is_active == True
            ).all()
            
            self.active_accounts = accounts
            return accounts
            
        except Exception as e:
            logger.error(f"Error fetching active accounts: {e}")
            return []
        finally:
            session.close()
    
    async def process_account(self, account: TradingAccount):
        """
        Process a single trading account - equivalent to crypto system's invokeAgent()
        This is the core function that runs every 5 minutes per account
        """
        logger.info(f"Processing account: {account.name}")
        
        session = self.session_factory()
        try:
            # 1. Check market hours
            if not self._is_market_open():
                logger.info(f"Market closed, skipping account {account.name}")
                return
                
            # 2. Check if account is within daily limits
            if not await self._check_daily_limits(session, account):
                logger.warning(f"Daily limits exceeded for account {account.name}")
                return
            
            # 3. Collect market data for all stocks
            market_context = await self._collect_market_data(account)
            
            # 4. Get current portfolio and positions
            portfolio_context = await self._get_portfolio_context(session, account)
            
            # 5. Create LLM invocation record
            invocation = await self._create_invocation_record(
                session, account, market_context, portfolio_context
            )
            
            # 6. Generate enriched prompt (like crypto system)
            enriched_prompt = await self._create_enriched_prompt(
                account, market_context, portfolio_context, invocation
            )
            
            # 7. Get LLM decision with tool calling
            llm_response = await self._get_llm_decision(
                account, enriched_prompt, invocation, session
            )
            
            # 8. Update invocation record with response
            await self._update_invocation_record(session, invocation, llm_response)
            
            # 9. Update account invocation count
            account.invocation_count += 1
            account.last_executed = datetime.utcnow()
            session.commit()
            
            logger.info(f"Successfully processed account {account.name}")
            
        except Exception as e:
            logger.error(f"Error processing account {account.name}: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    async def _collect_market_data(self, account: TradingAccount) -> Dict[str, Any]:
        """Collect market data for all stocks - equivalent to crypto system's indicator collection"""
        logger.debug(f"Collecting market data for account {account.name}")
        
        # Get stocks assigned to this account (based on LLM model)
        stocks = await self._get_account_stocks(account)
        
        market_data = {}
        
        for stock in stocks:
            try:
                # Collect multi-timeframe data
                stock_data = {
                    "symbol": stock.symbol,
                    "security_id": stock.security_id,
                    "timeframes": {}
                }
                
                # Get different timeframes (like crypto system's 5m and 4h)
                timeframes = ["5m", "15m", "1h", "daily"]
                for tf in timeframes:
                    tf_data = await self.market_data_manager.get_timeframe_data(stock.symbol, tf)
                    stock_data["timeframes"][tf] = tf_data
                
                # Calculate technical indicators for each timeframe
                stock_data["indicators"] = await self._calculate_indicators(stock_data)
                
                # Generate strategy signals
                stock_data["signals"] = await self._generate_strategy_signals(
                    account, stock, stock_data
                )
                
                market_data[stock.symbol] = stock_data
                
            except Exception as e:
                logger.error(f"Error collecting data for {stock.symbol}: {e}")
                continue
        
        return market_data
    
    async def _get_portfolio_context(self, session: Session, account: TradingAccount) -> Dict[str, Any]:
        """Get current portfolio context - equivalent to crypto system's portfolio data"""
        try:
            # Get current portfolio from Dhan
            dhan_portfolio = await self.dhan_client.get_portfolio(account)
            
            # Get current positions
            current_positions = await self.dhan_client.get_positions(account)
            
            # Get open trades from database
            open_trades = session.query(Trade).filter(
                Trade.account_id == account.id,
                Trade.status == "OPEN"
            ).all()
            
            # Calculate portfolio metrics
            portfolio_context = {
                "total_value": float(dhan_portfolio.get("total_value", 0)),
                "available_cash": float(dhan_portfolio.get("available_cash", 0)),
                "invested_amount": float(dhan_portfolio.get("invested_amount", 0)),
                "day_pnl": float(dhan_portfolio.get("day_pnl", 0)),
                "positions": [
                    {
                        "symbol": pos.get("symbol"),
                        "quantity": pos.get("quantity"),
                        "current_price": pos.get("current_price"),
                        "pnl": pos.get("pnl")
                    }
                    for pos in current_positions
                ],
                "open_trades_count": len(open_trades),
                "allocated_capital": float(account.capital_allocation)
            }
            
            return portfolio_context
            
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            return {
                "total_value": 0,
                "available_cash": 0,
                "invested_amount": 0,
                "day_pnl": 0,
                "positions": [],
                "open_trades_count": 0,
                "allocated_capital": float(account.capital_allocation)
            }
    
    async def _create_enriched_prompt(
        self, 
        account: TradingAccount, 
        market_context: Dict[str, Any], 
        portfolio_context: Dict[str, Any],
        invocation: Invocation
    ) -> str:
        """
        Create enriched prompt with market data and portfolio context
        Equivalent to crypto system's prompt enrichment
        """
        
        # Format market data for LLM (similar to crypto system's ALL_INDICATOR_DATA)
        market_data_text = ""
        for symbol, data in market_context.items():
            market_data_text += f"\n=== {symbol} ===\n"
            
            # Add timeframe data
            for tf, tf_data in data["timeframes"].items():
                if tf_data and len(tf_data.get("close", [])) > 0:
                    prices = tf_data["close"][-10:]  # Last 10 prices
                    market_data_text += f"{tf} timeframe (oldest → latest):\n"
                    market_data_text += f"  Prices: [{', '.join(map(str, prices))}]\n"
            
            # Add indicators
            indicators = data.get("indicators", {})
            for indicator, values in indicators.items():
                if values and len(values) > 0:
                    recent_values = values[-5:]  # Last 5 values
                    market_data_text += f"  {indicator}: [{', '.join(map(str, recent_values))}]\n"
            
            # Add signals
            signals = data.get("signals", {})
            if signals:
                market_data_text += f"  Signals: {json.dumps(signals)}\n"
        
        # Format positions
        positions_text = ""
        if portfolio_context["positions"]:
            positions_text = ", ".join([
                f"{pos['symbol']} {pos['quantity']}@{pos['current_price']} (P&L: {pos['pnl']})"
                for pos in portfolio_context["positions"]
            ])
        else:
            positions_text = "No open positions"
        
        # Create the enriched prompt (similar to crypto system's PROMPT template)
        prompt = f"""
You are an expert trader managing Indian stock market investments. 
You have been given ₹{portfolio_context['allocated_capital']:,.0f} to trade with.

ACCOUNT STATUS:
- This is invocation #{account.invocation_count + 1} for account '{account.name}'
- Current portfolio value: ₹{portfolio_context['total_value']:,.2f}
- Available cash: ₹{portfolio_context['available_cash']:,.2f}
- Day P&L: ₹{portfolio_context['day_pnl']:,.2f}
- Open positions: {positions_text}
- Number of open trades: {portfolio_context['open_trades_count']}

TRADING CAPABILITIES:
You can use these tools:
1. buy_stock(symbol, quantity, strategy) - Buy shares of a stock
2. sell_stock(symbol, quantity, strategy) - Sell shares of a stock  
3. close_all_positions() - Close all open positions
4. get_portfolio_status() - Get current portfolio details

RISK MANAGEMENT RULES:
- Risk only {account.risk_per_trade}% of capital per trade
- Maximum {account.max_positions} simultaneous positions
- Indian market hours: 9:15 AM - 3:30 PM
- All prices in Indian Rupees (₹)

MARKET DATA (All data ordered: OLDEST → LATEST):
{market_data_text}

INSTRUCTIONS:
Analyze the market data and make trading decisions based on:
1. VWAP breakout/retest patterns (proven 39.74% return strategy)
2. EMA crossover signals
3. RSI mean reversion opportunities  
4. Smart Money Concepts (order blocks, fair value gaps)

Consider the current portfolio state and risk management rules.
Make ONE trading decision or choose to hold.
"""
        
        return prompt.strip()
    
    async def _get_llm_decision(
        self,
        account: TradingAccount,
        prompt: str, 
        invocation: Invocation,
        session: Session
    ) -> Dict[str, Any]:
        """Get LLM decision with tool calling"""
        try:
            # Create trading tools for this account
            trading_tools = self._create_trading_tools(account, invocation, session)
            
            # Get LLM response with tool calling
            llm_response = await self.llm_manager.get_decision_with_tools(
                model_name=account.model_name,
                prompt=prompt,
                tools=trading_tools,
                account=account
            )
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Error getting LLM decision: {e}")
            return {
                "response": f"Error: {str(e)}",
                "tool_calls": [],
                "tokens_used": 0,
                "execution_time_ms": 0
            }
    
    def _create_trading_tools(self, account: TradingAccount, invocation: Invocation, session: Session):
        """Create trading tools for LLM - equivalent to crypto system's tools"""
        
        async def buy_stock_tool(symbol: str, quantity: int, strategy: str):
            """Buy stock tool"""
            try:
                result = await self._execute_buy_order(
                    account, symbol, quantity, strategy, invocation, session
                )
                
                # Log tool call
                await self._log_tool_call(
                    session, invocation, "buy_stock",
                    {"symbol": symbol, "quantity": quantity, "strategy": strategy},
                    result, "SUCCESS"
                )
                
                return f"Successfully bought {quantity} shares of {symbol} using {strategy} strategy"
                
            except Exception as e:
                # Log failed tool call
                await self._log_tool_call(
                    session, invocation, "buy_stock",
                    {"symbol": symbol, "quantity": quantity, "strategy": strategy},
                    str(e), "FAILED"
                )
                return f"Error buying {symbol}: {str(e)}"
        
        async def sell_stock_tool(symbol: str, quantity: int, strategy: str):
            """Sell stock tool"""
            try:
                result = await self._execute_sell_order(
                    account, symbol, quantity, strategy, invocation, session
                )
                
                await self._log_tool_call(
                    session, invocation, "sell_stock",
                    {"symbol": symbol, "quantity": quantity, "strategy": strategy},
                    result, "SUCCESS"
                )
                
                return f"Successfully sold {quantity} shares of {symbol}"
                
            except Exception as e:
                await self._log_tool_call(
                    session, invocation, "sell_stock",
                    {"symbol": symbol, "quantity": quantity, "strategy": strategy},
                    str(e), "FAILED"
                )
                return f"Error selling {symbol}: {str(e)}"
        
        async def close_all_positions_tool():
            """Close all positions tool - equivalent to crypto system's closeAllPosition"""
            try:
                result = await self._close_all_positions(account, invocation, session)
                
                await self._log_tool_call(
                    session, invocation, "close_all_positions", {}, result, "SUCCESS"
                )
                
                return "Successfully closed all positions"
                
            except Exception as e:
                await self._log_tool_call(
                    session, invocation, "close_all_positions", {}, str(e), "FAILED"
                )
                return f"Error closing positions: {str(e)}"
        
        async def get_portfolio_status_tool():
            """Get portfolio status tool"""
            try:
                portfolio = await self._get_portfolio_context(session, account)
                return json.dumps(portfolio, indent=2)
            except Exception as e:
                return f"Error getting portfolio: {str(e)}"
        
        return {
            "buy_stock": buy_stock_tool,
            "sell_stock": sell_stock_tool, 
            "close_all_positions": close_all_positions_tool,
            "get_portfolio_status": get_portfolio_status_tool
        }
    
    async def _execute_buy_order(
        self, account: TradingAccount, symbol: str, quantity: int, 
        strategy: str, invocation: Invocation, session: Session
    ):
        """Execute buy order through Dhan API"""
        
        # Validate order through risk manager
        await self.risk_manager.validate_order(account, symbol, quantity, "BUY")
        
        # Get current price
        current_price = await self.market_data_manager.get_current_price(symbol)
        
        # Calculate position size based on risk management
        validated_quantity = await self.risk_manager.calculate_position_size(
            account, current_price, quantity
        )
        
        # Execute order through Dhan API
        order_result = await self.dhan_client.place_buy_order(
            account, symbol, validated_quantity
        )
        
        # Create trade record
        trade = Trade(
            account_id=account.id,
            stock_id=await self._get_stock_id(session, symbol),
            strategy_id=await self._get_strategy_id(session, strategy),
            dhan_order_id=order_result.get("order_id"),
            side="BUY",
            quantity=validated_quantity,
            entry_price=current_price,
            status="OPEN",
            executed_at=datetime.utcnow()
        )
        
        session.add(trade)
        session.commit()
        
        return order_result
    
    # Helper methods
    async def _is_market_open(self) -> bool:
        """Check if Indian market is open"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # Check if it's a weekday and within market hours
        return (
            now.weekday() < 5 and  # Monday=0, Friday=4
            market_open <= now <= market_close
        )
    
    async def _check_daily_limits(self, session: Session, account: TradingAccount) -> bool:
        """Check if account has exceeded daily trading limits"""
        today = datetime.now().date()
        
        # Check daily loss limit (e.g., 10% of capital)
        daily_trades = session.query(Trade).filter(
            Trade.account_id == account.id,
            Trade.executed_at >= today
        ).all()
        
        daily_loss = sum(float(trade.net_pnl or 0) for trade in daily_trades if trade.net_pnl and trade.net_pnl < 0)
        max_daily_loss = float(account.capital_allocation) * 0.1  # 10% daily loss limit
        
        if abs(daily_loss) > max_daily_loss:
            logger.warning(f"Daily loss limit exceeded for {account.name}: {daily_loss}")
            return False
        
        return True
    
    async def _load_initial_data(self):
        """Load initial stocks and strategies data"""
        session = self.session_factory()
        try:
            # Create initial stocks if they don't exist
            stocks_data = [
                {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "security_id": "2885"},
                {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "security_id": "11536"},
                {"symbol": "INFY", "name": "Infosys Ltd", "security_id": "1594"},
                {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "security_id": "1333"},
                {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "security_id": "4963"}
            ]
            
            for stock_data in stocks_data:
                existing_stock = session.query(Stock).filter(
                    Stock.symbol == stock_data["symbol"]
                ).first()
                
                if not existing_stock:
                    stock = Stock(**stock_data)
                    session.add(stock)
            
            # Create initial strategies
            strategies_data = [
                {"name": "vwap", "description": "VWAP Breakout/Retest Strategy"},
                {"name": "ema", "description": "EMA Crossover Strategy"},
                {"name": "rsi", "description": "RSI Mean Reversion Strategy"},
                {"name": "smc", "description": "Smart Money Concepts Strategy"}
            ]
            
            for strategy_data in strategies_data:
                existing_strategy = session.query(Strategy).filter(
                    Strategy.name == strategy_data["name"]
                ).first()
                
                if not existing_strategy:
                    strategy = Strategy(**strategy_data)
                    session.add(strategy)
            
            session.commit()
            logger.info("Initial data loaded successfully")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading initial data: {e}")
            raise
        finally:
            session.close()
    
    # Additional helper methods would be implemented here...