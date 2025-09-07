"""
Basic usage examples for the Augmentry Python SDK
"""

import asyncio
from augmentry import AugmentryClient, SyncAugmentryClient


async def async_example():
    """Async usage example"""
    print("=== Async Usage Example ===")
    
    # Replace with your actual API key
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Health check
            health = await client.health_check()
            print(f"API Status: {health}")
            
            # Get market stats
            market_stats = await client.get_market_stats()
            print(f"Market Stats: {market_stats}")
            
            # Get new tokens (limited to 5)
            new_tokens = await client.get_new_tokens(limit=5)
            print(f"New Tokens Count: {len(new_tokens)}")
            for token in new_tokens[:3]:  # Show first 3
                print(f"  - {token.get('name', 'Unknown')} ({token.get('symbol', 'N/A')})")
            
            # Example wallet analysis (replace with actual wallet address)
            wallet_address = "your_wallet_address_here"
            try:
                wallet_pnl = await client.get_wallet_pnl(wallet_address, days=7)
                print(f"Wallet PnL (7 days): {wallet_pnl}")
            except Exception as e:
                print(f"Wallet analysis error: {e}")
                
        except Exception as e:
            print(f"Error: {e}")


def sync_example():
    """Synchronous usage example"""
    print("\n=== Sync Usage Example ===")
    
    # Replace with your actual API key
    API_KEY = "your_api_key_here"
    
    client = SyncAugmentryClient(api_key=API_KEY)
    
    try:
        # Health check
        health = client.health_check()
        print(f"API Status: {health}")
        
        # Get dashboard stats
        dashboard_stats = client.get_dashboard_stats()
        print(f"Dashboard Stats: {dashboard_stats}")
        
        # Get launchpad stats
        launchpad_stats = client.get_launchpad_stats()
        print(f"Launchpad Stats: {launchpad_stats}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    # Run async example
    asyncio.run(async_example())
    
    # Run sync example
    sync_example()