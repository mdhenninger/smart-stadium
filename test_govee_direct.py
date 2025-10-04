#!/usr/bin/env python3
"""
Test direct communication with Govee device at specific IP
"""

import socket
import json
import time

GOVEE_IP = "192.168.86.35"
GOVEE_PORT = 4003  # Standard Govee control port

def test_govee_device(ip: str):
    """Try to communicate with Govee device."""
    
    print(f"🔍 Testing Govee device at {ip}:{GOVEE_PORT}")
    print("=" * 60)
    
    # Test 1: Device status query
    print("\n📡 Test 1: Querying device status...")
    status_cmd = {
        "msg": {
            "cmd": "devStatus",
            "data": {}
        }
    }
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        message = json.dumps(status_cmd).encode()
        sock.sendto(message, (ip, GOVEE_PORT))
        print(f"   Sent: {status_cmd}")
        
        try:
            data, addr = sock.recvfrom(1024)
            response = json.loads(data.decode())
            print(f"✅ Response received!")
            print(f"   From: {addr}")
            print(f"   Data: {json.dumps(response, indent=2)}")
            return True
        except socket.timeout:
            print("⏱️  No response (timeout)")
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sock.close()
    
    # Test 2: Try scan command
    print("\n📡 Test 2: Trying scan command...")
    scan_cmd = {
        "msg": {
            "cmd": "scan",
            "data": {
                "account_topic": "reserve"
            }
        }
    }
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        message = json.dumps(scan_cmd).encode()
        sock.sendto(message, (ip, GOVEE_PORT))
        print(f"   Sent: {scan_cmd}")
        
        try:
            data, addr = sock.recvfrom(1024)
            response = json.loads(data.decode())
            print(f"✅ Response received!")
            print(f"   From: {addr}")
            print(f"   Data: {json.dumps(response, indent=2)}")
            return True
        except socket.timeout:
            print("⏱️  No response (timeout)")
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sock.close()
    
    # Test 3: Try different port (4001)
    print("\n📡 Test 3: Trying port 4001...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        message = json.dumps(status_cmd).encode()
        sock.sendto(message, (ip, 4001))
        print(f"   Sent to port 4001")
        
        try:
            data, addr = sock.recvfrom(1024)
            response = json.loads(data.decode())
            print(f"✅ Response received!")
            print(f"   From: {addr}")
            print(f"   Data: {json.dumps(response, indent=2)}")
            return True
        except socket.timeout:
            print("⏱️  No response (timeout)")
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sock.close()
    
    print("\n" + "=" * 60)
    print("❌ Device at", ip, "does not respond to Govee LAN protocol")
    print()
    print("💡 This likely means:")
    print("   • Device doesn't support LAN control")
    print("   • LAN control is disabled in Govee app")
    print("   • Device uses cloud API only")
    print()
    print("📱 Check your Govee Home app:")
    print("   1. Open the bulb settings")
    print("   2. Look for 'LAN Control' option")
    print("   3. Enable it if available")
    print("   4. Try this test again")
    print()
    return False

if __name__ == "__main__":
    test_govee_device(GOVEE_IP)
