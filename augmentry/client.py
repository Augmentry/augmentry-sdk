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
        base_url: Base URL for the API (default: https://data.augmentry.io)
        timeout: Request timeout in seconds (default: 10)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://data.augmentry.io",
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
                'User-Agent': 'Augmentry-Python-SDK/1.0.0'
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
    
    # Health and Status
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return await self._make_request('GET', '/health')
    
    # Token Endpoints
    async def get_all_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all tokens"""
        params = {}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', '/api/tokens/all', params=params)
    
    async def get_new_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get newly created tokens"""
        params = {}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', '/api/tokens/new', params=params)
    
    async def get_migrated_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get migrated tokens"""
        params = {}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', '/api/tokens/migrated', params=params)
    
    # Market Data
    async def get_market_stats(self) -> Dict[str, Any]:
        """Get market statistics"""
        return await self._make_request('GET', '/api/v1/market/stats')
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        return await self._make_request('GET', '/api/dashboard/stats')
    
    async def get_launchpad_stats(self) -> Dict[str, Any]:
        """Get launchpad statistics"""
        return await self._make_request('GET', '/api/launchpad/stats')
    
    # AI Analysis
    async def get_ai_analysis(self, token_address: str) -> Dict[str, Any]:
        """Get AI analysis for a token"""
        params = {'token': token_address}
        return await self._make_request('GET', '/api/ai-analysis', params=params)
    
    # Wallet Endpoints
    async def get_wallet_basic(self, address: str) -> Dict[str, Any]:
        """Get basic wallet information"""
        return await self._make_request('GET', f'/api/wallet/{address}/basic')
    
    async def get_wallet_pnl(self, address: str, days: Optional[int] = None) -> Dict[str, Any]:
        """Get wallet PnL data"""
        params = {}
        if days:
            params['days'] = days
        return await self._make_request('GET', f'/api/wallet/{address}/pnl', params=params)
    
    async def get_wallet_token_pnl(self, address: str, token: str) -> Dict[str, Any]:
        """Get wallet PnL for specific token"""
        return await self._make_request('GET', f'/api/wallet/{address}/token/{token}/pnl')
    
    async def get_wallet_trades(self, address: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get wallet trade history"""
        params = {}
        if limit:
            params['limit'] = limit
        return await self._make_request('GET', f'/api/wallet/{address}/trades', params=params)
    
    async def get_wallet_chart(self, address: str, days: Optional[int] = None) -> Dict[str, Any]:
        """Get wallet performance chart data"""
        params = {}
        if days:
            params['days'] = days
        return await self._make_request('GET', f'/api/wallet/{address}/chart', params=params)
    
    async def get_wallets_batch_pnl(self, addresses: List[str]) -> Dict[str, Any]:
        """Get PnL data for multiple wallets"""
        data = {'addresses': addresses}
        return await self._make_request('POST', '/api/wallets/batch-pnl', data=data)
    
    # Top Traders
    async def get_top_traders_all(self, page: Optional[int] = None) -> Dict[str, Any]:
        """Get all top traders"""
        if page:
            return await self._make_request('GET', f'/api/top-traders/all/{page}')
        return await self._make_request('GET', '/api/top-traders/all')
    
    async def get_top_traders_for_token(self, token: str) -> List[Dict[str, Any]]:
        """Get top traders for specific token"""
        return await self._make_request('GET', f'/api/top-traders/{token}')
    
    async def get_top_traders_by_timeframe(self, timeframe: str) -> List[Dict[str, Any]]:
        """Get top traders by timeframe (e.g., '24h', '7d', '30d')"""
        return await self._make_request('GET', f'/api/top-traders/{timeframe}')
    
    # First Buyers
    async def get_first_buyers(self, token: str) -> List[Dict[str, Any]]:
        """Get first buyers for a token"""
        return await self._make_request('GET', f'/api/first-buyers/{token}')
    
    async def get_tokens_batch_first_buyers(self, tokens: List[str]) -> Dict[str, Any]:
        """Get first buyers for multiple tokens"""
        data = {'tokens': tokens}
        return await self._make_request('POST', '/api/tokens/batch-first-buyers', data=data)
    
    # API Usage
    async def get_usage_stats(self, days: Optional[int] = 30) -> Dict[str, Any]:
        """Get API usage statistics"""
        params = {'days': days} if days else {}
        return await self._make_request('GET', '/api/usages', params=params)
    
    async def get_recent_usage(self, limit: Optional[int] = 50) -> List[Dict[str, Any]]:
        """Get recent API usage"""
        params = {'limit': limit} if limit else {}
        return await self._make_request('GET', '/api/usages/recent', params=params)
    
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
    
    def _run_async(self, coro):
        """Run an async coroutine in a sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def health_check(self) -> Dict[str, Any]:
        return self._run_async(self._client.health_check())
    
    def get_all_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_all_tokens(limit))
    
    def get_new_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_new_tokens(limit))
    
    def get_migrated_tokens(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_migrated_tokens(limit))
    
    def get_market_stats(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_market_stats())
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_dashboard_stats())
    
    def get_launchpad_stats(self) -> Dict[str, Any]:
        return self._run_async(self._client.get_launchpad_stats())
    
    def get_ai_analysis(self, token_address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_ai_analysis(token_address))
    
    def get_wallet_basic(self, address: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_basic(address))
    
    def get_wallet_pnl(self, address: str, days: Optional[int] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_pnl(address, days))
    
    def get_wallet_token_pnl(self, address: str, token: str) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_token_pnl(address, token))
    
    def get_wallet_trades(self, address: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_wallet_trades(address, limit))
    
    def get_wallet_chart(self, address: str, days: Optional[int] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallet_chart(address, days))
    
    def get_wallets_batch_pnl(self, addresses: List[str]) -> Dict[str, Any]:
        return self._run_async(self._client.get_wallets_batch_pnl(addresses))
    
    def get_top_traders_all(self, page: Optional[int] = None) -> Dict[str, Any]:
        return self._run_async(self._client.get_top_traders_all(page))
    
    def get_top_traders_for_token(self, token: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_top_traders_for_token(token))
    
    def get_top_traders_by_timeframe(self, timeframe: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_top_traders_by_timeframe(timeframe))
    
    def get_first_buyers(self, token: str) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_first_buyers(token))
    
    def get_tokens_batch_first_buyers(self, tokens: List[str]) -> Dict[str, Any]:
        return self._run_async(self._client.get_tokens_batch_first_buyers(tokens))
    
    def get_usage_stats(self, days: Optional[int] = 30) -> Dict[str, Any]:
        return self._run_async(self._client.get_usage_stats(days))
    
    def get_recent_usage(self, limit: Optional[int] = 50) -> List[Dict[str, Any]]:
        return self._run_async(self._client.get_recent_usage(limit))
    
    def close(self):
        self._run_async(self._client.close())