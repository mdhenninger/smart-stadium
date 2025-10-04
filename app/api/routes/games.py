"""Game data endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_container
from app.models.api import ApiResponse
from app.models.game import Sport

router = APIRouter(prefix="/api/games", tags=["Games"])


@router.get("/live", response_model=ApiResponse)
async def get_live_games(
    sport: Sport = Query(Sport.NFL, description="Sport to query"),
    container=Depends(get_container),
):
    try:
        scoreboard = await container.scoreboard_client.fetch_scoreboard(sport)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch scoreboard: {exc}")

    # GameSnapshot.model_dump() now defaults to by_alias=True and mode='json'
    games = [game.model_dump() for game in scoreboard.games]
    return ApiResponse(success=True, data={"sport": sport.value, "games": games})
