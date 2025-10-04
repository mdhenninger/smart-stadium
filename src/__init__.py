"""
Smart Stadium - Core Components
Standalone smart lighting and game monitoring system
"""

from .device_manager import SmartDeviceManager
from .game_monitor import SmartStadiumGameMonitor, ESPNService
from .smart_lights import BillsCelebrationController

__version__ = "2.0.0"
__author__ = "Smart Stadium Team"

__all__ = [
    "SmartDeviceManager",
    "SmartStadiumGameMonitor", 
    "ESPNService",
    "BillsCelebrationController"
]