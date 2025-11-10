"""
VWAP Strategy Implementation
Based on the proven VWAP breakout/retest strategy with 39.74% return
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

from strategies.base_strategy import BaseStrategy
from vwap_calculator import VWAPCalculator  # Use existing proven implementation

logger = logging.getLogger(__name__)

class VWAPStrategy(BaseStrategy):
    """
    VWAP Breakout/Retest Strategy
    
    Proven strategy with 39.74% return from backtesting
    Entry signals:
    1. BULLISH_BREAKOUT: Price crosses above VWAP with momentum
    2. BULLISH_RETEST: Price retests VWAP from above and holds
    3. BEARISH_BREAKDOWN: Price crosses below VWAP with momentum  
    4. BEARISH_RETEST: Price retests VWAP from below and holds
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        default_params = {
            'risk_per_trade': 2.0,
            'risk_reward_ratio': 3.0,
            'timeframe': '5m',
            'momentum_threshold': 0.5,
            'retest_tolerance': 0.1,
            'volume_threshold': 1.2,  # 20% above average
            'confirmation_candles': 2
        }
        
        if parameters:
            default_params.update(parameters)
            
        super().__init__("VWAP Breakout/Retest", default_params)
        
        # Initialize the proven VWAP calculator
        self.vwap_calc = VWAPCalculator()
        
        # Strategy-specific parameters
        self.momentum_threshold = self.parameters.get('momentum_threshold', 0.5)
        self.retest_tolerance = self.parameters.get('retest_tolerance', 0.1)
        self.volume_threshold = self.parameters.get('volume_threshold', 1.2)
        self.confirmation_candles = self.parameters.get('confirmation_candles', 2)
    
    async def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate VWAP-based trading signals
        Uses the proven VWAP calculator implementation
        """
        try:
            # Extract relevant timeframe data (5m for VWAP strategy)
            timeframe_data = market_data.get(self.timeframe, {})
            
            if not timeframe_data or not timeframe_data.get('close'):
                return self._no_signal("Insufficient market data")
            
            # Calculate VWAP using proven implementation
            vwap = self.vwap_calc.calculate_vwap(timeframe_data)
            
            if not vwap:
                return self._no_signal("VWAP calculation failed")
            
            # Detect VWAP signals using existing implementation
            signal_result = self.vwap_calc.detect_vwap_breakout(
                timeframe_data, 
                vwap, 
                current_idx=-1  # Latest candle
            )
            
            if not signal_result:
                return self._no_signal("No VWAP signal detected")
            
            # Enhanced signal analysis
            enhanced_signal = await self._analyze_signal_strength(
                signal_result, timeframe_data, vwap
            )
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Error generating VWAP signals: {e}")
            return self._no_signal(f"Error: {str(e)}")
    
    async def _analyze_signal_strength(
        self, 
        base_signal: Dict[str, Any], 
        market_data: Dict[str, Any], 
        vwap: List[float]
    ) -> Dict[str, Any]:
        """
        Analyze and enhance the signal with additional filters
        """
        try:
            signal_type = base_signal.get('type', 'NONE')
            current_price = float(market_data['close'][-1])
            current_vwap = float(vwap[-1])
            
            # Base signal strength from VWAP calculator
            base_strength = base_signal.get('strength', 50.0)
            
            # Calculate enhanced metrics
            volume_strength = await self._analyze_volume(market_data)
            momentum_strength = await self._analyze_momentum(market_data, vwap)
            pattern_strength = await self._analyze_pattern(signal_type, market_data, vwap)
            
            # Combine strengths (weighted average)
            final_strength = (
                base_strength * 0.4 +          # 40% base VWAP signal
                volume_strength * 0.25 +       # 25% volume confirmation
                momentum_strength * 0.25 +     # 25% momentum
                pattern_strength * 0.1         # 10% pattern quality
            )
            
            # Calculate confidence based on signal quality
            confidence = await self._calculate_confidence(
                signal_type, final_strength, market_data, vwap
            )
            
            # Determine entry/exit prices
            entry_price = current_price
            stop_loss = await self._calculate_vwap_stop_loss(
                entry_price, signal_type, current_vwap
            )
            target = self.calculate_target(entry_price, stop_loss, 
                                         'LONG' if 'BULLISH' in signal_type else 'SHORT')
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(
                signal_type, final_strength, confidence, 
                current_price, current_vwap, base_signal
            )
            
            return {
                'signal': self._map_signal_type(signal_type),
                'strength': min(100, max(0, final_strength)),
                'confidence': min(100, max(0, confidence)),
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'vwap_price': current_vwap,
                'signal_details': {
                    'vwap_signal_type': signal_type,
                    'volume_strength': volume_strength,
                    'momentum_strength': momentum_strength,
                    'pattern_strength': pattern_strength,
                    'price_vwap_diff': ((current_price - current_vwap) / current_vwap) * 100
                },
                'reasoning': reasoning,
                'strategy': self.name,
                'timeframe': self.timeframe,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing signal strength: {e}")
            return self._no_signal(f"Analysis error: {str(e)}")
    
    async def _analyze_volume(self, market_data: Dict[str, Any]) -> float:
        """Analyze volume confirmation"""
        try:
            volumes = market_data.get('volume', [])
            if len(volumes) < 10:
                return 50.0  # Neutral if insufficient data
            
            current_volume = volumes[-1]
            avg_volume = np.mean(volumes[-20:])  # 20-period average
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Score based on volume threshold
            if volume_ratio >= self.volume_threshold:
                return min(100, 50 + (volume_ratio - 1) * 50)
            else:
                return max(0, 50 * volume_ratio)
                
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return 50.0
    
    async def _analyze_momentum(
        self, 
        market_data: Dict[str, Any], 
        vwap: List[float]
    ) -> float:
        """Analyze price momentum relative to VWAP"""
        try:
            closes = market_data.get('close', [])
            if len(closes) < 5 or len(vwap) < 5:
                return 50.0
            
            # Calculate price momentum (price change over last 5 periods)
            price_change = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] > 0 else 0
            
            # Calculate VWAP momentum
            vwap_change = (vwap[-1] - vwap[-5]) / vwap[-5] if vwap[-5] > 0 else 0
            
            # Score momentum alignment
            momentum_score = 50  # Base score
            
            # Bonus for strong momentum in same direction
            if price_change > 0 and vwap_change > 0:
                momentum_score += min(50, abs(price_change) * 1000)
            elif price_change < 0 and vwap_change < 0:
                momentum_score += min(50, abs(price_change) * 1000)
            
            return min(100, max(0, momentum_score))
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {e}")
            return 50.0
    
    async def _analyze_pattern(
        self, 
        signal_type: str, 
        market_data: Dict[str, Any], 
        vwap: List[float]
    ) -> float:
        """Analyze chart pattern quality"""
        try:
            closes = market_data.get('close', [])
            if len(closes) < 10:
                return 50.0
            
            pattern_score = 50  # Base score
            
            # Analyze based on signal type
            if signal_type in ['BULLISH_BREAKOUT', 'BEARISH_BREAKDOWN']:
                # For breakouts, look for clean break with follow-through
                pattern_score += self._score_breakout_quality(closes, vwap)
                
            elif signal_type in ['BULLISH_RETEST', 'BEARISH_RETEST']:
                # For retests, look for bounce off VWAP level
                pattern_score += self._score_retest_quality(closes, vwap)
            
            return min(100, max(0, pattern_score))
            
        except Exception as e:
            logger.error(f"Error analyzing pattern: {e}")
            return 50.0
    
    def _score_breakout_quality(self, closes: List[float], vwap: List[float]) -> float:
        """Score the quality of a breakout"""
        try:
            # Check for clean break (price clearly above/below VWAP)
            recent_closes = closes[-3:]
            recent_vwap = vwap[-3:]
            
            clean_break_score = 0
            for i, (price, vwap_val) in enumerate(zip(recent_closes, recent_vwap)):
                if abs(price - vwap_val) / vwap_val > 0.002:  # 0.2% threshold
                    clean_break_score += 10
            
            return clean_break_score
            
        except Exception:
            return 0
    
    def _score_retest_quality(self, closes: List[float], vwap: List[float]) -> float:
        """Score the quality of a retest"""
        try:
            # Check for bounce at VWAP level
            current_price = closes[-1]
            current_vwap = vwap[-1]
            
            # Distance from VWAP (closer is better for retest)
            distance = abs(current_price - current_vwap) / current_vwap
            
            if distance < 0.001:  # Very close to VWAP (0.1%)
                return 20
            elif distance < 0.002:  # Close to VWAP (0.2%)
                return 15
            elif distance < 0.005:  # Reasonable distance (0.5%)
                return 10
            else:
                return 0
                
        except Exception:
            return 0
    
    async def _calculate_confidence(
        self,
        signal_type: str,
        strength: float,
        market_data: Dict[str, Any],
        vwap: List[float]
    ) -> float:
        """Calculate confidence score for the signal"""
        try:
            base_confidence = 50
            
            # Higher confidence for stronger signals
            if strength > 80:
                base_confidence += 30
            elif strength > 60:
                base_confidence += 20
            elif strength > 40:
                base_confidence += 10
            
            # Additional confidence factors
            if self._has_sufficient_data(market_data):
                base_confidence += 10
            
            if self._is_trending_market(market_data):
                base_confidence += 10
            
            return min(100, base_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 50.0
    
    async def _calculate_vwap_stop_loss(
        self,
        entry_price: float,
        signal_type: str,
        current_vwap: float
    ) -> float:
        """Calculate stop loss based on VWAP levels"""
        try:
            if 'BULLISH' in signal_type:
                # For long positions, stop below VWAP
                stop_distance = current_vwap * 0.002  # 0.2% below VWAP
                return current_vwap - stop_distance
            else:
                # For short positions, stop above VWAP  
                stop_distance = current_vwap * 0.002  # 0.2% above VWAP
                return current_vwap + stop_distance
                
        except Exception as e:
            logger.error(f"Error calculating VWAP stop loss: {e}")
            return self.calculate_stop_loss(
                entry_price, 
                'LONG' if 'BULLISH' in signal_type else 'SHORT'
            )
    
    async def _generate_reasoning(
        self,
        signal_type: str,
        strength: float,
        confidence: float,
        current_price: float,
        current_vwap: float,
        base_signal: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for the signal"""
        try:
            price_vwap_diff = ((current_price - current_vwap) / current_vwap) * 100
            
            reasoning = f"VWAP Strategy Signal: {signal_type}\n"
            reasoning += f"Current Price: ₹{current_price:.2f}, VWAP: ₹{current_vwap:.2f} "
            reasoning += f"({price_vwap_diff:+.2f}%)\n"
            
            if signal_type == 'BULLISH_BREAKOUT':
                reasoning += "Price has broken above VWAP with momentum, indicating bullish sentiment. "
            elif signal_type == 'BULLISH_RETEST':
                reasoning += "Price is retesting VWAP from above, showing support at this level. "
            elif signal_type == 'BEARISH_BREAKDOWN':
                reasoning += "Price has broken below VWAP with momentum, indicating bearish sentiment. "
            elif signal_type == 'BEARISH_RETEST':
                reasoning += "Price is retesting VWAP from below, showing resistance at this level. "
            
            reasoning += f"Signal strength: {strength:.1f}%, Confidence: {confidence:.1f}%. "
            
            if strength > 70:
                reasoning += "Strong signal quality with good confirmation. "
            elif strength > 50:
                reasoning += "Moderate signal quality, proceed with caution. "
            else:
                reasoning += "Weak signal quality, consider waiting for better setup. "
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return f"VWAP signal: {signal_type} with {strength:.1f}% strength"
    
    def _map_signal_type(self, vwap_signal_type: str) -> str:
        """Map VWAP signal types to standard signal types"""
        if vwap_signal_type in ['BULLISH_BREAKOUT', 'BULLISH_RETEST']:
            return 'BUY'
        elif vwap_signal_type in ['BEARISH_BREAKDOWN', 'BEARISH_RETEST']:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _has_sufficient_data(self, market_data: Dict[str, Any]) -> bool:
        """Check if we have sufficient data for analysis"""
        try:
            required_candles = 20
            return (len(market_data.get('close', [])) >= required_candles and
                   len(market_data.get('volume', [])) >= required_candles)
        except Exception:
            return False
    
    def _is_trending_market(self, market_data: Dict[str, Any]) -> bool:
        """Check if market is in a trending phase"""
        try:
            closes = market_data.get('close', [])
            if len(closes) < 20:
                return False
            
            # Simple trend detection using 20-period slope
            recent_closes = closes[-20:]
            x = range(len(recent_closes))
            slope = np.polyfit(x, recent_closes, 1)[0]
            
            # Consider trending if slope is significant
            avg_price = np.mean(recent_closes)
            slope_percent = (slope / avg_price) * 100
            
            return abs(slope_percent) > 0.1  # 0.1% slope threshold
            
        except Exception:
            return False
    
    def _no_signal(self, reason: str) -> Dict[str, Any]:
        """Return a no-signal response"""
        return {
            'signal': 'HOLD',
            'strength': 0,
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'target': 0,
            'reasoning': f"No VWAP signal: {reason}",
            'strategy': self.name,
            'timeframe': self.timeframe,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def calculate_position_size(
        self, 
        signal: Dict[str, Any], 
        account_value: float,
        current_price: float
    ) -> int:
        """
        Calculate position size using VWAP strategy risk management
        Uses the proven 2% risk per trade approach
        """
        try:
            if signal.get('signal') == 'HOLD':
                return 0
            
            entry_price = signal.get('entry_price', current_price)
            stop_loss = signal.get('stop_loss', 0)
            
            # Use existing VWAP calculator method
            quantity = self.vwap_calc.calculate_position_size(
                account_value=account_value,
                risk_pct=self.risk_per_trade,
                entry_price=entry_price,
                stop_loss_price=stop_loss
            )
            
            return max(1, quantity)  # Minimum 1 share
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 1  # Conservative fallback
    
    async def validate_entry(
        self, 
        signal: Dict[str, Any], 
        market_data: Dict[str, Any],
        current_positions: List[Dict[str, Any]]
    ) -> bool:
        """
        Validate VWAP entry conditions
        """
        try:
            if signal.get('signal') == 'HOLD':
                return False
            
            # Check signal strength threshold
            if signal.get('strength', 0) < 30:  # Minimum 30% strength
                return False
            
            # Check confidence threshold
            if signal.get('confidence', 0) < 40:  # Minimum 40% confidence
                return False
            
            # Check if we already have a position in this symbol
            # (VWAP strategy typically allows only one position per symbol)
            # This would be implemented based on current_positions data
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating VWAP entry: {e}")
            return False