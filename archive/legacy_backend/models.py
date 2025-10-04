"""
Smart Stadium API Data Models
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class CelebrationType(str, Enum):
    """Available celebration types"""
    TOUCHDOWN = "touchdown"
    FIELD_GOAL = "field_goal"
    EXTRA_POINT = "extra_point"
    TWO_POINT = "two_point"
    SAFETY = "safety"
    VICTORY = "victory"
    TURNOVER = "turnover"
    BIG_PLAY = "big_play"
    DEFENSIVE_STOP = "defensive_stop"
    SACK = "sack"
    RED_ZONE = "red_zone"
    GENERIC_SCORE = "generic_score"

class DeviceStatus(str, Enum):
    """Device status options"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class DeviceType(str, Enum):
    """Supported device types"""
    WIZ = "wiz"
    PHILIPS_HUE = "philips_hue"
    LIFX = "lifx"

class GameStatus(str, Enum):
    """Game status options"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    HALFTIME = "halftime"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"

class GamePeriod(str, Enum):
    """Game period/quarter options"""
    PREGAME = "pregame"
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"
    OVERTIME = "OT"
    FINAL = "final"

class League(str, Enum):
    """Supported leagues"""
    NFL = "nfl"
    COLLEGE = "college-football"

# Request Models
class CelebrationRequest(BaseModel):
    """Request to trigger a celebration"""
    celebration_type: CelebrationType
    team_name: Optional[str] = "BUFFALO BILLS"
    duration_override: Optional[int] = Field(None, description="Override default celebration duration in seconds")
    play_type: Optional[str] = Field(None, description="Specific play type for context")
    points: Optional[int] = Field(None, description="Points scored for generic celebrations")

class TeamChangeRequest(BaseModel):
    """Request to change the current team"""
    team_id: str = Field(..., description="Team ID in format LEAGUE-CITY-TEAM (e.g., NFL-BUFFALO-BILLS)")
    temporary: bool = Field(False, description="If true, team change is temporary for this celebration only")

class DeviceToggleRequest(BaseModel):
    """Request to enable/disable a device"""
    enabled: bool

class DeviceAddRequest(BaseModel):
    """Request to add a new device"""
    name: str = Field(..., description="Human-readable device name")
    ip_address: str = Field(..., description="Device IP address")
    device_type: DeviceType = DeviceType.WIZ
    enabled: bool = True

class LightingRequest(BaseModel):
    """Request to set lighting mode"""
    color_rgb: Optional[tuple[int, int, int]] = Field(None, description="RGB color tuple (0-255 each)")
    brightness: Optional[int] = Field(None, ge=0, le=255, description="Brightness level 0-255")
    color_temp: Optional[int] = Field(None, description="Color temperature in Kelvin (2200-6500)")

# Response Models
class Device(BaseModel):
    """Device information"""
    id: str
    name: str
    ip_address: str
    device_type: DeviceType
    status: DeviceStatus
    enabled: bool
    last_seen: Optional[str] = None
    response_time_ms: Optional[float] = None

class Team(BaseModel):
    """Team information"""
    id: str
    league: str
    city: str
    name: str
    full_name: str
    primary_color: tuple[int, int, int]
    secondary_color: tuple[int, int, int]

class SystemStatus(BaseModel):
    """Overall system status"""
    total_devices: int
    online_devices: int
    offline_devices: int
    current_team: Team
    red_zone_active: bool
    api_version: str = "1.0.0"
    uptime_seconds: float

class CelebrationStatus(BaseModel):
    """Status of a running celebration"""
    celebration_type: CelebrationType
    team_name: str
    start_time: str
    duration_seconds: int
    is_active: bool
    devices_participating: int

class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

# Game Data Models
class FieldPosition(BaseModel):
    """Field position information"""
    yard_line: int = Field(..., ge=0, le=100, description="Yard line position (0-100)")
    side: str = Field(..., description="Which team's side of field")
    is_red_zone: bool = Field(False, description="True if in red zone (within 20 yards of goal)")
    
class GameScore(BaseModel):
    """Team score information"""
    team_id: str
    team_name: str
    score: int
    timeouts_remaining: int = 3

class GameClock(BaseModel):
    """Game clock information"""
    period: GamePeriod
    time_remaining: str = Field(..., description="Time remaining in format MM:SS")
    is_intermission: bool = False

class PlayInfo(BaseModel):
    """Current play information"""
    down: Optional[int] = Field(None, ge=1, le=4)
    yards_to_go: Optional[int] = Field(None, ge=0)
    field_position: Optional[FieldPosition] = None
    possession_team_id: Optional[str] = None

class Game(BaseModel):
    """Complete game information"""
    id: str
    league: League
    status: GameStatus
    start_time: str = Field(..., description="Game start time in ISO format")
    
    # Teams
    home_team: GameScore
    away_team: GameScore
    
    # Game state
    clock: GameClock
    play_info: Optional[PlayInfo] = None
    
    # Metadata
    venue: Optional[str] = None
    weather: Optional[str] = None
    attendance: Optional[int] = None
    
    # ESPN API specific
    espn_game_id: Optional[str] = None
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class GameSummary(BaseModel):
    """Simplified game information for listings"""
    id: str
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    status: GameStatus
    start_time: str
    league: League

class TodaysGames(BaseModel):
    """Today's games response"""
    date: str
    total_games: int
    nfl_games: List[GameSummary]
    college_games: List[GameSummary]

