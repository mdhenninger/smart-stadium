import { useQuery } from '@tanstack/react-query';
import { fetchGames } from '../api/client';
import { queryKeys } from '../api/keys';
import type { SportCode } from '../types';

export const useGames = (sport: SportCode) =>
  useQuery({
    queryKey: queryKeys.games(sport),
    queryFn: () => fetchGames(sport),
    refetchInterval: 45_000,
    staleTime: 30_000,
  });
