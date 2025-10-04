"""Async wrapper around SmartStadiumLights hardware controller."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable, Tuple, Optional

from src.devices.smart_lights import SmartStadiumLights
from src.devices.govee_lights import GoveeStadiumLights

logger = logging.getLogger(__name__)


class LightsService:
    """Facade that manages both WiZ and Govee light controllers."""

    def __init__(self, light_ips: Iterable[str], govee_config: Optional[dict] = None):
        light_ip_list = list(light_ips)
        if not light_ip_list and not govee_config:
            raise ValueError("LightsService requires at least one light (WiZ or Govee)")
        
        # WiZ lights controller
        self._wiz_controller: Optional[SmartStadiumLights] = None
        if light_ip_list:
            self._wiz_controller = SmartStadiumLights(light_ip_list)
            logger.info(f"Initialized WiZ controller with {len(light_ip_list)} lights")
        
        # Govee lights controller
        self._govee_controller: Optional[GoveeStadiumLights] = None
        if govee_config:
            api_key = govee_config.get("api_key", "")
            devices = govee_config.get("devices", [])
            enabled_devices = [d for d in devices if d.get("enabled", True)]
            
            if api_key and enabled_devices:
                device_ids = [d["device_id"] for d in enabled_devices]
                model = enabled_devices[0].get("model", "H6009")  # Use first device's model
                
                self._govee_controller = GoveeStadiumLights(api_key, device_ids, model)
                logger.info(f"Initialized Govee controller with {len(device_ids)} lights")
        
        # Determine primary controller for team color updates
        self._primary_controller = self._wiz_controller if self._wiz_controller else self._govee_controller

    async def test_connectivity(self) -> bool:
        """Test connectivity to all light systems."""
        tasks = []
        if self._wiz_controller:
            tasks.append(self._wiz_controller.test_connectivity())
        if self._govee_controller:
            tasks.append(self._govee_controller.test_connectivity())
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return any(r is True for r in results)

    def set_team_colors(self, team_abbr: str, primary: Tuple[int, int, int], secondary: Tuple[int, int, int], sport: str | None = None) -> None:
        """Set team colors on all controllers."""
        if self._wiz_controller:
            self._wiz_controller.set_team_colors(team_abbr, primary, secondary, sport=sport)
        if self._govee_controller:
            self._govee_controller.set_team_colors(primary, secondary)

    async def set_default_lighting(self) -> None:
        """Set default warm white lighting on all systems."""
        tasks = []
        if self._wiz_controller:
            tasks.append(self._wiz_controller.set_default_lighting())
        if self._govee_controller:
            tasks.append(self._govee_controller.set_default_lighting())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_on_all(self, method_name: str, *args, **kwargs):
        """Helper to run a method on all available controllers."""
        tasks = []
        if self._wiz_controller and hasattr(self._wiz_controller, method_name):
            tasks.append(getattr(self._wiz_controller, method_name)(*args, **kwargs))
        if self._govee_controller and hasattr(self._govee_controller, method_name):
            tasks.append(getattr(self._govee_controller, method_name)(*args, **kwargs))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def celebrate_touchdown(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_field_goal(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._run_on_all("field_goal_celebration")

    async def celebrate_extra_point(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        # Map to touchdown for now (Govee uses touchdown_celebration)
        await self._run_on_all("touchdown_celebration")

    async def celebrate_two_point(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_safety(self, team_name: str) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_turnover(self, team_name: str, turnover_type: str) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_sack(self, team_name: str) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_big_play(self, team_name: str, play_description: str) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_defensive_stop(self, team_name: str) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_victory(self, team_name: str, final_score: str | None = None) -> None:
        await self._run_on_all("touchdown_celebration")

    async def celebrate_score(self, team_name: str, points: int, team_abbr: str | None = None, sport: str | None = None) -> None:
        if points >= 6:
            await self._run_on_all("touchdown_celebration")
        else:
            await self._run_on_all("field_goal_celebration")

    async def start_red_zone(self, team_abbr: str, sport: str | None = None) -> None:
        if self._wiz_controller:
            await self._wiz_controller.start_red_zone_ambient(team_abbr, sport=sport)
        if self._govee_controller:
            await self._govee_controller.start_red_zone_ambient(team_abbr, sport=sport)

    async def stop_red_zone(self) -> None:
        await self._run_on_all("stop_red_zone_ambient")
