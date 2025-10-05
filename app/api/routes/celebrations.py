"""Celebration control endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_container
from app.models.api import ApiResponse, CelebrationTriggerRequest
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/celebrations", tags=["Celebrations"])


@router.post("/trigger", response_model=ApiResponse)
async def trigger_celebration(payload: CelebrationTriggerRequest, container=Depends(get_container)):
    import asyncio
    
    lights = container.lights_service
    event = payload.event_type.lower()

    # Start celebration in background task (don't wait for it to complete)
    async def run_celebration():
        try:
            # Pass team_abbr and sport for sport-aware color lookup
            if event == "touchdown":
                await lights.celebrate_touchdown(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "field_goal":
                await lights.celebrate_field_goal(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "extra_point":
                await lights.celebrate_extra_point(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "two_point":
                await lights.celebrate_two_point(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "safety":
                await lights.celebrate_safety(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "victory":
                await lights.celebrate_victory(payload.team_name, payload.game_id or "")
            elif event == "turnover":
                await lights.celebrate_turnover(payload.team_name, "turnover", team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "sack":
                await lights.celebrate_sack(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "big_play":
                description = payload.game_id or "Big play"
                await lights.celebrate_big_play(payload.team_name, description, team_abbr=payload.team_abbr, sport=payload.sport)
            elif event == "defensive_stop":
                await lights.celebrate_defensive_stop(payload.team_name, team_abbr=payload.team_abbr, sport=payload.sport)
        except Exception as exc:
            logger.error(f"Celebration error: {exc}")
    
    # Validate event type before starting
    valid_events = ["touchdown", "field_goal", "extra_point", "two_point", "safety", 
                    "victory", "turnover", "sack", "big_play", "defensive_stop"]
    if event not in valid_events:
        raise HTTPException(status_code=400, detail=f"Unknown celebration type: {payload.event_type}")
    
    # Start celebration task in background
    asyncio.create_task(run_celebration())

    await container.history_store.record_celebration(
        sport="manual",
        team=payload.team_abbr,
        event_type=event,
        game_id=payload.game_id or "manual",
        detail=payload.team_name,
    )

    # Broadcast the celebration event via WebSocket
    if container.websocket_manager:
        await container.websocket_manager.broadcast({
            "type": "celebration",
            "sport": "manual",
            "team": payload.team_abbr,
            "event_type": event,
            "team_name": payload.team_name,
        })

    return ApiResponse(success=True, message=f"Celebration {payload.event_type} triggered")
