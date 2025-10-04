#!/usr/bin/env python3
"""
Enhanced WebSocket Test for Smart Stadium
Tests the new WebSocket reliability features
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

class WebSocketTester:
    def __init__(self, uri="ws://localhost:8000/api/ws"):
        self.uri = uri
        self.websocket = None
        self.running = False
        
    async def connect_and_test(self):
        """Connect and run comprehensive WebSocket tests"""
        print("🔌 Starting Enhanced WebSocket Tests")
        print(f"📡 Connecting to: {self.uri}")
        
        try:
            self.websocket = await websockets.connect(self.uri)
            print("✅ WebSocket connected successfully!")
            
            # Run test sequence
            await self.test_heartbeat()
            await self.test_subscriptions()
            await self.test_system_status()
            await self.test_error_handling()
            
            print("🎉 All WebSocket tests completed successfully!")
            
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
                print("🔌 WebSocket connection closed")
    
    async def test_heartbeat(self):
        """Test ping/pong heartbeat functionality"""
        print("\n💓 Testing Heartbeat (Ping/Pong)")
        
        # Send ping
        ping_message = {
            "type": "ping",
            "data": {"test": True},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.websocket.send(json.dumps(ping_message))
        print("📤 Sent ping message")
        
        # Wait for pong
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "pong":
                print("📥 Received pong response")
                print(f"   Server time: {response_data.get('data', {}).get('server_time')}")
                print("✅ Heartbeat test passed")
            else:
                print(f"⚠️ Unexpected response: {response_data}")
                
        except asyncio.TimeoutError:
            print("❌ Heartbeat test failed: No pong response")
    
    async def test_subscriptions(self):
        """Test subscription management"""
        print("\n📋 Testing Subscription Management")
        
        # Test subscription update
        subscription_message = {
            "action": "subscribe",
            "subscriptions": ["celebrations", "devices", "system_status"]
        }
        
        await self.websocket.send(json.dumps(subscription_message))
        print("📤 Sent subscription update")
        
        # Wait for confirmation
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "subscription_updated":
                subscriptions = response_data.get("data", {}).get("subscriptions", [])
                print(f"📥 Subscription confirmed: {subscriptions}")
                print("✅ Subscription test passed")
            else:
                print(f"⚠️ Unexpected response: {response_data}")
                
        except asyncio.TimeoutError:
            print("❌ Subscription test failed: No confirmation")
    
    async def test_system_status(self):
        """Test system status request"""
        print("\n⚙️ Testing System Status Request")
        
        status_request = {
            "type": "get_status",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.websocket.send(json.dumps(status_request))
        print("📤 Sent status request")
        
        # Wait for status response
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "system_status":
                status_data = response_data.get("data", {})
                print("📥 Received system status:")
                print(f"   API Status: {status_data.get('api_status', 'Unknown')}")
                print(f"   Connected Devices: {status_data.get('connected_devices', 0)}")
                print("✅ System status test passed")
            else:
                print(f"⚠️ Unexpected response: {response_data}")
                
        except asyncio.TimeoutError:
            print("❌ System status test failed: No response")
    
    async def test_error_handling(self):
        """Test error handling with invalid messages"""
        print("\n🚨 Testing Error Handling")
        
        # Send invalid JSON
        await self.websocket.send("invalid json")
        print("📤 Sent invalid JSON")
        
        # Wait for error response
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "error":
                error_details = response_data.get("data", {})
                print(f"📥 Received error response: {error_details.get('error')}")
                print("✅ Error handling test passed")
            else:
                print(f"⚠️ Unexpected response: {response_data}")
                
        except asyncio.TimeoutError:
            print("❌ Error handling test failed: No error response")
        
        # Send unknown message type
        unknown_message = {
            "type": "unknown_type",
            "data": {"test": True}
        }
        
        await self.websocket.send(json.dumps(unknown_message))
        print("📤 Sent unknown message type")
        
        # Wait for error response
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "error":
                print("📥 Received error for unknown message type")
                print("✅ Unknown message handling test passed")
            else:
                print(f"⚠️ Unexpected response: {response_data}")
                
        except asyncio.TimeoutError:
            print("❌ Unknown message test failed: No error response")

async def main():
    """Run the WebSocket tests"""
    print("🏟️ Smart Stadium WebSocket Enhanced Reliability Test")
    print("=" * 50)
    
    tester = WebSocketTester()
    await tester.connect_and_test()
    
    print("\n" + "=" * 50)
    print("🏁 WebSocket testing complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")