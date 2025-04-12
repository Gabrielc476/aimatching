/**
 * Auth Utilities
 * Funções utilitárias para autenticação e gerenciamento de tokens
 */
import { AUTH_ENDPOINTS } from "../api/endpoints";
import { apiClient } from "../api/client";
import { isTokenExpired } from "./validation";
import {
  ACCESS_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  USER_DATA_KEY,
  AUTH_STATE_KEY,
} from "../constants";

/**
 * Interface para resposta de autenticação
 */
interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: {
    id: string;
    email: string;
    name: string;
    [key: string]: any;
  };
  expiresIn: number;
}

/**
 * Interface para dados do usuário
 */
interface User {
  id: string;
  email: string;
  name: string;
  [key: string]: any;
}

/**
 * Interface para estado de autenticação
 */
interface AuthState {
  isAuthenticated: boolean;
  lastLogin?: string;
  lastActivity?: string;
}

/**
 * Realiza o login do usuário
 * @param email Email do usuário
 * @param password Senha do usuário
 * @returns Promise com a resposta de autenticação
 */
export const login = async (
  email: string,
  password: string
): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>(
    AUTH_ENDPOINTS.LOGIN.path,
    { email, password }
  );

  if (response && response.accessToken) {
    // Armazena tokens e dados do usuário
    setAccessToken(response.accessToken);
    setRefreshToken(response.refreshToken);
    setUserData(response.user);

    // Atualiza estado de autenticação
    updateAuthState(true);

    // Dispara evento de login
    window.dispatchEvent(new CustomEvent("auth:login", { detail: response }));
  }

  return response;
};

/**
 * Realiza o registro de um novo usuário
 * @param name Nome do usuário
 * @param email Email do usuário
 * @param password Senha do usuário
 * @returns Promise com a resposta de registro
 */
export const register = async (
  name: string,
  email: string,
  password: string
): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>(
    AUTH_ENDPOINTS.REGISTER.path,
    { name, email, password }
  );

  if (response && response.accessToken) {
    // Armazena tokens e dados do usuário
    setAccessToken(response.accessToken);
    setRefreshToken(response.refreshToken);
    setUserData(response.user);

    // Atualiza estado de autenticação
    updateAuthState(true);

    // Dispara evento de registro
    window.dispatchEvent(
      new CustomEvent("auth:register", { detail: response })
    );
  }

  return response;
};

/**
 * Realiza o logout do usuário
 * @returns Promise que resolve quando o logout for concluído
 */
export const logout = async (): Promise<void> => {
  try {
    // Tenta fazer logout no servidor
    await apiClient.post(AUTH_ENDPOINTS.LOGOUT.path);
  } catch (error) {
    console.warn("Error during logout from server:", error);
  } finally {
    // Limpa dados locais independentemente da resposta do servidor
    clearAuthData();

    // Dispara evento de logout
    window.dispatchEvent(new CustomEvent("auth:logout"));
  }
};

/**
 * Atualiza o token de acesso usando o token de refresh
 * @returns Promise com o novo token de acesso
 */
export const refreshAccessToken = async (): Promise<string> => {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  try {
    const response = await apiClient.post<{
      accessToken: string;
      expiresIn: number;
    }>(AUTH_ENDPOINTS.REFRESH_TOKEN.path, { refreshToken });

    if (response && response.accessToken) {
      setAccessToken(response.accessToken);

      // Atualiza timestamp de última atividade
      updateLastActivity();

      return response.accessToken;
    }

    throw new Error("Invalid response from token refresh");
  } catch (error) {
    // Em caso de erro no refresh, limpa os dados e força logout
    clearAuthData();
    window.dispatchEvent(new CustomEvent("auth:session-expired"));
    throw error;
  }
};

/**
 * Verifica se o usuário está autenticado
 * @returns Booleano indicando o estado de autenticação
 */
