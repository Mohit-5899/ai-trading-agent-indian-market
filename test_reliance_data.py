import os
from dotenv import load_dotenv
from dhanhq import dhanhq
from datetime import datetime, timedelta

load_dotenv()

DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

dhan = dhanhq(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)

print("=" * 80)
print("RELIANCE STOCK DATA - MULTIPLE TIMEFRAMES")
print("=" * 80)

print("\n" + "=" * 80)
print("1. LAST 3 MONTHS - DAILY DATA")
print("=" * 80)

to_date = datetime.now().strftime("%Y-%m-%d")
from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

print(f"Fetching from {from_date} to {to_date}...")

response = dhan.historical_daily_data(
    security_id="2885",
    exchange_segment="NSE_EQ",
    instrument_type="EQUITY",
    from_date=from_date,
    to_date=to_date
)

if response and response.get('status') == 'success':
    data = response.get('data', {})
    timestamps = data.get('timestamp', [])
    print(f"✅ Retrieved {len(timestamps)} days of data")
    
    if timestamps:
        print(f"   Date range: {datetime.fromtimestamp(timestamps[0]).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d')}")
        print(f"\n   Sample - Last 5 days:")
        print("   Date         | Open      | High      | Low       | Close     | Volume")
        print("   " + "-" * 80)
        
        opens = data.get('open', [])
        highs = data.get('high', [])
        lows = data.get('low', [])
        closes = data.get('close', [])
        volumes = data.get('volume', [])
        
        for i in range(max(0, len(timestamps) - 5), len(timestamps)):
            date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
            print(f"   {date} | {opens[i]:>9} | {highs[i]:>9} | {lows[i]:>9} | {closes[i]:>9} | {volumes[i]:>10}")
else:
    print(f"❌ Failed: {response}")

print("\n" + "=" * 80)
print("2. LAST FRIDAY (OCT 31) - INTRADAY 1-MINUTE DATA")
print("=" * 80)

to_date = "2025-10-31"
from_date = "2025-10-31"

print(f"Fetching intraday data for {from_date}...")

response = dhan.intraday_minute_data(
    security_id="2885",
    exchange_segment="NSE_EQ",
    instrument_type="EQUITY",
    from_date=from_date,
    to_date=to_date,
    interval=1
)

if response and response.get('status') == 'success':
    data = response.get('data', {})
    timestamps = data.get('timestamp', [])
    print(f"✅ Retrieved {len(timestamps)} minute candles")
    
    if timestamps:
        print(f"   Time range: {datetime.fromtimestamp(timestamps[0]).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d %H:%M')}")
        print(f"\n   Sample - Last 10 candles:")
        print("   Time           | Open      | High      | Low       | Close     | Volume")
        print("   " + "-" * 80)
        
        opens = data.get('open', [])
        highs = data.get('high', [])
        lows = data.get('low', [])
        closes = data.get('close', [])
        volumes = data.get('volume', [])
        
        for i in range(max(0, len(timestamps) - 10), len(timestamps)):
            time = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
            print(f"   {time} | {opens[i]:>9} | {highs[i]:>9} | {lows[i]:>9} | {closes[i]:>9} | {volumes[i]:>10}")
else:
    print(f"❌ Failed: {response}")

print("\n" + "=" * 80)
print("3. LAST FRIDAY (OCT 31) - INTRADAY 5-MINUTE DATA")
print("=" * 80)

to_date = "2025-10-31"
from_date = "2025-10-31"

print(f"Fetching 5-minute data for {from_date}...")

response = dhan.intraday_minute_data(
    security_id="2885",
    exchange_segment="NSE_EQ",
    instrument_type="EQUITY",
    from_date=from_date,
    to_date=to_date,
    interval=5
)

if response and response.get('status') == 'success':
    data = response.get('data', {})
    timestamps = data.get('timestamp', [])
    print(f"✅ Retrieved {len(timestamps)} 5-minute candles")
    
    if timestamps:
        print(f"   Time range: {datetime.fromtimestamp(timestamps[0]).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d %H:%M')}")
        print(f"\n   Sample - First 10 candles:")
        print("   Time           | Open      | High      | Low       | Close     | Volume")
        print("   " + "-" * 80)
        
        opens = data.get('open', [])
        highs = data.get('high', [])
        lows = data.get('low', [])
        closes = data.get('close', [])
        volumes = data.get('volume', [])
        
        for i in range(min(10, len(timestamps))):
            time = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
            print(f"   {time} | {opens[i]:>9} | {highs[i]:>9} | {lows[i]:>9} | {closes[i]:>9} | {volumes[i]:>10}")
else:
    print(f"❌ Failed: {response}")

print("\n" + "=" * 80)
print("4. LAST FRIDAY (OCT 31) - INTRADAY 15-MINUTE DATA")
print("=" * 80)

to_date = "2025-10-31"
from_date = "2025-10-31"

print(f"Fetching 15-minute data for {from_date}...")

response = dhan.intraday_minute_data(
    security_id="2885",
    exchange_segment="NSE_EQ",
    instrument_type="EQUITY",
    from_date=from_date,
    to_date=to_date,
    interval=15
)

if response and response.get('status') == 'success':
    data = response.get('data', {})
    timestamps = data.get('timestamp', [])
    print(f"✅ Retrieved {len(timestamps)} 15-minute candles")
    
    if timestamps:
        print(f"   Time range: {datetime.fromtimestamp(timestamps[0]).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d %H:%M')}")
        print(f"\n   All candles:")
        print("   Time           | Open      | High      | Low       | Close     | Volume")
        print("   " + "-" * 80)
        
        opens = data.get('open', [])
        highs = data.get('high', [])
        lows = data.get('low', [])
        closes = data.get('close', [])
        volumes = data.get('volume', [])
        
        for i in range(len(timestamps)):
            time = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
            print(f"   {time} | {opens[i]:>9} | {highs[i]:>9} | {lows[i]:>9} | {closes[i]:>9} | {volumes[i]:>10}")
else:
    print(f"❌ Failed: {response}")

print("\n" + "=" * 80)
