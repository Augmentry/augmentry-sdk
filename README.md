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
        # Get market stats
        market_stats = await client.get_market_stats()
        print(f"Total Volume: {market_stats['total_volume']}")
        
        # Get new tokens
        new_tokens = await client.get_new_tokens(limit=10)
        for token in new_tokens:
            print(f"Token: {token['name']} - {token['symbol']}")
        
        # Get wallet PnL
        wallet_pnl = await client.get_wallet_pnl("wallet_address_here")
        print(f"Total PnL: {wallet_pnl['total_pnl']}")

# Run async function
asyncio.run(main())
```

### Synchronous Usage

```python
from augmentry import SyncAugmentryClient

# Create client
client = SyncAugmentryClient(api_key="your_api_key")

# Get market stats
market_stats = client.get_market_stats()
print(f"Total Volume: {market_stats['total_volume']}")

# Get new tokens
new_tokens = client.get_new_tokens(limit=10)
for token in new_tokens:
    print(f"Token: {token['name']} - {token['symbol']}")

# Get wallet PnL
wallet_pnl = client.get_wallet_pnl("wallet_address_here")
print(f"Total PnL: {wallet_pnl['total_pnl']}")
```

## Authentication

Get your API key from the [Augmentry Dashboard](https://augmentry.io/dashboard) and initialize the client:

```python
from augmentry import AugmentryClient

client = AugmentryClient(
    api_key="ak_your_api_key_here",
    base_url="https://data.augmentry.io",  # Optional, this is the default
    timeout=10  # Optional timeout in seconds
)
```

## Available Endpoints

### Market Data
- `get_market_stats()` - Get overall market statistics
- `get_dashboard_stats()` - Get dashboard metrics
- `get_launchpad_stats()` - Get launchpad statistics

### Token Information
- `get_all_tokens(limit=None)` - Get all tokens
- `get_new_tokens(limit=None)` - Get newly created tokens
- `get_migrated_tokens(limit=None)` - Get migrated tokens

### Wallet Analytics
- `get_wallet_basic(address)` - Get basic wallet information
- `get_wallet_pnl(address, days=None)` - Get wallet PnL data
- `get_wallet_token_pnl(address, token)` - Get PnL for specific token
- `get_wallet_trades(address, limit=None)` - Get wallet trade history
- `get_wallet_chart(address, days=None)` - Get wallet performance chart
- `get_wallets_batch_pnl(addresses)` - Get PnL for multiple wallets

### Top Traders
- `get_top_traders_all(page=None)` - Get all top traders
- `get_top_traders_for_token(token)` - Get top traders for specific token
- `get_top_traders_by_timeframe(timeframe)` - Get top traders by timeframe

### First Buyers
- `get_first_buyers(token)` - Get first buyers for a token
- `get_tokens_batch_first_buyers(tokens)` - Get first buyers for multiple tokens

### AI Analysis
- `get_ai_analysis(token_address)` - Get AI analysis for a token

### API Usage
- `get_usage_stats(days=30)` - Get your API usage statistics
- `get_recent_usage(limit=50)` - Get recent API usage

### Health Check
- `health_check()` - Check API health status

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from augmentry import AugmentryClient, AugmentryError, AuthenticationError, RateLimitError

try:
    async with AugmentryClient(api_key="invalid_key") as client:
        data = await client.get_market_stats()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except AugmentryError as e:
    print(f"API error: {e}")
```

## Examples

### Analyze Top Performing Wallets

```python
import asyncio
from augmentry import AugmentryClient

async def analyze_top_wallets():
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get top traders
        top_traders = await client.get_top_traders_all()
        
        # Analyze top 5 wallets
        for trader in top_traders['data'][:5]:
            wallet_address = trader['wallet_address']
            
            # Get detailed PnL
            pnl_data = await client.get_wallet_pnl(wallet_address, days=7)
            
            # Get recent trades
            trades = await client.get_wallet_trades(wallet_address, limit=10)
            
            print(f"Wallet: {wallet_address}")
            print(f"7-day PnL: ${pnl_data['total_pnl']:.2f}")
            print(f"Recent trades: {len(trades)}")
            print("---")

asyncio.run(analyze_top_wallets())
```

### Monitor New Token Launches

```python
import asyncio
from augmentry import AugmentryClient

async def monitor_new_tokens():
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get latest tokens
        new_tokens = await client.get_new_tokens(limit=20)
        
        for token in new_tokens:
            # Get first buyers for each token
            first_buyers = await client.get_first_buyers(token['mint'])
            
            # Get AI analysis
            try:
                analysis = await client.get_ai_analysis(token['mint'])
                sentiment = analysis.get('sentiment', 'Unknown')
            except:
                sentiment = 'N/A'
            
            print(f"Token: {token['name']} ({token['symbol']})")
            print(f"Market Cap: ${token.get('market_cap', 0):,.2f}")
            print(f"First Buyers: {len(first_buyers)}")
            print(f"AI Sentiment: {sentiment}")
            print("---")

asyncio.run(monitor_new_tokens())
```

### Track Portfolio Performance

```python
import asyncio
from augmentry import AugmentryClient

async def track_portfolio(wallet_addresses):
    async with AugmentryClient(api_key="your_api_key") as client:
        # Get batch PnL data
        batch_pnl = await client.get_wallets_batch_pnl(wallet_addresses)
        
        total_pnl = 0
        for wallet_data in batch_pnl['data']:
            wallet_pnl = wallet_data['total_pnl']
            total_pnl += wallet_pnl
            
            print(f"Wallet: {wallet_data['wallet_address']}")
            print(f"PnL: ${wallet_pnl:,.2f}")
            
        print(f"\nTotal Portfolio PnL: ${total_pnl:,.2f}")

# Example usage
wallets = ["wallet1", "wallet2", "wallet3"]
asyncio.run(track_portfolio(wallets))
```

## Rate Limits

The API has rate limits in place. The SDK will automatically handle rate limit errors by raising a `RateLimitError` exception. You should implement appropriate backoff strategies in your application.

## Support

- **Documentation**: [https://docs.augmentry.io](https://docs.augmentry.io)
- **API Dashboard**: [https://augmentry.io/dashboard](https://augmentry.io/dashboard)
- **Issues**: [GitHub Issues](https://github.com/your-username/augmentry-python-sdk/issues)
- **Email**: support@augmentry.io

## License

This project is licensed under the MIT License - see the LICENSE file for details.