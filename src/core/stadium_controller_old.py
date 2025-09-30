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

from ..devices.smart_lights import SmartStadiumLights
from ..sports.nfl_monitor import NFLMonitor
from .config_manager import ConfigManager

class SmartStadiumController:
    """
    Main controller that orchestrates the Smart Stadium experience.
    
    Responsibilities:
    - Manage sport monitoring sessions
    - Coordinate device controllers
    - Trigger celebrations based on game events
    - Provide user interface for configuration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Smart Stadium Controller"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.celebration_engine = CelebrationEngine(config.get('devices', {}))
        self.event_detector = EventDetector(config.get('sports', {}))
        
        # State tracking
        self.active_sessions = {}  # Track active monitoring sessions
        self.is_running = False
        
        self.logger.info("Smart Stadium Controller initialized")
    
    async def test_devices(self) -> bool:
        """Test connectivity to all configured devices"""
        self.logger.info("Testing device connectivity...")
        
        # Test celebration engine devices
        device_status = await self.celebration_engine.test_connectivity()
        
        if device_status:
            self.logger.info("✅ All devices responding")
            return True
        else:
            self.logger.warning("⚠️ Some devices not responding")
            return False
    
    async def run(self):
        """Main run loop for Smart Stadium"""
        self.is_running = True
        self.logger.info("🚀 Smart Stadium starting...")
        
        try:
            # Show sport selection menu
            await self._show_sport_selection()
            
            # Start monitoring selected games
            await self._start_monitoring()
            
        except KeyboardInterrupt:
            self.logger.info("Smart Stadium stopped by user")
        finally:
            self.is_running = False
            await self._cleanup()
    
    async def _show_sport_selection(self):
        """Display sport and game selection interface"""
        print("\n🏟️ SMART STADIUM - SPORT SELECTION")
        print("=" * 50)
        print("Available Sports:")
        print("1. 🏈 NFL Football")
        print("2. 🏈 College Football") 
        print("3. 🏀 NBA Basketball (Coming Soon)")
        print("4. 🏒 NHL Hockey (Coming Soon)")
        print("5. ⚾ MLB Baseball (Coming Soon)")
        print("-" * 50)
        
        try:
            choice = input("Select sport (1-5): ").strip()
            
            if choice == "1":
                await self._configure_nfl_monitoring()
            elif choice == "2":
                await self._configure_college_monitoring()
            else:
                print("🚧 Coming soon! For now, try NFL (1) or College Football (2)")
                await self._show_sport_selection()
                
        except (EOFError, KeyboardInterrupt):
            print("\n⏹️ Selection cancelled")
            raise KeyboardInterrupt
    
    async def _configure_nfl_monitoring(self):
        """Configure NFL game monitoring"""
        print("\n🏈 NFL MONITORING SETUP")
        print("=" * 30)
        
        # This will import and use our existing NFL monitoring logic
        from sports.nfl_monitor import NFLMonitor
        
        nfl_monitor = NFLMonitor(self.config)
        games = await nfl_monitor.get_available_games()
        
        if not games:
            print("😴 No NFL games available today!")
            return
            
        # Let user select games and teams
        selected_games = await nfl_monitor.select_games_interactive(games)
        
        if selected_games:
            # Store monitoring session
            self.active_sessions['nfl'] = {
                'monitor': nfl_monitor,
                'games': selected_games,
                'sport': 'NFL'
            }
            print(f"✅ Configured monitoring for {len(selected_games)} NFL game(s)")
    
    async def _configure_college_monitoring(self):
        """Configure College Football game monitoring"""
        print("\n🏈 COLLEGE FOOTBALL MONITORING SETUP")
        print("=" * 40)
        
        # Future: Import college monitoring logic
        # from sports.college_monitor import CollegeMonitor
        print("🚧 College Football monitoring coming soon!")
        print("   Will integrate existing college football system")
    
    async def _start_monitoring(self):
        """Start monitoring all configured sessions"""
        if not self.active_sessions:
            print("\n😕 No monitoring sessions configured. Exiting...")
            return
            
        print(f"\n🎯 Starting monitoring for {len(self.active_sessions)} sport(s)...")
        
        # Create monitoring tasks for each active session
        tasks = []
        for sport, session in self.active_sessions.items():
            task = asyncio.create_task(
                self._monitor_sport_session(sport, session)
            )
            tasks.append(task)
        
        # Wait for all monitoring tasks
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _monitor_sport_session(self, sport: str, session: Dict[str, Any]):
        """Monitor a specific sport session"""
        monitor = session['monitor']
        games = session['games']
        
        self.logger.info(f"🎮 Starting {sport} monitoring for {len(games)} game(s)")
        
        try:
            # Start the sport-specific monitoring
            await monitor.start_monitoring(
                games, 
                event_callback=self._handle_game_event
            )
        except Exception as e:
            self.logger.error(f"Error monitoring {sport}: {e}")
    
    async def _handle_game_event(self, event: Dict[str, Any]):
        """Handle game events and trigger appropriate celebrations"""
        event_type = event.get('type')
        team = event.get('team')
        game_info = event.get('game', {})
        
        self.logger.info(f"🎉 Game Event: {event_type} for {team}")
        
        # Trigger appropriate celebration
        if event_type == 'touchdown':
            await self.celebration_engine.celebrate_touchdown(team, game_info)
        elif event_type == 'field_goal':
            await self.celebration_engine.celebrate_field_goal(team, game_info)
        elif event_type == 'red_zone_enter':
            await self.celebration_engine.start_red_zone_ambient(team, game_info)
        elif event_type == 'red_zone_exit':
            await self.celebration_engine.stop_red_zone_ambient()
        elif event_type == 'turnover':
            await self.celebration_engine.celebrate_turnover(team, game_info)
        elif event_type == 'sack':
            await self.celebration_engine.celebrate_sack(team, game_info)
        elif event_type == 'big_play':
            await self.celebration_engine.celebrate_big_play(team, game_info)
        elif event_type == 'victory':
            await self.celebration_engine.celebrate_victory(team, game_info)
        else:
            self.logger.debug(f"Unhandled event type: {event_type}")
    
    async def _cleanup(self):
        """Cleanup resources and reset devices"""
        self.logger.info("🧹 Cleaning up Smart Stadium...")
        
        # Stop any active celebrations
        await self.celebration_engine.stop_all_celebrations()
        
        # Reset devices to default state
        await self.celebration_engine.reset_devices()
        
        # Clear active sessions
        self.active_sessions.clear()
        
        self.logger.info("✅ Cleanup complete")