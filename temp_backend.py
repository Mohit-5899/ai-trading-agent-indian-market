
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI(title="AI Trading Arena Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/system/status")
async def get_system_status():
    return {
        "status": "healthy",
        "active_accounts": 2,
        "today_trades": random.randint(5, 25),
        "trading_enabled": True,
        "market_open": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/accounts")
async def get_accounts():
    return [
        {
            "id": "qwen_account",
            "name": "Qwen_3_235B", 
            "model_name": "qwen/qwen3-235b-a22b-2507",
            "capital_allocation": 10000,
            "allocation_percentage": 50,
            "invocation_count": random.randint(100, 500),
            "is_active": True
        },
        {
            "id": "deepseek_account", 
            "name": "DeepSeek_v3.2",
            "model_name": "deepseek/deepseek-v3.2-exp",
            "capital_allocation": 10000,
            "allocation_percentage": 50,
            "invocation_count": random.randint(100, 500),
            "is_active": True
        }
    ]

@app.get("/api/portfolio/performance")
async def get_performance(days: int = 7):
    # Generate sample performance data
    data = []
    for i in range(days * 24):  # Hourly data
        timestamp = datetime.now().replace(hour=i%24, minute=0, second=0, microsecond=0)
        qwen_value = 10000 + random.uniform(-500, 1500)
        deepseek_value = 10000 + random.uniform(-300, 1200)
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "account_id": "qwen_account",
            "total_value": qwen_value,
            "available_cash": 5000,
            "invested_amount": qwen_value - 5000,
            "day_pnl": random.uniform(-200, 300),
            "total_pnl": qwen_value - 10000
        })
        
        data.append({
            "timestamp": timestamp.isoformat(), 
            "account_id": "deepseek_account",
            "total_value": deepseek_value,
            "available_cash": 4000,
            "invested_amount": deepseek_value - 4000,
            "day_pnl": random.uniform(-150, 250),
            "total_pnl": deepseek_value - 10000
        })
    
    return data

@app.get("/api/trades")
async def get_trades(limit: int = 50):
    trades = []
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    
    for i in range(limit):
        trades.append({
            "id": f"trade_{i}",
            "account_name": random.choice(["Qwen_3_235B", "DeepSeek_v3.2"]),
            "stock_symbol": random.choice(symbols),
            "strategy_name": random.choice(["vwap", "ema"]),
            "side": random.choice(["BUY", "SELL"]),
            "quantity": random.randint(1, 20),
            "entry_price": random.uniform(1000, 3500),
            "exit_price": random.uniform(1000, 3500) if random.random() > 0.3 else None,
            "net_pnl": random.uniform(-500, 800) if random.random() > 0.3 else None,
            "status": random.choice(["OPEN", "CLOSED"]),
            "executed_at": datetime.now().isoformat(),
            "closed_at": datetime.now().isoformat() if random.random() > 0.3 else None
        })
    
    return trades

@app.get("/api/invocations")
async def get_invocations(limit: int = 20):
    invocations = []
    
    for i in range(limit):
        invocations.append({
            "id": f"invocation_{i}",
            "account_id": random.choice(["qwen_account", "deepseek_account"]),
            "account_name": random.choice(["Qwen_3_235B", "DeepSeek_v3.2"]),
            "llm_response": "Market analysis complete. Taking position based on VWAP signals.",
            "execution_time_ms": random.randint(1500, 4000),
            "tokens_used": random.randint(800, 2500),
            "created_at": datetime.now().isoformat(),
            "tool_calls": [
                {
                    "tool_name": random.choice(["buy_stock", "sell_stock", "get_portfolio_status"]),
                    "parameters": {"symbol": random.choice(["RELIANCE", "TCS", "INFY"])},
                    "result": "Order executed successfully",
                    "status": "SUCCESS"
                }
            ]
        })
    
    return invocations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
