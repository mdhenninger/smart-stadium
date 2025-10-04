"""
Buffalo Bills WiZ Light Controller - Multiple Celebration Types
TD, Extra Point, 2-Point Conversion, and Field Goal celebrations
"""

import asyncio
import time
import os
import json
import colorsys
from pywizlight import wizlight, PilotBuilder

# Buffalo Bills celebration colors - Pure for maximum impact
BILLS_BLUE = (0, 0, 255)    # Pure blue for maximum visibility
BILLS_RED = (255, 0, 0)     # Pure red for maximum visibility
WHITE = (255, 255, 255)
BRIGHT_WHITE = (255, 255, 255)
DIM_WHITE = (128, 128, 128)

class BillsCelebrationController:
    def __init__(self, light_ips):
        self.lights = [wizlight(ip) for ip in light_ips]
        self.light_ips = light_ips
        self.team_colors = {}  # Store team colors for multi-team support
        
        # Set default Bills colors
        self.current_primary_color = BILLS_BLUE
        self.current_secondary_color = BILLS_RED
        
        # Red zone ambient lighting state
        self.red_zone_active = False
        self.red_zone_team = None
        self.red_zone_task = None
    
    def set_team_colors(self, team_abbr, primary_color, secondary_color):
        """Set team colors for celebrations"""
        # Only log if this is a new team or the colors changed
        is_new_team = team_abbr not in self.team_colors
        colors_changed = (not is_new_team and 
                         (self.team_colors[team_abbr]['primary'] != primary_color or
                          self.team_colors[team_abbr]['secondary'] != secondary_color))
        
        self.team_colors[team_abbr] = {
            'primary': primary_color,
            'secondary': secondary_color
        }
        
        # Update current colors for this team
        self.current_primary_color = primary_color
        self.current_secondary_color = secondary_color
        
        # Only log when colors are actually new or changed
        if is_new_team or colors_changed:
            print(f"🎨 Set {team_abbr} colors: {primary_color} / {secondary_color}")
    
    def get_team_colors(self, team_abbr):
        """Get team colors or return default Bills colors"""
        if team_abbr in self.team_colors:
            return self.team_colors[team_abbr]['primary'], self.team_colors[team_abbr]['secondary']
        return BILLS_BLUE, BILLS_RED
    
    def enhance_color(self, rgb_color, saturation_boost=1.3, brightness_boost=1.0):
        """Enhance color saturation and brightness for better visibility on smart lights"""
        try:
            # Normalize RGB to 0-1 range
            r, g, b = rgb_color
            r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
            
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            
            # Boost saturation and brightness
            s_enhanced = min(1.0, s * saturation_boost)
            v_enhanced = min(1.0, v * brightness_boost)
            
            # Convert back to RGB
            r_enhanced, g_enhanced, b_enhanced = colorsys.hsv_to_rgb(h, s_enhanced, v_enhanced)
            
            # Convert back to 0-255 range
            enhanced_rgb = (
                int(r_enhanced * 255),
                int(g_enhanced * 255),
                int(b_enhanced * 255)
            )
            
            return enhanced_rgb
            
        except Exception as e:
            print(f"⚠️ Color enhancement failed: {e}, using original color")
            return rgb_color

    async def flash_color(self, color, duration=0.5):
        """Flash all lights to a specific color for a duration"""
        try:
            # Enhance the color for better visibility
            enhanced_color = self.enhance_color(color)
            r, g, b = enhanced_color
            
            # Use maximum brightness for celebrations
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

    async def celebrate_touchdown(self, team_name="BUFFALO BILLS"):
        """Epic 30-second touchdown celebration"""
        print(f"\n🏈 {team_name} TOUCHDOWN! 🏈")
        print("🎉 30-second epic celebration starting...")
        start_time = time.time()
        
        # Epic celebration sequence
        flash_count = 0
        for cycle in range(5):  # 5 cycles of different patterns
            # Rapid alternating (6 flashes per cycle)
            for i in range(6):
                flash_count += 1
                color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
                color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
                print(f"   Epic Flash {flash_count}/30: {color_name}")
                await self.flash_color(color, 0.4)  # Faster flash
        
        elapsed = time.time() - start_time
        print(f"🏈 Touchdown celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_field_goal(self, team_name="BUFFALO BILLS"):
        """10-second field goal celebration"""
        print(f"\n🥅 {team_name} FIELD GOAL! 🥅")
        print("⚡ 10-second celebration starting...")
        start_time = time.time()
        
        # 10 alternating flashes
        for i in range(10):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Field Goal Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🥅 Field goal celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_extra_point(self, team_name="BUFFALO BILLS"):
        """Quick 5-second extra point celebration"""
        print(f"\n✅ {team_name} EXTRA POINT! ✅")
        print("⚡ 5-second quick celebration starting...")
        start_time = time.time()
        
        # 5 quick alternating flashes
        for i in range(5):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Extra Point Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"✅ Extra point celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_two_point(self, team_name="BUFFALO BILLS"):
        """Special 10-second two-point conversion celebration"""
        print(f"\n💪 {team_name} 2-POINT CONVERSION! 💪")
        print("🔥 10-second power celebration starting...")
        start_time = time.time()
        
        # 10 alternating flashes with emphasis
        for i in range(10):
            color = self.current_secondary_color if i % 2 == 0 else self.current_primary_color  # Start with secondary for power
            color_name = "SECONDARY" if i % 2 == 0 else "PRIMARY"
            print(f"   2-Point Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"💪 2-point conversion celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_safety(self, team_name="BUFFALO BILLS"):
        """15-second safety celebration - rare but awesome"""
        print(f"\n🛡️ {team_name} SAFETY! 🛡️")
        print("⚡ 15-second rare celebration starting...")
        start_time = time.time()
        
        # 15 alternating flashes for this rare score
        for i in range(15):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Safety Flash {i+1}/15: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🛡️ Safety celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_victory(self, team_name="BUFFALO BILLS"):
        """Epic 60-second victory celebration"""
        print(f"\n🏆 {team_name} VICTORY! 🏆")
        print("🎊 60-second championship celebration starting...")
        start_time = time.time()
        
        # Epic victory sequence - 60 flashes total
        for cycle in range(10):  # 10 cycles of 6 flashes each
            for i in range(6):
                flash_num = cycle * 6 + i + 1
                color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
                color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
                print(f"   Victory Flash {flash_num}/60: {color_name}")
                await self.flash_color(color, 0.4)  # Slightly faster for excitement
        
        elapsed = time.time() - start_time
        print(f"🏆 Victory celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_turnover(self, team_name="BUFFALO BILLS"):
        """10-second turnover celebration - defensive highlight"""
        print(f"\n🔄 {team_name} TURNOVER! 🔄")
        print("🛡️ 10-second defensive highlight starting...")
        start_time = time.time()
        
        # 10 alternating flashes for turnovers
        for i in range(10):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Turnover Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.6)  # Slightly slower, more dramatic
        
        elapsed = time.time() - start_time
        print(f"🔄 Turnover celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_big_play(self, team_name="BUFFALO BILLS", play_type=""):
        """5-second big play celebration - 40+ yard rushing/passing plays only"""
        # Skip field goals - only celebrate rushing/passing big plays
        if 'field goal' in play_type.lower() or 'fg' in play_type.lower():
            print(f"\n⚠️ Skipping big play celebration for field goal: {play_type}")
            return
            
        print(f"\n🏃‍♂️ {team_name} BIG PLAY! 🏃‍♂️")
        print("💨 5-second explosive celebration starting...")
        start_time = time.time()
        
        # 5 rapid alternating flashes
        for i in range(5):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Big Play Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.4)  # Fast and exciting
        
        elapsed = time.time() - start_time
        print(f"🏃‍♂️ Big play celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_defensive_stop(self, team_name="BUFFALO BILLS"):
        """5-second defensive stop celebration - 4th down stops"""
        print(f"\n🛡️ {team_name} DEFENSIVE STOP! 🛡️")
        print("⚡ 5-second defensive celebration starting...")
        start_time = time.time()
        
        # 5 flashes with primary color emphasis (defense)
        for i in range(5):
            if i < 3:
                color = self.current_primary_color  # More primary for defense
                color_name = "PRIMARY"
            else:
                color = self.current_secondary_color
                color_name = "SECONDARY"
            print(f"   Defensive Stop Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🛡️ Defensive stop celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_sack(self, team_name="BUFFALO BILLS"):
        """2-second sack celebration - QB pressure"""
        print(f"\n⚡ {team_name} SACK! ⚡")
        print("💥 2-second pressure celebration starting...")
        start_time = time.time()
        
        # 1 flash of each color (2 total flashes)
        print(f"   Sack Flash 1/2: SECONDARY")
        await self.flash_color(self.current_secondary_color, 0.5)
        print(f"   Sack Flash 2/2: PRIMARY")
        await self.flash_color(self.current_primary_color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"⚡ Sack celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def celebrate_red_zone(self, team_name="BUFFALO BILLS"):
        """Red zone ambient lighting - entering scoring territory"""
        print(f"\n🎯 {team_name} RED ZONE! 🎯")
        print("🔥 Starting red zone ambient lighting...")
        start_time = time.time()
        
        try:
            # Step 1: Bright white flash
            print("   Red Zone Step 1/3: Bright white flash")
            pilot = PilotBuilder(rgb=BRIGHT_WHITE, brightness=255)
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
            
            # Step 2: Transition to team primary color
            print(f"   Red Zone Step 2/3: Transition to team color")
            enhanced_color = self.enhance_color(self.current_primary_color)
            r, g, b = enhanced_color
            pilot = PilotBuilder(rgb=(r, g, b), brightness=200)
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
            
            # Step 3: Hold steady at team color (ambient level)
            print(f"   Red Zone Step 3/3: Hold steady ambient")
            pilot = PilotBuilder(rgb=(r, g, b), brightness=150)  # Dimmer for ambient
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update red zone state
            self.red_zone_active = True
            self.red_zone_team = team_name
            
            elapsed = time.time() - start_time
            print(f"🎯 Red zone ambient lighting active! ({elapsed:.1f}s)")
            print(f"🎨 Holding steady at {self.current_primary_color} (brightness 150)")
            
        except Exception as e:
            print(f"❌ Error setting red zone ambient: {e}")
            # Fallback to default lighting
            await self.set_default_lighting()

    async def celebrate_generic_score(self, points=3, team_name="BUFFALO BILLS"):
        """Generic celebration for unusual scoring plays"""
        print(f"\n🎯 {team_name} SCORED {points} POINTS! 🎯")
        print(f"⚡ {points * 2}-second celebration starting...")
        start_time = time.time()
        
        # Flash count based on points scored
        flash_count = max(3, points)  # At least 3 flashes
        
        for i in range(flash_count):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Generic Score Flash {i+1}/{flash_count}: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🎯 Generic score celebration complete! ({elapsed:.1f}s)")
        
        # Return to default lighting
        await self.set_default_lighting()

    async def test_connectivity(self):
        """Test if all lights are responding"""
        print("🧪 Testing light connectivity...")
        try:
            # Quick test flash
            pilot = PilotBuilder(rgb=self.current_primary_color, brightness=255)
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

    async def test_all_celebrations(self):
        """Test all celebration types in sequence"""
        print("\n🧪 TESTING ALL CELEBRATION TYPES 🧪")
        print("=" * 50)
        
        celebrations = [
            ("🏈 Touchdown", self.celebrate_touchdown),
            ("🥅 Field Goal", self.celebrate_field_goal),
            ("✅ Extra Point", self.celebrate_extra_point),
            ("💪 2-Point Conversion", self.celebrate_two_point),
            ("🛡️ Safety", self.celebrate_safety),
            ("🔄 Turnover", self.celebrate_turnover),
            ("🏃‍♂️ Big Play", self.celebrate_big_play),
            ("🛡️ Defensive Stop", self.celebrate_defensive_stop),
            ("⚡ Sack", self.celebrate_sack),
            ("🎯 Red Zone", self.celebrate_red_zone),
            ("🏆 Victory", self.celebrate_victory)
        ]
        
        for i, (name, celebration_func) in enumerate(celebrations, 1):
            print(f"\n[{i}/{len(celebrations)}] Testing {name}...")
            await celebration_func()
            if i < len(celebrations):  # Don't wait after the last one
                print("   ⏳ Waiting 2 seconds before next test...")
                await asyncio.sleep(2)
        
        print("\n🧪 All celebration tests complete!")

    async def start_red_zone_ambient(self, team_name="Team"):
        """Start red zone ambient lighting with solid team color"""
        self.red_zone_active = True
        self.red_zone_team = team_name
        
        # Get team primary color for solid ambient
        primary, secondary = self.current_primary_color, self.current_secondary_color
        
        print(f"🎯 Starting red zone ambient lighting for {team_name}")
        print(f"🎨 Solid color: {primary}")
        
        try:
            # Set lights to enhanced team primary color at moderate brightness
            enhanced_color = self.enhance_color(primary)
            r, g, b = enhanced_color
            pilot = PilotBuilder(rgb=(r, g, b), brightness=150)  # Dimmer for ambient
            
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            print(f"❌ Error setting red zone ambient: {e}")

    async def stop_red_zone_ambient(self):
        """Stop red zone ambient lighting"""
        if hasattr(self, 'red_zone_active') and self.red_zone_active:
            self.red_zone_active = False
            print("🎯 Red zone ambient lighting stopped")
            await self.set_default_lighting()

def load_light_ips():
    """Load light IPs from config file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'wiz_lights_config.json')
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

async def main():
    """Main function to run the celebration system"""
    print("🏈 Buffalo Bills Smart Celebration System 🏈")
    print("=" * 55)
    
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
    controller = BillsCelebrationController(light_ips)
    
    # Test connectivity
    if not await controller.test_connectivity():
        print("❌ Some lights not responding. Check your network connection.")
        return
    
    # Main menu loop
    while True:
        print("\n🎮 BILLS CELEBRATION MENU")
        print("=" * 35)
        print("🏈 SCORING CELEBRATIONS:")
        print("1. 🏈 Touchdown (30s)")
        print("2. 🥅 Field Goal (10s)")
        print("3. ✅ Extra Point (5s)")
        print("4. 💪 2-Point Conversion (10s)")
        print("5. 🛡️ Safety (15s)")
        print("6. 🏆 Victory (60s)")
        print("\n🛡️ DEFENSIVE/PLAY CELEBRATIONS:")
        print("7. 🔄 Turnover (10s)")
        print("8. 🏃‍♂️ Big Play (5s)")
        print("9. 🛡️ Defensive Stop (5s)")
        print("10. ⚡ Sack (2s)")
        print("11. 🎯 Red Zone (Ambient)")
        print("\n🧪 SYSTEM OPTIONS:")
        print("12. 🧪 Test All Celebrations")
        print("13. 💡 Set Default & Exit")
        
        try:
            choice = input("\nSelect celebration type (1-13): ").strip()
            
            if choice == '1':
                await controller.celebrate_touchdown()
            elif choice == '2':
                await controller.celebrate_field_goal()
            elif choice == '3':
                await controller.celebrate_extra_point()
            elif choice == '4':
                await controller.celebrate_two_point()
            elif choice == '5':
                await controller.celebrate_safety()
            elif choice == '6':
                await controller.celebrate_victory()
            elif choice == '7':
                await controller.celebrate_turnover()
            elif choice == '8':
                await controller.celebrate_big_play()
            elif choice == '9':
                await controller.celebrate_defensive_stop()
            elif choice == '10':
                await controller.celebrate_sack()
            elif choice == '11':
                await controller.celebrate_red_zone()
            elif choice == '12':
                await controller.test_all_celebrations()
            elif choice == '13':
                print("💡 Setting lights to default warm white...")
                await controller.set_default_lighting()
                print("✅ Lights set to default. Thanks for testing! GO BILLS! 🦬")
                break
            else:
                print("❌ Invalid choice. Please select 1-13.")
                
        except KeyboardInterrupt:
            print("\n\n💡 Setting lights to default before exit...")
            await controller.set_default_lighting()
            print("👋 Goodbye! GO BILLS! 🦬")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())