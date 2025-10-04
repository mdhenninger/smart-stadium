import React from 'react';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { useApi } from '../../contexts/ApiContext';

const Header: React.FC = () => {
  const { connectionState } = useWebSocket();
  const { systemHealth } = useApi();

  const getConnectionStatus = () => {
    switch (connectionState) {
      case 'connected':
        return { text: 'Connected', color: 'text-green-400', icon: '🟢' };
      case 'connecting':
        return { text: 'Connecting...', color: 'text-yellow-400', icon: '🟡' };
      case 'disconnected':
        return { text: 'Disconnected', color: 'text-red-400', icon: '🔴' };
      default:
        return { text: 'Unknown', color: 'text-gray-400', icon: '⚫' };
    }
  };

  const status = getConnectionStatus();

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-3">
          <div className="text-2xl">🏟️</div>
          <div>
            <h1 className="text-xl font-bold text-white">Smart Stadium</h1>
            <p className="text-sm text-gray-400">Live Game Dashboard</p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center space-x-4">
          {/* API Health */}
          {systemHealth && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">API:</span>
              <span className={`text-xs font-medium ${
                systemHealth.api_status === 'healthy' ? 'text-green-400' :
                systemHealth.api_status === 'degraded' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {systemHealth.api_status.toUpperCase()}
              </span>
            </div>
          )}

          {/* WebSocket Connection */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Live:</span>
            <span className={`text-xs font-medium ${status.color}`}>
              {status.icon} {status.text}
            </span>
          </div>

          {/* Active Celebrations Count */}
          {systemHealth?.active_celebrations !== undefined && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">Active:</span>
              <span className="text-xs font-medium text-blue-400">
                {systemHealth.active_celebrations} 🎉
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;