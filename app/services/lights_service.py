"""Async wrapper around SmartStadiumLights hardware controller."""

from __future__ import annotations

from typing import Iterable, Tuple

from src.devices.smart_lights import SmartStadiumLights


class LightsService:
    """Facade that manages the SmartStadiumLights instance."""

    def __init__(self, light_ips: Iterable[str]):
        light_ip_list = list(light_ips)
        if not light_ip_list:
            raise ValueError("LightsService requires at least one light IP")
        self._controller = SmartStadiumLights(light_ip_list)

    async def test_connectivity(self) -> bool:
        return await self._controller.test_connectivity()

    def set_team_colors(self, team_abbr: str, primary: Tuple[int, int, int], secondary: Tuple[int, int, int], sport: str | None = None) -> None:
        self._controller.set_team_colors(team_abbr, primary, secondary, sport=sport)

    async def set_default_lighting(self) -> None:
        await self._controller.set_default_lighting()

    async def celebrate_touchdown(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._controller.celebrate_touchdown(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_field_goal(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._controller.celebrate_field_goal(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_extra_point(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._controller.celebrate_extra_point(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_two_point(self, team_name: str, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._controller.celebrate_two_point(team_name, team_abbr=team_abbr, sport=sport)

    async def celebrate_safety(self, team_name: str) -> None:
        await self._controller.celebrate_safety(team_name)

    async def celebrate_turnover(self, team_name: str, turnover_type: str) -> None:
        await self._controller.celebrate_turnover(team_name, turnover_type)

    async def celebrate_sack(self, team_name: str) -> None:
        await self._controller.celebrate_sack(team_name)

    async def celebrate_big_play(self, team_name: str, play_description: str) -> None:
        await self._controller.celebrate_big_play(team_name, play_description)

    async def celebrate_defensive_stop(self, team_name: str) -> None:
        await self._controller.celebrate_defensive_stop(team_name)

    async def celebrate_victory(self, team_name: str, final_score: str | None = None) -> None:
        await self._controller.celebrate_victory(team_name, final_score or "")

    async def celebrate_score(self, team_name: str, points: int, team_abbr: str | None = None, sport: str | None = None) -> None:
        await self._controller.celebrate_score(team_name, points, team_abbr=team_abbr, sport=sport)

    async def start_red_zone(self, team_abbr: str, sport: str | None = None) -> None:
        await self._controller.start_red_zone_ambient(team_abbr, sport=sport)

    async def stop_red_zone(self) -> None:
        await self._controller.stop_red_zone_ambient()
