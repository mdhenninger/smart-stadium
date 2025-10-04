import { WebSocketEvent, GameUpdateEvent, CelebrationUpdateEvent, DeviceUpdateEvent } from '../types';
import { config } from '../config/env';

export type WebSocketEventHandler = (event: WebSocketEvent) => void;
export type GameUpdateHandler = (event: GameUpdateEvent) => void;
export type CelebrationUpdateHandler = (event: CelebrationUpdateEvent) => void;
export type DeviceUpdateHandler = (event: DeviceUpdateEvent) => void;

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface SubscriptionMessage {
  action: 'subscribe' | 'unsubscribe';
  subscriptions: string[];
}

class EnhancedWebSocketService {
  private socket: WebSocket | null = null;
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map();
  private connectionId: string = '';
  private subscriptions: string[] = ['all'];
  
  // Connection management
  private _isConnecting = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectBaseDelay = 1000; // 1 second
  private reconnectMaxDelay = 30000; // 30 seconds
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private heartbeatIntervalId: NodeJS.Timeout | null = null;
  private heartbeatInterval = 30000; // 30 seconds
  
  // Connection state tracking
  private lastConnectedTime: Date | null = null;
  private lastDisconnectedTime: Date | null = null;
  private connectionAttempts = 0;
  private totalReconnections = 0;
  
  constructor() {
    // Generate unique client ID
    this.connectionId = `client_${Math.random().toString(36).substr(2, 9)}_${Date.now()}`;
    this.connect();
    
    // Handle page visibility changes
    if (typeof document !== 'undefined') {
      document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }
    
    // Handle online/offline events
    if (typeof window !== 'undefined') {
      window.addEventListener('online', this.handleOnline.bind(this));
      window.addEventListener('offline', this.handleOffline.bind(this));
    }
  }

  connect(): void {
    if (this._isConnecting || (this.socket && this.socket.readyState === WebSocket.CONNECTING)) {
      console.log('🔄 WebSocket already connecting...');
      return;
    }

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('✅ WebSocket already connected');
      return;
    }

    this._isConnecting = true;
    this.connectionAttempts++;

    try {
      // Clear any existing reconnect timeout
      if (this.reconnectTimeoutId) {
        clearTimeout(this.reconnectTimeoutId);
        this.reconnectTimeoutId = null;
      }

      // Build WebSocket URL with query parameters
      const wsBaseUrl = config.websocket.baseUrl;
      const wsUrl = new URL('/api/ws', wsBaseUrl);
      wsUrl.searchParams.set('client_id', this.connectionId);
      wsUrl.searchParams.set('subscriptions', this.subscriptions.join(','));

      console.log(`🔌 WebSocket connecting... (attempt ${this.connectionAttempts})`);
      console.log(`📡 URL: ${wsUrl.toString()}`);

      this.socket = new WebSocket(wsUrl.toString());
      this.setupEventHandlers();

    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      this._isConnecting = false;
      this.scheduleReconnect();
    }
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('✅ WebSocket connected');
      this._isConnecting = false;
      this.reconnectAttempts = 0;
      this.lastConnectedTime = new Date();
      this.lastDisconnectedTime = null;
      
      // Start heartbeat
      this.startHeartbeat();
      
