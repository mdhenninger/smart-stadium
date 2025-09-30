"""
Team Colors Configuration Loader
Loads team colors from JSON configuration files
"""

import json
import os
from typing import Dict, Tuple

def load_team_colors() -> Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
    """Load team colors from JSON configuration"""
    config_path = os.path.join(os.path.dirname(__file__), 'team_colors.json')
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        # Convert NFL teams to the format expected by the system
        nfl_colors = {}
        nfl_teams = data.get('nfl_teams', {})
        
        for division in nfl_teams.values():
            for team_abbr, team_data in division.items():
                primary = tuple(team_data['primary_color'])
                secondary = tuple(team_data['secondary_color'])
                nfl_colors[team_abbr] = (primary, secondary)
        
        return nfl_colors
        
    except FileNotFoundError:
        print(f"❌ Team colors config file not found at {config_path}")
        return {}
    except Exception as e:
        print(f"❌ Error loading team colors: {e}")
        return {}

def get_team_name(team_abbr: str) -> str:
    """Get full team name from abbreviation"""
    config_path = os.path.join(os.path.dirname(__file__), 'team_colors.json')
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        # Search through NFL teams
        nfl_teams = data.get('nfl_teams', {})
        for division in nfl_teams.values():
            if team_abbr in division:
                return division[team_abbr]['name']
        
        return team_abbr  # Fallback to abbreviation
        
    except:
        return team_abbr

# Load NFL team colors for backward compatibility
NFL_TEAM_COLORS = load_team_colors()