"""
College Football Smart Light Controller - Generic Team Celebration System
Supports any college team with customizable colors and celebration patterns
"""

import asyncio
import time
import os
import json
from pywizlight import wizlight, PilotBuilder

# Default colors (can be overridden per team)
DEFAULT_PRIMARY = (0, 51, 141)    # Blue
DEFAULT_SECONDARY = (198, 12, 48) # Red
WHITE = (255, 255, 255)
BRIGHT_WHITE = (255, 255, 255)

class CollegeCelebrationController:
    def __init__(self, light_ips):
        self.lights = [wizlight(ip) for ip in light_ips]
        self.light_ips = light_ips
        self.team_colors = {}  # Will store colors for each team
        self.red_zone_active = False
        self.red_zone_team = None
        self.red_zone_task = None
        
    def set_team_colors(self, team_name, primary_color, secondary_color=None):
        """Set custom colors for a specific team"""
        if secondary_color is None:
            secondary_color = WHITE
        self.team_colors[team_name] = {
            'primary': primary_color,
            'secondary': secondary_color
        }
        
    def get_team_colors(self, team_name):
        """Get colors for a team (or default if not set)"""
        if team_name in self.team_colors:
            return self.team_colors[team_name]['primary'], self.team_colors[team_name]['secondary']
        return DEFAULT_PRIMARY, DEFAULT_SECONDARY

    async def flash_color(self, color, duration=0.5):
        """Flash all lights to a specific color for a duration"""
        try:
            r, g, b = color
            pilot = PilotBuilder(rgb=(r, g, b), brightness=255)
            
            # Turn all lights to the color
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(duration)
        except Exception as e:
            print(f"Error flashing color {color}: {e}")

    async def set_default_lighting(self):
        """Set lights to warm default lighting"""
        try:
            # 2700K warm white setting - comfortable for normal use
            pilot = PilotBuilder(colortemp=2700, brightness=180)
            
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            print("💡 Lights set to warm default lighting (2700K)")
        except Exception as e:
            print(f"Error setting default lighting: {e}")

    async def celebrate_touchdown(self, team_name="Team"):
        """Epic 30-second touchdown celebration"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🏈 {team_name.upper()} TOUCHDOWN! 🏈")
        print("🎉 30-second epic celebration starting...")
        start_time = time.time()
        
        # Epic celebration sequence
        flash_count = 0
        for cycle in range(5):  # 5 cycles of different patterns
            # Rapid alternating (6 flashes per cycle)
            for i in range(6):
                flash_count += 1
                color = primary if i % 2 == 0 else secondary
                color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
                print(f"   Epic Flash {flash_count}/30: {color_name}")
                await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🏈 Touchdown celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_field_goal(self, team_name="Team"):
        """10-second field goal celebration"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🥅 {team_name.upper()} FIELD GOAL! 🥅")
        print("⚡ 10-second celebration starting...")
        start_time = time.time()
        
        # 10 alternating flashes
        for i in range(10):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Field Goal Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🥅 Field goal celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_extra_point(self, team_name="Team"):
        """Quick 5-second extra point celebration"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n✅ {team_name.upper()} EXTRA POINT! ✅")
        print("⚡ 5-second quick celebration starting...")
        start_time = time.time()
        
        # 5 quick alternating flashes
        for i in range(5):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Extra Point Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"✅ Extra point celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_two_point(self, team_name="Team"):
        """Special 10-second two-point conversion celebration"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n💪 {team_name.upper()} 2-POINT CONVERSION! 💪")
        print("🔥 10-second power celebration starting...")
        start_time = time.time()
        
        # 10 alternating flashes with emphasis (standardized duration)
        for i in range(10):
            color = secondary if i % 2 == 0 else primary  # Start with secondary for power
            color_name = "SECONDARY" if i % 2 == 0 else "PRIMARY"
            print(f"   2-Point Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"💪 2-point conversion celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_safety(self, team_name="Team"):
        """15-second safety celebration - rare but awesome"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🛡️ {team_name.upper()} SAFETY! 🛡️")
        print("⚡ 15-second rare celebration starting...")
        start_time = time.time()
        
        # 15 alternating flashes for this rare score
        for i in range(15):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Safety Flash {i+1}/15: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🛡️ Safety celebration complete! ({elapsed:.1f}s)")

    async def celebrate_victory(self, team_name="Team"):
        """Epic 60-second victory celebration"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🏆 {team_name.upper()} VICTORY! 🏆")
        print("🎊 60-second championship celebration starting...")
        start_time = time.time()
        
        # Epic victory sequence - 60 flashes total
        for cycle in range(10):  # 10 cycles of 6 flashes each
            for i in range(6):
                flash_num = cycle * 6 + i + 1
                color = primary if i % 2 == 0 else secondary
                color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
                print(f"   Victory Flash {flash_num}/60: {color_name}")
                await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🏆 Victory celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_turnover(self, team_name="Team"):
        """10-second turnover celebration - defensive highlight"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🔄 {team_name.upper()} TURNOVER! 🔄")
        print("🛡️ 10-second defensive highlight starting...")
        start_time = time.time()
        
        # 10 alternating flashes for turnovers
        for i in range(10):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Turnover Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.6)
        
        elapsed = time.time() - start_time
        print(f"🔄 Turnover celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_big_play(self, team_name="Team", play_type=""):
        """5-second big play celebration - 40+ yard rushing/passing plays only"""
        # Skip field goals - only celebrate rushing/passing big plays
        if 'field goal' in play_type.lower() or 'fg' in play_type.lower():
            print(f"\n⚠️ Skipping big play celebration for field goal: {play_type}")
            return
            
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🏃‍♂️ {team_name.upper()} BIG PLAY! 🏃‍♂️")
        print("💨 5-second explosive celebration starting...")
        start_time = time.time()
        
        # 5 rapid alternating flashes
        for i in range(5):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Big Play Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🏃‍♂️ Big play celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_generic_score(self, team_name="Team", points=3):
        """Generic celebration for any score amount"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🎯 {team_name.upper()} SCORES {points} POINTS! 🎯")
        
        # Determine celebration length based on points
        if points >= 6:
            flash_count = 15  # Longer for touchdowns
            duration = 0.4
        elif points >= 3:
            flash_count = 8   # Medium for field goals
            duration = 0.5
        else:
            flash_count = 5   # Short for smaller scores
            duration = 0.6
            
        print(f"🎉 {flash_count * duration:.1f}-second celebration starting...")
        start_time = time.time()
        
        for i in range(flash_count):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Score Flash {i+1}/{flash_count}: {color_name}")
            await self.flash_color(color, duration)
        
        elapsed = time.time() - start_time
        print(f"🎯 {points}-point celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_sack(self, team_name="Team"):
        """5-second sack celebration - QB pressure"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n⚡ {team_name.upper()} SACK! ⚡")
        print("💥 5-second pressure celebration starting...")
        start_time = time.time()
        
        # 5 flashes with primary emphasis for aggression
        for i in range(5):
            if i < 3:
                color = primary  # More primary color for aggression
                color_name = "PRIMARY"
            else:
                color = secondary
                color_name = "SECONDARY"
            print(f"   Sack Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"⚡ Sack celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_defensive_stop(self, team_name="Team"):
        """6-second defensive stop celebration - 4th down or goal line stand"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🛡️ {team_name.upper()} DEFENSIVE STOP! 🛡️")
        print("💪 6-second stand celebration starting...")
        start_time = time.time()
        
        # 6 alternating flashes for defensive stand
        for i in range(6):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Defensive Stop Flash {i+1}/6: {color_name}")
            await self.flash_color(color, 0.6)
        
        elapsed = time.time() - start_time
        print(f"🛡️ Defensive stop celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_red_zone(self, team_name="Team"):
        """4-second red zone entry celebration - scoring opportunity"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🎯 {team_name.upper()} RED ZONE! 🎯")
        print("🔥 4-second opportunity celebration starting...")
        start_time = time.time()
        
        # 4 quick flashes for red zone entry
        for i in range(4):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Red Zone Flash {i+1}/4: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🎯 Red zone celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def start_red_zone_ambient(self, team_name="Team"):
        """Start red zone ambient lighting - cycles team colors every 10 seconds"""
        self.red_zone_active = True
        self.red_zone_team = team_name
        primary, secondary = self.get_team_colors(team_name)
        
        print(f"🎯 {team_name.upper()} RED ZONE AMBIENT LIGHTING STARTED")
        print(f"🔄 Cycling colors every 10 seconds: {team_name} colors")
        
        # Start the ambient lighting task
        import asyncio
        self.red_zone_task = asyncio.create_task(self._red_zone_cycle(primary, secondary, team_name))
    
    async def stop_red_zone_ambient(self):
        """Stop red zone ambient lighting and return to default"""
        if hasattr(self, 'red_zone_active') and self.red_zone_active:
            self.red_zone_active = False
            if hasattr(self, 'red_zone_task'):
                self.red_zone_task.cancel()
                try:
                    await self.red_zone_task
                except asyncio.CancelledError:
                    pass
            
            print(f"🎯 RED ZONE AMBIENT LIGHTING STOPPED")
            await self.set_default_lighting()
    
    async def _red_zone_cycle(self, primary, secondary, team_name):
        """Internal method to cycle red zone colors"""
        try:
            cycle_count = 0
            while self.red_zone_active:
                cycle_count += 1
                
                # Cycle pattern: Primary -> Fade to Black -> Secondary -> Fade to Black
                colors = [
                    (primary, f"{team_name} PRIMARY"),
                    ((0, 0, 0), "FADE TO BLACK"),
                    (secondary, f"{team_name} SECONDARY"),
                    ((0, 0, 0), "FADE TO BLACK")
                ]
                
                for color, color_name in colors:
                    if not self.red_zone_active:
                        break
                        
                    # Smooth transition to color
                    r, g, b = color
                    pilot = PilotBuilder(rgb=(r, g, b), brightness=180)  # Softer ambient lighting
                    
                    tasks = [light.turn_on(pilot) for light in self.lights]
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Hold color for 2.5 seconds (10 seconds / 4 colors)
                    await asyncio.sleep(2.5)
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"⚠️ Red zone ambient lighting error: {e}")

    async def test_connectivity(self):
        """Test if all lights are responding"""
        print("🧪 Testing light connectivity...")
        try:
            # Quick test flash
            pilot = PilotBuilder(rgb=DEFAULT_PRIMARY, brightness=255)
            tasks = [light.turn_on(pilot) for light in self.lights]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            working_lights = 0
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    working_lights += 1
                else:
                    print(f"❌ Light {self.light_ips[i]} error: {result}")
            
            if working_lights == len(self.lights):
                print("✅ All lights responding!")
                return True
            else:
                print(f"⚠️ {working_lights}/{len(self.lights)} lights responding")
                return False
                
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            return False

    async def test_team_colors(self, team_name):
        """Test the colors for a specific team"""
        primary, secondary = self.get_team_colors(team_name)
        print(f"\n🎨 Testing {team_name} colors...")
        print(f"   Primary: RGB{primary}")
        print(f"   Secondary: RGB{secondary}")
        
        # Flash primary color
        print("   Flashing PRIMARY color...")
        await self.flash_color(primary, 1.0)
        await asyncio.sleep(0.5)
        
        # Flash secondary color
        print("   Flashing SECONDARY color...")
        await self.flash_color(secondary, 1.0)
        await asyncio.sleep(0.5)
        
        print(f"✅ {team_name} color test complete!")

def load_light_ips():
    """Load light IPs from config file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'wiz_lights_config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('known_ips', [])
    except FileNotFoundError:
        print(f"❌ Config file not found at {config_path}")
        return []
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return []

# Popular college team colors (RGB values)
COLLEGE_TEAM_COLORS = {
    'Alabama': ((158, 27, 50), (255, 255, 255)),      # Crimson & White
    'Georgia': ((186, 12, 47), (0, 0, 0)),            # Red & Black
    'Ohio State': ((187, 0, 0), (102, 102, 102)),     # Scarlet & Gray
    'Michigan': ((0, 39, 76), (255, 203, 5)),         # Blue & Maize
    'Texas': ((191, 87, 0), (255, 255, 255)),         # Burnt Orange & White
    'Oklahoma': ((153, 27, 30), (255, 255, 255)),     # Crimson & Cream
    'Notre Dame': ((0, 51, 102), (201, 151, 0)),      # Navy & Gold
    'USC': ((153, 27, 30), (255, 204, 0)),            # Cardinal & Gold
    'Florida': ((0, 33, 165), (255, 103, 0)),         # Blue & Orange
    'LSU': ((70, 29, 124), (253, 208, 35)),           # Purple & Gold
    'Auburn': ((12, 35, 64), (232, 119, 34)),         # Navy & Orange
    'Clemson': ((245, 102, 0), (82, 45, 128)),        # Orange & Purple
    'Penn State': ((4, 30, 66), (255, 255, 255)),     # Navy & White
    'Wisconsin': ((197, 5, 12), (255, 255, 255)),     # Red & White
    'Oregon': ((0, 71, 49), (254, 225, 35)),          # Green & Yellow
    'Miami': ((240, 81, 35), (0, 71, 27)),            # Orange & Green
    'Tennessee': ((255, 130, 0), (255, 255, 255)),    # Orange & White
    'Kentucky': ((0, 51, 160), (255, 255, 255)),      # Blue & White
    'Arkansas': ((157, 34, 53), (255, 255, 255)),     # Red & White
    'Mississippi': ((20, 35, 75), (206, 17, 65)),     # Navy & Red
    'South Carolina': ((115, 0, 10), (255, 255, 255)), # Garnet & White
}

async def main():
    """Main function to run the college celebration system"""
    print("🏈 College Football Smart Celebration System 🏈")
    print("=" * 60)
    
    # Load light IPs from config
    light_ips = load_light_ips()
    
    if not light_ips:
        print("❌ No light IPs found in config file!")
        return
    
    print(f"🎯 Initializing {len(light_ips)} light(s):")
    for ip in light_ips:
        print(f"   - {ip}")
    print()
    
    # Initialize controller
    controller = CollegeCelebrationController(light_ips)
    
    # Load popular team colors
    for team, (primary, secondary) in COLLEGE_TEAM_COLORS.items():
        controller.set_team_colors(team, primary, secondary)
    
    # Test connectivity
    if not await controller.test_connectivity():
        print("❌ Some lights not responding. Check your network connection.")
        return
    
    # Main menu loop
    while True:
        print("\n🎮 COLLEGE FOOTBALL CELEBRATION MENU")
        print("=" * 45)
        print("🏈 CELEBRATION OPTIONS:")
        print("1. 🏈 Touchdown (30s)")
        print("2. 🥅 Field Goal (10s)")
        print("3. ✅ Extra Point (5s)")
        print("4. 💪 2-Point Conversion (5s)")
        print("5. 🛡️ Safety (15s)")
        print("6. 🏆 Victory (60s)")
        print("7. 🔄 Turnover (10s)")
        print("8. 🏃‍♂️ Big Play (5s)")
        print("9. 🎯 Generic Score")
        print("\n🎨 TEAM OPTIONS:")
        print("10. 🎨 Test Team Colors")
        print("11. 📚 List Available Teams")
        print("12. ➕ Add Custom Team Colors")
        print("\n🧪 SYSTEM OPTIONS:")
        print("13. 💡 Set Default & Exit")
        
        try:
            choice = input("\nSelect option (1-13): ").strip()
            
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                # Get team name
                team_name = input("Enter team name (or press Enter for 'Team'): ").strip()
                if not team_name:
                    team_name = "Team"
                
                if choice == '1':
                    await controller.celebrate_touchdown(team_name)
                elif choice == '2':
                    await controller.celebrate_field_goal(team_name)
                elif choice == '3':
                    await controller.celebrate_extra_point(team_name)
                elif choice == '4':
                    await controller.celebrate_two_point(team_name)
                elif choice == '5':
                    await controller.celebrate_safety(team_name)
                elif choice == '6':
                    await controller.celebrate_victory(team_name)
                elif choice == '7':
                    await controller.celebrate_turnover(team_name)
                elif choice == '8':
                    await controller.celebrate_big_play(team_name)
                elif choice == '9':
                    try:
                        points = int(input("Enter points scored: ").strip())
                        await controller.celebrate_generic_score(team_name, points)
                    except ValueError:
                        print("❌ Invalid points value")
                        
            elif choice == '10':
                team_name = input("Enter team name to test colors: ").strip()
                if team_name:
                    await controller.test_team_colors(team_name)
                else:
                    print("❌ Please enter a team name")
                    
            elif choice == '11':
                print("\n📚 Available Teams with Colors:")
                print("=" * 40)
                for i, team in enumerate(sorted(COLLEGE_TEAM_COLORS.keys()), 1):
                    primary, secondary = COLLEGE_TEAM_COLORS[team]
                    print(f"{i:2d}. {team:<15} RGB{primary} / RGB{secondary}")
                    
            elif choice == '12':
                team_name = input("Enter team name: ").strip()
                if team_name:
                    try:
                        print("Enter primary color (RGB format: r,g,b):")
                        primary_input = input("Primary RGB: ").strip()
                        primary = tuple(map(int, primary_input.split(',')))
                        
                        print("Enter secondary color (RGB format: r,g,b):")
                        secondary_input = input("Secondary RGB: ").strip()
                        secondary = tuple(map(int, secondary_input.split(',')))
                        
                        controller.set_team_colors(team_name, primary, secondary)
                        print(f"✅ Colors set for {team_name}")
                        await controller.test_team_colors(team_name)
                    except ValueError:
                        print("❌ Invalid RGB format. Use: r,g,b (e.g., 255,0,0)")
                        
            elif choice == '13':
                print("💡 Setting lights to default warm white...")
                await controller.set_default_lighting()
                print("✅ Lights set to default. Thanks for testing! 🏈")
                break
            else:
                print("❌ Invalid choice. Please select 1-13.")
                
        except KeyboardInterrupt:
            print("\n\n💡 Setting lights to default before exit...")
            await controller.set_default_lighting()
            print("👋 Goodbye! 🏈")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())