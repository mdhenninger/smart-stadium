"""
Smart Stadium Light Controller
Manages intelligent lighting celebrations for multi-sport events
Evolved from Buffalo Bills celebration system
"""

import asyncio
import time
import os
import json
from typing import List, Tuple, Optional, Dict
from pywizlight import wizlight, PilotBuilder

class SmartStadiumLights:
    """
    Intelligent lighting system for sports celebrations
    Supports multi-team, multi-sport scenarios with configurable celebrations
    """
    
    def __init__(self, light_ips: List[str]):
        self.lights = [wizlight(ip) for ip in light_ips]
        self.light_ips = light_ips
        self.team_colors: Dict[str, Dict[str, Tuple[int, int, int]]] = {}
        
        # Current active team colors
        self.current_primary_color = (0, 51, 141)  # Default: Bills Blue
        self.current_secondary_color = (198, 12, 48)  # Default: Bills Red
        
        # Red zone ambient lighting state
        self.red_zone_active = False
        self.red_zone_team = None
        self.red_zone_task = None
        
        # Celebration intensity settings
        self.celebration_brightness = 255
        self.default_brightness = 180
        self.default_color_temp = 2700  # Warm white
    
    def set_team_colors(self, team_abbr: str, primary_color: Tuple[int, int, int], 
                       secondary_color: Tuple[int, int, int]) -> None:
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
    
    def get_team_colors(self, team_abbr: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Get team colors or return current defaults"""
        if team_abbr in self.team_colors:
            return self.team_colors[team_abbr]['primary'], self.team_colors[team_abbr]['secondary']
        return self.current_primary_color, self.current_secondary_color
    
    async def test_connectivity(self) -> bool:
        """Test connection to all lights"""
        print("🧪 Testing light connectivity...")
        success_count = 0
        
        for i, light in enumerate(self.lights):
            try:
                # Try to get light state
                state = await light.updateState()
                if state:
                    success_count += 1
                    print(f"✅ Light {i+1} ({self.light_ips[i]}): Connected")
                else:
                    print(f"❌ Light {i+1} ({self.light_ips[i]}): No response")
            except Exception as e:
                print(f"❌ Light {i+1} ({self.light_ips[i]}): Error - {e}")
        
        all_connected = success_count == len(self.lights)
        if all_connected:
            print("✅ All lights responding!")
        else:
            print(f"⚠️ {success_count}/{len(self.lights)} lights responding")
        
        return all_connected

    async def flash_color(self, color: Tuple[int, int, int], duration: float = 0.5) -> None:
        """Flash all lights to a specific color for a duration"""
        try:
            r, g, b = color
            pilot = PilotBuilder(rgb=(r, g, b), brightness=self.celebration_brightness)
            
            # Turn all lights to the color
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(duration)
        except Exception as e:
            print(f"Error flashing color {color}: {e}")

    async def set_default_lighting(self) -> None:
        """Set lights to warm default lighting"""
        try:
            pilot = PilotBuilder(colortemp=self.default_color_temp, brightness=self.default_brightness)
            
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"💡 Lights set to warm default lighting ({self.default_color_temp}K)")
        except Exception as e:
            print(f"Error setting default lighting: {e}")

    # CELEBRATION METHODS
    
    async def celebrate_touchdown(self, team_name: str = "TEAM") -> None:
        """Epic 30-second touchdown celebration"""
        print(f"\n🏈 {team_name} TOUCHDOWN! 🏈")
        print("🎉 30-second epic celebration starting...")
        start_time = time.time()
        
        # Epic celebration sequence - 5 cycles of 6 flashes each
        flash_count = 0
        for cycle in range(5):
            for i in range(6):
                flash_count += 1
                color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
                color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
                print(f"   Epic Flash {flash_count}/30: {color_name}")
                await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🏈 Touchdown celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_field_goal(self, team_name: str = "TEAM") -> None:
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
        await self.set_default_lighting()

    async def celebrate_extra_point(self, team_name: str = "TEAM") -> None:
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
        await self.set_default_lighting()

    async def celebrate_two_point(self, team_name: str = "TEAM") -> None:
        """Special 5-second two-point conversion celebration"""
        print(f"\n💪 {team_name} 2-POINT CONVERSION! 💪")
        print("💥 Special 2-point celebration starting...")
        start_time = time.time()
        
        # Unique pattern for 2-point conversions
        for i in range(8):
            if i < 4:
                # First 4 flashes: primary color
                await self.flash_color(self.current_primary_color, 0.3)
            else:
                # Last 4 flashes: secondary color
                await self.flash_color(self.current_secondary_color, 0.3)
        
        elapsed = time.time() - start_time
        print(f"💪 2-point conversion celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_safety(self, team_name: str = "TEAM") -> None:
        """Safety celebration - defensive play worth 2 points"""
        print(f"\n🛡️ {team_name} SAFETY! 🛡️")
        print("🔒 Safety celebration starting...")
        start_time = time.time()
        
        # Defensive celebration pattern
        for i in range(6):
            color = self.current_secondary_color if i % 2 == 0 else self.current_primary_color
            await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🛡️ Safety celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_turnover(self, team_name: str = "TEAM", turnover_type: str = "turnover") -> None:
        """Celebration for defensive turnovers (interceptions, fumbles)"""
        print(f"\n🔄 {team_name} {turnover_type.upper()}! 🔄")
        print("🛡️ Defensive turnover celebration starting...")
        start_time = time.time()
        
        # Defensive celebration - emphasize secondary color
        for i in range(8):
            if i % 3 == 0:
                await self.flash_color(self.current_primary_color, 0.3)
            else:
                await self.flash_color(self.current_secondary_color, 0.3)
        
        elapsed = time.time() - start_time
        print(f"🔄 {turnover_type.title()} celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_sack(self, team_name: str = "TEAM") -> None:
        """Sack celebration"""
        print(f"\n⚡ {team_name} SACK! ⚡")
        print("💥 Sack celebration starting...")
        start_time = time.time()
        
        # Quick, aggressive flashes for sacks
        for i in range(6):
            color = self.current_secondary_color if i % 2 == 0 else self.current_primary_color
            await self.flash_color(color, 0.25)
        
        elapsed = time.time() - start_time
        print(f"⚡ Sack celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_big_play(self, team_name: str = "TEAM", play_description: str = "BIG PLAY") -> None:
        """Celebration for big plays (long runs, passes, etc.)"""
        print(f"\n🚀 {team_name} {play_description}! 🚀")
        print("💫 Big play celebration starting...")
        start_time = time.time()
        
        # Moderate celebration for big plays
        for i in range(6):
            color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
            await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🚀 Big play celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_defensive_stop(self, team_name: str = "TEAM") -> None:
        """Celebration for key defensive stops"""
        print(f"\n🛑 {team_name} DEFENSIVE STOP! 🛑")
        print("🛡️ Defensive stop celebration starting...")
        start_time = time.time()
        
        # Subtle celebration for defensive stops
        for i in range(4):
            await self.flash_color(self.current_secondary_color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🛑 Defensive stop celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_victory(self, team_name: str = "TEAM", final_score: str = "") -> None:
        """Epic victory celebration for game wins"""
        print(f"\n🏆 {team_name} VICTORY! 🏆")
        if final_score:
            print(f"🎊 Final Score: {final_score}")
        print("🎉 EPIC VICTORY CELEBRATION STARTING...")
        start_time = time.time()
        
        # Extended victory celebration - 60 seconds of glory
        for cycle in range(10):  # 10 cycles
            for i in range(6):
                color = self.current_primary_color if i % 2 == 0 else self.current_secondary_color
                await self.flash_color(color, 0.3)
        
        elapsed = time.time() - start_time
        print(f"🏆 VICTORY CELEBRATION COMPLETE! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    # RED ZONE AMBIENT LIGHTING
    
    async def start_red_zone_ambient(self, team_name: str = "TEAM") -> None:
        """Start red zone ambient lighting with solid team color"""
        if self.red_zone_active:
            await self.stop_red_zone_ambient()
        
        print(f"🎯 Starting red zone ambient lighting for {team_name}")
        self.red_zone_active = True
        self.red_zone_team = team_name
        
        try:
            # Set solid team primary color at moderate brightness
            r, g, b = self.current_primary_color
            pilot = PilotBuilder(rgb=(r, g, b), brightness=150)
            
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"🎨 Solid color: {self.current_primary_color}")
            
        except Exception as e:
            print(f"❌ Error starting red zone ambient: {e}")
            self.red_zone_active = False

    async def stop_red_zone_ambient(self) -> None:
        """Stop red zone ambient lighting"""
        if not self.red_zone_active:
            return
        
        print(f"🛑 Stopping red zone ambient lighting")
        self.red_zone_active = False
        
        if self.red_zone_task:
            self.red_zone_task.cancel()
            self.red_zone_task = None
        
        # Return to default lighting
        await self.set_default_lighting()
        self.red_zone_team = None