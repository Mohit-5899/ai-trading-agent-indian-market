import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from dhanhq import dhanhq
from vwap_calculator import VWAPCalculator
import pandas as pd

load_dotenv()

class VWAPBacktester:
    """
    Backtest VWAP Breakout & Retest Strategy
    - 5-minute timeframe
    - 2% risk per trade
    - 1:3 Risk-Reward ratio
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
        
        self.trades = []
        self.equity_curve = []
        
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
    
    def backtest_day(self, day_data: Dict) -> List[Dict]:
        """
        Backtest a single trading day
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
            prev_close = data['close'][i-1]
            prev_vwap = vwap[i-1]
            
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
                            'vwap': current_vwap
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
                            'vwap': current_vwap
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
        Run complete backtest
        """
        print(f"\n{'='*80}")
        print(f"🔄 VWAP STRATEGY BACKTEST - {self.symbol}")
        print(f"{'='*80}")
        print(f"Initial Capital: ₹{self.initial_capital:,.0f}")
        print(f"Risk per trade: {self.risk_pct}%")
        print(f"Risk:Reward: 1:{self.risk_reward_ratio}")
        print(f"Backtesting Period: Last {days} days")
        
        data = self.fetch_historical_data(days)
        if not data:
            return {'status': 'FAILED', 'reason': 'No data'}
        
        trading_days = self.split_by_trading_day(data)
        print(f"\n📅 Total Trading Days: {len(trading_days)}")
        
        print(f"\n{'='*80}")
        print("🔄 Running Backtest...")
        print(f"{'='*80}")
        
        for day in trading_days:
            day_trades = self.backtest_day(day)
            self.trades.extend(day_trades)
            self.equity_curve.append({
                'date': day['date'],
                'capital': self.capital
            })
        
        return self.calculate_statistics()
    
    def calculate_statistics(self) -> Dict:
        """
        Calculate backtest statistics
        """
        if not self.trades:
            return {
                'status': 'NO_TRADES',
                'total_trades': 0
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
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
    
    def print_results(self, stats: Dict):
        """
        Print backtest results
        """
        print(f"\n{'='*80}")
        print("📊 BACKTEST RESULTS")
        print(f"{'='*80}")
        
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
            print(f"  P&L: ₹{trade['pnl']:,.0f} {'✅' if trade['pnl'] > 0 else '❌'}")
        
        print(f"\n{'='*80}")


if __name__ == "__main__":
    backtester = VWAPBacktester(
        symbol="RELIANCE",
        security_id="2885",
        initial_capital=100000
    )
    
    stats = backtester.run_backtest(days=90)
    
    if stats['status'] == 'COMPLETED':
        backtester.print_results(stats)
