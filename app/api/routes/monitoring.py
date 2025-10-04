"""Monitoring management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_container
from app.models.api import ApiResponse
from app.models.monitoring import MonitoredGameResponse, MonitoringRequest
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/", response_model=ApiResponse)
async def list_monitored_games(container=Depends(get_container)):
    """Get all currently monitored games."""
    games = await container.monitoring_store.get_monitored_games()
    
    # Convert to response models
    data = [
        MonitoredGameResponse(
            game_id=g.game_id,
            sport=g.sport,
            home_team_abbr=g.home_team_abbr,
            away_team_abbr=g.away_team_abbr,
            monitored_teams=g.monitored_teams,
            created_at=g.created_at,
            updated_at=g.updated_at,
        ).model_dump()
        for g in games
    ]
    
    return ApiResponse(
        success=True,
        data={"monitored_games": data, "count": len(data)},
    )


@router.post("/", response_model=ApiResponse)
async def add_monitoring(payload: MonitoringRequest, container=Depends(get_container)):
    """Add a game to monitoring or update monitored teams."""
    
    # Validate that monitored teams are either home, away, or both
    valid_teams = {payload.home_team_abbr, payload.away_team_abbr}
    for team in payload.monitored_teams:
        if team not in valid_teams:
            raise HTTPException(
                status_code=400,
                detail=f"Team {team} is not in this game. Valid teams: {list(valid_teams)}",
            )
    
    game = await container.monitoring_store.add_monitoring(
        game_id=payload.game_id,
        sport=payload.sport,
        home_team_abbr=payload.home_team_abbr,
        away_team_abbr=payload.away_team_abbr,
        monitored_teams=payload.monitored_teams,
    )
    
    # Broadcast update via WebSocket
    if container.websocket_manager:
        await container.websocket_manager.broadcast(
            {
                "type": "monitoring_added",
                "game_id": payload.game_id,
                "monitored_teams": payload.monitored_teams,
            }
        )
    
    return ApiResponse(
        success=True,
        message=f"Monitoring started for game {payload.game_id}",
        data=MonitoredGameResponse(
            game_id=game.game_id,
            sport=game.sport,
            home_team_abbr=game.home_team_abbr,
            away_team_abbr=game.away_team_abbr,
            monitored_teams=game.monitored_teams,
            created_at=game.created_at,
            updated_at=game.updated_at,
        ).model_dump(),
    )


@router.delete("/{game_id}", response_model=ApiResponse)
async def remove_monitoring(game_id: str, container=Depends(get_container)):
    """Remove a game from monitoring."""
    success = await container.monitoring_store.remove_monitoring(game_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Game {game_id} is not being monitored",
        )
    
    # Broadcast update via WebSocket
    if container.websocket_manager:
        await container.websocket_manager.broadcast(
            {
                "type": "monitoring_removed",
                "game_id": game_id,
                "reason": "user_action",
            }
        )
    
    return ApiResponse(
        success=True,
        message=f"Monitoring stopped for game {game_id}",
    )


@router.put("/{game_id}", response_model=ApiResponse)
async def update_monitoring(
    game_id: str,
    payload: MonitoringRequest,
    container=Depends(get_container),
):
    """Update which teams are being monitored in a game."""
    if payload.game_id != game_id:
        raise HTTPException(
            status_code=400,
            detail="Game ID in path must match game ID in request body",
        )
    
    # Validate that monitored teams are either home, away, or both
    valid_teams = {payload.home_team_abbr, payload.away_team_abbr}
    for team in payload.monitored_teams:
        if team not in valid_teams:
            raise HTTPException(
                status_code=400,
                detail=f"Team {team} is not in this game. Valid teams: {list(valid_teams)}",
            )
    
    game = await container.monitoring_store.add_monitoring(
        game_id=payload.game_id,
        sport=payload.sport,
        home_team_abbr=payload.home_team_abbr,
        away_team_abbr=payload.away_team_abbr,
        monitored_teams=payload.monitored_teams,
    )
    
    # Broadcast update via WebSocket
    if container.websocket_manager:
        await container.websocket_manager.broadcast(
            {
                "type": "monitoring_updated",
                "game_id": payload.game_id,
                "monitored_teams": payload.monitored_teams,
            }
        )
    
    return ApiResponse(
        success=True,
        message=f"Monitoring updated for game {payload.game_id}",
        data=MonitoredGameResponse(
            game_id=game.game_id,
            sport=game.sport,
            home_team_abbr=game.home_team_abbr,
            away_team_abbr=game.away_team_abbr,
            monitored_teams=game.monitored_teams,
            created_at=game.created_at,
            updated_at=game.updated_at,
        ).model_dump(),
    )
