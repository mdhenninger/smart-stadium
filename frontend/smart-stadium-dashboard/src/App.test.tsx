import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';

// Mock fetch for API health check
const mockFetch = vi.fn();
Object.defineProperty(globalThis, 'fetch', {
  value: mockFetch,
  writable: true,
});

// Mock the contexts to avoid dependency issues
vi.mock('./contexts/WebSocketContext', () => ({
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('./contexts/ApiContext', () => ({
  ApiProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock page components
vi.mock('./pages/AppLaunch', () => ({
  default: () => <div>App Launch Page</div>,
}));

vi.mock('./pages/SportSelection', () => ({
  default: () => <div>Sport Selection Page</div>,
}));

vi.mock('./pages/GameSelection', () => ({
  default: () => <div>Game Selection Page</div>,
}));

vi.mock('./pages/LiveDashboard', () => ({
  default: () => <div>Live Dashboard Page</div>,
}));

vi.mock('./pages/Help', () => ({
  default: () => <div>Help Page</div>,
}));

vi.mock('./pages/Settings', () => ({
  default: () => <div>Settings Page</div>,
}));

// Mock Layout component
vi.mock('./components/Layout/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="layout">
      <header>Smart Stadium Header</header>
      <main>{children}</main>
      <footer>Smart Stadium Footer</footer>
    </div>
  ),
}));

// Mock LoadingSpinner
vi.mock('./components/UI/LoadingSpinner', () => ({
  default: ({ message }: { message?: string }) => (
    <div data-testid="loading-spinner">{message || 'Loading...'}</div>
  ),
}));

describe('App', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('shows loading spinner initially', () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<App />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Connecting to Smart Stadium...')).toBeInTheDocument();
  });

  it('shows connection error when API health check fails', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('🚨 Connection Error')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Cannot connect to Smart Stadium API/)).toBeInTheDocument();
    expect(screen.getByText('Retry Connection')).toBeInTheDocument();
  });

  it('renders main app when API health check succeeds', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: 'healthy' }),
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('layout')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Smart Stadium Header')).toBeInTheDocument();
    expect(screen.getByText('App Launch Page')).toBeInTheDocument();
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  });

  it('shows connection error when API returns non-ok status', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('🚨 Connection Error')).toBeInTheDocument();
    });
  });
});