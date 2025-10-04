"""Monitoring services that poll ESPN scoreboards and trigger celebrations."""

from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List

from app.models.game import GameSnapshot, GameStatus, Scoreboard, Sport
from app.services.espn_client import EspnScoreboardClient
from app.services.history_store import HistoryStore
from app.services.lights_service import LightsService
from app.services.monitoring_store import MonitoringStore
from app.websocket.manager import WebSocketManager
from app.utils.logging import get_logger

logger = get_logger(__name__)

CelebrationCallback = Callable[[GameSnapshot, str, int], asyncio.Future]


@dataclass(slots=True)
class MonitorConfig:
    sport: Sport
    poll_interval: int
    favorite_teams: List[str]


class SportMonitor:
    """Polls ESPN for a single sport and triggers celebrations on events."""

    def __init__(
        self,
        config: MonitorConfig,
        client: EspnScoreboardClient,
        lights: LightsService,
        history: HistoryStore,
        monitoring_store: MonitoringStore,
        websocket_manager: WebSocketManager | None,
    ) -> None:
        self._config = config
        self._client = client
        self._lights = lights
        self._history = history
        self._monitoring_store = monitoring_store
        self._ws_manager = websocket_manager
        self._running = False
        self._task: asyncio.Task | None = None
        self._last_scores: Dict[str, Dict[str, int]] = defaultdict(dict)
        self._last_status: Dict[str, GameStatus] = {}

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _run_loop(self) -> None:
        logger.info("Starting %s monitor", self._config.sport.value)
        while self._running:
            try:
                board = await self._client.fetch_scoreboard(self._config.sport)
                await self._process_scoreboard(board)
            except Exception as exc:
                logger.exception("Monitor loop error", extra={"sport": self._config.sport.value, "error": str(exc)})
            await asyncio.sleep(self._config.poll_interval)

    async def _process_scoreboard(self, board: Scoreboard) -> None:
        for game in board.games:
            # Only process games with favorite teams (if favorite_teams is configured)
            # Empty list should mean "no favorites" not "all games"
            if len(self._config.favorite_teams) > 0 and not (
                game.home.abbreviation in self._config.favorite_teams
                or game.away.abbreviation in self._config.favorite_teams
            ):
                continue
            await self._handle_game(game)

    async def _handle_game(self, game: GameSnapshot) -> None:
        last_scores = self._last_scores[game.game_id]
        current_scores = game.scores
        previous_status = self._last_status.get(game.game_id)

        # Only process score changes for games that are IN PROGRESS
        if game.status == GameStatus.IN_PROGRESS:
            # Detect score increases (only if we've seen this game before)
            if previous_status is not None:
                for team_abbr, score in current_scores.items():
                    previous = last_scores.get(team_abbr, 0)
                    if score > previous:
                        delta = score - previous
                        await self._handle_score_event(game, team_abbr, delta)
            
            # Update scores for next poll
            for team_abbr, score in current_scores.items():
                last_scores[team_abbr] = score
        else:
            # For non-live games, just update the scores without triggering celebrations
            # This prevents false celebrations when first discovering a finished game
            for team_abbr, score in current_scores.items():
                last_scores[team_abbr] = score

        # Detect game completion for victory celebration
        if game.status == GameStatus.FINAL and previous_status and previous_status != GameStatus.FINAL:
            await self._handle_victory(game)
            
            # Auto-remove finished game from monitoring
            removed = await self._monitoring_store.remove_monitoring(game.game_id)
            if removed:
                logger.info("Auto-removed finished game %s from monitoring", game.game_id)
                if self._ws_manager:
                    await self._ws_manager.broadcast(
                        {
                            "type": "monitoring_removed",
                            "game_id": game.game_id,
                            "reason": "game_finished",
                        }
                    )
        
        self._last_status[game.game_id] = game.status

        # Red zone detection
        if game.red_zone.active and game.red_zone.team_abbr:
            await self._lights.start_red_zone(game.red_zone.team_abbr)
        else:
            await self._lights.stop_red_zone()

    async def _handle_score_event(self, game: GameSnapshot, team_abbr: str, delta: int) -> None:
        # Check if this team is being monitored
        is_monitored = await self._monitoring_store.is_team_monitored(game.game_id, team_abbr)
        if not is_monitored:
            logger.debug(
                "Score change detected but team not monitored",
                extra={"sport": self._config.sport.value, "team": team_abbr, "delta": delta, "game": game.game_id},
            )
            return  # Don't celebrate if not monitoring this team
        
        team_name = game.home.display_name if game.home.abbreviation == team_abbr else game.away.display_name
        logger.info(
            "Score change detected for monitored team",
            extra={"sport": self._config.sport.value, "team": team_abbr, "delta": delta, "game": game.game_id},
        )

        # Map sport enum to simple identifier for color lookup
        sport_id = "nfl" if self._config.sport.value == "nfl" else "cfb"

        if delta >= 6:
            await self._lights.celebrate_touchdown(team_name, team_abbr=team_abbr, sport=sport_id)
        elif delta == 3:
            await self._lights.celebrate_field_goal(team_name, team_abbr=team_abbr, sport=sport_id)
        elif delta == 1:
            await self._lights.celebrate_extra_point(team_name, team_abbr=team_abbr, sport=sport_id)
        elif delta == 2:
            await self._lights.celebrate_two_point(team_name, team_abbr=team_abbr, sport=sport_id)
        else:
            await self._lights.celebrate_score(team_name, delta, team_abbr=team_abbr, sport=sport_id)

        await self._history.record_celebration(
            sport=self._config.sport.value,
            team=team_abbr,
            event_type=f"score_{delta}",
            game_id=game.game_id,
            detail=f"{team_abbr} +{delta} ({game.home.abbreviation} {game.home.score}-{game.away.abbreviation} {game.away.score})",
        )
        await self._broadcast(
            {
                "type": "celebration",
                "sport": self._config.sport.value,
                "team": team_abbr,
                "delta": delta,
                "gameId": game.game_id,
            }
        )

    async def _handle_victory(self, game: GameSnapshot) -> None:
        winner = game.home if game.home.score > game.away.score else game.away
        final_score = f"{game.home.abbreviation} {game.home.score} - {game.away.abbreviation} {game.away.score}"
        await self._lights.celebrate_victory(winner.display_name, final_score)
        await self._history.record_celebration(
            sport=self._config.sport.value,
            team=winner.abbreviation,
            event_type="victory",
            game_id=game.game_id,
            detail=final_score,
        )
        await self._broadcast(
            {
                "type": "victory",
                "sport": self._config.sport.value,
                "winner": winner.abbreviation,
                "gameId": game.game_id,
                "final": final_score,
            }
        )

    async def _broadcast(self, message: dict) -> None:
        if self._ws_manager:
            await self._ws_manager.broadcast(message)


class MonitoringCoordinator:
    """Coordinates multiple sport monitors."""

    def __init__(
        self,
        client: EspnScoreboardClient,
        lights: LightsService,
        history: HistoryStore,
        monitoring_store: MonitoringStore,
        websocket_manager: WebSocketManager | None,
    ) -> None:
        self._client = client
        self._lights = lights
        self._history = history
        self._monitoring_store = monitoring_store
        self._ws_manager = websocket_manager
        self._monitors: Dict[Sport, SportMonitor] = {}

    def configure(self, configs: List[MonitorConfig]) -> None:
        for cfg in configs:
            monitor = SportMonitor(cfg, self._client, self._lights, self._history, self._monitoring_store, self._ws_manager)
            self._monitors[cfg.sport] = monitor

    async def start_all(self) -> None:
        for monitor in self._monitors.values():
            await monitor.start()

    async def stop_all(self) -> None:
        for monitor in self._monitors.values():
            await monitor.stop()
