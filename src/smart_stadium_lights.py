"""
Smart Stadium Lights Controller - Unified Multi-Sport Celebration System
Supports NFL, College Football, and future sports with consistent celebration patterns
Phase 2.5: Enhanced with smart device management and manual control
"""

import asyncio
import time
import os
import json
import colorsys
from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional
from smart_device_manager import SmartDeviceManager

# Common color constants
WHITE = (255, 255, 255)
BRIGHT_WHITE = (255, 255, 255)
DIM_WHITE = (128, 128, 128)

# Unified Team Color Database - Sport-City-Team format
TEAM_COLORS = {
    # NFL Teams (32 teams)
    'NFL-BUFFALO-BILLS': ((0, 0, 255), (255, 0, 0)),             # Pure Blue & Pure Red
    'NFL-MIAMI-DOLPHINS': ((0, 142, 204), (252, 76, 2)),          # Aqua & Orange  
    'NFL-NEW_ENGLAND-PATRIOTS': ((0, 34, 68), (198, 12, 48)),     # Navy & Red
    'NFL-NEW_YORK-JETS': ((18, 87, 64), (255, 255, 255)),         # Green & White
    'NFL-BALTIMORE-RAVENS': ((26, 25, 95), (158, 124, 12)),       # Purple & Gold
    'NFL-CINCINNATI-BENGALS': ((251, 79, 20), (0, 0, 0)),         # Orange & Black
    'NFL-CLEVELAND-BROWNS': ((49, 29, 0), (255, 60, 0)),          # Brown & Orange
    'NFL-PITTSBURGH-STEELERS': ((255, 182, 18), (0, 0, 0)),       # Gold & Black
    'NFL-HOUSTON-TEXANS': ((3, 32, 47), (167, 25, 48)),           # Navy & Red
    'NFL-INDIANAPOLIS-COLTS': ((0, 44, 95), (255, 255, 255)),     # Blue & White
    'NFL-JACKSONVILLE-JAGUARS': ((0, 103, 120), (215, 162, 42)),  # Teal & Gold
    'NFL-TENNESSEE-TITANS': ((12, 35, 64), (75, 146, 219)),       # Navy & Light Blue
    'NFL-DENVER-BRONCOS': ((251, 79, 20), (0, 34, 68)),           # Orange & Navy
    'NFL-KANSAS_CITY-CHIEFS': ((227, 24, 55), (255, 184, 28)),    # Red & Gold
    'NFL-LAS_VEGAS-RAIDERS': ((165, 172, 175), (0, 0, 0)),        # Silver & Black
    'NFL-LOS_ANGELES-CHARGERS': ((0, 128, 198), (255, 194, 14)),  # Blue & Gold
    'NFL-DALLAS-COWBOYS': ((0, 34, 68), (134, 147, 151)),         # Navy & Silver
    'NFL-NEW_YORK-GIANTS': ((1, 35, 82), (163, 13, 45)),          # Blue & Red
    'NFL-PHILADELPHIA-EAGLES': ((0, 76, 84), (165, 172, 175)),    # Green & Silver
    'NFL-WASHINGTON-COMMANDERS': ((90, 20, 20), (255, 182, 18)),  # Burgundy & Gold
    'NFL-CHICAGO-BEARS': ((11, 22, 42), (200, 56, 3)),            # Navy & Orange
    'NFL-DETROIT-LIONS': ((0, 118, 182), (165, 172, 175)),        # Blue & Silver
    'NFL-GREEN_BAY-PACKERS': ((24, 48, 40), (255, 184, 28)),      # Green & Gold
    'NFL-MINNESOTA-VIKINGS': ((79, 38, 131), (255, 198, 47)),     # Purple & Gold
    'NFL-ATLANTA-FALCONS': ((167, 25, 48), (0, 0, 0)),            # Red & Black
    'NFL-CAROLINA-PANTHERS': ((0, 133, 202), (165, 172, 175)),    # Blue & Silver
    'NFL-NEW_ORLEANS-SAINTS': ((211, 188, 141), (0, 0, 0)),       # Gold & Black
    'NFL-TAMPA_BAY-BUCCANEERS': ((213, 10, 10), (52, 48, 43)),    # Red & Pewter
    'NFL-ARIZONA-CARDINALS': ((151, 35, 63), (255, 255, 255)),    # Red & White
    'NFL-LOS_ANGELES-RAMS': ((0, 53, 148), (255, 209, 0)),        # Blue & Gold
    'NFL-SAN_FRANCISCO-49ERS': ((170, 0, 0), (173, 153, 93)),     # Red & Gold
    'NFL-SEATTLE-SEAHAWKS': ((0, 34, 68), (105, 190, 40)),        # Navy & Green
    
    # College Football Teams (21+ teams)
    'CFB-ALABAMA-CRIMSON_TIDE': ((158, 27, 50), (255, 255, 255)),      # Crimson & White
    'CFB-GEORGIA-BULLDOGS': ((186, 12, 47), (0, 0, 0)),                # Red & Black
    'CFB-OHIO_STATE-BUCKEYES': ((187, 0, 0), (102, 102, 102)),         # Scarlet & Gray
    'CFB-MICHIGAN-WOLVERINES': ((0, 39, 76), (255, 203, 5)),           # Blue & Maize
    'CFB-TEXAS-LONGHORNS': ((191, 87, 0), (255, 255, 255)),            # Burnt Orange & White
    'CFB-OKLAHOMA-SOONERS': ((153, 27, 30), (255, 255, 255)),          # Crimson & Cream
    'CFB-NOTRE_DAME-FIGHTING_IRISH': ((0, 51, 102), (201, 151, 0)),    # Navy & Gold
    'CFB-USC-TROJANS': ((153, 27, 30), (255, 204, 0)),                 # Cardinal & Gold
    'CFB-FLORIDA-GATORS': ((0, 33, 165), (255, 103, 0)),               # Blue & Orange
    'CFB-LSU-TIGERS': ((70, 29, 124), (253, 208, 35)),                 # Purple & Gold
    'CFB-AUBURN-TIGERS': ((12, 35, 64), (232, 119, 34)),               # Navy & Orange
    'CFB-CLEMSON-TIGERS': ((245, 102, 0), (82, 45, 128)),              # Orange & Purple
    'CFB-PENN_STATE-NITTANY_LIONS': ((4, 30, 66), (255, 255, 255)),    # Navy & White
    'CFB-WISCONSIN-BADGERS': ((197, 5, 12), (255, 255, 255)),          # Red & White
    'CFB-OREGON-DUCKS': ((0, 71, 49), (254, 225, 35)),                 # Green & Yellow
    'CFB-MIAMI-HURRICANES': ((240, 81, 35), (0, 71, 27)),              # Orange & Green
    'CFB-TENNESSEE-VOLUNTEERS': ((255, 130, 0), (255, 255, 255)),      # Orange & White
    'CFB-KENTUCKY-WILDCATS': ((0, 51, 160), (255, 255, 255)),          # Blue & White
    'CFB-ARKANSAS-RAZORBACKS': ((157, 34, 53), (255, 255, 255)),       # Red & White
    'CFB-MISSISSIPPI-REBELS': ((20, 35, 75), (206, 17, 65)),           # Navy & Red
    'CFB-SOUTH_CAROLINA-GAMECOCKS': ((115, 0, 10), (255, 255, 255)),   # Garnet & White
}

