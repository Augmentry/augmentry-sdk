"""
Augmentry API Client
Main client for interacting with the Augmentry API
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from .exceptions import AugmentryError, AuthenticationError, RateLimitError, APIError, ValidationError


class AugmentryClient:
    """
    Official Python client for the Augmentry API
    
    Args:
        api_key: Your Augmentry API key
        base_url: Base URL for the API (default: https://data.augmentry.io/api)
        timeout: Request timeout in seconds (default: 10)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://data.augmentry.io/api",
        timeout: int = 10
    ):
        if not api_key:
            raise ValidationError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
            
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self._session or self._session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Augmentry-Python-SDK/1.1.0'
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            API response data
            
        Raises:
            AugmentryError: For various API errors
        """
        await self._ensure_session()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=data,
                **kwargs
            ) as response:
                
                response_text = await response.text()
                
                # Handle different status codes
                if response.status == 401:
                    raise AuthenticationError("Invalid API key or authentication failed")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status >= 400:
                    try:
                        error_data = json.loads(response_text)
                        error_message = error_data.get('detail', f'HTTP {response.status}: {response.reason}')
                    except json.JSONDecodeError:
                        error_message = f'HTTP {response.status}: {response.reason}'
                    
                    raise APIError(error_message, response.status, response_text)
                
                # Parse successful response
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return {"data": response_text}
                    
        except aiohttp.ClientError as e:
            raise AugmentryError(f"Request failed: {str(e)}")
        except asyncio.TimeoutError:
            raise AugmentryError("Request timed out")
    
    # Token Endpoints
    async def get_token(self, token_address: str) -> Dict[str, Any]:
        """Get comprehensive token information with risk analysis"""
        return await self._make_request('GET', f'/tokens/{token_address}')
    
    async def get_token_holders(self, token_address: str, cursor: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get paginated list of token holders with balance information"""
        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', f'/tokens/{token_address}/holders', params=params)
    
    async def search_tokens(
        self, 
        q: Optional[str] = None,
        min_liquidity: Optional[float] = None,
        max_liquidity: Optional[float] = None,
        min_market_cap: Optional[float] = None,
        max_market_cap: Optional[float] = None,
        min_volume24h: Optional[float] = None,
        max_volume24h: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search tokens with filters"""
        params = {}
        if q:
            params['q'] = q
        if min_liquidity:
            params['minLiquidity'] = min_liquidity
        if max_liquidity:
            params['maxLiquidity'] = max_liquidity
        if min_market_cap:
            params['minMarketCap'] = min_market_cap
        if max_market_cap:
            params['maxMarketCap'] = max_market_cap
        if min_volume24h:
            params['minVolume24h'] = min_volume24h
        if max_volume24h:
            params['maxVolume24h'] = max_volume24h
        if sort_by:
            params['sortBy'] = sort_by
        if sort_order:
            params['sortOrder'] = sort_order
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', '/tokens/search', params=params)
    
    async def get_latest_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get latest newly created tokens"""
        params = {}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', '/tokens/latest', params=params)
    
    async def get_multi_tokens(self, tokens: List[str]) -> List[Dict[str, Any]]:
        """Batch request for multiple token details (up to 100 tokens)"""
        data = {'tokens': tokens}
        return await self._make_request('POST', '/tokens/multi', data=data)
    
    async def get_token_by_pool(self, pool_address: str) -> Dict[str, Any]:
        """Get token information by pool address across all DEXs"""
        return await self._make_request('GET', f'/pool/{pool_address}/token')
    
    async def get_tokens_by_deployer(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Get all tokens deployed by a specific wallet address"""
        return await self._make_request('GET', f'/deployer/{wallet_address}/tokens')
    
    # Price & Market Data
    async def get_price(self, token_address: str, include_price_changes: Optional[bool] = None) -> Dict[str, Any]:
        """Get real-time price with 24h/7d/30d changes and market cap"""
        params = {}
        if include_price_changes is not None:
            params['includePriceChanges'] = include_price_changes
        return await self._make_request('GET', f'/price/{token_address}', params=params)
    
    async def get_price_history(
        self, 
        token_address: str,
        interval: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Historical price data with customizable intervals (1m-1d)"""
        params = {}
        if interval:
            params['interval'] = interval
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return await self._make_request('GET', f'/price/{token_address}/history', params=params)
    
    async def get_multi_prices(self, tokens: List[str]) -> Dict[str, Any]:
        """Get prices for multiple tokens in single request"""
        data = {'tokens': tokens}
        return await self._make_request('POST', '/price/multi', data=data)
    
    async def get_price_at_timestamp(self, token_address: str, timestamp: int) -> Dict[str, Any]:
        """Get exact price at specific Unix timestamp"""
        return await self._make_request('GET', f'/price/{token_address}/timestamp/{timestamp}')
    
    async def get_price_ath(self, token_address: str) -> Dict[str, Any]:
        """Get all-time high price and timestamp data"""
        return await self._make_request('GET', f'/price/{token_address}/ath')
    
    # Wallet Analytics
    async def get_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Get wallet token holdings with USD values and portfolio breakdown"""
        return await self._make_request('GET', f'/wallet/{wallet_address}')
    
    async def get_wallet_basic(self, wallet_address: str) -> Dict[str, Any]:
        """Get basic wallet information and summary statistics"""
        return await self._make_request('GET', f'/wallet/{wallet_address}/basic')
    
    async def get_wallet_trades(
        self, 
        wallet_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        parse_jupiter: Optional[bool] = None,
        hide_arb: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Paginated wallet trading history with P&L data"""
        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = limit
        if parse_jupiter is not None:
            params['parseJupiter'] = parse_jupiter
        if hide_arb is not None:
            params['hideArb'] = hide_arb
        return await self._make_request('GET', f'/wallet/{wallet_address}/trades', params=params)
    
    async def get_pnl(self, wallet_address: str, show_historic_pnl: Optional[bool] = None) -> Dict[str, Any]:
        """Detailed profit/loss analysis with 24h and 30d performance"""
        params = {}
        if show_historic_pnl is not None:
            params['showHistoricPnL'] = show_historic_pnl
        return await self._make_request('GET', f'/pnl/{wallet_address}', params=params)
    
    async def get_wallet_chart(self, wallet_address: str) -> Dict[str, Any]:
        """Portfolio value chart data over time with performance metrics"""
        return await self._make_request('GET', f'/wallet/{wallet_address}/chart')
    
    # Trading & Market Activity
    async def get_trades(
        self, 
        token_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Real-time trades across all pools with volume and price data"""
        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', f'/trades/{token_address}', params=params)
    
    async def get_pool_trades(
        self, 
        token_address: str,
        pool_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Pool-specific trades with detailed transaction information"""
        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', f'/trades/{token_address}/{pool_address}', params=params)
    
    async def get_user_pool_trades(
        self, 
        token_address: str,
        pool_address: str,
        wallet_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """User-specific trades in a particular pool"""
        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', f'/trades/{token_address}/{pool_address}/user/{wallet_address}', params=params)
    
    async def get_top_traders_all(self) -> Dict[str, Any]:
        """Get top traders for all tokens"""
        return await self._make_request('GET', '/top-traders/all')
    
    async def get_top_traders(self, token_address: str) -> List[Dict[str, Any]]:
        """Top performing traders ranked by P&L for specific token"""
        return await self._make_request('GET', f'/top-traders/{token_address}')
    
    async def get_first_buyers(self, token_address: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """First buyers with current P&L since purchase"""
        params = {}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', f'/buyers/{token_address}/first', params=params)
    
    # Charts & Technical Analysis
    async def get_chart(
        self, 
        token_address: str,
        interval: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """OHLCV candlestick data with multiple timeframes (1s-1M)"""
        params = {}
        if interval:
            params['interval'] = interval
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return await self._make_request('GET', f'/chart/{token_address}', params=params)
    
    async def get_holders_chart(self, token_address: str) -> List[Dict[str, Any]]:
        """Token holder count progression over time"""
        return await self._make_request('GET', f'/chart/{token_address}/holders')
    
    async def get_stats(self, token_address: str, timeframe: Optional[str] = None) -> Dict[str, Any]:
        """Token statistics by timeframe: volume, transactions, unique traders"""
        params = {}
        if timeframe:
            params['timeframe'] = timeframe
        return await self._make_request('GET', f'/stats/{token_address}', params=params)
    
    async def get_events(self, token_address: str) -> List[Dict[str, Any]]:
        """Raw blockchain events and activities for token analysis"""
        return await self._make_request('GET', f'/events/{token_address}')
    
    # DEX Trading (Swap API)
    async def swap(
        self,
        from_token: str,
        to_token: str,
        amount: float,
        slippage: float,
        payer: str,
        priority_fee: Optional[float] = None,
        tx_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute swaps on Pump.fun, Raydium, Meteora with custom parameters"""
        data = {
            'from': from_token,
            'to': to_token,
            'amount': amount,
            'slippage': slippage,
            'payer': payer
        }
        if priority_fee is not None:
            data['priorityFee'] = priority_fee
        if tx_version:
            data['txVersion'] = tx_version
        return await self._make_request('POST', '/swap', data=data)
    
    async def get_priority_fee(self) -> Dict[str, Any]:
        """Get current priority fee estimates for faster transaction processing"""
        return await self._make_request('GET', '/priority-fee')
    
    # Account & Utilities
    async def get_account_credits(self) -> Dict[str, Any]:
        """Check remaining API credits and subscription status"""
        return await self._make_request('GET', '/account/credits')
    
    async def get_account_subscription(self) -> Dict[str, Any]:
        """Get detailed subscription plan information and billing"""
        return await self._make_request('GET', '/account/subscription')
    
    # Search endpoint
    async def search(self, q: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search tokens by symbol/name/mint"""
        params = {'q': q}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', '/search', params=params)
    
    # Utility methods
    async def close(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()


# Synchronous wrapper for easier usage
class SyncAugmentryClient:
    """
    Synchronous wrapper for AugmentryClient
    """
    
    def __init__(self, api_key: str, **kwargs):
        self._client = AugmentryClient(api_key, **kwargs)
        
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.close()
    
    def _run_async(self, coro):
        """Run an async coroutine in a sync context"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new loop if the current one is running
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(coro)
        finally:
            # Clean up any pending tasks
            pending = asyncio.all_tasks(loop) if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks(loop)
            for task in pending:
                task.cancel()
    
    # Token Endpoints
    def get_token(self, token_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_token(token_address))
    
    def get_token_holders(self, token_address: str, cursor: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_token_holders(token_address, cursor, limit))
    
    def search_tokens(
        self, 
        q: Optional[str] = None,
        min_liquidity: Optional[float] = None,
        max_liquidity: Optional[float] = None,
        min_market_cap: Optional[float] = None,
        max_market_cap: Optional[float] = None,
        min_volume24h: Optional[float] = None,
        max_volume24h: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        return self._run_async(self._client.search_tokens(
            q, min_liquidity, max_liquidity, min_market_cap, max_market_cap,
            min_volume24h, max_volume24h, sort_by, sort_order, limit
        ))
    
    def get_latest_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_latest_tokens(limit))
    
    def get_multi_tokens(self, tokens: List[str]) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_multi_tokens(tokens))
    
    def get_token_by_pool(self, pool_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_token_by_pool(pool_address))
    
    def get_tokens_by_deployer(self, wallet_address: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_tokens_by_deployer(wallet_address))
    
    # Price & Market Data
    def get_price(self, token_address: str, include_price_changes: Optional[bool] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_price(token_address, include_price_changes))
    
    def get_price_history(
        self, 
        token_address: str,
        interval: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_price_history(token_address, interval, start_time, end_time))
    
    def get_multi_prices(self, tokens: List[str]) -> Dict[str, Any]:
        return self._run_async(self._client.get_multi_prices(tokens))
    
    def get_price_at_timestamp(self, token_address: str, timestamp: int) -> Dict[str, Any]:
        return self._run_async(self._client.get_price_at_timestamp(token_address, timestamp))
    
    def get_price_ath(self, token_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_price_ath(token_address))
    
    # Wallet Analytics
    def get_wallet(self, wallet_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet(wallet_address))
    
    def get_wallet_basic(self, wallet_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_basic(wallet_address))
    
    def get_wallet_trades(
        self, 
        wallet_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        parse_jupiter: Optional[bool] = None,
        hide_arb: Optional[bool] = None
    ) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_trades(wallet_address, cursor, limit, parse_jupiter, hide_arb))
    
    def get_pnl(self, wallet_address: str, show_historic_pnl: Optional[bool] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_pnl(wallet_address, show_historic_pnl))
    
    def get_wallet_chart(self, wallet_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_chart(wallet_address))
    
    # Trading & Market Activity
    def get_trades(
        self, 
        token_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        return self._run_async(self._client.get_trades(token_address, cursor, limit))
    
    def get_pool_trades(
        self, 
        token_address: str,
        pool_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        return self._run_async(self._client.get_pool_trades(token_address, pool_address, cursor, limit))
    
    def get_user_pool_trades(
        self, 
        token_address: str,
        pool_address: str,
        wallet_address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        return self._run_async(self._client.get_user_pool_trades(token_address, pool_address, wallet_address, cursor, limit))
    
    def get_top_traders_all(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_top_traders_all())
    
    def get_top_traders(self, token_address: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_top_traders(token_address))
    
    def get_first_buyers(self, token_address: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_first_buyers(token_address, limit))
    
    # Charts & Technical Analysis
    def get_chart(
        self, 
        token_address: str,
        interval: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_chart(token_address, interval, start_time, end_time))
    
    def get_holders_chart(self, token_address: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_holders_chart(token_address))
    
    def get_stats(self, token_address: str, timeframe: Optional[str] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_stats(token_address, timeframe))
    
    def get_events(self, token_address: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_events(token_address))
    
    # DEX Trading (Swap API)
    def swap(
        self,
        from_token: str,
        to_token: str,
        amount: float,
        slippage: float,
        payer: str,
        priority_fee: Optional[float] = None,
        tx_version: Optional[str] = None
    ) -> Dict[str, Any]:
        return self._run_async(self._client.swap(from_token, to_token, amount, slippage, payer, priority_fee, tx_version))
    
    def get_priority_fee(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_priority_fee())
    
    # Account & Utilities
    def get_account_credits(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_account_credits())
    
    def get_account_subscription(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_account_subscription())
    
    # Search endpoint
    def search(self, q: str, limit: Optional[int] = None) -> Dict[str, Any]:
        return self._run_async(self._client.search(q, limit))
    
    def close(self):
        self._run_async(self._client.close())