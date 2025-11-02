import os
from dotenv import load_dotenv
from dhanhq import dhanhq, marketfeed

load_dotenv()

DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

def test_basic_connection():
    """Test basic connection to Dhan API"""
    print("=" * 60)
    print("Testing Dhan API Connection")
    print("=" * 60)
    
    try:
        dhan = dhanhq(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
        print("✅ Successfully initialized Dhan client")
        return dhan
    except Exception as e:
        print(f"❌ Failed to initialize Dhan client: {e}")
        return None

def test_fund_limits(dhan):
    """Test fetching fund limits"""
    print("\n" + "=" * 60)
    print("Testing Fund Limits")
    print("=" * 60)
    
    try:
        response = dhan.get_fund_limits()
        if response and response.get('status') == 'success':
            data = response['data']
            print(f"✅ Available Balance: ₹{data.get('availabelBalance', 0)}")
            print(f"   Total Collateral: ₹{data.get('collateralAmount', 0)}")
            print(f"   Used Margin: ₹{data.get('utilizedAmount', 0)}")
            return True
        else:
            print(f"❌ Failed to fetch fund limits: {response}")
            return False
    except Exception as e:
        print(f"❌ Error fetching fund limits: {e}")
        return False

def test_positions(dhan):
    """Test fetching current positions"""
    print("\n" + "=" * 60)
    print("Testing Positions")
    print("=" * 60)
    
    try:
        response = dhan.get_positions()
        if response and response.get('status') == 'success':
            positions = response.get('data', [])
            print(f"✅ Total positions: {len(positions)}")
            
            if positions:
                for pos in positions:
                    print(f"\n   Symbol: {pos.get('tradingSymbol')}")
                    print(f"   Quantity: {pos.get('netQty')}")
                    print(f"   P&L: ₹{pos.get('realizedProfit', 0)}")
            else:
                print("   No open positions")
            return True
        else:
            print(f"❌ Failed to fetch positions: {response}")
            return False
    except Exception as e:
        print(f"❌ Error fetching positions: {e}")
        return False

def test_market_quote(dhan):
    """Test fetching market quotes for popular Indian stocks"""
    print("\n" + "=" * 60)
    print("Testing Market Quotes")
    print("=" * 60)
    
    securities = {
        "NSE_EQ": [2885, 11536, 1594, 1333, 4963]
    }
    
    stock_names = {"2885": "RELIANCE", "11536": "TCS", "1594": "INFY", "1333": "HDFCBANK", "4963": "ICICIBANK"}
    
    try:
        response = dhan.quote_data(securities)
        
        if response and response.get('status') == 'success':
            data = response.get('data', {})
            nse_data = data.get('NSE_EQ', [])
            
            for stock in nse_data:
                security_id = str(stock.get('security_id', ''))
                name = stock_names.get(security_id, security_id)
                ltp = stock.get('LTP', 'N/A')
                prev_close = stock.get('prev_close_price', 'N/A')
                print(f"✅ {name:12} - LTP: ₹{ltp:>8}  Prev Close: ₹{prev_close:>8}")
            return True
        else:
            print(f"❌ Failed to fetch quotes: {response}")
            return False
    except Exception as e:
        print(f"❌ Error fetching market quotes: {e}")
        return False

def test_historical_data(dhan):
    """Test fetching historical daily data"""
    print("\n" + "=" * 60)
    print("Testing Historical Data (RELIANCE - Last 5 Days)")
    print("=" * 60)
    
    try:
        from datetime import datetime, timedelta
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        response = dhan.historical_daily_data(
            security_id="2885",
            exchange_segment="NSE_EQ",
            instrument_type="EQUITY",
            from_date=from_date,
            to_date=to_date
        )
        
        if response and response.get('status') == 'success':
            data = response.get('data', {})
            
            if isinstance(data, dict):
                timestamps = data.get('timestamp', [])
                opens = data.get('open', [])
                highs = data.get('high', [])
                lows = data.get('low', [])
                closes = data.get('close', [])
                volumes = data.get('volume', [])
                
                print(f"✅ Retrieved {len(timestamps)} days of data")
                
                if timestamps:
                    print("\n   Date       | Open    | High    | Low     | Close   | Volume")
                    print("   " + "-" * 70)
                    
                    for i in range(max(0, len(timestamps) - 5), len(timestamps)):
                        date = timestamps[i] if i < len(timestamps) else 'N/A'
                        open_p = opens[i] if i < len(opens) else 'N/A'
                        high = highs[i] if i < len(highs) else 'N/A'
                        low = lows[i] if i < len(lows) else 'N/A'
                        close = closes[i] if i < len(closes) else 'N/A'
                        volume = volumes[i] if i < len(volumes) else 'N/A'
                        print(f"   {date} | {open_p:>7} | {high:>7} | {low:>7} | {close:>7} | {volume:>8}")
            return True
        else:
            print(f"❌ Failed to fetch historical data: {response}")
            return False
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        return False

def test_intraday_data(dhan):
    """Test fetching intraday minute data"""
    print("\n" + "=" * 60)
    print("Testing Intraday Data (RELIANCE - 1 Minute)")
    print("=" * 60)
    
    try:
        from datetime import datetime, timedelta
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = datetime.now().strftime("%Y-%m-%d")
        
        response = dhan.intraday_minute_data(
            security_id="2885",
            exchange_segment=dhan.NSE,
            instrument_type=dhan.INDEX,
            from_date=from_date,
            to_date=to_date,
            interval=1
        )
        
        if response and response.get('status') == 'success':
            data = response.get('data', [])
            print(f"✅ Retrieved {len(data)} minute candles")
            
            if data:
                print("\n   Latest 5 candles:")
                print("   Time     | Open    | High    | Low     | Close   | Volume")
                print("   " + "-" * 70)
                for candle in data[-5:]:
                    timestamp = candle.get('timestamp', 'N/A')
                    open_p = candle.get('open', 'N/A')
                    high = candle.get('high', 'N/A')
                    low = candle.get('low', 'N/A')
                    close = candle.get('close', 'N/A')
                    volume = candle.get('volume', 'N/A')
                    print(f"   {timestamp} | {open_p:>7} | {high:>7} | {low:>7} | {close:>7} | {volume:>8}")
            return True
        else:
            print(f"❌ Failed to fetch intraday data: {response}")
            return False
    except Exception as e:
        print(f"❌ Error fetching intraday data: {e}")
        return False

def main():
    """Run all Dhan API tests"""
    print("\n" + "🚀" * 30)
    print("DHAN API CONNECTION TEST SUITE")
    print("🚀" * 30 + "\n")
    
    dhan = test_basic_connection()
    
    if not dhan:
        print("\n❌ Cannot proceed without valid connection. Please check your credentials.\n")
        return
    
    results = []
    results.append(("Historical Data", test_historical_data(dhan)))
    results.append(("Market Quotes", test_market_quote(dhan)))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
