"""
Tests for the Augmentry SDK client
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from augmentry import AugmentryClient, SyncAugmentryClient
from augmentry.exceptions import AuthenticationError, ValidationError, APIError


class TestAugmentryClient:
    """Test cases for the async AugmentryClient"""
    
    def test_client_initialization(self):
        """Test client initialization with valid parameters"""
        client = AugmentryClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://data.augmentry.io"
        assert client.timeout == 10
    
    def test_client_initialization_custom_params(self):
        """Test client initialization with custom parameters"""
        client = AugmentryClient(
            api_key="test_key",
            base_url="https://custom.url",
            timeout=30
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.url"
        assert client.timeout == 30
    
    def test_client_initialization_no_api_key(self):
        """Test that client raises error when no API key provided"""
        with pytest.raises(ValidationError, match="API key is required"):
            AugmentryClient(api_key="")
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client as async context manager"""
        async with AugmentryClient(api_key="test_key") as client:
            assert client._session is not None
            assert not client._session.closed
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{"status": "healthy"}')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with AugmentryClient(api_key="test_key") as client:
                result = await client.health_check()
                assert result == {"status": "healthy"}
    
    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test authentication error handling"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_response.text = AsyncMock(return_value='{"detail": "Unauthorized"}')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with AugmentryClient(api_key="invalid_key") as client:
                with pytest.raises(AuthenticationError):
                    await client.health_check()
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test general API error handling"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.reason = "Internal Server Error"
            mock_response.text = AsyncMock(return_value='{"detail": "Server error"}')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with AugmentryClient(api_key="test_key") as client:
                with pytest.raises(APIError) as exc_info:
                    await client.health_check()
                assert exc_info.value.status_code == 500


class TestSyncAugmentryClient:
    """Test cases for the sync wrapper client"""
    
    def test_sync_client_initialization(self):
        """Test sync client initialization"""
        client = SyncAugmentryClient(api_key="test_key")
        assert client._client.api_key == "test_key"
    
    @patch('augmentry.client.asyncio.get_event_loop')
    def test_sync_health_check(self, mock_get_loop):
        """Test sync health check"""
        mock_loop = Mock()
        mock_loop.run_until_complete.return_value = {"status": "healthy"}
        mock_get_loop.return_value = mock_loop
        
        client = SyncAugmentryClient(api_key="test_key")
        result = client.health_check()
        assert result == {"status": "healthy"}
    
    @patch('augmentry.client.asyncio.get_event_loop')  
    def test_sync_get_all_tokens(self, mock_get_loop):
        """Test sync get all tokens"""
        mock_tokens = [{"name": "Token1", "symbol": "TK1"}]
        mock_loop = Mock()
        mock_loop.run_until_complete.return_value = mock_tokens
        mock_get_loop.return_value = mock_loop
        
        client = SyncAugmentryClient(api_key="test_key")
        result = client.get_all_tokens(limit=10)
        assert result == mock_tokens


class TestClientMethods:
    """Test specific client methods"""
    
    @pytest.mark.asyncio
    async def test_get_all_tokens_with_limit(self):
        """Test get_all_tokens with limit parameter"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='[{"name": "Token1"}]')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with AugmentryClient(api_key="test_key") as client:
                result = await client.get_all_tokens(limit=5)
                
                # Verify the request was made with correct parameters
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                assert call_args[1]['params'] == {'limit': 5}
    
    @pytest.mark.asyncio
    async def test_get_wallet_pnl(self):
        """Test get_wallet_pnl method"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{"total_pnl": 1000.0}')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with AugmentryClient(api_key="test_key") as client:
                result = await client.get_wallet_pnl("test_address", days=7)
                
                assert result == {"total_pnl": 1000.0}
                
                # Verify the correct URL was called
                call_args = mock_request.call_args
                assert "/api/wallet/test_address/pnl" in str(call_args)
                assert call_args[1]['params'] == {'days': 7}
    
    @pytest.mark.asyncio
    async def test_get_wallets_batch_pnl(self):
        """Test batch wallet PnL method"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{"data": []}')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with AugmentryClient(api_key="test_key") as client:
                addresses = ["addr1", "addr2", "addr3"]
                result = await client.get_wallets_batch_pnl(addresses)
                
                assert result == {"data": []}
                
                # Verify POST request with correct data
                call_args = mock_request.call_args
                assert call_args[0] == ('POST',)  # First positional arg is method
                assert call_args[1]['json'] == {'addresses': addresses}


if __name__ == "__main__":
    pytest.main([__file__])