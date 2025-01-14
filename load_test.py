import aiohttp
import asyncio
import time
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv('API_URL', 'http://localhost:8080')

async def check_server():
    """Check if server is running"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{BASE_URL}/api/health') as response:
                if response.status == 200:
                    return True
                print(f"Server health check failed with status: {response.status}")
                return False
        except Exception as e:
            print(f"Server connection error: {str(e)}")
            return False

async def make_click():
    """Make a single click request"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f'{BASE_URL}/api/log-click') as response:
                if response.status != 200:
                    print(f"Click failed with status: {response.status}")
                    return False
                return True
        except Exception as e:
            print(f"Click error: {str(e)}")
            return False

async def get_stats():
    """Get current statistics"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{BASE_URL}/api/stats') as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Stats error: {str(e)}")
    return None

async def perform_load_test(clicks_per_second, duration=5):
    print(f"\nTesting {clicks_per_second:,} clicks per second...")
    
    total_clicks = int(clicks_per_second * duration)
    print(f"Sending {total_clicks:,} clicks over {duration} seconds...")
    
    tasks = [make_click() for _ in range(total_clicks)]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    actual_duration = time.time() - start_time
    
    successful_clicks = sum(1 for r in results if r)
    success_rate = (successful_clicks / total_clicks) * 100
    
    # Get final stats
    stats = await get_stats()
    
    return {
        'clicks_per_second': clicks_per_second,
        'success_rate': success_rate,
        'actual_duration': actual_duration,
        'successful_clicks': successful_clicks,
        'total_clicks': total_clicks,
        'server_stats': stats
    }

async def main():
    # Test server connection first
    print("Testing server connection...")
    if not await check_server():
        print(f"❌ Could not connect to server. Please ensure the server is running on {BASE_URL}")
        return
    print("✅ Server connection successful")
    
    # Create 25 logarithmically spaced points between 1 and 1,000,000
    click_rates = np.logspace(0, 6, num=25).astype(int)
    
    print("\nStarting load test...")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    last_success = None
    
    for rate in click_rates:
        result = await perform_load_test(rate)
        
        print(f"\nResults for {rate:,} clicks/second:")
        print(f"Success Rate: {result['success_rate']:.2f}%")
        print(f"Actual Duration: {result['actual_duration']:.2f} seconds")
        print(f"Successful Clicks: {result['successful_clicks']:,} / {result['total_clicks']:,}")
        
        if result['server_stats']:
            print(f"Server Stats - Total Clicks: {result['server_stats']['total_clicks']:,}")
            print(f"Server Stats - Current Rate: {result['server_stats']['clicks_per_second']:,}/s")
        
        if result['success_rate'] < 90:
            if last_success:
                print(f"\n🚨 System started failing at {rate:,} clicks/second")
                print(f"Last successful rate: {last_success:,} clicks/second")
            break
        
        last_success = rate
        await asyncio.sleep(2)  # Let the system stabilize between tests
    
    print("\n" + "=" * 80)
    print("Load Test Complete!")
    if last_success:
        print(f"Maximum successful load: {last_success:,} clicks/second")
    else:
        print("System failed at minimum load")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 