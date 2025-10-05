export type SportCode = 'nfl' | 'college_football';

export interface SystemStatus {
  uptime_seconds: number;
  environment: string;
  total_devices: number;
  enabled_devices: number;
  online_devices: number;
  offline_devices: number;
  monitoring_active: boolean;
  sports_enabled: Record<string, boolean>;
  fetched_at: string;
}

export interface DeviceInfo {
  device_id: string;
  ip_address: string;
  name: string;
  location?: string | null;
  enabled: boolean;
  device_type: string;
  light_type?: 'lamp' | 'ceiling-fan' | null;
  last_seen?: string | null;
  response_time_ms?: number | null;
  status: 'online' | 'offline' | 'unknown';
}

export interface DeviceSummary {
  total_devices: number;
  enabled_devices: number;
  online_devices: number;
  offline_devices: number;
}

export interface DevicesPayload {
  devices: DeviceInfo[];
  summary: DeviceSummary;
}

export interface CelebrationHistoryItem {
  id: number;
  timestamp: string;
  sport: string | null;
  team: string | null;
  event_type: string | null;
  game_id: string | null;
  detail?: string | null;
}

export interface DeviceEventHistoryItem {
  id: number;
  timestamp: string;
  device_id: string | null;
  status: string | null;
  message?: string | null;
}

export interface ErrorHistoryItem {
  id: number;
  timestamp: string;
  source: string | null;
  message: string | null;
}

export interface TeamScore {
  team_id: string;
  abbreviation: string;
  display_name: string;
  score: number;
  logo_url?: string | null;
}

export type GameStatusCode = 'pre' | 'in' | 'post' | 'unknown';

export interface RedZoneInfo {
  active: boolean;
  team_abbr?: string | null;
  yard_line?: number | null;
}

export interface GameSituation {
  possession_team_id?: string | null;
  down_distance?: string | null;
  field_position?: string | null;
  is_red_zone: boolean;
  clock?: string | null;
  period?: number | null;
}

export interface GameSnapshot {
  id: string;
  sport: SportCode;
  home: TeamScore;
  away: TeamScore;
  status: GameStatusCode;
  last_update: string;
  red_zone: RedZoneInfo;
  situation?: GameSituation | null;
}

export interface GamesPayload {
  sport: SportCode;
  games: GameSnapshot[];
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export type LiveEventMessage =
  | {
      type: 'celebration';
      sport: string;
      team: string;
      delta: number;
      gameId: string;
    }
  | {
      type: 'victory';
      sport: string;
      winner: string;
      gameId: string;
      final: string;
    }
  | {
      type: string;
      [key: string]: unknown;
    };

// ---- Teams (manual celebrations) ----

// Broader sport codes used for teams (can include leagues not in live scoreboard)
export type TeamSportCode = 'nfl' | 'cfb' | 'nhl' | 'nba' | 'mlb';

export interface TeamColors {
  primary: [number, number, number];
  secondary: [number, number, number];
  lighting_primary?: [number, number, number];
  lighting_secondary?: [number, number, number];
}

export interface TeamOption {
  value: string; // "sport:abbr" e.g. "nfl:BUF"
  label: string; // "Buffalo Bills (NFL)" when All is selected
  abbreviation: string;
  name: string;
  sport: TeamSportCode | string; // tolerate unknown/new sports
  city?: string | null;
  colors: TeamColors;
}

export interface TeamsResponse {
  teams: TeamOption[];
  total_count: number;
}
