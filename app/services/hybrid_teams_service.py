"""
Hybrid Teams Service - Safe Integration of Comprehensive Database
Adds 324 teams WITHOUT breaking existing 54-team system
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from app.models.api import TeamOption, TeamColors

class HybridTeamsService:
    """Service that safely merges current config with comprehensive database"""
    
    def __init__(self, config_dir: Path, src_dir: Path):
        self.config_dir = config_dir
        self.src_dir = src_dir
        self._current_config = None
        self._comprehensive_db = None
        self._team_index = None
    
    def _load_current_config(self) -> Dict[str, Any]:
        """Load current team_colors.json"""
        if self._current_config is None:
            config_path = self.config_dir / "team_colors.json"
            with open(config_path, 'r') as f:
                self._current_config = json.load(f)
        return self._current_config
    
    def _load_comprehensive_db(self) -> Dict[str, Any]:
        """Load comprehensive_sports_database.json"""
        if self._comprehensive_db is None:
            db_path = self.src_dir / "comprehensive_sports_database.json"
            with open(db_path, 'r') as f:
                self._comprehensive_db = json.load(f)
        return self._comprehensive_db
    
    def _build_team_index(self) -> Dict[str, Any]:
        """Build unified index of all teams from both sources"""
        if self._team_index is not None:
            return self._team_index
        
        current = self._load_current_config()
        comprehensive = self._load_comprehensive_db()
        
        index = {
            'by_sport': {},
            'by_abbreviation': {},
            'by_unified_key': {},
            'sources': {}
        }
        
        # Index current config teams (priority source)
        sport_mapping = {
            "nfl_teams": "nfl",
            "college_teams": "cfb", 
            "nhl_teams": "nhl",
            "nba_teams": "nba",
            "mlb_teams": "mlb"
        }
        
        for sport_key, sport_data in current.items():
            if sport_key not in sport_mapping:
                continue
                
            sport_code = sport_mapping[sport_key]
            if sport_code not in index['by_sport']:
                index['by_sport'][sport_code] = []
            
            # Process divisions in current config
            for division_key, division_data in sport_data.items():
                if not isinstance(division_data, dict):
                    continue
                    
                for team_abbr, team_data in division_data.items():
                    if not isinstance(team_data, dict) or 'primary_color' not in team_data:
                        continue
                    
                    team_entry = {
                        'source': 'current_config',
                        'sport': sport_code,
                        'abbreviation': team_abbr,
                        'name': team_data.get('name', f'Unknown {team_abbr}'),
                        'city': team_data.get('city'),
                        'division': division_key,
                        'primary_color': team_data['primary_color'],
                        'secondary_color': team_data['secondary_color'],
                        'lighting_primary_color': team_data.get('lighting_primary_color'),
                        'lighting_secondary_color': team_data.get('lighting_secondary_color'),
                        'colors_description': team_data.get('colors_description'),
                        'unified_key': f"{sport_code.upper()}-{team_abbr}"
                    }
                    
                    index['by_sport'][sport_code].append(team_entry)
                    index['by_abbreviation'][f"{sport_code}:{team_abbr}"] = team_entry
                    index['sources'][f"{sport_code}:{team_abbr}"] = 'current_config'
        
        # Add comprehensive database teams (for teams NOT in current config)
        comprehensive_teams = comprehensive.get('teams', {})
        
        for unified_key, team_data in comprehensive_teams.items():
            sport = team_data['sport'].lower()
            sport_map = {'nfl': 'nfl', 'cfb': 'cfb', 'nhl': 'nhl', 'mlb': 'mlb', 'nba': 'nba'}
            sport_code = sport_map.get(sport)
            
            if not sport_code:
                continue
            
            abbr = team_data.get('abbreviation', '')
            team_key = f"{sport_code}:{abbr}"
            
            # Skip if we already have this team from current config
            if team_key in index['by_abbreviation']:
                continue
            
            if sport_code not in index['by_sport']:
                index['by_sport'][sport_code] = []
            
            team_entry = {
                'source': 'comprehensive_db',
                'sport': sport_code,
                'abbreviation': abbr,
                'name': team_data.get('display_name', ''),
                'city': team_data.get('location', ''),
                'division': 'Additional',  # Group new teams
                'primary_color': team_data.get('primary_color', [128, 128, 128]),
                'secondary_color': team_data.get('secondary_color', [64, 64, 64]),
                'primary_hex': team_data.get('primary_hex'),
                'secondary_hex': team_data.get('secondary_hex'),
                'logo_url': team_data.get('logo_url'),
                'espn_id': team_data.get('espn_id'),
                'unified_key': unified_key
            }
            
            index['by_sport'][sport_code].append(team_entry)
            index['by_abbreviation'][team_key] = team_entry
            index['by_unified_key'][unified_key] = team_entry
            index['sources'][team_key] = 'comprehensive_db'
        
        self._team_index = index
        return index
    
    def get_teams(self, sport: Optional[str] = None) -> List[TeamOption]:
        """Get all teams, optionally filtered by sport"""
        index = self._build_team_index()
        teams = []
        
        # Determine which sports to include
        if sport:
            sports_to_include = [sport.lower()]
        else:
            sports_to_include = list(index['by_sport'].keys())
        
        for sport_code in sports_to_include:
            sport_teams = index['by_sport'].get(sport_code, [])
            
            for team_entry in sport_teams:
                # Build colors object
                primary = team_entry['primary_color']
                secondary = team_entry['secondary_color']
                lighting_primary = team_entry.get('lighting_primary_color')
                lighting_secondary = team_entry.get('lighting_secondary_color')
                
                colors = TeamColors(
                    primary=tuple(primary),
                    secondary=tuple(secondary),
                    lighting_primary=tuple(lighting_primary) if lighting_primary else None,
                    lighting_secondary=tuple(lighting_secondary) if lighting_secondary else None
                )
                
                # Create team option
                team_key = f"{sport_code}:{team_entry['abbreviation']}"
                sport_display = sport_code.upper()
                label = f"{team_entry['name']} ({sport_display})" if not sport else team_entry['name']
                
                team_option = TeamOption(
                    value=team_key,
                    label=label,
                    abbreviation=team_entry['abbreviation'],
                    name=team_entry['name'],
                    sport=sport_code,
                    city=team_entry.get('city'),
                    colors=colors
                )
                
                # Add enhanced fields if available
                if 'logo_url' in team_entry:
                    team_option.logo_url = team_entry['logo_url']
                if 'espn_id' in team_entry:
                    team_option.espn_id = team_entry['espn_id']
                if 'nickname' in team_entry:
                    team_option.nickname = team_entry.get('nickname')
                
                teams.append(team_option)
        
        # Sort teams: by sport first, then by name
        teams.sort(key=lambda t: (t.sport, t.name))
        return teams
    
    def get_team_stats(self) -> Dict[str, Any]:
        """Get statistics about the hybrid team database"""
        index = self._build_team_index()
        
        stats = {
            'total_teams': 0,
            'by_sport': {},
            'by_source': {'current_config': 0, 'comprehensive_db': 0}
        }
        
        for sport_code, sport_teams in index['by_sport'].items():
            stats['by_sport'][sport_code] = len(sport_teams)
            stats['total_teams'] += len(sport_teams)
            
            for team in sport_teams:
                source = team['source']
                stats['by_source'][source] += 1
        
        return stats

# Function to integrate with existing teams API
def create_hybrid_teams_service(config_dir: Path, src_dir: Path) -> HybridTeamsService:
    """Factory function to create hybrid teams service"""
    return HybridTeamsService(config_dir, src_dir)