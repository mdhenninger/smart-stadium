"""
Base Sport Monitor - Abstract base class for all sports
Defines common interface and functionality for sports monitoring
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio

class BaseSportMonitor(ABC):
    """
    Abstract base class for sport monitors
    Provides common functionality and interface for all sports
    """
    
    def __init__(self, sport_name: str, lights_controller):
        self.sport_name = sport_name
        self.lights_controller = lights_controller
        self.monitored_games = []  # List of game configurations being monitored
        self.game_scores = {}      # Track last known scores for each game
        self.monitoring = False
        
    @abstractmethod
    async def get_available_games(self) -> List[Dict[str, Any]]:
        """Get list of available games for this sport"""
        pass
    
    @abstractmethod
    async def get_current_game_data(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get current data for a specific game"""
        pass
    
    @abstractmethod
    async def process_game_update(self, game_config: Dict[str, Any]) -> None:
        """Process an update for a specific game"""
        pass
    
    async def start_monitoring(self, game_configs: List[Dict[str, Any]], 
                              check_interval: int = 10) -> None:
        """Start monitoring the specified games"""
        self.monitored_games = game_configs
        self.monitoring = True
        
        print(f"🎯 Starting {self.sport_name} monitoring")
        print(f"⚡ Polling: Checking every {check_interval} seconds")
        print(f"🎮 Monitoring {len(game_configs)} game(s):")
        
        for config in game_configs:
            game = config['game']
            teams = ", ".join(config['monitored_teams'])
            print(f"   🏈 {game['away_name']} @ {game['home_name']} (teams: {teams})")
        
        print("🚨 Waiting for events...")
        print("(Press Ctrl+C to stop monitoring)\n")
        
        # Initialize scores for all games
        for config in game_configs:
            game_id = config['game']['id']
            game_data = await self.get_current_game_data(game_id)
            if game_data and 'scores' in game_data:
                self.game_scores[game_id] = game_data['scores']
        
        try:
            while self.monitoring:
                # Process each monitored game
                for config in game_configs:
                    if self.monitoring:  # Check if still monitoring
                        await self.process_game_update(config)
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            await self.stop_monitoring()
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring and clean up"""
        self.monitoring = False
        
        # Stop any active ambient lighting
        if hasattr(self.lights_controller, 'red_zone_active') and self.lights_controller.red_zone_active:
            await self.lights_controller.stop_red_zone_ambient()
        
        print("💡 Setting lights to default...")
        await self.lights_controller.set_default_lighting()
        print(f"👋 {self.sport_name} monitoring ended.")
    
    def add_game_config(self, game_config: Dict[str, Any]) -> None:
        """Add a game configuration to the monitoring list"""
        self.monitored_games.append(game_config)
    
    def remove_game_config(self, game_id: str) -> None:
        """Remove a game configuration from monitoring"""
        self.monitored_games = [config for config in self.monitored_games 
                               if config['game']['id'] != game_id]
    
    def get_monitored_games(self) -> List[Dict[str, Any]]:
        """Get list of currently monitored games"""
        return self.monitored_games.copy()
    
    def is_monitoring(self) -> bool:
        """Check if currently monitoring"""
        return self.monitoring