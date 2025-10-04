import React, { useState, useEffect } from 'react';
import { Device } from '../../types';
import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';
import apiService from '../../services/api';

interface DeviceStatusGridProps {
  className?: string;
}

const DeviceStatusGrid: React.FC<DeviceStatusGridProps> = ({ className }) => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingDevice, setTestingDevice] = useState<string | null>(null);
  const [discovering, setDiscovering] = useState(false);

  useEffect(() => {
    loadDevices();
    
    // Refresh devices every 10 seconds
    const interval = setInterval(loadDevices, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadDevices = async () => {
    try {
      const deviceList = await apiService.getDevices();
      setDevices(deviceList);
      setError(null);
    } catch (err) {
      setError(apiService.handleError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleTestDevice = async (deviceId: string) => {
    setTestingDevice(deviceId);
    try {
      await apiService.testDevice(deviceId);
      // Refresh devices to get updated status
      await loadDevices();
    } catch (error) {
      console.error('Device test failed:', error);
    } finally {
      setTestingDevice(null);
    }
  };

  const handleDiscoverDevices = async () => {
    setDiscovering(true);
    try {
      await apiService.discoverDevices();
      await loadDevices();
    } catch (error) {
      console.error('Device discovery failed:', error);
    } finally {
      setDiscovering(false);
    }
  };

  const getDeviceStatusColor = (device: Device) => {
    if (!device.is_online) return 'bg-red-500';
    
    const lastSeen = new Date(device.last_seen);
    const now = new Date();
    const minutesAgo = (now.getTime() - lastSeen.getTime()) / (1000 * 60);
    
    if (minutesAgo < 2) return 'bg-green-500';
    if (minutesAgo < 10) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getDeviceStatusBadge = (device: Device) => {
    if (!device.is_online) return { variant: 'danger' as const, text: 'Offline' };
    
    const lastSeen = new Date(device.last_seen);
    const now = new Date();
    const minutesAgo = (now.getTime() - lastSeen.getTime()) / (1000 * 60);
    
    if (minutesAgo < 2) return { variant: 'success' as const, text: 'Online' };
    if (minutesAgo < 10) return { variant: 'warning' as const, text: 'Stale' };
    return { variant: 'danger' as const, text: 'Timeout' };
  };

  const getDeviceTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'wiz': return '💡';
      case 'lifx': return '🌈';
      case 'hue': return '🎨';
      default: return '🔌';
    }
  };

  const formatLastSeen = (lastSeen: string) => {
    const date = new Date(lastSeen);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const onlineDevices = devices.filter(d => d.is_online).length;
  const totalDevices = devices.length;

  if (loading) {
    return (
      <Card className={className}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-700 rounded w-1/3" />
          <div className="grid grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white flex items-center">
            💡 Smart Devices
          </h2>
          <div className="flex items-center space-x-2">
            <Badge 
              variant={onlineDevices === totalDevices ? 'success' : onlineDevices > 0 ? 'warning' : 'danger'}
              size="sm"
            >
              {onlineDevices}/{totalDevices} Online
            </Badge>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="p-3 bg-red-900/30 border border-red-500/50 rounded-lg">
            <div className="text-red-400 text-sm">{error}</div>
          </div>
        )}

        {/* Empty State */}
        {devices.length === 0 && !loading && (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-white mb-2">No Devices Found</h3>
            <p className="text-gray-400 mb-4">Discover smart lights on your network</p>
            <Button 
              onClick={handleDiscoverDevices}
              isLoading={discovering}
              variant="primary"
            >
              🔍 Discover Devices
            </Button>
          </div>
        )}

        {/* Device Grid */}
        {devices.length > 0 && (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-4 p-4 bg-gray-700 rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{onlineDevices}</div>
                <div className="text-xs text-gray-400">Online</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">{totalDevices - onlineDevices}</div>
                <div className="text-xs text-gray-400">Offline</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">{totalDevices}</div>
                <div className="text-xs text-gray-400">Total</div>
              </div>
            </div>

            {/* Device Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {devices.map((device) => {
                const statusBadge = getDeviceStatusBadge(device);
                const isTesting = testingDevice === device.id;
                
                return (
                  <div 
                    key={device.id}
                    className="p-4 bg-gray-700 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors"
                  >
                    {/* Device Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{getDeviceTypeIcon(device.type)}</span>
                        <div>
                          <h3 className="font-medium text-white text-sm">{device.name}</h3>
                          <p className="text-xs text-gray-400">{device.type.toUpperCase()}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <div 
                          className={`w-2 h-2 rounded-full ${getDeviceStatusColor(device)}`}
                        />
                        <Badge variant={statusBadge.variant} size="sm">
                          {statusBadge.text}
                        </Badge>
                      </div>
                    </div>
                    
                    {/* Device Info */}
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">IP:</span>
                        <span className="text-white font-mono">{device.ip_address}</span>
                      </div>
                      
                      {device.room && (
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Room:</span>
                          <span className="text-white">{device.room}</span>
                        </div>
                      )}
                      
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">Last Seen:</span>
                        <span className="text-white">{formatLastSeen(device.last_seen)}</span>
                      </div>
                      
                      {device.is_online && (
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Brightness:</span>
                          <span className="text-white">{device.current_state.brightness}%</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Current Color */}
                    {device.is_online && (
                      <div className="flex items-center space-x-2 mb-3">
                        <span className="text-xs text-gray-400">Color:</span>
                        <div 
                          className="w-4 h-4 rounded border border-gray-500"
                          style={{
                            backgroundColor: `rgb(${device.current_state.color.r}, ${device.current_state.color.g}, ${device.current_state.color.b})`
                          }}
                        />
                        <span className="text-xs text-white font-mono">
                          rgb({device.current_state.color.r}, {device.current_state.color.g}, {device.current_state.color.b})
                        </span>
                      </div>
                    )}
                    
                    {/* Device Actions */}
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant={device.is_online ? "secondary" : "danger"}
                        onClick={() => handleTestDevice(device.id)}
                        isLoading={isTesting}
                        className="flex-1"
                      >
                        {device.is_online ? '🧪 Test' : '🔄 Retry'}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Actions */}
            <div className="flex space-x-3 pt-4 border-t border-gray-700">
              <Button
                variant="secondary"
                size="sm"
                onClick={loadDevices}
                leftIcon={<span>🔄</span>}
              >
                Refresh
              </Button>
              
              <Button
                variant="primary"
                size="sm"
                onClick={handleDiscoverDevices}
                isLoading={discovering}
                leftIcon={<span>🔍</span>}
              >
                Discover New
              </Button>
            </div>
          </>
        )}
      </div>
    </Card>
  );
};

export default DeviceStatusGrid;