/**
 * Auth State Slice
 * Gerenciamento de estado para autenticação
 */
import { User } from "../../types";
import { SliceCreator } from "../index";
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
} from "../../utils/auth";

/**
 * Interface para o estado de autenticação
 */
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

/**
 * Interface para as ações do slice de autenticação
 */
export interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  clearAuthError: () => void;
}

/**
 * Interface completa do slice de autenticação (estado + ações)
 */
export interface AuthSlice {
  auth: AuthState;
  login: AuthActions["login"];
  register: AuthActions["register"];
  logout: AuthActions["logout"];
  setUser: AuthActions["setUser"];
  setToken: AuthActions["setToken"];
  setIsAuthenticated: AuthActions["setIsAuthenticated"];
  clearAuthError: AuthActions["clearAuthError"];
}

/**
 * Estado inicial de autenticação
 */
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  loading: false,
  error: null,
};

/**
 * Criador do slice de autenticação
 */
export const createAuthSlice: SliceCreator<AuthSlice> = (set, get) => ({
  auth: { ...initialState },

  /**
   * Login do usuário
   */
  login: async (email: string, password: string) => {
    try {
      // Atualiza loading state
      set((state) => ({
        auth: {
          ...state.auth,
          loading: true,
          error: null,
        },
      }));

      // Realiza login na API
      const response = await apiLogin(email, password);

      // Atualiza estado com dados da resposta
      set((state) => ({
        auth: {
          ...state.auth,
          isAuthenticated: true,
          user: response.user,
          token: response.accessToken,
          loading: false,
          error: null,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao realizar login. Verifique suas credenciais e tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        auth: {
          ...state.auth,
          loading: false,
          error: errorMessage,
        },
      }));

      throw error;
    }
  },

  /**
   * Registro de usuário
   */
  register: async (name: string, email: string, password: string) => {
    try {
      // Atualiza loading state
      set((state) => ({
        auth: {
          ...state.auth,
          loading: true,
          error: null,
        },
      }));

      // Realiza registro na API
      const response = await apiRegister(name, email, password);

      // Atualiza estado com dados da resposta
      set((state) => ({
        auth: {
          ...state.auth,
          isAuthenticated: true,
          user: response.user,
          token: response.accessToken,
          loading: false,
          error: null,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao realizar cadastro. Verifique os dados informados e tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        auth: {
          ...state.auth,
          loading: false,
          error: errorMessage,
        },
      }));

      throw error;
    }
  },

  /**
   * Logout do usuário
   */
  logout: async () => {
    try {
      // Atualiza loading state
      set((state) => ({
        auth: {
          ...state.auth,
          loading: true,
        },
      }));

      // Realiza logout na API
      await apiLogout();

      // Limpa estado
      set((state) => ({
        auth: {
          ...initialState,
          loading: false,
        },
      }));
    } catch (error) {
      console.error("Erro ao realizar logout:", error);

      // Mesmo com erro, limpa estado local
      set((state) => ({
        auth: {
          ...initialState,
          loading: false,
        },
      }));
    }
  },

  /**
   * Define o usuário atual
   */
  setUser: (user: User | null) => {
    set((state) => ({
      auth: {
        ...state.auth,
        user,
      },
    }));
  },

  /**
   * Define o token de autenticação
   */
  setToken: (token: string | null) => {
    set((state) => ({
      auth: {
        ...state.auth,
        token,
      },
    }));
  },

  /**
   * Define o estado de autenticação
   */
  setIsAuthenticated: (isAuthenticated: boolean) => {
    set((state) => ({
      auth: {
        ...state.auth,
        isAuthenticated,
      },
    }));

    // Se não está autenticado, limpa usuário e token
    if (!isAuthenticated) {
      get().setUser(null);
      get().setToken(null);
    }
  },

  /**
   * Limpa o erro de autenticação
   */
  clearAuthError: () => {
    set((state) => ({
      auth: {
        ...state.auth,
        error: null,
      },
    }));
  },
});
