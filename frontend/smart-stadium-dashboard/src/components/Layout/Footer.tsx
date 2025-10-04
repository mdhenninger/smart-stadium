import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 border-t border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between text-sm text-gray-400">
        <div className="flex items-center space-x-4">
          <span>© 2025 Smart Stadium Dashboard</span>
          <span>•</span>
          <span>Real-time NFL Game Monitoring</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>Built with React + FastAPI</span>
          <span>•</span>
          <span className="text-blue-400">v1.0.0</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;