export const isAuthenticated = (): boolean => {
  const token = getAccessToken();
  const authState = getAuthState();

  if (!token || !authState || !authState.isAuthenticated) {
    return false;
  }

  // Verifica se o token está expirado
  if (isTokenExpired(token)) {
    // Se expirou, não limpa os dados aqui para permitir refresh
    return false;
  }

  return true;
};

/**
 * Obtém o token de acesso do armazenamento local
 * @returns String com o token de acesso ou null
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Define o token de acesso no armazenamento local
 * @param token Token de acesso
 */
export const setAccessToken = (token: string): void => {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
};

/**
 * Obtém o token de refresh do armazenamento local
 * @returns String com o token de refresh ou null
 */
export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Define o token de refresh no armazenamento local
 * @param token Token de refresh
 */
export const setRefreshToken = (token: string): void => {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

/**
 * Obtém os dados do usuário do armazenamento local
 * @returns Objeto com dados do usuário ou null
 */
export const getUserData = (): User | null => {
  const userData = localStorage.getItem(USER_DATA_KEY);

  if (!userData) {
    return null;
  }

  try {
    return JSON.parse(userData);
  } catch (error) {
    console.error("Error parsing user data:", error);
    return null;
  }
};

/**
 * Define os dados do usuário no armazenamento local
 * @param user Objeto com dados do usuário
 */
export const setUserData = (user: User): void => {
  localStorage.setItem(USER_DATA_KEY, JSON.stringify(user));
};

/**
 * Obtém o estado de autenticação do armazenamento local
 * @returns Objeto com estado de autenticação ou estado padrão
 */
export const getAuthState = (): AuthState => {
  const authState = localStorage.getItem(AUTH_STATE_KEY);

  if (!authState) {
    return { isAuthenticated: false };
  }

  try {
    return JSON.parse(authState);
  } catch (error) {
    console.error("Error parsing auth state:", error);
    return { isAuthenticated: false };
  }
};

/**
 * Atualiza o estado de autenticação no armazenamento local
 * @param isAuthenticated Booleano indicando se está autenticado
 */
export const updateAuthState = (isAuthenticated: boolean): void => {
  const currentState = getAuthState();
  const now = new Date().toISOString();

  const newState: AuthState = {
    ...currentState,
    isAuthenticated,
    lastActivity: now,
  };

  // Se é um novo login, atualiza o timestamp de login
  if (isAuthenticated && !currentState.isAuthenticated) {
    newState.lastLogin = now;
  }

  localStorage.setItem(AUTH_STATE_KEY, JSON.stringify(newState));
};

/**
 * Atualiza o timestamp de última atividade
 */
export const updateLastActivity = (): void => {
  const currentState = getAuthState();

  if (currentState && currentState.isAuthenticated) {
    const newState: AuthState = {
      ...currentState,
      lastActivity: new Date().toISOString(),
    };

    localStorage.setItem(AUTH_STATE_KEY, JSON.stringify(newState));
  }
};

/**
 * Limpa todos os dados de autenticação
 */
export const clearAuthData = (): void => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_DATA_KEY);

  // Mantém o histórico de auth state, mas marca como não autenticado
  const authState = getAuthState();
  if (authState) {
    updateAuthState(false);
  } else {
    localStorage.removeItem(AUTH_STATE_KEY);
  }
};

/**
 * Verifica se o usuário tem uma permissão específica
 * @param permission Permissão a ser verificada
 * @returns Booleano indicando se tem a permissão
 */
export const hasPermission = (permission: string): boolean => {
  const user = getUserData();

  if (!user || !user.permissions) {
    return false;
  }

  return (
    Array.isArray(user.permissions) && user.permissions.includes(permission)
  );
};

/**
 * Exportação padrão de todas as funções
 */
export default {
  login,
  register,
  logout,
  refreshAccessToken,
  isAuthenticated,
  getAccessToken,
  getRefreshToken,
  getUserData,
  updateLastActivity,
  hasPermission,
};
