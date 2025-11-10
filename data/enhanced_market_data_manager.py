"""
Enhanced Market Data Manager
Built on top of existing market_data_manager.py with additional features
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from market_data_manager import MarketDataManager  # Import existing class
from config.settings import INDIAN_STOCKS

logger = logging.getLogger(__name__)

class EnhancedMarketDataManager(MarketDataManager):
    """
    Enhanced version of the existing MarketDataManager
    Adds async support and additional features for the trading system
    """
    
    def __init__(self, symbols: Optional[List[str]] = None):
        # Use top 5 stocks if no symbols provided
        default_symbols = list(INDIAN_STOCKS.keys())
        super().__init__(symbols or default_symbols)
        
        # Additional caching for different timeframes
        self.cache_durations = {
            "1m": 60,      # 1 minute
            "5m": 300,     # 5 minutes - always fresh
            "15m": 900,    # 15 minutes
            "1h": 3600,    # 1 hour
            "daily": 86400 # 24 hours
        }
        
        # Enhanced cache storage
        self.enhanced_cache = {}
        
    async def initialize(self):
        """Initialize the enhanced data manager"""
        logger.info("Initializing Enhanced Market Data Manager")
        
        # Test connection to Dhan API
        try:
            test_data = await self.get_current_price("RELIANCE")
            if test_data:
                logger.info("Dhan API connection successful")
            else:
                logger.warning("Dhan API connection test returned empty data")
        except Exception as e:
            logger.error(f"Dhan API connection failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the data manager"""
        logger.info("Enhanced Market Data Manager shutdown")
    
    async def get_timeframe_data(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Get market data for a specific timeframe with async support
        """
        try:
            if timeframe == "5m":
                return await self._async_wrapper(self.get_5min_data, symbol)
            elif timeframe == "15m":
                return await self._async_wrapper(self.get_15min_data, symbol)
            elif timeframe == "1h":
                return await self._async_wrapper(self.get_1h_data, symbol)
            elif timeframe == "daily":
                return await self._async_wrapper(self.get_daily_data, symbol)
            else:
                raise ValueError(f"Unsupported timeframe: {timeframe}")
                
        except Exception as e:
            logger.error(f"Error getting {timeframe} data for {symbol}: {e}")
            return {}
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        try:
            # Get latest 5-minute data
            data = await self.get_timeframe_data(symbol, "5m")
            if data and "close" in data and data["close"]:
                return float(data["close"][-1])  # Latest close price
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return 0.0
    
    async def get_all_timeframes(self, symbol: str) -> Dict[str, Any]:
        """
        Get data for all timeframes for a symbol
        Equivalent to crypto system's comprehensive data collection
        """
        try:
            timeframes = ["5m", "15m", "1h", "daily"]
            data = {}
            
            # Fetch all timeframes concurrently
            tasks = [
                self.get_timeframe_data(symbol, tf) for tf in timeframes
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for tf, result in zip(timeframes, results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {tf} data for {symbol}: {result}")
                    data[tf] = {}
                else:
                    data[tf] = result
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting all timeframes for {symbol}: {e}")
            return {}
    
    async def get_multiple_symbols_data(
        self, 
        symbols: List[str], 
        timeframes: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get market data for multiple symbols and timeframes
        Optimized for the trading engine's data collection needs
        """
        if not timeframes:
            timeframes = ["5m", "15m", "1h", "daily"]
        
        try:
            all_data = {}
            
            # Create tasks for all symbol-timeframe combinations
            tasks = []
            task_mapping = []
            
            for symbol in symbols:
                for timeframe in timeframes:
                    tasks.append(self.get_timeframe_data(symbol, timeframe))
                    task_mapping.append((symbol, timeframe))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Organize results
            for (symbol, timeframe), result in zip(task_mapping, results):
                if symbol not in all_data:
                    all_data[symbol] = {}
                
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {timeframe} data for {symbol}: {result}")
                    all_data[symbol][timeframe] = {}
                else:
                    all_data[symbol][timeframe] = result
            
            return all_data
            
        except Exception as e:
            logger.error(f"Error getting multiple symbols data: {e}")
            return {}
    
    async def format_for_llm(
        self, 
        data: Dict[str, Any], 
        format_type: str = "detailed"
    ) -> str:
        """
        Format market data for LLM consumption
        Supports both 'detailed' and 'toon' formats from the original system
        """
        try:
            if format_type == "toon":
                return await self._format_toon(data)
            else:
                return await self._format_detailed(data)
                
        except Exception as e:
            logger.error(f"Error formatting data for LLM: {e}")
            return "Error formatting market data"
    
    async def _format_toon(self, data: Dict[str, Any]) -> str:
        """
        Format data in TOON (Token-Oriented Object Notation) format
        84% fewer tokens as mentioned in the original system
        """
        toon_data = []
        
        for symbol, timeframes in data.items():
            symbol_data = f"{symbol}:"
            
            for tf, tf_data in timeframes.items():
                if tf_data and "close" in tf_data and tf_data["close"]:
                    # Get last 5 prices
                    prices = tf_data["close"][-5:]
                    symbol_data += f"{tf}[{','.join(map(str, prices))}]"
            
            toon_data.append(symbol_data)
        
        return "|".join(toon_data)
    
    async def _format_detailed(self, data: Dict[str, Any]) -> str:
        """Format data in detailed readable format"""
        formatted_lines = []
        
        for symbol, timeframes in data.items():
            formatted_lines.append(f"\n=== {symbol} ===")
            
            for tf, tf_data in timeframes.items():
                if tf_data and "close" in tf_data and tf_data["close"]:
                    prices = tf_data["close"][-10:]  # Last 10 prices
                    volumes = tf_data.get("volume", [])[-10:] if tf_data.get("volume") else []
                    
                    formatted_lines.append(f"{tf} timeframe (latest):")
                    formatted_lines.append(f"  Prices: {prices}")
                    if volumes:
                        formatted_lines.append(f"  Volumes: {volumes}")
        
        return "\n".join(formatted_lines)
    
    async def _async_wrapper(self, sync_func, *args, **kwargs):
        """
        Wrapper to run synchronous methods asynchronously
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_func, *args, **kwargs)
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status information"""
        try:
            status = {
                "daily_cache": {
                    "size": len(self.daily_cache),
                    "last_updated": self.daily_cache_date.isoformat() if self.daily_cache_date else None
                },
                "hourly_cache": {
                    "size": len(self.hourly_cache),
                    "last_updated": self.hourly_cache_time.isoformat() if self.hourly_cache_time else None
                },
                "min_15_cache": {
                    "size": len(self.min_15_cache),
                    "last_updated": self.min_15_cache_time.isoformat() if self.min_15_cache_time else None
                },
                "symbols": self.symbols,
                "timestamp": datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return {"error": str(e)}
    
    async def warm_cache(self) -> bool:
        """Pre-load cache with data for all symbols and timeframes"""
        try:
            logger.info("Warming cache for all symbols and timeframes")
            
            # Get data for all symbols and timeframes
            await self.get_multiple_symbols_data(self.symbols)
            
            logger.info("Cache warming completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error warming cache: {e}")
            return False