# Team Key Mapping - Convert common abbreviations to unified keys
TEAM_KEY_MAPPING = {
    # NFL abbreviations
    'BUF': 'NFL-BUFFALO-BILLS',
    'MIA': 'NFL-MIAMI-DOLPHINS', 
    'NE': 'NFL-NEW_ENGLAND-PATRIOTS',
    'NYJ': 'NFL-NEW_YORK-JETS',
    'BAL': 'NFL-BALTIMORE-RAVENS',
    'CIN': 'NFL-CINCINNATI-BENGALS',
    'CLE': 'NFL-CLEVELAND-BROWNS',
    'PIT': 'NFL-PITTSBURGH-STEELERS',
    'HOU': 'NFL-HOUSTON-TEXANS',
    'IND': 'NFL-INDIANAPOLIS-COLTS',
    'JAX': 'NFL-JACKSONVILLE-JAGUARS',
    'TEN': 'NFL-TENNESSEE-TITANS',
    'DEN': 'NFL-DENVER-BRONCOS',
    'KC': 'NFL-KANSAS_CITY-CHIEFS',
    'LV': 'NFL-LAS_VEGAS-RAIDERS',
    'LAC': 'NFL-LOS_ANGELES-CHARGERS',
    'DAL': 'NFL-DALLAS-COWBOYS',
    'NYG': 'NFL-NEW_YORK-GIANTS',
    'PHI': 'NFL-PHILADELPHIA-EAGLES',
    'WAS': 'NFL-WASHINGTON-COMMANDERS',
    'CHI': 'NFL-CHICAGO-BEARS',
    'DET': 'NFL-DETROIT-LIONS',
    'GB': 'NFL-GREEN_BAY-PACKERS',
    'MIN': 'NFL-MINNESOTA-VIKINGS',
    'ATL': 'NFL-ATLANTA-FALCONS',
    'CAR': 'NFL-CAROLINA-PANTHERS',
    'NO': 'NFL-NEW_ORLEANS-SAINTS',
    'TB': 'NFL-TAMPA_BAY-BUCCANEERS',
    'ARI': 'NFL-ARIZONA-CARDINALS',
    'LAR': 'NFL-LOS_ANGELES-RAMS',
    'SF': 'NFL-SAN_FRANCISCO-49ERS',
    'SEA': 'NFL-SEATTLE-SEAHAWKS',
    
    # College team name mappings
    'Alabama': 'CFB-ALABAMA-CRIMSON_TIDE',
    'Georgia': 'CFB-GEORGIA-BULLDOGS',
    'Ohio State': 'CFB-OHIO_STATE-BUCKEYES',
    'Michigan': 'CFB-MICHIGAN-WOLVERINES',
    'Texas': 'CFB-TEXAS-LONGHORNS',
    'Oklahoma': 'CFB-OKLAHOMA-SOONERS',
    'Notre Dame': 'CFB-NOTRE_DAME-FIGHTING_IRISH',
    'USC': 'CFB-USC-TROJANS',
    'Florida': 'CFB-FLORIDA-GATORS',
    'LSU': 'CFB-LSU-TIGERS',
    'Auburn': 'CFB-AUBURN-TIGERS',
    'Clemson': 'CFB-CLEMSON-TIGERS',
    'Penn State': 'CFB-PENN_STATE-NITTANY_LIONS',
    'Wisconsin': 'CFB-WISCONSIN-BADGERS',
    'Oregon': 'CFB-OREGON-DUCKS',
    'Miami': 'CFB-MIAMI-HURRICANES',
    'Tennessee': 'CFB-TENNESSEE-VOLUNTEERS',
    'Kentucky': 'CFB-KENTUCKY-WILDCATS',
    'Arkansas': 'CFB-ARKANSAS-RAZORBACKS',
    'Mississippi': 'CFB-MISSISSIPPI-REBELS',
    'South Carolina': 'CFB-SOUTH_CAROLINA-GAMECOCKS',
}

