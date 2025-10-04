import React, { useState } from 'react';
import { Game, CelebrationRequest, CelebrationStatus } from '../../types';
import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';
import TeamLogo from '../UI/TeamLogo';
import apiService from '../../services/api';

interface CelebrationControlsProps {
  game: Game;
  activeCelebrations: CelebrationStatus[];
  onCelebrationTriggered: (celebration: CelebrationStatus) => void;
  className?: string;
}

interface CelebrationType {
  id: string;
  name: string;
  icon: string;
  description: string;
  intensity: 'low' | 'medium' | 'high';
  category: 'scoring' | 'defensive' | 'special';
}

const CelebrationControls: React.FC<CelebrationControlsProps> = ({
  game,
  activeCelebrations,
  onCelebrationTriggered,
  className,
}) => {
  const [selectedTeam, setSelectedTeam] = useState<'home' | 'away'>('home');
  const [isTriggering, setIsTriggering] = useState<string | null>(null);
  const [lastTriggered, setLastTriggered] = useState<string | null>(null);

  const celebrationTypes: CelebrationType[] = [
    {
      id: 'touchdown',
      name: 'Touchdown',
      icon: '🏈',
      description: '6 points scored',
      intensity: 'high',
      category: 'scoring'
    },
    {
      id: 'field_goal',
      name: 'Field Goal',
      icon: '🥅',
      description: '3 points scored',
      intensity: 'medium',
      category: 'scoring'
    },
    {
      id: 'safety',
      name: 'Safety',
      icon: '🛡️',
      description: '2 points scored',
      intensity: 'medium',
      category: 'scoring'
    },
    {
      id: 'interception',
      name: 'Interception',
      icon: '🙌',
      description: 'Defensive turnover',
      intensity: 'medium',
      category: 'defensive'
    },
    {
      id: 'fumble_recovery',
      name: 'Fumble Recovery',
      icon: '🤲',
      description: 'Defensive turnover',
      intensity: 'medium',
      category: 'defensive'
    },
    {
      id: 'sack',
      name: 'Sack',
      icon: '💥',
      description: 'QB tackled for loss',
      intensity: 'low',
      category: 'defensive'
    },
    {
      id: 'big_play',
      name: 'Big Play',
      icon: '⚡',
      description: '20+ yard gain',
      intensity: 'medium',
      category: 'special'
    },
    {
      id: 'game_winner',
      name: 'Game Winner',
      icon: '🎆',
      description: 'Game-winning score',
      intensity: 'high',
      category: 'special'
    }
  ];

  const getCurrentTeam = () => {
    return selectedTeam === 'home' ? game.home_team : game.away_team;
  };

  const handleCelebrationTrigger = async (celebrationType: CelebrationType) => {
    const team = getCurrentTeam();
    setIsTriggering(celebrationType.id);
    
    try {
      const request: CelebrationRequest = {
        type: celebrationType.id as any,
        team_id: team.id,
        intensity: celebrationType.intensity,
      };
      
      const celebration = await apiService.triggerCelebration(request);
      onCelebrationTriggered(celebration);
      setLastTriggered(celebrationType.id);
      
      // Clear the "last triggered" indicator after 3 seconds
      setTimeout(() => setLastTriggered(null), 3000);
    } catch (error) {
      console.error('Failed to trigger celebration:', error);
    } finally {
      setIsTriggering(null);
    }
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'scoring': return '🎯';
      case 'defensive': return '🛡️';
      case 'special': return '⭐';
      default: return '🎉';
    }
  };

  const isActiveCelebration = (type: string) => {
    return activeCelebrations.some(c => 
      c.type === type && 
      c.status === 'running'
    );
  };

  return (
    <Card className={className}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white flex items-center">
            🎉 Celebration Controls
          </h2>
          <Badge variant="info" size="sm">
            {activeCelebrations.filter(c => c.status === 'running').length} Active
          </Badge>
        </div>

        {/* Team Selection */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-300">Select Team</h3>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setSelectedTeam('away')}
              className={`p-3 rounded-lg border transition-all duration-200 ${
                selectedTeam === 'away'
                  ? 'border-blue-500 bg-blue-600/20'
                  : 'border-gray-600 bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <div className="flex items-center space-x-3">
                <TeamLogo team={game.away_team} size="sm" />
                <div className="text-left">
                  <div className="font-medium text-white text-sm">
                    {game.away_team.city}
                  </div>
                  <div className="text-xs text-gray-400">Away</div>
                </div>
              </div>
            </button>
            
            <button
              onClick={() => setSelectedTeam('home')}
              className={`p-3 rounded-lg border transition-all duration-200 ${
                selectedTeam === 'home'
                  ? 'border-blue-500 bg-blue-600/20'
                  : 'border-gray-600 bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <div className="flex items-center space-x-3">
                <TeamLogo team={game.home_team} size="sm" />
                <div className="text-left">
                  <div className="font-medium text-white text-sm">
                    {game.home_team.city}
                  </div>
                  <div className="text-xs text-gray-400">Home</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Celebration Categories */}
        {['scoring', 'defensive', 'special'].map((category) => {
          const categoryTypes = celebrationTypes.filter(t => t.category === category);
          
          return (
            <div key={category} className="space-y-3">
              <h3 className="text-sm font-medium text-gray-300 flex items-center">
                {getCategoryIcon(category)}
                <span className="ml-2 capitalize">{category} Celebrations</span>
              </h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {categoryTypes.map((type) => {
                  const isActive = isActiveCelebration(type.id);
                  const isLoading = isTriggering === type.id;
                  const wasLastTriggered = lastTriggered === type.id;
                  
                  return (
                    <button
                      key={type.id}
                      onClick={() => handleCelebrationTrigger(type)}
                      disabled={isLoading || isActive}
                      className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                        isActive
                          ? 'border-green-500 bg-green-600/20'
                          : wasLastTriggered
                          ? 'border-blue-500 bg-blue-600/20'
                          : 'border-gray-600 bg-gray-700 hover:bg-gray-600 hover:border-gray-500'
                      } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-lg">{type.icon}</span>
                            <span className="font-medium text-white text-sm">
                              {type.name}
                            </span>
                            {isActive && (
                              <Badge variant="success" size="sm">ACTIVE</Badge>
                            )}
                            {wasLastTriggered && (
                              <Badge variant="info" size="sm">TRIGGERED</Badge>
                            )}
                          </div>
                          <p className="text-xs text-gray-400 mb-2">
                            {type.description}
                          </p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">Intensity:</span>
                            <span className={`text-xs font-medium ${getIntensityColor(type.intensity)}`}>
                              {type.intensity.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        
                        {isLoading && (
                          <div className="ml-2">
                            <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                          </div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Active Celebrations List */}
        {activeCelebrations.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-300">Active Celebrations</h3>
            <div className="space-y-2">
              {activeCelebrations.map((celebration) => (
                <div 
                  key={celebration.id} 
                  className="p-3 bg-gray-700 rounded-lg flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-white text-sm font-medium">
                      {celebration.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <Badge variant="success" size="sm">
                      {celebration.status.toUpperCase()}
                    </Badge>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-xs text-gray-400">
                      Progress: {celebration.progress}%
                    </div>
                    {celebration.estimated_end && (
                      <div className="text-xs text-gray-500">
                        Ends: {new Date(celebration.estimated_end).toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="pt-4 border-t border-gray-700">
          <div className="grid grid-cols-2 gap-3">
            <Button variant="secondary" size="sm" fullWidth>
              🔄 Refresh Status
            </Button>
            <Button variant="danger" size="sm" fullWidth>
              🛑 Stop All
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default CelebrationControls;