import React, { useState } from 'react';
import { useApi } from '../contexts/ApiContext';
import { UserPreferences } from '../types';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Settings: React.FC = () => {
  const { preferences, updatePreferences, isLoading } = useApi();
  const [localPreferences, setLocalPreferences] = useState<UserPreferences | null>(preferences);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handlePreferenceChange = (key: keyof UserPreferences, value: any) => {
    if (!localPreferences) return;
    
    const updated = { ...localPreferences, [key]: value };
    setLocalPreferences(updated);
    setHasChanges(true);
  };

  const handleNestedPreferenceChange = (
    parentKey: keyof UserPreferences, 
    childKey: string, 
    value: any
  ) => {
    if (!localPreferences) return;
    
    const parentObj = localPreferences[parentKey] as Record<string, any>;
    const updated = {
      ...localPreferences,
      [parentKey]: {
        ...parentObj,
        [childKey]: value
      }
    };
    setLocalPreferences(updated);
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!localPreferences || !hasChanges) return;
    
    setSaving(true);
    try {
      await updatePreferences(localPreferences);
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setLocalPreferences(preferences);
    setHasChanges(false);
  };

  if (isLoading || !localPreferences) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" message="Loading settings..." />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Settings</h1>
        <p className="text-xl text-gray-400">Configure your Smart Stadium experience</p>
        {hasChanges && (
          <div className="mt-4">
            <Badge variant="warning">Unsaved Changes</Badge>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* General Preferences */}
        <Card>
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            ⚙️ General Preferences
          </h2>
          
          <div className="space-y-6">
            {/* Favorite Team */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Favorite Team
              </label>
              <select 
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={localPreferences.favorite_team || ''}
                onChange={(e) => handlePreferenceChange('favorite_team', e.target.value || undefined)}
              >
                <option value="">Select a team...</option>
                <option value="buffalo-bills">Buffalo Bills</option>
                <option value="dallas-cowboys">Dallas Cowboys</option>
                <option value="green-bay-packers">Green Bay Packers</option>
                <option value="kansas-city-chiefs">Kansas City Chiefs</option>
                <option value="new-england-patriots">New England Patriots</option>
                {/* Add more teams as needed */}
              </select>
            </div>

            {/* Celebration Intensity */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Celebration Intensity
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['low', 'medium', 'high'].map((intensity) => (
                  <button
                    key={intensity}
                    className={`p-3 rounded-lg border transition-all duration-200 ${
                      localPreferences.celebration_intensity === intensity
                        ? 'bg-blue-600 border-blue-500 text-white'
                        : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                    }`}
                    onClick={() => handlePreferenceChange('celebration_intensity', intensity as 'low' | 'medium' | 'high')}
                  >
                    <div className="text-center">
                      <div className="text-lg mb-1">
                        {intensity === 'low' ? '🔅' : intensity === 'medium' ? '💡' : '✨'}
                      </div>
                      <div className="text-sm font-medium capitalize">{intensity}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Auto Celebrations */}
            <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
              <div>
                <h3 className="font-medium text-white">Automatic Celebrations</h3>
                <p className="text-sm text-gray-400">
                  Trigger celebrations automatically when your team scores
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={localPreferences.auto_celebrations}
                  onChange={(e) => handlePreferenceChange('auto_celebrations', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Theme */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Theme
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { value: 'dark', label: 'Dark', icon: '🌙' },
                  { value: 'light', label: 'Light', icon: '☀️' },
                  { value: 'auto', label: 'Auto', icon: '🔄' }
                ].map((theme) => (
                  <button
                    key={theme.value}
                    className={`p-3 rounded-lg border transition-all duration-200 ${
                      localPreferences.theme === theme.value
                        ? 'bg-blue-600 border-blue-500 text-white'
                        : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                    }`}
                    onClick={() => handlePreferenceChange('theme', theme.value as 'dark' | 'light' | 'auto')}
                  >
                    <div className="text-center">
                      <div className="text-lg mb-1">{theme.icon}</div>
                      <div className="text-sm font-medium">{theme.label}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Notifications */}
        <Card>
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            🔔 Notifications
          </h2>
          
          <div className="space-y-4">
            {[
              { key: 'game_updates', label: 'Game Updates', description: 'Score changes, quarter updates, etc.' },
              { key: 'celebration_complete', label: 'Celebration Complete', description: 'When a celebration finishes' },
              { key: 'device_issues', label: 'Device Issues', description: 'Device connectivity problems' }
            ].map((setting) => (
              <div key={setting.key} className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div>
                  <h3 className="font-medium text-white">{setting.label}</h3>
                  <p className="text-sm text-gray-400">{setting.description}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localPreferences.notification_settings[setting.key as keyof typeof localPreferences.notification_settings]}
                    onChange={(e) => handleNestedPreferenceChange('notification_settings', setting.key, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            ))}
          </div>
        </Card>

        {/* Dashboard Layout */}
        <Card>
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            📊 Dashboard Layout
          </h2>
          
          <div className="space-y-4">
            {[
              { key: 'show_field_position', label: 'Show Field Position', description: 'Display field position visualization' },
              { key: 'show_device_grid', label: 'Show Device Grid', description: 'Display device status grid' }
            ].map((setting) => (
              <div key={setting.key} className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div>
                  <h3 className="font-medium text-white">{setting.label}</h3>
                  <p className="text-sm text-gray-400">{setting.description}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localPreferences.dashboard_layout[setting.key as keyof typeof localPreferences.dashboard_layout] as boolean}
                    onChange={(e) => handleNestedPreferenceChange('dashboard_layout', setting.key, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            ))}

            {/* Refresh Interval */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Refresh Interval (seconds)
              </label>
              <select 
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={localPreferences.dashboard_layout.refresh_interval}
                onChange={(e) => handleNestedPreferenceChange('dashboard_layout', 'refresh_interval', parseInt(e.target.value))}
              >
                <option value={1000}>1 second</option>
                <option value={5000}>5 seconds</option>
                <option value={10000}>10 seconds</option>
                <option value={30000}>30 seconds</option>
                <option value={60000}>1 minute</option>
              </select>
            </div>
          </div>
        </Card>

        {/* System Info */}
        <Card>
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            ℹ️ System Information
          </h2>
          
          <div className="space-y-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Version:</span>
              <span className="text-white font-mono">v1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Build:</span>
              <span className="text-white font-mono">2025.10.02</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">API Status:</span>
              <Badge variant="success" size="sm">Connected</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">WebSocket:</span>
              <Badge variant="success" size="sm">Connected</Badge>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-700">
            <Button variant="ghost" size="sm" fullWidth>
              📊 View API Documentation
            </Button>
          </div>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4 mt-8">
        <Button
          variant="secondary"
          size="lg"
          onClick={handleReset}
          disabled={!hasChanges || saving}
        >
          Reset Changes
        </Button>
        
        <Button
          variant="primary"
          size="lg"
          onClick={handleSave}
          disabled={!hasChanges}
          isLoading={saving}
        >
          Save Settings
        </Button>
      </div>
    </div>
  );
};

export default Settings;