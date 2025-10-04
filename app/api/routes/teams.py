"""Teams API endpoints for Smart Stadium."""

from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_container
from app.models.api import ApiResponse, TeamOption, TeamsResponse, TeamColors
from app.core.container import ServiceContainer

router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.get("/", response_model=ApiResponse)
async def get_teams(
    sport: Optional[str] = Query(None, description="Filter by sport (nfl, cfb, nhl, etc.)"),
    container: ServiceContainer = Depends(get_container)
) -> ApiResponse:
    """Get all available teams with optional sport filtering."""
    
    try:
        # Use new flat teams_database structure (324 teams)
        teams_database = container.config.teams_database
        teams: List[TeamOption] = []
        
        # Get teams from the "teams" key in the database
        all_teams = teams_database.get("teams", {})
        
        # Iterate through flat team structure
        for unified_key, team_data in all_teams.items():
            if not isinstance(team_data, dict):
                continue
            
            # Extract team metadata
            team_sport = team_data.get("sport", "").lower()
            
            # Apply sport filter if specified
            if sport and team_sport != sport.lower():
                continue
            
            # Extract all team fields
            team_abbr = team_data.get("abbreviation", "")
            display_name = team_data.get("display_name", "Unknown Team")
            nickname = team_data.get("nickname")
            logo_url = team_data.get("logo_url")
            espn_id = team_data.get("espn_id")
            
            # Build colors object with both official and lighting colors
            primary = team_data.get("primary_color", [128, 128, 128])
            secondary = team_data.get("secondary_color", [64, 64, 64])
            lighting_primary = team_data.get("lighting_primary_color")
            lighting_secondary = team_data.get("lighting_secondary_color")
            
            colors = TeamColors(
                primary=tuple(primary),
                secondary=tuple(secondary),
                lighting_primary=tuple(lighting_primary) if lighting_primary else None,
                lighting_secondary=tuple(lighting_secondary) if lighting_secondary else None
            )
            
            # Create team option
            team_key = f"{team_sport}:{team_abbr}"
            sport_display = team_sport.upper()
            label = f"{display_name} ({sport_display})" if not sport else display_name
            
            team_option = TeamOption(
                value=team_key,
                label=label,
                abbreviation=team_abbr,
                name=display_name,
                sport=team_sport,
                city=None,  # City info not in new database structure
                nickname=nickname,
                logo_url=logo_url,
                espn_id=espn_id,
                colors=colors
            )
            
            teams.append(team_option)
        
        # Sort teams: by sport first, then by name
        teams.sort(key=lambda t: (t.sport, t.name))
        
        response_data = TeamsResponse(
            teams=teams,
            total_count=len(teams)
        )
        
        return ApiResponse(
            success=True,
            message=f"Found {len(teams)} teams" + (f" for sport {sport}" if sport else ""),
            data=response_data.model_dump()
        )
        
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"Error fetching teams: {str(e)}"
        )