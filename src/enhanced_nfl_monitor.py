"""
Enhanced Buffalo Bills & NFL Multi-Game Monitor
Auto-starts Bills monitoring + allows selection of additional NFL games
"""

import asyncio
import requests
import json
import time
import os
from datetime import datetime, timedelta
from bills_celebrations import BillsCelebrationController

# NFL Team Colors (Official team colors for all 32 teams)
NFL_TEAM_COLORS = {
    'BUF': ((0, 51, 141), (198, 12, 48)),        # Bills - Blue & Red
    'MIA': ((0, 142, 204), (252, 76, 2)),        # Dolphins - Aqua & Orange
    'NE': ((0, 34, 68), (198, 12, 48)),          # Patriots - Navy & Red
    'NYJ': ((18, 87, 64), (255, 255, 255)),      # Jets - Green & White
    'BAL': ((26, 25, 95), (158, 124, 12)),       # Ravens - Purple & Gold
    'CIN': ((251, 79, 20), (0, 0, 0)),           # Bengals - Orange & Black
    'CLE': ((49, 29, 0), (255, 60, 0)),          # Browns - Brown & Orange
    'PIT': ((255, 182, 18), (0, 0, 0)),          # Steelers - Gold & Black
    'HOU': ((3, 32, 47), (167, 25, 48)),         # Texans - Navy & Red
    'IND': ((0, 44, 95), (255, 255, 255)),       # Colts - Blue & White
    'JAX': ((0, 103, 120), (215, 162, 42)),      # Jaguars - Teal & Gold
    'TEN': ((12, 35, 64), (75, 146, 219)),       # Titans - Navy & Light Blue
    'DEN': ((251, 79, 20), (0, 34, 68)),         # Broncos - Orange & Navy
    'KC': ((227, 24, 55), (255, 184, 28)),       # Chiefs - Red & Gold
    'LV': ((165, 172, 175), (0, 0, 0)),          # Raiders - Silver & Black
    'LAC': ((0, 128, 198), (255, 194, 14)),      # Chargers - Blue & Gold
    'DAL': ((0, 34, 68), (134, 147, 151)),       # Cowboys - Navy & Silver
    'NYG': ((1, 35, 82), (163, 13, 45)),         # Giants - Blue & Red
    'PHI': ((0, 76, 84), (165, 172, 175)),       # Eagles - Green & Silver
    'WAS': ((90, 20, 20), (255, 182, 18)),       # Commanders - Burgundy & Gold
    'CHI': ((11, 22, 42), (200, 56, 3)),         # Bears - Navy & Orange
    'DET': ((0, 118, 182), (165, 172, 175)),     # Lions - Blue & Silver
    'GB': ((24, 48, 40), (255, 184, 28)),        # Packers - Green & Gold
    'MIN': ((79, 38, 131), (255, 198, 47)),      # Vikings - Purple & Gold
    'ATL': ((167, 25, 48), (0, 0, 0)),           # Falcons - Red & Black
    'CAR': ((0, 133, 202), (165, 172, 175)),     # Panthers - Blue & Silver
    'NO': ((211, 188, 141), (0, 0, 0)),          # Saints - Gold & Black
    'TB': ((213, 10, 10), (52, 48, 43)),         # Buccaneers - Red & Pewter
    'ARI': ((151, 35, 63), (255, 255, 255)),     # Cardinals - Red & White
    'LAR': ((0, 53, 148), (255, 209, 0)),        # Rams - Blue & Gold
    'SF': ((170, 0, 0), (173, 153, 93)),         # 49ers - Red & Gold
    'SEA': ((0, 34, 68), (105, 190, 40)),        # Seahawks - Navy & Green
}

