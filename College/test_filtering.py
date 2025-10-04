#!/usr/bin/env python3
"""
Test the fixed game filtering logic directly
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from college_game_monitor import CollegeGameMonitor

async def test_game_filtering():
    """Test if Alabama and South Carolina games are now properly included"""
    print("🧪 Testing fixed game filtering logic...")
    
    # Initialize with dummy light IPs for testing
    monitor = CollegeGameMonitor(['192.168.86.41', '192.168.86.47'])
    games = await monitor.get_available_games()
    
    print(f"\n📊 Total games found: {len(games)}")
    
    # Look for Alabama and South Carolina
    alabama_found = False
    sc_found = False
    
    for i, game in enumerate(games, 1):
        home_team = game['home_team']
        away_team = game['away_team']
        status = game['display_status']
        
        # Check for target games
        if "Alabama" in home_team or "Alabama" in away_team:
            print(f"\n⭐ FOUND ALABAMA: {away_team} @ {home_team}")
            print(f"   Status: {status}")
            print(f"   Raw Status: {game['status']}")
            alabama_found = True
            
        if "South Carolina" in home_team or "South Carolina" in away_team:
            print(f"\n⭐ FOUND SOUTH CAROLINA: {away_team} @ {home_team}")
            print(f"   Status: {status}")
            print(f"   Raw Status: {game['status']}")
            sc_found = True
    
    print(f"\n🎯 Results:")
    print(f"   Alabama found: {'✅' if alabama_found else '❌'}")
    print(f"   South Carolina found: {'✅' if sc_found else '❌'}")
    
    if not alabama_found or not sc_found:
        print(f"\n📋 All games in list:")
        for i, game in enumerate(games, 1):
            print(f"   {i:2d}. {game['away_team']:25} @ {game['home_team']:25} {game['display_status']}")

if __name__ == "__main__":
    asyncio.run(test_game_filtering())