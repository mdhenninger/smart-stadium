"""
College Football Game Monitor - Multi-Game Selection System
Detects live/upcoming college games and allows selection of games and teams to monitor
"""

import asyncio
import requests
import json
import time
import os
from datetime import datetime, timedelta
from college_celebrations import CollegeCelebrationController, COLLEGE_TEAM_COLORS

class CollegeGameMonitor:
    def __init__(self, light_ips):
        self.celebration_controller = CollegeCelebrationController(light_ips)
        self.monitored_games = []  # List of games to monitor
        self.monitored_teams = {}  # Dict of team names and which games they're in
        self.monitoring = False
        
        # Load team colors into celebration controller
        for team, (primary, secondary) in COLLEGE_TEAM_COLORS.items():
            self.celebration_controller.set_team_colors(team, primary, secondary)
        
        # Red zone tracking
        self.red_zone_status = {}  # Track red zone status per game
        self.active_red_zone_team = None  # Current team with red zone lighting
        
        # API endpoints for college football
        self.apis = {
            'espn_college': 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
            'espn_fbs': 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80',  # FBS only
            'espn_all': f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={datetime.now().strftime("%Y%m%d")}',  # All games today
        }
    
    async def get_available_games(self):
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
                            'status': status_type,
                            'status_detail': status_detail,
                            'display_status': display_status,
                            'date': game_date,
                            'raw_event': event
                        }
                        
                        games.append(game_info)
                        
                except Exception as e:
                    print(f"⚠️ Error parsing game: {e}")
                    continue
            
            # Sort games: Live first, then upcoming (final games already filtered out)
            def sort_key(game):
                status = game['status'].lower()
                if 'progress' in status or 'in' in status or 'halftime' in status:
                    return (0, game['home_team'])  # Live games first (including halftime)
                elif 'scheduled' in status or 'pre' in status:
                    return (1, game['date'])       # Upcoming games second
                else:
                    return (2, game['home_team'])  # Other statuses last
            
            games.sort(key=sort_key)
            
            print(f"📊 Found {len(games)} active college football games today (final games excluded)")
            return games
            
        except Exception as e:
            print(f"❌ Error getting games: {e}")
            return []
    
    async def check_red_zone_status(self, monitor_configs):
        """Check red zone status for monitored games and manage ambient lighting"""
        try:
            current_red_zone_team = None
            
            for config in monitor_configs:
                game_id = config['game_id']
                url = f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}'
                
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if there's situation data
                        if 'header' in data and 'competitions' in data['header']:
                            competition = data['header']['competitions'][0]
                            
                            if 'situation' in competition:
                                situation = competition['situation']
                                is_red_zone = situation.get('isRedZone', False)
                                possession_id = situation.get('possession')
                                
                                if is_red_zone and possession_id:
                                    # Find which team has possession
                                    possessing_team = None
                                    if str(possession_id) == str(config['home_team_id']):
                                        possessing_team = config['home_team']
                                    elif str(possession_id) == str(config['away_team_id']):
                                        possessing_team = config['away_team']
                                    
                                    if possessing_team and possessing_team in config['monitored_teams']:
                                        # Team we're monitoring is in red zone!
                                        if not current_red_zone_team:  # First detected gets priority
                                            current_red_zone_team = possessing_team
                                            
                                            # Check if this is a new red zone situation
                                            if self.active_red_zone_team != possessing_team:
                                                print(f"🎯 {possessing_team.upper()} ENTERED RED ZONE!")
                                                
                                                # Stop any existing red zone lighting
                                                await self.celebration_controller.stop_red_zone_ambient()
                                                
                                                # Start new red zone lighting
                                                await self.celebration_controller.start_red_zone_ambient(possessing_team)
                                                self.active_red_zone_team = possessing_team
                                        
                except Exception as e:
                    print(f"⚠️ Error checking red zone for game {game_id}: {e}")
                    continue
            
            # If no team is in red zone anymore, stop ambient lighting
            if not current_red_zone_team and self.active_red_zone_team:
                print(f"🎯 {self.active_red_zone_team.upper()} EXITED RED ZONE")
                await self.celebration_controller.stop_red_zone_ambient()
                self.active_red_zone_team = None
                
        except Exception as e:
            print(f"⚠️ Error in red zone check: {e}")
    
    async def display_game_selection_menu(self, games):
        """Display interactive menu for game selection"""
        if not games:
            print("😴 No college football games found today")
            return []
        
        print(f"\n🏈 COLLEGE FOOTBALL GAMES TODAY ({len(games)} games)")
        print("=" * 80)
        
        live_games = []
        upcoming_games = []
        
        for i, game in enumerate(games, 1):
            status_lower = game['status'].lower()
            game_line = f"{i:2d}. {game['away_team']:<25} @ {game['home_team']:<25}"
            score_line = f"({game['away_score']:2d}-{game['home_score']:2d}) {game['display_status']}"
            
            if 'progress' in status_lower or 'in' in status_lower or 'halftime' in status_lower:
                live_games.append((i, game_line, score_line, game))
            elif 'scheduled' in status_lower or 'pre' in status_lower:
                upcoming_games.append((i, game_line, score_line, game))
            # Final games are already filtered out, so no else clause needed
        
        # Display live games first
        if live_games:
            print("\n🔴 LIVE GAMES:")
            for i, game_line, score_line, _ in live_games:
                print(f"{game_line} {score_line}")
        
        if upcoming_games:
            print("\n⏰ UPCOMING GAMES:")
            for i, game_line, score_line, _ in upcoming_games:
                print(f"{game_line} {score_line}")
        
        # Final games are filtered out and not shown in selection menu
        
        return games
    
    async def select_games_to_monitor(self, games):
        """Interactive selection of games and teams to monitor"""
        if not games:
            return []
        
        selected_monitors = []
        
        while True:
            print(f"\n🎯 GAME SELECTION MENU")
            print("=" * 40)
            print("Commands:")
            print("  • Enter game number (e.g., '3') to select a game")
            print("  • Enter 'done' when finished selecting")
            print("  • Enter 'refresh' to update game list")
            print("  • Enter 'all-live' to monitor all live games")
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 'done':
                break
            elif choice == 'refresh':
                print("🔄 Refreshing game list...")
                games = await self.get_available_games()
                games = await self.display_game_selection_menu(games)
                continue
            elif choice == 'all-live':
                # Add all live games
                for i, game in enumerate(games, 1):
                    if 'progress' in game['status'].lower() or 'in' in game['status'].lower():
                        # Monitor both teams for live games
                        monitor_config = {
                            'game': game,
                            'game_id': game['id'],
                            'monitor_home': True,
                            'monitor_away': True,
                            'home_team': game['home_team'],
                            'away_team': game['away_team'],
                            'home_team_id': game['home_id'],
                            'away_team_id': game['away_id'],
                            'monitored_teams': [game['home_team'], game['away_team']]
                        }
                        selected_monitors.append(monitor_config)
                        print(f"✅ Added {game['away_team']} @ {game['home_team']} (both teams)")
                continue
            
            try:
                game_num = int(choice)
                if 1 <= game_num <= len(games):
                    selected_game = games[game_num - 1]
                    
                    print(f"\n🏈 Selected: {selected_game['away_team']} @ {selected_game['home_team']}")
                    print("Which team(s) do you want to monitor?")
                    print(f"1. {selected_game['home_team']} only")
                    print(f"2. {selected_game['away_team']} only")
                    print("3. Both teams")
                    
                    team_choice = input("Team choice (1-3): ").strip()
                    
                    monitor_home = False
                    monitor_away = False
                    
                    if team_choice == '1':
                        monitor_home = True
                        print(f"✅ Will monitor {selected_game['home_team']} scoring")
                    elif team_choice == '2':
                        monitor_away = True
                        print(f"✅ Will monitor {selected_game['away_team']} scoring")
                    elif team_choice == '3':
                        monitor_home = True
                        monitor_away = True
                        print(f"✅ Will monitor both teams scoring")
                    else:
                        print("❌ Invalid team choice")
                        continue
                    
                    # Build monitored teams list
                    monitored_teams = []
                    if monitor_home:
                        monitored_teams.append(selected_game['home_team'])
                    if monitor_away:
                        monitored_teams.append(selected_game['away_team'])
                    
                    monitor_config = {
                        'game': selected_game,
                        'game_id': selected_game['id'],
                        'monitor_home': monitor_home,
                        'monitor_away': monitor_away,
                        'home_team': selected_game['home_team'],
                        'away_team': selected_game['away_team'],
                        'home_team_id': selected_game['home_id'],
                        'away_team_id': selected_game['away_id'],
                        'monitored_teams': monitored_teams,
                        'last_home_score': selected_game['home_score'],
                        'last_away_score': selected_game['away_score']
                    }
                    
                    selected_monitors.append(monitor_config)
                    
                else:
                    print(f"❌ Invalid game number. Please enter 1-{len(games)}")
                    
            except ValueError:
                print("❌ Invalid input. Enter a game number, 'done', 'refresh', or 'all-live'")
        
        return selected_monitors
    
    async def get_current_scores(self, monitor_configs):
        """Get current scores for all monitored games with smart rate limiting"""
        try:
            # Use shorter timeout for faster polling
            response = requests.get(self.apis['espn_all'], timeout=8)  
            
            # Check for rate limiting
            if response.status_code == 429:  # Too Many Requests
                print("🚨 RATE LIMITED! Auto-adjusting speed...")
                self.api_error_count += 1
                old_interval = self.current_interval
                self.current_interval = min(30, self.current_interval * 2.0)  # More aggressive backoff
                print(f"   Slowing from {old_interval:.1f}s to {self.current_interval:.1f}s")
                await asyncio.sleep(5)  # Extra pause when rate limited
                return monitor_configs
            elif response.status_code == 503:  # Service Unavailable
                print("⚠️ ESPN API overloaded, backing off...")
                self.api_error_count += 1
                self.current_interval = min(30, self.current_interval * 1.5)
                return monitor_configs
            elif response.status_code >= 500:  # Server errors
                print("⚠️ ESPN server error, slowing down...")
                self.api_error_count += 1
                self.current_interval = min(20, self.current_interval * 1.3)
                return monitor_configs
                
            response.raise_for_status()
            
            # Success! Reset error count and potentially speed up
            if self.api_error_count > 0:
                self.api_error_count = max(0, self.api_error_count - 1)
                if self.api_error_count == 0 and self.current_interval > 10:
                    self.current_interval = max(10, self.current_interval * 0.9)
                    print(f"✅ API stable, speeding up to {self.current_interval:.1f}s")
            
            data = response.json()
            
            events = data.get('events', [])
            updated_configs = []
            
            for config in monitor_configs:
                game_id = config['game']['id']
                
                # Find the current game data
                for event in events:
                    if event.get('id') == game_id:
                        competition = event.get('competitions', [{}])[0]
                        competitors = competition.get('competitors', [])
                        
                        if len(competitors) >= 2:
                            home_score = int(competitors[0].get('score', 0))
                            away_score = int(competitors[1].get('score', 0))
                            
                            # Update the config with current scores
                            new_config = config.copy()
                            new_config['current_home_score'] = home_score
                            new_config['current_away_score'] = away_score
                            
                            # Update game status
                            status = event.get('status', {})
                            new_config['game']['status'] = status.get('type', {}).get('name', 'Unknown')
                            new_config['game']['status_detail'] = status.get('type', {}).get('detail', '')
                            
                            updated_configs.append(new_config)
                            break
                else:
                    # Game not found, keep original config
                    updated_configs.append(config)
            
            return updated_configs
            
        except Exception as e:
            print(f"❌ Error getting current scores: {e}")
            return monitor_configs
    
    async def detect_scoring_changes(self, monitor_configs):
        """Detect scoring changes and trigger celebrations"""
        for config in monitor_configs:
            game = config['game']
            
            current_home = config.get('current_home_score', config.get('last_home_score', 0))
            current_away = config.get('current_away_score', config.get('last_away_score', 0))
            last_home = config.get('last_home_score', 0)
            last_away = config.get('last_away_score', 0)
            
            # Check home team scoring
            if config['monitor_home'] and current_home > last_home:
                score_diff = current_home - last_home
                team_name = config['home_team']
                await self.celebrate_team_score(team_name, score_diff, current_home, current_away, config['away_team'])
            
            # Check away team scoring  
            if config['monitor_away'] and current_away > last_away:
                score_diff = current_away - last_away
                team_name = config['away_team']
                await self.celebrate_team_score(team_name, score_diff, current_away, current_home, config['home_team'])
            
            # Check for game end victories
            game_status = game.get('status', '').lower()
            if 'final' in game_status:
                if config['monitor_home'] and current_home > current_away and not config.get('home_victory_celebrated'):
                    print(f"\n🏆 {config['home_team']} WINS! Final: {current_home}-{current_away}")
                    await self.celebration_controller.celebrate_victory(config['home_team'])
                    config['home_victory_celebrated'] = True
                elif config['monitor_away'] and current_away > current_home and not config.get('away_victory_celebrated'):
                    print(f"\n🏆 {config['away_team']} WINS! Final: {current_away}-{current_home}")
                    await self.celebration_controller.celebrate_victory(config['away_team'])
                    config['away_victory_celebrated'] = True
            
            # Update last known scores
            config['last_home_score'] = current_home
            config['last_away_score'] = current_away
    
    async def celebrate_team_score(self, team_name, points, team_score, opponent_score, opponent_name):
        """Celebrate a team's scoring with appropriate celebration type"""
        print(f"\n🎉 {team_name.upper()} SCORED! +{points} points")
        print(f"📊 Score: {team_name} {team_score} - {opponent_name} {opponent_score}")
        
        # Determine celebration type based on points
        if points == 6:
            print("🏈 TOUCHDOWN detected!")
            await self.celebration_controller.celebrate_touchdown(team_name)
        elif points == 7:
            print("🏈 TOUCHDOWN + EXTRA POINT detected!")
            await self.celebration_controller.celebrate_touchdown(team_name)
        elif points == 8:
            print("🏈 TOUCHDOWN + 2-POINT CONVERSION detected!")
            await self.celebration_controller.celebrate_touchdown(team_name)
        elif points == 3:
            print("🥅 FIELD GOAL detected!")
            await self.celebration_controller.celebrate_field_goal(team_name)
        elif points == 1:
            print("✅ EXTRA POINT or SAFETY detected!")
            await self.celebration_controller.celebrate_extra_point(team_name)
        elif points == 2:
            print("💪 2-POINT CONVERSION or SAFETY detected!")
            await self.celebration_controller.celebrate_two_point(team_name)
        else:
            print(f"🎯 UNUSUAL SCORE (+{points}) - Generic celebration!")
            await self.celebration_controller.celebrate_generic_score(team_name, points)
    
    async def monitor_selected_games(self, monitor_configs, check_interval=10):
        """Monitor all selected games for scoring changes"""
        if not monitor_configs:
            print("❌ No games selected to monitor")
            return
        
        self.monitoring = True
        self.api_error_count = 0
        self.current_interval = check_interval
        
        print(f"\n🎯 Starting live monitoring of {len(monitor_configs)} game(s)")
        print(f"⚡ Aggressive polling: Starting at {check_interval} seconds (will adapt if rate limited)")
        
        # Display what we're monitoring
        for config in monitor_configs:
            game = config['game']
            teams_monitored = []
            if config['monitor_home']:
                teams_monitored.append(game['home_team'])
            if config['monitor_away']:
                teams_monitored.append(game['away_team'])
            
            print(f"🏈 {game['away_team']} @ {game['home_team']} - Monitoring: {', '.join(teams_monitored)}")
        
        print("\n🚨 Waiting for scoring changes...")
        print("(Press Ctrl+C to stop monitoring)\n")
        
        try:
            while self.monitoring:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Get current scores for all games
                updated_configs = await self.get_current_scores(monitor_configs)
                
                # Display current status
                print(f"[{current_time}] 📊 Current Scores:")
                for config in updated_configs:
                    game = config['game']
                    home_score = config.get('current_home_score', config.get('last_home_score', 0))
                    away_score = config.get('current_away_score', config.get('last_away_score', 0))
                    status = game.get('status_detail', game.get('status', 'Unknown'))
                    
                    print(f"   {game['away_team']} {away_score} - {game['home_team']} {home_score} | {status}")
                
                # Check for scoring changes
                await self.detect_scoring_changes(updated_configs)
                
                # Check red zone status for ambient lighting
                await self.check_red_zone_status(updated_configs)
                
                # Update monitor configs with new scores
                monitor_configs = updated_configs
                
                # Check if all games are finished
                all_finished = True
                for config in monitor_configs:
                    if 'final' not in config['game'].get('status', '').lower():
                        all_finished = False
                        break
                
                if all_finished:
                    print(f"\n🏁 All monitored games finished!")
                    break
                
                # Wait before next check (adaptive interval)
                current_time_for_interval = datetime.now().strftime("%H:%M:%S")
                if self.current_interval != check_interval:
                    print(f"[{current_time_for_interval}] ⏱️ Adaptive polling: {self.current_interval:.1f}s interval")
                await asyncio.sleep(self.current_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            self.monitoring = False
            print("💡 Setting lights to default...")
            await self.celebration_controller.set_default_lighting()
            print("👋 Monitoring ended. Great games! 🏈")

def load_light_ips():
    """Load light IPs from config file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'wiz_lights_config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('known_ips', [])
    except FileNotFoundError:
        print(f"❌ Config file not found at {config_path}")
        return []
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return []

async def main():
    """Main function to run the college game monitor"""
    print("🏈 College Football Multi-Game Monitor 🏈")
    print("=" * 55)
    
    # Load light IPs from config
    light_ips = load_light_ips()
    
    if not light_ips:
        print("❌ No light IPs found in config file!")
        return
    
    print(f"🎯 Initializing with {len(light_ips)} light(s):")
    for ip in light_ips:
        print(f"   - {ip}")
    
    # Initialize monitor
    monitor = CollegeGameMonitor(light_ips)
    
    # Test light connectivity
    print("\n🧪 Testing light connectivity...")
    if not await monitor.celebration_controller.test_connectivity():
        print("❌ Some lights not responding. Check your network connection.")
        return
    
    # Set initial warm default lighting
    await monitor.celebration_controller.set_default_lighting()
    
    # Get available games
    games = await monitor.get_available_games()
    
    if not games:
        print("\n😴 No college football games found today!")
        print("💡 Setting lights to default...")
        await monitor.celebration_controller.set_default_lighting()
        return
    
    # Display games menu
    games = await monitor.display_game_selection_menu(games)
    
    # Select games to monitor
    monitor_configs = await monitor.select_games_to_monitor(games)
    
    if monitor_configs:
        print(f"\n🎮 Ready to monitor {len(monitor_configs)} game configuration(s)!")
        
        # Start monitoring
        # Ask user for polling speed
        print(f"\n⚡ POLLING SPEED OPTIONS:")
        print("1. 🏃‍♂️ Ultra-Fast (5s) - Maximum speed, may hit rate limits")
        print("2. ⚡ Fast (10s) - Recommended balance")  
        print("3. 🚶‍♂️ Normal (15s) - Conservative, very stable")
        print("4. 🐌 Slow (30s) - Original speed")
        
        try:
            speed_choice = input("Select polling speed (1-4, default=2): ").strip()
            speed_map = {'1': 5, '2': 10, '3': 15, '4': 30}
            check_interval = speed_map.get(speed_choice, 10)
            
            if check_interval == 5:
                print("⚠️ WARNING: 5-second polling is experimental!")
                print("   System will automatically slow down if rate limited.")
                
            print(f"✅ Using {check_interval}-second polling interval")
        except:
            check_interval = 10
            print("✅ Using default 10-second polling interval")
        
        await monitor.monitor_selected_games(monitor_configs, check_interval=check_interval)
    else:
        print("\n😴 No games selected for monitoring.")
        print("💡 Setting lights to default...")
        await monitor.celebration_controller.set_default_lighting()

if __name__ == "__main__":
    asyncio.run(main())