class SmartStadiumLights:
    """
    Unified Smart Stadium Light Controller
    Handles celebrations for all sports with consistent patterns and timing
    Phase 2.4b: Enhanced with multi-brand device support
    """
    
    def __init__(self, light_ips: List[str] = None, govee_api_key: str = None):
        # Initialize smart device manager for better control
        self.device_manager = SmartDeviceManager()
        
        # Legacy support for direct IP list (migrate to device manager)
        if light_ips:
            self._migrate_legacy_ips(light_ips)
        
        # Set Govee API key if provided
        if govee_api_key:
            self.device_manager.govee_api_key = govee_api_key
            self.device_manager.save_device_config()
        
        # Team color management
        self.current_team_key = 'NFL-BUFFALO-BILLS'  # Default to Bills
        self.current_primary_color = TEAM_COLORS[self.current_team_key][0]
        self.current_secondary_color = TEAM_COLORS[self.current_team_key][1]
        
        # Red zone ambient lighting state
        self.red_zone_active = False
        self.red_zone_team = None
        self.red_zone_task = None
        
        # Device initialization flag
        self.devices_initialized = False
        
        print(f"🏟️ Smart Stadium Lights initialized")
        print(f"🎨 Default team: {self.current_team_key}")
        print(f"� Device manager: {len(self.device_manager.get_enabled_devices())} enabled devices")
    
    def _migrate_legacy_ips(self, light_ips: List[str]):
        """Migrate legacy IP list to device manager"""
        print(f"🔄 Migrating {len(light_ips)} legacy IP addresses...")
        
        for i, ip in enumerate(light_ips):
            # Check if this IP is already managed
            existing = next((d for d in self.device_manager.managed_devices if d.ip_address == ip), None)
            
            if not existing:
                from smart_device_manager import ManagedDevice
                device = ManagedDevice(
                    id=f"wiz_{ip.replace('.', '_')}",
                    name=f"WiZ Light {i+1} ({ip})",
                    brand='wiz',
                    ip_address=ip,
                    enabled=True,
                    notes="Migrated from legacy initialization"
                )
                self.device_manager.managed_devices.append(device)
        
        self.device_manager.save_device_config()
        print(f"✅ Migration complete")
    
    async def initialize_devices(self):
        """Initialize and check status of managed devices"""
        if self.devices_initialized:
            return
        
        print("\n🚀 INITIALIZING SMART STADIUM DEVICES")
        print("=" * 45)
        
        # Check status of all enabled devices (this will refresh timestamps)
        status_results = await self.device_manager.check_all_enabled_devices()
        
        online_count = sum(1 for status in status_results.values() if status)
        total_enabled = len([d for d in self.device_manager.managed_devices if d.enabled])
        print(f"🏟️ Smart Stadium ready with {online_count}/{total_enabled} devices online")
        
        if online_count == 0:
            print("⚠️ Warning: No devices are online. Celebrations may not work.")
        elif online_count < total_enabled:
            print(f"ℹ️ {total_enabled - online_count} devices are offline but system will continue with available devices")
        
        self.devices_initialized = True
    
    async def get_device_summary(self):
        """Get summary of all connected devices"""
        return self.device_manager.get_device_summary()
    
    async def get_active_light_manager(self):
        """Get the active light manager with enabled devices"""
        return await self.device_manager.get_active_light_manager()
    
    def resolve_team_key(self, team_identifier: str) -> str:
        """
        Convert various team identifiers to unified team key format
        Examples: 'BUF' -> 'NFL-BUFFALO-BILLS', 'Alabama' -> 'CFB-ALABAMA-CRIMSON_TIDE'
        """
        # Direct key match
        if team_identifier in TEAM_COLORS:
            return team_identifier
            
        # Mapping lookup
        if team_identifier in TEAM_KEY_MAPPING:
            return TEAM_KEY_MAPPING[team_identifier]
            
        # Fallback to current team if not found
        print(f"⚠️ Team '{team_identifier}' not found, using current team: {self.current_team_key}")
        return self.current_team_key
    
    def set_team(self, team_identifier: str) -> None:
        """
        Set the current team for celebrations
        Accepts team abbreviations, full names, or unified keys
        """
        team_key = self.resolve_team_key(team_identifier)
        
        if team_key in TEAM_COLORS:
            self.current_team_key = team_key
            self.current_primary_color = TEAM_COLORS[team_key][0]
            self.current_secondary_color = TEAM_COLORS[team_key][1]
            print(f"🎨 Team set to: {team_key}")
            print(f"   Primary: {self.current_primary_color}")
            print(f"   Secondary: {self.current_secondary_color}")
        else:
            print(f"❌ Team key '{team_key}' not found in database")
    
    def get_team_colors(self, team_identifier: str = None) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Get team colors for any team
        Returns (primary_color, secondary_color) tuple
        """
        if team_identifier is None:
            return self.current_primary_color, self.current_secondary_color
            
        team_key = self.resolve_team_key(team_identifier)
        if team_key in TEAM_COLORS:
            return TEAM_COLORS[team_key]
        else:
            # Fallback to current team
            return self.current_primary_color, self.current_secondary_color
    
    def get_current_team_info(self):
        """Get current team information for API responses"""
        # Try to import Team model, create basic dict if not available
        try:
            import sys
            import os
            api_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api')
            if api_dir not in sys.path:
                sys.path.insert(0, api_dir)
            from models import Team
            use_model = True
        except (ImportError, ModuleNotFoundError):
            use_model = False
        
        # Parse current team key
        parts = self.current_team_key.split('-')
        if len(parts) >= 3:
            league = parts[0]
            city = parts[1].replace('_', ' ').title()
            name = '-'.join(parts[2:]).replace('_', ' ').title()
            full_name = f"{city} {name}"
        else:
            league = "NFL"
            city = "Buffalo"
            name = "Bills"
            full_name = "Buffalo Bills"
        
        if use_model:
            return Team(
                id=self.current_team_key,
                league=league,
                city=city,
                name=name,
                full_name=full_name,
                primary_color=self.current_primary_color,
                secondary_color=self.current_secondary_color
            )
        else:
            # Return basic dict if model not available
            return {
                'id': self.current_team_key,
                'league': league,
                'city': city,
                'name': name,
                'full_name': full_name,
                'primary_color': self.current_primary_color,
                'secondary_color': self.current_secondary_color
            }
    
    def get_team_info(self, team_key: str):
        """Get team information for any team"""
        if team_key not in TEAM_COLORS:
            return None
            
        colors = TEAM_COLORS[team_key]
        parts = team_key.split('-')
        
        if len(parts) >= 3:
            league = parts[0]
            city = parts[1].replace('_', ' ').title()
            name = '-'.join(parts[2:]).replace('_', ' ').title()
            full_name = f"{city} {name}"
        else:
            league = "NFL"
            city = "Unknown"
            name = "Team"
            full_name = "Unknown Team"
        
        return {
            'id': team_key,
            'league': league,
            'city': city,
            'name': name,
            'full_name': full_name,
            'primary_color': colors[0],
            'secondary_color': colors[1]
        }
    
    def enhance_color(self, rgb_color: Tuple[int, int, int], saturation_boost: float = 1.3, brightness_boost: float = 1.0) -> Tuple[int, int, int]:
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

    async def flash_color(self, color: Tuple[int, int, int], duration: float = 0.5) -> None:
        """Flash all lights to a specific color for a duration"""
        try:
            # Ensure devices are initialized
            if not self.devices_initialized:
                await self.initialize_devices()
            
            # Get active light manager
            light_manager = await self.get_active_light_manager()
            
            # Enhance the color for better visibility
            enhanced_color = light_manager.enhance_color(color)
            
            # Flash all devices using unified manager
            await light_manager.flash_all_color(enhanced_color, duration, brightness=255)
            
        except Exception as e:
            print(f"Error flashing color {color}: {e}")

    async def set_default_lighting(self) -> None:
        """Set lights to warm default lighting (2700K)"""
        try:
            # Ensure devices are initialized
            if not self.devices_initialized:
                await self.initialize_devices()
            
            # Get active light manager
            light_manager = await self.get_active_light_manager()
            
            # Set all lights to default 2700K using unified manager
            await light_manager.set_all_default_lighting()
            
        except Exception as e:
            print(f"Error setting default lighting: {e}")

    # ========================================
    # UNIFIED CELEBRATION METHODS
    # ========================================

    async def celebrate_touchdown(self, team_identifier: str = None) -> None:
        """Epic 30-second touchdown celebration"""
        # Set team colors if provided
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🏈 {team_display} TOUCHDOWN! 🏈")
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

    async def celebrate_field_goal(self, team_identifier: str = None) -> None:
        """10-second field goal celebration"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🥅 {team_display} FIELD GOAL! 🥅")
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

    async def celebrate_extra_point(self, team_identifier: str = None) -> None:
        """Quick 5-second extra point celebration"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n✅ {team_display} EXTRA POINT! ✅")
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

    async def celebrate_two_point(self, team_identifier: str = None) -> None:
        """Special 10-second two-point conversion celebration"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n💪 {team_display} 2-POINT CONVERSION! 💪")
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

    async def celebrate_safety(self, team_identifier: str = None) -> None:
        """15-second safety celebration - rare but awesome"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🛡️ {team_display} SAFETY! 🛡️")
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

    async def celebrate_victory(self, team_identifier: str = None) -> None:
        """Epic 60-second victory celebration"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🏆 {team_display} VICTORY! 🏆")
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

    async def celebrate_turnover(self, team_identifier: str = None) -> None:
        """10-second turnover celebration - defensive highlight"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🔄 {team_display} TURNOVER! 🔄")
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

    async def celebrate_big_play(self, team_identifier: str = None, play_type: str = "") -> None:
        """5-second big play celebration - 40+ yard rushing/passing plays only"""
        # Skip field goals - only celebrate rushing/passing big plays
        if 'field goal' in play_type.lower() or 'fg' in play_type.lower():
            print(f"\n⚠️ Skipping big play celebration for field goal: {play_type}")
            return
            
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🏃‍♂️ {team_display} BIG PLAY! 🏃‍♂️")
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

    async def celebrate_defensive_stop(self, team_identifier: str = None) -> None:
        """5-second defensive stop celebration - 4th down stops"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🛡️ {team_display} DEFENSIVE STOP! 🛡️")
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

    async def celebrate_sack(self, team_identifier: str = None) -> None:
        """2-second sack celebration - QB pressure"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n⚡ {team_display} SACK! ⚡")
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

    async def celebrate_red_zone(self, team_identifier: str = None) -> None:
        """Red zone ambient lighting - entering scoring territory"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🎯 {team_display} RED ZONE! 🎯")
        print("🔥 Starting red zone ambient lighting...")
        start_time = time.time()
        
        try:
            # Ensure devices are initialized
            if not self.devices_initialized:
                await self.initialize_devices()
            
            # Get active light manager
            light_manager = await self.get_active_light_manager()
            
            # Step 1: Bright white flash
            print("   Red Zone Step 1/3: Bright white flash")
            await light_manager.flash_all_color(BRIGHT_WHITE, duration=0.5, brightness=255)
            
            # Step 2: Transition to team primary color
            print(f"   Red Zone Step 2/3: Transition to team color")
            enhanced_color = light_manager.enhance_color(self.current_primary_color)
            await light_manager.flash_all_color(enhanced_color, duration=0.5, brightness=200)
            
            # Step 3: Hold steady at team color (ambient level)
            print(f"   Red Zone Step 3/3: Hold steady ambient")
            # For ambient lighting, we'll use a longer duration flash that doesn't return to default
            await light_manager.flash_all_color(enhanced_color, duration=0.1, brightness=150)
            
            # Update red zone state
            self.red_zone_active = True
            self.red_zone_team = self.current_team_key
            
            elapsed = time.time() - start_time
            print(f"🎯 Red zone ambient lighting active! ({elapsed:.1f}s)")
            print(f"🎨 Holding steady at {self.current_primary_color} (brightness 150)")
            
        except Exception as e:
            print(f"❌ Error setting red zone ambient: {e}")
            # Fallback to default lighting
            await self.set_default_lighting()

    async def celebrate_generic_score(self, points: int = 3, team_identifier: str = None) -> None:
        """Generic celebration for unusual scoring plays"""
        if team_identifier:
            self.set_team(team_identifier)
            
        team_display = self.current_team_key.replace('_', ' ').replace('-', ' ')
        print(f"\n🎯 {team_display} SCORED {points} POINTS! 🎯")
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

    # ========================================
    # UTILITY AND TESTING METHODS
    # ========================================

    async def stop_red_zone_ambient(self) -> None:
        """Stop red zone ambient lighting"""
        if self.red_zone_active:
            self.red_zone_active = False
            print("🎯 Red zone ambient lighting stopped")
            await self.set_default_lighting()

    async def test_connectivity(self) -> bool:
        """Test if all lights are responding"""
        print("🧪 Testing light connectivity...")
        try:
            # Ensure devices are initialized
            if not self.devices_initialized:
                await self.initialize_devices()
            
            # Get active light manager
            light_manager = await self.get_active_light_manager()
            
            # Get device summary to check connectivity
            summary = await light_manager.get_device_summary()
            
            online_count = summary['online_devices']
            total_count = summary['total_devices']
            
            if online_count == total_count and total_count > 0:
                print("✅ All lights responding!")
                return True
            elif online_count > 0:
                print(f"⚠️ {online_count}/{total_count} lights responding")
                return True
            else:
                print("❌ No lights responding!")
                return False
                
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            return False

    async def test_all_celebrations(self, team_identifier: str = None) -> None:
        """Test all celebration types in sequence"""
        if team_identifier:
            self.set_team(team_identifier)
            
        print("\n🧪 TESTING ALL SMART STADIUM CELEBRATIONS 🧪")
        print("=" * 55)
        print(f"🎨 Testing with team: {self.current_team_key}")
        
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
        
        print("\n🧪 All Smart Stadium celebration tests complete!")

    def list_available_teams(self, sport: str = None) -> None:
        """List all available teams, optionally filtered by sport"""
        print(f"\n🏟️ SMART STADIUM TEAM DATABASE")
        print("=" * 50)
        
        if sport:
            sport_upper = sport.upper()
            filtered_teams = {k: v for k, v in TEAM_COLORS.items() if k.startswith(f"{sport_upper}-")}
            print(f"📋 {sport.upper()} Teams ({len(filtered_teams)} total):")
        else:
            filtered_teams = TEAM_COLORS
            print(f"📋 All Teams ({len(filtered_teams)} total):")
        
        for team_key in sorted(filtered_teams.keys()):
            primary, secondary = filtered_teams[team_key]
            display_name = team_key.replace('_', ' ').replace('-', ' ')
            print(f"   {team_key:<35} | {display_name}")
            print(f"   {'':35} | Primary: {primary} | Secondary: {secondary}")


