#!/usr/bin/env python3
"""
Smart Stadium Team Database Integration Script
Migrates from 54-team manual config to 324-team comprehensive ESPN database
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class TeamDatabaseMigrator:
    """Migrate Smart Stadium to use comprehensive team database"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.comprehensive_db_path = self.root_path / "src" / "comprehensive_sports_database.json"
        self.current_config_path = self.root_path / "config" / "team_colors.json"
        self.backup_path = self.root_path / "config" / f"team_colors_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def load_comprehensive_database(self) -> Dict[str, Any]:
        """Load the comprehensive sports database"""
        with open(self.comprehensive_db_path, 'r') as f:
            return json.load(f)
    
    def create_mapping_layer(self, comprehensive_db: Dict[str, Any]) -> Dict[str, Any]:
        """Create mapping from unified keys to current abbreviation system"""
        teams = comprehensive_db.get('teams', {})
        
        # Sport mappings for backward compatibility
        sport_mapping = {
            'NFL': 'nfl_teams',
            'CFB': 'college_teams', 
            'NHL': 'nhl_teams',
            'MLB': 'mlb_teams',
            'NBA': 'nba_teams'
        }
        
        # Division mappings for NFL (to maintain current structure)
        nfl_divisions = {
            'AFC_East': ['BUF', 'MIA', 'NE', 'NYJ'],
            'AFC_North': ['BAL', 'CIN', 'CLE', 'PIT'],
            'AFC_South': ['HOU', 'IND', 'JAX', 'TEN'],
            'AFC_West': ['DEN', 'KC', 'LV', 'LAC'],
            'NFC_East': ['DAL', 'NYG', 'PHI', 'WAS'],
            'NFC_North': ['CHI', 'DET', 'GB', 'MIN'],
            'NFC_South': ['ATL', 'CAR', 'NO', 'TB'],
            'NFC_West': ['ARI', 'LAR', 'SF', 'SEA']
        }
        
        # Create new structure compatible with current system
        new_config = {}
        
        for sport_key, sport_name in sport_mapping.items():
            sport_teams = {k: v for k, v in teams.items() if v['sport'] == sport_key}
            
            if sport_key == 'NFL':
                # Maintain divisional structure for NFL
                new_config[sport_name] = {}
                for division, team_abbrs in nfl_divisions.items():
                    new_config[sport_name][division] = {}
                    for abbr in team_abbrs:
                        # Find team by abbreviation
                        team_data = next((v for v in sport_teams.values() if v['abbreviation'] == abbr), None)
                        if team_data:
                            new_config[sport_name][division][abbr] = {
                                'name': team_data['display_name'],
                                'city': team_data['location'],
                                'primary_color': team_data['primary_color'],
                                'secondary_color': team_data['secondary_color'],
                                'primary_hex': team_data['primary_hex'],
                                'secondary_hex': team_data['secondary_hex'],
                                'logo_url': team_data['logo_url'],
                                'espn_id': team_data['espn_id'],
                                'unified_key': team_data['unified_key'],
                                'colors_description': f"{team_data['primary_hex']} & {team_data['secondary_hex']}"
                            }
            
            elif sport_key == 'CFB':
                # Group college teams by major conferences
                new_config[sport_name] = {}
                conferences = {}
                
                for unified_key, team_data in sport_teams.items():
                    # Use location as conference grouping for now
                    conference = team_data.get('location', 'Independent')
                    if conference not in conferences:
                        conferences[conference] = {}
                    
                    # Use display name as key for college teams (like current system)
                    team_name = team_data['display_name'].replace(' ', '_').upper()
                    conferences[conference][team_name] = {
                        'name': team_data['display_name'],
                        'abbreviation': team_data['abbreviation'],
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'primary_hex': team_data['primary_hex'],
                        'secondary_hex': team_data['secondary_hex'],
                        'logo_url': team_data['logo_url'],
                        'espn_id': team_data['espn_id'],
                        'unified_key': team_data['unified_key'],
                        'colors_description': f"{team_data['primary_hex']} & {team_data['secondary_hex']}"
                    }
                
                new_config[sport_name] = conferences
            
            else:
                # For NHL, MLB, NBA - create simple flat structure
                new_config[sport_name] = {}
                for unified_key, team_data in sport_teams.items():
                    abbr = team_data['abbreviation']
                    new_config[sport_name][abbr] = {
                        'name': team_data['display_name'],
                        'city': team_data['location'],
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'primary_hex': team_data['primary_hex'],
                        'secondary_hex': team_data['secondary_hex'],
                        'logo_url': team_data['logo_url'],
                        'espn_id': team_data['espn_id'],
                        'unified_key': team_data['unified_key'],
                        'colors_description': f"{team_data['primary_hex']} & {team_data['secondary_hex']}"
                    }
        
        # Add metadata
        new_config['metadata'] = {
            'migrated_from_comprehensive_db': True,
            'migration_date': datetime.now().isoformat(),
            'total_teams': len(teams),
            'sports_included': list(sport_mapping.keys()),
            'source_database': str(self.comprehensive_db_path),
            'comprehensive_db_metadata': comprehensive_db.get('metadata', {})
        }
        
        return new_config
    
    def backup_current_config(self):
        """Backup current team colors configuration"""
        if self.current_config_path.exists():
            shutil.copy2(self.current_config_path, self.backup_path)
            print(f"✅ Backed up current config to: {self.backup_path}")
    
    def migrate_database(self):
        """Perform the complete migration"""
        print("🚀 Starting Smart Stadium team database migration...")
        print(f"📊 Current teams: 54 (estimated)")
        print(f"📈 New teams: 324 (NFL: 32, CFB: 200, NHL: 32, MLB: 30, NBA: 30)")
        
        # Load comprehensive database
        print("\n📥 Loading comprehensive sports database...")
        comprehensive_db = self.load_comprehensive_database()
        
        # Backup current config
        print("\n💾 Creating backup of current configuration...")
        self.backup_current_config()
        
        # Create new structure
        print("\n🔄 Converting database structure...")
        new_config = self.create_mapping_layer(comprehensive_db)
        
        # Write new configuration
        print("\n💾 Writing new team configuration...")
        with open(self.current_config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print(f"\n✅ Migration complete!")
        print(f"📁 New config saved to: {self.current_config_path}")
        print(f"📁 Backup saved to: {self.backup_path}")
        
        # Summary
        sports_count = new_config.get('metadata', {}).get('comprehensive_db_metadata', {}).get('sports_count', {})
        print(f"\n📊 Team count summary:")
        for sport, count in sports_count.items():
            print(f"   {sport}: {count} teams")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Restart your Smart Stadium backend")
        print(f"   2. Test /api/teams endpoint to see all 324 teams")
        print(f"   3. Update frontend to handle logo URLs if desired")
        print(f"   4. Test manual celebrations with expanded team selection")

def main():
    """Main migration function"""
    migrator = TeamDatabaseMigrator()
    
    # Confirm migration
    print("🏟️ Smart Stadium Team Database Migration")
    print("=" * 50)
    print("This will replace your current 54-team configuration")
    print("with the comprehensive 324-team ESPN database.")
    print("")
    response = input("Continue with migration? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        migrator.migrate_database()
    else:
        print("❌ Migration cancelled.")

if __name__ == "__main__":
    main()