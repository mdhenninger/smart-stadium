import { io, Socket } from 'socket.io-client';
import { WebSocketEvent, GameUpdateEvent, CelebrationUpdateEvent, DeviceUpdateEvent } from '../types';

export type WebSocketEventHandler = (event: WebSocketEvent) => void;
export type GameUpdateHandler = (event: GameUpdateEvent) => void;
export type CelebrationUpdateHandler = (event: CelebrationUpdateEvent) => void;
export type DeviceUpdateHandler = (event: DeviceUpdateEvent) => void;

class WebSocketService {
  private socket: Socket | null = null;
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000;
  private isConnecting = false;

  constructor() {
    this.connect();
  }

  connect(): void {
    if (this.isConnecting || (this.socket && this.socket.connected)) {
      return;
    }

    this.isConnecting = true;

    try {
      this.socket = io('/', {
        path: '/ws/socket.io/',
        transports: ['websocket', 'polling'],
        upgrade: true,
        rememberUpgrade: true,
        timeout: 5000,
        forceNew: true,
      });

      this.setupEventHandlers();
      console.log('🔌 WebSocket connecting...');
    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.notifyHandlers('connection', { 
        type: 'system_update', 
        data: { status: 'connected' }, 
        timestamp: new Date().toISOString() 
      });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 WebSocket disconnected:', reason);
      this.isConnecting = false;
      this.notifyHandlers('connection', { 
        type: 'system_update', 
        data: { status: 'disconnected', reason }, 
        timestamp: new Date().toISOString() 
      });

      if (reason === 'io server disconnect') {
        // Server disconnected, manually reconnect
        this.scheduleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    });

    // Game events
    this.socket.on('game_update', (data: GameUpdateEvent) => {
      console.log('🏈 Game update received:', data);
      this.notifyHandlers('game_update', data);
      this.notifyHandlers('all', data);
    });

    // Celebration events
    this.socket.on('celebration_update', (data: CelebrationUpdateEvent) => {
      console.log('🎉 Celebration update received:', data);
      this.notifyHandlers('celebration_update', data);
      this.notifyHandlers('all', data);
    });

    // Device events
    this.socket.on('device_update', (data: DeviceUpdateEvent) => {
      console.log('💡 Device update received:', data);
      this.notifyHandlers('device_update', data);
      this.notifyHandlers('all', data);
    });

    // System events
    this.socket.on('system_update', (data: WebSocketEvent) => {
      console.log('⚙️ System update received:', data);
      this.notifyHandlers('system_update', data);
      this.notifyHandlers('all', data);
    });

    // Error events
    this.socket.on('error', (error: any) => {
      console.error('❌ WebSocket error:', error);
      this.notifyHandlers('error', { 
        type: 'system_update', 
        data: { error }, 
        timestamp: new Date().toISOString() 
      });
    });
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  private notifyHandlers(eventType: string, event: WebSocketEvent): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('❌ Error in WebSocket event handler:', error);
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

  onConnection(handler: (connected: boolean) => void): void {
    this.on('connection', (event) => {
      handler(event.data.status === 'connected');
    });
  }

  // Send events to server (if needed)
  emit(eventType: string, data: any): void {
    if (this.socket && this.socket.connected) {
      this.socket.emit(eventType, data);
    } else {
      console.warn('⚠️ Cannot emit event: WebSocket not connected');
    }
  }

  // Subscribe to game updates for specific game
  subscribeToGame(gameId: string): void {
    this.emit('subscribe_game', { game_id: gameId });
  }

  unsubscribeFromGame(gameId: string): void {
    this.emit('unsubscribe_game', { game_id: gameId });
  }

  // Subscribe to device updates for specific devices
  subscribeToDevices(deviceIds: string[]): void {
    this.emit('subscribe_devices', { device_ids: deviceIds });
  }

  // Subscribe to celebration updates
  subscribeToCelebrations(): void {
    this.emit('subscribe_celebrations', {});
  }

  // Connection status
  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  get connectionState(): 'connected' | 'connecting' | 'disconnected' {
    if (this.isConnecting) return 'connecting';
    if (this.socket?.connected) return 'connected';
    return 'disconnected';
  }

  // Cleanup
  disconnect(): void {
    if (this.socket) {
      console.log('🔌 Disconnecting WebSocket...');
      this.socket.disconnect();
      this.socket = null;
    }
    this.eventHandlers.clear();
    this.reconnectAttempts = 0;
    this.isConnecting = false;
  }
}

// Create singleton instance
export const webSocketService = new WebSocketService();
export default webSocketService;