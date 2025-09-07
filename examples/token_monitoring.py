"""
Token monitoring and analysis examples using the Augmentry Python SDK
"""

import asyncio
from datetime import datetime
from augmentry import AugmentryClient


async def monitor_new_tokens():
    """Monitor and analyze newly launched tokens"""
    print("=== New Token Monitoring ===")
    
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Get new tokens
            new_tokens = await client.get_new_tokens(limit=10)
            print(f"Found {len(new_tokens)} new tokens")
            
            for i, token in enumerate(new_tokens, 1):
                print(f"\n--- Token #{i} ---")
                print(f"Name: {token.get('name', 'Unknown')}")
                print(f"Symbol: {token.get('symbol', 'N/A')}")
                print(f"Mint: {token.get('mint', 'N/A')}")
                print(f"Market Cap: ${token.get('market_cap', 0):,.2f}")
                print(f"Created: {token.get('created_at', 'Unknown')}")
                
                # Get first buyers
                try:
                    first_buyers = await client.get_first_buyers(token['mint'])
                    print(f"First buyers: {len(first_buyers)}")
                    
                    # Show top first buyers
                    if first_buyers:
                        for j, buyer in enumerate(first_buyers[:3], 1):
                            print(f"  {j}. {buyer.get('wallet_address', '')[:8]}... - ${buyer.get('amount', 0):.2f}")
                            
                except Exception as e:
                    print(f"Error getting first buyers: {e}")
                
                # Get AI analysis if available
                try:
                    analysis = await client.get_ai_analysis(token['mint'])
                    sentiment = analysis.get('sentiment', 'Unknown')
                    confidence = analysis.get('confidence', 0)
                    print(f"AI Sentiment: {sentiment} (confidence: {confidence}%)")
                    
                except Exception as e:
                    print(f"AI analysis not available: {e}")
                    
        except Exception as e:
            print(f"Error monitoring new tokens: {e}")


async def analyze_migrated_tokens():
    """Analyze tokens that have migrated/graduated"""
    print("=== Migrated Token Analysis ===")
    
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Get migrated tokens
            migrated_tokens = await client.get_migrated_tokens(limit=5)
            print(f"Found {len(migrated_tokens)} migrated tokens")
            
            for token in migrated_tokens:
                print(f"\n--- {token.get('name', 'Unknown')} ({token.get('symbol', 'N/A')}) ---")
                
                # Get top traders for this token
                try:
                    top_traders = await client.get_top_traders_for_token(token['mint'])
                    print(f"Top traders: {len(top_traders)}")
                    
                    for i, trader in enumerate(top_traders[:3], 1):
                        print(f"  {i}. {trader.get('wallet_address', '')[:8]}... - PnL: ${trader.get('pnl', 0):.2f}")
                        
                except Exception as e:
                    print(f"Error getting top traders: {e}")
                    
        except Exception as e:
            print(f"Error analyzing migrated tokens: {e}")


async def batch_token_analysis():
    """Perform batch analysis on multiple tokens"""
    print("=== Batch Token Analysis ===")
    
    # Replace with actual token addresses you want to analyze
    token_addresses = [
        "token_mint_1_here",
        "token_mint_2_here",
        "token_mint_3_here"
    ]
    
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Get first buyers for multiple tokens at once
            batch_first_buyers = await client.get_tokens_batch_first_buyers(token_addresses)
            
            print(f"Batch analysis for {len(token_addresses)} tokens:")
            
            for token_address in token_addresses:
                token_data = batch_first_buyers.get('data', {}).get(token_address, {})
                first_buyers = token_data.get('first_buyers', [])
                
                print(f"\nToken: {token_address[:8]}...")
                print(f"First buyers: {len(first_buyers)}")
                
                if first_buyers:
                    total_early_investment = sum(buyer.get('amount', 0) for buyer in first_buyers)
                    print(f"Total early investment: ${total_early_investment:.2f}")
                    
                    # Show biggest early investor
                    biggest_buyer = max(first_buyers, key=lambda x: x.get('amount', 0), default={})
                    if biggest_buyer:
                        print(f"Biggest early buyer: {biggest_buyer.get('wallet_address', '')[:8]}... - ${biggest_buyer.get('amount', 0):.2f}")
                        
        except Exception as e:
            print(f"Error in batch analysis: {e}")


