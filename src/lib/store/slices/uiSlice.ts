/**
 * UI State Slice
 * Gerenciamento de estado para interface do usuário
 */
import { SliceCreator } from "../index";
import {
  DialogOptions,
  Notification,
  NotificationType,
  ToastOptions,
} from "../../types";
import { detectTheme } from "../../utils";
import { generateUUID } from "../../utils/helpers";

/**
 * Interface para o estado de toast
 */
export interface Toast extends ToastOptions {
  id: string;
  createdAt: Date;
}

/**
 * Interface para o estado de diálogo
 */
export interface Dialog extends DialogOptions {
  id: string;
  isOpen: boolean;
}

/**
 * Interface para o estado da UI
 */
export interface UIState {
  ui: {
    theme: "light" | "dark";
    sidebarCollapsed: boolean;
    notifications: Notification[];
    toasts: Toast[];
    dialogs: Dialog[];
  };
}

/**
 * Interface para as ações do slice da UI
 */
export interface UIActions {
  toggleTheme: () => void;
  setTheme: (theme: "light" | "dark") => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  addNotification: (
    notification: Omit<Notification, "id" | "isRead" | "createdAt">
  ) => void;
  markNotificationAsRead: (notificationId: string) => void;
  clearNotifications: () => void;
  showToast: (options: ToastOptions) => string;
  dismissToast: (id: string) => void;
  showDialog: (options: DialogOptions) => string;
  dismissDialog: (id: string) => void;
}

/**
 * Interface completa do slice da UI (estado + ações)
 */
export interface UISlice extends UIState, UIActions {}

/**
 * Estado inicial da UI
 */
const initialState: UIState = {
  ui: {
    theme: detectTheme(),
    sidebarCollapsed: false,
    notifications: [],
    toasts: [],
    dialogs: [],
  },
};

/**
 * Criador do slice da UI
 */
export const createUISlice: SliceCreator<UISlice> = (set, get) => ({
  ...initialState,

  /**
   * Alterna entre tema claro e escuro
   */
  toggleTheme: () => {
    const currentTheme = get().ui.theme;
    const newTheme = currentTheme === "light" ? "dark" : "light";

    // Atualiza o estado
    set((state) => ({
      ui: {
        ...state.ui,
        theme: newTheme,
      },
    }));

    // Atualiza a classe do document para aplicar o tema
    if (typeof document !== "undefined") {
      if (newTheme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }

      // Salva a preferência do usuário
      localStorage.setItem("linkedin-job-matcher-theme", newTheme);
    }
  },

  /**
   * Define o tema diretamente
   */
  setTheme: (theme: "light" | "dark") => {
    // Atualiza o estado apenas se for diferente do atual
    if (theme !== get().ui.theme) {
      set((state) => ({
        ui: {
          ...state.ui,
          theme,
        },
      }));

      // Atualiza a classe do document para aplicar o tema
      if (typeof document !== "undefined") {
        if (theme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }

        // Salva a preferência do usuário
        localStorage.setItem("linkedin-job-matcher-theme", theme);
      }
    }
  },

  /**
   * Alterna o estado de colapso da sidebar
   */
  toggleSidebar: () => {
    set((state) => ({
      ui: {
        ...state.ui,
        sidebarCollapsed: !state.ui.sidebarCollapsed,
      },
    }));
  },

  /**
   * Define o estado de colapso da sidebar
   */
  setSidebarCollapsed: (collapsed: boolean) => {
    set((state) => ({
      ui: {
        ...state.ui,
        sidebarCollapsed: collapsed,
      },
    }));
  },

  /**
   * Adiciona uma nova notificação
   */
  addNotification: (
    notification: Omit<Notification, "id" | "isRead" | "createdAt">
  ) => {
    const newNotification: Notification = {
      ...notification,
      id: generateUUID(),
      isRead: false,
      createdAt: new Date().toISOString(),
    };

    set((state) => ({
      ui: {
        ...state.ui,
        notifications: [newNotification, ...state.ui.notifications],
      },
    }));

    // Opcionalmente, também mostra um toast para notificações em tempo real
    if (notification.type === NotificationType.NEW_MATCH) {
      get().showToast({
        title: "Nova correspondência encontrada",
        description: notification.message,
        type: "success",
        action: notification.link
          ? {
              label: "Ver",
              onClick: () => {
                if (typeof window !== "undefined" && notification.link) {
                  window.location.href = notification.link;
                }
              },
            }
          : undefined,
      });
    }
  },

  /**
   * Marca uma notificação como lida
   */
  markNotificationAsRead: (notificationId: string) => {
    set((state) => ({
      ui: {
        ...state.ui,
        notifications: state.ui.notifications.map((notification) =>
          notification.id === notificationId
            ? { ...notification, isRead: true }
            : notification
        ),
      },
    }));
  },

  /**
   * Limpa todas as notificações
   */
  clearNotifications: () => {
    set((state) => ({
      ui: {
        ...state.ui,
        notifications: [],
      },
    }));
  },

  /**
   * Exibe um toast
   * @returns ID do toast criado
   */
  showToast: (options: ToastOptions) => {
    const id = generateUUID();

    const toast: Toast = {
      id,
      type: options.type || "default",
      title: options.title,
      description: options.description,
      duration: options.duration || 5000, // 5 segundos por padrão
      position: options.position || "top-right",
      action: options.action,
      createdAt: new Date(),
    };

    set((state) => ({
      ui: {
        ...state.ui,
        toasts: [...state.ui.toasts, toast],
      },
    }));

    // Remove o toast automaticamente após a duração
    if (toast.duration > 0) {
      setTimeout(() => {
        get().dismissToast(id);
      }, toast.duration);
    }

    return id;
  },

  /**
   * Remove um toast pelo ID
   */
  dismissToast: (id: string) => {
    set((state) => ({
      ui: {
        ...state.ui,
        toasts: state.ui.toasts.filter((toast) => toast.id !== id),
      },
    }));
  },

  /**
   * Exibe um diálogo
   * @returns ID do diálogo criado
   */
  showDialog: (options: DialogOptions) => {
    const id = generateUUID();

    const dialog: Dialog = {
      id,
      title: options.title,
      description: options.description,
      confirmLabel: options.confirmLabel || "Confirmar",
      cancelLabel: options.cancelLabel || "Cancelar",
      onConfirm: options.onConfirm,
      onCancel: options.onCancel,
      type: options.type || "default",
      isDismissable:
        options.isDismissable !== undefined ? options.isDismissable : true,
      isOpen: true,
    };

    set((state) => ({
      ui: {
        ...state.ui,
        dialogs: [...state.ui.dialogs, dialog],
      },
    }));

    return id;
  },

  /**
   * Remove um diálogo pelo ID
   */
  dismissDialog: (id: string) => {
    // Primeiro, encontra o diálogo para acionar callbacks se necessário
    const dialog = get().ui.dialogs.find((d) => d.id === id);

    // Atualiza o estado para fechar o diálogo
    set((state) => ({
      ui: {
        ...state.ui,
        dialogs: state.ui.dialogs.filter((dialog) => dialog.id !== id),
      },
    }));

    // Aciona callback de cancelamento se existe e não foi confirmado
    if (dialog && dialog.onCancel) {
      dialog.onCancel();
    }
  },
});
