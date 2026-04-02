'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import type { WSMessage } from '@/lib/types';

interface UseWebSocketOptions {
  onMessage: (msg: WSMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  autoReconnect?: boolean;
}

export function useWebSocket(url: string | null, options: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeout = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!url) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      options.onOpen?.();
    };

    ws.onclose = () => {
      setIsConnected(false);
      options.onClose?.();
      if (options.autoReconnect !== false) {
        reconnectTimeout.current = setTimeout(connect, 3000);
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as WSMessage;
        options.onMessage(msg);
      } catch {
        console.error('Failed to parse WS message');
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [url, options]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((msg: WSMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return { isConnected, sendMessage };
}
