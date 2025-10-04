#!/usr/bin/env python3
"""
Query Govee API to list your devices
Uses your API key to discover device IDs and models
"""

import asyncio
import json
import aiohttp

API_KEY = "f1454325-8c4e-456a-9f36-1954a45c762c"
BASE_URL = "https://developer-api.govee.com"

async def get_devices():
    """Fetch device list from Govee API."""
    
    print("=" * 60)
    print("🏟️  GOVEE API DEVICE QUERY")
    print("=" * 60)
    print()
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"🌐 Endpoint: {BASE_URL}/v1/devices")
    print()
    
    headers = {
        "Govee-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            print("📡 Querying Govee API...")
            async with session.get(f"{BASE_URL}/v1/devices") as response:
                print(f"   Status: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ API Error: {error_text}")
                    return []
                
                data = await response.json()
                
                # API response structure: {"data": {"devices": [...]}, "message": "Success", "code": 200}
                devices = data.get("data", {}).get("devices", [])
                
                print()
                print("=" * 60)
                print(f"✅ Found {len(devices)} Govee device(s)")
                print("=" * 60)
                
                if devices:
                    print()
                    for i, device in enumerate(devices, 1):
                        print(f"\n🔷 Device {i}:")
                        print(f"   Name:       {device.get('deviceName', 'Unknown')}")
                        print(f"   Model:      {device.get('model', 'Unknown')}")
                        print(f"   Device ID:  {device.get('device', 'Unknown')}")
                        print(f"   Retrievable: {device.get('retrievable', False)}")
                        print(f"   Controllable: {device.get('controllable', False)}")
                        
                        # Show supported commands if available
                        supported_cmds = device.get('supportCmds', [])
                        if supported_cmds:
                            print(f"   Commands:   {', '.join(supported_cmds)}")
                        
                        # Show properties if available
                        properties = device.get('properties', {})
                        if properties:
                            print(f"   Properties: {json.dumps(properties, indent=15)}")
                    
                    print()
                    print("=" * 60)
                    print("💡 CONFIGURATION")
                    print("=" * 60)
                    print()
                    print("📝 Use this config for config/govee_config.json:")
                    print("-" * 60)
                    
                    config = {
                        "api_key": API_KEY,
                        "devices": [
                            {
                                "device_id": device.get("device"),
                                "model": device.get("model"),
                                "name": device.get("deviceName", f"Govee Light {i}"),
                                "location": f"Zone {i+3}",  # Start at Zone 4 since WiZ uses 1-3
                                "enabled": True
                            }
                            for i, device in enumerate(devices)
                            if device.get("controllable", False)
                        ]
                    }
                    
                    print(json.dumps(config, indent=2))
                    print("-" * 60)
                    
                else:
                    print()
                    print("❌ No devices found in your Govee account")
                    print()
                    print("💡 Troubleshooting:")
                    print("   • Ensure devices are added to your Govee Home app")
                    print("   • Check they're online and connected to WiFi")
                    print("   • API may take a few minutes to sync new devices")
                
                return devices
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

async def test_control(device_id: str, model: str):
    """Test controlling a specific device."""
    
    print()
    print("=" * 60)
    print("🧪 TESTING DEVICE CONTROL")
    print("=" * 60)
    print(f"Device: {device_id}")
    print(f"Model:  {model}")
    print()
    
    headers = {
        "Govee-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test: Turn on and flash blue
    command = {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "turn",
            "value": "on"
        }
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            print("📡 Sending: Turn ON")
            async with session.put(f"{BASE_URL}/v1/devices/control", json=command) as response:
                result = await response.json()
                print(f"   Response: {result.get('message', 'Unknown')}")
            
            await asyncio.sleep(1)
            
            # Flash blue
            command["cmd"] = {
                "name": "color",
                "value": {"r": 0, "g": 51, "b": 141}  # Bills blue
            }
            
            print("📡 Sending: Blue color (Bills blue)")
            async with session.put(f"{BASE_URL}/v1/devices/control", json=command) as response:
                result = await response.json()
                print(f"   Response: {result.get('message', 'Unknown')}")
            
            await asyncio.sleep(2)
            
            # Return to warm white
            command["cmd"] = {
                "name": "colorTem",
                "value": 2700
            }
            
            print("📡 Sending: Warm white (2700K)")
            async with session.put(f"{BASE_URL}/v1/devices/control", json=command) as response:
                result = await response.json()
                print(f"   Response: {result.get('message', 'Unknown')}")
            
            print()
            print("✅ Control test complete!")
            
    except Exception as e:
        print(f"❌ Control test failed: {e}")

async def main():
    """Main entry point."""
    devices = await get_devices()
    
    # Offer to test first controllable device
    if devices:
        controllable = [d for d in devices if d.get("controllable", False)]
        if controllable:
            print()
            print("=" * 60)
            choice = input("Test control first device? (y/n): ").strip().lower()
            if choice == 'y':
                device = controllable[0]
                await test_control(device["device"], device["model"])
    
    print()

if __name__ == "__main__":
    asyncio.run(main())
