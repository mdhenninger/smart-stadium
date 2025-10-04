// Environment Configuration
// Centralized configuration management for the application

export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
  };
  websocket: {
    baseUrl: string;
    reconnectAttempts: number;
    reconnectInterval: number;
  };
  features: {
    devTools: boolean;
    errorReporting: boolean;
    analytics: boolean;
  };
  app: {
    version: string;
    environment: string;
    isDevelopment: boolean;
    isProduction: boolean;
  };
}

// Environment variable helpers
const getEnvVar = (key: string, defaultValue?: string): string => {
  const value = import.meta.env[key] || defaultValue;
  if (!value) {
    console.warn(`Environment variable ${key} is not defined`);
    return '';
  }
  return value;
};

const getBooleanEnvVar = (key: string, defaultValue: boolean = false): boolean => {
  const value = getEnvVar(key, defaultValue.toString());
  return value.toLowerCase() === 'true';
};

const getNumberEnvVar = (key: string, defaultValue: number): number => {
  const value = getEnvVar(key, defaultValue.toString());
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
};

// Application configuration
export const config: AppConfig = {
  api: {
    baseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),
    timeout: getNumberEnvVar('VITE_API_TIMEOUT', 10000),
  },
  websocket: {
    baseUrl: getEnvVar('VITE_WS_BASE_URL', 'ws://localhost:8000'),
    reconnectAttempts: getNumberEnvVar('VITE_WS_RECONNECT_ATTEMPTS', 5),
    reconnectInterval: getNumberEnvVar('VITE_WS_RECONNECT_INTERVAL', 1000),
  },
  features: {
    devTools: getBooleanEnvVar('VITE_ENABLE_DEV_TOOLS', import.meta.env.DEV),
    errorReporting: getBooleanEnvVar('VITE_ENABLE_ERROR_REPORTING', import.meta.env.PROD),
    analytics: getBooleanEnvVar('VITE_ENABLE_ANALYTICS', import.meta.env.PROD),
  },
  app: {
    version: getEnvVar('VITE_APP_VERSION', '1.0.0'),
    environment: import.meta.env.MODE,
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD,
  },
};

// Configuration validation
const validateConfig = () => {
  const errors: string[] = [];
  
  if (!config.api.baseUrl) {
    errors.push('API base URL is required');
  }
  
  if (!config.websocket.baseUrl) {
    errors.push('WebSocket base URL is required');
  }
  
  if (errors.length > 0) {
    console.error('Configuration validation errors:', errors);
    throw new Error(`Configuration validation failed: ${errors.join(', ')}`);
  }
};

// Validate configuration on import
validateConfig();

// Export individual configurations for convenience
export const apiConfig = config.api;
export const wsConfig = config.websocket;
export const featureFlags = config.features;
export const appInfo = config.app;

// Development helper
if (config.app.isDevelopment) {
  console.log('🔧 Development Configuration Loaded:', {
    environment: config.app.environment,
    version: config.app.version,
    apiUrl: config.api.baseUrl,
    wsUrl: config.websocket.baseUrl,
    features: config.features,
  });
}

export default config;