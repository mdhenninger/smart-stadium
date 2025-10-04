#!/usr/bin/env python3
"""
Test script to check if ESPN API provides field position/red zone data
"""
import requests
from datetime import datetime
import json

def check_field_position_data():
    """Check if ESPN API provides field position information"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        url = f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={today}'
        
        print(f"🔍 Checking ESPN API for field position data...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            
            print(f"\n📊 Found {len(games)} games. Checking for field position data:")
            print("=" * 80)
            
            for i, game in enumerate(games[:3], 1):  # Check first 3 games
                try:
                    # Get basic game info
                    teams = game['competitions'][0]['competitors']
                    away_team = next(team for team in teams if team['homeAway'] == 'away')
                    home_team = next(team for team in teams if team['homeAway'] == 'home')
                    
                    away_name = away_team['team']['displayName']
                    home_name = home_team['team']['displayName']
                    
                    print(f"\n🏈 Game {i}: {away_name} @ {home_name}")
                    
                    # Check competition data for field position
                    competition = game['competitions'][0]
                    print(f"   📋 Competition keys: {list(competition.keys())}")
                    
                    # Check if there's situation data
                    if 'situation' in competition:
                        situation = competition['situation']
                        print(f"   🎯 Situation data found!")
                        print(f"      Keys: {list(situation.keys())}")
                        
                        # Look for possession and field position
                        if 'possession' in situation:
                            print(f"      📍 Possession: {situation['possession']}")
                        if 'yardLine' in situation:
                            print(f"      🏁 Yard Line: {situation['yardLine']}")
                        if 'distance' in situation:
                            print(f"      📏 Distance: {situation['distance']}")
                        if 'down' in situation:
                            print(f"      ⬇️  Down: {situation['down']}")
                            
                        # Print full situation data
                        print(f"      📄 Full situation: {json.dumps(situation, indent=8)}")
                    else:
                        print(f"   ❌ No situation data found")
                    
                    # Check status for more detailed info
                    status = game['status']
                    if 'type' in status:
                        status_type = status['type']
                        print(f"   📊 Status type keys: {list(status_type.keys())}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error parsing game {i}: {e}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_field_position_data()