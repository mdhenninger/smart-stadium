import React, { createContext, useContext, useEffect, useState } from 'react';
import { UserPreferences, SystemHealth } from '../types';
import apiService from '../services/api';

interface ApiContextType {
  preferences: UserPreferences | null;
  systemHealth: SystemHealth | null;
  isLoading: boolean;
  error: string | null;
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>;
  refreshHealth: () => Promise<void>;
  clearError: () => void;
}

const defaultPreferences: UserPreferences = {
  celebration_intensity: 'medium',
  auto_celebrations: true,
  notification_settings: {
    game_updates: true,
    celebration_complete: true,
    device_issues: true,
  },
  dashboard_layout: {
    show_field_position: true,
    show_device_grid: true,
    refresh_interval: 5000,
  },
  theme: 'dark',
};

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

interface ApiProviderProps {
  children: React.ReactNode;
}

export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Load user preferences
        try {
          const userPrefs = await apiService.getUserPreferences();
          setPreferences(userPrefs);
        } catch (prefError) {
          console.warn('Failed to load user preferences, using defaults:', prefError);
          setPreferences(defaultPreferences);
        }

        // Load system health
        const health = await apiService.getHealth();
        setSystemHealth(health);

      } catch (err) {
        const errorMessage = apiService.handleError(err);
        setError(errorMessage);
        console.error('Failed to load initial API data:', err);
        
        // Set defaults if API is unavailable
        setPreferences(defaultPreferences);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // Refresh system health periodically
  useEffect(() => {
    const refreshInterval = preferences?.dashboard_layout.refresh_interval || 30000;
    
    const intervalId = setInterval(async () => {
      try {
        const health = await apiService.getHealth();
        setSystemHealth(health);
        setError(null); // Clear any previous errors
      } catch (err) {
        console.warn('Health check failed:', err);
        // Don't set error for periodic health checks to avoid UI noise
      }
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [preferences?.dashboard_layout.refresh_interval]);

  const updatePreferences = async (updates: Partial<UserPreferences>) => {
    if (!preferences) return;

    setIsLoading(true);
    setError(null);

    try {
      const updatedPreferences = await apiService.updateUserPreferences(updates);
      setPreferences(updatedPreferences);
    } catch (err) {
      const errorMessage = apiService.handleError(err);
      setError(errorMessage);
      console.error('Failed to update preferences:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshHealth = async () => {
    setError(null);
    
    try {
      const health = await apiService.getHealth();
      setSystemHealth(health);
    } catch (err) {
      const errorMessage = apiService.handleError(err);
      setError(errorMessage);
      console.error('Failed to refresh health:', err);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const contextValue: ApiContextType = {
    preferences,
    systemHealth,
    isLoading,
    error,
    updatePreferences,
    refreshHealth,
    clearError,
  };

  return (
    <ApiContext.Provider value={contextValue}>
      {children}
    </ApiContext.Provider>
  );
};