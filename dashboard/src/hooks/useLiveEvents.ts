import { useEffect, useMemo, useRef, useState } from 'react';
import { WS_URL } from '../lib/config';
import type { LiveEventMessage } from '../types';

export type ConnectionStatus = 'connecting' | 'open' | 'closed' | 'error';

interface LiveEventsState {
  events: LiveEventMessage[];
  status: ConnectionStatus;
}

const MAX_EVENTS = 50;
const RECONNECT_BASE_DELAY = 2000;
const RECONNECT_MAX_DELAY = 15000;

export const useLiveEvents = (): LiveEventsState => {
  const [events, setEvents] = useState<LiveEventMessage[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>('connecting');
  const retryRef = useRef(0);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let isUnmounted = false;

    const connect = () => {
      console.log('[WebSocket] Connecting to:', WS_URL);
      setStatus('connecting');
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        if (isUnmounted) {
          return;
        }
        console.log('[WebSocket] Connected successfully');
        retryRef.current = 0;
        setStatus('open');
      };

      ws.onmessage = (event) => {
        if (isUnmounted) {
          return;
        }
        try {
          const data = JSON.parse(event.data) as LiveEventMessage;
          // Ignore ping messages
          if (data.type === 'ping') {
            console.log('[WebSocket] Received ping');
            return;
          }
          console.log('[WebSocket] Received event:', data.type);
          setEvents((prev) => [data, ...prev].slice(0, MAX_EVENTS));
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error, event.data);
        }
      };

      ws.onerror = (error) => {
        if (isUnmounted) {
          return;
        }
        console.error('[WebSocket] Error:', error);
        setStatus('error');
      };

      ws.onclose = (event) => {
        if (isUnmounted) {
          return;
        }
        console.log('[WebSocket] Closed:', event.code, event.reason);
        setStatus('closed');
        retry();
      };
    };

    const retry = () => {
      const attempt = retryRef.current + 1;
      retryRef.current = attempt;
      const delay = Math.min(RECONNECT_BASE_DELAY * attempt, RECONNECT_MAX_DELAY);
      window.setTimeout(() => {
        if (!isUnmounted) {
          connect();
        }
      }, delay);
    };

    connect();

    return () => {
      isUnmounted = true;
      ws?.close();
    };
  }, []);

  return useMemo(() => ({ events, status }), [events, status]);
};
