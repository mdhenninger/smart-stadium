#!/usr/bin/env python3
"""
Quick script to check ALL college football games today, including finished ones
"""
import asyncio
import requests
from datetime import datetime

async def check_all_games():
    """Check all games including finished ones"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        url = f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={today}'
        
        print(f"🔍 Checking ESPN API for ALL games on {today}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            
            print(f"\n📊 Found {len(games)} total games today:")
            print("=" * 80)
            
            for i, game in enumerate(games, 1):
                try:
                    # Get teams
                    teams = game['competitions'][0]['competitors']
                    away_team = next(team for team in teams if team['homeAway'] == 'away')
                    home_team = next(team for team in teams if team['homeAway'] == 'home')
                    
                    away_name = away_team['team']['displayName']
                    home_name = home_team['team']['displayName']
                    away_score = away_team.get('score', '0')
                    home_score = home_team.get('score', '0')
                    
                    # Get status
                    status = game['status']
                    status_text = status['type']['description']
                    
                    # Special handling for different statuses
                    if status['type']['completed']:
                        status_display = "🏁 FINAL"
                    elif status['type']['name'] in ['STATUS_IN_PROGRESS', 'STATUS_HALFTIME']:
                        if 'displayClock' in status:
                            clock = status['displayClock']
                            period = status.get('period', 1)
                            periods = ['1st Quarter', '2nd Quarter', 'Halftime', '3rd Quarter', '4th Quarter']
                            period_name = periods[period-1] if period <= len(periods) else f"Period {period}"
                            if period == 3 and status_text == "Halftime":
                                period_name = "Halftime"
                            status_display = f"🔴 LIVE - {clock} - {period_name}"
                        else:
                            status_display = f"🔴 LIVE - {status_text}"
                    else:
                        status_display = f"⏰ {status_text}"
                    
                    print(f"{i:2d}. {away_name:25} @ {home_name:25} ({away_score:2}-{home_score:2}) {status_display}")
                    
                    # Highlight Alabama and South Carolina games
                    if "Alabama" in away_name or "Alabama" in home_name:
                        print(f"    ⭐ ALABAMA GAME FOUND! Status: {status_display}")
                    if "South Carolina" in away_name or "South Carolina" in home_name:
                        print(f"    ⭐ SOUTH CAROLINA GAME FOUND! Status: {status_display}")
                        
                except Exception as e:
                    print(f"{i:2d}. Error parsing game: {e}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_all_games())