class LiveGames(BaseModel):
    """Live games response"""
    total_live: int
    games: List[Game]
    last_updated: str

# Dashboard Data Models
class SystemHealth(BaseModel):
    """System health information"""
    api_status: str = "healthy"
    device_connectivity: str = "good"  # "good", "partial", "poor"
    espn_api_status: str = "connected"
    websocket_connections: int = 0
    live_monitoring_active: bool = False
    uptime_seconds: float
    last_error: Optional[str] = None
    error_count: int = 0
    
class UserPreferences(BaseModel):
    """User preferences and settings"""
    default_teams: List[str] = ["Buffalo Bills"]
    celebration_brightness: int = 255
    celebration_duration_multiplier: float = 1.0
    enable_auto_celebrations: bool = True
    enable_red_zone_ambient: bool = True
    dashboard_theme: str = "dark"  # "dark", "light", "auto"
    notification_sound: bool = True
    poll_interval: int = 15
    preferred_leagues: List[str] = ["NFL"]
    
class UsageStats(BaseModel):
    """Usage statistics and analytics"""
    total_celebrations: int = 0
    celebrations_today: int = 0
    most_active_team: Optional[str] = None
    peak_usage_hour: Optional[int] = None
    devices_utilized: int = 0
    games_monitored: int = 0
    uptime_hours: float = 0
    last_celebration: Optional[str] = None
    
class DashboardData(BaseModel):
    """Complete dashboard data bundle"""
    system_status: SystemStatus
    system_health: SystemHealth
    user_preferences: UserPreferences
    usage_stats: UsageStats
    
    # Current data
    live_games: LiveGames
    devices: List[Device]
    monitoring_status: Dict[str, Any]
    current_team: Team
    
    # Metadata
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0.0"

class DashboardConfig(BaseModel):
    """Dashboard configuration options"""
    available_themes: List[str] = ["dark", "light", "auto"]
    supported_leagues: List[str] = ["NFL", "College"]
    celebration_types: List[CelebrationType] = list(CelebrationType)
    poll_interval_range: Dict[str, int] = {"min": 5, "max": 300}
    max_monitoring_teams: int = 10
    
class PreferencesRequest(BaseModel):
    """Request to update user preferences"""
    default_teams: Optional[List[str]] = None
    celebration_brightness: Optional[int] = Field(None, ge=1, le=255)
    celebration_duration_multiplier: Optional[float] = Field(None, ge=0.1, le=3.0)
    enable_auto_celebrations: Optional[bool] = None
    enable_red_zone_ambient: Optional[bool] = None
    dashboard_theme: Optional[str] = None
    notification_sound: Optional[bool] = None
    poll_interval: Optional[int] = Field(None, ge=5, le=300)
    preferred_leagues: Optional[List[str]] = None

# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    data: Dict[str, Any]
    timestamp: str

class CelebrationEvent(BaseModel):
    """Celebration event for WebSocket broadcast"""
    event_type: str  # "celebration_started", "celebration_ended", "celebration_progress"
    celebration_type: CelebrationType
    team_name: str
    progress: Optional[int] = Field(None, description="Progress percentage 0-100")
    devices_count: int
    timestamp: str

class DeviceEvent(BaseModel):
    """Device status change event"""
    event_type: str  # "device_online", "device_offline", "device_added", "device_removed"
    device_id: str
    device_name: str
    status: DeviceStatus
    timestamp: str

class TeamEvent(BaseModel):
    """Team change event"""
    event_type: str = "team_changed"
    old_team_id: Optional[str]
    new_team_id: str
    team_name: str
    timestamp: str

class GameEvent(BaseModel):
    """Game update event for WebSocket broadcast"""
    event_type: str  # "game_update", "score_change", "quarter_change", "game_start", "game_end"
    game_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    status: GameStatus
    period: GamePeriod
    time_remaining: Optional[str] = None
    field_position: Optional[FieldPosition] = None
    timestamp: str

class PlayEvent(BaseModel):
    """Play-by-play event"""
    event_type: str = "play_update"
    game_id: str
    play_description: str
    down: Optional[int]
    yards_to_go: Optional[int]
    field_position: Optional[FieldPosition]
    scoring_play: bool = False
    celebration_triggered: Optional[CelebrationType] = None
    timestamp: str

# Error Models
class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any

class ErrorResponse(BaseModel):
    """Error response format"""
    error: str
    details: Optional[str] = None
    validation_errors: Optional[List[ValidationError]] = None
    timestamp: str