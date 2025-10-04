import { API_BASE_URL } from '../lib/config';
import type {
  ApiResponse,
  CelebrationHistoryItem,
  DevicesPayload,
  GamesPayload,
  SportCode,
  SystemStatus,
  TeamsResponse,
} from '../types';

const buildUrl = (path: string): string => {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  
  // If API_BASE_URL is empty, use relative URLs (for Vite proxy in dev)
  if (!API_BASE_URL || API_BASE_URL.trim().length === 0) {
    return normalized;
  }
  
  // Otherwise, construct full URL with base
  const base = API_BASE_URL.endsWith('/') ? API_BASE_URL : `${API_BASE_URL}/`;
  return new URL(normalized, base).toString();
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${message}`.trim());
  }

  return response.json() as Promise<T>;
}

export const fetchSystemStatus = async (): Promise<SystemStatus> =>
  request<SystemStatus>('/api/status/');

export const fetchDevices = async (): Promise<DevicesPayload> => {
  const payload = await request<ApiResponse<DevicesPayload>>('/api/devices/');
  if (!payload.data) {
    throw new Error('Device response missing data');
  }
  return payload.data;
};

export const fetchGames = async (sport: SportCode): Promise<GamesPayload> => {
  const payload = await request<ApiResponse<GamesPayload>>(`/api/games/live?sport=${sport}`);
  if (!payload.data) {
    throw new Error('Games response missing data');
  }
  return payload.data;
};

export const fetchCelebrationHistory = async (limit = 20): Promise<CelebrationHistoryItem[]> => {
  const payload = await request<ApiResponse<{ celebrations: CelebrationHistoryItem[] }>>(
    `/api/history/celebrations?limit=${limit}`,
  );
  if (!payload.data) {
    throw new Error('Celebrations response missing data');
  }
  return payload.data.celebrations;
};

export const toggleDevice = async (deviceId: string, enabled: boolean): Promise<void> => {
  await request<ApiResponse<unknown>>(`/api/devices/${deviceId}/toggle`, {
    method: 'PUT',
    body: JSON.stringify({ enabled }),
  });
};

export const runDeviceTest = async (deviceId: string): Promise<void> => {
  await request<ApiResponse<unknown>>(`/api/devices/${deviceId}/test`, {
    method: 'POST',
  });
};

export interface CelebrationTriggerPayload {
  team_abbr: string;
  team_name: string;
  event_type: string;
  sport?: string | null;  // Optional: "nfl", "cfb", "nhl", etc.
  points?: number | null;
  game_id?: string | null;
}

export const triggerCelebration = async (payload: CelebrationTriggerPayload): Promise<void> => {
  await request<ApiResponse<unknown>>('/api/celebrations/trigger', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

export const setDefaultLighting = async (): Promise<void> => {
  await request<ApiResponse<unknown>>('/api/devices/default-lighting', {
    method: 'POST',
  });
};

// ---- Teams ----

export const fetchTeams = async (sport?: string) => {
  const qs = sport ? `?sport=${encodeURIComponent(sport)}` : '';
  const payload = await request<ApiResponse<TeamsResponse>>(`/api/teams/${qs}`);
  if (!payload.data) {
    throw new Error('Teams response missing data');
  }
  return payload.data.teams;
};

// ---- Monitoring ----

export interface MonitoredGame {
  game_id: string;
  sport: SportCode;
  home_team_abbr: string;
  away_team_abbr: string;
  monitored_teams: string[];
  created_at: string;
  updated_at: string;
}

export interface MonitoringRequest {
  game_id: string;
  sport: SportCode;
  home_team_abbr: string;
  away_team_abbr: string;
  monitored_teams: string[];
}

export const fetchMonitoredGames = async (): Promise<MonitoredGame[]> => {
  const payload = await request<ApiResponse<{ monitored_games: MonitoredGame[]; count: number }>>(
    '/api/monitoring/',
  );
  if (!payload.data) {
    throw new Error('Monitoring response missing data');
  }
  return payload.data.monitored_games;
};

export const addMonitoring = async (monitoringRequest: MonitoringRequest): Promise<MonitoredGame> => {
  const payload = await request<ApiResponse<MonitoredGame>>('/api/monitoring/', {
    method: 'POST',
    body: JSON.stringify(monitoringRequest),
  });
  if (!payload.data) {
    throw new Error('Add monitoring response missing data');
  }
  return payload.data;
};

export const removeMonitoring = async (gameId: string): Promise<void> => {
  await request<ApiResponse<unknown>>(`/api/monitoring/${gameId}`, {
    method: 'DELETE',
  });
};

export const updateMonitoring = async (gameId: string, monitoringRequest: MonitoringRequest): Promise<MonitoredGame> => {
  const payload = await request<ApiResponse<MonitoredGame>>(`/api/monitoring/${gameId}`, {
    method: 'PUT',
    body: JSON.stringify(monitoringRequest),
  });
  if (!payload.data) {
    throw new Error('Update monitoring response missing data');
  }
  return payload.data;
};
