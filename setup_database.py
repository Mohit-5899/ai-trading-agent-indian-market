#!/usr/bin/env python3
"""
Database Setup Script
Creates database tables and populates initial data
"""

import asyncio
import logging
from sqlalchemy import create_engine
from models.database import Base, create_tables, TradingAccount, Stock, Strategy
from config.settings import get_settings, INDIAN_STOCKS, LLM_MODELS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """Setup database with initial data"""
    settings = get_settings()
    
    try:
        # Create database engine
        engine = create_engine(settings.database_url)
        
        # Create all tables
        logger.info("Creating database tables...")
        create_tables(engine)
        
        # Create session
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Create initial stocks
            logger.info("Creating initial stock data...")
            for symbol, stock_info in INDIAN_STOCKS.items():
                existing_stock = session.query(Stock).filter(Stock.symbol == symbol).first()
                if not existing_stock:
                    stock = Stock(
                        symbol=symbol,
                        name=stock_info['name'],
                        security_id=stock_info['security_id'],
                        exchange=stock_info['exchange'],
                        lot_size=stock_info['lot_size'],
                        tick_size=stock_info['tick_size']
                    )
                    session.add(stock)
                    logger.info(f"Created stock: {symbol}")
            
            # Create initial strategies
            logger.info("Creating initial strategy data...")
            strategies_data = [
                {"name": "vwap", "description": "VWAP Breakout/Retest Strategy - Proven 39.74% return"},
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
                    logger.info(f"Created strategy: {strategy_data['name']}")
            
            # Create sample trading accounts (you'll need to update with real credentials)
            logger.info("Creating sample trading accounts...")
            sample_accounts = [
                {
                    "name": "Primary_LLM_Account",
                    "model_name": "claude-3-5-sonnet",
                    "dhan_client_id": "SAMPLE_CLIENT_ID_1",
                    "dhan_access_token": "SAMPLE_TOKEN_1",
                    "account_id": "SAMPLE_ACCOUNT_1", 
                    "capital_allocation": 60000.00,  # 60% of 100k
                    "allocation_percentage": 60.0,
                    "risk_per_trade": 2.0,
                    "max_positions": 3
                },
                {
                    "name": "Secondary_LLM_Account", 
                    "model_name": "gpt-4-turbo",
                    "dhan_client_id": "SAMPLE_CLIENT_ID_2",
                    "dhan_access_token": "SAMPLE_TOKEN_2", 
                    "account_id": "SAMPLE_ACCOUNT_2",
                    "capital_allocation": 40000.00,  # 40% of 100k
                    "allocation_percentage": 40.0,
                    "risk_per_trade": 2.0,
                    "max_positions": 2
                }
            ]
            
            for account_data in sample_accounts:
                existing_account = session.query(TradingAccount).filter(
                    TradingAccount.name == account_data["name"]
                ).first()
                if not existing_account:
                    account = TradingAccount(**account_data)
                    session.add(account)
                    logger.info(f"Created trading account: {account_data['name']}")
            
            # Commit all changes
            session.commit()
            logger.info("Database setup completed successfully!")
            
            # Print summary
            stocks_count = session.query(Stock).count()
            strategies_count = session.query(Strategy).count()
            accounts_count = session.query(TradingAccount).count()
            
            logger.info(f"Database summary:")
            logger.info(f"  - Stocks: {stocks_count}")
            logger.info(f"  - Strategies: {strategies_count}")
            logger.info(f"  - Trading Accounts: {accounts_count}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error setting up database: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    print("Setting up AI Trading System Database...")
    print("Make sure you have:")
    print("1. PostgreSQL running")
    print("2. Database created")
    print("3. Correct DATABASE_URL in .env file")
    print()
    
    confirm = input("Continue with database setup? (y/N): ")
    if confirm.lower() == 'y':
        asyncio.run(setup_database())
    else:
        print("Database setup cancelled.")