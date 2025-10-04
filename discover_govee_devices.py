#!/usr/bin/env python3
"""
Discover Govee devices on local network
Scans for Govee devices that support LAN control
"""

import asyncio
import socket
import json
from typing import List, Dict

class GoveeDiscovery:
    """Discover Govee devices on local network."""
    
    SCAN_MESSAGE = {
        "msg": {
            "cmd": "scan",
            "data": {
                "account_topic": "reserve"
            }
        }
    }
    
    MULTICAST_IP = "239.255.255.250"
    PORT = 4001
    TIMEOUT = 5
    
    async def discover(self) -> List[Dict]:
        """Scan network for Govee devices."""
        print("🔍 Scanning for Govee devices on local network...")
        print(f"   Multicast: {self.MULTICAST_IP}:{self.PORT}")
        print(f"   Timeout: {self.TIMEOUT} seconds")
        print()
        
        devices = []
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.TIMEOUT)
        
        try:
            # Send scan message
            message = json.dumps(self.SCAN_MESSAGE).encode()
            sock.sendto(message, (self.MULTICAST_IP, self.PORT))
            print("📡 Scan request sent...")
            
            # Listen for responses
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = json.loads(data.decode())
                    
                    if response.get("msg", {}).get("cmd") == "scanResponse":
                        device_info = response.get("msg", {}).get("data", {})
                        device = {
                            "ip": device_info.get("ip"),
                            "device_id": device_info.get("device"),
                            "model": device_info.get("sku"),
                            "name": device_info.get("deviceName", "Unknown Govee Device"),
                            "ble_version": device_info.get("bleVersionHard"),
                            "wifi_version": device_info.get("wifiVersionHard"),
                        }
                        devices.append(device)
                        print(f"✅ Found: {device['name']} ({device['model']}) at {device['ip']}")
                        
                except socket.timeout:
                    break
                except Exception as e:
                    print(f"⚠️  Error parsing response: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error during discovery: {e}")
        finally:
            sock.close()
        
        return devices


async def main():
    """Run discovery and display results."""
    print("=" * 60)
    print("🏟️  GOVEE DEVICE DISCOVERY")
    print("=" * 60)
    print()
    
    discovery = GoveeDiscovery()
    devices = await discovery.discover()
    
    print()
    print("=" * 60)
    print(f"📊 RESULTS: Found {len(devices)} Govee device(s)")
    print("=" * 60)
    
    if devices:
        print()
        for i, device in enumerate(devices, 1):
            print(f"\n🔷 Device {i}:")
            print(f"   Name:     {device['name']}")
            print(f"   Model:    {device['model']}")
            print(f"   IP:       {device['ip']}")
            print(f"   ID:       {device['device_id']}")
            if device['ble_version']:
                print(f"   BLE Ver:  {device['ble_version']}")
            if device['wifi_version']:
                print(f"   WiFi Ver: {device['wifi_version']}")
        
        print()
        print("💡 Next steps:")
        print("   1. Note the IP addresses above")
        print("   2. Add them to config/govee_lights_config.json")
        print("   3. Run: pip install govee-api-laggat (if using cloud API)")
        print()
        
        # Generate config snippet
        print("📝 Config snippet for govee_lights_config.json:")
        print("-" * 60)
        config = {
            "devices": [
                {
                    "ip": device["ip"],
                    "device_id": device["device_id"],
                    "model": device["model"],
                    "name": device["name"],
                    "enabled": True
                }
                for device in devices
            ]
        }
        print(json.dumps(config, indent=2))
        print("-" * 60)
    else:
        print()
        print("❌ No Govee devices found on network.")
        print()
        print("💡 Troubleshooting:")
        print("   • Ensure Govee devices are powered on")
        print("   • Check they're connected to the same WiFi network")
        print("   • Some Govee models don't support LAN control")
        print("   • May need to enable LAN control in Govee app")
        print()
        print("📱 Govee models with LAN control:")
        print("   • H6199, H6163, H6110, H6117, H6159")
        print("   • H6141, H6142, H6143, H6144, H6148")
        print("   • H6160, H6168, H6182, H6046, etc.")
        print()


if __name__ == "__main__":
    asyncio.run(main())
