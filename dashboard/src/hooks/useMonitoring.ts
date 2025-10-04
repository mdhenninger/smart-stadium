import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { addMonitoring, fetchMonitoredGames, removeMonitoring, type MonitoredGame, type MonitoringRequest } from '../api/client';

export function useMonitoring() {
  const queryClient = useQueryClient();
  const [isAdding, setIsAdding] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  const { data: monitoredGames = [], isLoading, isError, refetch } = useQuery<MonitoredGame[]>({
    queryKey: ['monitoring'],
    queryFn: fetchMonitoredGames,
    refetchInterval: 10_000, // Refetch every 10 seconds for updates
  });

  const addGame = async (request: MonitoringRequest): Promise<void> => {
    setIsAdding(true);
    try {
      await addMonitoring(request);
      // Invalidate queries to refetch
      await queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    } finally {
      setIsAdding(false);
    }
  };

  const removeGame = async (gameId: string): Promise<void> => {
    setIsRemoving(true);
    try {
      await removeMonitoring(gameId);
      // Invalidate queries to refetch
      await queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    } finally {
      setIsRemoving(false);
    }
  };

  const isGameMonitored = (gameId: string): boolean => {
    return monitoredGames.some((mg: MonitoredGame) => mg.game_id === gameId);
  };

  const getMonitoredTeams = (gameId: string): string[] => {
    const game = monitoredGames.find((mg: MonitoredGame) => mg.game_id === gameId);
    return game?.monitored_teams ?? [];
  };

  return {
    monitoredGames,
    isLoading,
    isError,
    isAdding,
    isRemoving,
    addGame,
    removeGame,
    isGameMonitored,
    getMonitoredTeams,
    refetch,
  };
}
