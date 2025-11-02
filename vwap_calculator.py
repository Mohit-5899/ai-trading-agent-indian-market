import numpy as np
from typing import Dict, List, Tuple

class VWAPCalculator:
    """
    Calculate VWAP (Volume Weighted Average Price) for intraday trading
    """
    
    @staticmethod
    def calculate_vwap(data: Dict) -> List[float]:
        """
        Calculate VWAP from candle data
        
        Args:
            data: Dictionary with 'high', 'low', 'close', 'volume', 'timestamp'
            
        Returns:
            List of VWAP values for each candle
        """
        if not data or not data.get('timestamp'):
            return []
        
        highs = np.array(data['high'])
        lows = np.array(data['low'])
        closes = np.array(data['close'])
        volumes = np.array(data['volume'])
        
        typical_price = (highs + lows + closes) / 3
        
        cumulative_tpv = np.cumsum(typical_price * volumes)
        cumulative_volume = np.cumsum(volumes)
        
        vwap = cumulative_tpv / cumulative_volume
        
        return vwap.tolist()
    
    @staticmethod
    def calculate_vwap_bands(vwap: List[float], data: Dict, std_multiplier: float = 1.0) -> Tuple[List[float], List[float]]:
        """
        Calculate VWAP standard deviation bands
        
        Args:
            vwap: List of VWAP values
            data: Candle data
            std_multiplier: Standard deviation multiplier (default 1.0)
            
        Returns:
            Tuple of (upper_band, lower_band)
        """
        if not vwap or not data:
            return [], []
        
        highs = np.array(data['high'])
        lows = np.array(data['low'])
        closes = np.array(data['close'])
        volumes = np.array(data['volume'])
        
        typical_price = (highs + lows + closes) / 3
        vwap_array = np.array(vwap)
        
        squared_diff = (typical_price - vwap_array) ** 2
        cumulative_squared_diff = np.cumsum(squared_diff * volumes)
        cumulative_volume = np.cumsum(volumes)
        
        variance = cumulative_squared_diff / cumulative_volume
        std_dev = np.sqrt(variance)
        
        upper_band = vwap_array + (std_dev * std_multiplier)
        lower_band = vwap_array - (std_dev * std_multiplier)
        
        return upper_band.tolist(), lower_band.tolist()
    
    @staticmethod
    def detect_vwap_breakout(data: Dict, vwap: List[float], current_idx: int = -1) -> Dict:
        """
        Detect VWAP breakout/breakdown
        
        Returns:
            {
                'signal': 'BULLISH_BREAKOUT' | 'BEARISH_BREAKDOWN' | 'RETEST' | 'NEUTRAL',
                'price': current_price,
                'vwap': current_vwap,
                'distance_pct': distance from vwap in percentage
            }
        """
        if not data or not vwap:
            return {'signal': 'NEUTRAL', 'price': 0, 'vwap': 0, 'distance_pct': 0}
        
        closes = data['close']
        current_price = closes[current_idx]
        current_vwap = vwap[current_idx]
        
        distance_pct = ((current_price - current_vwap) / current_vwap) * 100
        
        prev_close = closes[current_idx - 1] if current_idx > 0 else current_price
        prev_vwap = vwap[current_idx - 1] if current_idx > 0 else current_vwap
        
        signal = 'NEUTRAL'
        
        if prev_close < prev_vwap and current_price > current_vwap:
            signal = 'BULLISH_BREAKOUT'
        elif prev_close > prev_vwap and current_price < current_vwap:
            signal = 'BEARISH_BREAKDOWN'
        elif abs(distance_pct) < 0.3:
            if prev_close > prev_vwap:
                signal = 'BULLISH_RETEST'
            else:
                signal = 'BEARISH_RETEST'
        
        return {
            'signal': signal,
            'price': current_price,
            'vwap': current_vwap,
            'distance_pct': distance_pct
        }
    
    @staticmethod
    def calculate_position_size(account_value: float, risk_pct: float, entry_price: float, stop_loss_price: float) -> int:
        """
        Calculate position size based on 2% risk
        
        Args:
            account_value: Total account value in INR
            risk_pct: Risk percentage (default 2%)
            entry_price: Entry price
            stop_loss_price: Stop loss price
            
        Returns:
            Number of shares to buy
        """
        risk_amount = account_value * (risk_pct / 100)
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return 0
        
        quantity = int(risk_amount / risk_per_share)
        
        return max(1, quantity)
    
    @staticmethod
    def calculate_targets(entry_price: float, stop_loss_price: float, risk_reward_ratio: float = 3.0) -> Dict:
        """
        Calculate take profit targets based on R:R ratio
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_reward_ratio: Risk to reward ratio (default 1:3)
            
        Returns:
            Dictionary with stop_loss, target1, target2, target3
        """
        risk = abs(entry_price - stop_loss_price)
        reward = risk * risk_reward_ratio
        
        is_long = entry_price > stop_loss_price
        
        if is_long:
            target = entry_price + reward
        else:
            target = entry_price - reward
        
        return {
            'entry': entry_price,
            'stop_loss': stop_loss_price,
            'target': target,
            'risk': risk,
            'reward': reward,
            'risk_reward_ratio': risk_reward_ratio
        }
