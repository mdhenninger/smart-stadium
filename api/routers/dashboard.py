"""
Dashboard API Router
Consolidated endpoints for dashboard data, health, preferences, and analytics
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from models import (
    DashboardData, SystemHealth, UserPreferences, UsageStats,
    DashboardConfig, PreferencesRequest, ApiResponse, LiveGames,
    Device, SystemStatus, Team, League
)
from websocket_manager import connection_manager
from live_game_monitor import live_monitor
from espn_service import espn_service

# Router setup
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Preferences file path
PREFERENCES_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "user_preferences.json")

class DashboardService:
    """Service for dashboard data aggregation and management"""
    
    def __init__(self):
        self.start_time = time.time()
        self.celebration_count = 0
        self.error_count = 0
        self.last_error = None
        self.daily_celebration_count = 0
        self.last_celebration_date = None
        
    def load_user_preferences(self) -> UserPreferences:
        """Load user preferences from file"""
        try:
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    data = json.load(f)
                    return UserPreferences(**data)
            else:
                # Return default preferences
                return UserPreferences()
        except Exception as e:
            print(f"⚠️ Error loading preferences: {e}")
            return UserPreferences()
    
    def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """Save user preferences to file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
            
            with open(PREFERENCES_FILE, 'w') as f:
                json.dump(preferences.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving preferences: {e}")
            return False
    
    async def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        try:
            # Check device connectivity
            device_status = "good"  # Would check actual devices
            
            # Check ESPN API status
            espn_status = "connected"
            try:
                # Use the singleton ESPN service instead of creating new instance
                # Quick test call
                await espn_service.fetch_scoreboard(League.NFL)
                espn_status = "connected"
            except Exception:
                espn_status = "error"
                self.error_count += 1
                self.last_error = "ESPN API connection failed"
            
            # WebSocket connection count
            ws_connections = len(connection_manager.active_connections)
            
            return SystemHealth(
                api_status="healthy",
                device_connectivity=device_status,
                espn_api_status=espn_status,
                websocket_connections=ws_connections,
                live_monitoring_active=live_monitor.monitoring_active,
                uptime_seconds=time.time() - self.start_time,
                last_error=self.last_error,
                error_count=self.error_count
            )
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            return SystemHealth(
                api_status="error",
                device_connectivity="unknown",
                espn_api_status="unknown",
                websocket_connections=0,
                live_monitoring_active=False,
                uptime_seconds=time.time() - self.start_time,
                last_error=str(e),
                error_count=self.error_count
            )
    
    def get_usage_stats(self) -> UsageStats:
        """Get usage statistics"""
        # Reset daily count if new day
        today = datetime.now().date()
        if self.last_celebration_date != today:
            self.daily_celebration_count = 0
            self.last_celebration_date = today
        
        return UsageStats(
            total_celebrations=self.celebration_count,
            celebrations_today=self.daily_celebration_count,
            most_active_team="Buffalo Bills",  # Could track this properly
            peak_usage_hour=19,  # 7 PM typical game time
            devices_utilized=3,  # Would get from device manager
            games_monitored=len(live_monitor.monitored_games),
            uptime_hours=(time.time() - self.start_time) / 3600,
            last_celebration=None  # Would track last celebration time
        )
    
    def increment_celebration_count(self):
        """Increment celebration counters"""
        self.celebration_count += 1
        self.daily_celebration_count += 1
        self.last_celebration_date = datetime.now().date()
    
    async def get_dashboard_bundle(self, stadium_api=None) -> DashboardData:
        """Get complete dashboard data bundle"""
        try:
            # Get all required data
            user_preferences = self.load_user_preferences()
            system_health = await self.get_system_health()
            usage_stats = self.get_usage_stats()
            
            # Get system status (from existing API)
            if stadium_api:
                system_status = await stadium_api.get_system_status()
            else:
                # Mock system status
                from models import Team
                mock_team = Team(
                    id="NFL-BUFFALO-BILLS",
                    league="NFL",
                    city="Buffalo", 
                    name="Bills",
                    full_name="Buffalo Bills",
                    primary_color=(0, 0, 255),
                    secondary_color=(255, 0, 0)
                )
                system_status = SystemStatus(
                    total_devices=0,
                    online_devices=0,
                    offline_devices=0,
                    current_team=mock_team,
                    red_zone_active=False,
                    uptime_seconds=time.time() - self.start_time
                )
            
            # Get live games
            try:
                nfl_games = await espn_service.get_live_games(League.NFL)
                live_games_list = nfl_games
                
                live_games = LiveGames(
                    total_live=len(live_games_list),
                    games=live_games_list,
                    last_updated=datetime.utcnow().isoformat()
                )
            except Exception as e:
                # Return empty live games on error
                live_games = LiveGames(
                    total_live=0,
                    games=[],
                    last_updated=datetime.utcnow().isoformat()
                )
            
            # Get devices (mock for now)
            devices = []  # Would get from device manager
            
            # Get monitoring status
            monitoring_status = live_monitor.get_monitoring_status()
            
            return DashboardData(
                system_status=system_status,
                system_health=system_health,
                user_preferences=user_preferences,
                usage_stats=usage_stats,
                live_games=live_games,
                devices=devices,
                monitoring_status=monitoring_status,
                current_team=system_status.current_team
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get dashboard data: {str(e)}"
            )

# Global service instance
dashboard_service = DashboardService()

# Dependency injection for stadium API
async def get_stadium_api():
    """Get stadium API reference from main app"""
    from main import stadium_api
    return stadium_api

# API Endpoints

@router.get("/data", response_model=DashboardData)
async def get_dashboard_data(
    stadium_api = Depends(get_stadium_api)
):
    """Get complete dashboard data bundle for frontend initial load"""
    try:
        return await dashboard_service.get_dashboard_bundle(stadium_api)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get detailed system health information"""
    try:
        return await dashboard_service.get_system_health()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences():
    """Get current user preferences"""
    try:
        return dashboard_service.load_user_preferences()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user preferences: {str(e)}"
        )

@router.post("/preferences", response_model=ApiResponse)
async def update_user_preferences(
    preferences_update: PreferencesRequest
):
    """Update user preferences"""
    try:
        # Load current preferences
        current_prefs = dashboard_service.load_user_preferences()
        
        # Update only provided fields
        update_data = preferences_update.model_dump(exclude_unset=True)
        
        # Apply updates
        for field, value in update_data.items():
            if hasattr(current_prefs, field):
                setattr(current_prefs, field, value)
        
        # Save updated preferences
        success = dashboard_service.save_user_preferences(current_prefs)
        
        if success:
            # Broadcast preferences update
            from models import WebSocketMessage
            await connection_manager.broadcast(
                WebSocketMessage(
                    type="preferences_updated",
                    data=current_prefs.model_dump(),
                    timestamp=datetime.utcnow().isoformat()
                ),
                "preferences"
            )
            
            return ApiResponse(
                success=True,
                message="User preferences updated successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to save preferences"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.get("/stats", response_model=UsageStats)
async def get_usage_statistics():
    """Get usage statistics and analytics"""
    try:
        return dashboard_service.get_usage_stats()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage statistics: {str(e)}"
        )

@router.get("/config", response_model=DashboardConfig)
async def get_dashboard_config():
    """Get dashboard configuration options"""
    try:
        return DashboardConfig()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard config: {str(e)}"
        )

@router.post("/reset-stats", response_model=ApiResponse)
async def reset_usage_statistics():
    """Reset usage statistics"""
    try:
        dashboard_service.celebration_count = 0
        dashboard_service.daily_celebration_count = 0
        dashboard_service.error_count = 0
        dashboard_service.last_error = None
        
        return ApiResponse(
            success=True,
            message="Usage statistics reset successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset statistics: {str(e)}"
        )

@router.post("/celebration-event", response_model=ApiResponse)
async def record_celebration_event():
    """Record a celebration event for statistics"""
    try:
        dashboard_service.increment_celebration_count()
        
        # Broadcast stats update
        from models import WebSocketMessage
        await connection_manager.broadcast(
            WebSocketMessage(
                type="stats_updated",
                data=dashboard_service.get_usage_stats().model_dump(),
                timestamp=datetime.utcnow().isoformat()
            ),
            "stats"
        )
        
        return ApiResponse(
            success=True,
            message="Celebration event recorded"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record celebration event: {str(e)}"
        )

@router.get("/summary")
async def get_dashboard_summary():
    """Get a quick dashboard summary for status checks"""
    try:
        health = await dashboard_service.get_system_health()
        stats = dashboard_service.get_usage_stats()
        monitoring = live_monitor.get_monitoring_status()
        
        return {
            "status": "healthy" if health.api_status == "healthy" else "degraded",
            "uptime_hours": round(health.uptime_seconds / 3600, 1),
            "celebrations_today": stats.celebrations_today,
            "live_monitoring": monitoring["active"],
            "monitored_games": monitoring["monitored_games"],
            "websocket_connections": health.websocket_connections,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )