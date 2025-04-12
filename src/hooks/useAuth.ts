/**
 * Hook useAuth
 * Hook customizado para autenticação que utiliza a store Zustand
 */
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "./useToast";
import { useAuthStore } from "@/lib/store";

export function useAuth() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Obtém o estado e métodos do slice de autenticação
  const {
    isAuthenticated,
    user,
    token,
    loading,
    error,
    login,
    register,
    logout: logoutStore,
    setIsAuthenticated,
    setUser,
    setToken,
    clearAuthError,
  } = useAuthStore();

  // Wrapper para logout que também limpa o cache do React Query
  const logout = async () => {
    await logoutStore();
    queryClient.clear();

    toast({
      title: "Logout realizado",
      description: "Você foi desconectado com sucesso.",
      type: "default",
    });
  };

  return {
    // Estado
    user,
    token,
    isAuthenticated,
    isLoading: loading,
    error,

    // Ações de autenticação
    login,
    register,
    logout,

    // Ações de gestão de estado
    setUser,
    setToken,
    setIsAuthenticated,
    clearAuthError,
  };
}
