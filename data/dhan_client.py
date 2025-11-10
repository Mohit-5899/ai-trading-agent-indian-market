"""
Enhanced Dhan API Client
Wraps the existing Dhan integration with async support and additional features
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from dhanhq import dhanhq
from models.database import TradingAccount
from config.settings import get_settings

logger = logging.getLogger(__name__)

class DhanClient:
    """
    Enhanced Dhan API client with async support
    Handles all trading operations through Dhan API
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.clients = {}  # Store multiple client instances for different accounts
        
    async def initialize(self):
        """Initialize Dhan clients"""
        logger.info("Initializing Dhan API clients")
        
        # Test with default credentials if available
        try:
            if self.settings.dhan_client_id and self.settings.dhan_access_token:
                test_client = dhanhq(
                    self.settings.dhan_client_id, 
                    self.settings.dhan_access_token
                )
                
                # Test connection
                await self._async_wrapper(test_client.get_fund_limits)
                logger.info("Default Dhan API connection successful")
            
        except Exception as e:
            logger.warning(f"Default Dhan API connection failed: {e}")
    
    async def shutdown(self):
        """Shutdown Dhan clients"""
        self.clients.clear()
        logger.info("Dhan API clients shutdown")
    
    def _get_client(self, account: TradingAccount) -> dhanhq:
        """Get or create Dhan client for specific account"""
        account_id = account.id
        
        if account_id not in self.clients:
            self.clients[account_id] = dhanhq(
                account.dhan_client_id,
                account.dhan_access_token
            )
        
        return self.clients[account_id]
    
    async def get_portfolio(self, account: TradingAccount) -> Dict[str, Any]:
        """
        Get portfolio information for account
        """
        try:
            client = self._get_client(account)
            
            # Get fund limits
            fund_limits = await self._async_wrapper(client.get_fund_limits)
            
            # Get positions
            positions = await self._async_wrapper(client.get_positions)
            
            # Calculate portfolio metrics
            available_cash = float(fund_limits.get('available_balance', 0))
            invested_amount = 0
            day_pnl = 0
            
            if positions and 'data' in positions:
                for position in positions['data']:
                    if position.get('qty', 0) != 0:  # Open position
                        invested_amount += float(position.get('costPrice', 0)) * abs(float(position.get('qty', 0)))
                        day_pnl += float(position.get('unrealizedPnl', 0))
            
            total_value = available_cash + invested_amount + day_pnl
            
            return {
                'total_value': total_value,
                'available_cash': available_cash,
                'invested_amount': invested_amount,
                'day_pnl': day_pnl,
                'fund_limits': fund_limits,
                'positions_data': positions
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio for account {account.name}: {e}")
            return {
                'total_value': 0,
                'available_cash': 0,
                'invested_amount': 0,
                'day_pnl': 0,
                'error': str(e)
            }
    
    async def get_positions(self, account: TradingAccount) -> List[Dict[str, Any]]:
        """
        Get current positions for account
        """
        try:
            client = self._get_client(account)
            positions_response = await self._async_wrapper(client.get_positions)
            
            if not positions_response or 'data' not in positions_response:
                return []
            
            formatted_positions = []
            for position in positions_response['data']:
                if position.get('qty', 0) != 0:  # Only open positions
                    formatted_positions.append({
                        'symbol': position.get('tradingSymbol', ''),
                        'quantity': int(position.get('qty', 0)),
                        'current_price': float(position.get('ltp', 0)),
                        'average_price': float(position.get('costPrice', 0)),
                        'pnl': float(position.get('unrealizedPnl', 0)),
                        'day_change': float(position.get('dayChange', 0)),
                        'day_change_percent': float(position.get('dayChangePercentage', 0)),
                        'security_id': position.get('securityId', ''),
                        'exchange': position.get('exchangeSegment', ''),
                        'position_type': 'LONG' if int(position.get('qty', 0)) > 0 else 'SHORT'
                    })
            
            return formatted_positions
            
        except Exception as e:
            logger.error(f"Error getting positions for account {account.name}: {e}")
            return []
    
    async def place_buy_order(
        self, 
        account: TradingAccount, 
        symbol: str, 
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a buy order through Dhan API
        """
        try:
            client = self._get_client(account)
            
            # Get security ID from symbol
            security_id = self._get_security_id(symbol)
            
            # Prepare order parameters
            order_params = {
                'security_id': security_id,
                'exchange_segment': dhanhq.NSE,
                'transaction_type': dhanhq.BUY,
                'quantity': quantity,
                'order_type': dhanhq.MARKET if order_type == "MARKET" else dhanhq.LIMIT,
                'product_type': dhanhq.INTRADAY,  # Can be changed to DELIVERY
                'validity': dhanhq.DAY
            }
            
            if order_type == "LIMIT" and price:
                order_params['price'] = price
            
            # Place order
            order_response = await self._async_wrapper(
                client.place_order, **order_params
            )
            
            logger.info(f"Buy order placed: {symbol} x {quantity} for account {account.name}")
            
            return {
                'order_id': order_response.get('data', {}).get('orderId'),
                'status': order_response.get('status'),
                'message': order_response.get('message', 'Order placed successfully'),
                'symbol': symbol,
                'quantity': quantity,
                'side': 'BUY',
                'order_type': order_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error placing buy order for {symbol}: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
                'quantity': quantity,
                'side': 'BUY',
                'status': 'FAILED'
            }
    
    async def place_sell_order(
        self,
        account: TradingAccount,
        symbol: str,
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a sell order through Dhan API
        """
        try:
            client = self._get_client(account)
            security_id = self._get_security_id(symbol)
            
            order_params = {
                'security_id': security_id,
                'exchange_segment': dhanhq.NSE,
                'transaction_type': dhanhq.SELL,
                'quantity': quantity,
                'order_type': dhanhq.MARKET if order_type == "MARKET" else dhanhq.LIMIT,
                'product_type': dhanhq.INTRADAY,
                'validity': dhanhq.DAY
            }
            
            if order_type == "LIMIT" and price:
                order_params['price'] = price
            
            order_response = await self._async_wrapper(
                client.place_order, **order_params
            )
            
            logger.info(f"Sell order placed: {symbol} x {quantity} for account {account.name}")
            
            return {
                'order_id': order_response.get('data', {}).get('orderId'),
                'status': order_response.get('status'),
                'message': order_response.get('message', 'Order placed successfully'),
                'symbol': symbol,
                'quantity': quantity,
                'side': 'SELL',
                'order_type': order_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error placing sell order for {symbol}: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
                'quantity': quantity,
                'side': 'SELL',
                'status': 'FAILED'
            }
    
    async def cancel_all_orders(self, account: TradingAccount) -> Dict[str, Any]:
        """
        Cancel all pending orders for account
        Equivalent to crypto system's cancelAllOrders
        """
        try:
            client = self._get_client(account)
            
            # Get all pending orders
            orders_response = await self._async_wrapper(client.get_order_list)
            
            cancelled_orders = []
            
            if orders_response and 'data' in orders_response:
                for order in orders_response['data']:
                    order_status = order.get('orderStatus', '')
                    if order_status in ['PENDING', 'OPEN', 'PARTIAL']:
                        try:
                            cancel_response = await self._async_wrapper(
                                client.cancel_order, order.get('orderId')
                            )
                            cancelled_orders.append({
                                'order_id': order.get('orderId'),
                                'symbol': order.get('tradingSymbol'),
                                'status': 'CANCELLED'
                            })
                        except Exception as e:
                            logger.error(f"Error cancelling order {order.get('orderId')}: {e}")
            
            logger.info(f"Cancelled {len(cancelled_orders)} orders for account {account.name}")
            
            return {
                'cancelled_orders': cancelled_orders,
                'count': len(cancelled_orders),
                'message': f'Successfully cancelled {len(cancelled_orders)} orders',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cancelling all orders for account {account.name}: {e}")
            return {
                'error': str(e),
                'cancelled_orders': [],
                'count': 0
            }
    
    async def get_order_status(self, account: TradingAccount, order_id: str) -> Dict[str, Any]:
        """Get status of a specific order"""
        try:
            client = self._get_client(account)
            order_response = await self._async_wrapper(client.get_order_by_id, order_id)
            
            if order_response and 'data' in order_response:
                order_data = order_response['data']
                return {
                    'order_id': order_data.get('orderId'),
                    'status': order_data.get('orderStatus'),
                    'symbol': order_data.get('tradingSymbol'),
                    'quantity': order_data.get('quantity'),
                    'filled_quantity': order_data.get('filledQty', 0),
                    'price': order_data.get('price'),
                    'average_price': order_data.get('avgPrice'),
                    'timestamp': order_data.get('createTime')
                }
            
            return {'error': 'Order not found'}
            
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {e}")
            return {'error': str(e)}
    
    def _get_security_id(self, symbol: str) -> str:
        """Get Dhan security ID for symbol"""
        from config.settings import INDIAN_STOCKS
        
        symbol = symbol.upper()
        if symbol in INDIAN_STOCKS:
            return INDIAN_STOCKS[symbol]['security_id']
        
        # Fallback mapping or raise error
        raise ValueError(f"Security ID not found for symbol: {symbol}")
    
    async def _async_wrapper(self, sync_func, *args, **kwargs):
        """Wrapper to run synchronous Dhan API calls asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_func, *args, **kwargs)
    
    async def test_connection(self, account: TradingAccount) -> Dict[str, Any]:
        """Test connection to Dhan API for specific account"""
        try:
            client = self._get_client(account)
            fund_limits = await self._async_wrapper(client.get_fund_limits)
            
            return {
                'status': 'success',
                'account_id': account.id,
                'account_name': account.name,
                'available_balance': fund_limits.get('available_balance', 0),
                'message': 'Dhan API connection successful'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'account_id': account.id,
                'account_name': account.name,
                'error': str(e),
                'message': 'Dhan API connection failed'
            }