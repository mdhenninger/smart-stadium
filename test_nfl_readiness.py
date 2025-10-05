"""
NFL Readiness Test Suite
Tests all critical NFL functionality before game day
"""
import asyncio
import json
from pathlib import Path

async def test_nfl_setup():
    """Comprehensive NFL readiness check"""
    
    print("🏈 NFL READINESS CHECK")
    print("=" * 60)
    
    results = {
        "team_colors": False,
        "espn_api": False,
        "logo_parsing": False,
        "monitoring": False,
        "lights": False,
    }
    
    # Test 1: NFL Team Colors Configuration
    print("\n1. Testing NFL Team Colors Configuration...")
    try:
        from pathlib import Path as PathLib
        config_path = PathLib("config/team_colors.json")
        with open(config_path) as f:
            team_colors = json.load(f)
        
        nfl_teams = team_colors.get("nfl_teams", {})
        divisions = ["AFC_East", "AFC_North", "AFC_South", "AFC_West", 
                    "NFC_East", "NFC_North", "NFC_South", "NFC_West"]
        
        total_teams = sum(len(nfl_teams.get(div, {})) for div in divisions)
        print(f"   ✅ Found {len(nfl_teams)} divisions")
        print(f"   ✅ Found {total_teams} NFL teams configured")
        
        # Sample a few teams
        sample_teams = ["BUF", "KC", "DAL", "SF"]
        for abbr in sample_teams:
            found = False
            for div_data in nfl_teams.values():
                if abbr in div_data:
                    team = div_data[abbr]
                    print(f"   ✅ {abbr}: {team.get('name')} - Colors: {team.get('colors_description', 'OK')}")
                    found = True
                    break
            if not found:
                print(f"   ⚠️  {abbr} not found")
        
        results["team_colors"] = total_teams >= 32
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: ESPN NFL API Connection
    print("\n2. Testing ESPN NFL API...")
    try:
        import httpx
        
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            events = data.get("events", [])
            print(f"   ✅ Connected to ESPN NFL API")
            print(f"   ✅ Found {len(events)} NFL games")
            
            # Check game statuses
            statuses = {}
            for event in events[:5]:  # Sample first 5
                comp = event.get("competitions", [{}])[0]
                status = comp.get("status", {}).get("type", {}).get("state", "unknown")
                statuses[status] = statuses.get(status, 0) + 1
            
            print(f"   📊 Game statuses: {dict(statuses)}")
            results["espn_api"] = True
            
    except Exception as e:
        print(f"   ❌ ESPN API Error: {e}")
    
    # Test 3: Logo URL Parsing
    print("\n3. Testing Logo URL Parsing...")
    try:
        from app.services.espn_client import EspnScoreboardClient
        from app.models.game import Sport
        
        client = EspnScoreboardClient()
        scoreboard = await client.fetch_scoreboard(Sport.NFL)
        await client.close()
        
        games_with_logos = sum(1 for g in scoreboard.games 
                              if g.home.logo_url and g.away.logo_url)
        
        print(f"   ✅ Parsed {len(scoreboard.games)} NFL games")
        print(f"   ✅ {games_with_logos}/{len(scoreboard.games)} games have team logos")
        
        if scoreboard.games:
            sample = scoreboard.games[0]
            print(f"   📷 Sample: {sample.home.display_name} - {sample.home.logo_url}")
            print(f"   📷 Sample: {sample.away.display_name} - {sample.away.logo_url}")
        
        results["logo_parsing"] = games_with_logos == len(scoreboard.games)
        
    except Exception as e:
        print(f"   ❌ Logo parsing error: {e}")
    
    # Test 4: Team Lookup Service
    print("\n4. Testing Team Lookup Service...")
    try:
        from app.services.hybrid_teams_service import HybridTeamsService
        from pathlib import Path as PathLib
        
        config_dir = PathLib("config")
        src_dir = PathLib("src")
        service = HybridTeamsService(config_dir=config_dir, src_dir=src_dir)
        
        # Get NFL teams
        nfl_teams = service.get_teams(sport="nfl")
        
        print(f"   ✅ Loaded {len(nfl_teams)} NFL teams from service")
        
        # Check for key teams
        test_abbrs = ["BUF", "KC", "SF", "DAL"]
        found_teams = [t for t in nfl_teams if t.abbreviation in test_abbrs]
        
        for team in found_teams[:4]:
            print(f"   ✅ {team.abbreviation}: {team.name} - Colors: RGB{team.colors.primary}")
        
        results["monitoring"] = len(nfl_teams) >= 30
        
    except Exception as e:
        import traceback
        print(f"   ❌ Team lookup error: {e}")
        traceback.print_exc()
    
    # Test 5: WiZ Lights Ready
    print("\n5. Testing WiZ Lights Configuration...")
    try:
        config_path = Path("config/wiz_lights_config.json")
        with open(config_path) as f:
            wiz_config = json.load(f)
        
        # Config uses "devices" not "lights"
        lights = wiz_config.get("devices", [])
        enabled_lights = [l for l in lights if l.get("enabled", True)]
        
        print(f"   ✅ {len(enabled_lights)} WiZ lights configured and enabled")
        for light in enabled_lights:
            print(f"   💡 {light.get('name')}: {light.get('ip')}")
        
        results["lights"] = len(enabled_lights) >= 3
        
    except Exception as e:
        print(f"   ❌ Lights config error: {e}")
    
    # Test 6: Dashboard Ready
    print("\n6. Checking Dashboard Configuration...")
    try:
        dashboard_path = Path("dashboard/src/types.ts")
        if dashboard_path.exists():
            content = dashboard_path.read_text()
            has_logo = "logo_url" in content
            has_nfl = "nfl" in content.lower()
            
            print(f"   ✅ Dashboard TypeScript types exist")
            print(f"   {'✅' if has_logo else '⚠️ '} Logo URL support: {has_logo}")
            print(f"   {'✅' if has_nfl else '⚠️ '} NFL support: {has_nfl}")
        else:
            print(f"   ⚠️  Dashboard not found")
    except Exception as e:
        print(f"   ❌ Dashboard check error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 READINESS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {test.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SYSTEM IS READY FOR NFL GAMES! 🏈")
    elif passed >= total - 1:
        print("\n⚠️  SYSTEM IS MOSTLY READY - Minor issues detected")
    else:
        print("\n❌ SYSTEM NEEDS ATTENTION - Multiple issues detected")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(test_nfl_setup())