# ========================================
# ABSTRACT BASE SPORT MONITOR
# ========================================

class BaseSportMonitor(ABC):
    """
    Abstract base class for sport-specific monitoring systems
    Provides common interface and functionality for all sports
    """
    
    def __init__(self, lights_controller: SmartStadiumLights):
        self.lights_controller = lights_controller
        self.monitoring = False
        self.monitored_games = []
        self.game_scores = {}
        self.red_zone_status = {}
        self.last_play_ids = {}
        
    @abstractmethod
    async def get_games_today(self) -> List[Dict]:
        """Get all games for today - must be implemented by each sport"""
        pass
        
    @abstractmethod
    async def monitor_game(self, game_id: str) -> None:
        """Monitor a specific game - must be implemented by each sport"""
        pass
        
    @abstractmethod
    def map_team_to_unified_key(self, sport_team_name: str) -> str:
        """Map sport-specific team name to unified team key"""
        pass
        
    async def start_monitoring(self, game_ids: List[str]) -> None:
        """Start monitoring multiple games"""
        self.monitoring = True
        self.monitored_games = game_ids
        print(f"🏟️ Starting monitoring for {len(game_ids)} games")
        
        # Start monitoring tasks for each game
        tasks = [self.monitor_game(game_id) for game_id in game_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def stop_monitoring(self) -> None:
        """Stop all monitoring"""
        self.monitoring = False
        print("⏹️ Monitoring stopped")


# ========================================
# CONFIGURATION LOADING
# ========================================

def load_smart_stadium_config() -> Dict:
    """Load unified Smart Stadium configuration"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'smart_stadium_config.json')
    
    # Default configuration
    default_config = {
        'lights': {
            'wiz_ips': [],
            'govee_devices': []
        },
        'teams': {
            'priority_teams': ['NFL-BUFFALO-BILLS'],
            'secondary_teams': []
        },
        'monitoring': {
            'nfl_enabled': True,
            'college_enabled': True,
            'api_timeout': 10
        },
        'celebrations': {
            'volume': 'normal',  # quiet, normal, loud
            'red_zone_ambient': True
        }
    }
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Merge with defaults
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
    except FileNotFoundError:
        print(f"⚠️ Config file not found at {config_path}, using defaults")
        return default_config
    except Exception as e:
        print(f"❌ Error loading config: {e}, using defaults")
        return default_config