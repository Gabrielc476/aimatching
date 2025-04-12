/**
 * API Client Base
 * Cliente HTTP base para comunicação com a API do backend
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import {
  applyRequestInterceptors,
  applyResponseInterceptors,
} from "./interceptors";
import { API_BASE_URL, API_TIMEOUT } from "../constants";

/**
 * Interface para configuração adicional do cliente HTTP
 */
export interface ApiClientConfig extends AxiosRequestConfig {
  withCredentials?: boolean;
  baseURL?: string;
  timeout?: number;
}

/**
 * Classe ApiClient - Implementa o padrão Singleton para o cliente HTTP
 */
class ApiClient {
  private static instance: ApiClient;
  private client: AxiosInstance;

  // Propriedade defaults exposta publicamente para compatibilidade com Axios padrão
  public defaults: {
    headers: {
      common: Record<string, string>;
      [key: string]: any;
    };
  };

  private constructor(config: ApiClientConfig = {}) {
    // Configura o cliente HTTP com valores padrão e configurações adicionais
    this.client = axios.create({
      baseURL: config.baseURL || API_BASE_URL,
      timeout: config.timeout || API_TIMEOUT,
      withCredentials: config.withCredentials || true,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...config.headers,
      },
      ...config,
    });

    // Inicializa a propriedade defaults com referência à do cliente Axios
    this.defaults = {
      headers: this.client.defaults.headers,
    };

    // Aplica interceptadores de requisição e resposta
    applyRequestInterceptors(this.client);
    applyResponseInterceptors(this.client);
  }

  /**
   * Obtém a instância única do cliente API (padrão Singleton)
   */
  public static getInstance(config?: ApiClientConfig): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient(config);
    }
    return ApiClient.instance;
  }

  /**
   * Define o token de autenticação para todas as requisições
   */
  public setAuthToken(token: string | null): void {
    if (token) {
      this.client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      this.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete this.client.defaults.headers.common["Authorization"];
      delete this.defaults.headers.common["Authorization"];
    }
  }

  /**
   * Realiza uma requisição GET
   */
  public async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get<T>(url, config);
    return response.data;
  }

  /**
   * Realiza uma requisição POST
   */
  public async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post<T>(
      url,
      data,
      config
    );
    return response.data;
  }

  /**
   * Realiza uma requisição PUT
   */
  public async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put<T>(
      url,
      data,
      config
    );
    return response.data;
  }

  /**
   * Realiza uma requisição PATCH
   */
  public async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.patch<T>(
      url,
      data,
      config
    );
    return response.data;
  }

  /**
   * Realiza uma requisição DELETE
   */
  public async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete<T>(url, config);
    return response.data;
  }

  /**
   * Upload de arquivo com multipart/form-data
   */
  public async uploadFile<T = any>(
    url: string,
    file: File,
    fieldName: string = "file",
    additionalData?: Record<string, any>,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const formData = new FormData();
    formData.append(fieldName, file);

    // Adiciona dados adicionais ao FormData, se houver
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const uploadConfig: AxiosRequestConfig = {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      ...config,
    };

    const response: AxiosResponse<T> = await this.client.post<T>(
      url,
      formData,
      uploadConfig
    );
    return response.data;
  }

  /**
   * Obtém a instância do cliente Axios para casos de uso avançados
   */
  public getAxiosInstance(): AxiosInstance {
    return this.client;
  }
}

/**
 * Exporta uma instância única do cliente API para uso em toda a aplicação
 */
export const api = ApiClient.getInstance();

/**
 * Função para criar uma instância personalizada do cliente API com configurações específicas
 * (útil para casos de teste ou endpoints específicos)
 */
export const createApiClient = (config: ApiClientConfig): ApiClient => {
  return ApiClient.getInstance(config);
};

export default api;
