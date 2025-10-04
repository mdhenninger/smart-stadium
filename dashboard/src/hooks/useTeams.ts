import { useQuery } from '@tanstack/react-query';
import { fetchTeams } from '../api/client';
import { queryKeys } from '../api/keys';
import type { TeamOption } from '../types';

export const useTeams = (sport?: string) =>
  useQuery<TeamOption[]>({
    queryKey: [...queryKeys.teams, sport ?? 'all'],
    queryFn: () => fetchTeams(sport),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
