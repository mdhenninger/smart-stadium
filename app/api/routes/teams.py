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
    use_comprehensive: bool = Query(False, description="Use comprehensive 324-team database"),
    container: ServiceContainer = Depends(get_container)
) -> ApiResponse:
    """Get all available teams with optional sport filtering."""
    
    try:
        # SAFE HYBRID APPROACH: Choose data source based on parameter
        if use_comprehensive:
            # Use new hybrid service (324 teams)
            from app.services.hybrid_teams_service import create_hybrid_teams_service
            config_dir = Path(__file__).parent.parent.parent / "config"
            src_dir = Path(__file__).parent.parent.parent / "src"
            hybrid_service = create_hybrid_teams_service(config_dir, src_dir)
            teams = hybrid_service.get_teams(sport)
            
            # Get stats for response
            stats = hybrid_service.get_team_stats()
            total_teams = stats['total_teams']
            source_info = f" (Hybrid: {stats['by_source']['current_config']} current + {stats['by_source']['comprehensive_db']} comprehensive)"
            
        else:
            # Use existing logic (54 teams) - UNCHANGED FOR SAFETY
            team_colors = container.config.team_colors
        
        teams: List[TeamOption] = []
        
        # Flatten nested team structure and create TeamOption objects
        for sport_key, sport_data in team_colors.items():
            # Skip non-team sections
            if sport_key in ["other_sports"] or not isinstance(sport_data, dict):
                continue
                
            # Map sport keys to sport codes
            sport_code = {
                "nfl_teams": "nfl",
                "college_teams": "cfb", 
                "nhl_teams": "nhl",
                "nba_teams": "nba",
                "mlb_teams": "mlb"
            }.get(sport_key)
            
            if not sport_code:
                continue
                
            # Apply sport filter if specified
            if sport and sport_code.lower() != sport.lower():
                continue
                
            # Iterate through divisions/conferences
            for division_key, division_data in sport_data.items():
                if not isinstance(division_data, dict):
                    continue
                    
                # Iterate through teams in division
                for team_abbr, colors_data in division_data.items():
                    if not isinstance(colors_data, dict) or "primary_color" not in colors_data:
                        continue
                    
                    # Extract team data
                    team_name = colors_data.get("name", f"Unknown {team_abbr}")
                    team_city = colors_data.get("city")
                    
                    # Build colors object
                    primary = colors_data.get("primary_color", [128, 128, 128])
                    secondary = colors_data.get("secondary_color", [64, 64, 64])
                    lighting_primary = colors_data.get("lighting_primary_color")
                    lighting_secondary = colors_data.get("lighting_secondary_color")
                    
                    colors = TeamColors(
                        primary=tuple(primary),
                        secondary=tuple(secondary),
                        lighting_primary=tuple(lighting_primary) if lighting_primary else None,
                        lighting_secondary=tuple(lighting_secondary) if lighting_secondary else None
                    )
                    
                    # Create team option
                    team_key = f"{sport_code}:{team_abbr}"
                    sport_display = sport_code.upper()
                    label = f"{team_name} ({sport_display})" if not sport else team_name
                    
                    team_option = TeamOption(
                        value=team_key,
                        label=label,
                        abbreviation=team_abbr,
                        name=team_name,
                        sport=sport_code,
                        city=team_city,
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