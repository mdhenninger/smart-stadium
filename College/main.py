#!/usr/bin/env python3
"""
College Football Smart Light Celebration System - Manual Control
Test any team's celebrations with custom colors
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from college_celebrations import main

if __name__ == "__main__":
    print("🏈 College Football Manual Celebration Controller 🏈")
    print("Test any team's celebrations with authentic colors!")
    print("=" * 65)
    asyncio.run(main())