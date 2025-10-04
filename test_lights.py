#!/usr/bin/env python3
"""Quick test to check WiZ light connectivity"""
import asyncio
from pywizlight import wizlight

async def test_lights():
    ips = ["192.168.86.41", "192.168.86.47", "192.168.86.48"]
    names = ["Living Room", "Kitchen", "Bedroom"]
    
    for ip, name in zip(ips, names):
        try:
            print(f"Testing {name} ({ip})...")
            light = wizlight(ip)
            state = await light.updateState()
            if state:
                print(f"  ✅ ONLINE - State: {state.get_state()}")
            else:
                print(f"  ❌ OFFLINE - No response")
        except Exception as e:
            print(f"  ❌ ERROR - {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_lights())
