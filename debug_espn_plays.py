#!/usr/bin/env python3
"""Debug script to examine ESPN API play type responses."""

import asyncio
import json
from datetime import datetime
from app.services.espn_client import EspnScoreboardClient
from app.models.game import Sport

async def debug_espn_plays():
    """Fetch current games and examine play type data."""
    client = EspnScoreboardClient()
    
    print("🏈 Fetching NFL scoreboard to examine play types...")
    try:
        scoreboard = await client.fetch_scoreboard(Sport.NFL)
        
        # Our current detection mappings
        defensive_type_mapping = {
            "8": "sack",
            "26": "interception", 
            "52": "fumble_recovery",
            "53": "fumble",
            "54": "safety",
            "27": "interception",  # Interception return TD
            "28": "fumble_recovery",  # Fumble return TD
        }
        
        plays_found = []
        
        for game in scoreboard.games:
            print(f"\n📊 Game: {game.away.abbreviation} @ {game.home.abbreviation}")
            print(f"   Status: {game.status.value}")
            
            if game.last_play:
                play_data = {
                    "game": f"{game.away.abbreviation} @ {game.home.abbreviation}",
                    "play_id": game.last_play.play_id,
                    "play_type_id": game.last_play.play_type_id,
                    "play_type_name": game.last_play.play_type_name,
                    "team_id": game.last_play.team_id,
                    "description": game.last_play.description,
                    "score_value": game.last_play.score_value,
                    "timestamp": datetime.now().isoformat()
                }
                plays_found.append(play_data)
                
                print(f"   Last Play ID: {game.last_play.play_id}")
                print(f"   Play Type ID: {game.last_play.play_type_id}")
                print(f"   Play Type Name: {game.last_play.play_type_name}")
                print(f"   Team ID: {game.last_play.team_id}")
                print(f"   Description: {game.last_play.description}")
                print(f"   Score Value: {game.last_play.score_value}")
                
                # Check our detection logic
                play_type_id = game.last_play.play_type_id
                description = game.last_play.description or ""
                description_lower = description.lower()
                
                detected_by_id = defensive_type_mapping.get(play_type_id)
                detected_by_sack_keywords = any(keyword in description_lower for keyword in ["sack", "sacked"])
                detected_by_int_keywords = any(keyword in description_lower for keyword in ["interception", "intercepted", "int "])
                detected_by_fumble_keywords = "fumble" in description_lower and any(keyword in description_lower for keyword in ["recover", "recovery"])
                detected_by_safety_keywords = "safety" in description_lower
                
                any_detection = detected_by_id or detected_by_sack_keywords or detected_by_int_keywords or detected_by_fumble_keywords or detected_by_safety_keywords
                
                if any_detection:
                    print(f"   🚨 DEFENSIVE PLAY DETECTED:")
                    print(f"      By ID ({play_type_id}): {detected_by_id}")
                    print(f"      By Sack Keywords: {detected_by_sack_keywords}")
                    print(f"      By Int Keywords: {detected_by_int_keywords}")
                    print(f"      By Fumble Keywords: {detected_by_fumble_keywords}")
                    print(f"      By Safety Keywords: {detected_by_safety_keywords}")
                    
            else:
                print("   No last play data available")
        
        # Save all play data for analysis
        if plays_found:
            with open("espn_play_debug.json", "w") as f:
                json.dump(plays_found, f, indent=2)
            print(f"\n💾 Saved {len(plays_found)} plays to espn_play_debug.json")
        
        # Show known play type mapping
        print("\n📋 Our Current Play Type ID Mapping:")
        for type_id, event_type in defensive_type_mapping.items():
            print(f"   {type_id}: {event_type}")
                
    except Exception as e:
        print(f"❌ Error fetching scoreboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_espn_plays())