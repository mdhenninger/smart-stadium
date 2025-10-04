"""
Smart Stadium API - Teams Router
Endpoints for team management and settings
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query

from models import (
    ApiResponse, Team, TeamChangeRequest, TeamEvent, WebSocketMessage
)

router = APIRouter()

def get_stadium_api():
    """Dependency to get the stadium API instance"""
    from main import stadium_api
    if not stadium_api.stadium_lights:
        raise HTTPException(status_code=503, detail="Smart Stadium not initialized")
    return stadium_api

@router.get("/", response_model=ApiResponse)
async def get_all_teams(
    league: Optional[str] = Query(None, description="Filter by league (NFL, COLLEGE)"),
    search: Optional[str] = Query(None, description="Search teams by name or city"),
    limit: Optional[int] = Query(50, description="Maximum number of teams to return"),
    stadium_api = Depends(get_stadium_api)
):
    """Get all available teams with optional filtering"""
    try:
        all_teams = []
        
        # Get teams from Smart Stadium
        team_colors = stadium_api.stadium_lights.TEAM_COLORS
        
        for team_id, colors in team_colors.items():
            # Parse team ID (format: LEAGUE-CITY-TEAM)
            parts = team_id.split('-')
            if len(parts) >= 3:
                team_league = parts[0]
                team_city = parts[1]
                team_name = '-'.join(parts[2:])
                
                # Apply league filter
                if league and team_league.upper() != league.upper():
                    continue
                
                # Apply search filter
                if search:
                    search_text = search.lower()
                    if (search_text not in team_city.lower() and 
                        search_text not in team_name.lower() and 
                        search_text not in team_id.lower()):
                        continue
                
                team = Team(
                    id=team_id,
                    league=team_league,
                    city=team_city.replace('-', ' ').title(),
                    name=team_name.replace('-', ' ').title(),
                    full_name=f"{team_city.replace('-', ' ').title()} {team_name.replace('-', ' ').title()}",
                    primary_color=colors['primary'],
                    secondary_color=colors['secondary']
                )
                all_teams.append(team)
        
        # Sort teams by league then by city
        all_teams.sort(key=lambda t: (t.league, t.city, t.name))
        
        # Apply limit
        if limit:
            all_teams = all_teams[:limit]
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(all_teams)} teams",
            data={
                "teams": [team.model_dump() for team in all_teams],
                "total_count": len(all_teams),
                "filters_applied": {"league": league, "search": search, "limit": limit}
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")

@router.get("/current", response_model=ApiResponse)
async def get_current_team(stadium_api = Depends(get_stadium_api)):
    """Get the currently selected team"""
    try:
        current_team_info = stadium_api.stadium_lights.get_current_team_info()
        
        return ApiResponse(
            success=True,
            message="Current team information",
            data=current_team_info.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current team: {str(e)}")

@router.put("/current", response_model=ApiResponse)
async def set_current_team(request: TeamChangeRequest, stadium_api = Depends(get_stadium_api)):
    """Change the current team"""
    try:
        # Get old team for event broadcasting
        old_team_info = stadium_api.stadium_lights.get_current_team_info()
        old_team_id = old_team_info.id if old_team_info else None
        
        # Validate team exists
        if request.team_id not in stadium_api.stadium_lights.TEAM_COLORS:
            raise HTTPException(status_code=404, detail=f"Team {request.team_id} not found")
        
        # Set the new team
        result = stadium_api.stadium_lights.set_team(request.team_id)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to set team")
        
        # Get new team info
        new_team_info = stadium_api.stadium_lights.get_current_team_info()
        
        # Broadcast team change event
        team_event = TeamEvent(
            event_type="team_changed",
            old_team_id=old_team_id,
            new_team_id=request.team_id,
            team_name=new_team_info.full_name,
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="team_event",
            data=team_event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        await stadium_api.broadcast_to_websockets(message)
        
        return ApiResponse(
            success=True,
            message=f"Team changed to {new_team_info.full_name}",
            data={
                "previous_team": old_team_id,
                "new_team": new_team_info.model_dump(),
                "temporary": request.temporary
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change team: {str(e)}")

@router.get("/{team_id}", response_model=ApiResponse)
async def get_team(team_id: str, stadium_api = Depends(get_stadium_api)):
    """Get specific team information"""
    try:
        if team_id not in stadium_api.stadium_lights.TEAM_COLORS:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        colors = stadium_api.stadium_lights.TEAM_COLORS[team_id]
        
        # Parse team ID
        parts = team_id.split('-')
        if len(parts) >= 3:
            team_league = parts[0]
            team_city = parts[1]
            team_name = '-'.join(parts[2:])
        else:
            raise HTTPException(status_code=400, detail=f"Invalid team ID format: {team_id}")
        
        team = Team(
            id=team_id,
            league=team_league,
            city=team_city.replace('-', ' ').title(),
            name=team_name.replace('-', ' ').title(),
            full_name=f"{team_city.replace('-', ' ').title()} {team_name.replace('-', ' ').title()}",
            primary_color=colors['primary'],
            secondary_color=colors['secondary']
        )
        
        return ApiResponse(
            success=True,
            message=f"Team {team_id} information",
            data=team.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team: {str(e)}")

@router.get("/leagues/list", response_model=ApiResponse)
async def get_leagues(stadium_api = Depends(get_stadium_api)):
    """Get all available leagues"""
    try:
        leagues = set()
        
        for team_id in stadium_api.stadium_lights.TEAM_COLORS.keys():
            parts = team_id.split('-')
            if len(parts) >= 3:
                leagues.add(parts[0])
        
        leagues_list = sorted(list(leagues))
        
        # Count teams per league
        league_counts = {}
        for league in leagues_list:
            count = sum(1 for team_id in stadium_api.stadium_lights.TEAM_COLORS.keys() 
                       if team_id.startswith(f"{league}-"))
            league_counts[league] = count
        
        return ApiResponse(
            success=True,
            message=f"Found {len(leagues_list)} leagues",
            data={
                "leagues": leagues_list,
                "league_counts": league_counts,
                "total_teams": len(stadium_api.stadium_lights.TEAM_COLORS)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leagues: {str(e)}")

@router.get("/search/{query}", response_model=ApiResponse)
async def search_teams(
    query: str,
    limit: Optional[int] = Query(20, description="Maximum number of results"),
    stadium_api = Depends(get_stadium_api)
):
    """Search teams by name, city, or league"""
    try:
        query_lower = query.lower()
        matching_teams = []
        
        for team_id, colors in stadium_api.stadium_lights.TEAM_COLORS.items():
            # Parse team ID
            parts = team_id.split('-')
            if len(parts) >= 3:
                team_league = parts[0]
                team_city = parts[1]
                team_name = '-'.join(parts[2:])
                
                # Check if query matches any part
                if (query_lower in team_city.lower() or 
                    query_lower in team_name.lower() or 
                    query_lower in team_league.lower() or
                    query_lower in team_id.lower()):
                    
                    team = Team(
                        id=team_id,
                        league=team_league,
                        city=team_city.replace('-', ' ').title(),
                        name=team_name.replace('-', ' ').title(),
                        full_name=f"{team_city.replace('-', ' ').title()} {team_name.replace('-', ' ').title()}",
                        primary_color=colors['primary'],
                        secondary_color=colors['secondary']
                    )
                    matching_teams.append(team)
        
        # Sort by relevance (exact matches first)
        def relevance_score(team):
            score = 0
            if query_lower == team.city.lower(): score += 100
            if query_lower == team.name.lower(): score += 100
            if query_lower in team.city.lower(): score += 50
            if query_lower in team.name.lower(): score += 50
            if query_lower == team.league.lower(): score += 25
            return score
        
        matching_teams.sort(key=relevance_score, reverse=True)
        
        # Apply limit
        if limit:
            matching_teams = matching_teams[:limit]
        
        return ApiResponse(
            success=True,
            message=f"Found {len(matching_teams)} teams matching '{query}'",
            data={
                "query": query,
                "teams": [team.model_dump() for team in matching_teams],
                "result_count": len(matching_teams)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Team search failed: {str(e)}")

@router.post("/{team_id}/test-colors", response_model=ApiResponse)
async def test_team_colors(team_id: str, stadium_api = Depends(get_stadium_api)):
    """Test a team's colors by flashing them briefly"""
    try:
        if team_id not in stadium_api.stadium_lights.TEAM_COLORS:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        # Temporarily set team and flash colors
        original_team = stadium_api.stadium_lights.current_team
        stadium_api.stadium_lights.set_team(team_id)
        
        # Quick color test (2 flashes)
        colors = stadium_api.stadium_lights.TEAM_COLORS[team_id]
        await stadium_api.stadium_lights.flash_all_color(colors['primary'], duration=0.5)
        await stadium_api.stadium_lights.flash_all_color(colors['secondary'], duration=0.5)
        
        # Restore original team
        if original_team:
            stadium_api.stadium_lights.set_team(original_team)
        
        # Return to default lighting
        await stadium_api.stadium_lights.set_all_default_lighting()
        
        team_info = stadium_api.stadium_lights.get_team_info(team_id)
        
        return ApiResponse(
            success=True,
            message=f"Color test completed for {team_info['full_name']}",
            data={
                "team_id": team_id,
                "colors_tested": {
                    "primary": colors['primary'],
                    "secondary": colors['secondary']
                },
                "test_timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Color test failed: {str(e)}")