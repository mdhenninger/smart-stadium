"""
Govee Light Controller for Smart Stadium
Uses Govee's official HTTP API for cloud-based control
"""

import asyncio
import logging
from typing import List, Tuple, Optional
import aiohttp

logger = logging.getLogger(__name__)

class GoveeLightController:
    """Controller for Govee smart lights via cloud API."""
    
    BASE_URL = "https://developer-api.govee.com"
    
    def __init__(self, api_key: str, device_ids: List[str], model: str):
        """
        Initialize Govee controller.
        
        Args:
            api_key: Govee API key from developer portal
            device_ids: List of Govee device IDs (MAC addresses)
            model: Govee model number (e.g., "H6009")
        """
        self.api_key = api_key
        self.device_ids = device_ids
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Govee-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _send_command(self, device_id: str, command: dict) -> bool:
        """
        Send command to a Govee device.
        
        Args:
            device_id: Device MAC address
            command: Command payload
            
        Returns:
            True if successful
        """
        await self._ensure_session()
        
        payload = {
            "device": device_id,
            "model": self.model,
            "cmd": command
        }
        
        try:
            async with self.session.put(
                f"{self.BASE_URL}/v1/devices/control",
                json=payload
            ) as response:
                if response.status == 200:
                    return True
                else:
                    result = await response.json()
                    logger.warning(
                        f"Govee API error for {device_id}: {result.get('message', 'Unknown error')}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error sending command to {device_id}: {e}")
            return False
    
    async def _send_to_all(self, command: dict) -> bool:
        """Send command to all configured devices."""
        tasks = [self._send_command(device_id, command) for device_id in self.device_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        logger.debug(f"Govee command sent to {success_count}/{len(self.device_ids)} devices")
        
        return success_count > 0
    
    async def turn_on(self) -> bool:
        """Turn on all lights."""
        logger.debug("Govee: Turning on")
        command = {"name": "turn", "value": "on"}
        return await self._send_to_all(command)
    
    async def turn_off(self) -> bool:
        """Turn off all lights."""
        logger.debug("Govee: Turning off")
        command = {"name": "turn", "value": "off"}
        return await self._send_to_all(command)
    
    async def set_brightness(self, brightness: int) -> bool:
        """
        Set brightness for all lights.
        
        Args:
            brightness: 0-255 scale
        """
        # Govee API uses 0-100 scale
        govee_brightness = int((brightness / 255) * 100)
        govee_brightness = max(0, min(100, govee_brightness))
        
        logger.debug(f"Govee: Setting brightness to {govee_brightness}%")
        command = {"name": "brightness", "value": govee_brightness}
        return await self._send_to_all(command)
    
    async def set_color(self, r: int, g: int, b: int, brightness: Optional[int] = None) -> bool:
        """
        Set RGB color for all lights.
        
        Args:
            r, g, b: RGB values (0-255)
            brightness: Optional brightness (0-255)
        """
        logger.debug(f"Govee: Setting color to RGB({r}, {g}, {b})")
        
        # Set color
        color_command = {
            "name": "color",
            "value": {"r": r, "g": g, "b": b}
        }
        color_result = await self._send_to_all(color_command)
        
        # Set brightness if provided
        if brightness is not None:
            await self.set_brightness(brightness)
        
        return color_result
    
    async def set_warm_white(self, kelvin: int = 2700, brightness: int = 180) -> bool:
        """
        Set warm white color temperature.
        
        Args:
            kelvin: Color temperature (2000-9000K)
            brightness: Brightness (0-255)
        """
        logger.debug(f"Govee: Setting warm white {kelvin}K @ {brightness}")
        
        # Govee API uses color temp in Kelvin directly
        temp_command = {
            "name": "colorTem",
            "value": kelvin
        }
        temp_result = await self._send_to_all(temp_command)
        
        # Add delay to respect Govee API rate limits
        await asyncio.sleep(0.3)
        
        # Set brightness
        await self.set_brightness(brightness)
        
        return temp_result
    
    async def flash_color(self, r: int, g: int, b: int, duration: float = 0.5) -> bool:
        """
        Flash lights to a color briefly.
        
        Args:
            r, g, b: RGB values
            duration: How long to show the color (seconds)
        """
        logger.debug(f"Govee: Flashing RGB({r}, {g}, {b}) for {duration}s")
        
        # Flash to color at full brightness
        await self.set_color(r, g, b, brightness=255)
        await asyncio.sleep(duration)
        
        return True
    
    async def test_connectivity(self) -> bool:
        """
        Test connection to Govee API.
        
        Returns:
            True if API is reachable and devices are accessible
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.BASE_URL}/v1/devices") as response:
                if response.status == 200:
                    data = await response.json()
                    devices = data.get("data", {}).get("devices", [])
                    
                    # Check if our device IDs are in the response
                    device_ids_found = [d["device"] for d in devices]
                    our_devices = [d for d in self.device_ids if d in device_ids_found]
                    
                    logger.info(f"Govee: Found {len(our_devices)}/{len(self.device_ids)} devices")
                    return len(our_devices) > 0
                else:
                    logger.error(f"Govee API returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Govee connectivity test failed: {e}")
            return False


class GoveeStadiumLights:
    """
    Stadium-specific wrapper for Govee lights.
    Provides same interface as SmartStadiumLights for celebrations.
    """
    
    def __init__(self, api_key: str, device_ids: List[str], model: str):
        self.controller = GoveeLightController(api_key, device_ids, model)
        self.current_primary_color = (0, 51, 141)  # Buffalo Bills blue default
        self.current_secondary_color = (198, 12, 48)  # Buffalo Bills red default
    
    async def close(self):
        """Clean up resources."""
        await self.controller.close()
    
    def set_team_colors(self, primary: Tuple[int, int, int], secondary: Tuple[int, int, int]):
        """Set the team colors for celebrations."""
        self.current_primary_color = primary
        self.current_secondary_color = secondary
        logger.debug(f"Govee: Set team colors - Primary: {primary}, Secondary: {secondary}")
    
    async def set_default_lighting(self) -> bool:
        """Set default warm white lighting."""
        logger.info("Govee: Setting default warm white (2700K @ 180)")
        try:
            # Turn off briefly to reset state, then turn on with warm white
            await self.controller.turn_off()
            await asyncio.sleep(1.0)  # Wait for off command to process
            
            await self.controller.turn_on()
            await asyncio.sleep(0.5)  # Wait for on command
            
            result = await self.controller.set_warm_white(2700, 180)
            logger.info(f"Govee: Default lighting {'set successfully' if result else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Govee: Error setting default lighting: {e}")
            return False
    
    async def test_connectivity(self) -> bool:
        """Test connection to Govee devices."""
        return await self.controller.test_connectivity()
    
    async def flash_color(self, color: Tuple[int, int, int], duration: float = 0.5):
        """Flash a specific color."""
        r, g, b = color
        await self.controller.flash_color(r, g, b, duration)
    
    async def touchdown_celebration(self) -> bool:
        """Touchdown celebration - 30 flashes @ 1.0s, synchronized with WiZ."""
        logger.info("Govee: 🏈 TOUCHDOWN!")
        
        primary = self.current_primary_color
        secondary = self.current_secondary_color
        
        # 30 alternating flashes @ 1.0s each (matches WiZ timing exactly)
        for i in range(30):
            color = primary if i % 2 == 0 else secondary
            await self.controller.set_color(*color, brightness=255)
            await asyncio.sleep(1.0)  # 1 request/second for Govee API rate limit
        
        logger.info("Govee: Touchdown celebration complete (light stays on last color)")
        return True
    
    async def field_goal_celebration(self) -> bool:
        """Field goal celebration - 10 flashes @ 1.0s, synchronized with WiZ."""
        logger.info("Govee: ⚡ Field Goal!")
        
        primary = self.current_primary_color
        secondary = self.current_secondary_color
        
        # 10 alternating flashes @ 1.0s each (matches WiZ timing exactly)
        for i in range(10):
            color = primary if i % 2 == 0 else secondary
            await self.controller.set_color(*color, brightness=255)
            await asyncio.sleep(1.0)  # 1 request/second for Govee API rate limit
        
        logger.info("Govee: Field goal celebration complete (light stays on last color)")
        return True
    
    async def start_red_zone_ambient(self, team_abbr: str, sport: Optional[str] = None) -> bool:
        """
        Start red zone ambient lighting.
        
        Args:
            team_abbr: Team abbreviation
            sport: Sport identifier (for color lookup)
        """
        logger.info(f"Govee: 🚨 RED ZONE - {team_abbr}")
        
        # Use current primary color at medium brightness
        r, g, b = self.current_primary_color
        await self.controller.turn_on()
        await self.controller.set_color(r, g, b, brightness=150)
        return True
    
    async def stop_red_zone_ambient(self) -> bool:
        """Stop red zone lighting and return to default."""
        logger.info("Govee: Red zone ended - returning to default")
        return await self.set_default_lighting()
