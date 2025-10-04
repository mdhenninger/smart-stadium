import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  Game, 
  Device, 
  Team, 
  CelebrationRequest, 
  CelebrationStatus, 
  DashboardData, 
  SystemHealth, 
  UserPreferences 
} from '../types';
import { apiConfig } from '../config/env';

class ApiService {
  private api: AxiosInstance;
  private config = apiConfig;

  constructor() {
    this.api = axios.create({
      baseURL: this.config.baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('❌ API Response Error:', error.response?.status, error.response?.data);
        return Promise.reject(error);
      }
    );
  }

  // Health and System
  async getHealth(): Promise<SystemHealth> {
    const response: AxiosResponse<SystemHealth> = await this.api.get('/health');
    return response.data;
  }

  // Games
  async getTodaysGames(): Promise<Game[]> {
    const response: AxiosResponse<Game[]> = await this.api.get('/games/today');
    return response.data;
  }

  async getLiveGames(): Promise<Game[]> {
    const response: AxiosResponse<Game[]> = await this.api.get('/games/live');
    return response.data;
  }

  async getGame(gameId: string): Promise<Game> {
    const response: AxiosResponse<Game> = await this.api.get(`/games/${gameId}`);
    return response.data;
  }

  async getGamesByWeek(week: number, seasonType: string = 'regular'): Promise<Game[]> {
    const response: AxiosResponse<Game[]> = await this.api.get(`/games/week/${week}`, {
      params: { season_type: seasonType }
    });
    return response.data;
  }

  async getGamesByTeam(teamId: string): Promise<Game[]> {
    const response: AxiosResponse<Game[]> = await this.api.get(`/games/team/${teamId}`);
    return response.data;
  }

  // Teams
  async getAllTeams(): Promise<Team[]> {
    const response: AxiosResponse<Team[]> = await this.api.get('/teams');
    return response.data;
  }

  async getTeam(teamId: string): Promise<Team> {
    const response: AxiosResponse<Team> = await this.api.get(`/teams/${teamId}`);
    return response.data;
  }

  async getTeamsByConference(conference: string): Promise<Team[]> {
    const response: AxiosResponse<Team[]> = await this.api.get(`/teams/conference/${conference}`);
    return response.data;
  }

  // Devices
  async getDevices(): Promise<Device[]> {
    const response: AxiosResponse<Device[]> = await this.api.get('/devices');
    return response.data;
  }

  async getDevice(deviceId: string): Promise<Device> {
    const response: AxiosResponse<Device> = await this.api.get(`/devices/${deviceId}`);
    return response.data;
  }

  async discoverDevices(): Promise<Device[]> {
    const response: AxiosResponse<Device[]> = await this.api.post('/devices/discover');
    return response.data;
  }

  async testDevice(deviceId: string): Promise<{ success: boolean; message: string }> {
    const response = await this.api.post(`/devices/${deviceId}/test`);
    return response.data;
  }

  async updateDevice(deviceId: string, updates: Partial<Device>): Promise<Device> {
    const response: AxiosResponse<Device> = await this.api.put(`/devices/${deviceId}`, updates);
    return response.data;
  }

  async deleteDevice(deviceId: string): Promise<void> {
    await this.api.delete(`/devices/${deviceId}`);
  }

  // Celebrations
  async triggerCelebration(request: CelebrationRequest): Promise<CelebrationStatus> {
    const response: AxiosResponse<CelebrationStatus> = await this.api.post('/celebrations/trigger', request);
    return response.data;
  }

  async getCelebrationStatus(celebrationId: string): Promise<CelebrationStatus> {
    const response: AxiosResponse<CelebrationStatus> = await this.api.get(`/celebrations/${celebrationId}`);
    return response.data;
  }

  async getActiveCelebrations(): Promise<CelebrationStatus[]> {
    const response: AxiosResponse<CelebrationStatus[]> = await this.api.get('/celebrations/active');
    return response.data;
  }

  async stopCelebration(celebrationId: string): Promise<void> {
    await this.api.post(`/celebrations/${celebrationId}/stop`);
  }

  async previewCelebration(request: CelebrationRequest): Promise<{ preview_url: string }> {
    const response = await this.api.post('/celebrations/preview', request);
    return response.data;
  }

  // Dashboard
  async getDashboardData(): Promise<DashboardData> {
    const response: AxiosResponse<DashboardData> = await this.api.get('/dashboard/data');
    return response.data;
  }

  async getUserPreferences(): Promise<UserPreferences> {
    const response: AxiosResponse<UserPreferences> = await this.api.get('/dashboard/preferences');
    return response.data;
  }

  async updateUserPreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    const response: AxiosResponse<UserPreferences> = await this.api.put('/dashboard/preferences', preferences);
    return response.data;
  }

  async getSystemStats(): Promise<any> {
    const response = await this.api.get('/dashboard/stats');
    return response.data;
  }

  async getDashboardConfig(): Promise<any> {
    const response = await this.api.get('/dashboard/config');
    return response.data;
  }

  async getDashboardSummary(): Promise<any> {
    const response = await this.api.get('/dashboard/summary');
    return response.data;
  }

  // Utility methods
  async ping(): Promise<{ status: string; timestamp: string }> {
    const response = await this.api.get('/ping');
    return response.data;
  }

  // Error handling helper
  handleError(error: any): string {
    if (error.response) {
      // Server responded with error status
      return error.response.data?.message || `Error ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
      // Request made but no response received
      return 'Network error: Unable to connect to the server';
    } else {
      // Something else happened
      return error.message || 'An unexpected error occurred';
    }
  }
}

// Create singleton instance
export const apiService = new ApiService();
export default apiService;