import { Component, ErrorInfo, ReactNode } from 'react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';
import { appInfo } from '../../config/env';

interface Props {
  children: ReactNode;
  gameId?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
  retryCount: number;
}

class DashboardErrorBoundary extends Component<Props, State> {
  private maxRetries = 3;
  
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, retryCount: 0 };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
    
    // Track dashboard-specific errors
    console.group('🏈 Dashboard Error Details');
    console.error('Game ID:', this.props.gameId);
    console.error('Error:', error.message);
    console.error('Component Stack:', errorInfo.componentStack);
    console.groupEnd();
  }

  handleRetry = () => {
    const newRetryCount = this.state.retryCount + 1;
    
    if (newRetryCount <= this.maxRetries) {
      this.setState({ 
        hasError: false, 
        error: undefined, 
        retryCount: newRetryCount 
      });
    }
  };

  handleReset = () => {
    this.setState({ 
      hasError: false, 
      error: undefined, 
      retryCount: 0 
    });
  };

  render() {
    if (this.state.hasError) {
      const canRetry = this.state.retryCount < this.maxRetries;
      
      return (
        <div className="min-h-screen bg-gray-900">
          {/* Dashboard Header */}
          <div className="bg-gray-800 border-b border-gray-700">
            <div className="max-w-7xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">
                  🏈 Smart Stadium Dashboard
                </h1>
                <Badge variant="danger" size="sm">
                  ⚠️ Error
                </Badge>
              </div>
            </div>
          </div>
          
          {/* Error Content */}
          <div className="max-w-4xl mx-auto p-6">
            <Card className="text-center space-y-6">
              {/* Error Icon */}
              <div className="text-6xl text-red-400">
                🚨
              </div>
              
              {/* Error Message */}
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Dashboard Error
                </h2>
                <p className="text-gray-400">
                  The live dashboard encountered an error and couldn't load properly.
                  {this.props.gameId && (
                    <span className="block mt-2 text-sm">
                      Game ID: <code className="bg-gray-700 px-2 py-1 rounded">{this.props.gameId}</code>
                    </span>
                  )}
                </p>
              </div>

              {/* Retry Information */}
              {this.state.retryCount > 0 && (
                <div className="bg-yellow-900/20 border border-yellow-600/50 rounded-lg p-4">
                  <p className="text-yellow-400 text-sm">
                    Retry attempt {this.state.retryCount} of {this.maxRetries}
                  </p>
                </div>
              )}

              {/* Error Details (Development) */}
              {appInfo.isDevelopment && this.state.error && (
                <div className="text-left">
                  <details className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                    <summary className="text-yellow-400 font-medium cursor-pointer mb-2">
                      🔍 Technical Details
                    </summary>
                    <pre className="text-gray-300 text-sm whitespace-pre-wrap overflow-x-auto">
                      {this.state.error.message}
                    </pre>
                  </details>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                {canRetry && (
                  <Button 
                    variant="primary" 
                    onClick={this.handleRetry}
                    className="min-w-32"
                  >
                    🔄 Retry ({this.maxRetries - this.state.retryCount} left)
                  </Button>
                )}
                
                <Button 
                  variant="secondary" 
                  onClick={this.handleReset}
                  className="min-w-32"
                >
                  🔃 Reset Dashboard
                </Button>
                
                <Button 
                  variant="secondary" 
                  onClick={() => window.location.href = '/games'}
                  className="min-w-32"
                >
                  📅 Back to Games
                </Button>
                
                <Button 
                  variant="secondary" 
                  onClick={() => window.location.href = '/'}
                  className="min-w-32"
                >
                  🏠 Home
                </Button>
              </div>

              {/* Troubleshooting Tips */}
              <div className="bg-blue-900/20 border border-blue-600/50 rounded-lg p-4 text-left">
                <h3 className="text-blue-400 font-medium mb-2">💡 Troubleshooting Tips</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Check your internet connection</li>
                  <li>• Ensure the backend API is running</li>
                  <li>• Try refreshing the page</li>
                  <li>• Clear browser cache if issues persist</li>
                </ul>
              </div>
            </Card>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default DashboardErrorBoundary;