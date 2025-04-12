import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
  useCallback,
} from "react";
import { io, Socket } from "socket.io-client";
import { useAuth } from "./authContext";
import { useToast } from "@/hooks/useToast";

// Tipo para as notificações
export interface Notification {
  id: string;
  type: "job_match" | "application_status" | "resume_feedback" | "system";
  title: string;
  message: string;
  data?: any;
  isRead: boolean;
  createdAt: string;
}

// Tipos para o contexto de notificações
interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotifications: () => void;
  isConnected: boolean;
}

// Valor padrão do contexto
const defaultNotificationContext: NotificationContextType = {
  notifications: [],
  unreadCount: 0,
  markAsRead: () => {},
  markAllAsRead: () => {},
  clearNotifications: () => {},
  isConnected: false,
};

// Criação do contexto
const NotificationContext = createContext<NotificationContextType>(
  defaultNotificationContext
);

// Hook personalizado para usar o contexto
export const useNotifications = () => useContext(NotificationContext);

// Tipos para o provider
interface NotificationProviderProps {
  children: ReactNode;
}

// Provider de notificações
export const NotificationProvider: React.FC<NotificationProviderProps> = ({
  children,
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();

  // Inicialização do socket
  useEffect(() => {
    // Só conecta o socket se o usuário estiver autenticado
    if (!isAuthenticated || !user) {
      if (socket) {
        socket.disconnect();
        setSocket(null);
        setIsConnected(false);
      }
      return;
    }

    // Criar conexão WebSocket
    const socketInstance = io(
      process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:5000/ws",
      {
        query: {
          userId: user.id,
        },
        transports: ["websocket"],
        withCredentials: true,
      }
    );

    // Configurar event listeners
    socketInstance.on("connect", () => {
      setIsConnected(true);
      console.log("Socket connected");
    });

    socketInstance.on("disconnect", () => {
      setIsConnected(false);
      console.log("Socket disconnected");
    });

    socketInstance.on("notification", (notification: Notification) => {
      // Adicionar nova notificação
      setNotifications((prev) => [notification, ...prev]);

      // Incrementar contador de não lidos
      setUnreadCount((prev) => prev + 1);

      // Mostrar toast para notificações importantes
      if (notification.type === "job_match") {
        toast({
          title: "Nova vaga compatível",
          description: notification.message,
          variant: "default",
        });
      }
    });

    // Carregar notificações existentes
    const fetchNotifications = async () => {
      try {
        const response = await fetch("/api/notifications");
        const data = await response.json();

        if (data?.notifications) {
          setNotifications(data.notifications);
          setUnreadCount(
            data.notifications.filter((n: Notification) => !n.isRead).length
          );
        }
      } catch (error) {
        console.error("Erro ao carregar notificações:", error);
      }
    };

    fetchNotifications();

    // Cleanup ao desmontar
    setSocket(socketInstance);
    return () => {
      socketInstance.disconnect();
      setSocket(null);
      setIsConnected(false);
    };
  }, [isAuthenticated, user, toast]);

  // Função para marcar notificação como lida
  const markAsRead = useCallback(async (id: string) => {
    try {
      // Atualizar estado local
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
      );

      // Atualizar contador de não lidos
      setUnreadCount((prev) => Math.max(0, prev - 1));

      // Enviar requisição para o servidor
      await fetch(`/api/notifications/${id}/read`, {
        method: "PUT",
      });
    } catch (error) {
      console.error("Erro ao marcar notificação como lida:", error);
    }
  }, []);

  // Função para marcar todas as notificações como lidas
  const markAllAsRead = useCallback(async () => {
    try {
      // Atualizar estado local
      setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));

      // Zerar contador de não lidos
      setUnreadCount(0);

      // Enviar requisição para o servidor
      await fetch("/api/notifications/read-all", {
        method: "PUT",
      });
    } catch (error) {
      console.error("Erro ao marcar todas notificações como lidas:", error);
    }
  }, []);

  // Função para limpar todas as notificações
  const clearNotifications = useCallback(async () => {
    try {
      // Limpar estado local
      setNotifications([]);
      setUnreadCount(0);

      // Enviar requisição para o servidor
      await fetch("/api/notifications/clear", {
        method: "DELETE",
      });
    } catch (error) {
      console.error("Erro ao limpar notificações:", error);
    }
  }, []);

  // Valor do contexto
  const notificationContextValue: NotificationContextType = {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    clearNotifications,
    isConnected,
  };

  return (
    <NotificationContext.Provider value={notificationContextValue}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
