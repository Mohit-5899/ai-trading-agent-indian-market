import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from market_data_manager import MarketDataManager
from vwap_calculator import VWAPCalculator
from datetime import datetime

load_dotenv()

class VWAPTradingAgent:
    """
    LLM-powered VWAP Breakout & Retest Trading Agent
    Strategy:
    - 5-minute timeframe
    - VWAP breakout/retest entries
    - 2% risk per trade
    - 1:3 Risk-Reward ratio
    """
    
    def __init__(self, symbol: str, account_value: float = 100000):
        self.symbol = symbol
        self.account_value = account_value
        self.risk_pct = 2.0
        self.risk_reward_ratio = 3.0
        
        self.data_manager = MarketDataManager(
            symbols=[symbol],
            env_path='/Users/mohitmandawat/Coding/CodeTrading/ai-trading-agent-indian-market/.env'
        )
        self.vwap_calc = VWAPCalculator()
        
        self.openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        self.current_position = None
    
    def get_market_context(self) -> str:
        """
        Fetch and format market data with VWAP analysis
        """
        data = self.data_manager.get_all_timeframes(self.symbol)
        
        min_5_data = data.get('min_5', {})
        if not min_5_data or not min_5_data.get('timestamp'):
            return "No market data available"
        
        vwap = self.vwap_calc.calculate_vwap(min_5_data)
        upper_band, lower_band = self.vwap_calc.calculate_vwap_bands(vwap, min_5_data, std_multiplier=1.0)
        
        vwap_signal = self.vwap_calc.detect_vwap_breakout(min_5_data, vwap, current_idx=-1)
        
        base_context = self.data_manager.format_for_llm(data, format_type='toon')
        
        timestamps = min_5_data['timestamp']
        closes = min_5_data['close']
        
        vwap_context = f"\n\nVWAP_ANALYSIS[{self.symbol}]:\n"
        vwap_context += f"Current Signal: {vwap_signal['signal']}\n"
        vwap_context += f"Current Price: {vwap_signal['price']:.2f}\n"
        vwap_context += f"Current VWAP: {vwap_signal['vwap']:.2f}\n"
        vwap_context += f"Distance from VWAP: {vwap_signal['distance_pct']:.2f}%\n\n"
        
        vwap_context += "vwap_data[20]{datetime,close,vwap,upper_band,lower_band}:\n"
        
        start_idx = max(0, len(timestamps) - 20)
        for i in range(start_idx, len(timestamps)):
            dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
            vwap_context += f" {dt},{closes[i]:.2f},{vwap[i]:.2f},{upper_band[i]:.2f},{lower_band[i]:.2f}\n"
        
        return base_context + vwap_context
    
    def generate_trading_prompt(self, market_context: str) -> str:
        """
        Generate LLM prompt for trading decision
        """
        prompt = f"""You are an expert VWAP breakout trader managing a ₹{self.account_value:,.0f} account.

STRATEGY RULES:
- Trade on 5-minute timeframe only
- Enter on VWAP breakout/retest
- Risk: {self.risk_pct}% per trade (₹{self.account_value * self.risk_pct / 100:,.0f})
- Risk-Reward: 1:{self.risk_reward_ratio}
- Stop loss: Below VWAP for long, Above VWAP for short
- Target: {self.risk_reward_ratio}x the risk

ENTRY SIGNALS:
1. BULLISH_BREAKOUT: Price crosses above VWAP with momentum
2. BULLISH_RETEST: Price retests VWAP from above and holds
3. BEARISH_BREAKDOWN: Price crosses below VWAP with momentum
4. BEARISH_RETEST: Price retests VWAP from below and holds

CURRENT POSITION:
{f"LONG {self.current_position['quantity']} shares @ ₹{self.current_position['entry_price']:.2f}, SL: ₹{self.current_position['stop_loss']:.2f}, Target: ₹{self.current_position['target']:.2f}" if self.current_position else "NO POSITION"}

MARKET DATA:
{market_context}

INSTRUCTIONS:
Analyze the market structure, VWAP position, and recent price action.
Decide whether to:
1. ENTER LONG - if bullish breakout/retest setup
2. ENTER SHORT - if bearish breakdown/retest setup  
3. EXIT POSITION - if stop loss hit or target reached
4. HOLD - if no clear setup or position is still valid

Respond ONLY with valid JSON:
{{
  "action": "ENTER_LONG" | "ENTER_SHORT" | "EXIT" | "HOLD",
  "reasoning": "Brief explanation of your decision based on VWAP analysis",
  "entry_price": price_to_enter_if_applicable,
  "stop_loss": stop_loss_price_if_applicable,
  "confidence": 0-100
}}"""
        
        return prompt
    
    def calculate_trade_parameters(self, action: str, entry_price: float) -> Optional[Dict]:
        """
        Calculate position size, stop loss, and target
        """
        min_5_data = self.data_manager.get_all_timeframes(self.symbol).get('min_5', {})
        if not min_5_data:
            return None
        
        vwap = self.vwap_calc.calculate_vwap(min_5_data)
        current_vwap = vwap[-1]
        
        if action == "ENTER_LONG":
            stop_loss = current_vwap * 0.998
        elif action == "ENTER_SHORT":
            stop_loss = current_vwap * 1.002
        else:
            return None
        
        quantity = self.vwap_calc.calculate_position_size(
            self.account_value,
            self.risk_pct,
            entry_price,
            stop_loss
        )
        
        targets = self.vwap_calc.calculate_targets(
            entry_price,
            stop_loss,
            self.risk_reward_ratio
        )
        
        return {
            'action': action,
            'entry_price': entry_price,
            'stop_loss': targets['stop_loss'],
            'target': targets['target'],
            'quantity': quantity,
            'risk_amount': self.account_value * self.risk_pct / 100,
            'potential_profit': targets['reward'] * quantity,
            'vwap_reference': current_vwap
        }
    
    def format_trade_signal(self, trade_params: Dict) -> str:
        """
        Format trade signal for display
        """
        if not trade_params:
            return "NO TRADE SIGNAL"
        
        signal = f"""
{'='*80}
🎯 TRADE SIGNAL - {self.symbol}
{'='*80}
Action: {trade_params['action']}
Entry Price: ₹{trade_params['entry_price']:.2f}
Stop Loss: ₹{trade_params['stop_loss']:.2f}
Target: ₹{trade_params['target']:.2f}
Quantity: {trade_params['quantity']} shares

VWAP Reference: ₹{trade_params['vwap_reference']:.2f}
Risk per trade: ₹{trade_params['risk_amount']:.2f} ({self.risk_pct}%)
Potential Profit: ₹{trade_params['potential_profit']:.2f}
Risk:Reward = 1:{self.risk_reward_ratio}
{'='*80}
"""
        return signal
    
    def get_llm_decision(self, trading_prompt: str) -> Dict:
        """
        Get trading decision from LLM via OpenRouter
        """
        try:
            print("\n🤖 Calling DeepSeek LLM via OpenRouter...")
            
            completion = self.openrouter_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/ai-trading-agent",
                    "X-Title": "AI Trading Agent"
                },
                model="deepseek/deepseek-chat-v3-0324",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert VWAP breakout trader. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": trading_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = completion.choices[0].message.content
            print(f"\n📝 LLM Response:\n{response_text}")
            
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            llm_decision = json.loads(response_text)
            
            return llm_decision
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {response_text}")
            return {'action': 'HOLD', 'reasoning': 'Failed to parse LLM response', 'confidence': 0}
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return {'action': 'HOLD', 'reasoning': f'Error: {str(e)}', 'confidence': 0}
    
    def execute_trade_decision(self, llm_response: Dict) -> Optional[Dict]:
        """
        Execute the LLM's trading decision
        """
        action = llm_response.get('action', 'HOLD')
        
        if action in ['ENTER_LONG', 'ENTER_SHORT']:
            entry_price = llm_response.get('entry_price')
            if not entry_price:
                return None
            
            trade_params = self.calculate_trade_parameters(action, entry_price)
            
            if trade_params:
                self.current_position = {
                    'action': action,
                    'entry_price': trade_params['entry_price'],
                    'stop_loss': trade_params['stop_loss'],
                    'target': trade_params['target'],
                    'quantity': trade_params['quantity'],
                    'entry_time': datetime.now()
                }
                
                return trade_params
        
        elif action == 'EXIT' and self.current_position:
            exit_info = self.current_position.copy()
            self.current_position = None
            return {'action': 'EXIT', 'details': exit_info}
        
        return {'action': 'HOLD'}
    
    def run_trading_cycle(self, call_llm: bool = True) -> Dict:
        """
        Run a complete trading cycle:
        1. Fetch market data
        2. Generate LLM prompt
        3. Get LLM decision
        4. Execute trade
        """
        print(f"\n{'='*80}")
        print(f"🤖 VWAP TRADING AGENT - {self.symbol}")
        print(f"{'='*80}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Account Value: ₹{self.account_value:,.0f}")
        print(f"Risk per trade: {self.risk_pct}% (₹{self.account_value * self.risk_pct / 100:,.0f})")
        
        market_context = self.get_market_context()
        
        print("\n📊 Market Context Generated")
        print(f"Context size: ~{len(market_context.split())} words")
        
        trading_prompt = self.generate_trading_prompt(market_context)
        
        print("\n💭 LLM Prompt Generated")
        print(f"Prompt size: ~{len(trading_prompt.split())} words")
        
        if not call_llm:
            print("\n📝 FULL LLM PROMPT:")
            print("="*80)
            print(trading_prompt)
            return {
                'status': 'READY',
                'prompt': trading_prompt,
                'market_context': market_context,
                'timestamp': datetime.now().isoformat()
            }
        
        llm_decision = self.get_llm_decision(trading_prompt)
        
        print(f"\n{'='*80}")
        print("📊 LLM DECISION")
        print(f"{'='*80}")
        print(f"Action: {llm_decision.get('action', 'UNKNOWN')}")
        print(f"Reasoning: {llm_decision.get('reasoning', 'N/A')}")
        print(f"Confidence: {llm_decision.get('confidence', 0)}%")
        
        trade_result = self.execute_trade_decision(llm_decision)
        
        if trade_result and trade_result.get('action') in ['ENTER_LONG', 'ENTER_SHORT']:
            signal = self.format_trade_signal(trade_result)
            print(signal)
        elif trade_result and trade_result.get('action') == 'EXIT':
            print(f"\n{'='*80}")
            print("🚪 EXIT POSITION")
            print(f"{'='*80}")
            print(f"Position closed: {trade_result.get('details', {})}")
        else:
            print(f"\n{'='*80}")
            print("⏸️  HOLD - No action taken")
            print(f"{'='*80}")
        
        return {
            'status': 'COMPLETED',
            'llm_decision': llm_decision,
            'trade_result': trade_result,
            'timestamp': datetime.now().isoformat()
        }
