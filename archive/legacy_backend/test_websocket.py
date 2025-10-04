"""
Smart Stadium WebSocket Test Client
Demonstrates real-time communication features
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

class WebSocketTestClient:
    def __init__(self, uri="ws://localhost:8000/api/ws"):
        self.uri = uri
        self.websocket = None
        self.running = False
        
    async def connect(self, client_id="test_client", subscriptions="all"):
        """Connect to the WebSocket server"""
        try:
            # Add query parameters for enhanced connection
            uri_with_params = f"{self.uri}?client_id={client_id}&subscriptions={subscriptions}"
            self.websocket = await websockets.connect(uri_with_params)
            self.running = True
            print(f"🔌 Connected to Smart Stadium WebSocket")
            print(f"📍 URI: {uri_with_params}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from WebSocket")
    
    async def send_message(self, message_type, data=None):
        """Send a message to the server"""
        if not self.websocket:
            print("❌ Not connected")
            return
            
        message = {
            "type": message_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent: {message_type}")
        except Exception as e:
            print(f"❌ Send failed: {e}")
    
    async def listen(self):
        """Listen for messages from the server"""
        if not self.websocket:
            print("❌ Not connected")
            return
            
        try:
            while self.running:
                message = await self.websocket.recv()
                await self.handle_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by server")
        except Exception as e:
            print(f"❌ Listen error: {e}")
    
    async def handle_message(self, message):
        """Handle incoming messages"""
        message_type = message.get("type", "unknown")
        data = message.get("data", {})
        timestamp = message.get("timestamp", "unknown")
        
        if message_type == "connection_established":
            print(f"✅ {data.get('message', 'Connected')}")
            print(f"🔗 Connection ID: {data.get('connection_id', 'Unknown')}")
            available_subs = data.get('available_subscriptions', [])
            print(f"📋 Available subscriptions: {', '.join(available_subs)}")
            
        elif message_type == "celebration_event":
            event_type = data.get("event_type", "unknown")
            celebration_type = data.get("celebration_type", "unknown")
            team_name = data.get("team_name", "unknown")
            
            if event_type == "celebration_started":
                print(f"🎉 CELEBRATION STARTED: {celebration_type.upper()} for {team_name}")
                print(f"   📊 Devices: {data.get('devices_count', 0)}")
            elif event_type == "celebration_progress":
                progress = data.get("progress", 0)
                print(f"⚡ CELEBRATION PROGRESS: {celebration_type.upper()} - {progress}%")
            elif event_type == "celebration_ended":
                print(f"🏁 CELEBRATION ENDED: {celebration_type.upper()} for {team_name}")
                
        elif message_type == "device_event":
            event_type = data.get("event_type", "unknown")
            device_name = data.get("device_name", "unknown")
            status = data.get("status", "unknown")
            print(f"📱 DEVICE EVENT: {device_name} - {event_type} ({status})")
            
        elif message_type == "team_event":
            old_team = data.get("old_team_id", "unknown")
            new_team = data.get("new_team_id", "unknown")
            team_name = data.get("team_name", "unknown")
            print(f"🏈 TEAM CHANGED: {old_team} → {new_team} ({team_name})")
            
        elif message_type == "system_status":
            total_devices = data.get("total_devices", 0)
            online_devices = data.get("online_devices", 0)
            current_team = data.get("current_team", {})
            print(f"📊 SYSTEM STATUS: {online_devices}/{total_devices} devices online")
            print(f"   🏈 Current team: {current_team.get('full_name', 'Unknown')}")
            
        elif message_type == "pong":
            print(f"🏓 Pong received")
            
        elif message_type == "error":
            error = data.get("error", "Unknown error")
            print(f"❌ SERVER ERROR: {error}")
            
        else:
            print(f"📩 {message_type.upper()}: {data}")
    
    async def run_interactive_demo(self):
        """Run an interactive demonstration"""
        print("\n🎮 SMART STADIUM WEBSOCKET DEMO")
        print("=" * 50)
        
        # Connect
        if not await self.connect("demo_client", "all"):
            return
        
        # Start listening in background
        listen_task = asyncio.create_task(self.listen())
        
        try:
            # Wait a moment for welcome message
            await asyncio.sleep(2)
            
            print("\n🧪 Testing WebSocket features...")
            
            # Test ping
            print("\n📍 Testing ping...")
            await self.send_message("ping")
            await asyncio.sleep(1)
            
            # Test subscription update
            print("\n📍 Testing subscription update...")
            await self.send_message("subscribe", {"subscriptions": ["celebrations", "devices"]})
            await asyncio.sleep(1)
            
            # Test status request
            print("\n📍 Requesting system status...")
            await self.send_message("get_status")
            await asyncio.sleep(2)
            
            # Test connection stats (admin feature)
            print("\n📍 Requesting connection stats...")
            await self.send_message("get_connection_stats")
            await asyncio.sleep(2)
            
            print("\n🎉 Demo complete! WebSocket is working perfectly!")
            print("💡 Now try triggering celebrations via the API to see real-time updates!")
            print("   Example: POST http://localhost:8000/api/celebrations/sack")
            
            # Keep listening for real-time events
            print("\n👂 Listening for real-time events (Press Ctrl+C to stop)...")
            await listen_task
            
        except KeyboardInterrupt:
            print("\n🛑 Demo stopped by user")
        finally:
            await self.disconnect()

async def main():
    """Main demo function"""
    client = WebSocketTestClient()
    await client.run_interactive_demo()

if __name__ == "__main__":
    print("🏈 Smart Stadium WebSocket Test Client")
    print("Make sure the API server is running on localhost:8000")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")