#!/usr/bin/env python3
"""Validate enhanced teams database structure and data integrity."""

import json
from pathlib import Path
from typing import Dict, Any, List

def validate_teams_database(db_path: Path) -> Dict[str, Any]:
    """Comprehensive validation of teams database."""
    
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    # Load database
    try:
        with open(db_path) as f:
            db = json.load(f)
    except FileNotFoundError:
        results["valid"] = False
        results["errors"].append(f"Database file not found: {db_path}")
        return results
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Failed to load database: {e}")
        return results
    
    # Validate structure
    if "teams" not in db:
        results["valid"] = False
        results["errors"].append("Missing 'teams' key")
        return results
    
    teams = db["teams"]
    results["stats"]["total_teams"] = len(teams)
    
    # Track for uniqueness checks
    abbreviations_by_sport: Dict[str, List[str]] = {}
    espn_ids = []
    teams_with_lighting_colors = 0
    
    # Validate each team
    for unified_key, team in teams.items():
        # Required fields
        required = [
            "sport", "abbreviation", "display_name", "nickname", "location",
            "primary_color", "secondary_color", "primary_hex", "secondary_hex",
            "logo_url", "espn_id"
        ]
        for field in required:
            if field not in team:
                results["errors"].append(f"{unified_key}: Missing required field '{field}'")
                results["valid"] = False
        
        # Validate color arrays
        for color_field in ["primary_color", "secondary_color"]:
            if color_field in team:
                color = team[color_field]
                if not isinstance(color, list) or len(color) != 3:
                    results["errors"].append(f"{unified_key}: {color_field} must be RGB array [r,g,b]")
                    results["valid"] = False
                elif not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                    results["errors"].append(f"{unified_key}: {color_field} values must be 0-255")
                    results["valid"] = False
        
        # Validate lighting colors if present
        has_lighting_colors = True
        for color_field in ["lighting_primary_color", "lighting_secondary_color"]:
            if color_field in team:
                color = team[color_field]
                if not isinstance(color, list) or len(color) != 3:
                    results["errors"].append(f"{unified_key}: {color_field} must be RGB array")
                    results["valid"] = False
                    has_lighting_colors = False
                elif not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                    results["errors"].append(f"{unified_key}: {color_field} values must be 0-255")
                    results["valid"] = False
                    has_lighting_colors = False
            else:
                has_lighting_colors = False
        
        if has_lighting_colors:
            teams_with_lighting_colors += 1
        
        # Validate hex colors
        for hex_field in ["primary_hex", "secondary_hex"]:
            if hex_field in team:
                hex_val = team[hex_field]
                if not isinstance(hex_val, str) or not hex_val.startswith("#") or len(hex_val) != 7:
                    results["errors"].append(f"{unified_key}: {hex_field} must be #RRGGBB format")
                    results["valid"] = False
        
        # Validate lighting hex colors if present
        for hex_field in ["lighting_primary_hex", "lighting_secondary_hex"]:
            if hex_field in team:
                hex_val = team[hex_field]
                if not isinstance(hex_val, str) or not hex_val.startswith("#") or len(hex_val) != 7:
                    results["warnings"].append(f"{unified_key}: {hex_field} must be #RRGGBB format")
        
        # Validate RGB to hex consistency
        if "primary_color" in team and "primary_hex" in team:
            rgb = team["primary_color"]
            expected_hex = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            if team["primary_hex"] != expected_hex:
                results["warnings"].append(
                    f"{unified_key}: primary_hex mismatch. Expected {expected_hex}, got {team['primary_hex']}"
                )
        
        # Track abbreviations by sport
        if "sport" in team and "abbreviation" in team:
            sport = team["sport"]
            abbr = team["abbreviation"]
            if sport not in abbreviations_by_sport:
                abbreviations_by_sport[sport] = []
            abbreviations_by_sport[sport].append(abbr)
        
        # Track ESPN IDs
        if "espn_id" in team:
            espn_ids.append(team["espn_id"])
    
    # Check for duplicate abbreviations within sport
    for sport, abbrs in abbreviations_by_sport.items():
        duplicates = [a for a in set(abbrs) if abbrs.count(a) > 1]
        if duplicates:
            results["warnings"].append(f"{sport}: Duplicate abbreviations: {duplicates}")
    
    # Check for duplicate ESPN IDs
    duplicate_ids = [eid for eid in set(espn_ids) if espn_ids.count(eid) > 1]
    if duplicate_ids:
        results["warnings"].append(f"Duplicate ESPN IDs: {duplicate_ids}")
    
    # Stats by sport
    results["stats"]["by_sport"] = {}
    for sport in sorted(abbreviations_by_sport.keys()):
        results["stats"]["by_sport"][sport] = len(abbreviations_by_sport[sport])
    
    results["stats"]["teams_with_lighting_colors"] = teams_with_lighting_colors
    
    # Check for Bills optimized colors
    bills_key = "NFL-BUFFALO-BILLS"
    if bills_key in teams:
        bills = teams[bills_key]
        if "lighting_primary_color" in bills and "lighting_secondary_color" in bills:
            lp = bills["lighting_primary_color"]
            ls = bills["lighting_secondary_color"]
            # Check if they're different from official colors (indicating optimization)
            op = bills["primary_color"]
            os = bills["secondary_color"]
            if lp != op or ls != os:
                results["stats"]["bills_optimized"] = True
                results["stats"]["bills_lighting_colors"] = {
                    "primary": lp,
                    "secondary": ls
                }
            else:
                results["warnings"].append("Bills lighting colors same as official (not optimized)")
                results["stats"]["bills_optimized"] = False
        else:
            results["warnings"].append("Bills missing lighting-optimized colors")
            results["stats"]["bills_optimized"] = False
    else:
        results["errors"].append("Bills team not found in database!")
        results["valid"] = False
    
    return results

def print_results(results: Dict[str, Any]) -> None:
    """Pretty print validation results."""
    print("=" * 60)
    print("🔍 TEAMS DATABASE VALIDATION REPORT")
    print("=" * 60)
    print(f"\n{'✅ VALID' if results['valid'] else '❌ INVALID'}")
    
    if results["stats"]:
        print("\n📊 Statistics:")
        for key, value in results["stats"].items():
            if key == "by_sport":
                print(f"  Teams by sport:")
                for sport, count in value.items():
                    print(f"    {sport}: {count}")
            elif key == "bills_lighting_colors":
                print(f"  Bills lighting colors:")
                print(f"    Primary: {value['primary']}")
                print(f"    Secondary: {value['secondary']}")
            else:
                print(f"  {key}: {value}")
    
    if results["errors"]:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for i, error in enumerate(results["errors"][:20], 1):  # Limit to first 20
            print(f"  {i}. {error}")
        if len(results["errors"]) > 20:
            print(f"  ... and {len(results['errors']) - 20} more errors")
    
    if results["warnings"]:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for i, warning in enumerate(results["warnings"][:20], 1):  # Limit to first 20
            print(f"  {i}. {warning}")
        if len(results["warnings"]) > 20:
            print(f"  ... and {len(results['warnings']) - 20} more warnings")
    
    if results["valid"]:
        print("\n✅ Database is valid and ready for migration!")
    else:
        print("\n❌ Database has errors - fix before migration")
    
    print("=" * 60)

if __name__ == "__main__":
    db_path = Path(__file__).parent / "config" / "teams_database.json"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("💡 Run create_enhanced_teams_database.py first")
        exit(1)
    
    results = validate_teams_database(db_path)
    print_results(results)
    
    exit(0 if results["valid"] else 1)
