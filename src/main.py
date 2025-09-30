#!/usr/bin/env python3
"""
Smart Stadium - Main Entry Point

Transform your space into a smart stadium that monitors game activity 
and presents audio visual celebrations and reactions to live events.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.stadium_controller import SmartStadiumController
from core.config_manager import ConfigManager

def print_banner():
    """Display Smart Stadium startup banner"""
    banner = """
🏟️  SMART STADIUM 🏟️
═══════════════════════════════════════════════════════════════
 Transform your space into an intelligent sports venue
 Monitoring live games • Audio/Visual celebrations • Smart reactions
═══════════════════════════════════════════════════════════════
    """
    print(banner)

async def main():
    """Main application entry point"""
    print_banner()
    
    try:
        # Load configuration
        print("🔧 Loading configuration...")
        config_manager = ConfigManager()
        config = await config_manager.load_config()
        
        # Initialize Smart Stadium Controller
        print("🎯 Initializing Smart Stadium...")
        stadium = SmartStadiumController(config)
        
        # Test device connectivity
        print("🧪 Testing device connectivity...")
        if not await stadium.test_devices():
            print("⚠️  Some devices not responding. Check configuration.")
            
        # Start the stadium experience
        print("🚀 Smart Stadium is ready!")
        print("   Select your sport and games to begin monitoring...")
        print("   (Press Ctrl+C to stop)\n")
        
        # Start monitoring
        await stadium.run()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Smart Stadium stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting Smart Stadium: {e}")
        return 1
    finally:
        print("👋 Thanks for using Smart Stadium! 🏟️")
        
    return 0

if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)