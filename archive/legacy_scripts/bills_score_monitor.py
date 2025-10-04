"""
Buffalo Bills Real-Time Score Monitor
Monitors live NFL games for Bills scoring and triggers light celebrations
"""

import asyncio
import requests
import json
import time
import os
from datetime import datetime, timedelta
from bills_celebrations import BillsCelebrationController

class BillsScoreMonitor:
    def __init__(self, light_ips):
        self.celebration_controller = BillsCelebrationController(light_ips)
        self.bills_team_id = "BUF"  # Buffalo Bills team identifier
        self.current_game = None
        self.last_bills_score = 0
        self.last_opponent_score = 0
        self.monitoring = False
        
        # API endpoints (free, public APIs)
        self.apis = {
            'espn': 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
            'nfl_backup': 'https://api.sportsdata.io/v3/nfl/scores/json/LiveGameStats',  # backup
        }
    
    async def find_bills_game_today(self):
        """Find if Bills are playing today and get game info"""
        print("🔍 Checking if Bills are playing today...")
        
        try:
            response = requests.get(self.apis['espn'], timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Look through today's games
            games = data.get('events', [])
            for game in games:
                competitors = game.get('competitions', [{}])[0].get('competitors', [])
                
                # Check if Bills are playing
                for competitor in competitors:
                    team = competitor.get('team', {})
                    if team.get('abbreviation') == self.bills_team_id:
                        # Found Bills game!
                        opponent = None
                        for comp in competitors:
                            if comp.get('team', {}).get('abbreviation') != self.bills_team_id:
                                opponent = comp.get('team', {}).get('displayName', 'Unknown')
                                break
                        
                        game_status = game.get('status', {}).get('type', {}).get('name', 'Unknown')
                        game_time = game.get('date', '')
                        
                        self.current_game = {
                            'id': game.get('id'),
                            'opponent': opponent,
                            'status': game_status,
                            'time': game_time,
                            'competitors': competitors,
                            'raw_game': game
                        }
                        
                        print(f"🏈 Found Bills vs {opponent}")
                        print(f"📅 Status: {game_status}")
                        print(f"🕒 Time: {game_time}")
                        return True
            
            print("😴 No Bills game found today")
            return False
            
        except Exception as e:
            print(f"❌ Error checking for Bills game: {e}")
            return False
    
    async def get_current_score(self):
        """Get the current score of the Bills game with rate limiting protection"""
        if not self.current_game:
            return None, None
        
        try:
            response = requests.get(self.apis['espn'], timeout=8)
            
            # Check for rate limiting
            if response.status_code == 429:
                print("⚠️ ESPN API rate limited - waiting extra time...")
                await asyncio.sleep(5)  # Extra delay if rate limited
                return self.last_bills_score, self.last_opponent_score
            
            response.raise_for_status()
            data = response.json()
            
            # Find our specific game
            games = data.get('events', [])
            for game in games:
                if game.get('id') == self.current_game['id']:
                    competitors = game.get('competitions', [{}])[0].get('competitors', [])
                    
                    bills_score = 0
                    opponent_score = 0
                    
                    for competitor in competitors:
                        team = competitor.get('team', {})
                        score = int(competitor.get('score', 0))
                        
                        if team.get('abbreviation') == self.bills_team_id:
                            bills_score = score
                        else:
                            opponent_score = score
                    
                    # Also update game status
                    self.current_game['status'] = game.get('status', {}).get('type', {}).get('name', 'Unknown')
                    
                    return bills_score, opponent_score
            
            print("❌ Could not find Bills game in current data")
            return None, None
            
        except Exception as e:
            print(f"❌ Error getting current score: {e}")
            return None, None
    
    async def detect_score_change(self, new_bills_score, new_opponent_score):
        """Detect what type of scoring occurred and trigger appropriate celebration"""
        
        # Check if Bills scored
        if new_bills_score > self.last_bills_score:
            score_diff = new_bills_score - self.last_bills_score
            print(f"\n🎉 BILLS SCORED! +{score_diff} points")
            print(f"📊 Score: Bills {new_bills_score} - {self.current_game['opponent']} {new_opponent_score}")
            
            # Determine type of score and celebrate
            if score_diff == 6:
                print("🏈 TOUCHDOWN detected!")
                await self.celebration_controller.celebrate_touchdown()
            elif score_diff == 3:
                print("🥅 FIELD GOAL detected!")
                await self.celebration_controller.celebrate_field_goal()
            elif score_diff == 1:
                print("✅ EXTRA POINT detected!")
                await self.celebration_controller.celebrate_extra_point()
            elif score_diff == 2:
                if self.last_bills_score % 8 == 6:  # If last score ended in 6, this is likely a 2-point conversion
                    print("💪 2-POINT CONVERSION detected!")
                    await self.celebration_controller.celebrate_two_point()
                else:  # Otherwise it's a safety
                    print("🛡️ SAFETY detected!")
                    await self.celebration_controller.celebrate_safety()
            elif score_diff == 8:
                print("🏈 TOUCHDOWN + EXTRA POINT detected!")
                await self.celebration_controller.celebrate_touchdown()
            else:
                print(f"🎯 UNUSUAL SCORE (+{score_diff}) - Generic celebration!")
                await self.celebration_controller.celebrate_touchdown()  # Default to TD celebration
        
        # Check if game ended in Bills victory
        game_status = self.current_game.get('status', '').lower()
        if 'final' in game_status and new_bills_score > new_opponent_score:
            if self.last_bills_score <= new_opponent_score or self.current_game.get('victory_celebrated') != True:
                print(f"\n🏆 BILLS WIN! Final Score: {new_bills_score} - {new_opponent_score}")
                await self.celebration_controller.celebrate_victory()
                self.current_game['victory_celebrated'] = True
    
    async def monitor_game(self, check_interval=10):
        """Monitor the Bills game for score changes"""
        if not self.current_game:
            print("❌ No Bills game found to monitor")
            return
        
        self.monitoring = True
        print(f"\n🎯 Starting live monitoring of Bills vs {self.current_game['opponent']}")
        print(f"⚡ Aggressive polling: Checking every {check_interval} seconds for fastest celebrations!")
        print("🚨 Waiting for Bills to score...")
        print("(Press Ctrl+C to stop monitoring)\n")
        
        try:
            while self.monitoring:
                # Get current score
                bills_score, opponent_score = await self.get_current_score()
                
                if bills_score is not None and opponent_score is not None:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"[{current_time}] 📊 Bills {bills_score} - {self.current_game['opponent']} {opponent_score} | Status: {self.current_game['status']}")
                    
                    # Check for score changes
                    if bills_score != self.last_bills_score or opponent_score != self.last_opponent_score:
                        await self.detect_score_change(bills_score, opponent_score)
                        
                        # Update last known scores
                        self.last_bills_score = bills_score
                        self.last_opponent_score = opponent_score
                    
                    # Check if game is over
                    if 'final' in self.current_game.get('status', '').lower():
                        print(f"\n🏁 Game finished! Final: Bills {bills_score} - {self.current_game['opponent']} {opponent_score}")
                        if bills_score > opponent_score:
                            print("🎉 BILLS WIN!")
                        else:
                            print("😢 Bills lost...")
                        break
                
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Could not get current score")
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            self.monitoring = False
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
    """Main function to run the score monitor"""
    print("🏈 Buffalo Bills Real-Time Score Monitor 🏈")
    print("=" * 50)
    
    # Load light IPs from config
    light_ips = load_light_ips()
    
    if not light_ips:
        print("❌ No light IPs found in config file!")
        return
    
    print(f"🎯 Initializing with {len(light_ips)} light(s):")
    for ip in light_ips:
        print(f"   - {ip}")
    
    # Initialize monitor
    monitor = BillsScoreMonitor(light_ips)
    
    # Test light connectivity
    print("\n🧪 Testing light connectivity...")
    if not await monitor.celebration_controller.test_connectivity():
        print("❌ Some lights not responding. Check your network connection.")
        return
    
    # Set initial warm default lighting
    await monitor.celebration_controller.set_default_lighting()
    
    # Look for Bills game today
    if await monitor.find_bills_game_today():
        print(f"\n🎮 Ready to monitor Bills vs {monitor.current_game['opponent']}!")
        
        # Get initial score
        bills_score, opponent_score = await monitor.get_current_score()
        if bills_score is not None and opponent_score is not None:
            monitor.last_bills_score = bills_score
            monitor.last_opponent_score = opponent_score
            print(f"🏁 Starting Score: Bills {bills_score} - {monitor.current_game['opponent']} {opponent_score}")
        
        # Start monitoring
        # Ask user for polling speed
        print(f"\n⚡ POLLING SPEED OPTIONS:")
        print("1. 🏃‍♂️ Ultra-Fast (5s) - Experimental maximum speed")
        print("2. ⚡ Fast (10s) - Recommended for quick celebrations")  
        print("3. 🚶‍♂️ Normal (15s) - Conservative and stable")
        print("4. 🐌 Slow (30s) - Original speed")
        
        try:
            speed_choice = input("Select polling speed (1-4, default=2): ").strip()
            speed_map = {'1': 5, '2': 10, '3': 15, '4': 30}
            check_interval = speed_map.get(speed_choice, 10)
            
            if check_interval == 5:
                print("⚠️ WARNING: 5-second polling is very aggressive!")
                print("   May trigger ESPN rate limiting. Will auto-adjust if needed.")
                
            print(f"✅ Using {check_interval}-second polling for Bills game")
        except:
            check_interval = 10
            print("✅ Using default 10-second polling")
        
        await monitor.monitor_game(check_interval=check_interval)
    else:
        print("\n😴 No Bills game today. Try again on game day!")
        print("💡 Setting lights to default...")
        await monitor.celebration_controller.set_default_lighting()

if __name__ == "__main__":
    asyncio.run(main())