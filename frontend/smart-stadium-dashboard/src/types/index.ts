// Core API Types matching backend models
export interface Team {
  id: string;
  name: string;
  city: string;
  abbreviation: string;
  conference: string;
  division: string;
  colors: {
    primary: string;
    secondary: string;
    accent?: string;
  };
  logo_url?: string;
}

export interface Game {
  id: string;
  week: number;
  season_type: string;
  home_team: Team;
  away_team: Team;
  status: 'scheduled' | 'in_progress' | 'completed' | 'postponed';
  start_time: string;
  venue: string;
  scores: {
    home: number;
    away: number;
  };
  current_period: number;
  time_remaining: string;
  field_position?: {
    team: string;
    yard_line: number;
    down?: number;
    distance?: number;
  };
  last_play?: string;
}

export interface Device {
  id: string;
  name: string;
  type: 'wiz' | 'lifx' | 'hue' | 'generic';
  ip_address: string;
  mac_address?: string;
  is_online: boolean;
  current_state: {
    brightness: number;
    color: {
      r: number;
      g: number;
      b: number;
    };
    effect?: string;
  };
  capabilities: string[];
  room?: string;
  last_seen: string;
}

export interface CelebrationRequest {
  type: 'touchdown' | 'field_goal' | 'safety' | 'interception' | 'fumble_recovery' | 
        'sack' | 'big_play' | 'game_winner' | 'victory' | 'big_stop' | 'custom';
  team_id: string;
  duration?: number;
  intensity?: 'low' | 'medium' | 'high';
  devices?: string[];
  custom_colors?: {
    primary: string;
    secondary: string;
  };
}

export interface CelebrationStatus {
  id: string;
  type: string;
  team_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  started_at: string;
  estimated_end?: string;
  devices_count: number;
  error_message?: string;
}

// WebSocket Event Types
export interface WebSocketEvent {
  type: string;
  data: any;
  timestamp: string;
}

export interface GameUpdateEvent extends WebSocketEvent {
  type: 'game_update';
  data: {
    game: Game;
    changes: string[];
  };
}

export interface CelebrationUpdateEvent extends WebSocketEvent {
  type: 'celebration_update';
  data: CelebrationStatus;
}

export interface DeviceUpdateEvent extends WebSocketEvent {
  type: 'device_update';
  data: {
    device: Device;
    status: 'online' | 'offline' | 'updated';
  };
}

// Dashboard Data Types
export interface DashboardData {
  current_game?: Game;
  active_celebrations: CelebrationStatus[];
  device_summary: {
    total: number;
    online: number;
    offline: number;
  };
  recent_events: WebSocketEvent[];
  system_health: SystemHealth;
}

export interface SystemHealth {
  api_status: 'healthy' | 'degraded' | 'down';
  database_status: 'connected' | 'disconnected';
  websocket_connections: number;
  active_celebrations: number;
  device_health: {
    total_devices: number;
    responsive_devices: number;
    last_check: string;
  };
  uptime: number;
}

export interface UserPreferences {
  favorite_team?: string;
  celebration_intensity: 'low' | 'medium' | 'high';
  auto_celebrations: boolean;
  notification_settings: {
    game_updates: boolean;
    celebration_complete: boolean;
    device_issues: boolean;
  };
  dashboard_layout: {
    show_field_position: boolean;
    show_device_grid: boolean;
    refresh_interval: number;
  };
  theme: 'dark' | 'light' | 'auto';
}

// UI State Types
export interface AppState {
  currentGame?: Game;
  selectedSport: 'nfl' | 'college';
  isConnected: boolean;
  preferences: UserPreferences;
  loading: boolean;
  error?: string;
}

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  badge?: number;
}

// Field Position Visualization Types
export interface FieldZone {
  id: string;
  start_yard: number;
  end_yard: number;
  team: 'home' | 'away' | 'neutral';
  is_endzone: boolean;
  is_active: boolean;
}

export interface PlayInfo {
  down: number;
  distance: number;
  yard_line: number;
  possession_team: string;
  time_remaining: string;
  period: number;
}