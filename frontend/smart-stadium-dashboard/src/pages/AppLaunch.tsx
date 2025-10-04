import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../contexts/ApiContext';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const AppLaunch: React.FC = () => {
  const navigate = useNavigate();
  const { systemHealth, isLoading } = useApi();

  useEffect(() => {
    // Auto-navigate after 3 seconds if system is healthy
    if (!isLoading && systemHealth?.api_status === 'healthy') {
      const timer = setTimeout(() => {
        navigate('/sport');
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [isLoading, systemHealth, navigate]);

  const handleGetStarted = () => {
    navigate('/sport');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" message="Initializing Smart Stadium..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <div className="text-center max-w-2xl mx-auto px-6">
        {/* Logo */}
        <div className="mb-8">
          <div className="text-8xl mb-4">🏟️</div>
          <h1 className="text-5xl font-bold text-white mb-4">
            Smart Stadium
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Real-time NFL Game Monitoring & Smart Lighting Control
          </p>
        </div>

        {/* System Status */}
        <div className="mb-8 p-6 bg-gray-800 rounded-lg border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">System Status</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">API Status:</span>
              <span className={`font-medium ${
                systemHealth?.api_status === 'healthy' ? 'text-green-400' :
                systemHealth?.api_status === 'degraded' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {systemHealth?.api_status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Database:</span>
              <span className={`font-medium ${
                systemHealth?.database_status === 'connected' ? 'text-green-400' : 'text-red-400'
              }`}>
                {systemHealth?.database_status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Devices:</span>
              <span className="text-blue-400 font-medium">
                {systemHealth?.device_health.responsive_devices || 0} / {systemHealth?.device_health.total_devices || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">WebSocket:</span>
              <span className="text-blue-400 font-medium">
                {systemHealth?.websocket_connections || 0} connections
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-4">
          <button
            onClick={handleGetStarted}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200"
          >
            🚀 Get Started
          </button>
          
          <p className="text-sm text-gray-400">
            {systemHealth?.api_status === 'healthy' 
              ? 'System ready! Redirecting automatically in 3 seconds...'
              : 'Please check system status before proceeding'
            }
          </p>
        </div>

        {/* Feature Highlights */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div className="text-center">
            <div className="text-2xl mb-2">🏈</div>
            <h3 className="font-semibold text-white mb-1">Live Game Data</h3>
            <p className="text-gray-400">Real-time scores and field position</p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">💡</div>
            <h3 className="font-semibold text-white mb-1">Smart Lighting</h3>
            <p className="text-gray-400">Automated team celebrations</p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-white mb-1">Live Dashboard</h3>
            <p className="text-gray-400">Team Tracker-inspired interface</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppLaunch;