import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from dhanhq import dhanhq
import time

load_dotenv()

class MarketDataManager:
    """
    Manages multi-timeframe market data with intelligent caching
    - Daily: Cache for entire day
    - 1-hour: Cache for 60 minutes
    - 15-minute: Cache for 15 minutes
    - 5-minute: Fetch fresh every time
    """
    
    MARKET_OPEN = "09:15"
    MARKET_CLOSE = "15:30"
    
    def __init__(self, symbols: List[str], env_path: str = None):
        if env_path:
            load_dotenv(env_path)
        self.client_id = os.getenv("DHAN_CLIENT_ID")
        self.access_token = os.getenv("DHAN_ACCESS_TOKEN")
        self.dhan = dhanhq(self.client_id, self.access_token)
        self.symbols = symbols
        
        self.security_ids = {
            "RELIANCE": "2885",
            "TCS": "11536",
            "INFY": "1594",
            "HDFCBANK": "1333",
            "ICICIBANK": "4963",
            "SBIN": "3045",
            "BHARTIARTL": "3677",
            "ITC": "1660",
            "LT": "11483",
            "HINDUNILVR": "1394"
        }
        
        self.daily_cache = {}
        self.daily_cache_date = None
        
        self.hourly_cache = {}
        self.hourly_cache_time = None
        
        self.min_15_cache = {}
        self.min_15_cache_time = None
        
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        if now.weekday() >= 5:
            return False
        
        current_time = now.strftime("%H:%M")
        return self.MARKET_OPEN <= current_time <= self.MARKET_CLOSE
    
    def get_daily_data(self, symbol: str, days: int = 7) -> Optional[Dict]:
        """
        Fetch daily candles (last 7 days)
        Cached for entire day - fetched once at market open
        """
        today = datetime.now().date()
        
        if self.daily_cache_date == today and symbol in self.daily_cache:
            print(f"[CACHE HIT] Daily data for {symbol}")
            return self.daily_cache[symbol]
        
        print(f"[FETCHING] Daily data for {symbol}")
        
        security_id = self.security_ids.get(symbol)
        if not security_id:
            return None
        
        now = datetime.now()
        if now.weekday() >= 5:
            last_trading_day = now - timedelta(days=(now.weekday() - 4))
            to_date = last_trading_day.strftime("%Y-%m-%d")
        else:
            to_date = now.strftime("%Y-%m-%d")
        
        from_date = (datetime.now() - timedelta(days=days + 2)).strftime("%Y-%m-%d")
        
        try:
            response = self.dhan.historical_daily_data(
                security_id=security_id,
                exchange_segment="NSE_EQ",
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date
            )
            
            if response and response.get('status') == 'success':
                data = response.get('data', {})
                
                if self.daily_cache_date != today:
                    self.daily_cache = {}
                    self.daily_cache_date = today
                
                self.daily_cache[symbol] = data
                return data
            else:
                print(f"API Error for {symbol}: {response}")
        except Exception as e:
            print(f"Exception fetching daily data for {symbol}: {e}")
        
        return None
    
    def get_hourly_data(self, symbol: str, days: int = 7) -> Optional[Dict]:
        """
        Fetch 1-hour candles (last 7 days from 15-min data aggregated)
        Cached for 60 minutes
        """
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        cache_key = f"{symbol}_{current_hour}"
        
        if self.hourly_cache_time == current_hour and symbol in self.hourly_cache:
            print(f"[CACHE HIT] Hourly data for {symbol}")
            return self.hourly_cache[symbol]
        
        print(f"[FETCHING] Hourly data for {symbol} (using 60-min interval)")
        
        security_id = self.security_ids.get(symbol)
        if not security_id:
            return None
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            response = self.dhan.intraday_minute_data(
                security_id=security_id,
                exchange_segment="NSE_EQ",
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date,
                interval=60
            )
            
            if response and response.get('status') == 'success':
                data = response.get('data', {})
                
                if self.hourly_cache_time != current_hour:
                    self.hourly_cache = {}
                    self.hourly_cache_time = current_hour
                
                self.hourly_cache[symbol] = data
                return data
        except Exception as e:
            print(f"Error fetching hourly data for {symbol}: {e}")
        
        return None
    
    def get_15min_data(self, symbol: str, days: int = 3) -> Optional[Dict]:
        """
        Fetch 15-minute candles (last 3 days)
        Cached for 15 minutes
        """
        now = datetime.now()
        current_15min = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)
        
        if self.min_15_cache_time == current_15min and symbol in self.min_15_cache:
            print(f"[CACHE HIT] 15-min data for {symbol}")
            return self.min_15_cache[symbol]
        
        print(f"[FETCHING] 15-min data for {symbol}")
        
        security_id = self.security_ids.get(symbol)
        if not security_id:
            return None
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            response = self.dhan.intraday_minute_data(
                security_id=security_id,
                exchange_segment="NSE_EQ",
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date,
                interval=15
            )
            
            if response and response.get('status') == 'success':
                data = response.get('data', {})
                
                if self.min_15_cache_time != current_15min:
                    self.min_15_cache = {}
                    self.min_15_cache_time = current_15min
                
                self.min_15_cache[symbol] = data
                return data
        except Exception as e:
            print(f"Error fetching 15-min data for {symbol}: {e}")
        
        return None
    
    def get_5min_data(self, symbol: str, days: int = 3) -> Optional[Dict]:
        """
        Fetch 5-minute candles (last 3 days)
        Always fetched fresh - no caching
        """
        print(f"[FETCHING] 5-min data for {symbol} (always fresh)")
        
        security_id = self.security_ids.get(symbol)
        if not security_id:
            return None
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            response = self.dhan.intraday_minute_data(
                security_id=security_id,
                exchange_segment="NSE_EQ",
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date,
                interval=5
            )
            
            if response and response.get('status') == 'success':
                return response.get('data', {})
        except Exception as e:
            print(f"Error fetching 5-min data for {symbol}: {e}")
        
        return None
    
    def get_all_timeframes(self, symbol: str) -> Dict:
        """
        Get data for all timeframes with intelligent caching
        Returns structured data ready for LLM context
        """
        print(f"\n{'='*60}")
        print(f"Fetching multi-timeframe data for {symbol}")
        print(f"{'='*60}")
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'daily': self.get_daily_data(symbol, days=7),
            'hourly': self.get_hourly_data(symbol, days=7),
            'min_15': self.get_15min_data(symbol, days=3),
            'min_5': self.get_5min_data(symbol, days=3)
        }
        
        return result
    
    def format_for_llm(self, data: Dict, format_type: str = "toon") -> str:
        """
        Format multi-timeframe data into LLM-friendly context
        - Daily: ALL candles
        - Hourly: ALL candles
        - 15-min: ALL candles
        - 5-min: Last 20 candles only
        
        Args:
            format_type: "toon" (compact, 50% fewer tokens) or "readable" (human-friendly)
        """
        if format_type == "toon":
            return self._format_toon(data)
        else:
            return self._format_readable(data)
    
    def _format_toon(self, data: Dict) -> str:
        """
        TOON format - Token-Oriented Object Notation
        Optimized for LLMs: 40-50% fewer tokens, better accuracy
        """
        symbol = data['symbol']
        context = f"MARKET_DATA[{symbol}]@{data['timestamp']}\n\n"
        
        daily = data.get('daily', {})
        if daily and daily.get('timestamp'):
            timestamps = daily['timestamp']
            count = len(timestamps)
            context += f"daily[{count}]{{date,open,high,low,close,volume}}:\n"
            
            for i in range(count):
                date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                context += f" {date},{daily['open'][i]:.2f},{daily['high'][i]:.2f},{daily['low'][i]:.2f},{daily['close'][i]:.2f},{daily['volume'][i]:.0f}\n"
        
        hourly = data.get('hourly', {})
        if hourly and hourly.get('timestamp'):
            timestamps = hourly['timestamp']
            count = len(timestamps)
            context += f"\nhourly[{count}]{{datetime,open,high,low,close,volume}}:\n"
            
            for i in range(count):
                dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
                context += f" {dt},{hourly['open'][i]:.2f},{hourly['high'][i]:.2f},{hourly['low'][i]:.2f},{hourly['close'][i]:.2f},{hourly['volume'][i]:.0f}\n"
        
        min_15 = data.get('min_15', {})
        if min_15 and min_15.get('timestamp'):
            timestamps = min_15['timestamp']
            count = len(timestamps)
            context += f"\nmin15[{count}]{{datetime,open,high,low,close,volume}}:\n"
            
            for i in range(count):
                dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
                context += f" {dt},{min_15['open'][i]:.2f},{min_15['high'][i]:.2f},{min_15['low'][i]:.2f},{min_15['close'][i]:.2f},{min_15['volume'][i]:.0f}\n"
        
        min_5 = data.get('min_5', {})
        if min_5 and min_5.get('timestamp'):
            timestamps = min_5['timestamp']
            total = len(timestamps)
            count = min(20, total)
            start_idx = max(0, total - 20)
            context += f"\nmin5[{count}/{total}]{{datetime,open,high,low,close,volume}}:\n"
            
            for i in range(start_idx, total):
                dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
                context += f" {dt},{min_5['open'][i]:.2f},{min_5['high'][i]:.2f},{min_5['low'][i]:.2f},{min_5['close'][i]:.2f},{min_5['volume'][i]:.0f}\n"
        
        return context
    
    def _format_readable(self, data: Dict) -> str:
        """
        Readable table format - Human-friendly for debugging
        Uses more tokens but easier to read
        """
        symbol = data['symbol']
        context = f"\n{'='*80}\n"
        context += f"MARKET DATA FOR {symbol} - {data['timestamp']}\n"
        context += f"{'='*80}\n"
        
        daily = data.get('daily', {})
        if daily and daily.get('timestamp'):
            timestamps = daily['timestamp']
            closes = daily['close']
            context += f"\n📊 DAILY CANDLES (ALL {len(timestamps)} days):\n"
            context += "Date         | Open      | High      | Low       | Close     | Volume\n"
            context += "-" * 80 + "\n"
            
            for i in range(len(timestamps)):
                date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                context += f"{date} | {daily['open'][i]:>9.2f} | {daily['high'][i]:>9.2f} | {daily['low'][i]:>9.2f} | {daily['close'][i]:>9.2f} | {daily['volume'][i]:>10.0f}\n"
        
        hourly = data.get('hourly', {})
        if hourly and hourly.get('timestamp'):
            timestamps = hourly['timestamp']
            context += f"\n⏰ HOURLY CANDLES (ALL {len(timestamps)} hours):\n"
            context += "DateTime           | Open      | High      | Low       | Close     | Volume\n"
            context += "-" * 80 + "\n"
            
            for i in range(len(timestamps)):
                dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
                context += f"{dt} | {hourly['open'][i]:>9.2f} | {hourly['high'][i]:>9.2f} | {hourly['low'][i]:>9.2f} | {hourly['close'][i]:>9.2f} | {hourly['volume'][i]:>10.0f}\n"
        
        min_15 = data.get('min_15', {})
        if min_15 and min_15.get('timestamp'):
            timestamps = min_15['timestamp']
            context += f"\n🕒 15-MINUTE CANDLES (ALL {len(timestamps)} candles):\n"
            context += "DateTime           | Open      | High      | Low       | Close     | Volume\n"
            context += "-" * 80 + "\n"
            
            for i in range(len(timestamps)):
                dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
                context += f"{dt} | {min_15['open'][i]:>9.2f} | {min_15['high'][i]:>9.2f} | {min_15['low'][i]:>9.2f} | {min_15['close'][i]:>9.2f} | {min_15['volume'][i]:>10.0f}\n"
        
        min_5 = data.get('min_5', {})
        if min_5 and min_5.get('timestamp'):
            timestamps = min_5['timestamp']
            context += f"\n⚡ 5-MINUTE CANDLES (Last 20 of {len(timestamps)} candles):\n"
            context += "DateTime           | Open      | High      | Low       | Close     | Volume\n"
            context += "-" * 80 + "\n"
            
            for i in range(max(0, len(timestamps) - 20), len(timestamps)):
                dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
                context += f"{dt} | {min_5['open'][i]:>9.2f} | {min_5['high'][i]:>9.2f} | {min_5['low'][i]:>9.2f} | {min_5['close'][i]:>9.2f} | {min_5['volume'][i]:>10.0f}\n"
        
        return context
    
    def print_cache_status(self):
        """Print current cache status"""
        print(f"\n{'='*60}")
        print("CACHE STATUS")
        print(f"{'='*60}")
        print(f"Daily Cache: {len(self.daily_cache)} symbols (Date: {self.daily_cache_date})")
        print(f"Hourly Cache: {len(self.hourly_cache)} symbols (Time: {self.hourly_cache_time})")
        print(f"15-min Cache: {len(self.min_15_cache)} symbols (Time: {self.min_15_cache_time})")
        print(f"5-min Cache: Never cached (always fresh)")
        print(f"{'='*60}\n")
