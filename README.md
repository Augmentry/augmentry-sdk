# Augmentry Python SDK

Official Python SDK for the Augmentry API - Access Solana market data, wallet analytics, and trading insights.

## Installation

```bash
pip install augmentry
```

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from augmentry import AugmentryClient

async def main():
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get account credits
        credits = await client.get_account_credits()
        print(credits)
        
        # Get token information
        token_info = await client.get_token("token_address")
        print(token_info)
        
        # Get recent trades
        trades = await client.get_trades("token_address", limit=5)
        print(trades)

# Run async function
asyncio.run(main())
```

### Synchronous Usage

```python
from augmentry import SyncAugmentryClient

# Using context manager (recommended)
with SyncAugmentryClient(api_key="your_api_key") as client:
    # Get account credits
    credits = client.get_account_credits()
    print(credits)
    
    # Get token information
    token_info = client.get_token("token_address")
    print(token_info)

# Or without context manager
client = SyncAugmentryClient(api_key="your_api_key")
credits = client.get_account_credits()
client.close()  # Remember to close when done
```

## Authentication

Get your API key from the [Augmentry Dashboard](https://augmentry.io/dashboard) and initialize the client:

```python
from augmentry import AugmentryClient

client = AugmentryClient(
    api_key="ak_your_api_key_here",
    base_url="https://data.augmentry.io/api",  # Optional, this is the default
    timeout=10  # Optional timeout in seconds
)
```

## Available Endpoints

### Token Information
- `get_token(token_address)` - Get comprehensive token information with risk analysis
- `get_token_holders(token_address, cursor=None, limit=None)` - Get paginated list of token holders
- `search_tokens(q=None, min_liquidity=None, max_liquidity=None, min_market_cap=None, max_market_cap=None, min_volume24h=None, max_volume24h=None, sort_by=None, sort_order=None, limit=None)` - Search tokens with filters
- `get_latest_tokens(limit=None)` - Get latest newly created tokens
- `get_multi_tokens(tokens)` - Batch request for multiple token details (up to 100 tokens)
- `get_token_by_pool(pool_address)` - Get token information by pool address
- `get_tokens_by_deployer(wallet_address)` - Get all tokens deployed by a specific wallet

### Price & Market Data
- `get_price(token_address, include_price_changes=None)` - Get real-time price with changes
- `get_price_history(token_address, interval=None, start_time=None, end_time=None)` - Historical price data (intervals: 1m-1d)
- `get_multi_prices(tokens)` - Get prices for multiple tokens in single request
- `get_price_at_timestamp(token_address, timestamp)` - Get exact price at specific Unix timestamp
- `get_price_ath(token_address)` - Get all-time high price data

### Wallet Analytics
- `get_wallet(wallet_address)` - Get wallet token holdings with USD values
- `get_wallet_basic(wallet_address)` - Get basic wallet information
- `get_wallet_trades(wallet_address, cursor=None, limit=None, parse_jupiter=None, hide_arb=None)` - Paginated trading history
- `get_pnl(wallet_address, show_historic_pnl=None)` - Detailed profit/loss analysis
- `get_wallet_chart(wallet_address)` - Portfolio value chart data over time

### Trading & Market Activity
- `get_trades(token_address, cursor=None, limit=None)` - Real-time trades across all pools
- `get_pool_trades(token_address, pool_address, cursor=None, limit=None)` - Pool-specific trades
- `get_user_pool_trades(token_address, pool_address, wallet_address, cursor=None, limit=None)` - User trades in pool
- `get_top_traders_all()` - Get top traders for all tokens
- `get_top_traders(token_address)` - Top performing traders for specific token
- `get_first_buyers(token_address, limit=None)` - First buyers with current P&L

### Charts & Technical Analysis
- `get_chart(token_address, interval=None, start_time=None, end_time=None)` - OHLCV candlestick data (intervals: 1s-1M)
- `get_holders_chart(token_address)` - Token holder count progression
- `get_stats(token_address, timeframe=None)` - Token statistics by timeframe
- `get_events(token_address)` - Raw blockchain events for token analysis

### DEX Trading (Swap API)
- `swap(from_token, to_token, amount, slippage, payer, priority_fee=None, tx_version=None)` - Execute swaps on Pump.fun, Raydium, Meteora
- `get_priority_fee()` - Get current priority fee estimates

### Account & Utilities
- `get_account_credits()` - Check remaining API credits
- `get_account_subscription()` - Get subscription plan information
- `search(q, limit=None)` - Search tokens by symbol/name/mint

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from augmentry import AugmentryClient, AugmentryError, AuthenticationError, RateLimitError

try:
    async with AugmentryClient(api_key="invalid_key") as client:
        data = await client.get_token("token_address")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except AugmentryError as e:
    print(f"API error: {e}")
```


## Rate Limits

The API has rate limits in place. The SDK will automatically handle rate limit errors by raising a `RateLimitError` exception. You should implement appropriate backoff strategies in your application.

## Support

- **Documentation**: [https://docs.augmentry.io](https://docs.augmentry.io)
- **API Dashboard**: [https://echelon.augmentry.io/](https://echelon.augmentry.io/)
- **Issues**: [GitHub Issues](https://github.com/augmentry/augmentry-python-sdk/issues)
- **Email**: support@augmentry.io

## License

This project is licensed under the MIT License - see the LICENSE file for details.