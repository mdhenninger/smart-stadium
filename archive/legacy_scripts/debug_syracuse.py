#!/usr/bin/env python3
"""
Debug script to check Syracuse processing
"""

import json
from pathlib import Path

# Load comprehensive database
db_path = Path("src/comprehensive_sports_database.json")
with open(db_path, 'r') as f:
    db = json.load(f)

# Find Syracuse
syracuse_teams = {k: v for k, v in db.items() if 'Syracuse' in v.get('display_name', '')}

print("Syracuse teams found:")
for key, team in syracuse_teams.items():
    print(f"Key: {key}")
    print(f"Display name: {team.get('display_name')}")
    print(f"Sport: {team.get('sport')}")
    print(f"Abbreviation: {team.get('abbreviation')}")
    print(f"Location: {team.get('location')}")
    print("---")

# Check if it's being filtered correctly
cfb_teams = {k: v for k, v in db.items() if v.get('sport') == 'CFB'}
syracuse_cfb = {k: v for k, v in cfb_teams.items() if 'Syracuse' in v.get('display_name', '')}

print(f"\nCFB teams total: {len(cfb_teams)}")
print(f"Syracuse CFB teams: {len(syracuse_cfb)}")

if syracuse_cfb:
    for key, team in syracuse_cfb.items():
        print(f"Syracuse CFB found: {team.get('display_name')}")
        print(f"  Abbreviation: {team.get('abbreviation')}")