"""Common API response models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: Dict[str, Any] | None = None


class SystemStatusResponse(BaseModel):
    uptime_seconds: float
    environment: str
    total_devices: int
    enabled_devices: int
    online_devices: int
    offline_devices: int
    monitoring_active: bool
    sports_enabled: Dict[str, bool]
    fetched_at: datetime = Field(default_factory=utc_now)


class CelebrationTriggerRequest(BaseModel):
    team_abbr: str
    team_name: str
    event_type: str
    sport: str | None = None  # Optional: "nfl", "cfb", "nhl", etc.
    points: int | None = None
    game_id: str | None = None


class DeviceToggleRequest(BaseModel):
    enabled: bool


class TeamColors(BaseModel):
    primary: tuple[int, int, int]
    secondary: tuple[int, int, int]
    lighting_primary: tuple[int, int, int] | None = None
    lighting_secondary: tuple[int, int, int] | None = None


class TeamOption(BaseModel):
    value: str  # Format: "sport:abbr" (e.g., "nfl:BUF")
    label: str  # Format: "Team Name (SPORT)" (e.g., "Buffalo Bills (NFL)")
    abbreviation: str
    name: str
    sport: str
    city: str | None = None
    colors: TeamColors


class TeamsResponse(BaseModel):
    teams: list[TeamOption]
    total_count: int
