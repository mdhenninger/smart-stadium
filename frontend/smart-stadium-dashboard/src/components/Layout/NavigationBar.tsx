import React from 'react';
import { NavLink } from 'react-router-dom';
import { useWebSocket } from '../../contexts/WebSocketContext';

interface NavItem {
  path: string;
  label: string;
  icon: string;
  badge?: number;
}

const NavigationBar: React.FC = () => {
  const { gameUpdates } = useWebSocket();

  const navItems: NavItem[] = [
    { path: '/sport', label: 'Sports', icon: '🏈' },
    { path: '/games', label: 'Games', icon: '📅', badge: gameUpdates.length },
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
    { path: '/help', label: 'Help', icon: '❓' },
  ];

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="px-4">
        <div className="flex space-x-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `relative flex items-center space-x-2 px-4 py-3 text-sm font-medium transition-colors duration-200 ${
                  isActive
                    ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-700'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {item.badge > 99 ? '99+' : item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default NavigationBar;