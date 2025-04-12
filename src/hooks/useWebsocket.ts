import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAuth } from "./useAuth";
import WS_BASE_URL from "@/lib/constants";

interface UseWebSocketOptions {
  channel: string;
  autoConnect?: boolean;
  onMessage?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

export function useWebSocket({
  channel,
  autoConnect = true,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const socketRef = useRef<Socket | null>(null);
  const { token } = useAuth();

  // Função para conectar ao WebSocket
  const connect = useCallback(() => {
    if (!token) return;

    // Inicializar socket com o token de autenticação
    socketRef.current = io(WS_BASE_URL, {
      auth: {
        token,
      },
      transports: ["websocket"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    // Configurar event handlers
    socketRef.current.on("connect", () => {
      setIsConnected(true);
      onConnect?.();
    });

    socketRef.current.on("disconnect", () => {
      setIsConnected(false);
      onDisconnect?.();
    });

    socketRef.current.on("connect_error", (error) => {
      console.error("WebSocket connection error:", error);
      onError?.(error);
    });

    // Escutar mensagens no canal específico
    socketRef.current.on(channel, (data) => {
      setLastMessage(data);
      setMessages((prev) => [...prev, data]);
      onMessage?.(data);
    });

    return () => {
      socketRef.current?.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    };
  }, [token, channel, onConnect, onDisconnect, onError, onMessage]);

  // Função para desconectar
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // Função para enviar mensagem
  const sendMessage = useCallback(
    (event: string, data: any) => {
      if (socketRef.current && isConnected) {
        socketRef.current.emit(event, data);
      } else {
        console.warn(
          "Tentativa de enviar mensagem sem conexão WebSocket ativa"
        );
      }
    },
    [isConnected]
  );

  // Conectar/desconectar automaticamente com base nas dependências
  useEffect(() => {
    if (autoConnect && token) {
      const cleanup = connect();
      return cleanup;
    }
    return undefined;
  }, [autoConnect, token, connect]);

  // Limpar recursos ao desmontar
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    lastMessage,
    messages,
    sendMessage,
    connect,
    disconnect,
    socket: socketRef.current,
  };
}
