import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from dhanhq import dhanhq
from vwap_calculator import VWAPCalculator
from openai import OpenAI
import time

load_dotenv()

class VWAPLLMBacktester:
    """
    Backtest VWAP Strategy with LLM Decision Making
    - LLM analyzes VWAP signals and market context
    - LLM decides whether to take each trade
    - 2% risk per trade, 1:3 R:R ratio
    """
    
    def __init__(self, symbol: str, security_id: str, initial_capital: float = 100000):
        self.symbol = symbol
        self.security_id = security_id
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_pct = 2.0
        self.risk_reward_ratio = 3.0
        
        self.dhan = dhanhq(
            os.getenv("DHAN_CLIENT_ID"),
            os.getenv("DHAN_ACCESS_TOKEN")
        )
        self.vwap_calc = VWAPCalculator()
        
        self.openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        self.trades = []
        self.equity_curve = []
        self.llm_calls = 0
        self.llm_accepts = 0
        self.llm_rejects = 0
        
    def fetch_historical_data(self, days: int = 90) -> Optional[Dict]:
        """
        Fetch last 90 days of 5-minute data
        """
        print(f"📥 Fetching {days} days of 5-minute data for {self.symbol}...")
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            response = self.dhan.intraday_minute_data(
                security_id=self.security_id,
                exchange_segment="NSE_EQ",
                instrument_type="EQUITY",
                from_date=from_date,
                to_date=to_date,
                interval=5
            )
            
            if response and response.get('status') == 'success':
                data = response.get('data', {})
                count = len(data.get('timestamp', []))
                print(f"✅ Retrieved {count} 5-minute candles")
                return data
            else:
                print(f"❌ Failed to fetch data: {response}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def split_by_trading_day(self, data: Dict) -> List[Dict]:
        """
        Split continuous data into individual trading days
        """
        timestamps = data['timestamp']
        days = {}
        
        for i in range(len(timestamps)):
            dt = datetime.fromtimestamp(timestamps[i])
            date_key = dt.strftime('%Y-%m-%d')
            
            if date_key not in days:
                days[date_key] = {
                    'timestamp': [],
                    'open': [],
                    'high': [],
                    'low': [],
                    'close': [],
                    'volume': []
                }
            
            days[date_key]['timestamp'].append(timestamps[i])
            days[date_key]['open'].append(data['open'][i])
            days[date_key]['high'].append(data['high'][i])
            days[date_key]['low'].append(data['low'][i])
            days[date_key]['close'].append(data['close'][i])
            days[date_key]['volume'].append(data['volume'][i])
        
        sorted_days = []
        for date in sorted(days.keys()):
            sorted_days.append({
                'date': date,
                'data': days[date]
            })
        
        return sorted_days
    
    def format_context_for_llm(self, data: Dict, vwap: List[float], current_idx: int, signal: Dict) -> str:
        """
        Format last 20 candles with VWAP for LLM context
        """
        context = f"MARKET_CONTEXT[{self.symbol}]\\n\\n"
        context += f"CURRENT_SIGNAL: {signal['signal']}\\n"
        context += f"Price: ₹{signal['price']:.2f} | VWAP: ₹{signal['vwap']:.2f} | Distance: {signal['distance_pct']:.2f}%\\n\\n"
        
        context += "LAST_20_CANDLES{time,close,vwap,position}:\\n"
        
        start_idx = max(0, current_idx - 19)
        for i in range(start_idx, current_idx + 1):
            dt = datetime.fromtimestamp(data['timestamp'][i]).strftime('%H:%M')
            close = data['close'][i]
            vwap_val = vwap[i]
            position = "ABOVE" if close > vwap_val else "BELOW"
            context += f" {dt},{close:.2f},{vwap_val:.2f},{position}\\n"
        
        return context
    
    def get_llm_decision(self, context: str, signal: Dict) -> Dict:
        """
        Ask LLM whether to take the trade
        """
        self.llm_calls += 1
        
        prompt = f"""You are an expert VWAP trader managing a ₹{self.capital:,.0f} account.

STRATEGY:
- Trade on 5-minute VWAP breakout/retest
- Risk: {self.risk_pct}% per trade
- Risk:Reward: 1:{self.risk_reward_ratio}

SIGNAL TYPES:
- BULLISH_BREAKOUT: Price just crossed above VWAP (strong momentum)
- BULLISH_RETEST: Price retesting VWAP from above (support test)
- BEARISH_BREAKDOWN: Price just crossed below VWAP (strong momentum down)
- BEARISH_RETEST: Price retesting VWAP from below (resistance test)

CURRENT SITUATION:
{context}

QUESTION: Should we take this {signal['signal']} trade?

Consider:
1. Is the signal strong enough?
2. Is price action confirming the signal?
3. Is there clear momentum?
4. Are we at a good risk:reward point?

Respond ONLY with valid JSON:
{{
  "take_trade": true/false,
  "reasoning": "Brief explanation (1-2 sentences)",
  "confidence": 0-100
}}"""
        
        try:
            completion = self.openrouter_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/ai-trading-agent",
                    "X-Title": "AI Trading Agent Backtest"
                },
                model="deepseek/deepseek-chat-v3-0324",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert VWAP trader. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            decision = json.loads(response_text)
            
            if decision.get('take_trade'):
                self.llm_accepts += 1
            else:
                self.llm_rejects += 1
            
            return decision
            
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return {'take_trade': False, 'reasoning': f'Error: {str(e)}', 'confidence': 0}
    
    def backtest_day(self, day_data: Dict) -> List[Dict]:
        """
        Backtest a single trading day with LLM decisions
        """
        date = day_data['date']
        data = day_data['data']
        
        if len(data['timestamp']) < 20:
            return []
        
        vwap = self.vwap_calc.calculate_vwap(data)
        
        day_trades = []
        in_position = False
        position = None
        
        for i in range(20, len(data['timestamp'])):
            current_price = data['close'][i]
            current_vwap = vwap[i]
            
            if in_position:
                if position['side'] == 'LONG':
                    if current_price <= position['stop_loss']:
                        pnl = (position['stop_loss'] - position['entry']) * position['quantity']
                        position['exit_price'] = position['stop_loss']
                        position['exit_reason'] = 'STOP_LOSS'
                        position['pnl'] = pnl
                        day_trades.append(position)
                        in_position = False
                        self.capital += pnl
                    elif current_price >= position['target']:
                        pnl = (position['target'] - position['entry']) * position['quantity']
                        position['exit_price'] = position['target']
                        position['exit_reason'] = 'TARGET'
                        position['pnl'] = pnl
                        day_trades.append(position)
                        in_position = False
                        self.capital += pnl
                
                elif position['side'] == 'SHORT':
                    if current_price >= position['stop_loss']:
                        pnl = (position['entry'] - position['stop_loss']) * position['quantity']
                        position['exit_price'] = position['stop_loss']
                        position['exit_reason'] = 'STOP_LOSS'
                        position['pnl'] = pnl
                        day_trades.append(position)
                        in_position = False
                        self.capital += pnl
                    elif current_price <= position['target']:
                        pnl = (position['entry'] - position['target']) * position['quantity']
                        position['exit_price'] = position['target']
                        position['exit_reason'] = 'TARGET'
                        position['pnl'] = pnl
                        day_trades.append(position)
                        in_position = False
                        self.capital += pnl
            
            else:
                signal = self.vwap_calc.detect_vwap_breakout(data, vwap, i)
                
                if signal['signal'] not in ['NEUTRAL']:
                    context = self.format_context_for_llm(data, vwap, i, signal)
                    
                    llm_decision = self.get_llm_decision(context, signal)
                    
                    time.sleep(0.5)
                    
                    if llm_decision.get('take_trade'):
                        if signal['signal'] in ['BULLISH_BREAKOUT', 'BULLISH_RETEST']:
                            entry_price = current_price
                            stop_loss = current_vwap * 0.998
                            
                            quantity = self.vwap_calc.calculate_position_size(
                                self.capital,
                                self.risk_pct,
                                entry_price,
                                stop_loss
                            )
                            
                            if quantity > 0:
                                targets = self.vwap_calc.calculate_targets(
                                    entry_price,
                                    stop_loss,
                                    self.risk_reward_ratio
                                )
                                
                                position = {
                                    'date': date,
                                    'entry_time': datetime.fromtimestamp(data['timestamp'][i]).strftime('%H:%M'),
                                    'side': 'LONG',
                                    'entry': entry_price,
                                    'stop_loss': targets['stop_loss'],
                                    'target': targets['target'],
                                    'quantity': quantity,
                                    'signal': signal['signal'],
                                    'vwap': current_vwap,
                                    'llm_reasoning': llm_decision.get('reasoning'),
                                    'llm_confidence': llm_decision.get('confidence')
                                }
                                in_position = True
                        
                        elif signal['signal'] in ['BEARISH_BREAKDOWN', 'BEARISH_RETEST']:
                            entry_price = current_price
                            stop_loss = current_vwap * 1.002
                            
                            quantity = self.vwap_calc.calculate_position_size(
                                self.capital,
                                self.risk_pct,
                                entry_price,
                                stop_loss
                            )
                            
                            if quantity > 0:
                                targets = self.vwap_calc.calculate_targets(
                                    entry_price,
                                    stop_loss,
                                    self.risk_reward_ratio
                                )
                                
                                position = {
                                    'date': date,
                                    'entry_time': datetime.fromtimestamp(data['timestamp'][i]).strftime('%H:%M'),
                                    'side': 'SHORT',
                                    'entry': entry_price,
                                    'stop_loss': targets['stop_loss'],
                                    'target': targets['target'],
                                    'quantity': quantity,
                                    'signal': signal['signal'],
                                    'vwap': current_vwap,
                                    'llm_reasoning': llm_decision.get('reasoning'),
                                    'llm_confidence': llm_decision.get('confidence')
                                }
                                in_position = True
        
        if in_position:
            position['exit_price'] = data['close'][-1]
            position['exit_reason'] = 'END_OF_DAY'
            if position['side'] == 'LONG':
                pnl = (position['exit_price'] - position['entry']) * position['quantity']
            else:
                pnl = (position['entry'] - position['exit_price']) * position['quantity']
            position['pnl'] = pnl
            day_trades.append(position)
            self.capital += pnl
        
        return day_trades
    
    def run_backtest(self, days: int = 90) -> Dict:
        """
        Run complete backtest with LLM
        """
        print(f"\n{'='*80}")
        print(f"🤖 VWAP STRATEGY BACKTEST WITH LLM - {self.symbol}")
        print(f"{'='*80}")
        print(f"Initial Capital: ₹{self.initial_capital:,.0f}")
        print(f"Risk per trade: {self.risk_pct}%")
        print(f"Risk:Reward: 1:{self.risk_reward_ratio}")
        print(f"Backtesting Period: Last {days} days")
        print(f"LLM Model: DeepSeek v3")
        
        data = self.fetch_historical_data(days)
        if not data:
            return {'status': 'FAILED', 'reason': 'No data'}
        
        trading_days = self.split_by_trading_day(data)
        print(f"\n📅 Total Trading Days: {len(trading_days)}")
        
        print(f"\n{'='*80}")
        print("🔄 Running Backtest with LLM Decision Making...")
        print(f"{'='*80}")
        
        for idx, day in enumerate(trading_days):
            print(f"\n[Day {idx+1}/{len(trading_days)}] {day['date']} - Capital: ₹{self.capital:,.0f}")
            day_trades = self.backtest_day(day)
            self.trades.extend(day_trades)
            self.equity_curve.append({
                'date': day['date'],
                'capital': self.capital
            })
            print(f"  Trades today: {len(day_trades)} | LLM calls: {self.llm_calls} | Accepts: {self.llm_accepts} | Rejects: {self.llm_rejects}")
        
        return self.calculate_statistics()
    
    def calculate_statistics(self) -> Dict:
        """
        Calculate backtest statistics
        """
        if not self.trades:
            return {
                'status': 'NO_TRADES',
                'total_trades': 0,
                'llm_stats': {
                    'total_calls': self.llm_calls,
                    'accepts': self.llm_accepts,
                    'rejects': self.llm_rejects,
                    'acceptance_rate': 0
                }
            }
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(t['pnl'] for t in winning_trades)
        total_loss = sum(t['pnl'] for t in losing_trades)
        net_pnl = self.capital - self.initial_capital
        
        avg_win = total_profit / win_count if win_count > 0 else 0
        avg_loss = total_loss / loss_count if loss_count > 0 else 0
        
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
        
        max_capital = self.initial_capital
        max_drawdown = 0
        
        for point in self.equity_curve:
            if point['capital'] > max_capital:
                max_capital = point['capital']
            drawdown = ((max_capital - point['capital']) / max_capital) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        acceptance_rate = (self.llm_accepts / self.llm_calls * 100) if self.llm_calls > 0 else 0
        
        return {
            'status': 'COMPLETED',
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'net_pnl': net_pnl,
            'return_pct': (net_pnl / self.initial_capital) * 100,
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'llm_stats': {
                'total_calls': self.llm_calls,
                'accepts': self.llm_accepts,
                'rejects': self.llm_rejects,
                'acceptance_rate': acceptance_rate
            },
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
    
    def print_results(self, stats: Dict):
        """
        Print backtest results
        """
        print(f"\n{'='*80}")
        print("📊 LLM BACKTEST RESULTS")
        print(f"{'='*80}")
        
        print(f"\n🤖 LLM STATISTICS:")
        print(f"  Total LLM Calls:     {stats['llm_stats']['total_calls']}")
        print(f"  Trades Accepted:     {stats['llm_stats']['accepts']}")
        print(f"  Trades Rejected:     {stats['llm_stats']['rejects']}")
        print(f"  Acceptance Rate:     {stats['llm_stats']['acceptance_rate']:.1f}%")
        
        print(f"\n💰 PERFORMANCE:")
        print(f"  Initial Capital: ₹{stats['initial_capital']:,.0f}")
        print(f"  Final Capital:   ₹{stats['final_capital']:,.0f}")
        print(f"  Net P&L:         ₹{stats['net_pnl']:,.0f}")
        print(f"  Return:          {stats['return_pct']:.2f}%")
        
        print(f"\n📈 TRADE STATISTICS:")
        print(f"  Total Trades:    {stats['total_trades']}")
        print(f"  Winning Trades:  {stats['winning_trades']} ({stats['win_rate']:.1f}%)")
        print(f"  Losing Trades:   {stats['losing_trades']}")
        
        print(f"\n💵 PROFIT/LOSS:")
        print(f"  Total Profit:    ₹{stats['total_profit']:,.0f}")
        print(f"  Total Loss:      ₹{stats['total_loss']:,.0f}")
        print(f"  Avg Win:         ₹{stats['avg_win']:,.0f}")
        print(f"  Avg Loss:        ₹{stats['avg_loss']:,.0f}")
        print(f"  Profit Factor:   {stats['profit_factor']:.2f}")
        
        print(f"\n📉 RISK METRICS:")
        print(f"  Max Drawdown:    {stats['max_drawdown']:.2f}%")
        
        print(f"\n{'='*80}")
        print("📝 SAMPLE TRADES (First 10):")
        print(f"{'='*80}")
        
        for i, trade in enumerate(stats['trades'][:10]):
            print(f"\nTrade #{i+1}:")
            print(f"  Date: {trade['date']} {trade['entry_time']}")
            print(f"  Side: {trade['side']} | Signal: {trade['signal']}")
            print(f"  Entry: ₹{trade['entry']:.2f} | Exit: ₹{trade['exit_price']:.2f}")
            print(f"  SL: ₹{trade['stop_loss']:.2f} | Target: ₹{trade['target']:.2f}")
            print(f"  Exit Reason: {trade['exit_reason']}")
            print(f"  LLM Reasoning: {trade.get('llm_reasoning', 'N/A')}")
            print(f"  LLM Confidence: {trade.get('llm_confidence', 0)}%")
            print(f"  P&L: ₹{trade['pnl']:,.0f} {'✅' if trade['pnl'] > 0 else '❌'}")
        
        print(f"\n{'='*80}")


if __name__ == "__main__":
    backtester = VWAPLLMBacktester(
        symbol="RELIANCE",
        security_id="2885",
        initial_capital=100000
    )
    
    stats = backtester.run_backtest(days=90)
    
    if stats['status'] == 'COMPLETED':
        backtester.print_results(stats)
