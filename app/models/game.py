"""Game domain models for Smart Stadium."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Sport(str, Enum):
    NFL = "nfl"
    COLLEGE_FOOTBALL = "college_football"


class TeamScore(BaseModel):
    team_id: str
    abbreviation: str
    display_name: str
    score: int
    logo_url: Optional[str] = None  # ESPN team logo URL


class GameStatus(Enum):
    PREGAME = "pre"
    IN_PROGRESS = "in"
    FINAL = "post"
    UNKNOWN = "unknown"


class RedZoneInfo(BaseModel):
    active: bool = False
    team_abbr: Optional[str] = None
    yard_line: Optional[int] = None


class GameSituation(BaseModel):
    """Current game situation for in-progress games."""
    possession_team_id: Optional[str] = None
    down_distance: Optional[str] = None  # e.g., "1st & 10"
    field_position: Optional[str] = None  # e.g., "UGA 19"
    is_red_zone: bool = False
    clock: Optional[str] = None  # e.g., "11:09"
    period: Optional[int] = None  # Quarter/period number


class DefensivePlayType(str, Enum):
    SACK = "sack"
    INTERCEPTION = "interception"
    FUMBLE_RECOVERY = "fumble_recovery"
    FUMBLE = "fumble"
    SAFETY = "safety"
    INTERCEPTION_TD = "interception_td"
    FUMBLE_TD = "fumble_td"


class DefensivePlay(BaseModel):
    """Represents a defensive play that occurred."""
    play_id: str
    play_type: DefensivePlayType
    team_abbr: str  # Defending team that made the play
    description: str  # Full play description
    score_value: int = 0  # Points scored (for TDs, safeties)
    timestamp: datetime = Field(default_factory=datetime.now)


class LastPlayInfo(BaseModel):
    """Information about the last play in a game."""
    play_id: Optional[str] = None
    play_type_id: Optional[str] = None
    play_type_name: Optional[str] = None
    description: Optional[str] = None
    score_value: int = 0
    team_id: Optional[str] = None  # Team that executed the play


class GameSnapshot(BaseModel):
    game_id: str = Field(..., alias="id")
    sport: Sport
    home: TeamScore
    away: TeamScore
    status: GameStatus
    last_update: datetime
    red_zone: RedZoneInfo = Field(default_factory=RedZoneInfo)
    situation: Optional[GameSituation] = None  # Only populated for in-progress games
    last_play: Optional[LastPlayInfo] = None  # Track last play for defensive event detection

    class Config:
        populate_by_name = True
        # Allow serialization to use field aliases
        by_alias = True

    def model_dump(self, **kwargs):
        """Override to ensure by_alias=True by default."""
        kwargs.setdefault('by_alias', True)
        kwargs.setdefault('mode', 'json')
        return super().model_dump(**kwargs)

    @property
    def scores(self) -> Dict[str, int]:
        return {self.home.abbreviation: self.home.score, self.away.abbreviation: self.away.score}


class Scoreboard(BaseModel):
    sport: Sport
    games: List[GameSnapshot]
    fetched_at: datetime
