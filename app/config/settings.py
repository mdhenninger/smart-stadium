"""Application settings and environment configuration for Smart Stadium backend."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


DEFAULT_POLL_INTERVAL = 7  # seconds
DEFAULT_POLL_PRESETS = [5, 7, 10, 15, 30]


@dataclass(slots=True)
class Settings:
    """Runtime settings resolved from environment variables and defaults."""

    environment: str = field(default_factory=lambda: os.getenv("SMART_STADIUM_ENV", "development"))
    root_dir: Path = field(default_factory=lambda: Path(os.getenv("SMART_STADIUM_ROOT", Path.cwd())))
    config_dir: Path = field(default_factory=lambda: Path(os.getenv("SMART_STADIUM_CONFIG_DIR", "config")))
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("SMART_STADIUM_DATA_DIR", "data")))
    logs_dir: Path = field(default_factory=lambda: Path(os.getenv("SMART_STADIUM_LOG_DIR", "logs")))
    light_ips_env: str | None = field(default_factory=lambda: os.getenv("SMART_STADIUM_LIGHT_IPS"))
    nfl_poll_interval: int = field(default_factory=lambda: int(os.getenv("SMART_STADIUM_NFL_POLL", DEFAULT_POLL_INTERVAL)))
    cfb_poll_interval: int = field(default_factory=lambda: int(os.getenv("SMART_STADIUM_CFB_POLL", DEFAULT_POLL_INTERVAL)))
    poll_presets: List[int] = field(default_factory=lambda: DEFAULT_POLL_PRESETS.copy())
    enable_reload: bool = field(default_factory=lambda: os.getenv("SMART_STADIUM_RELOAD", "false").lower() == "true")

    def resolve_paths(self) -> None:
        """Ensure directories are absolute and exist."""

        if not self.config_dir.is_absolute():
            self.config_dir = (self.root_dir / self.config_dir).resolve()
        if not self.data_dir.is_absolute():
            self.data_dir = (self.root_dir / self.data_dir).resolve()
        if not self.logs_dir.is_absolute():
            self.logs_dir = (self.root_dir / self.logs_dir).resolve()

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def get_light_ips(self) -> list[str] | None:
        """Return optional light IP override from environment."""
        if self.light_ips_env:
            return [ip.strip() for ip in self.light_ips_env.split(",") if ip.strip()]
        return None


def load_settings() -> Settings:
    """Factory that loads, resolves, and returns application settings."""

    settings = Settings()
    settings.resolve_paths()
    return settings
