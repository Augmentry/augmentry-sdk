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
        # Get token information
        token_info = await client.get_token("token_address")
        print(f"Token: {token_info['name']} - Price: ${token_info['price']}")
        
        # Get real-time price
        price_data = await client.get_price("token_address")
        print(f"Current Price: ${price_data['price']}")
        
        # Get wallet PnL
        pnl = await client.get_pnl("wallet_address")
        print(f"Total PnL: ${pnl['totalPnL']}")

# Run async function
asyncio.run(main())
```

### Synchronous Usage

```python
from augmentry import SyncAugmentryClient

# Create client
client = SyncAugmentryClient(api_key="your_api_key")

# Get token information
token_info = client.get_token("token_address")
print(f"Token: {token_info['name']} - Price: ${token_info['price']}")

# Get wallet PnL
pnl = client.get_pnl("wallet_address")
print(f"Total PnL: ${pnl['totalPnL']}")
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

## Examples

### Analyze Token Performance

```python
import asyncio
from augmentry import AugmentryClient

async def analyze_token(token_address):
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get comprehensive token information
        token_info = await client.get_token(token_address)
        print(f"Token: {token_info['name']} ({token_info['symbol']})")
        print(f"Price: ${token_info['price']:,.6f}")
        print(f"Market Cap: ${token_info['marketCap']:,.2f}")
        
        # Get price history for last 24h
        price_history = await client.get_price_history(
            token_address,
            interval="1h",
            start_time=int(time.time() - 86400)
        )
        
        # Get top traders
        top_traders = await client.get_top_traders(token_address)
        print(f"\nTop Traders: {len(top_traders)}")
        
        # Get recent trades
        trades = await client.get_trades(token_address, limit=10)
        print(f"Recent Trades: {len(trades['data'])}")

asyncio.run(analyze_token("your_token_address"))
```

### Track Wallet Performance

```python
import asyncio
from augmentry import AugmentryClient

async def track_wallet(wallet_address):
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get wallet holdings
        wallet = await client.get_wallet(wallet_address)
        total_value = sum(token['usdValue'] for token in wallet['tokens'])
        print(f"Total Portfolio Value: ${total_value:,.2f}")
        
        # Get PnL data
        pnl = await client.get_pnl(wallet_address, show_historic_pnl=True)
        print(f"Total PnL: ${pnl['totalPnL']:,.2f}")
        print(f"24h PnL: ${pnl['pnl24h']:,.2f}")
        print(f"30d PnL: ${pnl['pnl30d']:,.2f}")
        
        # Get recent trades
        trades = await client.get_wallet_trades(
            wallet_address,
            limit=20,
            parse_jupiter=True,
            hide_arb=True
        )
        print(f"\nRecent Trades: {len(trades['data'])}")

asyncio.run(track_wallet("your_wallet_address"))
```

### Monitor New Token Launches

```python
import asyncio
from augmentry import AugmentryClient

async def monitor_new_tokens():
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get latest tokens
        new_tokens = await client.get_latest_tokens(limit=10)
        
        for token in new_tokens:
            # Get detailed token info
            token_info = await client.get_token(token['mint'])
            
            # Get first buyers
            first_buyers = await client.get_first_buyers(token['mint'], limit=5)
            
            # Check holder count
            holders = await client.get_token_holders(token['mint'], limit=1)
            
            print(f"\nToken: {token_info['name']} ({token_info['symbol']})")
            print(f"Mint: {token['mint']}")
            print(f"Liquidity: ${token_info.get('liquidity', 0):,.2f}")
            print(f"Holders: {holders.get('total', 0)}")
            print(f"First Buyers: {len(first_buyers)}")
            
            # Show first buyer profits
            for buyer in first_buyers[:3]:
                print(f"  - {buyer['wallet']}: ${buyer.get('pnl', 0):,.2f} PnL")

asyncio.run(monitor_new_tokens())
```

### Execute DEX Swap

```python
import asyncio
from augmentry import AugmentryClient

async def execute_swap():
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get current priority fee
        priority_fee = await client.get_priority_fee()
        
        # Execute swap
        swap_result = await client.swap(
            from_token="So11111111111111111111111111111111111111112",  # SOL
            to_token="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",   # USDC
            amount=1.0,  # 1 SOL
            slippage=0.5,  # 0.5%
            payer="your_wallet_address",
            priority_fee=priority_fee['medium']
        )
        
        print(f"Swap transaction: {swap_result['txid']}")

asyncio.run(execute_swap())
```

### Search and Filter Tokens

```python
import asyncio
from augmentry import AugmentryClient

async def search_tokens():
    async with AugmentryClient(api_key="your_api_key") as client:
        # Search tokens with filters
        results = await client.search_tokens(
            q="BONK",  # Search query
            min_liquidity=10000,  # Min $10k liquidity
            max_liquidity=1000000,  # Max $1M liquidity
            min_volume24h=5000,  # Min $5k daily volume
            sort_by="volume24h",
            sort_order="desc",
            limit=10
        )
        
        for token in results['data']:
            print(f"\nToken: {token['name']} ({token['symbol']})")
            print(f"Liquidity: ${token['liquidity']:,.2f}")
            print(f"24h Volume: ${token['volume24h']:,.2f}")
            print(f"Market Cap: ${token['marketCap']:,.2f}")

asyncio.run(search_tokens())
```

### Get Historical Price Data

```python
import asyncio
from augmentry import AugmentryClient
import time

async def get_price_analysis(token_address):
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get current price with changes
        current = await client.get_price(token_address, include_price_changes=True)
        print(f"Current Price: ${current['price']:,.6f}")
        print(f"24h Change: {current['change24h']:.2f}%")
        
        # Get ATH data
        ath = await client.get_price_ath(token_address)
        print(f"\nAll-Time High: ${ath['price']:,.6f}")
        print(f"ATH Date: {ath['timestamp']}")
        
        # Get price at specific time (1 week ago)
        week_ago = int(time.time()) - (7 * 24 * 3600)
        historical = await client.get_price_at_timestamp(token_address, week_ago)
        print(f"\nPrice 1 week ago: ${historical['price']:,.6f}")

asyncio.run(get_price_analysis("your_token_address"))
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