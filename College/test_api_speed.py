#!/usr/bin/env python3
"""
ESPN API Response Time Tester
Tests how fast ESPN API responds and if 5-second polling causes issues
"""

import requests
import time
import asyncio
from datetime import datetime

async def test_espn_api_speed():
    """Test ESPN API response times and rate limiting"""
    
    url = 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
    
    print("🧪 ESPN API Speed Test")
    print("=" * 50)
    print("Testing response times and rate limiting behavior...")
    print("Will test 20 requests at different intervals\n")
    
    # Test different intervals
    intervals = [5, 7, 10, 15]  # seconds
    
    for interval in intervals:
        print(f"🔬 Testing {interval}-second intervals:")
        
        response_times = []
        error_count = 0
        
        for i in range(5):  # 5 requests per interval test
            start_time = time.time()
            
            try:
                response = requests.get(url, timeout=8)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    data = response.json()
                    game_count = len(data.get('events', []))
                    print(f"  Request {i+1}: ✅ {response_time:.0f}ms ({game_count} games)")
                elif response.status_code == 429:
                    print(f"  Request {i+1}: 🚨 RATE LIMITED (429)")
                    error_count += 1
                else:
                    print(f"  Request {i+1}: ⚠️ HTTP {response.status_code}")
                    error_count += 1
                    
            except Exception as e:
                print(f"  Request {i+1}: ❌ Error: {str(e)[:50]}")
                error_count += 1
            
            # Wait for interval (except on last request)
            if i < 4:
                await asyncio.sleep(interval)
        
        # Calculate stats
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"  📊 Average response: {avg_time:.0f}ms")
        
        if error_count == 0:
            print(f"  ✅ {interval}s interval: NO ERRORS - Safe to use!")
        elif error_count <= 1:
            print(f"  ⚠️ {interval}s interval: {error_count} error - Mostly stable")
        else:
            print(f"  🚨 {interval}s interval: {error_count} errors - Too aggressive!")
        
        print()
        
        # Extra delay between interval tests
        if interval != intervals[-1]:
            print("  ⏳ Waiting 10s before next test...")
            await asyncio.sleep(10)
    
    print("🎯 RECOMMENDATIONS:")
    print("✅ 15s+ intervals: Always safe")
    print("⚡ 10s intervals: Recommended balance") 
    print("🧪 7s intervals: Experimental, monitor for errors")
    print("🚨 5s intervals: High risk, use adaptive backing-off")
    
if __name__ == "__main__":
    asyncio.run(test_espn_api_speed())