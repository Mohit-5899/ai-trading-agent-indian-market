#!/usr/bin/env python3
"""
AI Trading System - Indian Market
Main application entry point
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.main import app as api_app
from core.trading_engine import TradingEngine
from config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/trading_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TradingSystemManager:
    """Main application manager"""
    
    def __init__(self):
        self.settings = get_settings()
        self.trading_engine = None
        self.trading_task = None
        self.running = False
        
    async def startup(self):
        """Initialize the trading system"""
        logger.info("Starting AI Trading System - Indian Market")
        
        # Initialize trading engine
        self.trading_engine = TradingEngine()
        await self.trading_engine.initialize()
        
        # Start trading loop if enabled
        if self.settings.trading_enabled:
            await self.start_trading()
        
        logger.info("Trading system initialized successfully")
        
    async def start_trading(self):
        """Start the automated trading loop"""
        if self.trading_task and not self.trading_task.done():
            logger.warning("Trading loop already running")
            return
            
        logger.info("Starting automated trading loop")
        self.running = True
        self.trading_task = asyncio.create_task(self._trading_loop())
        
    async def stop_trading(self):
        """Stop the automated trading loop"""
        logger.info("Stopping automated trading loop")
        self.running = False
        
        if self.trading_task:
            self.trading_task.cancel()
            try:
                await self.trading_task
            except asyncio.CancelledError:
                pass
                
    async def shutdown(self):
        """Shutdown the trading system"""
        logger.info("Shutting down trading system")
        
        await self.stop_trading()
        
        if self.trading_engine:
            await self.trading_engine.shutdown()
            
        logger.info("Trading system shutdown complete")
        
    async def _trading_loop(self):
        """Main trading loop - runs every 5 minutes"""
        while self.running:
            try:
                logger.info("Executing trading cycle")
                
                # Get all active trading accounts
                accounts = await self.trading_engine.get_active_accounts()
                
                # Process each account
                for account in accounts:
                    try:
                        await self.trading_engine.process_account(account)
                        logger.info(f"Processed account: {account.name}")
                    except Exception as e:
                        logger.error(f"Error processing account {account.name}: {e}")
                        
                logger.info("Trading cycle completed")
                
                # Wait 5 minutes before next cycle
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                logger.info("Trading loop cancelled")
                break
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

# Global manager instance
trading_manager = TradingSystemManager()

# FastAPI app events
@api_app.on_event("startup")
async def startup_event():
    await trading_manager.startup()

@api_app.on_event("shutdown") 
async def shutdown_event():
    await trading_manager.shutdown()

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating shutdown")
    asyncio.create_task(trading_manager.shutdown())
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    settings = get_settings()
    
    # Run FastAPI server
    uvicorn.run(
        "main:api_app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )