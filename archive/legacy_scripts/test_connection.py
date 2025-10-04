"""Quick test script to verify WebSocket and API functionality."""

import asyncio
import json
from datetime import datetime

import httpx
import websockets


async def test_api_status():
    """Test the /api/status endpoint."""
    print("\n🔍 Testing API Status Endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/status/")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status OK - Uptime: {data.get('uptime_seconds', 0):.0f}s")
                print(f"   📊 Devices: {data.get('online_devices', 0)}/{data.get('total_devices', 0)} online")
                return True
            else:
                print(f"   ❌ Status: {response.status_code}")
                return False
        except Exception as exc:
            print(f"   ❌ Error: {exc}")
            return False


async def test_api_games():
    """Test the /api/games/live endpoint."""
    print("\n🏈 Testing Games Endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/games/live?sport=nfl")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    games = data.get("data", {}).get("games", [])
                    print(f"   ✅ Games API OK - {len(games)} games found")
                    if games:
                        game = games[0]
                        # Check for proper serialization
                        if "id" in game and "home" in game and "away" in game:
                            print(f"   ✅ Serialization OK - Fields present")
                            print(f"   📋 Sample: {game.get('home', {}).get('abbreviation')} vs {game.get('away', {}).get('abbreviation')}")
                        else:
                            print(f"   ⚠️  Serialization issue - Missing fields")
                            print(f"   Fields: {list(game.keys())}")
                    return True
                else:
                    print(f"   ❌ API returned success=false")
                    return False
            else:
                print(f"   ❌ Status: {response.status_code}")
                return False
        except Exception as exc:
            print(f"   ❌ Error: {exc}")
            return False


async def test_websocket():
    """Test WebSocket connection and message receipt."""
    print("\n🔌 Testing WebSocket Connection...")
    try:
        async with websockets.connect("ws://localhost:8000/api/ws") as websocket:
            print("   ✅ WebSocket connected")
            
            # Wait for messages with timeout
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=35.0)
                data = json.loads(message)
                print(f"   ✅ Received message: {data.get('type', 'unknown')}")
                
                if data.get('type') == 'ping':
                    print("   ✅ Ping received - connection is alive!")
                    return True
                else:
                    print(f"   ℹ️  Event received: {data}")
                    return True
            except asyncio.TimeoutError:
                print("   ⚠️  No message received in 35s (expected ping within 30s)")
                return False
                
    except Exception as exc:
        print(f"   ❌ Error: {exc}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🏟️  Smart Stadium - Connection Tests")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API endpoints
    api_ok = await test_api_status()
    games_ok = await test_api_games()
    
    # Test WebSocket
    ws_ok = await test_websocket()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"   Status API:  {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"   Games API:   {'✅ PASS' if games_ok else '❌ FAIL'}")
    print(f"   WebSocket:   {'✅ PASS' if ws_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if api_ok and games_ok and ws_ok:
        print("\n✅ All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    print("\n💡 Next steps:")
    print("   1. Open browser to http://localhost:5173")
    print("   2. Open DevTools Console (F12)")
    print("   3. Look for [WebSocket] log messages")
    print("   4. Check Status Bar shows 'Live updates'")
    print("   5. Verify Live Feed panel is ready")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