class EnhancedNFLMonitor:
    def __init__(self, light_ips):
        self.celebration_controller = BillsCelebrationController(light_ips)
        self.bills_team_id = "BUF"
        self.monitored_games = []  # List of games being monitored
        self.game_scores = {}      # Track last known scores for each game
        self.monitoring = False
        self.red_zone_status = {}  # Track red zone status per game
        self.last_play_ids = {}   # Track last play ID per game for play detection
        
        # Load team colors into celebration controller
        for team, (primary, secondary) in NFL_TEAM_COLORS.items():
            self.celebration_controller.set_team_colors(team, primary, secondary)
        
        # API endpoint
        self.api_url = 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
    
    async def get_all_nfl_games_today(self):
        """Get all NFL games for today"""
        print("🔍 Searching for NFL games today...")
        
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = data.get('events', [])
            bills_games = []
            other_games = []
            
            for game in games:
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
                
                game_status = game.get('status', {}).get('type', {}).get('name', 'Unknown')
                game_time = game.get('date', '')
                
                game_info = {
                    'id': game.get('id'),
                    'away_abbr': away_team_abbr,
                    'home_abbr': home_team_abbr,
                    'away_name': away_team_name,
                    'home_name': home_team_name,
                    'away_score': away_score,
                    'home_score': home_score,
                    'status': game_status,
                    'time': game_time,
                    'raw_game': game
                }
                
                # Separate Bills games from others
                if self.bills_team_id in [away_team_abbr, home_team_abbr]:
                    bills_games.append(game_info)
                else:
                    other_games.append(game_info)
            
            return bills_games, other_games
            
        except Exception as e:
            print(f"❌ Error getting NFL games: {e}")
            return [], []
    
    async def select_games_to_monitor(self, bills_games, other_games):
        """Select which games to monitor (Bills auto-selected)"""
        monitor_configs = []
        
        # Auto-add Bills games with both teams monitored
        for game in bills_games:
            bills_team = self.bills_team_id
            opponent = game['away_abbr'] if game['home_abbr'] == self.bills_team_id else game['home_abbr']
            
            config = {
                'game': game,
                'monitored_teams': [bills_team, opponent],  # Monitor both teams
                'primary_team': bills_team  # Bills are always primary
            }
            monitor_configs.append(config)
            print(f"✅ Auto-selected: {game['away_name']} @ {game['home_name']} (Bills game)")
        
        if not other_games:
            return monitor_configs
        
        # Show other games for selection
        print(f"\n🏈 OTHER NFL GAMES TODAY ({len(other_games)} games)")
        print("=" * 60)
        
        # Filter for live and upcoming games
        live_games = [g for g in other_games if 'in_progress' in g['status'].lower() or 'live' in g['status'].lower()]
        upcoming_games = [g for g in other_games if 'scheduled' in g['status'].lower() or 'pre' in g['status'].lower()]
        
        all_selectable = live_games + upcoming_games
        
        if live_games:
            print("🔴 LIVE GAMES:")
            for i, game in enumerate(live_games, 1):
                idx = i
                print(f" {idx:2d}. {game['away_name']} @ {game['home_name']} ({game['away_score']}-{game['home_score']}) - LIVE")
        
        if upcoming_games:
            print("⏰ UPCOMING GAMES:")
            start_idx = len(live_games) + 1
            for i, game in enumerate(upcoming_games, start_idx):
                print(f" {i:2d}. {game['away_name']} @ {game['home_name']} - {game['status']}")
        
        if not all_selectable:
            print("😴 No other games available to monitor")
            return monitor_configs
        
        print(f"\n🎯 ADDITIONAL GAME SELECTION")
        print("=" * 40)
        print("Commands:")
        print("  • Enter game number (e.g., '3') to select a game")
        print("  • Enter 'done' when finished selecting")
        print("  • Enter 'refresh' to update game list")
        
        while True:
            try:
                choice = input("\nYour choice: ").strip().lower()
                
                if choice == 'done':
                    break
                elif choice == 'refresh':
                    # Refresh the game list
                    bills_games, other_games = await self.get_all_nfl_games_today()
                    return await self.select_games_to_monitor(bills_games, other_games)
                
                # Try to parse as game number
                try:
                    game_num = int(choice)
                    if 1 <= game_num <= len(all_selectable):
                        selected_game = all_selectable[game_num - 1]
                        
                        # Ask which team(s) to monitor
                        print(f"\n🏈 Selected: {selected_game['away_name']} @ {selected_game['home_name']}")
                        print("Which team(s) do you want to monitor?")
                        print(f"1. {selected_game['home_name']} only")
                        print(f"2. {selected_game['away_name']} only") 
                        print("3. Both teams")
                        
                        try:
                            team_choice = input("Team choice (1-3): ").strip()
                        except EOFError:
                            print("\n⏹️ Input ended, skipping team selection")
                            continue
                        
                        if team_choice == '1':
                            monitored_teams = [selected_game['home_abbr']]
                            primary_team = selected_game['home_abbr']
                        elif team_choice == '2':
                            monitored_teams = [selected_game['away_abbr']]
                            primary_team = selected_game['away_abbr']
                        elif team_choice == '3':
                            monitored_teams = [selected_game['home_abbr'], selected_game['away_abbr']]
                            primary_team = selected_game['home_abbr']  # Home team as primary
                        else:
                            print("❌ Invalid choice. Skipping this game.")
                            continue
                        
                        config = {
                            'game': selected_game,
                            'monitored_teams': monitored_teams,
                            'primary_team': primary_team
                        }
                        monitor_configs.append(config)
                        
                        teams_str = " & ".join([t for t in monitored_teams])
                        print(f"✅ Added: {selected_game['away_name']} @ {selected_game['home_name']} (monitoring: {teams_str})")
                        
                    else:
                        print(f"❌ Invalid game number. Please enter 1-{len(all_selectable)}")
                
                except ValueError:
                    print("❌ Invalid input. Please enter a game number or 'done'")
                    
            except KeyboardInterrupt:
                print("\n⏹️ Selection cancelled")
                break
            except EOFError:
                print("\n⏹️ Input ended, finishing selection")
                break
        
        return monitor_configs
    
    async def get_current_scores(self, game_id):
        """Get current scores and red zone status for a specific game"""
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
                            
                            red_zone_info['team'] = team_abbr
                            red_zone_info['active'] = True
                            yard_line = situation.get('yardLine', 0)
                            red_zone_info['yard_line'] = yard_line
                        else:
                            red_zone_info['active'] = False
                    else:
                        red_zone_info['active'] = False
                    
                    # If no red zone info from scoreboard, try Summary API with field position
                    if not red_zone_info.get('active'):
                        try:
                            summary_url = f'http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}'
                            summary_response = requests.get(summary_url, timeout=5)
                            if summary_response.status_code == 200:
                                summary_data = summary_response.json()
                                
                                # Try situation data first
                                situation = summary_data.get('situation', {})
                                if situation:
                                    is_red_zone = situation.get('isRedZone', False)
                                    possession_team = situation.get('possession', '')
                                    
                                    if is_red_zone and possession_team:
                                        red_zone_info['team'] = possession_team
                                        red_zone_info['active'] = True
                                        yard_line = situation.get('yardLine', 0)
                                        red_zone_info['yard_line'] = yard_line
                                
                                # If no situation data, check drives for field position
                                if not red_zone_info.get('active'):
                                    drives = summary_data.get('drives', {})
                                    if drives and isinstance(drives, dict):
                                        current = drives.get('current', {})
                                        if current:
                                            plays = current.get('plays', [])
                                            if plays:
                                                last_play = plays[-1]
                                                end_pos = last_play.get('end', {})
                                                
                                                if end_pos:
                                                    # Use yardsToEndzone for more accurate red zone detection
                                                    yards_to_endzone = end_pos.get('yardsToEndzone', 0)
                                                    yard_line = end_pos.get('yardLine', 0)
                                                    team_info = end_pos.get('team', {})
                                                    
                                                    # Get team abbreviation from the drive team info
                                                    drive_team_info = current.get('team', {})
                                                    team_abbr = drive_team_info.get('abbreviation', '')
                                                    
                                                    # Red zone is 20 yards or less from goal line
                                                    if yards_to_endzone <= 20 and yards_to_endzone > 0 and team_abbr:
                                                        red_zone_info['team'] = team_abbr
                                                        red_zone_info['active'] = True
                                                        red_zone_info['yard_line'] = yards_to_endzone
                                                        print(f"🎯 RED ZONE DETECTED: {team_abbr} at {yards_to_endzone} yards from goal!")
                        except:
                            pass  # Fallback failed, continue without red zone info
                    
                    return scores, status, red_zone_info
            
            return None, None, {}
            
        except Exception as e:
            print(f"❌ Error getting scores for game {game_id}: {e}")
            return None, None, {}
    
    def get_team_display_name(self, team_abbr, game):
        """Get team display name from abbreviation"""
        if team_abbr == game['home_abbr']:
            return game['home_name']
        elif team_abbr == game['away_abbr']:
            return game['away_name']
        return team_abbr  # Fallback to abbreviation
    
    async def detect_score_change(self, config, new_scores, status):
        """Detect scoring changes and trigger celebrations"""
        game = config['game']
        monitored_teams = config['monitored_teams']
        game_id = game['id']
        
        # Get last known scores
        last_scores = self.game_scores.get(game_id, {})
        
        for team in monitored_teams:
            if team in new_scores and team in last_scores:
                old_score = last_scores[team]
                new_score = new_scores[team]
                
                if new_score > old_score:
                    score_diff = new_score - old_score
                    opponent = [t for t in [game['home_abbr'], game['away_abbr']] if t != team][0]
                    opponent_score = new_scores.get(opponent, 0)
                    
                    print(f"\n🎉 {team} SCORED! +{score_diff} points")
                    print(f"📊 Score: {team} {new_score} - {opponent} {opponent_score}")
                    
                    # Use team-specific colors for celebrations
                    if team in NFL_TEAM_COLORS:
                        primary, secondary = NFL_TEAM_COLORS[team]
                        self.celebration_controller.set_team_colors(team, primary, secondary)
                    
                    # Get team display name for celebrations
                    team_name = self.get_team_display_name(team, game)
                    
                    # Determine celebration type and trigger
                    if score_diff == 6:
                        print(f"🏈 {team} TOUCHDOWN detected!")
                        await self.celebration_controller.celebrate_touchdown(team_name)
                    elif score_diff == 3:
                        print(f"🥅 {team} FIELD GOAL detected!")
                        await self.celebration_controller.celebrate_field_goal(team_name)
                    elif score_diff == 1:
                        print(f"✅ {team} EXTRA POINT detected!")
                        await self.celebration_controller.celebrate_extra_point(team_name)
                    elif score_diff == 2:
                        # For 2-point changes, check recent plays to determine if it's a 2-point conversion or safety
                        recent_plays = await self.get_recent_plays(game_id)
                        is_two_point = False
                        
                        if recent_plays:
                            # Check last few plays for conversion attempt
                            for play in recent_plays[-3:]:
                                play_text = play.get('text', '').lower()
                                if 'conversion' in play_text or 'two-point' in play_text or '2-pt' in play_text:
                                    is_two_point = True
                                    break
                        
                        if is_two_point:
                            print(f"💪 {team} 2-POINT CONVERSION detected!")
                            await self.celebration_controller.celebrate_two_point(team_name)
                        else:
                            print(f"🛡️ {team} SAFETY detected!")
                            await self.celebration_controller.celebrate_safety(team_name)
                    else:
                        print(f"🎯 {team} UNUSUAL SCORE (+{score_diff}) - Touchdown celebration!")
                        await self.celebration_controller.celebrate_touchdown(team_name)
        
        # Check for game end victories (only celebrate if the game just became final)
        if 'final' in status.lower():
            # Check if this game was already final when we started monitoring
            initial_status = self.initial_game_status.get(game_id, '')
            was_already_final = 'final' in initial_status.lower()
            
            # Only trigger victory if this is a newly finished game, not one that was already final
            if not was_already_final:
                for team in monitored_teams:
                    if team in new_scores:
                        team_score = new_scores[team]
                        opponent_scores = [new_scores[t] for t in new_scores if t != team]
                        
                        if opponent_scores and team_score > max(opponent_scores):
                            if not game.get(f'{team}_victory_celebrated'):
                                team_display_name = self.get_team_display_name(team, game)
                                print(f"\n🏆 {team} WINS! Final Score: {team_score}-{max(opponent_scores)}")
                                await self.celebration_controller.celebrate_victory(team_display_name)
                                game[f'{team}_victory_celebrated'] = True
        
        # Update stored scores
        self.game_scores[game_id] = new_scores
    
    async def check_red_zone_status(self, config, red_zone_info, game_id):
        """Check for red zone changes and manage ambient lighting"""
        game = config['game']
        monitored_teams = config['monitored_teams']
        
        # Get last known red zone status
        last_red_zone = self.red_zone_status.get(game_id, {})
        current_active = red_zone_info.get('active', False)
        current_team = red_zone_info.get('team', '')
        
        # Check if red zone status changed
        if current_active and current_team in monitored_teams:
            # Team is in red zone
            if not last_red_zone.get('active') or last_red_zone.get('team') != current_team:
                # Red zone started or team changed
                print(f"\n🎯 RED ZONE: {current_team} is in the red zone!")
                
                # Stop any existing red zone ambient
                if hasattr(self.celebration_controller, 'red_zone_active') and self.celebration_controller.red_zone_active:
                    await self.celebration_controller.stop_red_zone_ambient()
                
                # Set team colors for red zone lighting (only when status changes)
                if current_team in NFL_TEAM_COLORS:
                    primary, secondary = NFL_TEAM_COLORS[current_team]
                    self.celebration_controller.set_team_colors(current_team, primary, secondary)
                
                # Start red zone ambient lighting
                await self.celebration_controller.start_red_zone_ambient(current_team)
                
        elif last_red_zone.get('active') and not current_active:
            # Red zone ended
            last_team = last_red_zone.get('team', 'Team')
            print(f"\n🚫 RED ZONE ENDED: {last_team} left the red zone")
            
            # Stop red zone ambient lighting
            if hasattr(self.celebration_controller, 'red_zone_active') and self.celebration_controller.red_zone_active:
                await self.celebration_controller.stop_red_zone_ambient()
        
        # Update stored red zone status
        self.red_zone_status[game_id] = red_zone_info.copy()
    
    async def get_recent_plays(self, game_id):
        """Get recent plays for advanced play detection"""
        try:
            # Use ESPN summary API for detailed play data
            summary_url = f'http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}'
            response = requests.get(summary_url, timeout=8)
            response.raise_for_status()
            data = response.json()
            
            plays_data = []
            
            # Get plays from current drive
            drives = data.get('drives', {})
            current_drive = drives.get('current', {})
            current_plays = current_drive.get('plays', [])
            
            # Get plays from most recent previous drive
            previous_drives = drives.get('previous', [])
            recent_previous_plays = []
            if previous_drives:
                recent_drive = previous_drives[-1]
                recent_previous_plays = recent_drive.get('plays', [])
            
            # Combine recent plays (last 5 from previous drive + all current drive)
            all_recent_plays = recent_previous_plays[-5:] + current_plays
            
            # Get team ID to abbreviation mapping from the game data
            team_mapping = {}
            header = data.get('header', {})
            competitions = header.get('competitions', [])
            if competitions:
                competitors = competitions[0].get('competitors', [])
                for competitor in competitors:
                    team_info = competitor.get('team', {})
                    team_id = team_info.get('id', '')
                    team_abbr = team_info.get('abbreviation', '')
                    if team_id and team_abbr:
                        team_mapping[team_id] = team_abbr
            
            # Extract play information
            for play in all_recent_plays:
                # Try to get team from various sources
                team_abbr = ''
                
                # First try the top-level team field
                team_data = play.get('team', {})
                if isinstance(team_data, dict):
                    team_abbr = team_data.get('abbreviation', '')
                
                # If not found, try to get from start position team ID
                if not team_abbr:
                    start_data = play.get('start', {})
                    if start_data:
                        start_team = start_data.get('team', {})
                        team_id = start_team.get('id', '')
                        if team_id in team_mapping:
                            team_abbr = team_mapping[team_id]
                
                # If still not found, try to extract from play text
                if not team_abbr:
                    play_text = play.get('text', '')
                    # Look for team patterns in play text (this is a fallback)
                    for team_id, abbr in team_mapping.items():
                        if abbr.lower() in play_text.lower():
                            team_abbr = abbr
                            break
                
                play_info = {
                    'id': play.get('id', ''),
                    'text': play.get('text', ''),
                    'type': play.get('type', {}).get('text', 'Unknown') if isinstance(play.get('type'), dict) else play.get('type', 'Unknown'),
                    'team': team_abbr,
                    'start': play.get('start', {}),
                    'end': play.get('end', {}),
                    'statYardage': play.get('statYardage', 0)
                }
                plays_data.append(play_info)
            
            return plays_data
            
        except Exception as e:
            print(f"❌ Error getting plays for game {game_id}: {e}")
            return []
    
    async def check_play_events(self, config, game_id):
        """Check for new turnovers, sacks, big plays, and defensive stops"""
        monitored_teams = config['monitored_teams']
        
        # Get recent plays
        recent_plays = await self.get_recent_plays(game_id)
        if not recent_plays:
            return
        
        # Get the last play ID we processed
        last_processed_id = self.last_play_ids.get(game_id, '')
        
        # Find new plays since last check
        new_plays = []
        found_last = False if last_processed_id else True
        
        for play in recent_plays:
            if found_last:
                new_plays.append(play)
            elif play['id'] == last_processed_id:
                found_last = True
        
        # Process new plays for celebrations
        for play in new_plays:
            play_team = play['team']
            play_text = play['text'].lower()
            play_type = play['type']
            yards = play.get('statYardage', 0)
            
            # Only celebrate plays by monitored teams
            if play_team not in monitored_teams:
                continue
            
            # Set team colors for this play
            if play_team in NFL_TEAM_COLORS:
                primary, secondary = NFL_TEAM_COLORS[play_team]
                self.celebration_controller.set_team_colors(play_team, primary, secondary)
            
            # Detect different play types
            celebration_triggered = False
            
            # Get team display name for celebrations
            team_display_name = self.get_team_display_name(play_team, config['game'])
            
            # 1. SACK DETECTION
            if 'sack' in play_text and ('loss' in play_text or 'yards' in play_text):
                print(f"\n⚡ {play_team} SACK DETECTED!")
                print(f"📝 Play: {play['text'][:100]}")
                await self.celebration_controller.celebrate_sack(team_display_name)
                celebration_triggered = True
            
            # 2. TURNOVER DETECTION
            elif 'interception' in play_text or 'intercepted' in play_text:
                print(f"\n🔄 {play_team} INTERCEPTION!")
                print(f"📝 Play: {play['text'][:100]}")
                await self.celebration_controller.celebrate_turnover(team_display_name)
                celebration_triggered = True
            
            elif 'fumble' in play_text and ('recovered' in play_text or 'recovers' in play_text):
                # For fumble recoveries, the play_team is the recovering team (defense)
                # This is a turnover if our monitored team recovered the fumble
                print(f"\n🔄 {play_team} FUMBLE RECOVERY!")
                print(f"📝 Play: {play['text'][:100]}")
                await self.celebration_controller.celebrate_turnover(team_display_name)
                celebration_triggered = True
            
            # 3. BIG PLAY DETECTION (40+ yards, non-scoring, non-field goal)
            elif yards >= 40 and 'touchdown' not in play_text and 'field goal' not in play_text:
                print(f"\n🏃‍♂️ {play_team} BIG PLAY! {yards} yards!")
                print(f"📝 Play: {play['text'][:100]}")
                await self.celebration_controller.celebrate_big_play(team_display_name, play_text)
                celebration_triggered = True
            
            # 4. DEFENSIVE STOP DETECTION (4th down stops)
            elif ('4th' in play_text or 'fourth' in play_text) and ('incomplete' in play_text or 'no gain' in play_text or yards < 0):
                print(f"\n🛡️ {play_team} DEFENSIVE STOP!")
                print(f"📝 Play: {play['text'][:100]}")
                await self.celebration_controller.celebrate_defensive_stop(team_display_name)
                celebration_triggered = True
            
            if celebration_triggered:
                print(f"🎉 Advanced play celebration complete for {play_team}")
        
        # Update last processed play ID
        if recent_plays:
            self.last_play_ids[game_id] = recent_plays[-1]['id']
    
    async def monitor_all_games(self, monitor_configs, check_interval=10):
        """Monitor all selected games simultaneously"""
        if not monitor_configs:
            print("❌ No games to monitor")
            return
        
        self.monitoring = True
        self.first_check = True  # Skip victory celebrations on first monitoring check
        
        print(f"\n🎯 Starting multi-game NFL monitoring")
        print(f"⚡ Polling: Checking every {check_interval} seconds")
        print(f"🎮 Monitoring {len(monitor_configs)} game(s):")
        
        for config in monitor_configs:
            game = config['game']
            teams = ", ".join([t for t in config['monitored_teams']])
            print(f"   🏈 {game['away_name']} @ {game['home_name']} (teams: {teams})")
        
        print("🚨 Waiting for scores...")
        print("(Press Ctrl+C to stop monitoring)\n")
        
        # Initialize scores and track initial game status
        self.initial_game_status = {}
        for config in monitor_configs:
            game_id = config['game']['id']
            scores, status, _ = await self.get_current_scores(game_id)
            if scores:
                self.game_scores[game_id] = scores
                self.initial_game_status[game_id] = status
        
        try:
            while self.monitoring:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                for config in monitor_configs:
                    game = config['game']
                    game_id = game['id']
                    
                    # Get current scores and red zone info
                    scores, status, red_zone_info = await self.get_current_scores(game_id)
                    
                    if scores:
                        # Display current status
                        score_display = " - ".join([f"{team} {scores.get(team, 0)}" for team in config['monitored_teams']])
                        red_zone_display = ""
                        if red_zone_info.get('active'):
                            rz_team = red_zone_info.get('team', 'Unknown')
                            rz_yards = red_zone_info.get('yard_line', 0)
                            red_zone_display = f" | 🎯 {rz_team} RED ZONE ({rz_yards} yd)"
                        
                        print(f"[{current_time}] 📊 {game['away_name']} @ {game['home_name']}: {score_display} | {status}{red_zone_display}")
                        
                        # Check for score changes
                        await self.detect_score_change(config, scores, status)
                        
                        # Check for red zone changes
                        await self.check_red_zone_status(config, red_zone_info, game_id)
                        
                        # Check for advanced play events (turnovers, sacks, big plays)
                        await self.check_play_events(config, game_id)
                        
                        # Check if game is finished
                        if 'final' in status.lower():
                            print(f"🏁 Game finished: {game['away_name']} @ {game['home_name']}")
                    else:
                        print(f"[{current_time}] ⚠️ Could not get scores for {game['away_name']} @ {game['home_name']}")
                
                # After first check, allow victory celebrations for future score changes
                if hasattr(self, 'first_check'):
                    self.first_check = False
                
                await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            self.monitoring = False
            # Stop any active red zone lighting
            if hasattr(self.celebration_controller, 'red_zone_active') and self.celebration_controller.red_zone_active:
                await self.celebration_controller.stop_red_zone_ambient()
            print("💡 Setting lights to default...")
            await self.celebration_controller.set_default_lighting()
            print("👋 Monitoring ended. GO BILLS! 🦬")

