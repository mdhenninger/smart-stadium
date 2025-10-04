"""Client for ESPN public scoreboard endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

import httpx

from app.models.game import GameSnapshot, GameStatus, Scoreboard, Sport, TeamScore, RedZoneInfo, GameSituation
from app.utils.logging import get_logger

logger = get_logger(__name__)


class EspnScoreboardClient:
    ENDPOINTS: Dict[Sport, str] = {
        Sport.NFL: "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        Sport.COLLEGE_FOOTBALL: "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
    }

    def __init__(self, timeout: float = 10.0):
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_scoreboard(self, sport: Sport) -> Scoreboard:
        url = self.ENDPOINTS[sport]
        logger.debug("Fetching ESPN scoreboard", extra={"sport": sport.value, "url": url})
        response = await self._client.get(url)
        response.raise_for_status()
        payload = response.json()

        games = []
        for event in payload.get("events", []):
            try:
                games.append(self._parse_event(event, sport))
            except Exception as exc:
                logger.warning("Failed to parse event", extra={"sport": sport.value, "error": str(exc)})

        return Scoreboard(sport=sport, games=games, fetched_at=datetime.now(timezone.utc))

    def _parse_event(self, event: Dict, sport: Sport) -> GameSnapshot:
        competition = (event.get("competitions") or [{}])[0]
        competitors = competition.get("competitors", [])

        home_comp = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away_comp = next((c for c in competitors if c.get("homeAway") == "away"), {})

        home_team = self._parse_competitor(home_comp)
        away_team = self._parse_competitor(away_comp)

        status_info = event.get("status", {}).get("type", {})
        status = self._map_status(status_info.get("state") or status_info.get("name"))

        situation_data = competition.get("situation", {}) or {}
        
        # Determine which team has possession for red zone
        possession_team_abbr = None
        if situation_data.get("possession"):
            possession_team_id = situation_data.get("possession")
            # Match possession team ID to home or away team
            if home_comp.get("team", {}).get("id") == possession_team_id:
                possession_team_abbr = home_team.abbreviation
            elif away_comp.get("team", {}).get("id") == possession_team_id:
                possession_team_abbr = away_team.abbreviation
        
        red_zone = RedZoneInfo(
            active=bool(situation_data.get("isRedZone")),
            team_abbr=possession_team_abbr,
            yard_line=situation_data.get("yardLine"),
        )

        # Parse game situation for in-progress games
        game_situation = None
        if status == GameStatus.IN_PROGRESS and situation_data:
            status_obj = event.get("status", {})
            game_situation = GameSituation(
                possession_team_id=situation_data.get("possession"),
                down_distance=situation_data.get("shortDownDistanceText"),
                field_position=situation_data.get("possessionText"),
                is_red_zone=bool(situation_data.get("isRedZone")),
                clock=status_obj.get("displayClock"),
                period=status_obj.get("period"),
            )

        last_update = status_info.get("detail") or event.get("date")
        try:
            parsed_last_update = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
        except Exception:
            parsed_last_update = datetime.now(timezone.utc)

        return GameSnapshot(
            id=event.get("id"),
            sport=sport,
            home=home_team,
            away=away_team,
            status=status,
            last_update=parsed_last_update,
            red_zone=red_zone,
            situation=game_situation,
        )

    @staticmethod
    def _parse_competitor(competitor: Dict) -> TeamScore:
        team = competitor.get("team", {})
        return TeamScore(
            team_id=team.get("id", ""),
            abbreviation=team.get("abbreviation", ""),
            display_name=team.get("displayName", team.get("name", "")),
            score=int(competitor.get("score", 0)),
        )

    @staticmethod
    def _map_status(state: str | None) -> GameStatus:
        if not state:
            return GameStatus.UNKNOWN
        state = state.lower()
        if state in {"pre", "pre-game", "scheduled"}:
            return GameStatus.PREGAME
        if state in {"in", "in-progress", "inprogress"}:
            return GameStatus.IN_PROGRESS
        if state in {"post", "postgame", "final"}:
            return GameStatus.FINAL
        return GameStatus.UNKNOWN
