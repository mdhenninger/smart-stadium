import { useQuery } from '@tanstack/react-query';
import { fetchSystemStatus } from '../api/client';
import { queryKeys } from '../api/keys';

export const useSystemStatus = () =>
  useQuery({
    queryKey: queryKeys.status,
    queryFn: fetchSystemStatus,
    refetchInterval: 30_000,
  });
