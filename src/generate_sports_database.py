"""
Comprehensive Sports Database Generator
Creates unified database for NFL, College Football, NHL, MLB, NBA with colors and logos
"""

import requests
import json
import time
from typing import Dict, List, Optional

class SportsDataCollector:
    """Collect team data from ESPN APIs across all major sports"""
    
    def __init__(self):
        self.base_urls = {
            'nfl': 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams',
            'college': 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams',
            'nhl': 'http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams',
            'mlb': 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams',
            'nba': 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams'
        }
        
        self.sports_database = {}
        
    def collect_nfl_teams(self) -> Dict:
        """Collect all 32 NFL teams with colors and logos"""
        print("🏈 Collecting NFL teams...")
        
        try:
            response = requests.get(self.base_urls['nfl'], timeout=15)
            response.raise_for_status()
            data = response.json()
            
            nfl_teams = {}
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            for team in teams:
                team_data = team.get('team', {})
                
                # Basic info
                team_id = team_data.get('id')
                name = team_data.get('displayName', '')
                abbreviation = team_data.get('abbreviation', '')
                location = team_data.get('location', '')
                nickname = team_data.get('name', '')
                
                # Colors - ESPN provides color and alternateColor
                color = team_data.get('color', '#000000')
                alt_color = team_data.get('alternateColor', '#FFFFFF')
                
                # Convert hex to RGB
                primary_rgb = self.hex_to_rgb(color)
                secondary_rgb = self.hex_to_rgb(alt_color)
                
                # Logos - ESPN provides multiple logo sizes
                logos = team_data.get('logos', [])
                logo_url = logos[0].get('href', '') if logos else ''
                
                # Create unified key
                unified_key = f"NFL-{location.upper().replace(' ', '_')}-{nickname.upper().replace(' ', '_')}"
                
                nfl_teams[unified_key] = {
                    'sport': 'NFL',
                    'espn_id': team_id,
                    'display_name': name,
                    'location': location,
                    'nickname': nickname,
                    'abbreviation': abbreviation,
                    'primary_color': primary_rgb,
                    'secondary_color': secondary_rgb,
                    'primary_hex': color,
                    'secondary_hex': alt_color,
                    'logo_url': logo_url,
                    'unified_key': unified_key
                }
                
                print(f"   ✅ {name} - {primary_rgb} / {secondary_rgb}")
            
            print(f"🏈 Collected {len(nfl_teams)} NFL teams")
            return nfl_teams
            
        except Exception as e:
            print(f"❌ Error collecting NFL teams: {e}")
            return {}
    
    def collect_college_teams(self) -> Dict:
        """Collect College Football teams with colors and logos"""
        print("🎓 Collecting College Football teams...")
        
        try:
            # Try multiple endpoints to get all teams
            college_endpoints = [
                'http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams',
                'http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams?groups=80',  # FBS only
                'http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams?limit=200'   # Higher limit
            ]
            
            college_teams = {}
            
            for endpoint in college_endpoints:
                try:
                    print(f"   📡 Trying endpoint: {endpoint.split('/')[-1]}")
                    response = requests.get(endpoint, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    
                    teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
                    print(f"   📊 Found {len(teams)} teams in this endpoint")
                    
                    for team in teams:
                        team_data = team.get('team', {})
                        
                        # Basic info
                        team_id = team_data.get('id')
                        name = team_data.get('displayName', '')
                        abbreviation = team_data.get('abbreviation', '')
                        location = team_data.get('location', '')
                        nickname = team_data.get('name', '')
                        
                        # Skip if we already have this team (by id)
                        if any(existing['espn_id'] == team_id for existing in college_teams.values()):
                            continue
                        
                        # Colors
                        color = team_data.get('color', '#000000')
                        alt_color = team_data.get('alternateColor', '#FFFFFF')
                        
                        primary_rgb = self.hex_to_rgb(color)
                        secondary_rgb = self.hex_to_rgb(alt_color)
                        
                        # Logos
                        logos = team_data.get('logos', [])
                        logo_url = logos[0].get('href', '') if logos else ''
                        
                        # Create unified key - use school name approach
                        school_name = location if location else name.split()[0]
                        unified_key = f"CFB-{school_name.upper().replace(' ', '_')}-{nickname.upper().replace(' ', '_')}"
                        
                        # Handle duplicate keys
                        counter = 2
                        original_key = unified_key
                        while unified_key in college_teams:
                            unified_key = f"{original_key}_{counter}"
                            counter += 1
                        
                        college_teams[unified_key] = {
                            'sport': 'CFB',
                            'espn_id': team_id,
                            'display_name': name,
                            'location': location,
                            'nickname': nickname,
                            'abbreviation': abbreviation,
                            'primary_color': primary_rgb,
                            'secondary_color': secondary_rgb,
                            'primary_hex': color,
                            'secondary_hex': alt_color,
                            'logo_url': logo_url,
                            'unified_key': unified_key
                        }
                        
                        # Show progress for college teams
                        if len(college_teams) <= 10:
                            print(f"   ✅ {name} - {primary_rgb} / {secondary_rgb}")
                        elif len(college_teams) == 11:
                            print(f"   ... (collecting all FBS teams, showing progress)")
                        elif len(college_teams) % 50 == 0:  # Show progress every 50 teams
                            print(f"   📊 Progress: {len(college_teams)} teams collected...")
                
                except Exception as e:
                    print(f"   ⚠️ Error with endpoint: {e}")
                    continue
            
            print(f"🎓 Collected {len(college_teams)} College Football teams")
            return college_teams
            
        except Exception as e:
            print(f"❌ Error collecting college teams: {e}")
            return {}
    
    def collect_nhl_teams(self) -> Dict:
        """Collect all 32 NHL teams with colors and logos"""
        print("🏒 Collecting NHL teams...")
        
        try:
            response = requests.get(self.base_urls['nhl'], timeout=15)
            response.raise_for_status()
            data = response.json()
            
            nhl_teams = {}
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            for team in teams:
                team_data = team.get('team', {})
                
                # Basic info
                team_id = team_data.get('id')
                name = team_data.get('displayName', '')
                abbreviation = team_data.get('abbreviation', '')
                location = team_data.get('location', '')
                nickname = team_data.get('name', '')
                
                # Colors
                color = team_data.get('color', '#000000')
                alt_color = team_data.get('alternateColor', '#FFFFFF')
                
                primary_rgb = self.hex_to_rgb(color)
                secondary_rgb = self.hex_to_rgb(alt_color)
                
                # Logos
                logos = team_data.get('logos', [])
                logo_url = logos[0].get('href', '') if logos else ''
                
                # Create unified key
                unified_key = f"NHL-{location.upper().replace(' ', '_')}-{nickname.upper().replace(' ', '_')}"
                
                nhl_teams[unified_key] = {
                    'sport': 'NHL',
                    'espn_id': team_id,
                    'display_name': name,
                    'location': location,
                    'nickname': nickname,
                    'abbreviation': abbreviation,
                    'primary_color': primary_rgb,
                    'secondary_color': secondary_rgb,
                    'primary_hex': color,
                    'secondary_hex': alt_color,
                    'logo_url': logo_url,
                    'unified_key': unified_key
                }
                
                print(f"   ✅ {name} - {primary_rgb} / {secondary_rgb}")
            
            print(f"🏒 Collected {len(nhl_teams)} NHL teams")
            return nhl_teams
            
        except Exception as e:
            print(f"❌ Error collecting NHL teams: {e}")
            return {}
    
    def collect_mlb_teams(self) -> Dict:
        """Collect all 30 MLB teams with colors and logos"""
        print("⚾ Collecting MLB teams...")
        
        try:
            response = requests.get(self.base_urls['mlb'], timeout=15)
            response.raise_for_status()
            data = response.json()
            
            mlb_teams = {}
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            for team in teams:
                team_data = team.get('team', {})
                
                # Basic info
                team_id = team_data.get('id')
                name = team_data.get('displayName', '')
                abbreviation = team_data.get('abbreviation', '')
                location = team_data.get('location', '')
                nickname = team_data.get('name', '')
                
                # Colors
                color = team_data.get('color', '#000000')
                alt_color = team_data.get('alternateColor', '#FFFFFF')
                
                primary_rgb = self.hex_to_rgb(color)
                secondary_rgb = self.hex_to_rgb(alt_color)
                
                # Logos
                logos = team_data.get('logos', [])
                logo_url = logos[0].get('href', '') if logos else ''
                
                # Create unified key
                unified_key = f"MLB-{location.upper().replace(' ', '_')}-{nickname.upper().replace(' ', '_')}"
                
                mlb_teams[unified_key] = {
                    'sport': 'MLB',
                    'espn_id': team_id,
                    'display_name': name,
                    'location': location,
                    'nickname': nickname,
                    'abbreviation': abbreviation,
                    'primary_color': primary_rgb,
                    'secondary_color': secondary_rgb,
                    'primary_hex': color,
                    'secondary_hex': alt_color,
                    'logo_url': logo_url,
                    'unified_key': unified_key
                }
                
                print(f"   ✅ {name} - {primary_rgb} / {secondary_rgb}")
            
            print(f"⚾ Collected {len(mlb_teams)} MLB teams")
            return mlb_teams
            
        except Exception as e:
            print(f"❌ Error collecting MLB teams: {e}")
            return {}
    
    def collect_nba_teams(self) -> Dict:
        """Collect all 30 NBA teams with colors and logos"""
        print("🏀 Collecting NBA teams...")
        
        try:
            response = requests.get(self.base_urls['nba'], timeout=15)
            response.raise_for_status()
            data = response.json()
            
            nba_teams = {}
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            for team in teams:
                team_data = team.get('team', {})
                
                # Basic info
                team_id = team_data.get('id')
                name = team_data.get('displayName', '')
                abbreviation = team_data.get('abbreviation', '')
                location = team_data.get('location', '')
                nickname = team_data.get('name', '')
                
                # Colors
                color = team_data.get('color', '#000000')
                alt_color = team_data.get('alternateColor', '#FFFFFF')
                
                primary_rgb = self.hex_to_rgb(color)
                secondary_rgb = self.hex_to_rgb(alt_color)
                
                # Logos
                logos = team_data.get('logos', [])
                logo_url = logos[0].get('href', '') if logos else ''
                
                # Create unified key
                unified_key = f"NBA-{location.upper().replace(' ', '_')}-{nickname.upper().replace(' ', '_')}"
                
                nba_teams[unified_key] = {
                    'sport': 'NBA',
                    'espn_id': team_id,
                    'display_name': name,
                    'location': location,
                    'nickname': nickname,
                    'abbreviation': abbreviation,
                    'primary_color': primary_rgb,
                    'secondary_color': secondary_rgb,
                    'primary_hex': color,
                    'secondary_hex': alt_color,
                    'logo_url': logo_url,
                    'unified_key': unified_key
                }
                
                print(f"   ✅ {name} - {primary_rgb} / {secondary_rgb}")
            
            print(f"🏀 Collected {len(nba_teams)} NBA teams")
            return nba_teams
            
        except Exception as e:
            print(f"❌ Error collecting NBA teams: {e}")
            return {}
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Handle 3-digit hex
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            
            # Convert to RGB
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (0, 0, 0)  # Default to black
    
    def create_abbreviation_mapping(self, teams_db: Dict) -> Dict:
        """Create mapping from abbreviations to unified keys"""
        mapping = {}
        
        for unified_key, team_data in teams_db.items():
            abbr = team_data.get('abbreviation', '')
            if abbr:
                mapping[abbr] = unified_key
                
                # Add some common variations for NFL
                if team_data['sport'] == 'NFL':
                    # Handle cases like LAR/LA, etc.
                    if abbr == 'LAR':
                        mapping['LA'] = unified_key
                    elif abbr == 'LV':
                        mapping['LAS'] = unified_key
        
        return mapping
    
    def collect_all_sports(self) -> Dict:
        """Collect all sports data and create unified database"""
        print("🌟 COLLECTING COMPREHENSIVE SPORTS DATABASE 🌟")
        print("=" * 60)
        
        all_teams = {}
        
        # Collect each sport
        all_teams.update(self.collect_nfl_teams())
        time.sleep(1)  # Be nice to ESPN
        
        all_teams.update(self.collect_college_teams())
        time.sleep(1)
        
        all_teams.update(self.collect_nhl_teams())
        time.sleep(1)
        
        all_teams.update(self.collect_mlb_teams())
        time.sleep(1)
        
        all_teams.update(self.collect_nba_teams())
        
        # Create abbreviation mapping
        abbr_mapping = self.create_abbreviation_mapping(all_teams)
        
        # Create final database structure
        database = {
            'metadata': {
                'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_teams': len(all_teams),
                'sports_count': {
                    'NFL': len([t for t in all_teams.values() if t['sport'] == 'NFL']),
                    'CFB': len([t for t in all_teams.values() if t['sport'] == 'CFB']),
                    'NHL': len([t for t in all_teams.values() if t['sport'] == 'NHL']),
                    'MLB': len([t for t in all_teams.values() if t['sport'] == 'MLB']),
                    'NBA': len([t for t in all_teams.values() if t['sport'] == 'NBA'])
                }
            },
            'teams': all_teams,
            'abbreviation_mapping': abbr_mapping
        }
        
        print("\n🎯 COLLECTION COMPLETE!")
        print("=" * 40)
        for sport, count in database['metadata']['sports_count'].items():
            print(f"{sport}: {count} teams")
        print(f"Total: {database['metadata']['total_teams']} teams")
        
        return database


def main():
    """Generate comprehensive sports database"""
    print("🚀 COMPREHENSIVE SPORTS DATABASE GENERATOR 🚀")
    print("=" * 55)
    
    collector = SportsDataCollector()
    
    try:
        # Collect all sports data
        database = collector.collect_all_sports()
        
        # Save to file
        output_file = 'comprehensive_sports_database.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Database saved to: {output_file}")
        print(f"📊 Total teams: {database['metadata']['total_teams']}")
        print("✅ Ready for Smart Stadium integration!")
        
        # Show sample data
        print("\n📋 SAMPLE TEAMS:")
        print("-" * 30)
        sample_count = 0
        for key, team in database['teams'].items():
            if sample_count < 5:
                print(f"{team['sport']}: {team['display_name']}")
                print(f"   Key: {key}")
                print(f"   Colors: {team['primary_color']} / {team['secondary_color']}")
                print(f"   Logo: {team['logo_url'][:50]}..." if team['logo_url'] else "   Logo: None")
                print()
                sample_count += 1
            else:
                break
        
        return database
        
    except Exception as e:
        print(f"❌ Error generating database: {e}")
        return None

if __name__ == "__main__":
    main()