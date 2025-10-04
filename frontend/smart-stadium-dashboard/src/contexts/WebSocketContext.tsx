import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { 
  WebSocketEvent, 
  GameUpdateEvent, 
  CelebrationUpdateEvent, 
  DeviceUpdateEvent 
} from '../types';
import webSocketService from '../services/enhancedWebSocket';

interface WebSocketContextType {
  isConnected: boolean;
  connectionState: 'connected' | 'connecting' | 'disconnected';
  latestEvent: WebSocketEvent | null;
  gameUpdates: GameUpdateEvent[];
  celebrationUpdates: CelebrationUpdateEvent[];
  deviceUpdates: DeviceUpdateEvent[];
  subscribeToGame: (gameId: string) => void;
  unsubscribeFromGame: (gameId: string) => void;
  subscribeToDevices: (deviceIds: string[]) => void;
  subscribeToCelebrations: () => void;
  clearEvents: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const [latestEvent, setLatestEvent] = useState<WebSocketEvent | null>(null);
  const [gameUpdates, setGameUpdates] = useState<GameUpdateEvent[]>([]);
  const [celebrationUpdates, setCelebrationUpdates] = useState<CelebrationUpdateEvent[]>([]);
  const [deviceUpdates, setDeviceUpdates] = useState<DeviceUpdateEvent[]>([]);

  // Connection status handler
  const handleConnectionChange = useCallback((connected: boolean) => {
    setIsConnected(connected);
    setConnectionState(connected ? 'connected' : 'disconnected');
  }, []);

  // Game update handler
  const handleGameUpdate = useCallback((event: GameUpdateEvent) => {
    setLatestEvent(event);
    setGameUpdates(prev => {
      const updated = [...prev, event];
      // Keep only last 50 events to prevent memory issues
      return updated.slice(-50);
    });
  }, []);

  // Celebration update handler
  const handleCelebrationUpdate = useCallback((event: CelebrationUpdateEvent) => {
    setLatestEvent(event);
    setCelebrationUpdates(prev => {
      const updated = [...prev, event];
      return updated.slice(-50);
    });
  }, []);

  // Device update handler
  const handleDeviceUpdate = useCallback((event: DeviceUpdateEvent) => {
    setLatestEvent(event);
    setDeviceUpdates(prev => {
      const updated = [...prev, event];
      return updated.slice(-50);
    });
  }, []);

  // System update handler
  const handleSystemUpdate = useCallback((event: WebSocketEvent) => {
    setLatestEvent(event);
    
    // Handle connection state changes
    if (event.type === 'system_update' && event.data.status) {
      if (event.data.status === 'connected') {
        setIsConnected(true);
        setConnectionState('connected');
      } else if (event.data.status === 'disconnected') {
        setIsConnected(false);
        setConnectionState('disconnected');
      }
    }
  }, []);

  // Setup WebSocket event listeners
  useEffect(() => {
    // Register event handlers
    webSocketService.onConnection(handleConnectionChange);
    webSocketService.onGameUpdate(handleGameUpdate);
    webSocketService.onCelebrationUpdate(handleCelebrationUpdate);
    webSocketService.onDeviceUpdate(handleDeviceUpdate);
    webSocketService.on('system_update', handleSystemUpdate);

    // Update initial connection state
    setIsConnected(webSocketService.isConnected);
    setConnectionState(webSocketService.connectionState);

    // Cleanup on unmount
    return () => {
      // Note: WebSocketService handles cleanup internally
      // We don't need to manually remove listeners as the service is a singleton
    };
  }, [handleConnectionChange, handleGameUpdate, handleCelebrationUpdate, handleDeviceUpdate, handleSystemUpdate]);

  // Monitor connection state changes
  useEffect(() => {
    const intervalId = setInterval(() => {
      const currentState = webSocketService.connectionState;
      if (currentState !== connectionState) {
        setConnectionState(currentState);
        setIsConnected(webSocketService.isConnected);
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, [connectionState]);

  const subscribeToGame = useCallback((gameId: string) => {
    webSocketService.subscribeToGame(gameId);
  }, []);

  const unsubscribeFromGame = useCallback((gameId: string) => {
    webSocketService.unsubscribeFromGame(gameId);
  }, []);

  const subscribeToDevices = useCallback((deviceIds: string[]) => {
    webSocketService.subscribeToDevices(deviceIds);
  }, []);

  const subscribeToCelebrations = useCallback(() => {
    webSocketService.subscribeToCelebrations();
  }, []);

  const clearEvents = useCallback(() => {
    setGameUpdates([]);
    setCelebrationUpdates([]);
    setDeviceUpdates([]);
    setLatestEvent(null);
  }, []);

  const contextValue: WebSocketContextType = {
    isConnected,
    connectionState,
    latestEvent,
    gameUpdates,
    celebrationUpdates,
    deviceUpdates,
    subscribeToGame,
    unsubscribeFromGame,
    subscribeToDevices,
    subscribeToCelebrations,
    clearEvents,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};