"""
Wallet analysis examples using the Augmentry Python SDK
"""

import asyncio
from augmentry import AugmentryClient


async def analyze_single_wallet(client: AugmentryClient, wallet_address: str):
    """Analyze a single wallet comprehensively"""
    print(f"\n=== Analyzing Wallet: {wallet_address[:8]}...{wallet_address[-8:]} ===")
    
    try:
        # Get basic wallet info
        basic_info = await client.get_wallet_basic(wallet_address)
        print(f"Basic Info: {basic_info}")
        
        # Get PnL data for different timeframes
        pnl_7d = await client.get_wallet_pnl(wallet_address, days=7)
        pnl_30d = await client.get_wallet_pnl(wallet_address, days=30)
        
        print(f"7-day PnL: ${pnl_7d.get('total_pnl', 0):.2f}")
        print(f"30-day PnL: ${pnl_30d.get('total_pnl', 0):.2f}")
        
        # Get recent trades
        trades = await client.get_wallet_trades(wallet_address, limit=10)
        print(f"Recent trades count: {len(trades)}")
        
        # Get performance chart
        chart_data = await client.get_wallet_chart(wallet_address, days=7)
        print(f"Chart data points: {len(chart_data.get('data', []))}")
        
        return {
            'address': wallet_address,
            'pnl_7d': pnl_7d.get('total_pnl', 0),
            'pnl_30d': pnl_30d.get('total_pnl', 0),
            'recent_trades': len(trades)
        }
        
    except Exception as e:
        print(f"Error analyzing wallet {wallet_address}: {e}")
        return None


async def compare_multiple_wallets():
    """Compare performance of multiple wallets"""
    print("=== Multiple Wallet Comparison ===")
    
    # Replace with actual wallet addresses
    wallet_addresses = [
        "wallet_address_1_here",
        "wallet_address_2_here", 
        "wallet_address_3_here"
    ]
    
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Analyze each wallet individually
            wallet_results = []
            for address in wallet_addresses:
                result = await analyze_single_wallet(client, address)
                if result:
                    wallet_results.append(result)
            
            # Get batch PnL for comparison
            print("\n=== Batch PnL Comparison ===")
            try:
                batch_pnl = await client.get_wallets_batch_pnl(wallet_addresses)
                
                total_portfolio_pnl = 0
                for wallet_data in batch_pnl.get('data', []):
                    wallet_pnl = wallet_data.get('total_pnl', 0)
                    total_portfolio_pnl += wallet_pnl
                    print(f"Wallet {wallet_data['wallet_address'][:8]}...: ${wallet_pnl:.2f}")
                
                print(f"\nTotal Portfolio PnL: ${total_portfolio_pnl:.2f}")
                
            except Exception as e:
                print(f"Batch PnL error: {e}")
            
            # Sort wallets by performance
            if wallet_results:
                wallet_results.sort(key=lambda x: x['pnl_7d'], reverse=True)
                
                print("\n=== Top Performers (7-day PnL) ===")
                for i, wallet in enumerate(wallet_results, 1):
                    print(f"{i}. {wallet['address'][:8]}...: ${wallet['pnl_7d']:.2f}")
                    
        except Exception as e:
            print(f"Error in wallet comparison: {e}")


async def find_top_traders_and_analyze():
    """Find top traders and analyze their performance"""
    print("=== Top Traders Analysis ===")
    
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Get top traders
            top_traders = await client.get_top_traders_all()
            
            if 'data' in top_traders and top_traders['data']:
                print(f"Found {len(top_traders['data'])} top traders")
                
                # Analyze top 3 traders
                for i, trader in enumerate(top_traders['data'][:3], 1):
                    wallet_address = trader.get('wallet_address', '')
                    if wallet_address:
                        print(f"\n--- Top Trader #{i} ---")
                        await analyze_single_wallet(client, wallet_address)
            else:
                print("No top traders data available")
                
        except Exception as e:
            print(f"Error analyzing top traders: {e}")


async def track_token_specific_performance():
    """Track performance of wallets for specific tokens"""
    print("=== Token-Specific Performance ===")
    
    API_KEY = "your_api_key_here"
    wallet_address = "your_wallet_address_here"
    token_address = "your_token_address_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Get wallet PnL for specific token
            token_pnl = await client.get_wallet_token_pnl(wallet_address, token_address)
            print(f"Token-specific PnL: {token_pnl}")
            
            # Get first buyers for the token
            first_buyers = await client.get_first_buyers(token_address)
            print(f"First buyers count: {len(first_buyers)}")
            
            # Check if our wallet was among first buyers
            wallet_in_first_buyers = any(
                buyer.get('wallet_address') == wallet_address 
                for buyer in first_buyers
            )
            print(f"Wallet was first buyer: {wallet_in_first_buyers}")
            
        except Exception as e:
            print(f"Error in token-specific analysis: {e}")


if __name__ == "__main__":
    print("Choose an analysis to run:")
    print("1. Compare multiple wallets")
    print("2. Find and analyze top traders")
    print("3. Track token-specific performance")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(compare_multiple_wallets())
    elif choice == "2":
        asyncio.run(find_top_traders_and_analyze())
    elif choice == "3":
        asyncio.run(track_token_specific_performance())
    else:
        print("Invalid choice. Running multiple wallet comparison...")
        asyncio.run(compare_multiple_wallets())