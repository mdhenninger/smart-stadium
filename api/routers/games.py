"""
Games API Router
Endpoints for game data, live scores, and ESPN integration
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from models import (
    Game, GameSummary, TodaysGames, LiveGames, 
    GameStatus, League, GamePeriod, FieldPosition, 
    GameScore, GameClock, PlayInfo, ApiResponse,
    WebSocketMessage
)
from websocket_manager import connection_manager
from espn_service import espn_service

# Router setup
router = APIRouter(prefix="/api/games", tags=["games"])

# Dependency to get ESPN service
def get_espn_service():
    """Dependency to get ESPN service instance"""
    return espn_service

# API Endpoints

@router.get("/today", response_model=TodaysGames)
async def get_todays_games(
    league: League = Query(League.NFL, description="League to get games for"),
    service = Depends(get_espn_service)
):
    """Get all games scheduled for today"""
    try:
        games = await service.get_todays_games(league)
        return TodaysGames(
            games=games,
            count=len(games),
            league=league,
            date=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch games: {str(e)}")

@router.get("/live", response_model=LiveGames)
async def get_live_games(
    league: League = Query(League.NFL, description="League to get games for"),
    service = Depends(get_espn_service)
):
    """Get currently live games"""
    try:
        games = await service.get_live_games(league)
        return LiveGames(
            games=games,
            count=len(games),
            league=league
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live games: {str(e)}")

@router.get("/{game_id}", response_model=Game)
async def get_game_details(
    game_id: str,
    league: League = Query(League.NFL, description="League for the game"),
    service = Depends(get_espn_service)
):
    """Get detailed information for a specific game"""
    try:
        game = await service.get_game_details(game_id, league)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        return game
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch game details: {str(e)}")

@router.get("/team/{team_abbreviation}", response_model=List[Game])
async def get_team_games(
    team_abbreviation: str,
    league: League = Query(League.NFL, description="League to search in"),
    service = Depends(get_espn_service)
):
    """Get games for a specific team"""
    try:
        all_games = await service.get_todays_games(league)
        team_games = [
            game for game in all_games 
            if (game.home_team_abbreviation.upper() == team_abbreviation.upper() or 
                game.away_team_abbreviation.upper() == team_abbreviation.upper())
        ]
        return team_games
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch team games: {str(e)}")

# Live Game Monitoring Control

@router.post("/monitor/start")
async def start_live_monitoring():
    """Start live game monitoring"""
    try:
        # Import here to avoid circular imports
        from live_game_monitor import live_monitor
        
        if live_monitor.monitoring_active:
            return JSONResponse({
                "success": True,
                "message": "Live monitoring is already active"
            })
        
        await live_monitor.initialize()
        
        # Start monitoring in background
        asyncio.create_task(live_monitor.start_monitoring())
        
        return JSONResponse({
            "success": True,
            "message": "Live game monitoring started"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/monitor/stop")
async def stop_live_monitoring():
    """Stop live game monitoring"""
    try:
        from live_game_monitor import live_monitor
        await live_monitor.stop_monitoring()
        
        return JSONResponse({
            "success": True,
            "message": "Live game monitoring stopped"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.get("/monitor/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    try:
        from live_game_monitor import live_monitor
        status = live_monitor.get_monitoring_status()
        return JSONResponse(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring status: {str(e)}")

@router.post("/monitor/team/{team_name}")
async def add_team_monitoring(team_name: str):
    """Add a team to monitoring"""
    try:
        from live_game_monitor import live_monitor
        await live_monitor.add_monitoring_target(team_name)
        
        return JSONResponse({
            "success": True,
            "message": f"Added {team_name} to monitoring"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add team monitoring: {str(e)}")

@router.delete("/monitor/team/{team_name}")
async def remove_team_monitoring(team_name: str):
    """Remove a team from monitoring"""
    try:
        from live_game_monitor import live_monitor
        await live_monitor.remove_monitoring_target(team_name)
        
        return JSONResponse({
            "success": True,
            "message": f"Removed {team_name} from monitoring"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove team monitoring: {str(e)}")

@router.post("/monitor/config")
async def update_monitoring_config(
    poll_interval: Optional[int] = None,
    big_play_threshold: Optional[int] = None
):
    """Update monitoring configuration"""
    try:
        from live_game_monitor import live_monitor
        
        if poll_interval is not None:
            live_monitor.poll_interval = poll_interval
        
        if big_play_threshold is not None:
            live_monitor.big_play_threshold = big_play_threshold
        
        return JSONResponse({
            "success": True,
            "message": "Monitoring configuration updated",
            "config": {
                "poll_interval": live_monitor.poll_interval,
                "big_play_threshold": live_monitor.big_play_threshold
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update monitoring config: {str(e)}")