#!/usr/bin/env python3
"""
Create Enhanced Teams Database
Converts comprehensive_sports_database.json to enhanced format with lighting-optimized colors
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def rgb_to_hex(rgb: list) -> str:
    """Convert RGB array [r,g,b] to hex string #RRGGBB"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def create_enhanced_database():
    """Create enhanced teams database with lighting-optimized colors."""
    
    # Paths
    root = Path(__file__).parent
    source_path = root / "src" / "comprehensive_sports_database.json"
    output_path = root / "config" / "teams_database.json"
    current_config_path = root / "config" / "team_colors.json"
    
    print("🏗️  Creating Enhanced Teams Database")
    print("=" * 60)
    
    # Load source database
    print(f"📂 Loading source: {source_path}")
    with open(source_path) as f:
        source_db = json.load(f)
    
    # Load current config for Bills optimized colors
    print(f"📂 Loading current config for Bills colors: {current_config_path}")
    with open(current_config_path) as f:
        current_config = json.load(f)
    
    # Extract Bills optimized colors
    bills_lighting_primary = None
    bills_lighting_secondary = None
    try:
        bills_data = current_config["nfl_teams"]["AFC_East"]["BUF"]
        bills_lighting_primary = bills_data.get("lighting_primary_color")
        bills_lighting_secondary = bills_data.get("lighting_secondary_color")
        if bills_lighting_primary and bills_lighting_secondary:
            print(f"✅ Found Bills optimized colors: {bills_lighting_primary} / {bills_lighting_secondary}")
        else:
            print("⚠️  Bills optimized colors not found in current config")
    except KeyError:
        print("⚠️  Could not extract Bills colors from current config")
    
    # Create enhanced database
    enhanced_db = {
        "metadata": {
            "version": "2.0.0",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_teams": len(source_db["teams"]),
            "description": "Enhanced teams database with lighting-optimized colors",
            "sports": source_db["metadata"]["sports_count"]
        },
        "teams": {}
    }
    
    # Process each team
    print(f"\n🔄 Processing {len(source_db['teams'])} teams...")
    for unified_key, team_data in source_db["teams"].items():
        # Copy all original fields
        enhanced_team = team_data.copy()
        
        # Fix hex colors if missing # prefix
        if "primary_hex" in enhanced_team and not enhanced_team["primary_hex"].startswith("#"):
            enhanced_team["primary_hex"] = "#" + enhanced_team["primary_hex"]
        if "secondary_hex" in enhanced_team and not enhanced_team["secondary_hex"].startswith("#"):
            enhanced_team["secondary_hex"] = "#" + enhanced_team["secondary_hex"]
        
        # Add lighting colors (initially same as official)
        primary = team_data["primary_color"]
        secondary = team_data["secondary_color"]
        
        enhanced_team["lighting_primary_color"] = primary.copy()
        enhanced_team["lighting_secondary_color"] = secondary.copy()
        
        # Calculate hex versions of lighting colors
        enhanced_team["lighting_primary_hex"] = rgb_to_hex(primary)
        enhanced_team["lighting_secondary_hex"] = rgb_to_hex(secondary)
        
        # Special case: Override Bills with optimized colors
        if unified_key == "NFL-BUFFALO-BILLS" and bills_lighting_primary and bills_lighting_secondary:
            enhanced_team["lighting_primary_color"] = bills_lighting_primary
            enhanced_team["lighting_secondary_color"] = bills_lighting_secondary
            enhanced_team["lighting_primary_hex"] = rgb_to_hex(bills_lighting_primary)
            enhanced_team["lighting_secondary_hex"] = rgb_to_hex(bills_lighting_secondary)
            print(f"  ⚡ Bills: Applied optimized colors")
        
        enhanced_db["teams"][unified_key] = enhanced_team
    
    # Write output
    print(f"\n💾 Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_db, f, indent=2, ensure_ascii=False)
    
    # Statistics
    stats_by_sport = {}
    for team in enhanced_db["teams"].values():
        sport = team["sport"]
        stats_by_sport[sport] = stats_by_sport.get(sport, 0) + 1
    
    print("\n✅ Enhanced Database Created Successfully!")
    print("=" * 60)
    print(f"📊 Statistics:")
    print(f"  Total teams: {len(enhanced_db['teams'])}")
    for sport, count in sorted(stats_by_sport.items()):
        print(f"  {sport}: {count} teams")
    print(f"\n📁 Output: {output_path}")
    print(f"💾 Size: {output_path.stat().st_size / 1024:.1f} KB")
    
    return enhanced_db

if __name__ == "__main__":
    create_enhanced_database()
