"""
Live Game Monitoring Service
Background service for real-time game monitoring and automatic celebration triggering
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from models import (
    Game, GameStatus, CelebrationType, GameEvent, PlayEvent,
    WebSocketMessage, FieldPosition, League
)
from websocket_manager import connection_manager, celebration_broadcaster
from espn_service import espn_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GameState:
    """Tracks the state of a monitored game"""
    game_id: str
    home_team_id: str
    away_team_id: str
    home_score: int = 0
    away_score: int = 0
    last_update: datetime = field(default_factory=datetime.utcnow)
    status: GameStatus = GameStatus.SCHEDULED
    period: str = "pregame"
    time_remaining: str = "00:00"
    field_position: Optional[FieldPosition] = None
    red_zone_active: bool = False
    last_celebration: Optional[str] = None
    celebration_count: int = 0

class LiveGameMonitor:
    """Monitors live games and triggers celebrations automatically"""
    
    def __init__(self, stadium_api=None):
        self.stadium_api = stadium_api
        self.espn_service = espn_service  # Use the singleton instance
        self.monitored_games: Dict[str, GameState] = {}
        self.monitoring_active = False
        self.poll_interval = 15  # seconds
        self.bills_team_names = ["Buffalo Bills", "Buffalo", "BUF"]
        self.target_teams: Set[str] = set()  # Teams to monitor for celebrations
        self.last_poll_time = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Celebration thresholds
        self.big_play_threshold = 40  # yards for big play celebration
        self.celebration_cooldown = 30  # seconds between celebrations
        
    async def initialize(self):
        """Initialize the monitoring service"""
        try:
            logger.info("🎮 Initializing Live Game Monitor...")
            
            # Add Buffalo Bills as default monitoring target
            self.target_teams.update(self.bills_team_names)
            
            logger.info(f"📺 Monitoring teams: {', '.join(self.target_teams)}")
            logger.info(f"⏱️ Poll interval: {self.poll_interval} seconds")
            logger.info("✅ Live Game Monitor initialized successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Live Game Monitor: {e}")
            return False
    
    async def start_monitoring(self):
        """Start the live game monitoring loop"""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("🚀 Starting live game monitoring...")
        
        try:
            while self.monitoring_active:
                await self._monitoring_cycle()
                await asyncio.sleep(self.poll_interval)
                
        except Exception as e:
            logger.error(f"❌ Monitoring loop error: {e}")
        finally:
            self.monitoring_active = False
            logger.info("🛑 Live game monitoring stopped")
    
    async def stop_monitoring(self):
        """Stop the live game monitoring"""
        logger.info("🛑 Stopping live game monitoring...")
        self.monitoring_active = False
        await self.espn_service.close()
    
    async def add_monitoring_target(self, team_name: str):
        """Add a team to monitoring targets"""
        self.target_teams.add(team_name)
        logger.info(f"➕ Added monitoring target: {team_name}")
        
        # Broadcast update
        await connection_manager.broadcast(
            WebSocketMessage(
                type="monitoring_update",
                data={
                    "action": "team_added",
                    "team": team_name,
                    "total_targets": len(self.target_teams)
                },
                timestamp=datetime.utcnow().isoformat()
            ),
            "monitoring"
        )
    
    async def remove_monitoring_target(self, team_name: str):
        """Remove a team from monitoring targets"""
        self.target_teams.discard(team_name)
        logger.info(f"➖ Removed monitoring target: {team_name}")
        
        # Remove related games from monitoring
        games_to_remove = []
        for game_id, game_state in self.monitored_games.items():
            if not self._is_target_team_in_game(game_state):
                games_to_remove.append(game_id)
        
        for game_id in games_to_remove:
            del self.monitored_games[game_id]
            logger.info(f"🗑️ Removed game {game_id} from monitoring")
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        cycle_start = time.time()
        self.last_poll_time = cycle_start
        
        try:
            # Get live games
            live_games_data = await self.espn_service.fetch_scoreboard(League.NFL)
            college_games_data = await self.espn_service.fetch_scoreboard(League.COLLEGE)
            
            # Process NFL games
            await self._process_games(live_games_data.get("events", []), League.NFL)
            
            # Process College games
            await self._process_games(college_games_data.get("events", []), League.COLLEGE)
            
            # Clean up finished games
            await self._cleanup_finished_games()
            
            # Reset error counter on success
            self.consecutive_errors = 0
            
            cycle_time = time.time() - cycle_start
            logger.debug(f"📊 Monitoring cycle completed in {cycle_time:.2f}s")
            
        except Exception as e:
            self.consecutive_errors += 1
            logger.error(f"❌ Monitoring cycle error ({self.consecutive_errors}/{self.max_consecutive_errors}): {e}")
            
            if self.consecutive_errors >= self.max_consecutive_errors:
                logger.error("🚨 Too many consecutive errors, stopping monitoring")
                await self.stop_monitoring()
    
    async def _process_games(self, games_data: List[dict], league: League):
        """Process games from ESPN data"""
        for game_data in games_data:
            try:
                # Parse game using existing ESPN service
                game = self.espn_service.parse_game_from_espn(game_data, league)
                
                # Check if this game involves a target team
                if not self._is_target_game(game):
                    continue
                
                # Process the game
                await self._process_game_update(game)
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing game: {e}")
                continue
    
    def _is_target_game(self, game: Game) -> bool:
        """Check if game involves a target team"""
        home_team = game.home_team.team_name.lower()
        away_team = game.away_team.team_name.lower()
        
        for target in self.target_teams:
            target_lower = target.lower()
            if target_lower in home_team or target_lower in away_team:
                return True
        
        return False
    
    def _is_target_team_in_game(self, game_state: GameState) -> bool:
        """Check if game state involves a target team"""
        for target in self.target_teams:
            target_lower = target.lower()
            if (target_lower in game_state.home_team_id.lower() or 
                target_lower in game_state.away_team_id.lower()):
                return True
        return False
    
    async def _process_game_update(self, game: Game):
        """Process a game update and check for celebration triggers"""
        game_id = game.id
        
        # Get or create game state
        if game_id not in self.monitored_games:
            self.monitored_games[game_id] = GameState(
                game_id=game_id,
                home_team_id=game.home_team.team_id,
                away_team_id=game.away_team.team_id,
                home_score=game.home_team.score,
                away_score=game.away_team.score,
                status=game.status,
                period=game.clock.period,
                time_remaining=game.clock.time_remaining
            )
            
            logger.info(f"📺 Started monitoring: {game.away_team.team_name} @ {game.home_team.team_name}")
            
            # Broadcast new game monitoring
            await self._broadcast_game_event(game, "game_monitoring_started")
            
            return  # Don't check for celebrations on first detection
        
        # Get previous state
        prev_state = self.monitored_games[game_id]
        
        # Check for score changes (potential celebrations)
        await self._check_score_changes(game, prev_state)
        
        # Check for red zone status
        await self._check_red_zone_status(game, prev_state)
        
        # Update game state
        prev_state.home_score = game.home_team.score
        prev_state.away_score = game.away_team.score
        prev_state.last_update = datetime.utcnow()
        prev_state.status = game.status
        prev_state.period = game.clock.period
        prev_state.time_remaining = game.clock.time_remaining
        
        if game.play_info and game.play_info.field_position:
            prev_state.field_position = game.play_info.field_position
            prev_state.red_zone_active = game.play_info.field_position.is_red_zone
        
        # Broadcast game update
        await self._broadcast_game_event(game, "game_update")
    
    async def _check_score_changes(self, game: Game, prev_state: GameState):
        """Check for score changes and trigger appropriate celebrations"""
        home_score_diff = game.home_team.score - prev_state.home_score
        away_score_diff = game.away_team.score - prev_state.away_score
        
        # Determine which team scored and celebration type
        if home_score_diff > 0:
            await self._handle_scoring_play(
                game, game.home_team.team_name, home_score_diff, prev_state
            )
        
        if away_score_diff > 0:
            await self._handle_scoring_play(
                game, game.away_team.team_name, away_score_diff, prev_state
            )
    
    async def _handle_scoring_play(self, game: Game, team_name: str, points: int, prev_state: GameState):
        """Handle a scoring play and trigger appropriate celebration"""
        # Check celebration cooldown
        if (prev_state.last_celebration and 
            (datetime.utcnow() - datetime.fromisoformat(prev_state.last_celebration)).seconds < self.celebration_cooldown):
            logger.debug(f"⏱️ Celebration cooldown active for {team_name}")
            return
        
        # Determine celebration type based on points
        celebration_type = self._determine_celebration_type(points)
        
        # Check if this is a target team
        is_target_team = any(
            target.lower() in team_name.lower() 
            for target in self.target_teams
        )
        
        if is_target_team:
            logger.info(f"🎉 {team_name} scored {points} points! Triggering {celebration_type.value}")
            
            # Trigger celebration via stadium API
            if self.stadium_api:
                try:
                    await self._trigger_celebration(celebration_type, team_name)
                    prev_state.last_celebration = datetime.utcnow().isoformat()
                    prev_state.celebration_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to trigger celebration: {e}")
        
        # Broadcast scoring event regardless of target team
        await self._broadcast_play_event(
            game, f"{team_name} scored {points} points", 
            scoring_play=True, 
            celebration_triggered=celebration_type if is_target_team else None
        )
    
    def _determine_celebration_type(self, points: int) -> CelebrationType:
        """Determine celebration type based on points scored"""
        if points == 6:
            return CelebrationType.TOUCHDOWN
        elif points == 3:
            return CelebrationType.FIELD_GOAL
        elif points == 1:
            return CelebrationType.EXTRA_POINT
        elif points == 2:
            return CelebrationType.TWO_POINT
        elif points == 8:  # Touchdown + 2-point conversion
            return CelebrationType.TOUCHDOWN
        else:
            return CelebrationType.GENERIC_SCORE
    
    async def _check_red_zone_status(self, game: Game, prev_state: GameState):
        """Check for red zone entry and trigger ambient lighting"""
        if not game.play_info or not game.play_info.field_position:
            return
        
        current_red_zone = game.play_info.field_position.is_red_zone
        prev_red_zone = prev_state.red_zone_active
        
        # Check for red zone entry
        if current_red_zone and not prev_red_zone:
            # Determine which team is in red zone
            possession_team = game.play_info.possession_team_id
            
            # Check if it's a target team
            is_target_team = False
            team_name = "Unknown"
            
            if possession_team == game.home_team.team_id:
                team_name = game.home_team.team_name
                is_target_team = any(target.lower() in team_name.lower() for target in self.target_teams)
            elif possession_team == game.away_team.team_id:
                team_name = game.away_team.team_name
                is_target_team = any(target.lower() in team_name.lower() for target in self.target_teams)
            
            if is_target_team:
                logger.info(f"🎯 {team_name} entered the red zone!")
                
                # Trigger red zone celebration
                if self.stadium_api:
                    try:
                        await self._trigger_celebration(CelebrationType.RED_ZONE, team_name)
                    except Exception as e:
                        logger.error(f"❌ Failed to trigger red zone celebration: {e}")
            
            # Broadcast red zone event
            await self._broadcast_play_event(
                game, f"{team_name} entered the red zone",
                scoring_play=False,
                celebration_triggered=CelebrationType.RED_ZONE if is_target_team else None
            )
    
    async def _trigger_celebration(self, celebration_type: CelebrationType, team_name: str):
        """Trigger a celebration via the stadium API"""
        if not self.stadium_api:
            logger.warning("⚠️ No stadium API available for celebration")
            return
        
        try:
            # This would call the actual celebration endpoint
            # For now, we'll simulate by broadcasting the celebration event
            await celebration_broadcaster.broadcast_celebration_start(
                celebration_type, team_name, 
                duration=self._get_celebration_duration(celebration_type),
                devices_count=3  # Mock device count
            )
            
            logger.info(f"🎉 Triggered {celebration_type.value} celebration for {team_name}")
            
        except Exception as e:
            logger.error(f"❌ Celebration trigger failed: {e}")
            raise
    
    def _get_celebration_duration(self, celebration_type: CelebrationType) -> int:
        """Get celebration duration based on type"""
        durations = {
            CelebrationType.TOUCHDOWN: 30,
            CelebrationType.FIELD_GOAL: 10,
            CelebrationType.EXTRA_POINT: 5,
            CelebrationType.TWO_POINT: 10,
            CelebrationType.SAFETY: 15,
            CelebrationType.RED_ZONE: 3,
            CelebrationType.GENERIC_SCORE: 10
        }
        return durations.get(celebration_type, 5)
    
    async def _broadcast_game_event(self, game: Game, event_type: str):
        """Broadcast a game event via WebSocket"""
        event = GameEvent(
            event_type=event_type,
            game_id=game.id,
            home_team=game.home_team.team_name,
            away_team=game.away_team.team_name,
            home_score=game.home_team.score,
            away_score=game.away_team.score,
            status=game.status,
            period=game.clock.period,
            time_remaining=game.clock.time_remaining,
            field_position=game.play_info.field_position if game.play_info else None,
            timestamp=datetime.utcnow().isoformat()
        )
        
        message = WebSocketMessage(
            type="game_event",
            data=event.model_dump(),
            timestamp=datetime.utcnow().isoformat()
        )
        
        await connection_manager.broadcast(message, "games")
    
    async def _broadcast_play_event(self, game: Game, description: str, 
                                   scoring_play: bool = False, 
                                   celebration_triggered: Optional[CelebrationType] = None):
        """Broadcast a play event via WebSocket"""
        event = PlayEvent(
            event_type="play_update",
            game_id=game.id,
            play_description=description,
            down=game.play_info.down if game.play_info else None,
            yards_to_go=game.play_info.yards_to_go if game.play_info else None,
            field_position=game.play_info.field_position if game.play_info else None,
            scoring_play=scoring_play,
            celebration_triggered=celebration_triggered,
            timestamp=datetime.utcnow().isoformat()
        )
        
        message = WebSocketMessage(
            type="play_event", 
            data=event.model_dump(),
            timestamp=datetime.utcnow().isoformat()
        )
        
        await connection_manager.broadcast(message, "plays")
    
    async def _cleanup_finished_games(self):
        """Remove finished games from monitoring"""
        current_time = datetime.utcnow()
        games_to_remove = []
        
        for game_id, game_state in self.monitored_games.items():
            # Remove games that finished more than 1 hour ago
            if (game_state.status == GameStatus.FINAL and 
                (current_time - game_state.last_update) > timedelta(hours=1)):
                games_to_remove.append(game_id)
        
        for game_id in games_to_remove:
            game_state = self.monitored_games[game_id]
            del self.monitored_games[game_id]
            logger.info(f"🧹 Cleaned up finished game: {game_state.home_team_id} vs {game_state.away_team_id}")
    
    def get_monitoring_status(self) -> dict:
        """Get current monitoring status"""
        return {
            "active": self.monitoring_active,
            "monitored_games": len(self.monitored_games),
            "target_teams": list(self.target_teams),
            "poll_interval": self.poll_interval,
            "last_poll": self.last_poll_time,
            "consecutive_errors": self.consecutive_errors,
            "games": [
                {
                    "game_id": state.game_id,
                    "home_team": state.home_team_id,
                    "away_team": state.away_team_id,
                    "score": f"{state.away_score}-{state.home_score}",
                    "status": state.status,
                    "celebrations": state.celebration_count,
                    "last_update": state.last_update.isoformat()
                }
                for state in self.monitored_games.values()
            ]
        }

# Global monitor instance
live_monitor = LiveGameMonitor()