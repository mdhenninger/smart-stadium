"""Async wrapper around SmartStadiumLights hardware controller."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Iterable, Tuple

from src.devices.smart_lights import SmartStadiumLights

logger = logging.getLogger(__name__)


class LightsService:
    """Facade that manages WiZ light controllers."""

    def __init__(self, light_ips: Iterable[str], govee_config: dict | None = None):
        """Initialize lights service with WiZ lights only."""
        light_ip_list = list(light_ips)
        if not light_ip_list:
            raise ValueError("LightsService requires at least one WiZ light IP address")
        
        # WiZ lights controller (only controller now)
        self._controller = SmartStadiumLights(light_ip_list)
        logger.info(f"Initialized WiZ controller with {len(light_ip_list)} lights")

    async def test_connectivity(self) -> bool:
        """Test connectivity to light system."""
        return await self._controller.test_connectivity()
    
    async def test_individual_connectivity(self, enabled_ips: list[str] | None = None) -> Dict[str, bool]:
        """Test connectivity to each light individually.
        
        Args:
            enabled_ips: Optional list of IPs to check. If None, checks all lights.
        
        Returns:
            Dict mapping IP address to online status (True/False)
        """
        if enabled_ips is None:
            return await self._controller.test_individual_connectivity()
        
        # Only check enabled IPs
        all_statuses = await self._controller.test_individual_connectivity()
        return {ip: status for ip, status in all_statuses.items() if ip in enabled_ips}

    def set_team_colors(self, team_abbr: str, primary: Tuple[int, int, int], secondary: Tuple[int, int, int], sport: str | None = None) -> None:
        """Set team colors on controller."""
        self._controller.set_team_colors(team_abbr, primary, secondary, sport=sport)

    async def set_default_lighting(self) -> None:
        """Set default warm white lighting."""
        await self._controller.set_default_lighting()

    async def celebrate_touchdown(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a touchdown."""
        await self._controller.celebrate_touchdown(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_field_goal(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a field goal."""
        await self._controller.celebrate_field_goal(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_extra_point(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate an extra point."""
        await self._controller.celebrate_extra_point(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_two_point(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a two-point conversion."""
        await self._controller.celebrate_two_point(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_safety(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a safety."""
        await self._controller.celebrate_safety(team_name)

    async def celebrate_turnover(self, team_name: str, turnover_type: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a turnover."""
        await self._controller.celebrate_turnover(team_name, turnover_type, team_abbr=team_abbr, sport=sport)

    async def celebrate_sack(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a sack."""
        await self._controller.celebrate_sack(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_big_play(self, team_name: str, play_description: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a big play."""
        await self._controller.celebrate_big_play(team_name, play_description, team_abbr=team_abbr, sport=sport)

    async def celebrate_defensive_stop(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a defensive stop."""
        await self._controller.celebrate_defensive_stop(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_victory(self, team_name: str, final_score: str | None = None) -> None:
        """Celebrate a victory."""
        await self._controller.celebrate_victory(team_name, final_score or "")

    async def celebrate_score(self, team_name: str, points: int, team_abbr: str | None = None, sport: str | None = None) -> None:
        """Celebrate a score based on points."""
        if points >= 6:
            await self.celebrate_touchdown(team_name, team_abbr=team_abbr, sport=sport)
        else:
            await self.celebrate_field_goal(team_name, team_abbr=team_abbr, sport=sport)

    async def start_red_zone(self, team_abbr: str, sport: str | None = None) -> None:
        """Start red zone ambient lighting."""
        await self._controller.start_red_zone_ambient(team_abbr, sport=sport)

    async def stop_red_zone(self) -> None:
        """Stop red zone ambient lighting."""
        await self._controller.stop_red_zone_ambient()
