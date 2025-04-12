/**
 * API Interceptors
 * Interceptores para requisições e respostas HTTP
 */
import {
  AxiosInstance,
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
} from "axios";
import { getAccessToken, refreshAccessToken } from "../utils/auth";
import { isTokenExpired } from "../utils/validation";

// Armazena requisições que estão aguardando refresh do token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason?: any) => void;
  config: AxiosRequestConfig;
}> = [];

/**
 * Processa a fila de requisições que falharam após o refresh do token
 */
const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((request) => {
    if (error) {
      request.reject(error);
    } else {
      // Atualiza o cabeçalho de autorização com o novo token
      if (token && request.config.headers) {
        request.config.headers.Authorization = `Bearer ${token}`;
      }
      request.resolve(request.config);
    }
  });

  failedQueue = [];
};

/**
 * Aplica interceptadores de requisição ao cliente Axios
 * @param client Instância do cliente Axios
 */
export const applyRequestInterceptors = (client: AxiosInstance): void => {
  client.interceptors.request.use(
    async (config) => {
      // Não adiciona token para rotas que não exigem autenticação
      if (
        config.url?.includes("/auth/login") ||
        config.url?.includes("/auth/register")
      ) {
        return config;
      }

      // Obtém o token de acesso do armazenamento local
      const token = getAccessToken();

      // Se não há token, continua com a requisição sem modificações
      if (!token) {
        return config;
      }

      // Verifica se o token está expirado
      if (isTokenExpired(token)) {
        // Se já está em processo de refresh, adiciona à fila
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject, config });
          });
        }

        isRefreshing = true;

        try {
          // Tenta renovar o token
          const newToken = await refreshAccessToken();

          // Atualiza o cabeçalho com o novo token
          if (config.headers) {
            config.headers.Authorization = `Bearer ${newToken}`;
          }

          // Processa fila de requisições pendentes
          processQueue(null, newToken);
          return config;
        } catch (error) {
          // Em caso de erro no refresh, processa a fila com erro
          processQueue(error as Error);

          // Redireciona para login ou gerencia de outra forma (evento, etc.)
          window.dispatchEvent(new CustomEvent("auth:session-expired"));

          throw error;
        } finally {
          isRefreshing = false;
        }
      }

      // Adiciona o token ao cabeçalho da requisição
      if (config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );
};

/**
 * Aplica interceptadores de resposta ao cliente Axios
 * @param client Instância do cliente Axios
 */
export const applyResponseInterceptors = (client: AxiosInstance): void => {
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Pode processar a resposta antes de retorná-la
      return response;
    },
    async (error: AxiosError) => {
      // Obtém a configuração original e a resposta
      const originalConfig = error.config as AxiosRequestConfig;

      // Se não houver configuração ou a URL for de refresh, rejeita diretamente
      if (!originalConfig || originalConfig.url?.includes("/auth/refresh")) {
        return Promise.reject(error);
      }

      // Tratamento de erro 401 (Não autorizado)
      if (error.response?.status === 401) {
        // Verifica se já tentou refresh para este request para evitar loop infinito
        if (!(originalConfig as any)._retry) {
          // Se já está em processo de refresh, adiciona à fila
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject, config: originalConfig });
            })
              .then((config) => client(config as AxiosRequestConfig))
              .catch((err) => Promise.reject(err));
          }

          // Marca que já tentou refresh para esta requisição
          (originalConfig as any)._retry = true;
          isRefreshing = true;

          try {
            // Tenta renovar o token
            const newToken = await refreshAccessToken();

            // Atualiza o cabeçalho com o novo token
            if (originalConfig.headers) {
              originalConfig.headers.Authorization = `Bearer ${newToken}`;
            }

            // Processa fila de requisições pendentes
            processQueue(null, newToken);

            // Refaz a requisição original com o novo token
            return client(originalConfig);
          } catch (refreshError) {
            // Em caso de erro no refresh, processa a fila com erro
            processQueue(refreshError as Error);

            // Redireciona para login ou gerencia de outra forma
            window.dispatchEvent(new CustomEvent("auth:session-expired"));

            return Promise.reject(refreshError);
          } finally {
            isRefreshing = false;
          }
        }
      }

      // Tratamento para outros códigos de erro
      if (error.response) {
        // O servidor respondeu com um código de status fora do intervalo 2xx
        switch (error.response.status) {
          case 400: // Bad Request
            // Possível tratamento especial para validação de dados
            break;
          case 403: // Forbidden
            // Usuário autenticado mas sem permissão
            window.dispatchEvent(new CustomEvent("auth:forbidden"));
            break;
          case 404: // Not Found
            // Recurso não encontrado
            break;
          case 429: // Too Many Requests
            // Rate limiting
            window.dispatchEvent(new CustomEvent("api:rate-limited"));
            break;
          case 500: // Internal Server Error
          case 502: // Bad Gateway
          case 503: // Service Unavailable
          case 504: // Gateway Timeout
            // Erros do servidor
            window.dispatchEvent(
              new CustomEvent("api:server-error", {
                detail: { status: error.response.status },
              })
            );
            break;
        }
      } else if (error.request) {
        // A requisição foi feita mas não houve resposta
        window.dispatchEvent(new CustomEvent("api:network-error"));
      }

      // Rejeita a promessa com o erro para tratamento adicional
      return Promise.reject(error);
    }
  );
};
