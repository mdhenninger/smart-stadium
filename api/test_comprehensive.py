"""
Comprehensive Smart Stadium API + WebSocket Test
Tests both REST API and real-time WebSocket features
"""

import asyncio
import requests
import json
import time
from datetime import datetime
import threading

# WebSocket test client
import websockets

class ComprehensiveApiTest:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.ws_uri = "ws://localhost:8000/api/ws"
        self.websocket = None
        self.ws_messages = []
        self.ws_connected = False
        
    def test_rest_api(self):
        """Test REST API endpoints"""
        print("🧪 TESTING REST API ENDPOINTS")
        print("=" * 40)
        
        tests = [
            ("Health Check", "GET", "/api/health"),
            ("System Status", "GET", "/api/status"),
            ("WebSocket Stats", "GET", "/api/websockets/stats"),
            ("Get Teams", "GET", "/api/teams/?limit=5"),
            ("Get Current Team", "GET", "/api/teams/current"),
            ("Get Devices", "GET", "/api/devices/"),
            ("Celebration Types", "GET", "/api/celebrations/types"),
        ]
        
        passed = 0
        for test_name, method, endpoint in tests:
            try:
                url = f"{self.api_base}{endpoint}"
                response = requests.request(method, url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {test_name}: {response.status_code}")
                    passed += 1
                else:
                    print(f"❌ {test_name}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {test_name}: {str(e)}")
        
        print(f"\n📊 REST API Results: {passed}/{len(tests)} passed")
        return passed == len(tests)
    
    async def test_websocket_connection(self):
        """Test WebSocket connection and basic features"""
        print("\n🔌 TESTING WEBSOCKET CONNECTION")
        print("=" * 40)
        
        try:
            # Connect with test parameters
            uri = f"{self.ws_uri}?client_id=test_client&subscriptions=all"
            self.websocket = await websockets.connect(uri)
            self.ws_connected = True
            print("✅ WebSocket connected successfully")
            
            # Test basic message exchange
            await self.test_websocket_messages()
            
            return True
            
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
        finally:
            if self.websocket:
                await self.websocket.close()
                self.ws_connected = False
    
    async def test_websocket_messages(self):
        """Test WebSocket message handling"""
        print("\n📡 Testing WebSocket messages...")
        
        # Listen for welcome message
        try:
            welcome_msg = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
            welcome_data = json.loads(welcome_msg)
            if welcome_data.get("type") == "connection_established":
                print("✅ Welcome message received")
            else:
                print(f"⚠️ Unexpected welcome message: {welcome_data.get('type')}")
        except asyncio.TimeoutError:
            print("❌ No welcome message received")
        
        # Test ping/pong
        ping_msg = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        await self.websocket.send(json.dumps(ping_msg))
        print("📤 Ping sent")
        
        try:
            pong_response = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
            pong_data = json.loads(pong_response)
            if pong_data.get("type") == "pong":
                print("✅ Pong received")
            else:
                print(f"⚠️ Unexpected response to ping: {pong_data.get('type')}")
        except asyncio.TimeoutError:
            print("❌ No pong response received")
        
        # Test status request
        status_msg = {
            "type": "get_status",
            "timestamp": datetime.now().isoformat()
        }
        await self.websocket.send(json.dumps(status_msg))
        print("📤 Status request sent")
        
        try:
            status_response = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
            status_data = json.loads(status_response)
            if status_data.get("type") == "system_status":
                print("✅ System status received")
            else:
                print(f"⚠️ Unexpected status response: {status_data.get('type')}")
        except asyncio.TimeoutError:
            print("❌ No status response received")
    
    def test_celebration_with_websocket(self):
        """Test celebration API with WebSocket monitoring"""
        print("\n🎉 TESTING CELEBRATION WITH REAL-TIME MONITORING")
        print("=" * 50)
        
        # This would require running WebSocket listener in parallel
        # For now, just test the API call
        try:
            response = requests.post(f"{self.api_base}/api/celebrations/sack")
            if response.status_code == 200:
                print("✅ Sack celebration triggered successfully")
                data = response.json()
                print(f"   Message: {data.get('message', 'No message')}")
                return True
            else:
                print(f"❌ Celebration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Celebration test failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run all tests"""
        print("🏈 COMPREHENSIVE SMART STADIUM API TEST")
        print("=" * 60)
        print(f"🎯 Testing API at: {self.api_base}")
        print(f"🔌 Testing WebSocket at: {self.ws_uri}")
        print()
        
        # Test REST API
        rest_success = self.test_rest_api()
        
        # Test WebSocket
        ws_success = await self.test_websocket_connection()
        
        # Test celebration
        celebration_success = self.test_celebration_with_websocket()
        
        # Final results
        print("\n📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 40)
        print(f"✅ REST API: {'PASS' if rest_success else 'FAIL'}")
        print(f"🔌 WebSocket: {'PASS' if ws_success else 'FAIL'}")
        print(f"🎉 Celebration: {'PASS' if celebration_success else 'FAIL'}")
        
        if rest_success and ws_success and celebration_success:
            print("\n🎊 ALL TESTS PASSED! Your Smart Stadium API is fully functional!")
            print("🚀 Ready for:")
            print("   📱 Mobile app integration")
            print("   🖥️ Real-time dashboard")
            print("   🎮 Live game monitoring")
            print("   🏈 Multi-client celebrations")
        else:
            print("\n⚠️ Some tests failed. Check the details above.")
        
        return rest_success and ws_success and celebration_success

async def main():
    """Main test function"""
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tester = ComprehensiveApiTest()
    success = await tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎯 Next steps:")
        print(f"   1. Try the WebSocket demo: python test_websocket.py")
        print(f"   2. Open API docs: http://localhost:8000/api/docs")
        print(f"   3. Connect your React dashboard!")
    
    return success

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")