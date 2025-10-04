"""Application service container."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.core.config_manager import AppConfig, ConfigManager
from app.models.game import Sport
from app.services.device_manager import DeviceManager
from app.services.espn_client import EspnScoreboardClient
from app.services.history_store import HistoryStore
from app.services.lights_service import LightsService
from app.services.monitoring import MonitorConfig, MonitoringCoordinator
from app.services.monitoring_store import MonitoringStore
from app.websocket.manager import WebSocketManager
from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class ServiceContainer:
    config: AppConfig
    lights_service: LightsService
    device_manager: DeviceManager
    scoreboard_client: EspnScoreboardClient
    monitoring: MonitoringCoordinator
    history_store: HistoryStore
    monitoring_store: MonitoringStore
    websocket_manager: WebSocketManager


def _initialize_team_colors(lights_service: LightsService, team_colors: Dict[str, Any]) -> None:
    """Load all team colors from config into lights service.
    
    Prefers lighting-optimized colors (lighting_primary_color, lighting_secondary_color) 
    over official team colors for better bulb visibility. Falls back to official colors
    if lighting colors are not defined.
    
    Handles nested structure: {"nfl_teams": {"AFC_East": {"BUF": {...}}}}
    Tracks sport context to disambiguate teams with same abbreviation (e.g., NFL BUF vs CFB BUF).
    """
    count = 0
    
    # Map top-level keys to sport identifiers
    SPORT_MAPPING = {
        "nfl_teams": "nfl",
        "college_teams": "cfb",
        "nhl_teams": "nhl",
        "nba_teams": "nba",
        "mlb_teams": "mlb",
    }
    
    def _load_team(team_abbr: str, colors: Dict[str, Any], sport: str | None = None) -> None:
        nonlocal count
        try:
            # Skip if not a team entry (no primary_color field)
            if "primary_color" not in colors:
                return
            
            # Prefer lighting-optimized colors, fallback to official colors
            primary = tuple(colors.get("lighting_primary_color", colors["primary_color"]))
            secondary = tuple(colors.get("lighting_secondary_color", colors["secondary_color"]))
            
            lights_service.set_team_colors(team_abbr, primary, secondary, sport=sport)
            count += 1
        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to load colors for team {team_abbr}: {e}")
    
    # Recursively traverse the nested team colors structure with sport context
    def _traverse(data: Any, sport: str | None = None) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    # Check if this key indicates a sport category
                    detected_sport = SPORT_MAPPING.get(key, sport)
                    
                    # Check if this is a team entry (has primary_color) or a division/category
                    if "primary_color" in value:
                        _load_team(key, value, sport=detected_sport)
                    else:
                        # Recurse into divisions/categories, carrying sport context
                        _traverse(value, sport=detected_sport)
    
    _traverse(team_colors)
    logger.info(f"Loaded {count} team color configurations into lights service")


def build_container(config_manager: ConfigManager, websocket_manager: WebSocketManager) -> ServiceContainer:
    config = config_manager.get_config()
    lights_service = LightsService(config.light_ips)
    
    # Load all team colors into lights service
    _initialize_team_colors(lights_service, config.team_colors)
    
    history_store = HistoryStore(config_manager.settings.data_dir / "history.db")
    monitoring_store = MonitoringStore(config_manager.settings.data_dir / "monitoring.db")
    device_manager = DeviceManager(config, lights_service, history_store)
    scoreboard_client = EspnScoreboardClient()

    monitoring = MonitoringCoordinator(scoreboard_client, lights_service, history_store, monitoring_store, websocket_manager)

    monitor_configs: list[MonitorConfig] = []
    sports_enabled = config.get_sports_enabled()
    if sports_enabled.get("nfl", False):
        monitor_configs.append(
            MonitorConfig(
                sport=Sport.NFL,
                poll_interval=config_manager.settings.nfl_poll_interval,
                favorite_teams=config.get_favorite_teams("nfl"),
            )
        )
    if sports_enabled.get("college_football", False):
        monitor_configs.append(
            MonitorConfig(
                sport=Sport.COLLEGE_FOOTBALL,
                poll_interval=config_manager.settings.cfb_poll_interval,
                favorite_teams=config.get_favorite_teams("college_football"),
            )
        )

    monitoring.configure(monitor_configs)
    return ServiceContainer(
        config=config,
        lights_service=lights_service,
        device_manager=device_manager,
        scoreboard_client=scoreboard_client,
        monitoring=monitoring,
        history_store=history_store,
        monitoring_store=monitoring_store,
        websocket_manager=websocket_manager,
    )
