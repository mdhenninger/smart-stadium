import requests
import json
from datetime import datetime, timedelta

# Check today and tomorrow for South Carolina games
for days_offset in [0, 1, 2]:  # Check today, tomorrow, and day after
    date = datetime.now() + timedelta(days=days_offset)
    date_str = date.strftime('%Y%m%d')
    
    try:
        url = f'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={date_str}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        games = data.get('events', [])
        print(f'=== {date.strftime("%B %d, %Y")} ({len(games)} games) ===')
        
        south_carolina_games = []
        for game in games:
            competitors = game.get('competitions', [{}])[0].get('competitors', [])
            if len(competitors) >= 2:
                home_team = competitors[0].get('team', {}).get('displayName', '')
                away_team = competitors[1].get('team', {}).get('displayName', '')
                
                # Check if South Carolina is playing
                if 'South Carolina' in home_team or 'South Carolina' in away_team or 'Gamecock' in home_team or 'Gamecock' in away_team:
                    status = game.get('status', {}).get('type', {}).get('detail', '')
                    game_date = game.get('date', '')
                    print(f'🏈 FOUND: {away_team} @ {home_team}')
                    print(f'   Status: {status}')
                    print(f'   Date: {game_date}')
                    south_carolina_games.append(game)
        
        if not south_carolina_games:
            print('   No South Carolina games found this day')
        print()
            
    except Exception as e:
        print(f'Error checking {date_str}: {e}')
        print()

print("🔍 Also checking all teams in today's games...")
try:
    url = 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
    response = requests.get(url, timeout=10)
    data = response.json()
    
    games = data.get('events', [])
    print(f"All teams playing today:")
    
    all_teams = set()
    for game in games:
        competitors = game.get('competitions', [{}])[0].get('competitors', [])
        for comp in competitors:
            team_name = comp.get('team', {}).get('displayName', '')
            all_teams.add(team_name)
    
    # Look for any South Carolina related teams
    carolina_teams = [team for team in sorted(all_teams) if 'Carolina' in team or 'Gamecock' in team]
    if carolina_teams:
        print("Carolina-related teams found:")
        for team in carolina_teams:
            print(f"  - {team}")
    else:
        print("No Carolina-related teams found in today's games")
        
except Exception as e:
    print(f'Error: {e}')