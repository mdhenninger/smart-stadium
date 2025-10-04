import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { ApiProvider } from './contexts/ApiContext';
import ErrorBoundary from './components/UI/ErrorBoundary';
import DashboardErrorBoundary from './components/Dashboard/DashboardErrorBoundary';
import { apiConfig, appInfo } from './config/env';

// Page imports
import AppLaunch from './pages/AppLaunch';
import SportSelection from './pages/SportSelection';
import GameSelection from './pages/GameSelection';
import LiveDashboard from './pages/LiveDashboard';
import Help from './pages/Help';
import Settings from './pages/Settings';

// Component imports
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);

  // Check API health on startup
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const response = await fetch(`${apiConfig.baseUrl}/health`);
        setApiHealth(response.ok);
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealth(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkApiHealth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <LoadingSpinner size="large" message="Connecting to Smart Stadium..." />
      </div>
    );
  }

  if (apiHealth === false) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-400 mb-4">
            🚨 Connection Error
          </h1>
          <p className="text-gray-300 mb-6">
            Cannot connect to Smart Stadium API. Please ensure the backend server is running.
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn-primary"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // Log to external service in production
        if (appInfo.isProduction) {
          console.error('Production Error:', { error, errorInfo, version: appInfo.version });
          // Here you could send to error tracking service like Sentry
        }
      }}
    >
      <ApiProvider>
        <WebSocketProvider>
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<AppLaunch />} />
                <Route path="/sport" element={<SportSelection />} />
                <Route path="/games" element={<GameSelection />} />
                <Route 
                  path="/dashboard/:gameId?" 
                  element={
                    <DashboardErrorBoundary>
                      <LiveDashboard />
                    </DashboardErrorBoundary>
                  } 
                />
                <Route path="/help" element={<Help />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          </Router>
        </WebSocketProvider>
      </ApiProvider>
    </ErrorBoundary>
  );
}

export default App;