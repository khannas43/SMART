import { useEffect, useRef, useState, useCallback } from 'react';
import { Client, IMessage } from '@stomp/stompjs';
import SockJS from 'sockjs-client';
import { useAppSelector } from '@/store/hooks';

interface UseWebSocketOptions {
  topics: string[];
  onMessage?: (message: any) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  autoConnect?: boolean;
}

interface UseWebSocketReturn {
  client: Client | null;
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (destination: string, body: any) => void;
}

export const useWebSocket = (options: UseWebSocketOptions): UseWebSocketReturn => {
  const { topics, onMessage, onError, onConnect, onDisconnect, autoConnect = true } = options;
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const [isConnected, setIsConnected] = useState(false);
  const clientRef = useRef<Client | null>(null);
  const subscriptionsRef = useRef<Array<{ unsubscribe: () => void }>>([]);

  const connect = useCallback(() => {
    if (!isAuthenticated) {
      console.warn('Cannot connect WebSocket: User not authenticated');
      return;
    }

    if (clientRef.current?.active) {
      console.log('WebSocket already connected');
      return;
    }

    // Get token from localStorage
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.warn('Cannot connect WebSocket: No token found');
      return;
    }

    // Create SockJS connection
    // Note: The backend context path is /citizen/api/v1, so WebSocket endpoint is at /ws
    // For production, this should use the same origin or be configured via environment variable
    const wsUrl = import.meta.env.VITE_WS_URL || 'http://localhost:8081/citizen/api/v1/ws';
    const socket = new SockJS(wsUrl);
    
    // Create STOMP client
    const client = new Client({
      webSocketFactory: () => socket,
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      debug: (str) => {
        if (process.env.NODE_ENV === 'development') {
          console.log('STOMP:', str);
        }
      },
      onConnect: () => {
        console.log('WebSocket connected');
        setIsConnected(true);

        // Subscribe to all topics
        subscriptionsRef.current = topics.map((topic) => {
          const subscription = client.subscribe(topic, (message: IMessage) => {
            try {
              const data = JSON.parse(message.body);
              onMessage?.(data);
            } catch (error) {
              console.error('Error parsing WebSocket message:', error);
            }
          });
          return { unsubscribe: subscription.unsubscribe };
        });

        onConnect?.();
      },
      onStompError: (frame) => {
        console.error('STOMP error:', frame);
        setIsConnected(false);
        onError?.(new Error(frame.headers['message'] || 'STOMP error') as any);
      },
      onWebSocketClose: () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        subscriptionsRef.current = [];
        onDisconnect?.();
      },
      onWebSocketError: (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        onError?.(error);
      },
    });

    // Add authorization header if token exists
    if (token) {
      client.configure({
        connectHeaders: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    client.activate();
    clientRef.current = client;
  }, [isAuthenticated, topics, onMessage, onError, onConnect, onDisconnect]);

  const disconnect = useCallback(() => {
    // Unsubscribe from all topics
    subscriptionsRef.current.forEach((sub) => sub.unsubscribe());
    subscriptionsRef.current = [];

    // Deactivate client
    if (clientRef.current) {
      clientRef.current.deactivate();
      clientRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((destination: string, body: any) => {
    if (!clientRef.current?.active) {
      console.warn('Cannot send message: WebSocket not connected');
      return;
    }

    clientRef.current.publish({
      destination,
      body: JSON.stringify(body),
    });
  }, []);

  useEffect(() => {
    if (autoConnect && isAuthenticated) {
      connect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect, isAuthenticated]);

  return {
    client: clientRef.current,
    isConnected,
    connect,
    disconnect,
    sendMessage,
  };
};

