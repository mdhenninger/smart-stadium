"""High-level configuration manager combining JSON sources and environment settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from app.config.loaders import (
    load_celebrations,
    load_govee_config,
    load_stadium_config,
    load_team_colors,
    load_teams_database,
    load_wiz_config,
    ConfigLoadError,
)
from app.config.settings import Settings


@dataclass(slots=True)
class AppConfig:
    stadium: Dict[str, Any]
    team_colors: Dict[str, Any]
    teams_database: Dict[str, Any]
    celebrations: Dict[str, Any]
    wiz_config: Dict[str, Any]
    govee_config: Dict[str, Any]
    light_ips: List[str]

    @property
    def nfl_poll_interval(self) -> int:
        monitoring = self.stadium.get("monitoring", {})
        return int(monitoring.get("default_polling_interval", 7))

    def get_favorite_teams(self, sport: str) -> List[str]:
        monitoring = self.stadium.get("monitoring", {})
        favorites = monitoring.get("favorite_teams", {})
        return favorites.get(sport, [])

    def get_sports_enabled(self) -> Dict[str, bool]:
        monitoring = self.stadium.get("monitoring", {})
        return monitoring.get("sports_enabled", {})


class ConfigManager:
    """Service that loads and caches merged configuration."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._config: AppConfig | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    def refresh(self) -> AppConfig:
        stadium = load_stadium_config(self._settings)
        team_colors = load_team_colors(self._settings)
        teams_database = load_teams_database(self._settings)
        celebrations = load_celebrations(self._settings)

        try:
            wiz_config = load_wiz_config(self._settings)
        except ConfigLoadError:
            wiz_config = {"devices": []}

        try:
            govee_config = load_govee_config(self._settings)
        except ConfigLoadError:
            govee_config = {"api_key": "", "devices": []}

        light_ips = self._settings.get_light_ips()
        if light_ips is None:
            light_ips = _extract_light_ips(stadium, wiz_config)

        self._config = AppConfig(
            stadium=stadium,
            team_colors=team_colors,
            teams_database=teams_database,
            celebrations=celebrations,
            wiz_config=wiz_config,
            govee_config=govee_config,
            light_ips=light_ips,
        )
        return self._config

    def get_config(self) -> AppConfig:
        if self._config is None:
            return self.refresh()
        return self._config


def _extract_light_ips(stadium: Dict[str, Any], wiz_config: Dict[str, Any]) -> List[str]:
    ips: List[str] = []

    devices = stadium.get("devices", {})
    smart_lights = devices.get("smart_lights", {})
    ips.extend(smart_lights.get("ips", []))

    for entry in wiz_config.get("devices", []):
        ip = entry.get("ip")
        if isinstance(ip, str) and ip not in ips:
            ips.append(ip)

    # Filter empty strings just in case
    return [ip for ip in ips if ip]