async def monitor_token_trends():
    """Monitor trending tokens and their performance"""
    print("=== Token Trend Monitoring ===")
    
    API_KEY = "your_api_key_here"
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            # Get all tokens and analyze trends
            all_tokens = await client.get_all_tokens(limit=20)
            print(f"Analyzing {len(all_tokens)} tokens for trends")
            
            trending_tokens = []
            
            for token in all_tokens:
                token_mint = token.get('mint', '')
                if not token_mint:
                    continue
                    
                # Get top traders to gauge activity
                try:
                    top_traders = await client.get_top_traders_for_token(token_mint)
                    trader_count = len(top_traders)
                    
                    # Calculate total trading activity
                    total_pnl = sum(trader.get('pnl', 0) for trader in top_traders)
                    
                    trending_tokens.append({
                        'token': token,
                        'trader_count': trader_count,
                        'total_pnl': total_pnl,
                        'avg_pnl': total_pnl / trader_count if trader_count > 0 else 0
                    })
                    
                except Exception as e:
                    print(f"Error analyzing token {token_mint[:8]}...: {e}")
                    continue
            
            # Sort by activity (trader count and total PnL)
            trending_tokens.sort(key=lambda x: (x['trader_count'], abs(x['total_pnl'])), reverse=True)
            
            print(f"\n=== Top Trending Tokens ===")
            for i, trend_data in enumerate(trending_tokens[:5], 1):
                token = trend_data['token']
                print(f"{i}. {token.get('name', 'Unknown')} ({token.get('symbol', 'N/A')})")
                print(f"   Traders: {trend_data['trader_count']}")
                print(f"   Total PnL: ${trend_data['total_pnl']:.2f}")
                print(f"   Avg PnL: ${trend_data['avg_pnl']:.2f}")
                print(f"   Market Cap: ${token.get('market_cap', 0):,.2f}")
                
        except Exception as e:
            print(f"Error monitoring trends: {e}")


async def real_time_token_alerts():
    """Set up alerts for token conditions (example structure)"""
    print("=== Token Alert System ===")
    
    API_KEY = "your_api_key_here"
    
    # Alert conditions
    HIGH_ACTIVITY_THRESHOLD = 10  # More than 10 top traders
    HIGH_MARKET_CAP_THRESHOLD = 1000000  # $1M market cap
    HIGH_PNL_THRESHOLD = 50000  # $50K total PnL
    
    async with AugmentryClient(api_key=API_KEY) as client:
        try:
            print("Scanning for alert conditions...")
            
            # Get new tokens to monitor
            new_tokens = await client.get_new_tokens(limit=15)
            
            alerts = []
            
            for token in new_tokens:
                token_mint = token.get('mint', '')
                token_name = token.get('name', 'Unknown')
                market_cap = token.get('market_cap', 0)
                
                # Market cap alert
                if market_cap > HIGH_MARKET_CAP_THRESHOLD:
                    alerts.append(f"🚨 HIGH MARKET CAP: {token_name} - ${market_cap:,.2f}")
                
                # Check trading activity
                try:
                    top_traders = await client.get_top_traders_for_token(token_mint)
                    trader_count = len(top_traders)
                    
                    if trader_count > HIGH_ACTIVITY_THRESHOLD:
                        alerts.append(f"📈 HIGH ACTIVITY: {token_name} - {trader_count} active traders")
                    
                    # Check total PnL
                    total_pnl = sum(abs(trader.get('pnl', 0)) for trader in top_traders)
                    if total_pnl > HIGH_PNL_THRESHOLD:
                        alerts.append(f"💰 HIGH PNL ACTIVITY: {token_name} - ${total_pnl:,.2f} total PnL")
                        
                except Exception:
                    continue
            
            # Display alerts
            if alerts:
                print(f"\n🔔 {len(alerts)} ALERTS TRIGGERED:")
                for alert in alerts:
                    print(f"  {alert}")
            else:
                print("No alerts triggered at this time.")
                
        except Exception as e:
            print(f"Error in alert system: {e}")


if __name__ == "__main__":
    print("Choose a token monitoring option:")
    print("1. Monitor new tokens")
    print("2. Analyze migrated tokens")
    print("3. Batch token analysis")
    print("4. Monitor token trends")
    print("5. Real-time token alerts")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        asyncio.run(monitor_new_tokens())
    elif choice == "2":
        asyncio.run(analyze_migrated_tokens())
    elif choice == "3":
        asyncio.run(batch_token_analysis())
    elif choice == "4":
        asyncio.run(monitor_token_trends())
    elif choice == "5":
        asyncio.run(real_time_token_alerts())
    else:
        print("Invalid choice. Running new token monitoring...")
        asyncio.run(monitor_new_tokens())