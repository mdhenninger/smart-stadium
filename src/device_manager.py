"""
Smart Stadium Device Manager
Standalone device management for Smart Stadium system
"""

import json
import os
from typing import List, Dict, Any, Optional
from .smart_lights import BillsCelebrationController

class SmartDeviceManager:
    """Manages smart devices for the Smart Stadium system"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'wiz_lights_config.json')
        
        self.config_path = config_path
        self.devices = []
        self.light_controller = None
        self.load_configuration()
        
    def load_configuration(self):
        """Load device configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Extract device IPs
            device_ips = []
            self.devices = []
            
            for device in config.get('devices', []):
                if device.get('enabled', True):
                    device_ips.append(device['ip'])
                    self.devices.append({
                        'ip': device['ip'],
                        'name': device.get('name', f"Device {device['ip']}"),
                        'location': device.get('location', 'Unknown'),
                        'enabled': device.get('enabled', True)
                    })
            
            # Initialize light controller with device IPs
            if device_ips:
                self.light_controller = BillsCelebrationController(device_ips)
                
            print(f"📱 Loaded {len(self.devices)} managed devices")
                
        except FileNotFoundError:
            print(f"⚠️ Configuration file not found: {self.config_path}")
            self.devices = []
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.devices = []
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of all managed devices"""
        return self.devices
    
    def get_enabled_devices(self) -> List[Dict[str, Any]]:
        """Get list of enabled devices only"""
        return [device for device in self.devices if device.get('enabled', True)]
    
    def get_device_count(self) -> int:
        """Get total number of managed devices"""
        return len(self.devices)
    
    def get_enabled_device_count(self) -> int:
        """Get number of enabled devices"""
        return len(self.get_enabled_devices())
    
    async def trigger_celebration(self, celebration_type: str, team: str = "Bills") -> bool:
        """Trigger a celebration on all enabled devices"""
        if not self.light_controller:
            print("❌ No light controller available")
            return False
            
        try:
            if celebration_type.lower() == "touchdown":
                await self.light_controller.touchdown_celebration()
            elif celebration_type.lower() == "field_goal":
                await self.light_controller.field_goal_celebration()
            elif celebration_type.lower() == "sack":
                await self.light_controller.sack_celebration()
            elif celebration_type.lower() == "interception":
                await self.light_controller.interception_celebration()
            elif celebration_type.lower() == "fumble_recovery":
                await self.light_controller.fumble_recovery_celebration()
            else:
                print(f"⚠️ Unknown celebration type: {celebration_type}")
                return False
                
            return True
        except Exception as e:
            print(f"❌ Error triggering celebration: {e}")
            return False
    
    async def set_ambient_lighting(self, mode: str = "game_day") -> bool:
        """Set ambient lighting mode"""
        if not self.light_controller:
            return False
            
        try:
            if mode == "red_zone":
                await self.light_controller.red_zone_ambient()
            elif mode == "game_day":
                await self.light_controller.game_day_ambient()
            elif mode == "victory":
                await self.light_controller.victory_celebration()
            else:
                # Default to game day ambient
                await self.light_controller.game_day_ambient()
            return True
        except Exception as e:
            print(f"❌ Error setting ambient lighting: {e}")
            return False
    
    def get_device_status_summary(self) -> Dict[str, Any]:
        """Get summary of device status"""
        return {
            "total_devices": self.get_device_count(),
            "enabled_devices": self.get_enabled_device_count(),
            "devices": self.get_devices(),
            "controller_ready": self.light_controller is not None
        }