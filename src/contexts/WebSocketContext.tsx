"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

// Tipos para as mensagens WebSocket
type NotificationType = "match" | "job" | "application" | "system";

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  data?: Record<string, any>;
}

// Interface do contexto WebSocket
interface WebSocketContextType {
  isConnected: boolean;
  notifications: Notification[];
  unreadCount: number;
  connect: () => void;
  disconnect: () => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
}

// Criação do contexto
const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined
);

/**
 * Provider para o contexto WebSocket
 * Gerencia a conexão WebSocket e as notificações em tempo real
 */
export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Calcular número de notificações não lidas
  const unreadCount = notifications.filter((n) => !n.read).length;

  // Função para conectar ao WebSocket
  const connect = () => {
    if (socket !== null) return;

    // Em um ambiente real, isso usaria o URL do WebSocket do backend
    const wsUrl =
      process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:5000/ws/notifications";
    const newSocket = new WebSocket(wsUrl);

    newSocket.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
    };

    newSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "notification") {
          setNotifications((prev) => [data.notification, ...prev]);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    newSocket.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);
      setSocket(null);
    };

    newSocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      newSocket.close();
    };

    setSocket(newSocket);
  };

  // Função para desconectar do WebSocket
  const disconnect = () => {
    if (socket) {
      socket.close();
      setSocket(null);
      setIsConnected(false);
    }
  };

  // Função para marcar uma notificação como lida
  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((notification) =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  // Função para marcar todas as notificações como lidas
  const markAllAsRead = () => {
    setNotifications((prev) =>
      prev.map((notification) => ({ ...notification, read: true }))
    );
  };

  // Conectar ao WebSocket quando o componente for montado
  useEffect(() => {
    // Verifica se estamos no lado do cliente
    if (typeof window !== "undefined") {
      connect();

      // Dados de exemplo para desenvolvimento
      setNotifications([
        {
          id: "1",
          type: "match",
          title: "Nova correspondência",
          message:
            "Você tem 92% de compatibilidade com a vaga de Desenvolvedor Full Stack na empresa TechSolutions",
          timestamp: new Date().toISOString(),
          read: false,
          data: {
            jobId: "job-101",
            matchScore: 92,
          },
        },
        {
          id: "2",
          type: "job",
          title: "Novas vagas disponíveis",
          message: "Encontramos 5 novas vagas compatíveis com seu perfil",
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          read: true,
        },
      ]);
    }

    // Desconectar quando o componente for desmontado
    return () => {
      disconnect();
    };
  }, []);

  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        notifications,
        unreadCount,
        connect,
        disconnect,
        markAsRead,
        markAllAsRead,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
}

/**
 * Hook para acessar o contexto WebSocket
 */
export function useWebSocket() {
  const context = useContext(WebSocketContext);

  if (context === undefined) {
    throw new Error(
      "useWebSocket deve ser usado dentro de um WebSocketProvider"
    );
  }

  return context;
}
