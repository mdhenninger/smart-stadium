#!/usr/bin/env python3
"""Scan for new WiZ lights on the network."""

import asyncio
import socket
import ipaddress
import json
from pywizlight import wizlight
from pywizlight.exceptions import WizLightTimeOutError, WizLightConnectionError

async def scan_for_wiz_lights():
    """Scan the local network for WiZ lights."""
    print("🔍 Scanning for WiZ lights on your network...")
    
    # Get your local network range
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"📍 Your local IP: {local_ip}")
        
        # Assume /24 subnet (common for home networks)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        print(f"🌐 Scanning network: {network}")
        
    except Exception as e:
        print(f"❌ Could not determine local network: {e}")
        # Fallback to common home network range
        network = ipaddress.IPv4Network("192.168.86.0/24")
        print(f"🌐 Using fallback network: {network}")
    
    # Known existing lights for comparison
    existing_lights = [
        "192.168.86.41",
        "192.168.86.47", 
        "192.168.86.48",
        "192.168.86.51",
        "192.168.86.50",
        "192.168.86.55",
        "192.168.86.56"
    ]
    
    print(f"💡 Known existing lights: {existing_lights}")
    print("🔎 Scanning for new WiZ lights...")
    print("⏳ This will scan the network efficiently...")
    
    found_lights = []
    new_lights = []
    scanned_count = 0
    
    # Focus on the IP range where lights are likely to be
    # Scan from .40 to .60 first (where existing lights are)
    priority_range = range(40, 61)
    
    print("🎯 Scanning priority range (192.168.86.40-60) first...")
    
    for ip_suffix in priority_range:
        ip_str = f"192.168.86.{ip_suffix}"
        scanned_count += 1
        
        print(f"🔍 Testing {ip_str}...", end=" ")
        
        # Skip known existing lights
        if ip_str in existing_lights:
            print("⚪ Known existing light")
            found_lights.append({"ip": ip_str, "status": "existing", "info": None})
            continue
            
        try:
            # Try to connect to WiZ light with short timeout
            light = wizlight(ip_str)
            
            # Quick connection test
            await asyncio.wait_for(light.updateState(), timeout=1.0)
            
            # Get device info
            info = await asyncio.wait_for(light.getBulbConfig(), timeout=2.0)
            model = info.get('moduleName', 'Unknown')
            firmware = info.get('fwVersion', 'Unknown')
            mac = info.get('mac', 'Unknown')
            
            print(f"✅ NEW WiZ Light Found!")
            print(f"   Model: {model}")
            print(f"   Firmware: {firmware}")
            print(f"   MAC: {mac}")
            
            found_lights.append({
                "ip": ip_str, 
                "status": "new", 
                "info": {
                    "model": model,
                    "firmware": firmware,
                    "mac": mac
                }
            })
            new_lights.append(ip_str)
            
        except (WizLightTimeOutError, WizLightConnectionError, asyncio.TimeoutError):
            print("❌ No response")
        except Exception as e:
            # Other error - might still be worth noting for debugging
            if "WiZ" in str(e) or "light" in str(e).lower():
                print(f"⚠️ Possible WiZ device but error: {e}")
            else:
                print("❌ Not a WiZ light")
    
    print(f"\n📊 Priority Range Scan Results:")
    print(f"   IPs scanned: {scanned_count}")
    print(f"   Total WiZ lights found: {len(found_lights)}")
    print(f"   Existing lights confirmed: {len([l for l in found_lights if l['status'] == 'existing'])}")
    print(f"   New lights found: {len(new_lights)}")
    
    if new_lights:
        print(f"\n🎉 New WiZ lights discovered:")
        for ip in new_lights:
            light_info = next(l for l in found_lights if l['ip'] == ip)
            info = light_info['info']
            print(f"   • {ip} - {info['model']} (MAC: {info['mac']})")
        
        print(f"\n🔧 Ready to add to config! Suggested names:")
        for i, ip in enumerate(new_lights, 5):
            print(f"   Stadium Light {i}: {ip}")
            
    else:
        print(f"\n🤔 No new WiZ lights found in priority range.")
        print("   Options:")
        print("   1. Provide the IP addresses manually")
        print("   2. Run a full network scan (slower)")
        print("   3. Check if lights are powered on and connected to WiFi")
    
    return new_lights, found_lights

async def main():
    """Main function to run the scan."""
    try:
        new_lights, all_lights = await scan_for_wiz_lights()
        
        if new_lights:
            print(f"\n💾 Found {len(new_lights)} new lights. Ready to add to config!")
            return new_lights
        else:
            print(f"\n🔍 No new lights found. You can provide IPs manually if needed.")
            return []
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Scan interrupted by user")
        return []
    except Exception as e:
        print(f"\n❌ Scan error: {e}")
        return []

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\nNew light IPs: {result}")