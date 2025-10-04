import { Component, ErrorInfo, ReactNode } from 'react';
import Card from './Card';
import Button from './Button';
import { appInfo } from '../../config/env';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console and call optional error handler
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Call optional error handler prop
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <Card className="max-w-2xl mx-auto mt-8">
          <div className="text-center space-y-6">
            {/* Error Icon */}
            <div className="text-6xl text-red-400">
              ⚠️
            </div>
            
            {/* Error Title */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Oops! Something went wrong
              </h2>
              <p className="text-gray-400">
                We encountered an unexpected error. Please try refreshing the page or contact support if the problem persists.
              </p>
            </div>

            {/* Error Details (Development Only) */}
            {appInfo.isDevelopment && this.state.error && (
              <div className="text-left">
                <details className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                  <summary className="text-yellow-400 font-medium cursor-pointer mb-2">
                    🔍 Error Details (Development)
                  </summary>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-red-400 font-medium">Error:</span>
                      <pre className="text-gray-300 mt-1 whitespace-pre-wrap">
                        {this.state.error.message}
                      </pre>
                    </div>
                    
                    {this.state.error.stack && (
                      <div>
                        <span className="text-red-400 font-medium">Stack Trace:</span>
                        <pre className="text-gray-300 mt-1 text-xs whitespace-pre-wrap overflow-x-auto">
                          {this.state.error.stack}
                        </pre>
                      </div>
                    )}
                    
                    {this.state.errorInfo?.componentStack && (
                      <div>
                        <span className="text-red-400 font-medium">Component Stack:</span>
                        <pre className="text-gray-300 mt-1 text-xs whitespace-pre-wrap overflow-x-auto">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button 
                variant="primary" 
                onClick={this.handleReset}
                className="min-w-32"
              >
                🔄 Try Again
              </Button>
              
              <Button 
                variant="secondary" 
                onClick={() => window.location.reload()}
                className="min-w-32"
              >
                🔃 Refresh Page
              </Button>
              
              <Button 
                variant="secondary" 
                onClick={() => window.location.href = '/'}
                className="min-w-32"
              >
                🏠 Go Home
              </Button>
            </div>

            {/* Support Information */}
            <div className="text-sm text-gray-500">
              <p>Error ID: {Date.now().toString(36)}</p>
              <p>Time: {new Date().toLocaleString()}</p>
              <p>Version: {appInfo.version}</p>
            </div>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;