import { Card } from './Card';
import { Loader } from './feedback/Loader';
import { useCelebrationHistory } from '../hooks/useCelebrationsHistory';
import { formatTimestamp, fromNow } from '../lib/time';

export const HistoryPanel = () => {
  const { data, isLoading, isError, refetch } = useCelebrationHistory(30);

  return (
    <Card title="Recent celebrations" subtitle="Last 30 events">
      {isLoading ? (
        <div className="panel-empty">
          <Loader />
          <span>Loading history…</span>
        </div>
      ) : null}
      {isError ? (
        <div className="panel-empty panel-empty--error">
          <span>Could not load history.</span>
          <button type="button" onClick={() => refetch()}>
            Retry
          </button>
        </div>
      ) : null}
      {!isLoading && !isError && data && data.length === 0 ? (
        <div className="panel-empty">
          <span>No celebrations recorded yet.</span>
        </div>
      ) : null}
      {!isLoading && !isError && data ? (
        <ul className="history-list">
          {data.map((item) => (
            <li key={item.id}>
              <div className="history-list__primary">
                <span className="history-list__tag">{item.sport?.toUpperCase() ?? 'MANUAL'}</span>
                <span className="history-list__event">{item.event_type ?? 'event'}</span>
                <span className="history-list__team">{item.team ?? '—'}</span>
              </div>
              <div className="history-list__secondary">
                <span>{item.detail ?? item.game_id ?? ''}</span>
                <span>{formatTimestamp(item.timestamp)}</span>
                <span>{fromNow(item.timestamp)}</span>
              </div>
            </li>
          ))}
        </ul>
      ) : null}
    </Card>
  );
};
