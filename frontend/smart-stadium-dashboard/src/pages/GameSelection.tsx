import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Game } from '../types';
import apiService from '../services/api';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import TeamLogo from '../components/UI/TeamLogo';
import { formatDateTime, formatGameStatus, storage } from '../utils';

const GameSelection: React.FC = () => {
  const navigate = useNavigate();
  const [games, setGames] = useState<Game[]>([]);
  const [liveGames, setLiveGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'live' | 'today'>('all');
  const selectedSport = storage.get('selectedSport', 'nfl');

  useEffect(() => {
    const loadGames = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Load today's games and live games
        const [todaysGames, currentLiveGames] = await Promise.all([
          apiService.getTodaysGames(),
          apiService.getLiveGames()
        ]);
        
        setGames(todaysGames);
        setLiveGames(currentLiveGames);
      } catch (err) {
        setError(apiService.handleError(err));
      } finally {
        setLoading(false);
      }
    };

    loadGames();
    
    // Refresh games every 30 seconds
    const interval = setInterval(loadGames, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleGameSelect = (gameId: string) => {
    navigate(`/dashboard/${gameId}`);
  };

  const getFilteredGames = () => {
    switch (filter) {
      case 'live':
        return liveGames;
      case 'today':
        return games.filter(game => {
          const gameDate = new Date(game.start_time);
          const today = new Date();
          return gameDate.toDateString() === today.toDateString();
        });
      default:
        return games;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'in_progress':
        return 'success';
      case 'completed':
        return 'default';
      case 'postponed':
        return 'warning';
      default:
        return 'info';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" message="Loading games..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">❌</div>
        <h2 className="text-xl font-semibold text-red-400 mb-4">{error}</h2>
        <Button onClick={() => window.location.reload()} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  const filteredGames = getFilteredGames();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Select a Game</h1>
        <p className="text-xl text-gray-400 mb-4">
          Choose a {selectedSport.toUpperCase()} game to monitor live
        </p>
        
        {/* Game Stats */}
        <div className="flex justify-center space-x-6 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{games.length}</div>
            <div className="text-sm text-gray-500">Today's Games</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{liveGames.length}</div>
            <div className="text-sm text-gray-500">Live Now</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {games.filter(g => g.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-500">Completed</div>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex justify-center space-x-2 mb-8">
        <Button
          variant={filter === 'all' ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => setFilter('all')}
        >
          All Games ({games.length})
        </Button>
        <Button
          variant={filter === 'live' ? 'success' : 'ghost'}
          size="sm"
          onClick={() => setFilter('live')}
          leftIcon={liveGames.length > 0 ? '🔴' : undefined}
        >
          Live ({liveGames.length})
        </Button>
        <Button
          variant={filter === 'today' ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => setFilter('today')}
        >
          Today ({games.filter(g => {
            const gameDate = new Date(g.start_time);
            const today = new Date();
            return gameDate.toDateString() === today.toDateString();
          }).length})
        </Button>
      </div>

      {/* Games Grid */}
      {filteredGames.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📅</div>
          <h2 className="text-xl font-semibold text-white mb-2">
            {filter === 'live' ? 'No Live Games' : 'No Games Found'}
          </h2>
          <p className="text-gray-400 mb-6">
            {filter === 'live' 
              ? 'Check back during game time for live games!' 
              : 'Check back during the season for scheduled games!'
            }
          </p>
          <Button onClick={() => setFilter('all')} variant="secondary">
            View All Games
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {filteredGames.map((game) => {
            const dateTime = formatDateTime(game.start_time);
            
            return (
              <Card
                key={game.id}
                clickable
                onClick={() => handleGameSelect(game.id)}
                className="hover:border-blue-500 transition-all duration-200"
              >
                {/* Game Header */}
                <div className="flex items-center justify-between mb-4">
                  <Badge variant={getStatusBadgeVariant(game.status)} size="sm">
                    {formatGameStatus(game.status)}
                  </Badge>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">{dateTime.date}</div>
                    <div className="text-xs text-gray-500">{dateTime.time}</div>
                  </div>
                </div>
                
                {/* Teams */}
                <div className="space-y-4 mb-4">
                  {/* Away Team */}
                  <div className="flex items-center justify-between">
                    <TeamLogo team={game.away_team} size="md" showName />
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">
                        {game.scores.away}
                      </div>
                      {game.status === 'in_progress' && (
                        <div className="text-xs text-gray-400">Away</div>
                      )}
                    </div>
                  </div>
                  
                  {/* Home Team */}
                  <div className="flex items-center justify-between">
                    <TeamLogo team={game.home_team} size="md" showName />
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">
                        {game.scores.home}
                      </div>
                      {game.status === 'in_progress' && (
                        <div className="text-xs text-gray-400">Home</div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Game Info */}
                <div className="border-t border-gray-700 pt-3">
                  <div className="text-sm text-gray-400 mb-2">
                    📍 {game.venue}
                  </div>
                  
                  {game.status === 'in_progress' && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-green-400 font-medium">
                        🔴 Q{game.current_period} - {game.time_remaining}
                      </span>
                      {game.field_position && (
                        <span className="text-blue-400">
                          {game.field_position.team} {game.field_position.yard_line}
                        </span>
                      )}
                    </div>
                  )}
                  
                  {game.status === 'scheduled' && (
                    <div className="text-sm text-blue-400">
                      Starts {dateTime.relative}
                    </div>
                  )}
                  
                  {game.last_play && (
                    <div className="text-xs text-gray-500 mt-2 truncate">
                      Last: {game.last_play}
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => navigate('/sport')}
          leftIcon={<span>←</span>}
        >
          Back to Sports
        </Button>
        
        <Button
          variant="ghost"
          size="lg"
          onClick={() => window.location.reload()}
          leftIcon={<span>🔄</span>}
        >
          Refresh Games
        </Button>
      </div>
    </div>
  );
};

export default GameSelection;