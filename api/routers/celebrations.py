"""
Smart Stadium API - Celebrations Router
Endpoints for triggering and managing celebrations
"""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from models import (
    ApiResponse, CelebrationRequest, CelebrationStatus, CelebrationEvent,
    WebSocketMessage, CelebrationType
)

router = APIRouter()

def get_stadium_api():
    """Dependency to get the stadium API instance"""
    from main import stadium_api
    if not stadium_api.stadium_lights:
        raise HTTPException(status_code=503, detail="Smart Stadium not initialized")
    return stadium_api

async def broadcast_celebration_events(celebration_type: CelebrationType, team_name: str, duration: int, stadium_api):
    """Handle real-time broadcasting for celebrations"""
    device_count = len(stadium_api.stadium_lights.device_manager.enabled_devices)
    
    # Broadcast start
    await stadium_api.celebration_broadcaster.broadcast_celebration_start(
        celebration_type, team_name, duration, device_count
    )
    
    # Broadcast progress updates during longer celebrations
    if duration > 5:  # Only for celebrations longer than 5 seconds
        progress_interval = max(1, duration // 10)  # Update every 10% or 1 second minimum
        for i in range(1, 11):  # 10% increments
            await asyncio.sleep(progress_interval)
            progress = i * 10
            await stadium_api.celebration_broadcaster.broadcast_celebration_progress(
                celebration_type, team_name, progress, device_count
            )
    
    # Broadcast end
    await stadium_api.celebration_broadcaster.broadcast_celebration_end(
        celebration_type, team_name, device_count
    )

@router.post("/touchdown", response_model=ApiResponse)
async def trigger_touchdown(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 30-second touchdown celebration 🏈"""
    try:
        # Start real-time broadcasting task
        broadcast_task = asyncio.create_task(
            broadcast_celebration_events(CelebrationType.TOUCHDOWN, team_name, 30, stadium_api)
        )
        
        # Trigger celebration
        celebration_task = asyncio.create_task(
            stadium_api.stadium_lights.celebrate_touchdown(team_name)
        )
        
        # Wait for both to complete
        await asyncio.gather(broadcast_task, celebration_task)
        
        return ApiResponse(
            success=True,
            message=f"Touchdown celebration completed for {team_name}!",
            data={"celebration_type": "touchdown", "team": team_name, "duration": 30}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/field-goal", response_model=ApiResponse)
async def trigger_field_goal(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 10-second field goal celebration 🥅"""
    try:
        await stadium_api.stadium_lights.celebrate_field_goal(team_name)
        return ApiResponse(
            success=True,
            message=f"Field goal celebration completed for {team_name}!",
            data={"celebration_type": "field_goal", "team": team_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/sack", response_model=ApiResponse)
async def trigger_sack(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 2-second sack celebration ⚡"""
    try:
        # Start real-time broadcasting task
        broadcast_task = asyncio.create_task(
            broadcast_celebration_events(CelebrationType.SACK, team_name, 2, stadium_api)
        )
        
        # Trigger celebration
        celebration_task = asyncio.create_task(
            stadium_api.stadium_lights.celebrate_sack(team_name)
        )
        
        # Wait for both to complete
        await asyncio.gather(broadcast_task, celebration_task)
        
        return ApiResponse(
            success=True,
            message=f"Sack celebration completed for {team_name}!",
            data={"celebration_type": "sack", "team": team_name, "duration": 2}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/turnover", response_model=ApiResponse)
async def trigger_turnover(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 10-second turnover celebration 🔄"""
    try:
        await stadium_api.stadium_lights.celebrate_turnover(team_name)
        return ApiResponse(
            success=True,
            message=f"Turnover celebration completed for {team_name}!",
            data={"celebration_type": "turnover", "team": team_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/big-play", response_model=ApiResponse)
async def trigger_big_play(
    team_name: Optional[str] = "BUFFALO BILLS",
    play_type: Optional[str] = "",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 5-second big play celebration 🏃‍♂️"""
    try:
        await stadium_api.stadium_lights.celebrate_big_play(team_name, play_type)
        return ApiResponse(
            success=True,
            message=f"Big play celebration completed for {team_name}!",
            data={"celebration_type": "big_play", "team": team_name, "play_type": play_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/defensive-stop", response_model=ApiResponse)
async def trigger_defensive_stop(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 5-second defensive stop celebration 🛡️"""
    try:
        await stadium_api.stadium_lights.celebrate_defensive_stop(team_name)
        return ApiResponse(
            success=True,
            message=f"Defensive stop celebration completed for {team_name}!",
            data={"celebration_type": "defensive_stop", "team": team_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/victory", response_model=ApiResponse)
async def trigger_victory(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger a 60-second victory celebration 🏆"""
    try:
        await stadium_api.stadium_lights.celebrate_victory(team_name)
        return ApiResponse(
            success=True,
            message=f"Victory celebration completed for {team_name}!",
            data={"celebration_type": "victory", "team": team_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/red-zone", response_model=ApiResponse)
async def trigger_red_zone(
    team_name: Optional[str] = "BUFFALO BILLS",
    stadium_api = Depends(get_stadium_api)
):
    """Trigger red zone ambient lighting 🎯"""
    try:
        await stadium_api.stadium_lights.celebrate_red_zone(team_name)
        return ApiResponse(
            success=True,
            message=f"Red zone ambient lighting activated for {team_name}!",
            data={"celebration_type": "red_zone", "team": team_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Red zone activation failed: {str(e)}")

@router.post("/custom", response_model=ApiResponse)
async def trigger_custom_celebration(
    request: CelebrationRequest,
    stadium_api = Depends(get_stadium_api)
):
    """Trigger any celebration type with custom parameters"""
    try:
        celebration_map = {
            CelebrationType.TOUCHDOWN: stadium_api.stadium_lights.celebrate_touchdown,
            CelebrationType.FIELD_GOAL: stadium_api.stadium_lights.celebrate_field_goal,
            CelebrationType.SACK: stadium_api.stadium_lights.celebrate_sack,
            CelebrationType.TURNOVER: stadium_api.stadium_lights.celebrate_turnover,
            CelebrationType.BIG_PLAY: lambda team: stadium_api.stadium_lights.celebrate_big_play(team, request.play_type or ""),
            CelebrationType.DEFENSIVE_STOP: stadium_api.stadium_lights.celebrate_defensive_stop,
            CelebrationType.VICTORY: stadium_api.stadium_lights.celebrate_victory,
            CelebrationType.RED_ZONE: stadium_api.stadium_lights.celebrate_red_zone,
            CelebrationType.EXTRA_POINT: stadium_api.stadium_lights.celebrate_extra_point,
            CelebrationType.TWO_POINT: stadium_api.stadium_lights.celebrate_two_point,
            CelebrationType.SAFETY: stadium_api.stadium_lights.celebrate_safety,
        }
        
        if request.celebration_type == CelebrationType.GENERIC_SCORE:
            await stadium_api.stadium_lights.celebrate_generic_score(
                points=request.points or 3,
                team_name=request.team_name
            )
        else:
            celebration_func = celebration_map.get(request.celebration_type)
            if not celebration_func:
                raise HTTPException(status_code=400, detail=f"Unknown celebration type: {request.celebration_type}")
            
            await celebration_func(request.team_name)
        
        return ApiResponse(
            success=True,
            message=f"{request.celebration_type.value} celebration completed for {request.team_name}!",
            data=request.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celebration failed: {str(e)}")

@router.post("/stop", response_model=ApiResponse)
async def stop_celebration(stadium_api = Depends(get_stadium_api)):
    """Stop any running celebration and return to default lighting"""
    try:
        await stadium_api.stadium_lights.set_all_default_lighting()
        return ApiResponse(
            success=True,
            message="All celebrations stopped, lights set to default",
            data={"action": "stop_celebration"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop celebration: {str(e)}")

@router.get("/types")
async def get_celebration_types():
    """Get all available celebration types"""
    celebrations = {
        "touchdown": {"duration": 30, "description": "Epic touchdown celebration with 30 flashes"},
        "field_goal": {"duration": 10, "description": "Field goal celebration with 10 flashes"},
        "extra_point": {"duration": 5, "description": "Quick extra point celebration"},
        "two_point": {"duration": 10, "description": "Two-point conversion power celebration"},
        "safety": {"duration": 15, "description": "Rare safety celebration"},
        "victory": {"duration": 60, "description": "Epic 60-second victory celebration"},
        "turnover": {"duration": 10, "description": "Defensive turnover celebration"},
        "big_play": {"duration": 5, "description": "Big play celebration for 40+ yard plays"},
        "defensive_stop": {"duration": 5, "description": "4th down defensive stop celebration"},
        "sack": {"duration": 2, "description": "Quick sack celebration"},
        "red_zone": {"duration": "ambient", "description": "Red zone ambient lighting"},
        "generic_score": {"duration": "variable", "description": "Generic scoring celebration"}
    }
    
    return ApiResponse(
        success=True,
        message="Available celebration types",
        data=celebrations
    )