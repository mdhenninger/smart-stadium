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


def _initialize_team_colors(lights_service: LightsService, teams_database: Dict[str, Any]) -> None:
    """Load team colors from teams_database into the lights service.
    
    The teams_database uses a flat structure with unified keys like "NFL-BUFFALO-BILLS".
    Each team has lighting_primary_color and lighting_secondary_color for celebrations.
    """
    count = 0
    
    # Get teams from the "teams" key in the database
    all_teams = teams_database.get("teams", {})
    
    for unified_key, team_data in all_teams.items():
        try:
            if not isinstance(team_data, dict):
                continue
            
            # Extract team metadata
            sport = team_data.get("sport", "").lower()
            abbreviation = team_data.get("abbreviation", "")
            
            if not sport or not abbreviation:
                logger.warning(f"Skipping team {unified_key}: missing sport or abbreviation")
                continue
            
            # Use lighting-optimized colors for celebrations
            lighting_primary = team_data.get("lighting_primary_color")
            lighting_secondary = team_data.get("lighting_secondary_color")
            
            if not lighting_primary or not lighting_secondary:
                logger.warning(f"Skipping team {unified_key}: missing lighting colors")
                continue
            
            # Convert to tuples and register with lights service
            primary = tuple(lighting_primary)
            secondary = tuple(lighting_secondary)
            lights_service.set_team_colors(abbreviation, primary, secondary, sport=sport)
            count += 1
            
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Failed to load colors for team {unified_key}: {e}")
    
    logger.info(f"Loaded {count} team color configurations into lights service")


def build_container(config_manager: ConfigManager, websocket_manager: WebSocketManager) -> ServiceContainer:
    config = config_manager.get_config()
    lights_service = LightsService(config.light_ips, govee_config=config.govee_config)
    
    # Load all team colors into lights service from teams database
    _initialize_team_colors(lights_service, config.teams_database)
    
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
