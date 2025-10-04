#!/usr/bin/env python3
"""
Debug script to check exact status types for Alabama and South Carolina games
"""
import requests
from datetime import datetime
import json

def debug_game_statuses():
    """Check detailed status information for all games"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        url = f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={today}'
        
        print(f"🔍 Debugging game statuses for {today}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            
            print(f"\n📊 Found {len(games)} total games. Looking for Alabama and South Carolina:")
            print("=" * 100)
            
            for i, game in enumerate(games, 1):
                try:
                    # Get teams
                    teams = game['competitions'][0]['competitors']
                    away_team = next(team for team in teams if team['homeAway'] == 'away')
                    home_team = next(team for team in teams if team['homeAway'] == 'home')
                    
                    away_name = away_team['team']['displayName']
                    home_name = home_team['team']['displayName']
                    
                    # Check if this is Alabama or South Carolina
                    is_target_game = ("Alabama" in away_name or "Alabama" in home_name or 
                                    "South Carolina" in away_name or "South Carolina" in home_name)
                    
                    if is_target_game:
                        print(f"\n⭐ FOUND TARGET GAME: {away_name} @ {home_name}")
                        
                        # Get detailed status info
                        status = game['status']
                        print(f"   📊 Full Status Object:")
                        print(f"      - type.name: '{status['type']['name']}'")
                        print(f"      - type.description: '{status['type']['description']}'")
                        print(f"      - type.detail: '{status['type'].get('detail', 'N/A')}'")
                        print(f"      - type.shortDetail: '{status['type'].get('shortDetail', 'N/A')}'")
                        print(f"      - type.completed: {status['type'].get('completed', False)}")
                        print(f"      - displayClock: '{status.get('displayClock', 'N/A')}'")
                        print(f"      - period: {status.get('period', 'N/A')}")
                        
                        # Show our filtering logic
                        status_type = status['type']['name']
                        print(f"\n   🔍 Our Filter Logic:")
                        print(f"      - 'final' in status_type.lower(): {'final' in status_type.lower()}")
                        print(f"      - 'progress' in status_type.lower(): {'progress' in status_type.lower()}")
                        print(f"      - 'in' in status_type.lower(): {'in' in status_type.lower()}")
                        print(f"      - 'halftime' in status_type.lower(): {'halftime' in status_type.lower()}")
                        
                        if 'final' in status_type.lower():
                            print(f"      ❌ WOULD BE FILTERED OUT (final game)")
                        elif ('progress' in status_type.lower() or 'in' in status_type.lower() or 
                              'halftime' in status_type.lower()):
                            print(f"      ✅ WOULD BE INCLUDED (live game)")
                        else:
                            print(f"      ❓ UNCLEAR STATUS - might be filtered out")
                            
                except Exception as e:
                    print(f"Error parsing game {i}: {e}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_game_statuses()