def load_light_ips():
    """Load light IPs from config file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'wiz_lights_config.json')
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
    """Main function to run the enhanced NFL monitor"""
    print("🏈 Enhanced Buffalo Bills & NFL Multi-Game Monitor 🏈")
    print("=" * 65)
    
    # Load light IPs from config
    light_ips = load_light_ips()
    
    if not light_ips:
        print("❌ No light IPs found in config file!")
        return
    
    print(f"🎯 Initializing with {len(light_ips)} light(s):")
    for ip in light_ips:
        print(f"   - {ip}")
    
    # Initialize monitor
    monitor = EnhancedNFLMonitor(light_ips)
    
    # Test light connectivity
    print("\n🧪 Testing light connectivity...")
    if not await monitor.celebration_controller.test_connectivity():
        print("❌ Some lights not responding. Check your network connection.")
        return
    
    # Set initial warm default lighting
    await monitor.celebration_controller.set_default_lighting()
    
    # Get all NFL games
    bills_games, other_games = await monitor.get_all_nfl_games_today()
    
    if not bills_games and not other_games:
        print("😴 No NFL games found today!")
        print("💡 Setting lights to default...")
        await monitor.celebration_controller.set_default_lighting()
        return
    
    print(f"📊 Found {len(bills_games)} Bills game(s) and {len(other_games)} other NFL games")
    
    # Select games to monitor (Bills auto-selected)
    monitor_configs = await monitor.select_games_to_monitor(bills_games, other_games)
    
    if not monitor_configs:
        print("😴 No games selected for monitoring")
        print("💡 Setting lights to default...")
        await monitor.celebration_controller.set_default_lighting()
        return
    
    # Choose polling speed
    print(f"\n⚡ POLLING SPEED OPTIONS:")
    print("1. 🏃‍♂️ Ultra-Fast (5s) - Maximum speed for instant celebrations")
    print("2. ⚡ Fast (10s) - Recommended for multi-game monitoring")  
    print("3. 🚶‍♂️ Normal (15s) - Conservative and stable")
    print("4. 🐌 Slow (30s) - Original speed")
    
    try:
        speed_choice = input("Select polling speed (1-4, default=2): ").strip()
        speed_map = {'1': 5, '2': 10, '3': 15, '4': 30}
        check_interval = speed_map.get(speed_choice, 10)
        
        if check_interval == 5:
            print("⚠️ WARNING: 5-second polling is very aggressive!")
            print("   May trigger ESPN rate limiting with multiple games.")
            
        print(f"✅ Using {check_interval}-second polling for {len(monitor_configs)} game(s)")
    except:
        check_interval = 10
        print("✅ Using default 10-second polling")
    
    # Start monitoring
    await monitor.monitor_all_games(monitor_configs, check_interval=check_interval)

if __name__ == "__main__":
    asyncio.run(main())