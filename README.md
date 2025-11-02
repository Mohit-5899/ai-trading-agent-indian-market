# AI Trading Agent - Indian Stock Market

Automated trading system for Indian stock market using Dhan API with rule-based VWAP strategy.

## 🎯 Strategy Performance

**VWAP Breakout/Retest Strategy** - Backtested on RELIANCE (90 days)

| Metric | Value |
|--------|-------|
| **Return** | **39.74%** |
| **Win Rate** | 51.8% |
| **Profit Factor** | 1.44 |
| **Max Drawdown** | 10.07% |
| **Total Trades** | 85 |

## 📊 Strategy Rules

### VWAP Breakout/Retest Strategy

**Entry Signals:**
1. **BULLISH_BREAKOUT**: Price crosses above VWAP with momentum
2. **BULLISH_RETEST**: Price retests VWAP from above and holds
3. **BEARISH_BREAKDOWN**: Price crosses below VWAP with momentum
4. **BEARISH_RETEST**: Price retests VWAP from below and holds

**Risk Management:**
- **Timeframe**: 5-minute candles
- **Stop Loss**: 0.2% away from VWAP (below for long, above for short)
- **Risk per trade**: 2% of account
- **Risk-Reward**: 1:3
- **Position sizing**: Based on stop loss distance

**Exit Rules:**
- Target hit (3x risk)
- Stop loss hit
- End of day (close all positions)

## 🚀 Setup

### Prerequisites
- Python 3.8+
- Dhan Trading Account (paid subscription for intraday data)
- Virtual environment at `/Users/mohitmandawat/Coding/CodeTrading/.venv`

### Installation

1. **Activate virtual environment:**
```bash
source /Users/mohitmandawat/Coding/CodeTrading/.venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install dhanhq python-dotenv numpy pandas openai
```

3. **Configure environment variables:**

Create `.env` file:
```bash
DHAN_CLIENT_ID=your_client_id
DHAN_ACCESS_TOKEN=your_access_token
DHAN_BASE_URL=https://api.dhan.co/v2/
OPENROUTER_API_KEY=your_openrouter_key  # Optional, only for LLM features
```

## 📁 Project Structure

```
ai-trading-agent-indian-market/
├── README.md                      # This file
├── .env                          # API credentials (not in git)
├── vwap_calculator.py            # VWAP calculation & signal detection
├── backtest_vwap.py              # Rule-based VWAP backtest
├── market_data_manager.py        # Multi-timeframe data fetching with caching
├── trading_agent.py              # LLM trading agent (for execution)
└── backtest_vwap_llm.py          # LLM backtest (31.94% - not recommended)
```

## 🧪 Running Backtests

### VWAP Strategy Backtest (Recommended)

```bash
source /Users/mohitmandawat/Coding/CodeTrading/.venv/bin/activate
PYTHONPATH=/Users/mohitmandawat/Coding/CodeTrading/ai-trading-agent-indian-market \
python backtest_vwap.py
```

**Output:**
- Performance metrics (return, win rate, profit factor)
- Trade-by-trade breakdown
- Equity curve
- Sample trades with entry/exit details

## 📡 Data Management

### Market Data Manager

Fetches multi-timeframe data from Dhan API with intelligent caching:

| Timeframe | Cache Duration | Use Case |
|-----------|----------------|----------|
| Daily (7 days) | Entire day | Trend context |
| Hourly (35 hours) | 60 minutes | Medium-term trend |
| 15-min (50 candles) | 15 minutes | Short-term structure |
| 5-min (150 candles) | Always fresh | Entry signals |

**Data Format:**
- TOON format (Token-Oriented Object Notation) for LLM - 84% fewer tokens
- Readable format for debugging

## 🔧 Core Components

### 1. VWAP Calculator (`vwap_calculator.py`)

```python
from vwap_calculator import VWAPCalculator

calc = VWAPCalculator()

# Calculate VWAP
vwap = calc.calculate_vwap(data)

# Detect entry signal
signal = calc.detect_vwap_breakout(data, vwap, current_idx=-1)

# Calculate position size (2% risk)
quantity = calc.calculate_position_size(
    account_value=100000,
    risk_pct=2.0,
    entry_price=1400,
    stop_loss_price=1395
)

# Calculate targets (1:3 R:R)
targets = calc.calculate_targets(
    entry_price=1400,
    stop_loss_price=1395,
    risk_reward_ratio=3.0
)
```

