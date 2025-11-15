import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from dhanhq import dhanhq
import time
from pathlib import Path
import json

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
        
        # Simulation mode
        self.simulation_mode = False
        self.historical_data = {}
        self.current_time_index = {}
        self.data_dir = Path("historical_data")
        self.simulation_start_time = None
        
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
        # Use simulation data if in simulation mode
        if self.simulation_mode:
            return self.get_simulation_data(symbol)
        
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
    
    def fetch_and_save_historical_data(self, days: int = 7):
        """Fetch last N days data and save to CSV files for simulation"""
        print(f"Fetching {days} days of historical data for all symbols...")
        
        self.data_dir.mkdir(exist_ok=True)
        
        for symbol in self.symbols:
            print(f"Fetching historical data for {symbol}")
            
            # Fetch all timeframes
            timeframes = {
                "5m": {"interval": 5, "days": days},
                "15m": {"interval": 15, "days": days}, 
                "1h": {"interval": 60, "days": days},
                "daily": {"type": "daily", "days": days + 2}
            }
            
            for tf_name, tf_config in timeframes.items():
                try:
                    if tf_config.get("type") == "daily":
                        data = self._fetch_historical_daily(symbol, tf_config["days"])
                    else:
                        data = self._fetch_historical_intraday(symbol, tf_config["interval"], tf_config["days"])
                    
                    if data:
                        # Convert to DataFrame and add indicators
                        df = self._convert_to_dataframe(data)
                        df = self._add_technical_indicators(df)
                        
                        # Save to CSV
                        filename = f"{symbol}_{tf_name}.csv"
                        filepath = self.data_dir / filename
                        df.to_csv(filepath, index=False)
                        print(f"Saved {len(df)} records to {filepath}")
                    
                except Exception as e:
                    print(f"Error fetching {symbol} {tf_name}: {e}")
        
        print("Historical data fetch completed!")
    
    def _fetch_historical_daily(self, symbol: str, days: int) -> Optional[Dict]:
        """Fetch historical daily data"""
        security_id = self.security_ids.get(symbol)
        if not security_id:
            return None
            
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            response = self.dhan.historical_daily_data(
                security_id=security_id,
                exchange_segment="NSE_EQ", 
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date
            )
            
            if response and response.get('status') == 'success':
                return response.get('data', {})
        except Exception as e:
            print(f"Error fetching daily data: {e}")
        
        return None
    
    def _fetch_historical_intraday(self, symbol: str, interval: int, days: int) -> Optional[Dict]:
        """Fetch historical intraday data"""
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
                interval=interval
            )
            
            if response and response.get('status') == 'success':
                return response.get('data', {})
        except Exception as e:
            print(f"Error fetching intraday data: {e}")
        
        return None
    
    def _convert_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """Convert Dhan API response to pandas DataFrame"""
        if not data or not data.get('timestamp'):
            return pd.DataFrame()
        
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['timestamp'], unit='s'),
            'open': data['open'],
            'high': data['high'], 
            'low': data['low'],
            'close': data['close'],
            'volume': data['volume']
        })
        
        return df.sort_values('timestamp')
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to dataframe"""
        if len(df) < 50:
            return df
        
        try:
            import talib
            import numpy as np
            
            close = df['close'].astype(float).values
            high = df['high'].astype(float).values
            low = df['low'].astype(float).values
            volume = df['volume'].astype(float).values
            
            # EMAs
            df['ema_9'] = talib.EMA(close, timeperiod=9)
            df['ema_21'] = talib.EMA(close, timeperiod=21)
            
            # RSI
            df['rsi'] = talib.RSI(close, timeperiod=14)
            
            # VWAP
            typical_price = (high + low + close) / 3
            df['vwap'] = (typical_price * volume).cumsum() / volume.cumsum()
            
            # MACD
            macd, signal, hist = talib.MACD(close)
            df['macd'] = macd
            df['macd_signal'] = signal
            
            return df
            
        except Exception as e:
            print(f"Error adding indicators: {e}")
            return df
    
    def start_simulation_mode(self):
        """Start simulation mode using historical CSV data"""
        print("Starting simulation mode...")
        
        self.simulation_mode = True
        self.simulation_start_time = datetime.now()
        
        # Load all CSV files
        self.historical_data = {}
        self.current_time_index = {}
        
        for symbol in self.symbols:
            self.historical_data[symbol] = {}
            self.current_time_index[symbol] = {}
            
            timeframes = ["5m", "15m", "1h", "daily"]
            
            for tf in timeframes:
                filepath = self.data_dir / f"{symbol}_{tf}.csv"
                
                if filepath.exists():
                    df = pd.read_csv(filepath)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp')
                    
                    self.historical_data[symbol][tf] = df
                    self.current_time_index[symbol][tf] = 0
                    
                    print(f"Loaded {len(df)} records for {symbol} {tf}")
                else:
                    print(f"Warning: {filepath} not found")
        
        print("Simulation mode started!")
    
    def get_simulation_data(self, symbol: str) -> Dict:
        """Get current simulation data (forward-only)"""
        if not self.simulation_mode:
            return self.get_all_timeframes(symbol)
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': True
        }
        
        timeframes = {"daily": "daily", "hourly": "1h", "min_15": "15m", "min_5": "5m"}
        
        for result_key, tf_key in timeframes.items():
            if symbol in self.historical_data and tf_key in self.historical_data[symbol]:
                df = self.historical_data[symbol][tf_key]
                current_idx = self.current_time_index[symbol][tf_key]
                
                # Get data up to current index (forward-only)
                if current_idx < len(df):
                    available_data = df.iloc[:current_idx + 1]
                    
                    if len(available_data) > 0:
                        # Convert back to Dhan format
                        result[result_key] = {
                            'timestamp': [int(ts.timestamp()) for ts in available_data['timestamp']],
                            'open': available_data['open'].tolist(),
                            'high': available_data['high'].tolist(),
                            'low': available_data['low'].tolist(),
                            'close': available_data['close'].tolist(),
                            'volume': available_data['volume'].tolist()
                        }
        
        return result
    
    def advance_simulation(self, minutes: int = 5):
        """Advance simulation by specified minutes"""
        if not self.simulation_mode:
            return
        
        for symbol in self.symbols:
            if symbol not in self.current_time_index:
                continue
            
            for tf in self.current_time_index[symbol]:
                if symbol in self.historical_data and tf in self.historical_data[symbol]:
                    df = self.historical_data[symbol][tf]
                    current_idx = self.current_time_index[symbol][tf]
                    
                    # Calculate advancement based on timeframe
                    if tf == "5m":
                        advance_by = max(1, minutes // 5)
                    elif tf == "15m":
                        advance_by = max(1, minutes // 15)
                    elif tf == "1h":
                        advance_by = max(1, minutes // 60)
                    elif tf == "daily":
                        advance_by = 1 if minutes >= 1440 else 0
                    else:
                        advance_by = 1
                    
                    new_idx = min(current_idx + advance_by, len(df) - 1)
                    self.current_time_index[symbol][tf] = new_idx
    
    def get_simulation_progress(self) -> float:
        """Get simulation progress percentage"""
        if not self.simulation_mode:
            return 0.0
        
        total_progress = 0
        count = 0
        
        for symbol in self.symbols:
            if symbol in self.current_time_index:
                for tf in self.current_time_index[symbol]:
                    if symbol in self.historical_data and tf in self.historical_data[symbol]:
                        df = self.historical_data[symbol][tf]
                        current_idx = self.current_time_index[symbol][tf]
                        
                        if len(df) > 0:
                            progress = (current_idx / len(df)) * 100
                            total_progress += progress
                            count += 1
        
        return total_progress / count if count > 0 else 0.0
    
    def get_current_simulation_time(self) -> Optional[datetime]:
        """Get current simulation timestamp"""
        if not self.simulation_mode:
            return None
        
        # Use 5m data from first symbol to determine current time
        first_symbol = self.symbols[0] if self.symbols else None
        
        if (first_symbol and 
            first_symbol in self.historical_data and 
            "5m" in self.historical_data[first_symbol]):
            
            df = self.historical_data[first_symbol]["5m"]
            current_idx = self.current_time_index[first_symbol]["5m"]
            
            if current_idx < len(df):
                return df.iloc[current_idx]['timestamp']
        
        return None
