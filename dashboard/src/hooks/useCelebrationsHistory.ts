import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchCelebrationHistory, triggerCelebration } from '../api/client';
import { queryKeys } from '../api/keys';

export const useCelebrationHistory = (limit = 25) =>
  useQuery({
    queryKey: [...queryKeys.celebrations, limit],
    queryFn: () => fetchCelebrationHistory(limit),
    refetchInterval: 60_000,
  });

export const useTriggerCelebration = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: triggerCelebration,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: queryKeys.celebrations });
    },
  });
};