### 2. Market Data Manager (`market_data_manager.py`)

```python
from market_data_manager import MarketDataManager

manager = MarketDataManager(symbols=["RELIANCE"])

# Fetch all timeframes
data = manager.get_all_timeframes("RELIANCE")

# Format for LLM (TOON format)
context = manager.format_for_llm(data, format_type='toon')

# Check cache status
manager.print_cache_status()
```

### 3. Backtest Engine (`backtest_vwap.py`)

```python
from backtest_vwap import VWAPBacktester

backtester = VWAPBacktester(
    symbol="RELIANCE",
    security_id="2885",
    initial_capital=100000
)

stats = backtester.run_backtest(days=90)

if stats['status'] == 'COMPLETED':
    backtester.print_results(stats)
```

## 📈 Supported Stocks

Security IDs for popular Indian stocks:

| Symbol | Security ID | Exchange |
|--------|-------------|----------|
| RELIANCE | 2885 | NSE_EQ |
| TCS | 11536 | NSE_EQ |
| INFY | 1594 | NSE_EQ |
| HDFCBANK | 1333 | NSE_EQ |
| ICICIBANK | 4963 | NSE_EQ |
| SBIN | 3045 | NSE_EQ |
| BHARTIARTL | 3677 | NSE_EQ |
| ITC | 1660 | NSE_EQ |
| LT | 11483 | NSE_EQ |
| HINDUNILVR | 1394 | NSE_EQ |

## ⚠️ Important Notes

### Tested Strategies

| Strategy | Result | Reason |
|----------|--------|--------|
| ✅ VWAP Breakout/Retest | **39.74% return** | Clear signals, good R:R |
| ❌ VWAP + LLM Decision | 31.94% return | LLM followed rules 90%, added no value |
| ❌ EMA + Candlestick | 8.28% return | Subjective patterns, inconsistent |
| ❌ EMA + Candlestick + RSI | 1.06% return | Over-filtered, removed good trades |
| ❌ BB + RSI | 2.76% return | Low win rate (37%), high drawdown (22%) |

### Recommendations

1. **Use rule-based VWAP strategy only** - Proven 39.74% return
2. **Don't use LLM for decision-making** - Only for trade execution
3. **5-minute timeframe works best** - RSI/BB filters fail on this timeframe
4. **Keep it simple** - Complex filters reduce performance

## 🔐 Security

- Never commit `.env` file to git
- Store API keys securely
- Use environment variables for credentials
- Dhan access tokens expire - update regularly

## 📊 Market Hours

**NSE Trading Hours:**
- Pre-market: 09:00 - 09:15
- Regular: 09:15 - 15:30
- Post-market: 15:40 - 16:00

**Strategy runs during:**
- Regular trading hours (09:15 - 15:30)
- Closes all positions at end of day

## 🛠️ Development

### Testing Data Fetch

```bash
# Test daily data
PYTHONPATH=/Users/mohitmandawat/Coding/CodeTrading/ai-trading-agent-indian-market \
python -c "from market_data_manager import MarketDataManager; m = MarketDataManager(['RELIANCE']); print(m.get_daily_data('RELIANCE'))"

# Test 5-min data
PYTHONPATH=/Users/mohitmandawat/Coding/CodeTrading/ai-trading-agent-indian-market \
python -c "from market_data_manager import MarketDataManager; m = MarketDataManager(['RELIANCE']); print(m.get_5min_data('RELIANCE'))"
```

### Adding New Stocks

1. Find security ID from Dhan API
2. Add to `security_ids` dict in `market_data_manager.py`
3. Run backtest to validate strategy performance

## 📞 Support

- **Dhan API Docs**: https://dhanhq.co/docs/
- **Project Location**: `/Users/mohitmandawat/Coding/CodeTrading/ai-trading-agent-indian-market`
- **Virtual Env**: `/Users/mohitmandawat/Coding/CodeTrading/.venv`

## ⚖️ Disclaimer

This is an educational project. Trading involves risk of loss. Past performance (39.74% in backtest) does not guarantee future results. Always test strategies thoroughly before live trading. Not financial advice.

## 📝 License

Private project - All rights reserved.

---

**Last Updated**: November 2025
**Backtested Period**: August - October 2025 (90 days)
**Best Strategy**: VWAP Breakout/Retest (39.74% return)
