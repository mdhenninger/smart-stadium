"""
NFL Sports Monitor for Smart Stadium
Handles NFL game monitoring and event detection
"""

import asyncio
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_sport_monitor import BaseSportMonitor
from devices.smart_lights import SmartStadiumLights

class NFLMonitor(BaseSportMonitor):
    """
    NFL-specific sports monitor
    Handles game tracking, score detection, and event celebrations
    """
    
    def __init__(self, lights_controller: SmartStadiumLights):
        super().__init__("NFL", lights_controller)
        self.api_url = 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
        
        # NFL-specific tracking
        self.red_zone_status = {}  # Track red zone status per game
        self.last_play_ids = {}    # Track last play ID per game for play detection
        
    async def get_available_games(self) -> List[Dict[str, Any]]:
        """Get all NFL games for today"""
        print("🔍 Searching for NFL games today...")
        
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = []
            events = data.get('events', [])
            
            for game in events:
                competitors = game.get('competitions', [{}])[0].get('competitors', [])
                
                home_team_abbr = ""
                away_team_abbr = ""
                home_team_name = ""
                away_team_name = ""
                home_score = 0
                away_score = 0
                
                for competitor in competitors:
                    team = competitor.get('team', {})
                    score = int(competitor.get('score', 0))
                    abbr = team.get('abbreviation', '')
                    name = team.get('displayName', 'Unknown')
                    
                    if competitor.get('homeAway') == 'home':
                        home_team_abbr = abbr
                        home_team_name = name
                        home_score = score
                    else:
                        away_team_abbr = abbr
                        away_team_name = name
                        away_score = score
                
                status_info = game.get('status', {})
                status_name = status_info.get('type', {}).get('name', 'Unknown')
                
                game_info = {
                    'id': game.get('id'),
                    'home_abbr': home_team_abbr,
                    'away_abbr': away_team_abbr,
                    'home_name': home_team_name,
                    'away_name': away_team_name,
                    'home_score': home_score,
                    'away_score': away_score,
                    'status': status_name,
                    'sport': 'NFL'
                }
                games.append(game_info)
            
            print(f"📊 Found {len(games)} NFL games")
            return games
            
        except Exception as e:
            print(f"❌ Error fetching NFL games: {e}")
            return []
    
    async def get_current_game_data(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get current game data including scores and red zone status"""
        try:
            response = requests.get(self.api_url, timeout=8)
            response.raise_for_status()
            data = response.json()
            
            games = data.get('events', [])
            for game in games:
                if game.get('id') == game_id:
                    competitors = game.get('competitions', [{}])[0].get('competitors', [])
                    competition = game.get('competitions', [{}])[0]
                    
                    scores = {}
                    status = game.get('status', {}).get('type', {}).get('name', 'Unknown')
                    red_zone_info = {}
                    
                    # Extract scores
                    for competitor in competitors:
                        team_abbr = competitor.get('team', {}).get('abbreviation', '')
                        score = int(competitor.get('score', 0))
                        scores[team_abbr] = score
                    
                    # Check for red zone information
                    situation = competition.get('situation', {})
                    if situation:
                        is_red_zone = situation.get('isRedZone', False)
                        possession_team = situation.get('possession', '')
                        
                        if is_red_zone and possession_team:
                            # Map team ID to abbreviation if needed
                            team_abbr = possession_team
                            
                            # If possession_team looks like an ID (numeric), try to map it
                            if possession_team.isdigit():
                                for competitor in competitors:
                                    team_info = competitor.get('team', {})
                                    if team_info.get('id') == possession_team:
                                        team_abbr = team_info.get('abbreviation', possession_team)
                                        break
                            
                            red_zone_info = {
                                'team': team_abbr,
                                'active': True,
                                'yard_line': situation.get('yardLine', 0)
                            }
                        else:
                            red_zone_info = {'active': False}
                    else:
                        red_zone_info = {'active': False}
                    
                    return {
                        'scores': scores,
                        'status': status,
                        'red_zone': red_zone_info,
                        'game_id': game_id
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting game data for {game_id}: {e}")
            return None
    
    async def detect_score_changes(self, game_config: Dict[str, Any], 
                                 new_game_data: Dict[str, Any]) -> None:
        """Detect and celebrate score changes"""
        game_id = game_config['game']['id']
        monitored_teams = game_config['monitored_teams']
        new_scores = new_game_data['scores']
        
        # Get last known scores
        last_scores = self.game_scores.get(game_id, {})
        
        for team in monitored_teams:
            if team in new_scores and team in last_scores:
                old_score = last_scores[team]
                new_score = new_scores[team]
                
                if new_score > old_score:
                    score_diff = new_score - old_score
                    opponent = [t for t in [game_config['game']['home_abbr'], 
                                          game_config['game']['away_abbr']] if t != team][0]
                    opponent_score = new_scores.get(opponent, 0)
                    
                    print(f"\n🎉 {team} SCORED! +{score_diff} points")
                    print(f"📊 Score: {team} {new_score} - {opponent} {opponent_score}")
                    
                    # Get team display name
                    team_name = self.get_team_display_name(team, game_config['game'])
                    
                    # Trigger appropriate celebration
                    await self.celebrate_score(team, team_name, score_diff, new_game_data)
        
        # Update stored scores
        self.game_scores[game_id] = new_scores.copy()
    
    async def celebrate_score(self, team_abbr: str, team_name: str, 
                            score_diff: int, game_data: Dict[str, Any]) -> None:
        """Trigger appropriate celebration based on score type"""
        # Set team colors for celebration
        await self.set_team_colors_for_celebration(team_abbr)
        
        if score_diff == 6:
            print(f"🏈 {team_abbr} TOUCHDOWN detected!")
            await self.lights_controller.celebrate_touchdown(team_name)
        elif score_diff == 3:
            print(f"🥅 {team_abbr} FIELD GOAL detected!")
            await self.lights_controller.celebrate_field_goal(team_name)
        elif score_diff == 1:
            print(f"✅ {team_abbr} EXTRA POINT detected!")
            await self.lights_controller.celebrate_extra_point(team_name)
        elif score_diff == 2:
            # For 2-point changes, could be 2-point conversion or safety
            # Default to 2-point conversion for now
            print(f"💪 {team_abbr} 2-POINT CONVERSION detected!")
            await self.lights_controller.celebrate_two_point(team_name)
        else:
            print(f"🎯 {team_abbr} scored {score_diff} points!")
            await self.lights_controller.celebrate_big_play(team_name, f"{score_diff}-POINT SCORE")
    
    async def check_red_zone_status(self, game_config: Dict[str, Any], 
                                  game_data: Dict[str, Any]) -> None:
        """Check for red zone changes and manage ambient lighting"""
        game_id = game_config['game']['id']
        monitored_teams = game_config['monitored_teams']
        red_zone_info = game_data['red_zone']
        
        # Get last known red zone status
        last_red_zone = self.red_zone_status.get(game_id, {})
        current_active = red_zone_info.get('active', False)
        current_team = red_zone_info.get('team', '')

        print(f"[DEBUG] Red zone poll: current_active={current_active}, current_team={current_team}, last_red_zone={last_red_zone}, monitored_teams={monitored_teams}")
        # Check if red zone status changed
        if current_active and current_team in monitored_teams:
            # Team is in red zone
            if not last_red_zone.get('active') or last_red_zone.get('team') != current_team:
                # Red zone started or team changed
                print(f"\n🎯 RED ZONE: {current_team} is in the red zone!")

                # Stop any existing red zone ambient
                if self.lights_controller.red_zone_active:
                    await self.lights_controller.stop_red_zone_ambient()
                else:
                    print("[DEBUG] Not calling stop_red_zone_ambient: already inactive (red zone start logic)")

                # Set team colors and start red zone ambient lighting
                await self.set_team_colors_for_celebration(current_team)
                team_name = self.get_team_display_name(current_team, game_config['game'])
                await self.lights_controller.start_red_zone_ambient(team_name)

        # Only call red zone end logic if last_red_zone was active, current is not, and last team was a monitored team
        elif last_red_zone.get('active') and not current_active and last_red_zone.get('team') in monitored_teams and last_red_zone.get('team'):
            last_team = last_red_zone.get('team', 'Team')
            print(f"\n🚫 RED ZONE ENDED: {last_team} left the red zone")

            # Stop red zone ambient lighting
            if self.lights_controller.red_zone_active:
                await self.lights_controller.stop_red_zone_ambient()
            else:
                print("[DEBUG] Not calling stop_red_zone_ambient: already inactive (red zone end logic)")
        else:
            print(f"[DEBUG] No red zone transition: last_active={last_red_zone.get('active')}, current_active={current_active}, last_team={last_red_zone.get('team')}, monitored_teams={monitored_teams}")
        
        # Update stored red zone status
        self.red_zone_status[game_id] = red_zone_info.copy()
    
    async def check_for_other_events(self, game_config: Dict[str, Any]) -> None:
        """Check for turnovers, sacks, and other events"""
        # This would require more detailed play-by-play data
        # For now, this is a placeholder for future implementation
        pass
    
    def get_team_display_name(self, team_abbr: str, game: Dict[str, Any]) -> str:
        """Get team display name from abbreviation"""
        if team_abbr == game['home_abbr']:
            return game['home_name']
        elif team_abbr == game['away_abbr']:
            return game['away_name']
        return team_abbr  # Fallback to abbreviation
    
    async def set_team_colors_for_celebration(self, team_abbr: str) -> None:
        """Set team colors in the lights controller"""
        # Import team colors
        from config.team_colors import NFL_TEAM_COLORS
        
        if team_abbr in NFL_TEAM_COLORS:
            primary, secondary = NFL_TEAM_COLORS[team_abbr]
            self.lights_controller.set_team_colors(team_abbr, primary, secondary)
    
    async def process_game_update(self, game_config: Dict[str, Any]) -> None:
        """Process a single game update - main monitoring logic"""
        game_id = game_config['game']['id']
        
        # Get current game data
        game_data = await self.get_current_game_data(game_id)
        if not game_data:
            return
        
        # Check for score changes
        await self.detect_score_changes(game_config, game_data)
        
        # Check red zone status
        await self.check_red_zone_status(game_config, game_data)
        
        # Check for other events (turnovers, sacks, etc.)
        await self.check_for_other_events(game_config)
        
        # Display current status
        await self.display_game_status(game_config, game_data)
    
    async def display_game_status(self, game_config: Dict[str, Any], 
                                game_data: Dict[str, Any]) -> None:
        """Display current game status"""
        game = game_config['game']
        scores = game_data['scores']
        status = game_data['status']
        red_zone = game_data['red_zone']
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Build score display
        score_parts = []
        for team in game_config['monitored_teams']:
            if team in scores:
                score_parts.append(f"{team} {scores[team]}")
        score_display = " - ".join(score_parts)
        
        # Add red zone info if active
        red_zone_display = ""
        if red_zone.get('active'):
            rz_team = red_zone.get('team', 'Unknown')
            rz_yards = red_zone.get('yard_line', 0)
            red_zone_display = f" | 🎯 {rz_team} RED ZONE ({rz_yards} yd)"
        
        print(f"[{current_time}] 📊 {game['away_name']} @ {game['home_name']}: {score_display} | {status}{red_zone_display}")
        
        # Check if game is finished
        if 'final' in status.lower():
            print(f"🏁 Game finished: {game['away_name']} @ {game['home_name']}")