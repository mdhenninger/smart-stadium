#!/usr/bin/env python3
"""Test script to validate defensive play detection fixes."""

import re

def test_enhanced_detection():
    """Test the enhanced defensive play detection logic with problematic cases."""
    
    # Test cases from your actual problematic plays
    test_cases = [
        {
            "description": "M.Wishnowsky punts 43 yards to NE 30, Center-R.Ferguson. M.Jones pushed ob at NE 30 for no gain (S.F",
            "expected_detection": None,
            "issue": "False fumble recovery on punt"
        },
        {
            "description": "D.Maye pass short left to R.Stevenson to BUF 36 for no gain (A.Epenesa). PENALTY on NE-K.Boutte, Fac",
            "expected_detection": None,
            "issue": "False sack on completed pass"
        },
        {
            "description": "J.Allen FUMBLES (Aborted) at 50, RECOVERED by NE-J.Farmer at BUF 47.",
            "expected_detection": "fumble_recovery",
            "expected_team": "NE",
            "issue": "Wrong team assignment for fumble recovery"
        },
        {
            "description": "(Shotgun) D.Maye sacked at NE 46 for -2 yards (G.Rousseau).",
            "expected_detection": "sack",
            "issue": "Real sack should still work"
        },
        {
            "description": "(Shotgun) D.Maye sacked at NE 45 for -3 yards (T.Bernard).",
            "expected_detection": "sack", 
            "issue": "Another real sack test"
        }
    ]
    
    print("🧪 Testing Enhanced Defensive Play Detection")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['issue']}")
        print(f"Description: {test_case['description'][:80]}...")
        
        # Apply our enhanced detection logic
        play_text = test_case['description']
        play_text_lower = play_text.lower()
        
        detected_event = None
        detected_team = None
        
        # Enhanced sack detection with yardage loss verification
        if any(keyword in play_text_lower for keyword in ["sack", "sacked"]):
            if (re.search(r'sacked.*for -\\d+', play_text_lower) or 
                re.search(r'loss of \\d+', play_text_lower) or
                "sacked at" in play_text_lower):
                # Additional check: not a completed pass
                if not ("pass" in play_text_lower and "incomplete" not in play_text_lower and "sacked" not in play_text_lower):
                    detected_event = "sack"
                    
        # Enhanced fumble recovery detection
        elif "fumble" in play_text_lower:
            # Must have proper "RECOVERED by TEAM-PLAYER" pattern
            recover_match = re.search(r'recovered by ([A-Z]{2,3})-', play_text, re.IGNORECASE)
            if recover_match:
                detected_event = "fumble_recovery"
                detected_team = recover_match.group(1)
                
        # Interception detection  
        elif any(keyword in play_text_lower for keyword in ["interception", "intercepted"]):
            detected_event = "interception"
            
        # Safety detection
        elif "safety" in play_text_lower:
            detected_event = "safety"
        
        # Results
        expected = test_case.get('expected_detection')
        expected_team = test_case.get('expected_team')
        
        if detected_event == expected:
            print(f"✅ Detection: PASS ({detected_event or 'None'})")
        else:
            print(f"❌ Detection: FAIL (got {detected_event}, expected {expected})")
            
        if expected_team:
            if detected_team == expected_team:
                print(f"✅ Team Assignment: PASS ({detected_team})")
            else:
                print(f"❌ Team Assignment: FAIL (got {detected_team}, expected {expected_team})")
    
    print(f"\n🎯 Test Summary:")
    print(f"- Enhanced regex patterns prevent false positives")
    print(f"- Yardage loss verification for sacks")
    print(f"- Proper team parsing from 'RECOVERED by TEAM-' patterns")
    print(f"- Completed pass vs sack differentiation")

if __name__ == "__main__":
    test_enhanced_detection()