#!/usr/bin/env python3
"""
College Football Multi-Game Monitor - Live Game Selection
Monitor multiple games and teams with interactive selection
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from college_game_monitor import main

if __name__ == "__main__":
    print("🏈 College Football Multi-Game Live Monitor 🏈")
    print("Select from tonight's games and monitor any teams!")
    print("=" * 70)
    asyncio.run(main())