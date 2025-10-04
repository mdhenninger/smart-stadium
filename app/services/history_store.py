"""SQLite-backed history store for Smart Stadium events."""

from __future__ import annotations

import aiosqlite
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.utils.logging import get_logger

logger = get_logger(__name__)


class HistoryStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS celebrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sport TEXT,
                    team TEXT,
                    event_type TEXT,
                    game_id TEXT,
                    detail TEXT
                );

                CREATE TABLE IF NOT EXISTS device_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    device_id TEXT,
                    status TEXT,
                    message TEXT
                );

                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT,
                    message TEXT
                );
                """
            )
            await db.commit()
        self._initialized = True
        logger.info("History store initialized at %s", self._db_path)

    async def record_celebration(self, sport: str, team: str, event_type: str, game_id: str, detail: str | None = None) -> None:
        await self._insert(
            "INSERT INTO celebrations (timestamp, sport, team, event_type, game_id, detail) VALUES (?, ?, ?, ?, ?, ?)",
            [self._now(), sport, team, event_type, game_id, detail],
        )

    async def record_device_event(self, device_id: str, status: str, message: str | None = None) -> None:
        await self._insert(
            "INSERT INTO device_events (timestamp, device_id, status, message) VALUES (?, ?, ?, ?)",
            [self._now(), device_id, status, message],
        )

    async def record_error(self, source: str, message: str) -> None:
        await self._insert(
            "INSERT INTO errors (timestamp, source, message) VALUES (?, ?, ?)",
            [self._now(), source, message],
        )

    async def recent_celebrations(self, limit: int = 50) -> List[Dict[str, Any]]:
        return await self._fetch("SELECT * FROM celebrations ORDER BY id DESC LIMIT ?", [limit])

    async def recent_device_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return await self._fetch("SELECT * FROM device_events ORDER BY id DESC LIMIT ?", [limit])

    async def recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        return await self._fetch("SELECT * FROM errors ORDER BY id DESC LIMIT ?", [limit])

    async def _insert(self, query: str, params: List[Any]) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(query, params)
            await db.commit()

    async def _fetch(self, query: str, params: List[Any]) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
