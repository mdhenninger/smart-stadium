"""
Buffalo Bills Light System Launcher
Choose between Bills-only monitoring or multi-game NFL monitoring
"""

import asyncio
import sys
import os

def main():
    print("🦬 Buffalo Bills Smart Light System 🦬")
    print("=" * 50)
    print()
    print("🎯 MONITORING OPTIONS:")
    print("1. 🏈 Bills Only - Monitor only Buffalo Bills games (original)")
    print("2. 🏟️ Multi-Game NFL - Monitor Bills + additional NFL games")
    print("3. 🎓 College Football - Monitor college games")
    print("4. ❌ Exit")
    print()
    
    try:
        choice = input("Select monitoring mode (1-4): ").strip()
        
        if choice == '1':
            print("🦬 Launching Bills-only monitor...")
            # Import and run original Bills monitor
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            from bills_score_monitor import main as bills_main
            asyncio.run(bills_main())
            
        elif choice == '2':
            print("🏟️ Launching Enhanced NFL Multi-Game monitor...")
            # Import and run enhanced monitor
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            from enhanced_nfl_monitor import main as enhanced_main
            asyncio.run(enhanced_main())
            
        elif choice == '3':
            print("🎓 Launching College Football monitor...")
            # Change to college directory and run
            college_path = os.path.join(os.path.dirname(__file__), '..', 'College')
            if os.path.exists(college_path):
                os.chdir(college_path)
                sys.path.append(os.path.join(college_path, 'src'))
                from college_game_monitor import main as college_main
                asyncio.run(college_main())
            else:
                print("❌ College football system not found!")
                
        elif choice == '4':
            print("👋 Goodbye! GO BILLS! 🦬")
            
        else:
            print("❌ Invalid choice. Please select 1-4.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye! GO BILLS! 🦬")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()