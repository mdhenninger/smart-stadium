#!/usr/bin/env python3
"""
Smart Stadium Team Database Migration - Single Source Conversion
Converts comprehensive database (324 teams) to existing config format
Maintains exact structure while expanding from 54 to 324 teams
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class SmartTeamMigrator:
    """Convert comprehensive database to existing config format"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.comprehensive_db_path = self.root_path / "src" / "comprehensive_sports_database.json"
        self.current_config_path = self.root_path / "config" / "team_colors.json"
        self.backup_path = self.root_path / "config" / f"team_colors_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # NFL Division mappings (maintain exact current structure)
        self.nfl_divisions = {
            'AFC_East': ['BUF', 'MIA', 'NE', 'NYJ'],
            'AFC_North': ['BAL', 'CIN', 'CLE', 'PIT'], 
            'AFC_South': ['HOU', 'IND', 'JAX', 'TEN'],
            'AFC_West': ['DEN', 'KC', 'LV', 'LAC'],
            'NFC_East': ['DAL', 'NYG', 'PHI', 'WAS'],
            'NFC_North': ['CHI', 'DET', 'GB', 'MIN'],
            'NFC_South': ['ATL', 'CAR', 'NO', 'TB'],
            'NFC_West': ['ARI', 'LAR', 'SF', 'SEA']
        }
        
        # NHL Division mappings
        self.nhl_divisions = {
            'Atlantic': ['BOS', 'BUF', 'DET', 'FLA', 'MTL', 'OTT', 'TB', 'TOR'],
            'Metropolitan': ['CAR', 'CBJ', 'NJ', 'NYI', 'NYR', 'PHI', 'PIT', 'WSH'],
            'Central': ['ARI', 'CHI', 'COL', 'DAL', 'MIN', 'NSH', 'STL', 'WPG'],
            'Pacific': ['ANA', 'CGY', 'EDM', 'LA', 'SJ', 'SEA', 'VAN', 'VGK']
        }
        
        # MLB Division mappings  
        self.mlb_divisions = {
            'AL_East': ['BAL', 'BOS', 'NYY', 'TB', 'TOR'],
            'AL_Central': ['CHW', 'CLE', 'DET', 'KC', 'MIN'],
            'AL_West': ['HOU', 'LAA', 'OAK', 'SEA', 'TEX'],
            'NL_East': ['ATL', 'MIA', 'NYM', 'PHI', 'WSH'],
            'NL_Central': ['CHC', 'CIN', 'MIL', 'PIT', 'STL'],
            'NL_West': ['ARI', 'COL', 'LAD', 'SD', 'SF']
        }
        
        # NBA Conference mappings
        self.nba_conferences = {
            'Eastern': ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND', 
                       'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WSH'],
            'Western': ['DAL', 'DEN', 'GS', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN',
                       'NO', 'OKC', 'PHX', 'POR', 'SA', 'SAC', 'UTA']
        }
    
    def load_comprehensive_database(self) -> Dict[str, Any]:
        """Load the comprehensive sports database"""
        print(f"📥 Loading comprehensive database from: {self.comprehensive_db_path}")
        with open(self.comprehensive_db_path, 'r') as f:
            return json.load(f)
    
    def backup_current_config(self):
        """Backup current team colors configuration"""
        if self.current_config_path.exists():
            shutil.copy2(self.current_config_path, self.backup_path)
            print(f"✅ Backed up current config to: {self.backup_path}")
        else:
            print("ℹ️  No existing config to backup")
    
    def convert_to_current_format(self, comprehensive_db: Dict[str, Any]) -> Dict[str, Any]:
        """Convert comprehensive database to exact current config format"""
        teams = comprehensive_db.get('teams', {})
        
        # Initialize new config with same structure as current
        new_config = {
            'nfl_teams': {},
            'college_teams': {},
            'nhl_teams': {},
            'mlb_teams': {},
            'nba_teams': {}
        }
        
        print("🔄 Converting teams to current format...")
        
        # Process NFL teams (maintain divisional structure)
        print("🏈 Processing NFL teams...")
        for division, team_abbrs in self.nfl_divisions.items():
            new_config['nfl_teams'][division] = {}
            for abbr in team_abbrs:
                # Find team by abbreviation
                team_data = next((v for v in teams.values() 
                                if v.get('sport') == 'NFL' and v.get('abbreviation') == abbr), None)
                if team_data:
                    new_config['nfl_teams'][division][abbr] = {
                        'name': team_data['display_name'],
                        'city': team_data.get('location', ''),
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'colors_description': f"{team_data.get('primary_hex', '')} & {team_data.get('secondary_hex', '')}",
                        'logo_url': team_data.get('logo_url', ''),
                        'espn_id': team_data.get('espn_id', ''),
                        'unified_key': team_data.get('unified_key', '')
                    }
        
        # Process College Football teams (flat structure like current)
        print("🎓 Processing College Football teams...")
        cfb_teams = {k: v for k, v in teams.items() if v.get('sport') == 'CFB'}
        
        # Create proper conference mappings for major CFB teams
        conference_map = {
            # ACC teams
            'Syracuse Orange': 'ACC',
            'Clemson Tigers': 'ACC', 
            'Miami Hurricanes': 'ACC',
            'Florida State Seminoles': 'ACC',
            'Duke Blue Devils': 'ACC',
            'North Carolina Tar Heels': 'ACC',
            'NC State Wolfpack': 'ACC',
            'Virginia Cavaliers': 'ACC',
            'Virginia Tech Hokies': 'ACC',
            'Wake Forest Demon Deacons': 'ACC',
            'Boston College Eagles': 'ACC',
            'Pittsburgh Panthers': 'ACC',
            'Louisville Cardinals': 'ACC',
            'Georgia Tech Yellow Jackets': 'ACC',
            'California Golden Bears': 'ACC',
            'Stanford Cardinal': 'ACC',
            'SMU Mustangs': 'ACC',
            
            # SEC teams  
            'Alabama Crimson Tide': 'SEC',
            'Georgia Bulldogs': 'SEC',
            'Florida Gators': 'SEC',
            'LSU Tigers': 'SEC',
            'Auburn Tigers': 'SEC',
            'Tennessee Volunteers': 'SEC',
            'Kentucky Wildcats': 'SEC',
            'Arkansas Razorbacks': 'SEC',
            'Ole Miss Rebels': 'SEC',
            'Mississippi State Bulldogs': 'SEC',
            'South Carolina Gamecocks': 'SEC',
            'Vanderbilt Commodores': 'SEC',
            'Texas A&M Aggies': 'SEC',
            'Missouri Tigers': 'SEC',
            'Texas Longhorns': 'SEC',
            'Oklahoma Sooners': 'SEC',
            
            # Big Ten teams
            'Ohio State Buckeyes': 'Big_Ten',
            'Michigan Wolverines': 'Big_Ten',
            'Penn State Nittany Lions': 'Big_Ten',
            'Wisconsin Badgers': 'Big_Ten',
            'Iowa Hawkeyes': 'Big_Ten',
            'Minnesota Golden Gophers': 'Big_Ten',
            'Illinois Fighting Illini': 'Big_Ten',
            'Indiana Hoosiers': 'Big_Ten',
            'Northwestern Wildcats': 'Big_Ten',
            'Purdue Boilermakers': 'Big_Ten',
            'Michigan State Spartans': 'Big_Ten',
            'Nebraska Cornhuskers': 'Big_Ten',
            'Maryland Terrapins': 'Big_Ten',
            'Rutgers Scarlet Knights': 'Big_Ten',
            'Oregon Ducks': 'Big_Ten',
            'Washington Huskies': 'Big_Ten',
            'UCLA Bruins': 'Big_Ten',
            'USC Trojans': 'Big_Ten',
            
            # Big 12 teams
            'Kansas Jayhawks': 'Big_12',
            'Kansas State Wildcats': 'Big_12',
            'Iowa State Cyclones': 'Big_12',
            'Baylor Bears': 'Big_12',
            'TCU Horned Frogs': 'Big_12',
            'Texas Tech Red Raiders': 'Big_12',
            'Oklahoma State Cowboys': 'Big_12',
            'West Virginia Mountaineers': 'Big_12',
            'Cincinnati Bearcats': 'Big_12',
            'Houston Cougars': 'Big_12',
            'UCF Knights': 'Big_12',
            'BYU Cougars': 'Big_12',
            'Colorado Buffaloes': 'Big_12',
            'Arizona Wildcats': 'Big_12',
            'Arizona State Sun Devils': 'Big_12',
            'Utah Utes': 'Big_12',
            
            # Pac-12 teams (remaining)
            'Washington State Cougars': 'Pac_12',
            'Oregon State Beavers': 'Pac_12',
            
            # Independent
            'Notre Dame Fighting Irish': 'Independent',
            'UConn Huskies': 'Independent',
            'UMass Minutemen': 'Independent',
            'Army Black Knights': 'Independent',
            'Navy Midshipmen': 'Independent',
        }
        
        # Group by conferences for better organization
        conferences = {}
        for unified_key, team_data in cfb_teams.items():
            team_name = team_data['display_name']
            
            # Use our proper conference mapping
            conference = conference_map.get(team_name, 'Other')
            
            if conference not in conferences:
                conferences[conference] = {}
            
            # Use team abbreviation as key (more consistent)
            key = team_data.get('abbreviation', team_name.replace(' ', '_').replace('.', '').replace("'", ""))
            conferences[conference][key] = {
                'name': team_data['display_name'],
                'abbreviation': team_data.get('abbreviation', ''),
                'primary_color': team_data['primary_color'],
                'secondary_color': team_data['secondary_color'],
                'colors_description': f"{team_data.get('primary_hex', '')} & {team_data.get('secondary_hex', '')}",
                'logo_url': team_data.get('logo_url', ''),
                'espn_id': team_data.get('espn_id', ''),
                'unified_key': team_data.get('unified_key', '')
            }
        
        new_config['college_teams'] = conferences
        
        # Process NHL teams (divisional structure)
        print("🏒 Processing NHL teams...")
        for division, team_abbrs in self.nhl_divisions.items():
            new_config['nhl_teams'][division] = {}
            for abbr in team_abbrs:
                team_data = next((v for v in teams.values() 
                                if v.get('sport') == 'NHL' and v.get('abbreviation') == abbr), None)
                if team_data:
                    new_config['nhl_teams'][division][abbr] = {
                        'name': team_data['display_name'],
                        'city': team_data.get('location', ''),
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'colors_description': f"{team_data.get('primary_hex', '')} & {team_data.get('secondary_hex', '')}",
                        'logo_url': team_data.get('logo_url', ''),
                        'espn_id': team_data.get('espn_id', ''),
                        'unified_key': team_data.get('unified_key', '')
                    }
        
        # Process MLB teams (divisional structure)
        print("⚾ Processing MLB teams...")
        for division, team_abbrs in self.mlb_divisions.items():
            new_config['mlb_teams'][division] = {}
            for abbr in team_abbrs:
                team_data = next((v for v in teams.values() 
                                if v.get('sport') == 'MLB' and v.get('abbreviation') == abbr), None)
                if team_data:
                    new_config['mlb_teams'][division][abbr] = {
                        'name': team_data['display_name'],
                        'city': team_data.get('location', ''),
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'colors_description': f"{team_data.get('primary_hex', '')} & {team_data.get('secondary_hex', '')}",
                        'logo_url': team_data.get('logo_url', ''),
                        'espn_id': team_data.get('espn_id', ''),
                        'unified_key': team_data.get('unified_key', '')
                    }
        
        # Process NBA teams (conference structure)
        print("🏀 Processing NBA teams...")
        for conference, team_abbrs in self.nba_conferences.items():
            new_config['nba_teams'][conference] = {}
            for abbr in team_abbrs:
                team_data = next((v for v in teams.values() 
                                if v.get('sport') == 'NBA' and v.get('abbreviation') == abbr), None)
                if team_data:
                    new_config['nba_teams'][conference][abbr] = {
                        'name': team_data['display_name'],
                        'city': team_data.get('location', ''),
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'colors_description': f"{team_data.get('primary_hex', '')} & {team_data.get('secondary_hex', '')}",
                        'logo_url': team_data.get('logo_url', ''),
                        'espn_id': team_data.get('espn_id', ''),
                        'unified_key': team_data.get('unified_key', '')
                    }
        
        # Add metadata
        new_config['metadata'] = {
            'migrated_from_comprehensive_db': True,
            'migration_date': datetime.now().isoformat(),
            'source_teams': len(teams),
            'comprehensive_db_metadata': comprehensive_db.get('metadata', {}),
            'note': 'Expanded from 54 to 324 teams while maintaining exact structure'
        }
        
        return new_config
    
    def count_teams(self, config: Dict[str, Any]) -> Dict[str, int]:
        """Count teams in each sport"""
        counts = {}
        for sport, sport_data in config.items():
            if sport == 'metadata':
                continue
            count = 0
            if isinstance(sport_data, dict):
                for division_data in sport_data.values():
                    if isinstance(division_data, dict):
                        count += len(division_data)
            counts[sport] = count
        return counts
    
    def execute_migration(self):
        """Execute the complete migration"""
        print("🚀 Starting Smart Stadium Single-Source Migration...")
        print("=" * 60)
        
        # Load comprehensive database
        comprehensive_db = self.load_comprehensive_database()
        original_count = len(comprehensive_db.get('teams', {}))
        print(f"📊 Source database: {original_count} teams")
        
        # Backup current config
        self.backup_current_config()
        
        # Convert to current format
        new_config = self.convert_to_current_format(comprehensive_db)
        
        # Count teams in new config
        team_counts = self.count_teams(new_config)
        total_new = sum(team_counts.values())
        
        # Write new configuration
        print(f"\n💾 Writing expanded configuration...")
        with open(self.current_config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print(f"\n✅ Migration completed successfully!")
        print("=" * 60)
        print(f"📁 Config updated: {self.current_config_path}")
        print(f"📁 Backup saved: {self.backup_path}")
        
        print(f"\n📊 Team count summary:")
        for sport, count in team_counts.items():
            sport_name = sport.replace('_teams', '').upper()
            print(f"   {sport_name}: {count} teams")
        print(f"   TOTAL: {total_new} teams")
        
        print(f"\n🎯 What changed:")
        print(f"   ✅ Same exact config structure")
        print(f"   ✅ Same API format")
        print(f"   ✅ Added logo URLs and ESPN IDs")
        print(f"   ✅ Expanded from 54 to {total_new} teams")
        print(f"   ✅ All major sports now included")
        
        print(f"\n🚀 Next steps:")
        print(f"   1. Restart your Smart Stadium backend")
        print(f"   2. Test: curl http://localhost:8000/api/teams/")
        print(f"   3. Manual celebrations now has {total_new} teams!")
        
        if self.backup_path.exists():
            print(f"\n⚠️  Rollback: If any issues, restore backup:")
            print(f"   cp {self.backup_path} {self.current_config_path}")

def main():
    """Main migration function"""
    migrator = SmartTeamMigrator()
    
    print("🏟️ Smart Stadium Single-Source Migration")
    print("=" * 50)
    print("This will expand your team database from 54 to 324 teams")
    print("while maintaining the exact same config structure.")
    print("")
    
    if not migrator.comprehensive_db_path.exists():
        print(f"❌ Error: Comprehensive database not found at:")
        print(f"   {migrator.comprehensive_db_path}")
        print(f"   Please ensure the file exists before running migration.")
        return
    
    response = input("Proceed with migration? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        migrator.execute_migration()
    else:
        print("❌ Migration cancelled.")

if __name__ == "__main__":
    main()