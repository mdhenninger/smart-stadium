import { Card } from './Card';
import type { LiveEventMessage } from '../types';

interface LiveFeedProps {
  events: LiveEventMessage[];
}

const renderEvent = (event: LiveEventMessage) => {
  switch (event.type) {
    case 'celebration':
      return `Score: ${event.team} +${event.delta}`;
    case 'victory':
      return `Victory: ${event.winner} (${event.final})`;
    default:
      return event.type;
  }
};

const sportLabel = (event: LiveEventMessage): string => {
  const sport = (event as { sport?: unknown }).sport;
  return typeof sport === 'string' ? sport.toUpperCase() : '—';
};

export const LiveFeed = ({ events }: LiveFeedProps) => {
  return (
    <Card title="Live feed" subtitle="Real-time events">
      {events.length === 0 ? (
        <p className="live-feed__empty">Waiting for real-time events…</p>
      ) : (
        <ul className="live-feed__list">
          {events.map((event, index) => {
            const gameId = (event as { gameId?: unknown }).gameId;
            return (
              <li key={index}>
                <span className="live-feed__sport">{sportLabel(event)}</span>
                <span>{renderEvent(event)}</span>
                {typeof gameId === 'string' ? <span className="live-feed__game">{gameId}</span> : null}
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
};
