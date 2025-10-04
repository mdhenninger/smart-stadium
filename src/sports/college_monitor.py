"""
College Football Sports Monitor for Smart Stadium
Handles college football game monitoring and event detection with multi-game selection
"""

import asyncio
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_sport_monitor import BaseSportMonitor
from devices.smart_lights import SmartStadiumLights

class CollegeFootballMonitor(BaseSportMonitor):
    """
    College Football-specific sports monitor
    Handles game tracking, score detection, event celebrations, and multi-game selection
    """
    
    def __init__(self, lights_controller: SmartStadiumLights):
        super().__init__("College Football", lights_controller)
        
        # College Football API endpoints
        self.apis = {
            'espn_college': 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
            'espn_fbs': 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80',  # FBS only
            'espn_all': f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={datetime.now().strftime("%Y%m%d")}',  # All games today
        }
        
        # College-specific tracking
        self.monitored_games = []       # List of games to monitor
        self.monitored_teams = {}       # Dict of team names and which games they're in
        self.red_zone_status = {}       # Track red zone status per game
        self.active_red_zone_team = None # Current team with red zone lighting
        self.last_play_ids = {}         # Track last play ID per game for play detection
        
    async def get_available_games(self) -> List[Dict[str, Any]]:
        """Get all college football games today (in progress, upcoming, or recently finished)"""
        print("🔍 Searching for college football games today...")
        
        try:
            # Try the date-specific API first to get all games
            response = requests.get(self.apis['espn_all'], timeout=15)
            response.raise_for_status()
            data = response.json()
            
            games = []
            events = data.get('events', [])
            
            for event in events:
                try:
                    competition = event.get('competitions', [{}])[0]
                    competitors = competition.get('competitors', [])
                    
                    if len(competitors) >= 2:
                        # Get team information
                        home_team = competitors[0].get('team', {})
                        away_team = competitors[1].get('team', {})
                        
                        home_name = home_team.get('displayName', 'Unknown')
                        away_name = away_team.get('displayName', 'Unknown')
                        home_abbr = home_team.get('abbreviation', home_name[:4].upper())
                        away_abbr = away_team.get('abbreviation', away_name[:4].upper())
                        home_id = home_team.get('id', 'unknown')
                        away_id = away_team.get('id', 'unknown')
                        
                        # Get scores
                        home_score = int(competitors[0].get('score', 0))
                        away_score = int(competitors[1].get('score', 0))
                        
                        # Get game status
                        status = event.get('status', {})
                        status_type = status.get('type', {}).get('name', 'Unknown')
                        status_detail = status.get('type', {}).get('detail', '')
                        
                        # Get game time
                        game_date = event.get('date', '')
                        
                        # Format status for display and skip final games
                        if 'final' in status_type.lower():
                            # Skip final games - no more scoring to celebrate
                            continue
                        elif ('progress' in status_type.lower() or 'in' in status_type.lower() or 
                              'halftime' in status_type.lower()):
                            # Live games including halftime
                            display_status = f"🔴 LIVE - {status_detail}"
                        elif 'scheduled' in status_type.lower() or 'pre' in status_type.lower():
                            # Parse game time for upcoming games
                            try:
                                game_time = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                                local_time = game_time.strftime('%I:%M %p')
                                display_status = f"⏰ {local_time}"
                            except:
                                display_status = "⏰ Upcoming"
                        else:
                            display_status = f"📊 {status_type}"
                        
                        game_info = {
                            'id': event.get('id'),
                            'home_team': home_name,
                            'away_team': away_name,
                            'home_abbr': home_abbr,
                            'away_abbr': away_abbr,
                            'home_id': home_id,
                            'away_id': away_id,
                            'home_score': home_score,
                            'away_score': away_score,
                            'status': display_status,
                            'status_type': status_type.lower(),
                            'is_live': 'progress' in status_type.lower() or 'in' in status_type.lower()
                        }
                        
                        games.append(game_info)
                        
                except Exception as e:
                    print(f"⚠️  Error parsing game: {e}")
                    continue
            
            # Sort games: live first, then upcoming by time
            def sort_key(game):
                if game['is_live']:
                    return (0, game['home_team'])  # Live games first
                else:
                    return (1, game['home_team'])  # Then upcoming/scheduled
            
            games.sort(key=sort_key)
            
            print(f"✅ Found {len(games)} college football games")
            return games
            
        except Exception as e:
            print(f"❌ Error fetching college games: {e}")
            return []
    
    def select_games_and_teams(self, available_games: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Interactive selection of games and teams to monitor
        Returns dict mapping game_id to list of team names to monitor
        """
        if not available_games:
            print("❌ No games available to monitor")
            return {}
        
        print("\n🏈 COLLEGE FOOTBALL GAMES AVAILABLE:")
        print("=" * 60)
        
        # Display games with numbers for selection
        for i, game in enumerate(available_games, 1):
            status_emoji = "🔴" if game['is_live'] else "⏰"
            print(f"{i:2d}. {status_emoji} {game['away_team']} @ {game['home_team']}")
            print(f"     Score: {game['away_abbr']} {game['away_score']} - {game['home_score']} {game['home_abbr']}")
            print(f"     Status: {game['status']}")
            print()
        
        # Get game selections
        selected_games = {}
        
        print("📋 GAME SELECTION:")
        while True:
            try:
                selection = input(f"\nEnter game numbers to monitor (1-{len(available_games)}, comma-separated, or 'done'): ").strip()
                
                if selection.lower() in ['done', 'quit', 'exit', '']:
                    break
                
                # Parse selections
                game_numbers = [int(x.strip()) for x in selection.split(',') if x.strip().isdigit()]
                valid_numbers = [n for n in game_numbers if 1 <= n <= len(available_games)]
                
                if not valid_numbers:
                    print("❌ No valid game numbers entered")
                    continue
                
                # For each selected game, ask which teams to monitor
                for game_num in valid_numbers:
                    game = available_games[game_num - 1]
                    game_id = game['id']
                    
                    print(f"\n🎯 Game {game_num}: {game['away_team']} @ {game['home_team']}")
                    print("   Which teams should we monitor for celebrations?")
                    print(f"   1. {game['away_team']} (away)")
                    print(f"   2. {game['home_team']} (home)")
                    print("   3. Both teams")
                    
                    while True:
                        team_choice = input("   Choice (1/2/3): ").strip()
                        
                        if team_choice == '1':
                            selected_games[game_id] = [game['away_team']]
                            break
                        elif team_choice == '2':
                            selected_games[game_id] = [game['home_team']]
                            break
                        elif team_choice == '3':
                            selected_games[game_id] = [game['away_team'], game['home_team']]
                            break
                        else:
                            print("   ❌ Please enter 1, 2, or 3")
                
                break
                
            except ValueError:
                print("❌ Please enter valid numbers")
            except KeyboardInterrupt:
                print("\n👋 Selection cancelled")
                return {}
        
        # Summary
        if selected_games:
            print(f"\n✅ MONITORING CONFIGURATION:")
            print("=" * 40)
            for game_id, teams in selected_games.items():
                game = next(g for g in available_games if g['id'] == game_id)
                teams_str = " & ".join(teams)
                print(f"🎯 {game['away_abbr']} @ {game['home_abbr']} - {teams_str}")
            print()
        
        return selected_games
    
    async def check_red_zone_status(self, monitor_configs: Dict[str, List[str]]):
        """Check red zone status for monitored games and manage ambient lighting"""
        try:
            current_red_zone_team = None
            
            for game_id, monitored_teams in monitor_configs.items():
                try:
                    # Get game data
                    game_url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
                    response = requests.get(game_url, timeout=10)
                    
                    if response.status_code == 200:
                        game_data = response.json()
                        
                        # Check if game has current situation data
                        current_situation = game_data.get('gameInfo', {}).get('situation')
                        if current_situation:
                            situation = current_situation
                            if isinstance(situation, dict):
                                is_red_zone = situation.get('isRedZone', False)
                                possession_id = situation.get('possession')
                                
                                if is_red_zone and possession_id:
                                    # Find which team has possession
                                    competitors = game_data.get('header', {}).get('competitions', [{}])[0].get('competitors', [])
                                    possessing_team = None
                                    
                                    for competitor in competitors:
                                        if competitor.get('id') == possession_id:
                                            possessing_team = competitor.get('team', {}).get('displayName')
                                            break
                                    
                                    if possessing_team and possessing_team in monitored_teams:
                                        # Team we're monitoring is in red zone!
                                        if not current_red_zone_team:  # First detected gets priority
                                            current_red_zone_team = possessing_team
                                            
                                            # Check if this is a new red zone situation
                                            if self.active_red_zone_team != possessing_team:
                                                print(f"🎯 {possessing_team.upper()} ENTERED RED ZONE!")
                                                
                                                # Stop any existing red zone lighting
                                                await self.lights_controller.stop_red_zone_ambient()
                                                
                                                # Start new red zone lighting
                                                await self.lights_controller.start_red_zone_ambient(possessing_team)
                                                self.active_red_zone_team = possessing_team
                
                except Exception as e:
                    print(f"⚠️  Error checking red zone for game {game_id}: {e}")
                    continue
            
            # If no team is in red zone but we had active lighting, stop it
            if not current_red_zone_team and self.active_red_zone_team:
                print(f"🟢 {self.active_red_zone_team.upper()} LEFT RED ZONE")
                await self.lights_controller.stop_red_zone_ambient()
                self.active_red_zone_team = None
        
        except Exception as e:
            print(f"⚠️  Error in red zone check: {e}")
    
    async def get_game_updates(self, game_ids: List[str]) -> List[Dict[str, Any]]:
        """Get current game data for specified games"""
        if not game_ids:
            return []
        
        try:
            # For college, we use the general scoreboard with multiple game IDs
            # or fetch individual games
            games_data = []
            
            for game_id in game_ids:
                try:
                    game_url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
                    response = requests.get(game_url, timeout=10)
                    
                    if response.status_code == 200:
                        game_data = response.json()
                        
                        # Extract game info
                        header = game_data.get('header', {})
                        competition = header.get('competitions', [{}])[0]
                        competitors = competition.get('competitors', [])
                        
                        if len(competitors) >= 2:
                            game_info = {
                                'id': game_id,
                                'home_team': competitors[0].get('team', {}).get('displayName', ''),
                                'away_team': competitors[1].get('team', {}).get('displayName', ''),
                                'home_score': int(competitors[0].get('score', 0)),
                                'away_score': int(competitors[1].get('score', 0)),
                                'status': header.get('status', {}).get('type', {}).get('name', ''),
                                'period': header.get('status', {}).get('period', 1),
                                'clock': header.get('status', {}).get('displayClock', ''),
                                'last_play': None  # Will add play tracking if needed
                            }
                            games_data.append(game_info)
                
                except Exception as e:
                    print(f"⚠️  Error fetching game {game_id}: {e}")
                    continue
            
            return games_data
            
        except Exception as e:
            print(f"❌ Error getting game updates: {e}")
            return []
    
    async def monitor_games(self, game_configs: Dict[str, List[str]]):
        """
        Monitor selected college football games for score changes and celebrations
        """
        if not game_configs:
            print("❌ No games configured for monitoring")
            return
        
        print(f"\n🎯 Starting college football monitoring for {len(game_configs)} games...")
        self.monitoring = True
        
        # Initialize previous scores
        previous_scores = {}
        for game_id in game_configs.keys():
            previous_scores[game_id] = {'home': 0, 'away': 0}
        
        try:
            while self.monitoring:
                # Check red zone status
                await self.check_red_zone_status(game_configs)
                
                # Get current game data
                game_ids = list(game_configs.keys())
                current_games = await self.get_game_updates(game_ids)
                
                # Check for score changes
                for game in current_games:
                    game_id = game['id']
                    monitored_teams = game_configs.get(game_id, [])
                    
                    if game_id in previous_scores:
                        prev_home = previous_scores[game_id]['home']
                        prev_away = previous_scores[game_id]['away']
                        curr_home = game['home_score']
                        curr_away = game['away_score']
                        
                        # Check for home team scoring
                        if curr_home > prev_home and game['home_team'] in monitored_teams:
                            score_diff = curr_home - prev_home
                            await self._handle_scoring_event(game['home_team'], score_diff, game)
                        
                        # Check for away team scoring
                        if curr_away > prev_away and game['away_team'] in monitored_teams:
                            score_diff = curr_away - prev_away
                            await self._handle_scoring_event(game['away_team'], score_diff, game)
                        
                        # Update previous scores
                        previous_scores[game_id] = {'home': curr_home, 'away': curr_away}
                
                # Wait before next check
                await asyncio.sleep(15)  # Check every 15 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error in monitoring: {e}")
        finally:
            self.monitoring = False
            # Stop any active red zone lighting
            if self.active_red_zone_team:
                await self.lights_controller.stop_red_zone_ambient()
                self.active_red_zone_team = None
    
    async def _handle_scoring_event(self, team_name: str, score_diff: int, game_info: Dict[str, Any]):
        """Handle different types of scoring events"""
        print(f"\n🎉 {team_name.upper()} SCORED! (+{score_diff} points)")
        
        # Determine celebration type based on score difference
        if score_diff >= 6:
            # Touchdown (6+ points)
            await self.lights_controller.celebrate_touchdown(team_name)
        elif score_diff == 3:
            # Field goal
            await self.lights_controller.celebrate_field_goal(team_name)
        elif score_diff == 2:
            # Safety
            await self.lights_controller.celebrate_safety(team_name)
        elif score_diff == 1:
            # Extra point or other 1-point score
            await self.lights_controller.celebrate_extra_point(team_name)
        else:
            # Generic scoring celebration
            await self.lights_controller.celebrate_score(team_name)
    
    async def start_monitoring(self, selected_teams: Optional[List[str]] = None):
        """
        Start monitoring college football games
        If no teams specified, will prompt for game and team selection
        """
        print("🏈 Starting College Football Monitoring...")
        
        # Get available games
        available_games = await self.get_available_games()
        
        if not available_games:
            print("❌ No college football games found for today")
            return
        
        # If no specific teams provided, do interactive selection
        if not selected_teams:
            game_configs = self.select_games_and_teams(available_games)
        else:
            # Auto-configure based on selected teams
            game_configs = {}
            for game in available_games:
                teams_in_game = []
                if game['home_team'] in selected_teams:
                    teams_in_game.append(game['home_team'])
                if game['away_team'] in selected_teams:
                    teams_in_game.append(game['away_team'])
                
                if teams_in_game:
                    game_configs[game['id']] = teams_in_game
        
        if not game_configs:
            print("❌ No teams selected for monitoring")
            return
        
        # Start monitoring
        await self.monitor_games(game_configs)
    
    async def stop_monitoring(self):
        """Stop college football game monitoring"""
        print("🛑 Stopping college football monitoring...")
        self.monitoring = False
        
        # Stop any active red zone lighting
        if self.active_red_zone_team:
            await self.lights_controller.stop_red_zone_ambient()
            self.active_red_zone_team = None