#!/usr/bin/env python3
"""
Test script to measure ESPN API update delay.
Run this during a live game to see how quickly ESPN updates their API.
"""

import asyncio
import sys
from datetime import datetime
import httpx

async def monitor_espn_delay(sport="college-football", poll_interval=2):
    """
    Monitor ESPN API for score changes and measure delay.
    
    Args:
        sport: "nfl" or "college-football"
        poll_interval: How often to poll in seconds
    """
    base_url = f"http://site.api.espn.com/apis/site/v2/sports/football/{sport}/scoreboard"
    last_scores = {}
    
    print(f"🏈 Monitoring ESPN {sport} API (polling every {poll_interval}s)")
    print(f"📡 URL: {base_url}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"\n{'='*80}\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        iteration = 0
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            try:
                response = await client.get(base_url)
                data = response.json()
                
                if "events" not in data:
                    print(f"[{timestamp}] ⚠️  No events found in API response")
                    await asyncio.sleep(poll_interval)
                    continue
                
                # Process each game
                for event in data["events"]:
                    game_id = event.get("id")
                    status = event.get("status", {}).get("type", {}).get("name", "Unknown")
                    
                    competitions = event.get("competitions", [])
                    if not competitions:
                        continue
                    
                    comp = competitions[0]
                    competitors = comp.get("competitors", [])
                    
                    if len(competitors) != 2:
                        continue
                    
                    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
                    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
                    
                    if not home or not away:
                        continue
                    
                    home_abbr = home.get("team", {}).get("abbreviation", "???")
                    away_abbr = away.get("team", {}).get("abbreviation", "???")
                    home_score = int(home.get("score", 0))
                    away_score = int(away.get("score", 0))
                    
                    # Initialize last scores
                    if game_id not in last_scores:
                        last_scores[game_id] = {
                            "home_abbr": home_abbr,
                            "away_abbr": away_abbr,
                            "home_score": home_score,
                            "away_score": away_score,
                        }
                        if status == "in":
                            print(f"[{timestamp}] 🎮 Tracking: {away_abbr} @ {home_abbr} ({away_score}-{home_score}) - {status}")
                        continue
                    
                    # Check for score changes
                    last = last_scores[game_id]
                    home_delta = home_score - last["home_score"]
                    away_delta = away_score - last["away_score"]
                    
                    if home_delta > 0 or away_delta > 0:
                        print(f"\n[{timestamp}] 🚨 SCORE CHANGE DETECTED!")
                        print(f"  Game: {away_abbr} @ {home_abbr}")
                        if home_delta > 0:
                            print(f"  🏠 {home_abbr}: {last['home_score']} → {home_score} (+{home_delta})")
                        if away_delta > 0:
                            print(f"  ✈️  {away_abbr}: {last['away_score']} → {away_score} (+{away_delta})")
                        print(f"  ⏱️  Detection time: {timestamp}")
                        print(f"  📊 Current score: {away_abbr} {away_score} - {home_abbr} {home_score}")
                        print()
                        
                        # Update stored scores
                        last_scores[game_id].update({
                            "home_score": home_score,
                            "away_score": away_score,
                        })
                
                # Show alive indicator every 10 iterations
                if iteration % 10 == 0:
                    in_progress = sum(1 for gid, data in last_scores.items() if True)
                    print(f"[{timestamp}] 💓 Monitoring {in_progress} game(s)... (iteration {iteration})")
                
            except Exception as e:
                print(f"[{timestamp}] ❌ Error: {e}")
            
            await asyncio.sleep(poll_interval)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ESPN API delay")
    parser.add_argument(
        "--sport",
        choices=["nfl", "college-football"],
        default="college-football",
        help="Sport to monitor (default: college-football)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Poll interval in seconds (default: 2)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("ESPN API DELAY TESTER".center(80))
    print("="*80 + "\n")
    print("📝 Instructions:")
    print("   1. Run this script while watching a live game")
    print("   2. When you see a score happen on TV, note the time")
    print("   3. Watch when this script detects the score change")
    print("   4. The difference is ESPN's API delay")
    print(f"\n   Press Ctrl+C to stop\n")
    print("="*80 + "\n")
    
    try:
        asyncio.run(monitor_espn_delay(args.sport, args.interval))
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
