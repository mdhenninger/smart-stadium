import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { Dashboard } from '../components/Dashboard';

const LiveDashboard: React.FC = () => {
  const { gameId } = useParams<{ gameId?: string }>();

  // Redirect to game selection if no game ID
  if (!gameId) {
    return <Navigate to="/games" replace />;
  }

  return <Dashboard gameId={gameId} />;
};

export default LiveDashboard;