      // Notify connection handlers
      this.notifyHandlers('connection', {
        type: 'connection_established',
        data: { 
          status: 'connected',
          connectionId: this.connectionId,
          subscriptions: this.subscriptions,
          connectionAttempts: this.connectionAttempts,
          totalReconnections: this.totalReconnections
        },
        timestamp: new Date().toISOString()
      });
    };

    this.socket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log(`📨 WebSocket message (${message.type}):`, message);
        
        // Handle different message types
        switch (message.type) {
          case 'connection_established':
            this.handleConnectionEstablished(message);
            break;
          case 'subscription_updated':
            this.handleSubscriptionUpdated(message);
            break;
          case 'game_update':
            this.notifyHandlers('game_update', message as GameUpdateEvent);
            break;
          case 'celebration_event':
            this.notifyHandlers('celebration_update', message as CelebrationUpdateEvent);
            break;
          case 'device_event':
            this.notifyHandlers('device_update', message as DeviceUpdateEvent);
            break;
          case 'system_status':
          case 'initial_system_status':
            this.notifyHandlers('system_update', message);
            break;
          case 'error':
            this.handleError(message);
            break;
          case 'pong':
            console.log('💓 Heartbeat pong received');
            break;
          default:
            console.log(`🔀 Unknown message type: ${message.type}`, message);
            this.notifyHandlers('unknown', message);
        }
        
        // Always notify 'all' handlers
        this.notifyHandlers('all', message);
        
      } catch (error) {
        console.error('❌ Failed to parse WebSocket message:', error, event.data);
      }
    };

    this.socket.onclose = (event) => {
      console.log(`🔌 WebSocket disconnected (code: ${event.code}, reason: ${event.reason})`);
      this._isConnecting = false;
      this.lastDisconnectedTime = new Date();
      
      // Stop heartbeat
      this.stopHeartbeat();
      
      // Notify disconnection handlers
      this.notifyHandlers('connection', {
        type: 'connection_lost',
        data: { 
          status: 'disconnected',
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean
        },
        timestamp: new Date().toISOString()
      });

      // Schedule reconnection unless it was a clean close
      if (!event.wasClean || event.code !== 1000) {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      this._isConnecting = false;
      
      this.notifyHandlers('error', {
        type: 'connection_error',
        data: { error: error.toString() },
        timestamp: new Date().toISOString()
      });
    };
  }

  private handleConnectionEstablished(message: WebSocketMessage): void {
    console.log('🎉 Connection established:', message.data);
    this.notifyHandlers('connection_established', message);
  }

  private handleSubscriptionUpdated(message: WebSocketMessage): void {
    console.log('📋 Subscriptions updated:', message.data);
    this.notifyHandlers('subscription_updated', message);
  }

  private handleError(message: WebSocketMessage): void {
    console.error('❌ Server error:', message.data);
    this.notifyHandlers('error', message);
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`❌ Max reconnection attempts (${this.maxReconnectAttempts}) reached. Giving up.`);
      this.notifyHandlers('connection', {
        type: 'connection_failed',
        data: { 
          status: 'failed',
          attempts: this.reconnectAttempts,
          maxAttempts: this.maxReconnectAttempts
        },
        timestamp: new Date().toISOString()
      });
      return;
    }

    this.reconnectAttempts++;
    this.totalReconnections++;
    
    // Exponential backoff with jitter
    const baseDelay = Math.min(
      this.reconnectBaseDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.reconnectMaxDelay
    );
    const jitter = Math.random() * 1000; // Add up to 1 second of jitter
    const delay = baseDelay + jitter;

    console.log(`🔄 Scheduling reconnect in ${Math.round(delay)}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimeoutId = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat(); // Clear any existing heartbeat
    
    this.heartbeatIntervalId = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        console.log('💓 Sending heartbeat ping');
        this.send({
          type: 'ping',
          data: { timestamp: new Date().toISOString() },
          timestamp: new Date().toISOString()
        });
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatIntervalId) {
      clearInterval(this.heartbeatIntervalId);
      this.heartbeatIntervalId = null;
    }
  }

  private handleVisibilityChange(): void {
    if (document.visibilityState === 'visible') {
      console.log('📱 Page became visible - checking connection');
      if (!this.isConnected) {
        this.connect();
      }
    } else {
      console.log('📱 Page became hidden');
    }
  }

  private handleOnline(): void {
    console.log('🌐 Network online - attempting reconnection');
    if (!this.isConnected) {
      this.reconnectAttempts = 0; // Reset attempts on network recovery
      this.connect();
    }
  }

  private handleOffline(): void {
    console.log('🌐 Network offline');
    this.notifyHandlers('connection', {
      type: 'network_offline',
      data: { status: 'offline' },
      timestamp: new Date().toISOString()
    });
  }

  private notifyHandlers(eventType: string, event: WebSocketEvent): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error(`❌ Error in WebSocket event handler for ${eventType}:`, error);
      }
    });
  }

  // Public methods for subscribing to events
  on(eventType: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  // Convenience methods for specific event types
  onGameUpdate(handler: GameUpdateHandler): void {
    this.on('game_update', handler as WebSocketEventHandler);
  }

  onCelebrationUpdate(handler: CelebrationUpdateHandler): void {
    this.on('celebration_update', handler as WebSocketEventHandler);
  }

  onDeviceUpdate(handler: DeviceUpdateHandler): void {
    this.on('device_update', handler as WebSocketEventHandler);
  }

  onConnection(handler: (event: WebSocketEvent) => void): void {
    this.on('connection', handler);
  }

  onConnectionEstablished(handler: (connected: boolean) => void): void {
    this.on('connection_established', () => handler(true));
    this.on('connection_lost', () => handler(false));
    this.on('connection_failed', () => handler(false));
  }

  // Send messages to server
  send(message: any): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.socket.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('❌ Failed to send WebSocket message:', error);
        return false;
      }
    } else {
      console.warn('⚠️ Cannot send message: WebSocket not connected');
      return false;
    }
  }

  // Update subscriptions
  updateSubscriptions(subscriptions: string[]): void {
    this.subscriptions = subscriptions;
    
    const message: SubscriptionMessage = {
      action: 'subscribe',
      subscriptions: subscriptions
    };
    
    if (this.send(message)) {
      console.log(`📋 Updated subscriptions: ${subscriptions.join(', ')}`);
    }
  }

  // Subscribe to specific types
  subscribeToGame(gameId: string): void {
    this.send({
      action: 'subscribe_game',
      game_id: gameId
    });
  }

  unsubscribeFromGame(gameId: string): void {
    this.send({
      action: 'unsubscribe_game',
      game_id: gameId
    });
  }

  subscribeToDevices(deviceIds: string[]): void {
    this.send({
      action: 'subscribe_devices',
      device_ids: deviceIds
    });
  }

  subscribeToCelebrations(): void {
    this.send({
      action: 'subscribe_celebrations'
    });
  }

  // Connection status properties
  get isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  get isConnecting(): boolean {
    return this._isConnecting || this.socket?.readyState === WebSocket.CONNECTING;
  }

  get connectionState(): 'connected' | 'connecting' | 'disconnected' | 'error' {
    if (!this.socket) return 'disconnected';
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }

  get connectionStats() {
    return {
      connectionId: this.connectionId,
      state: this.connectionState,
      subscriptions: this.subscriptions,
      connectionAttempts: this.connectionAttempts,
      reconnectAttempts: this.reconnectAttempts,
      totalReconnections: this.totalReconnections,
      lastConnectedTime: this.lastConnectedTime,
      lastDisconnectedTime: this.lastDisconnectedTime,
      isConnected: this.isConnected,
      maxReconnectAttempts: this.maxReconnectAttempts
    };
  }

  // Force reconnection
  reconnect(): void {
    console.log('🔄 Manual reconnection requested');
    this.disconnect();
    this.reconnectAttempts = 0; // Reset attempts
    setTimeout(() => this.connect(), 100);
  }

  // Cleanup and disconnect
  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket...');
    
    // Clear timeouts and intervals
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
    this.stopHeartbeat();
    
    // Close socket cleanly
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        this.socket.close(1000, 'Client disconnect');
      }
      this.socket = null;
    }
    
    // Clean up state
    this._isConnecting = false;
    this.reconnectAttempts = 0;
    
    // Remove event listeners
    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    }
    if (typeof window !== 'undefined') {
      window.removeEventListener('online', this.handleOnline);
      window.removeEventListener('offline', this.handleOffline);
    }
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    return new Promise((resolve) => {
      if (!this.isConnected) {
        resolve(false);
        return;
      }

      const timeout = setTimeout(() => {
        resolve(false);
      }, 5000);

      const handlePong = (event: WebSocketEvent) => {
        if (event.type === 'pong') {
          clearTimeout(timeout);
          this.off('all', handlePong);
          resolve(true);
        }
      };

      this.on('all', handlePong);
      this.send({
        type: 'ping',
        data: { healthCheck: true },
        timestamp: new Date().toISOString()
      });
    });
  }
}

// Create singleton instance
export const enhancedWebSocketService = new EnhancedWebSocketService();
export default enhancedWebSocketService;