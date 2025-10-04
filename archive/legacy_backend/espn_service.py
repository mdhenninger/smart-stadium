"""
ESPN API Service
Separate service for ESPN data fetching to avoid circular imports
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from models import (
    Game, GameSummary, GameStatus, League, GamePeriod, 
    FieldPosition, GameScore, GameClock, PlayInfo
)

# ESPN API endpoints
ESPN_NFL_SCOREBOARD = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
ESPN_COLLEGE_SCOREBOARD = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
ESPN_GAME_SUMMARY = "http://site.api.espn.com/apis/site/v2/sports/football/{league}/summary"

class ESPNGameService:
    """Service for fetching game data from ESPN API"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def close(self):
        """Alias for close_session for compatibility"""
        await self.close_session()
    
    async def get_todays_games(self, league: League = League.NFL) -> List[Game]:
        """Get all games for today"""
        await self.ensure_session()
        
        url = ESPN_NFL_SCOREBOARD if league == League.NFL else ESPN_COLLEGE_SCOREBOARD
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"ESPN API returned status {response.status}")
                
                data = await response.json()
                games = []
                
                for event in data.get('events', []):
                    game = self._parse_game_data(event, league)
                    if game:
                        games.append(game)
                
                return games
        
        except Exception as e:
            print(f"❌ Error fetching games: {e}")
            return []
    
    async def get_live_games(self, league: League = League.NFL) -> List[Game]:
        """Get currently live games"""
        games = await self.get_todays_games(league)
        return [game for game in games if game.status in [GameStatus.IN_PROGRESS, GameStatus.HALFTIME]]
    
    async def get_game_details(self, game_id: str, league: League = League.NFL) -> Optional[Game]:
        """Get detailed information for a specific game"""
        await self.ensure_session()
        
        league_str = "nfl" if league == League.NFL else "college-football"
        url = ESPN_GAME_SUMMARY.format(league=league_str)
        
        try:
            async with self.session.get(url, params={'event': game_id}) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Parse header info
                header = data.get('header', {})
                competition = header.get('competitions', [{}])[0]
                
                return self._parse_game_data(header, league)
        
        except Exception as e:
            print(f"❌ Error fetching game details: {e}")
            return None
    
    def _parse_game_data(self, event_data: Dict[Any, Any], league: League) -> Optional[Game]:
        """Parse ESPN event data into Game object"""
        try:
            competition = event_data.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) != 2:
                return None
            
            # Find home and away teams
            home_team = None
            away_team = None
            
            for comp in competitors:
                if comp.get('homeAway') == 'home':
                    home_team = comp
                else:
                    away_team = comp
            
            if not home_team or not away_team:
                return None
            
            # Parse basic game info
            game_id = event_data.get('id', '')
            game_date = event_data.get('date', '')
            
            # Parse scores
            home_score = int(home_team.get('score', 0))
            away_score = int(away_team.get('score', 0))
            
            # Parse team info
            home_team_info = home_team.get('team', {})
            away_team_info = away_team.get('team', {})
            
            # Parse status
            status_data = competition.get('status', {})
            status_type = status_data.get('type', {}).get('name', 'Unknown')
            
            game_status = self._map_espn_status(status_type)
            
            # Parse period info
            period_data = status_data.get('period', 1)
            period = self._map_espn_period(period_data, league)
            
            # Parse clock
            clock_data = status_data.get('displayClock', '00:00')
            
            return Game(
                game_id=game_id,
                league=league,
                home_team_id=home_team_info.get('id', ''),
                home_team_name=home_team_info.get('displayName', ''),
                home_team_abbreviation=home_team_info.get('abbreviation', ''),
                away_team_id=away_team_info.get('id', ''),
                away_team_name=away_team_info.get('displayName', ''),
                away_team_abbreviation=away_team_info.get('abbreviation', ''),
                home_score=home_score,
                away_score=away_score,
                status=game_status,
                period=period,
                game_clock=GameClock(
                    display_clock=clock_data,
                    seconds_remaining=self._parse_clock_seconds(clock_data)
                ),
                game_date=datetime.fromisoformat(game_date.replace('Z', '+00:00')) if game_date else datetime.now(),
                venue=competition.get('venue', {}).get('fullName', ''),
                field_position=self._parse_field_position(competition)
            )
        
        except Exception as e:
            print(f"❌ Error parsing game data: {e}")
            return None
    
    def _map_espn_status(self, espn_status: str) -> GameStatus:
        """Map ESPN status to our GameStatus enum"""
        status_map = {
            'STATUS_SCHEDULED': GameStatus.SCHEDULED,
            'STATUS_IN_PROGRESS': GameStatus.IN_PROGRESS,
            'STATUS_HALFTIME': GameStatus.HALFTIME,
            'STATUS_FINAL': GameStatus.FINAL,
            'STATUS_POSTPONED': GameStatus.POSTPONED,
            'STATUS_CANCELLED': GameStatus.CANCELLED,
            'STATUS_SUSPENDED': GameStatus.POSTPONED
        }
        return status_map.get(espn_status, GameStatus.SCHEDULED)
    
    def _map_espn_period(self, period: int, league: League) -> GamePeriod:
        """Map ESPN period to our GamePeriod enum"""
        if league == League.NFL:
            period_map = {
                1: GamePeriod.FIRST_QUARTER,
                2: GamePeriod.SECOND_QUARTER, 
                3: GamePeriod.THIRD_QUARTER,
                4: GamePeriod.FOURTH_QUARTER,
                5: GamePeriod.OVERTIME
            }
        else:  # College
            period_map = {
                1: GamePeriod.FIRST_QUARTER,
                2: GamePeriod.SECOND_QUARTER,
                3: GamePeriod.THIRD_QUARTER,
                4: GamePeriod.FOURTH_QUARTER,
                5: GamePeriod.OVERTIME
            }
        
        return period_map.get(period, GamePeriod.FIRST_QUARTER)
    
    def _parse_clock_seconds(self, clock_display: str) -> int:
        """Parse clock display into total seconds remaining"""
        try:
            if ':' in clock_display:
                parts = clock_display.split(':')
                if len(parts) == 2:
                    minutes, seconds = parts
                    return int(minutes) * 60 + int(seconds)
            return 0
        except:
            return 0
    
    def _parse_field_position(self, competition: Dict) -> Optional[FieldPosition]:
        """Parse field position from competition data"""
        try:
            # Look for situation data
            situation = competition.get('situation', {})
            if not situation:
                return None
            
            possession_team = situation.get('possession', {}).get('abbreviation')
            yard_line = situation.get('yardLine', 50)
            down = situation.get('down', 1)
            distance = situation.get('distance', 10)
            
            return FieldPosition(
                possession_team=possession_team,
                yard_line=yard_line,
                down=down,
                distance=distance,
                is_red_zone=yard_line <= 20
            )
        except:
            return None

# Create singleton instance
espn_service = ESPNGameService()