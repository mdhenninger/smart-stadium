"""Monitoring domain models for Smart Stadium."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.models.game import Sport


class MonitoredGameResponse(BaseModel):
    """Response model for a monitored game."""

    game_id: str
    sport: Sport
    home_team_abbr: str
    away_team_abbr: str
    monitored_teams: List[str]  # ["BUF"], ["NE"], or ["BUF", "NE"]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MonitoringRequest(BaseModel):
    """Request to add or update game monitoring."""

    game_id: str
    sport: Sport
    home_team_abbr: str
    away_team_abbr: str
    monitored_teams: List[str] = Field(
        ...,
        min_length=1,
        max_length=2,
        description="List of team abbreviations to monitor (1 or 2 teams)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "game_id": "401772922",
                "sport": "nfl",
                "home_team_abbr": "BUF",
                "away_team_abbr": "NE",
                "monitored_teams": ["BUF"],
            }
        }
