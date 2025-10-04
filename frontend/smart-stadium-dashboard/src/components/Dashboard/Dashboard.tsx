import React, { useState, useEffect } from 'react';
import { Game, CelebrationStatus } from '../../types';
import webSocketService from '../../services/websocket';
import FieldPositionVisualization from './FieldPositionVisualization';
import CelebrationControls from './CelebrationControls';
import DeviceStatusGrid from './DeviceStatusGrid';
import Card from '../UI/Card';
import Badge from '../UI/Badge';
import TeamLogo from '../UI/TeamLogo';
import LoadingSpinner from '../UI/LoadingSpinner';
import apiService from '../../services/api';

interface DashboardProps {
  gameId: string;
}

const Dashboard: React.FC<DashboardProps> = ({ gameId }) => {
  const [game, setGame] = useState<Game | null>(null);
  const [activeCelebrations, setActiveCelebrations] = useState<CelebrationStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  // Monitor WebSocket connection status
  useEffect(() => {
    const checkConnection = () => {
      setConnectionStatus(webSocketService.connectionState);
    };
    
    // Check connection status every 2 seconds
    const interval = setInterval(checkConnection, 2000);
    checkConnection(); // Initial check
    
    return () => clearInterval(interval);
  }, []);

  // Load initial game data
  useEffect(() => {
    loadGameData();
  }, [gameId]);

  // WebSocket event handlers
  useEffect(() => {
    const handleGameUpdate = (event: any) => {
      if (event.type === 'game_update' && event.data?.game) {
        setGame(event.data.game);
      }
    };

    const handleScoreUpdate = (event: any) => {
      if (event.type === 'score_update' && event.data?.game_id === gameId) {
        setGame(prev => prev ? {
          ...prev,
          scores: {
            home: event.data.home_score,
            away: event.data.away_score
          }
        } : null);
      }
    };

    const handleCelebrationUpdate = (event: any) => {
      if (event.type === 'celebration_update' && event.data) {
        const celebrationData = event.data as CelebrationStatus;
        setActiveCelebrations(prev => {
          const existing = prev.find(c => c.id === celebrationData.id);
          if (existing) {
            return prev.map(c => c.id === celebrationData.id ? celebrationData : c);
          } else {
            return [...prev, celebrationData];
          }
        });
      }
    };

    const handleCelebrationComplete = (event: any) => {
      if (event.type === 'celebration_complete' && event.data?.celebration_id) {
        setActiveCelebrations(prev => 
          prev.filter(c => c.id !== event.data.celebration_id)
        );
      }
    };

    // Subscribe to events with proper event handlers
    webSocketService.on('game_update', handleGameUpdate);
    webSocketService.on('score_update', handleScoreUpdate);
    webSocketService.on('celebration_update', handleCelebrationUpdate);
    webSocketService.on('celebration_complete', handleCelebrationComplete);

    // Subscribe to specific game updates
    webSocketService.subscribeToGame(gameId);
    webSocketService.subscribeToCelebrations();

    return () => {
      webSocketService.off('game_update', handleGameUpdate);
      webSocketService.off('score_update', handleScoreUpdate);
      webSocketService.off('celebration_update', handleCelebrationUpdate);
      webSocketService.off('celebration_complete', handleCelebrationComplete);
      webSocketService.unsubscribeFromGame(gameId);
    };
  }, [gameId]);

  const loadGameData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load game details
      const gameData = await apiService.getGame(gameId);
      setGame(gameData);
      
      // Load active celebrations
      const celebrations = await apiService.getActiveCelebrations();
      setActiveCelebrations(celebrations);
      
    } catch (err) {
      setError(apiService.handleError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCelebrationTriggered = (celebration: CelebrationStatus) => {
    setActiveCelebrations(prev => [...prev, celebration]);
  };

  const getConnectionBadgeProps = () => {
    switch (connectionStatus) {
      case 'connected':
        return { variant: 'success' as const, text: 'Connected', icon: '🟯' };
      case 'connecting':
        return { variant: 'warning' as const, text: 'Connecting', icon: '🔄' };
      case 'disconnected':
        return { variant: 'danger' as const, text: 'Disconnected', icon: '⚠️' };
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-96">
            <LoadingSpinner size="large" />
            <span className="ml-3 text-white">Loading game dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="max-w-lg mx-auto">
            <div className="text-center space-y-4">
              <div className="text-6xl">⚠️</div>
              <h2 className="text-xl font-semibold text-white">Dashboard Error</h2>
              <p className="text-gray-400">{error}</p>
              <button 
                onClick={loadGameData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (!game) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="max-w-lg mx-auto">
            <div className="text-center space-y-4">
              <div className="text-6xl">🔍</div>
              <h2 className="text-xl font-semibold text-white">Game Not Found</h2>
              <p className="text-gray-400">The requested game could not be loaded.</p>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  const connectionBadge = getConnectionBadgeProps();

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Dashboard Header */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Game Title */}
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">
                🏈 Live Game Dashboard
              </h1>
              
              <div className="flex items-center space-x-3">
                <TeamLogo team={game.away_team} size="sm" />
                <span className="text-white font-medium">
                  {game.away_team.abbreviation}
                </span>
                <span className="text-gray-400">@</span>
                <span className="text-white font-medium">
                  {game.home_team.abbreviation}
                </span>
                <TeamLogo team={game.home_team} size="sm" />
              </div>
            </div>
            
            {/* Status Indicators */}
            <div className="flex items-center space-x-3">
              <Badge 
                variant={connectionBadge.variant} 
                size="sm"
              >
                {connectionBadge.icon} {connectionBadge.text}
              </Badge>
              
              <Badge 
                variant={game.status === 'in_progress' ? 'success' : 'default'}
                size="sm"
              >
                {game.status === 'in_progress' ? '🔴 LIVE' : game.status.toUpperCase()}
              </Badge>
              
              <Badge variant="info" size="sm">
                {activeCelebrations.filter(c => c.status === 'running').length} Active
              </Badge>
            </div>
          </div>
          
          {/* Game Clock */}
          {game.status === 'in_progress' && (
            <div className="mt-2 text-center">
              <div className="text-3xl font-bold text-white">
                {game.scores.away} - {game.scores.home}
              </div>
              <div className="text-sm text-gray-400">
                Q{game.current_period} • {game.time_remaining}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Main Content - Field Visualization */}
          <div className="xl:col-span-2 space-y-6">
            <FieldPositionVisualization 
              game={game}
              className="w-full"
            />
            
            {/* Celebration Controls */}
            <CelebrationControls
              game={game}
              activeCelebrations={activeCelebrations}
              onCelebrationTriggered={handleCelebrationTriggered}
              className="w-full"
            />
          </div>
          
          {/* Sidebar - Device Status */}
          <div className="space-y-6">
            <DeviceStatusGrid className="w-full" />
            
            {/* Quick Stats */}
            <Card>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">
                  📈 Game Stats
                </h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-700 rounded-lg">
                    <div className="text-xl font-bold text-blue-400">
                      {game.scores.away}
                    </div>
                    <div className="text-xs text-gray-400">
                      {game.away_team.abbreviation}
                    </div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-700 rounded-lg">
                    <div className="text-xl font-bold text-blue-400">
                      {game.scores.home}
                    </div>
                    <div className="text-xs text-gray-400">
                      {game.home_team.abbreviation}
                    </div>
                  </div>
                </div>
                
                {game.status === 'in_progress' && (
                  <>
                    <div className="border-t border-gray-700 pt-3">
                      <div className="text-sm text-gray-400 mb-2">Current Period</div>
                      <div className="text-lg font-medium text-white">
                        Quarter {game.current_period}
                      </div>
                    </div>
                    
                    <div className="border-t border-gray-700 pt-3">
                      <div className="text-sm text-gray-400 mb-2">Time Remaining</div>
                      <div className="text-lg font-medium text-white">
                        {game.time_remaining}
                      </div>
                    </div>
                  </>
                )}
                
                <div className="border-t border-gray-700 pt-3">
                  <div className="text-sm text-gray-400 mb-2">Game Status</div>
                  <Badge 
                    variant={game.status === 'in_progress' ? 'success' : 'default'}
                    size="sm"
                  >
                    {game.status === 'in_progress' ? 'Live' : game.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;