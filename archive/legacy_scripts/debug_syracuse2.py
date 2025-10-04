#!/usr/bin/env python3
"""
Debug script to check Syracuse processing in migration
"""

import json
from pathlib import Path

# Load comprehensive database
db_path = Path("src/comprehensive_sports_database.json")
with open(db_path, 'r') as f:
    comprehensive_db = json.load(f)

# Extract teams like the migration script does
teams = comprehensive_db.get('teams', {})

print(f"Total teams in database: {len(teams)}")

# Find Syracuse
syracuse_teams = {k: v for k, v in teams.items() if 'Syracuse' in v.get('display_name', '')}

print(f"Syracuse teams found: {len(syracuse_teams)}")
for key, team in syracuse_teams.items():
    print(f"Key: {key}")
    print(f"Display name: {team.get('display_name')}")
    print(f"Sport: {team.get('sport')}")
    print(f"Abbreviation: {team.get('abbreviation')}")
    print("---")

# Check CFB teams
cfb_teams = {k: v for k, v in teams.items() if v.get('sport') == 'CFB'}
print(f"CFB teams found: {len(cfb_teams)}")

# Check if Syracuse would be in the conference mapping
conference_map = {
    'Syracuse Orange': 'ACC',
}

syracuse_cfb = {k: v for k, v in cfb_teams.items() if 'Syracuse' in v.get('display_name', '')}
print(f"Syracuse CFB teams: {len(syracuse_cfb)}")

if syracuse_cfb:
    for key, team in syracuse_cfb.items():
        team_name = team.get('display_name')
        mapped_conference = conference_map.get(team_name, 'Other')
        print(f"Syracuse CFB: {team_name}")
        print(f"  Would map to conference: {mapped_conference}")
        print(f"  Abbreviation: {team.get('abbreviation')}")