#!/usr/bin/env python3
"""
SAFE Team Database Integration
Adds comprehensive database WITHOUT breaking existing system
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class SafeTeamDatabaseIntegrator:
    """Safely integrate comprehensive database without breaking existing system"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.comprehensive_db_path = self.root_path / "src" / "comprehensive_sports_database.json"
        self.current_config_path = self.root_path / "config" / "team_colors.json"
        
    def load_comprehensive_database(self) -> Dict[str, Any]:
        """Load comprehensive database"""
        with open(self.comprehensive_db_path, 'r') as f:
            return json.load(f)
    
    def load_current_config(self) -> Dict[str, Any]:
        """Load current team configuration"""
        with open(self.current_config_path, 'r') as f:
            return json.load(f)
    
    def create_hybrid_teams_service(self) -> Dict[str, Any]:
        """Create service that merges both databases safely"""
        
        print("🔍 Analyzing current system...")
        current_config = self.load_current_config()
        current_teams = self._count_teams_in_config(current_config)
        print(f"   Current teams: {current_teams}")
        
        print("📊 Loading comprehensive database...")
        comprehensive_db = self.load_comprehensive_database()
        comprehensive_teams = comprehensive_db.get('metadata', {}).get('total_teams', 0)
        print(f"   Comprehensive teams: {comprehensive_teams}")
        
        # Create mapping from comprehensive to current format
        comprehensive_teams_data = comprehensive_db.get('teams', {})
        
        # Group by sport for analysis
        by_sport = {}
        for team_key, team_data in comprehensive_teams_data.items():
            sport = team_data['sport']
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(team_data)
        
        print(f"\n📈 Expansion potential:")
        sport_mapping = {
            'NFL': 'nfl_teams',
            'CFB': 'college_teams', 
            'NHL': 'nhl_teams',
            'MLB': 'mlb_teams',
            'NBA': 'nba_teams'
        }
        
        expansion_analysis = {}
        for sport, config_key in sport_mapping.items():
            current_sport_teams = self._count_teams_in_sport(current_config, config_key)
            comprehensive_sport_teams = len(by_sport.get(sport, []))
            expansion = comprehensive_sport_teams - current_sport_teams
            expansion_analysis[sport] = {
                'current': current_sport_teams,
                'comprehensive': comprehensive_sport_teams,
                'expansion': expansion
            }
            print(f"   {sport}: {current_sport_teams} → {comprehensive_sport_teams} (+{expansion})")
        
        return {
            'current_config': current_config,
            'comprehensive_db': comprehensive_db,
            'expansion_analysis': expansion_analysis,
            'safe_to_proceed': self._assess_safety(expansion_analysis)
        }
    
    def _count_teams_in_config(self, config: Dict[str, Any]) -> int:
        """Count teams in current config structure"""
        count = 0
        for sport_key, sport_data in config.items():
            if sport_key.endswith('_teams') and isinstance(sport_data, dict):
                for division_data in sport_data.values():
                    if isinstance(division_data, dict):
                        count += len([k for k, v in division_data.items() 
                                    if isinstance(v, dict) and 'primary_color' in v])
        return count
    
    def _count_teams_in_sport(self, config: Dict[str, Any], sport_key: str) -> int:
        """Count teams in specific sport"""
        count = 0
        sport_data = config.get(sport_key, {})
        if isinstance(sport_data, dict):
            for division_data in sport_data.values():
                if isinstance(division_data, dict):
                    count += len([k for k, v in division_data.items() 
                                if isinstance(v, dict) and 'primary_color' in v])
        return count
    
    def _assess_safety(self, expansion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess safety of integration"""
        
        risks = []
        warnings = []
        
        # Check for potential conflicts
        for sport, analysis in expansion_analysis.items():
            if analysis['expansion'] < 0:
                risks.append(f"{sport}: Comprehensive DB has FEWER teams than current config")
            elif analysis['expansion'] > analysis['current'] * 2:
                warnings.append(f"{sport}: Large expansion ({analysis['expansion']} new teams)")
        
        # Overall assessment
        total_current = sum(a['current'] for a in expansion_analysis.values())
        total_comprehensive = sum(a['comprehensive'] for a in expansion_analysis.values())
        total_expansion = total_comprehensive - total_current
        
        is_safe = len(risks) == 0 and total_expansion > 0
        
        return {
            'is_safe': is_safe,
            'risks': risks,
            'warnings': warnings,
            'total_expansion': total_expansion,
            'expansion_ratio': total_comprehensive / total_current if total_current > 0 else 0
        }

def main():
    """Analyze integration safety without making changes"""
    print("🔒 SAFE Team Database Integration Analysis")
    print("=" * 50)
    print("This analysis will NOT modify any files.")
    print("")
    
    integrator = SafeTeamDatabaseIntegrator()
    
    try:
        analysis = integrator.create_hybrid_teams_service()
        
        print(f"\n🛡️ SAFETY ASSESSMENT:")
        safety = analysis['safe_to_proceed']
        
        if safety['is_safe']:
            print("✅ SAFE TO PROCEED")
        else:
            print("❌ RISKS DETECTED")
        
        if safety['risks']:
            print(f"\n🚨 RISKS:")
            for risk in safety['risks']:
                print(f"   • {risk}")
        
        if safety['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in safety['warnings']:
                print(f"   • {warning}")
        
        print(f"\n📊 EXPANSION SUMMARY:")
        print(f"   Total expansion: +{safety['total_expansion']} teams")
        print(f"   Expansion ratio: {safety['expansion_ratio']:.1f}x")
        
        if safety['is_safe']:
            print(f"\n🎯 RECOMMENDED APPROACH:")
            print(f"   1. Create hybrid service (non-destructive)")
            print(f"   2. Add comprehensive teams as additional source")
            print(f"   3. Maintain existing config for backward compatibility")
            print(f"   4. Test expanded API without breaking current functionality")
        else:
            print(f"\n⛔ RECOMMENDED APPROACH:")
            print(f"   1. DO NOT PROCEED with direct migration")
            print(f"   2. Investigate data inconsistencies first")
            print(f"   3. Consider gradual expansion approach")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print("🔒 Your system remains unchanged and safe.")

if __name__ == "__main__":
    main()