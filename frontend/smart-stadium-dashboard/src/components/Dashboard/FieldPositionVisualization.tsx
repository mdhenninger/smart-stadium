import React from 'react';
import { clsx } from 'clsx';
import { Game, FieldZone } from '../../types';
import { getTeamColors } from '../../utils';
import TeamLogo from '../UI/TeamLogo';
import Badge from '../UI/Badge';

interface FieldPositionVisualizationProps {
  game: Game;
  className?: string;
}

const FieldPositionVisualization: React.FC<FieldPositionVisualizationProps> = ({
  game,
  className,
}) => {
  // Create field zones (20 zones of 5 yards each)
  const createFieldZones = (): FieldZone[] => {
    const zones: FieldZone[] = [];
    
    // Away team endzone
    zones.push({
      id: 'away-endzone',
      start_yard: 0,
      end_yard: 0,
      team: 'away',
      is_endzone: true,
      is_active: false
    });
    
    // Field zones (5-yard increments)
    for (let i = 0; i < 20; i++) {
      const startYard = i * 5;
      const endYard = (i + 1) * 5;
      // const yardLine = i < 10 ? (50 - startYard) : (endYard - 50);
      
      zones.push({
        id: `zone-${i}`,
        start_yard: startYard,
        end_yard: endYard,
        team: 'neutral',
        is_endzone: false,
        is_active: false
      });
    }
    
    // Home team endzone
    zones.push({
      id: 'home-endzone',
      start_yard: 100,
      end_yard: 100,
      team: 'home',
      is_endzone: true,
      is_active: false
    });
    
    return zones;
  };
  
  const zones = createFieldZones();
  const awayColors = getTeamColors(game.away_team);
  const homeColors = getTeamColors(game.home_team);
  
  // Determine current field position
  const getCurrentPosition = () => {
    if (!game.field_position) return null;
    
    const { yard_line, team } = game.field_position;
    
    // Convert to field position (0-100)
    let fieldPosition: number;
    if (team === game.home_team.abbreviation) {
      fieldPosition = yard_line;
    } else {
      fieldPosition = 100 - yard_line;
    }
    
    return {
      position: fieldPosition,
      zone: Math.floor(fieldPosition / 5),
      team: team
    };
  };
  
  const currentPosition = getCurrentPosition();
  
  return (
    <div className={clsx('bg-gray-800 rounded-lg p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white flex items-center">
          🏈 Field Position
        </h2>
        {game.status === 'in_progress' && (
          <Badge variant="success" size="sm">
            🔴 LIVE
          </Badge>
        )}
      </div>
      
      {/* Team Headers */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <TeamLogo team={game.away_team} size="sm" />
          <div className="text-sm">
            <div className="font-medium text-white">{game.away_team.city}</div>
            <div className="text-gray-400">Away</div>
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-white">
            {game.scores.away} - {game.scores.home}
          </div>
          {game.status === 'in_progress' && (
            <div className="text-sm text-gray-400">
              Q{game.current_period} • {game.time_remaining}
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="text-sm text-right">
            <div className="font-medium text-white">{game.home_team.city}</div>
            <div className="text-gray-400">Home</div>
          </div>
          <TeamLogo team={game.home_team} size="sm" />
        </div>
      </div>
      
      {/* Football Field */}
      <div className="relative">
        {/* Field Background */}
        <div className="bg-green-700 rounded-lg p-4 relative overflow-hidden">
          {/* Yard Lines */}
          <div className="flex h-16 relative">
            {/* Away Endzone */}
            <div 
              className="flex-shrink-0 w-8 h-full rounded-l-md border-r-2 border-white flex items-center justify-center"
              style={{ backgroundColor: awayColors.primary }}
            >
              <span className="text-white text-xs font-bold transform -rotate-90">
                {game.away_team.abbreviation}
              </span>
            </div>
            
            {/* Field Zones */}
            {zones.slice(1, -1).map((zone, index) => {
              const yardNumber = index < 10 ? (50 - (index * 5)) : ((index - 9) * 5);
              const isGoalLine = yardNumber === 10 || yardNumber === 10;
              const isMidfield = yardNumber === 50;
              const isCurrentPosition = currentPosition?.zone === index;
              
              return (
                <div
                  key={zone.id}
                  className={clsx(
                    'flex-1 h-full border-r border-white/30 relative flex items-center justify-center transition-all duration-300',
                    {
                      'bg-yellow-400/20 shadow-lg': isCurrentPosition,
                      'bg-red-500/20': isGoalLine,
                      'bg-white/10': isMidfield,
                    }
                  )}
                >
                  {/* Yard Number */}
                  {(index % 2 === 0 || isMidfield) && (
                    <span className="text-white text-xs font-bold">
                      {yardNumber}
                    </span>
                  )}
                  
                  {/* Goal Line Markers */}
                  {isGoalLine && (
                    <div className="absolute inset-y-0 left-0 w-1 bg-red-500" />
                  )}
                  
                  {/* Midfield Marker */}
                  {isMidfield && (
                    <div className="absolute inset-y-0 left-0 w-1 bg-white" />
                  )}
                </div>
              );
            })}
            
            {/* Home Endzone */}
            <div 
              className="flex-shrink-0 w-8 h-full rounded-r-md border-l-2 border-white flex items-center justify-center"
              style={{ backgroundColor: homeColors.primary }}
            >
              <span className="text-white text-xs font-bold transform -rotate-90">
                {game.home_team.abbreviation}
              </span>
            </div>
          </div>
          
          {/* Ball Position Indicator */}
          {currentPosition && (
            <div 
              className="absolute top-2 transform -translate-x-1/2 transition-all duration-500"
              style={{ 
                left: `${(currentPosition.position / 100) * 100}%`,
                marginLeft: '32px', // Account for endzone width
                width: `calc(100% - 64px)` // Account for both endzones
              }}
            >
              <div className="bg-yellow-400 text-black px-2 py-1 rounded-full text-xs font-bold shadow-lg">
                🏈 {game.field_position?.yard_line} YD
              </div>
            </div>
          )}
        </div>
        
        {/* Game Situation */}
        {game.status === 'in_progress' && game.field_position && (
          <div className="mt-4 p-3 bg-gray-700 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-4">
                <span className="text-gray-400">Possession:</span>
                <span className="font-medium text-white">
                  {game.field_position.team}
                </span>
              </div>
              
              {game.field_position.down && game.field_position.distance && (
                <div className="flex items-center space-x-4">
                  <span className="text-gray-400">Down & Distance:</span>
                  <span className="font-medium text-white">
                    {game.field_position.down} & {game.field_position.distance}
                  </span>
                </div>
              )}
              
              <div className="flex items-center space-x-4">
                <span className="text-gray-400">Field Position:</span>
                <span className="font-medium text-white">
                  {game.field_position.team} {game.field_position.yard_line}
                </span>
              </div>
            </div>
          </div>
        )}
        
        {/* Last Play */}
        {game.last_play && (
          <div className="mt-3 p-3 bg-blue-900/30 rounded-lg">
            <div className="text-sm">
              <span className="text-blue-400 font-medium">Last Play: </span>
              <span className="text-gray-300">{game.last_play}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FieldPositionVisualization;