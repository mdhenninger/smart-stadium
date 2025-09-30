"""
Smart Stadium Controller

Main orchestrator for the Smart Stadium system. Coordinates:
- Sport monitoring modules
- Device controllers  
- Event detection and celebration triggering
- User interface and configuration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from devices.smart_lights import SmartStadiumLights
from sports.nfl_monitor import NFLMonitor
from core.config_manager import ConfigManager

class SmartStadiumController:
    """
    Main controller that orchestrates the Smart Stadium experience.
    
    Responsibilities:
    - Manage sport monitoring sessions
    - Coordinate device controllers
    - Trigger celebrations based on game events
    - Provide user interface for configuration
    """
    
    def __init__(self, config_path: str = None):
        # Setup logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        self.config = None  # Will be loaded in async init
        
        # Device and monitor initialization will happen in async_init
        self.lights_controller = None
        self.sport_monitors = {}
        
        # System state
        self.current_monitoring_session = None
        self.is_running = False
    
    async def async_init(self):
        """Async initialization that requires config loading"""
        # Load configuration
        self.config = await self.config_manager.load_config()
        
        # Initialize devices and sport monitors
        self.initialize_devices()
        self.initialize_sport_monitors()
    
    def initialize_devices(self):
        """Initialize all configured devices"""
        devices_config = self.config.get('devices', {})
        
        # Initialize smart lights
        lights_config = devices_config.get('smart_lights', {})
        if lights_config.get('enabled', False):
            light_ips = lights_config.get('ips', [])
            if light_ips:
                self.lights_controller = SmartStadiumLights(light_ips)
                
                # Configure brightness and color temp settings
                self.lights_controller.default_brightness = lights_config.get('default_brightness', 180)
                self.lights_controller.celebration_brightness = lights_config.get('celebration_brightness', 255)
                self.lights_controller.default_color_temp = lights_config.get('default_color_temp', 2700)
                
                self.logger.info(f"🎯 Initialized smart lights with {len(light_ips)} devices")
            else:
                self.logger.warning("⚠️ Smart lights enabled but no IPs configured")
        else:
            self.logger.info("💡 Smart lights disabled in configuration")
    
    def initialize_sport_monitors(self):
        """Initialize sport monitoring modules"""
        monitoring_config = self.config.get('monitoring', {})
        sports_enabled = monitoring_config.get('sports_enabled', {})
        
        # Initialize NFL monitor
        if sports_enabled.get('nfl', False) and self.lights_controller:
            self.sport_monitors['nfl'] = NFLMonitor(self.lights_controller)
            self.logger.info("🏈 NFL monitor initialized")
        
        # Future: Add other sports monitors here
        # if sports_enabled.get('nba', False):
        #     self.sport_monitors['nba'] = NBAMonitor(self.lights_controller)
    
    async def start_monitoring_session(self, sport: str, selected_games: List[Dict], polling_interval: int = 10):
        """Start a monitoring session for selected games"""
        if sport not in self.sport_monitors:
            raise ValueError(f"Sport '{sport}' not available or not enabled")
        
        if self.current_monitoring_session:
            await self.stop_monitoring_session()
        
        monitor = self.sport_monitors[sport]
        self.current_monitoring_session = {
            'sport': sport,
            'monitor': monitor,
            'games': selected_games
        }
        
        self.is_running = True
        self.logger.info(f"🎯 Starting {sport.upper()} monitoring session")
        
        # Start monitoring
        await monitor.start_monitoring(selected_games, polling_interval)
    
    async def stop_monitoring_session(self):
        """Stop the current monitoring session"""
        if self.current_monitoring_session:
            monitor = self.current_monitoring_session['monitor']
            await monitor.stop_monitoring()
            self.current_monitoring_session = None
        
        self.is_running = False
        self.logger.info("⏹️ Monitoring session stopped")
    
    async def get_available_games(self, sport: str) -> List[Dict]:
        """Get available games for a sport"""
        if sport not in self.sport_monitors:
            return []
        
        monitor = self.sport_monitors[sport]
        return await monitor.get_available_games()
    
    def get_favorite_teams(self, sport: str) -> List[str]:
        """Get favorite teams for a sport"""
        monitoring_config = self.config.get('monitoring', {})
        favorites = monitoring_config.get('favorite_teams', {})
        return favorites.get(sport, [])
    
    def is_monitoring_active(self) -> bool:
        """Check if currently monitoring games"""
        return self.is_running
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            'lights_connected': self.lights_controller is not None,
            'available_sports': list(self.sport_monitors.keys()),
            'monitoring': self.is_running,
            'current_session': self.current_monitoring_session['sport'] if self.current_monitoring_session else None
        }
        
        if self.lights_controller:
            status['light_count'] = len(self.lights_controller.lights)
            status['light_ips'] = self.lights_controller.light_ips
        
        return status
    
    async def test_connectivity(self) -> bool:
        """Test connectivity to all devices"""
        if not self.lights_controller:
            print("⚠️ No lights controller initialized")
            return False
        
        return await self.lights_controller.test_connectivity()
    
    async def test_devices(self) -> bool:
        """Test connectivity to all devices (alias for test_connectivity)"""
        return await self.test_connectivity()
    
    async def run(self):
        """Run an interactive Smart Stadium session"""
        await self.run_interactive_session()
    
    async def run_interactive_session(self):
        """Run an interactive Smart Stadium session"""
        print("\n🏟️ SMART STADIUM - INTERACTIVE MODE")
        print("=" * 50)
        
        # Test connectivity first
        print("\n🧪 Testing device connectivity...")
        if self.lights_controller:
            connectivity_ok = await self.test_connectivity()
            if not connectivity_ok:
                print("⚠️ Warning: Some devices not responding (lights may be offline)")
                print("   System will continue with limited functionality")
        else:
            print("⚠️ No lights controller available")
        
        # Show available sports
        print(f"\n🎮 Available Sports: {', '.join(self.sport_monitors.keys())}")
        
        # For now, if NFL is available, start NFL monitoring demo
        if 'nfl' in self.sport_monitors:
            print("\n🏈 Starting NFL monitoring demo...")
            try:
                games = await self.get_available_games('nfl')
                print(f"📊 Found {len(games)} NFL games")
                
                if games:
                    # For demo, we could auto-select some games or show menu
                    # For now, just show that the system is working
                    print("✅ Smart Stadium system initialized successfully!")
                    print("💡 System ready for game monitoring")
                else:
                    print("ℹ️ No NFL games found today")
            except Exception as e:
                print(f"❌ Error fetching NFL games: {e}")
        
        print("\n👋 Interactive session complete")