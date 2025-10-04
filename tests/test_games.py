from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.game import GameSnapshot, GameStatus, RedZoneInfo, Scoreboard, Sport, TeamScore


@pytest.mark.asyncio
async def test_games_endpoint(client, app):
    scoreboard = Scoreboard(
        sport=Sport.NFL,
        games=[
            GameSnapshot(
                id="1234",
                sport=Sport.NFL,
                home=TeamScore(team_id="1", abbreviation="BUF", display_name="Buffalo Bills", score=14),
                away=TeamScore(team_id="2", abbreviation="MIA", display_name="Miami Dolphins", score=10),
                status=GameStatus.IN_PROGRESS,
                last_update=datetime.now(timezone.utc),
                red_zone=RedZoneInfo(active=False),
            )
        ],
        fetched_at=datetime.now(timezone.utc),
    )

    container = app.state.app_state.container
    assert container is not None
    container.scoreboard_client.fetch_scoreboard = AsyncMock(return_value=scoreboard)

    response = await client.get("/api/games/live?sport=nfl")
    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["data"]["sport"] == "nfl"
    assert len(payload["data"]["games"]) == 1
    game = payload["data"]["games"][0]
    assert game["home"]["abbreviation"] == "BUF"
    assert game["away"]["score"] == 10
