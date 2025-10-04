import { Loader } from './feedback/Loader';
import { useSystemStatus } from '../hooks/useSystemStatus';
import { formatUptime } from '../lib/time';
import type { ConnectionStatus } from '../hooks/useLiveEvents';

interface StatusBarProps {
  connectionStatus: ConnectionStatus;
}

const connectionCopy: Record<ConnectionStatus, string> = {
  connecting: 'Connecting…',
  open: 'Live updates',
  closed: 'Disconnected',
  error: 'Connection error',
};

export const StatusBar = ({ connectionStatus }: StatusBarProps) => {
  const { data, isLoading, isError, refetch } = useSystemStatus();

  if (isLoading) {
    return (
      <div className="status-bar">
        <Loader size="small" />
        <span>Loading stadium status…</span>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="status-bar status-bar--error">
        <span>Failed to load system status.</span>
        <button onClick={() => refetch()} type="button">
          Retry
        </button>
      </div>
    );
  }

  const deviceSummary = `${data.online_devices}/${data.total_devices} online`;

  return (
    <div className="status-bar">
      <div className="status-bar__cluster">
        <strong>Environment:</strong>
        <span>{data.environment}</span>
      </div>
      <div className="status-bar__cluster">
        <strong>Uptime:</strong>
        <span>{formatUptime(data.uptime_seconds)}</span>
      </div>
      <div className="status-bar__cluster">
        <strong>Devices:</strong>
        <span>{deviceSummary}</span>
      </div>
      <div className="status-bar__cluster">
        <span className={connectionStatus === 'open' ? 'status-pill status-pill--ok' : 'status-pill status-pill--warn'}>
          {connectionCopy[connectionStatus]}
        </span>
      </div>
    </div>
  );
};
