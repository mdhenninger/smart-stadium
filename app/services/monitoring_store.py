"""Persistence layer for monitoring preferences."""

from __future__ import annotations

import aiosqlite
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.models.game import Sport
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MonitoredGame:
    """Represents a game being monitored for celebrations."""

    def __init__(
        self,
        game_id: str,
        sport: str,
        home_team_abbr: str,
        away_team_abbr: str,
        monitored_teams: List[str],
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.game_id = game_id
        self.sport = sport
        self.home_team_abbr = home_team_abbr
        self.away_team_abbr = away_team_abbr
        self.monitored_teams = monitored_teams
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "sport": self.sport,
            "home_team_abbr": self.home_team_abbr,
            "away_team_abbr": self.away_team_abbr,
            "monitored_teams": self.monitored_teams,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MonitoringStore:
    """SQLite-backed storage for monitoring preferences."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialized = False

    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS monitored_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL UNIQUE,
                    sport TEXT NOT NULL,
                    home_team_abbr TEXT NOT NULL,
                    away_team_abbr TEXT NOT NULL,
                    monitored_teams TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

        self._initialized = True
        logger.info("Monitoring store initialized at %s", self.db_path)

    async def add_monitoring(
        self,
        game_id: str,
        sport: Sport,
        home_team_abbr: str,
        away_team_abbr: str,
        monitored_teams: List[str],
    ) -> MonitoredGame:
        """Add a game to monitoring or update existing monitoring."""
        now = datetime.now(timezone.utc).isoformat()
        teams_json = json.dumps(monitored_teams)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO monitored_games 
                (game_id, sport, home_team_abbr, away_team_abbr, monitored_teams, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(game_id) DO UPDATE SET
                    monitored_teams = excluded.monitored_teams,
                    updated_at = excluded.updated_at
                """,
                (game_id, sport.value, home_team_abbr, away_team_abbr, teams_json, now, now),
            )
            await db.commit()

        logger.info(
            "Added monitoring for game %s: teams=%s",
            game_id,
            monitored_teams,
        )

        return MonitoredGame(
            game_id=game_id,
            sport=sport.value,
            home_team_abbr=home_team_abbr,
            away_team_abbr=away_team_abbr,
            monitored_teams=monitored_teams,
        )

    async def remove_monitoring(self, game_id: str) -> bool:
        """Remove a game from monitoring."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM monitored_games WHERE game_id = ?",
                (game_id,),
            )
            await db.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            logger.info("Removed monitoring for game %s", game_id)
        return deleted

    async def get_monitored_games(self) -> List[MonitoredGame]:
        """Get all currently monitored games."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT game_id, sport, home_team_abbr, away_team_abbr, 
                       monitored_teams, created_at, updated_at
                FROM monitored_games
                ORDER BY created_at DESC
                """
            ) as cursor:
                rows = await cursor.fetchall()

        games = []
        for row in rows:
            games.append(
                MonitoredGame(
                    game_id=row["game_id"],
                    sport=row["sport"],
                    home_team_abbr=row["home_team_abbr"],
                    away_team_abbr=row["away_team_abbr"],
                    monitored_teams=json.loads(row["monitored_teams"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
            )
        return games

    async def is_team_monitored(self, game_id: str, team_abbr: str) -> bool:
        """Check if a specific team in a game is being monitored."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT monitored_teams FROM monitored_games WHERE game_id = ?",
                (game_id,),
            ) as cursor:
                row = await cursor.fetchone()

        if not row:
            return False

        monitored_teams = json.loads(row[0])
        return team_abbr in monitored_teams

    async def cleanup_finished_games(self, finished_game_ids: List[str]) -> int:
        """Remove multiple finished games from monitoring."""
        if not finished_game_ids:
            return 0

        placeholders = ",".join("?" * len(finished_game_ids))
        query = f"DELETE FROM monitored_games WHERE game_id IN ({placeholders})"

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, finished_game_ids)
            await db.commit()
            count = cursor.rowcount

        if count > 0:
            logger.info("Cleaned up %d finished games from monitoring", count)
        return count
