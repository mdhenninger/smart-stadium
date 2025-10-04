"""
Smart Stadium - Enhanced NFL Game Monitor
Standalone ESPN API integration for live game monitoring
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ESPNService:
    """ESPN API service for fetching live game data"""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    @staticmethod
    async def fetch_live_games() -> List[Dict[str, Any]]:
        """Fetch current live NFL games"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{ESPNService.BASE_URL}/scoreboard"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('events', [])
                    else:
                        logger.error(f"ESPN API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching live games: {e}")
            return []

class SmartStadiumGameMonitor:
    """Enhanced game monitor for Smart Stadium system"""
    
    def __init__(self, teams: List[str] = None, poll_interval: int = 15):
        self.monitored_teams = teams or ["Buffalo", "Buffalo Bills", "BUF"]
        self.poll_interval = poll_interval
        self.espn_service = ESPNService()
        self.monitoring = False
        self.current_games = {}
        self.callbacks = []
        
        logger.info("🎮 Initializing Smart Stadium Game Monitor...")
        logger.info(f"📺 Monitoring teams: {', '.join(self.monitored_teams)}")
        logger.info(f"⏱️ Poll interval: {poll_interval} seconds")
        
    def add_callback(self, callback):
        """Add callback for game events"""
        self.callbacks.append(callback)
        
    async def start_monitoring(self):
        """Start the game monitoring loop"""
        if self.monitoring:
            logger.warning("🔄 Game monitoring already running")
            return
            
        self.monitoring = True
        logger.info("✅ Smart Stadium Game Monitor initialized successfully!")
        
        while self.monitoring:
            try:
                await self.check_games()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(self.poll_interval)
                
    async def stop_monitoring(self):
        """Stop the game monitoring"""
        self.monitoring = False
        logger.info("🛑 Stopping Smart Stadium game monitoring...")
        
    async def check_games(self):
        """Check for live games and updates"""
        try:
            games = await self.espn_service.fetch_live_games()
            
            for game in games:
                game_id = game.get('id')
                if not game_id:
                    continue
                    
                # Check if any monitored team is playing
                teams = game.get('competitions', [{}])[0].get('competitors', [])
                team_names = []
                
                for team in teams:
                    team_info = team.get('team', {})
                    team_names.extend([
                        team_info.get('displayName', ''),
                        team_info.get('shortDisplayName', ''),
                        team_info.get('abbreviation', '')
                    ])
                
                # Check if any monitored team is in this game
                if any(monitored_team in team_names for monitored_team in self.monitored_teams):
                    await self.process_game_update(game)
                    
        except Exception as e:
            logger.error(f"❌ Error checking games: {e}")
            
    async def process_game_update(self, game_data: Dict[str, Any]):
        """Process game update and trigger events"""
        try:
            game_id = game_data.get('id')
            competition = game_data.get('competitions', [{}])[0]
            
            # Extract game info
            game_info = {
                'id': game_id,
                'status': competition.get('status', {}),
                'competitors': competition.get('competitors', []),
                'last_play': None
            }
            
            # Check for scoring plays
            if 'drives' in competition:
                drives = competition.get('drives', {})
                if 'current' in drives:
                    current_drive = drives['current']
                    if 'plays' in current_drive and current_drive['plays']:
                        last_play = current_drive['plays'][-1]
                        game_info['last_play'] = last_play
                        
                        # Check for touchdown, field goal, etc.
                        await self.check_scoring_play(last_play, game_info)
            
            # Store current game state
            self.current_games[game_id] = game_info
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    await callback(game_info)
                except Exception as e:
                    logger.error(f"❌ Error in callback: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error processing game update: {e}")
            
    async def check_scoring_play(self, play: Dict[str, Any], game_info: Dict[str, Any]):
        """Check if play was a scoring play and trigger celebration"""
        try:
            play_type = play.get('type', {}).get('text', '').lower()
            scoring_play = play.get('scoringPlay', False)
            
            if scoring_play:
                if 'touchdown' in play_type:
                    logger.info("🏈 TOUCHDOWN! Triggering celebration")
                    await self.trigger_event('touchdown', play, game_info)
                elif 'field goal' in play_type:
                    logger.info("🎯 FIELD GOAL! Triggering celebration")
                    await self.trigger_event('field_goal', play, game_info)
                elif 'safety' in play_type:
                    logger.info("🛡️ SAFETY! Triggering celebration")
                    await self.trigger_event('safety', play, game_info)
                    
        except Exception as e:
            logger.error(f"❌ Error checking scoring play: {e}")
            
    async def trigger_event(self, event_type: str, play: Dict[str, Any], game_info: Dict[str, Any]):
        """Trigger celebration event"""
        event_data = {
            'type': event_type,
            'play': play,
            'game': game_info,
            'timestamp': datetime.now().isoformat()
        }
        
        # Notify all callbacks
        for callback in self.callbacks:
            try:
                await callback(event_data)
            except Exception as e:
                logger.error(f"❌ Error triggering event callback: {e}")
                
    def get_current_games(self) -> Dict[str, Any]:
        """Get current game status"""
        return self.current_games
        
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self.monitoring