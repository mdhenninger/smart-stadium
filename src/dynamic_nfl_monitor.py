"""
Pure Dynamic NFL Monitor - No Hardcoded Games
Auto-starts Bills monitoring + interactive selection for any other games
"""

import asyncio
from enhanced_nfl_monitor import EnhancedNFLMonitor
import json
import os

def load_light_ips():
    """Load light IPs from config file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'wiz_lights_config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('known_ips', [])
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return []

async def dynamic_nfl_monitor():
    print("🏈 Dynamic NFL Multi-Game Monitor 🏈")
    print("=" * 45)
    print("✅ Auto-monitors ALL Bills games")
    print("🎯 Interactive selection for any other games")
    print()
    
    # Load light IPs
    light_ips = load_light_ips()
    if not light_ips:
        print("❌ No light IPs found!")
        return
    
    print(f"🎯 Using {len(light_ips)} lights")
    
    # Initialize monitor
    monitor = EnhancedNFLMonitor(light_ips)
    
    # Test connectivity (continue even if some lights don't respond)
    print("\n🧪 Testing light connectivity...")
    connectivity_result = await monitor.celebration_controller.test_connectivity()
    if not connectivity_result:
        print("⚠️ Some lights not responding, but continuing with available lights...")
    else:
        print("✅ All lights responding!")
    
    # Set default lighting
    await monitor.celebration_controller.set_default_lighting()
    
    # Get games dynamically from ESPN API
    bills_games, other_games = await monitor.get_all_nfl_games_today()
    
    print(f"📊 Found {len(bills_games)} Bills games and {len(other_games)} other games")
    
    if not bills_games and not other_games:
        print("😴 No NFL games found today!")
        return
    
    # Auto-configure Bills games only
    monitor_configs = []
    
    for game in bills_games:
        opponent = game['away_abbr'] if game['home_abbr'] == 'BUF' else game['home_abbr']
        config = {
            'game': game,
            'monitored_teams': ['BUF', opponent],
            'primary_team': 'BUF'
        }
        monitor_configs.append(config)
        print(f"✅ Auto-added Bills game: {game['away_name']} @ {game['home_name']}")
    
    # Show other available games
    if other_games:
        print(f"\n🏈 OTHER NFL GAMES AVAILABLE ({len(other_games)} games)")
        print("=" * 60)
        
        # Filter for live and upcoming games
        live_games = [g for g in other_games if 'in_progress' in g['status'].lower() or 'live' in g['status'].lower()]
        upcoming_games = [g for g in other_games if 'scheduled' in g['status'].lower() or 'pre' in g['status'].lower()]
        
        all_selectable = live_games + upcoming_games
        
        if live_games:
            print("🔴 LIVE GAMES:")
            for i, game in enumerate(live_games, 1):
                print(f"  {i:2d}. {game['away_name']} @ {game['home_name']} ({game['away_score']}-{game['home_score']}) - LIVE")
        
        if upcoming_games:
            print("⏰ UPCOMING GAMES:")
            start_idx = len(live_games) + 1
            for i, game in enumerate(upcoming_games, start_idx):
                print(f"  {i:2d}. {game['away_name']} @ {game['home_name']} - {game['status']}")
        
        if all_selectable:
            print(f"\n🎯 ADDITIONAL GAME SELECTION")
            print("Commands:")
            print("  • Enter game number (e.g., '1') to select a game")
            print("  • Enter 'skip' to monitor only Bills games")
            print("  • Enter 'quit' to exit")
            
            while True:
                try:
                    choice = input("\nYour choice: ").strip().lower()
                    
                    if choice == 'skip':
                        print("⏭️ Skipping additional games - monitoring Bills only")
                        break
                    elif choice == 'quit':
                        print("👋 Goodbye! GO BILLS! 🦬")
                        return
                    
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
                            
                            team_choice = input("Team choice (1-3): ").strip()
                            
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
                            
                            teams_str = " & ".join(monitored_teams)
                            print(f"✅ Added: {selected_game['away_name']} @ {selected_game['home_name']} (monitoring: {teams_str})")
                            
                            # Ask if they want to add more games
                            more = input("Add another game? (y/n): ").strip().lower()
                            if more != 'y':
                                break
                        else:
                            print(f"❌ Invalid game number. Please enter 1-{len(all_selectable)}")
                    
                    except ValueError:
                        print("❌ Invalid input. Please enter a game number, 'skip', or 'quit'")
                        
                except KeyboardInterrupt:
                    print("\n⏹️ Selection cancelled")
                    break
    
    if not monitor_configs:
        print("😴 No games configured for monitoring")
        return
    
    print(f"\n🎯 FINAL MONITORING SETUP ({len(monitor_configs)} games)")
    print("=" * 50)
    for config in monitor_configs:
        game = config['game']
        teams = ", ".join(config['monitored_teams'])
        print(f"   🏈 {game['away_name']} @ {game['home_name']} (teams: {teams})")
    
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
    print(f"\n🚀 Starting dynamic multi-game monitoring...")
    await monitor.monitor_all_games(monitor_configs, check_interval=check_interval)

if __name__ == "__main__":
    asyncio.run(dynamic_nfl_monitor())