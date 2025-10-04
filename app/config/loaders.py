"""Configuration loading utilities for Smart Stadium."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .settings import Settings


class ConfigLoadError(RuntimeError):
    """Raised when configuration files cannot be loaded or parsed."""


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigLoadError(f"Missing configuration file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigLoadError(f"Invalid JSON in configuration file: {path}") from exc


def load_stadium_config(settings: Settings) -> Dict[str, Any]:
    """Load primary stadium configuration."""

    return _read_json(settings.config_dir / "stadium_config.json")


def load_team_colors(settings: Settings) -> Dict[str, Any]:
    """Load team colors configuration."""

    return _read_json(settings.config_dir / "team_colors.json")


def load_celebrations(settings: Settings) -> Dict[str, Any]:
    """Load celebrations configuration."""

    return _read_json(settings.config_dir / "celebrations.json")


def load_wiz_config(settings: Settings) -> Dict[str, Any]:
    """Load WiZ light configuration file."""

    return _read_json(settings.config_dir / "wiz_lights_config.json")


def load_teams_database(settings: Settings) -> Dict[str, Any]:
    """Load teams database with all team metadata."""

    return _read_json(settings.config_dir / "teams_database.json")
