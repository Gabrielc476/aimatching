import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";
import { User, AuthTokens } from "@/lib/types";

// Tipos para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
}

// Valor padrão do contexto
const defaultAuthContext: AuthContextType = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  updateUser: () => {},
};

// Criação do contexto
const AuthContext = createContext<AuthContextType>(defaultAuthContext);

// Hook personalizado para usar o contexto
export const useAuth = () => useContext(AuthContext);

// Tipos para o provider
interface AuthProviderProps {
  children: ReactNode;
}

// Gerenciamento de tokens
const TOKEN_KEY = "auth_tokens";

const saveTokens = (tokens: AuthTokens) => {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
};

const getTokens = (): AuthTokens | null => {
  const tokens = localStorage.getItem(TOKEN_KEY);
  return tokens ? JSON.parse(tokens) : null;
};

const removeTokens = () => {
  localStorage.removeItem(TOKEN_KEY);
};

// Provider de autenticação
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Função para verificar a autenticação atual
  const checkAuth = async () => {
    try {
      const tokens = getTokens();

      if (!tokens) {
        setIsLoading(false);
        return;
      }

      // Configure o token de autenticação no cliente da API usando o método adequado
      api.setAuthToken(tokens.accessToken);

      // Buscar informações do usuário
      const response = await api.get("/api/profile");
      setUser(response.user);
    } catch (error) {
      // Em caso de erro, tentar atualizar o token
      try {
        const tokens = getTokens();
        if (tokens?.refreshToken) {
          const refreshResponse = await api.post("/api/auth/refresh", {
            refreshToken: tokens.refreshToken,
          });

          saveTokens(refreshResponse);
          api.setAuthToken(refreshResponse.accessToken);

          // Tentar novamente com o novo token
          const userResponse = await api.get("/api/profile");
          setUser(userResponse.user);
        }
      } catch (refreshError) {
        // Se a atualização falhar, remover tokens e redirecionar para login
        removeTokens();
        api.setAuthToken(null);
        setUser(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Verificar autenticação ao montar o componente
  useEffect(() => {
    checkAuth();
  }, []);

  // Função de login
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await api.post("/api/auth/login", { email, password });
      saveTokens(response);
      api.setAuthToken(response.accessToken);

      const userResponse = await api.get("/api/profile");
      setUser(userResponse.user);

      router.push("/dashboard");
    } catch (error) {
      console.error("Erro ao fazer login:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Função de registro
  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      await api.post("/api/auth/register", { name, email, password });
      await login(email, password);
    } catch (error) {
      console.error("Erro ao registrar:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Função de logout
  const logout = async () => {
    try {
      const tokens = getTokens();
      if (tokens) {
        await api.post("/api/auth/logout", {
          refreshToken: tokens.refreshToken,
        });
      }
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
    } finally {
      removeTokens();
      api.setAuthToken(null);
      setUser(null);
      router.push("/login");
    }
  };

  // Função para atualizar dados do usuário
  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  // Valor do contexto
  const authContextValue: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
