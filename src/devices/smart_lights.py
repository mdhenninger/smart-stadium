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
        # Store colors by sport+team: {"nfl:BUF": {...}, "cfb:BUF": {...}}
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
        
        # Track which lights are currently online (set of IPs)
        self._online_lights: set[str] = set()  # Start empty - will be populated by first connectivity check
    
    def set_team_colors(self, team_abbr: str, primary_color: Tuple[int, int, int], 
                       secondary_color: Tuple[int, int, int], sport: Optional[str] = None) -> None:
        """Set team colors for celebrations. 
        
        Args:
            team_abbr: Team abbreviation (e.g., "BUF")
            primary_color: Primary RGB color tuple
            secondary_color: Secondary RGB color tuple
            sport: Optional sport identifier (e.g., "nfl", "cfb") to disambiguate teams with same abbreviation
        """
        # Create unique key: "sport:ABBR" or just "ABBR" if no sport
        key = f"{sport}:{team_abbr}" if sport else team_abbr
        
        # Only log if this is a new team or the colors changed
        is_new_team = key not in self.team_colors
        colors_changed = (not is_new_team and 
                         (self.team_colors[key]['primary'] != primary_color or
                          self.team_colors[key]['secondary'] != secondary_color))
        
        self.team_colors[key] = {
            'primary': primary_color,
            'secondary': secondary_color
        }
        
        # Update current colors for this team
        self.current_primary_color = primary_color
        self.current_secondary_color = secondary_color
        
        # Only log when colors are actually new or changed
        if is_new_team or colors_changed:
            sport_prefix = f"[{sport.upper()}] " if sport else ""
            print(f"🎨 Set {sport_prefix}{team_abbr} colors: {primary_color} / {secondary_color}")
    
    def get_team_colors(self, team_abbr: str, sport: Optional[str] = None) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Get team colors or return current defaults. Prefers lighting-optimized colors for bulb control.
        
        Args:
            team_abbr: Team abbreviation (e.g., "BUF")
            sport: Optional sport identifier to disambiguate (e.g., "nfl", "cfb")
        """
        # Try sport-specific lookup first, then fallback to generic
        keys_to_try = []
        if sport:
            keys_to_try.append(f"{sport}:{team_abbr}")
        keys_to_try.append(team_abbr)
        
        for key in keys_to_try:
            if key in self.team_colors:
                colors = self.team_colors[key]
                # Prefer lighting-optimized colors (pure/bright colors) for bulb visibility
                primary = colors.get('lighting_primary', colors['primary'])
                secondary = colors.get('lighting_secondary', colors['secondary'])
                return primary, secondary
        
        return self.current_primary_color, self.current_secondary_color
    
    async def test_connectivity(self) -> bool:
        """Test connection to all lights. Returns True if ANY lights are responding."""
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
        
        # Return True if at least one light is working
        return success_count > 0
    
    async def test_individual_connectivity(self) -> Dict[str, bool]:
        """Test connection to each light individually and return per-device status.
        
        All lights are checked in parallel to avoid sequential timeout delays.
        
        Returns:
            Dict mapping IP address to online status (True/False)
        """
        async def check_light(ip: str, light: wizlight) -> tuple[str, bool]:
            """Check a single light and return (ip, status)."""
            try:
                # Try to get light state with a timeout
                state = await asyncio.wait_for(light.updateState(), timeout=1.0)
                return (ip, state is not None)
            except asyncio.TimeoutError:
                return (ip, False)
            except Exception:
                return (ip, False)
        
        # Check all lights in parallel
        tasks = [check_light(ip, light) for ip, light in zip(self.light_ips, self.lights)]
        results = await asyncio.gather(*tasks)
        
        # Convert list of tuples to dict
        status_map = dict(results)
        
        # Update cached online lights set
        self._online_lights = {ip for ip, is_online in status_map.items() if is_online}
        
        return status_map

    async def flash_color(self, color: Tuple[int, int, int], duration: float = 0.5) -> None:
        """Flash all lights to a specific color for a duration"""
        try:
            r, g, b = color
            pilot = PilotBuilder(rgb=(r, g, b), brightness=self.celebration_brightness)
            
            # Only send commands to lights we know are online
            tasks = [
                light.turn_on(pilot) 
                for ip, light in zip(self.light_ips, self.lights) 
                if ip in self._online_lights
            ]
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(duration)
        except Exception as e:
            print(f"Error flashing color {color}: {e}")

    async def set_default_lighting(self) -> None:
        """Set lights to warm default lighting - clears RGB mode and sets color temperature"""
        try:
            # Create pilot with ONLY color temp and brightness (no RGB)
            # This forces the lights out of RGB mode into white mode
            pilot = PilotBuilder(colortemp=self.default_color_temp, brightness=self.default_brightness)
            
            # Turn on only online lights with the white pilot
            for ip, light in zip(self.light_ips, self.lights):
                if ip not in self._online_lights:
                    continue  # Skip offline lights
                    
                try:
                    await light.turn_on(pilot)
                    print(f"  ✅ {light.ip} set to {self.default_color_temp}K")
                except Exception as e:
                    print(f"  ❌ {light.ip} error: {e}")
            
            online_count = len(self._online_lights)
            print(f"💡 {online_count} online lights set to warm default lighting ({self.default_color_temp}K, brightness={self.default_brightness})")
        except Exception as e:
            print(f"Error setting default lighting: {e}")

    # CELEBRATION METHODS
    
    async def celebrate_touchdown(self, team_name: str = "TEAM", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_touchdown called for {team_name} ({team_abbr}, {sport})")
        """Epic 12-second touchdown celebration"""
        
        # Stop red zone if active before celebration
        if self.red_zone_active:
            print(f"🛑 Stopping red zone for {team_name} touchdown celebration")
            await self.stop_red_zone_ambient(from_celebration=True)
        
        print(f"\n🏈 {team_name} TOUCHDOWN! 🏈")
        print("🎉 12-second epic celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # Epic celebration sequence - 30 alternating flashes @ 0.4s each = 12 seconds total
        for i in range(30):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Epic Flash {i+1}/30: {color_name}")
            await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🏈 Touchdown celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_field_goal(self, team_name: str = "TEAM", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_field_goal called for {team_name} ({team_abbr}, {sport})")
        """5-second field goal celebration"""
        
        # Stop red zone if active before celebration
        if self.red_zone_active:
            print(f"🛑 Stopping red zone for {team_name} field goal celebration")
            await self.stop_red_zone_ambient(from_celebration=True)
        
        print(f"\n🥅 {team_name} FIELD GOAL! 🥅")
        print("⚡ 5-second celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # 10 alternating flashes @ 0.5s each = 5 seconds total
        for i in range(10):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Field Goal Flash {i+1}/10: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🥅 Field goal celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_extra_point(self, team_name: str = "TEAM", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_extra_point called for {team_name} ({team_abbr}, {sport})")
        """Quick 5-second extra point celebration"""
        print(f"\n✅ {team_name} EXTRA POINT! ✅")
        print("⚡ 5-second quick celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # 5 quick alternating flashes
        for i in range(5):
            color = primary if i % 2 == 0 else secondary
            color_name = "PRIMARY" if i % 2 == 0 else "SECONDARY"
            print(f"   Extra Point Flash {i+1}/5: {color_name}")
            await self.flash_color(color, 0.5)
        
        elapsed = time.time() - start_time
        print(f"✅ Extra point celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_two_point(self, team_name: str = "TEAM", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_two_point called for {team_name} ({team_abbr}, {sport})")
        """Special 5-second two-point conversion celebration"""
        print(f"\n💪 {team_name} 2-POINT CONVERSION! 💪")
        print("💥 Special 2-point celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # Unique pattern for 2-point conversions
        for i in range(8):
            if i < 4:
                # First 4 flashes: primary color
                await self.flash_color(primary, 0.3)
            else:
                # Last 4 flashes: secondary color
                await self.flash_color(secondary, 0.3)
        
        elapsed = time.time() - start_time
        print(f"💪 2-point conversion celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_safety(self, team_name: str = "TEAM") -> None:
        print(f"[DEBUG] celebrate_safety called for {team_name}")
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

    async def celebrate_turnover(self, team_name: str = "TEAM", turnover_type: str = "turnover", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_turnover called for {team_name} ({turnover_type}, {team_abbr}, {sport})")
        """Celebration for defensive turnovers (interceptions, fumbles)"""
        
        # Stop red zone if active before celebration
        if self.red_zone_active:
            print(f"🛑 Stopping red zone for {team_name} turnover celebration")
            await self.stop_red_zone_ambient(from_celebration=True)
        
        print(f"\n🔄 {team_name} {turnover_type.upper()}! 🔄")
        print("🛡️ Defensive turnover celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # Defensive celebration - emphasize secondary color
        for i in range(8):
            if i % 3 == 0:
                await self.flash_color(primary, 0.3)
            else:
                await self.flash_color(secondary, 0.3)
        
        elapsed = time.time() - start_time
        print(f"🔄 {turnover_type.title()} celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_sack(self, team_name: str = "TEAM", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_sack called for {team_name} ({team_abbr}, {sport})")
        """Sack celebration"""
        
        # Stop red zone if active before celebration
        if self.red_zone_active:
            print(f"🛑 Stopping red zone for {team_name} sack celebration")
            await self.stop_red_zone_ambient(from_celebration=True)
        
        print(f"\n⚡ {team_name} SACK! ⚡")
        print("💥 Sack celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # Quick, aggressive flashes for sacks
        for i in range(6):
            color = secondary if i % 2 == 0 else primary
            await self.flash_color(color, 0.25)
        
        elapsed = time.time() - start_time
        print(f"⚡ Sack celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_big_play(self, team_name: str = "TEAM", play_description: str = "BIG PLAY", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_big_play called for {team_name} ({play_description}, {team_abbr}, {sport})")
        """Celebration for big plays (long runs, passes, etc.)"""
        
        # Note: Don't stop red zone for big plays - they can happen during red zone
        
        print(f"\n🚀 {team_name} {play_description}! 🚀")
        print("💫 Big play celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # Moderate celebration for big plays
        for i in range(6):
            color = primary if i % 2 == 0 else secondary
            await self.flash_color(color, 0.4)
        
        elapsed = time.time() - start_time
        print(f"🚀 Big play celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_defensive_stop(self, team_name: str = "TEAM", team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        print(f"[DEBUG] celebrate_defensive_stop called for {team_name} ({team_abbr}, {sport})")
        """Celebration for key defensive stops"""
        
        # Note: Don't stop red zone for defensive stops - they can happen during red zone
        
        print(f"\n🛑 {team_name} DEFENSIVE STOP! 🛑")
        print("🛡️ Defensive stop celebration starting...")
        start_time = time.time()
        
        # Get sport-specific colors if team_abbr provided
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
        # Subtle celebration for defensive stops
        for i in range(4):
            await self.flash_color(secondary, 0.5)
        
        elapsed = time.time() - start_time
        print(f"🛑 Defensive stop celebration complete! ({elapsed:.1f}s)")
        await self.set_default_lighting()

    async def celebrate_victory(self, team_name: str = "TEAM", final_score: str = "") -> None:
        print(f"[DEBUG] celebrate_victory called for {team_name} (final_score={final_score})")
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

    async def celebrate_score(self, team_name: str = "TEAM", points: int = 3, team_abbr: Optional[str] = None, sport: Optional[str] = None) -> None:
        """Generic celebration for any score amount"""
        
        # Stop red zone if active before celebration
        if self.red_zone_active:
            print(f"🛑 Stopping red zone for {team_name} score celebration ({points} pts)")
            await self.stop_red_zone_ambient(from_celebration=True)
        
        print(f"\n🎯 {team_name.upper()} SCORES {points} POINTS! 🎯")
        
        primary, secondary = self.get_team_colors(team_abbr, sport) if team_abbr else (self.current_primary_color, self.current_secondary_color)
        
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
        await self.set_default_lighting()

    # RED ZONE AMBIENT LIGHTING
    
    async def start_red_zone_ambient(self, team_abbr: str = "TEAM", sport: Optional[str] = None) -> None:
        """Start red zone ambient lighting with solid team color
        
        Args:
            team_abbr: Team abbreviation (e.g., "BUF")
            sport: Sport identifier (e.g., "nfl", "cfb") for color disambiguation
        """
        # If already active for the same team, don't restart (prevents flickering)
        if self.red_zone_active and self.red_zone_team == team_abbr:
            return
        
        # If active for a different team, stop first
        if self.red_zone_active:
            await self.stop_red_zone_ambient(from_celebration=False)
        
        print(f"🎯 Starting red zone ambient lighting for {team_abbr}")
        self.red_zone_active = True
        self.red_zone_team = team_abbr
        
        try:
            # Get sport-specific team color for red zone
            primary, _ = self.get_team_colors(team_abbr, sport)
            r, g, b = primary
            pilot = PilotBuilder(rgb=(r, g, b), brightness=150)
            
            tasks = [light.turn_on(pilot) for light in self.lights]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"🎨 Red zone solid color: {primary} for {sport}:{team_abbr}")
            
        except Exception as e:
            print(f"❌ Error starting red zone ambient: {e}")
            self.red_zone_active = False

    async def stop_red_zone_ambient(self, from_celebration: bool = False) -> None:
        """Stop red zone ambient lighting
        
        Args:
            from_celebration: True if called by a celebration (default lighting will be handled by celebration)
                             False if called by monitoring (need to return to default lighting)
        """
        if not self.red_zone_active:
            print("[DEBUG] stop_red_zone_ambient called, but red_zone_active is already False. No action taken.")
            return

        print(f"🛑 Stopping red zone ambient lighting (was active for team: {self.red_zone_team})")
        
        if from_celebration:
            print("📍 Reason: Celebration starting - lights will transition to celebration")
        else:
            print("📍 Reason: Team left red zone - returning to default lighting")
            
        self.red_zone_active = False

        if self.red_zone_task:
            self.red_zone_task.cancel()
            self.red_zone_task = None

        if from_celebration:
            # Celebration will handle the lighting transition
            print("[DEBUG] Red zone stopped, celebration will handle lighting transition.")
        else:
            # No celebration - need to return to default lighting
            print("[DEBUG] Red zone stopped, returning to default lighting.")
            await self.set_default_lighting()
            
        self.red_zone_team = None