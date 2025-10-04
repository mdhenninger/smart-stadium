import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  fetchDevices,
  runDeviceTest,
  setDefaultLighting,
  toggleDevice,
} from '../api/client';
import { queryKeys } from '../api/keys';

export const useDevices = () =>
  useQuery({
    queryKey: queryKeys.devices,
    queryFn: fetchDevices,
    refetchInterval: 60_000,
  });

export const useToggleDevice = () => {
  const client = useQueryClient();
  return useMutation<void, Error, { deviceId: string; enabled: boolean }>({
    mutationFn: ({ deviceId, enabled }: { deviceId: string; enabled: boolean }) =>
      toggleDevice(deviceId, enabled),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: queryKeys.devices });
    },
  });
};

export const useDeviceTest = () => {
  const client = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (deviceId: string) => runDeviceTest(deviceId),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: queryKeys.devices });
    },
  });
};

export const useDefaultLighting = () => {
  const client = useQueryClient();
  return useMutation<void, Error>({
    mutationFn: () => setDefaultLighting(),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: queryKeys.devices });
    },
  });
};
