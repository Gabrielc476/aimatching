/**
 * API Endpoints
 * Configuração centralizada de todos os endpoints da API
 */

/**
 * Enum para categorias de endpoints
 * Facilita a organização dos endpoints por domínio
 */
export enum EndpointCategory {
  AUTH = "auth",
  PROFILE = "profile",
  RESUME = "resume",
  JOBS = "jobs",
  MATCHES = "matches",
  ANALYTICS = "analytics",
}

/**
 * Interface para tipo de endpoints
 * Garante que todos os endpoints tenham as mesmas propriedades
 */
export interface Endpoint {
  path: string;
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  requiresAuth: boolean;
  cacheable?: boolean;
  cacheTime?: number; // em milissegundos
}

/**
 * Interface para mapeamento de endpoints por categoria
 */
interface EndpointMap {
  [key: string]: Endpoint;
}

/**
 * Endpoints de autenticação
 */
export const AUTH_ENDPOINTS: EndpointMap = {
  LOGIN: {
    path: "/auth/login",
    method: "POST",
    requiresAuth: false,
  },
  REGISTER: {
    path: "/auth/register",
    method: "POST",
    requiresAuth: false,
  },
  LOGOUT: {
    path: "/auth/logout",
    method: "POST",
    requiresAuth: true,
  },
  REFRESH_TOKEN: {
    path: "/auth/refresh",
    method: "POST",
    requiresAuth: false,
  },
  VERIFY_EMAIL: {
    path: "/auth/verify-email",
    method: "POST",
    requiresAuth: false,
  },
  RESET_PASSWORD: {
    path: "/auth/reset-password",
    method: "POST",
    requiresAuth: false,
  },
  REQUEST_PASSWORD_RESET: {
    path: "/auth/request-reset",
    method: "POST",
    requiresAuth: false,
  },
};

/**
 * Endpoints de perfil
 */
export const PROFILE_ENDPOINTS: EndpointMap = {
  GET_PROFILE: {
    path: "/profile",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 5 * 60 * 1000, // 5 minutos
  },
  UPDATE_PROFILE: {
    path: "/profile",
    method: "PUT",
    requiresAuth: true,
  },
  UPDATE_PREFERENCES: {
    path: "/profile/preferences",
    method: "PATCH",
    requiresAuth: true,
  },
  UPDATE_SKILLS: {
    path: "/profile/skills",
    method: "PATCH",
    requiresAuth: true,
  },
};

/**
 * Endpoints de currículo
 */
export const RESUME_ENDPOINTS: EndpointMap = {
  UPLOAD_RESUME: {
    path: "/resume/upload",
    method: "POST",
    requiresAuth: true,
  },
  GET_RESUMES: {
    path: "/resume",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 10 * 60 * 1000, // 10 minutos
  },
  GET_RESUME: {
    path: "/resume/:id",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 10 * 60 * 1000, // 10 minutos
  },
  DELETE_RESUME: {
    path: "/resume/:id",
    method: "DELETE",
    requiresAuth: true,
  },
  SET_PRIMARY_RESUME: {
    path: "/resume/:id/primary",
    method: "PATCH",
    requiresAuth: true,
  },
  ANALYZE_RESUME: {
    path: "/resume/:id/analyze",
    method: "POST",
    requiresAuth: true,
  },
};

/**
 * Endpoints de vagas
 */
export const JOB_ENDPOINTS: EndpointMap = {
  GET_JOBS: {
    path: "/jobs",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 5 * 60 * 1000, // 5 minutos
  },
  GET_JOB: {
    path: "/jobs/:id",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 15 * 60 * 1000, // 15 minutos
  },
  SEARCH_JOBS: {
    path: "/jobs/search",
    method: "POST",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 5 * 60 * 1000, // 5 minutos
  },
  SAVE_JOB: {
    path: "/jobs/:id/save",
    method: "POST",
    requiresAuth: true,
  },
  UNSAVE_JOB: {
    path: "/jobs/:id/save",
    method: "DELETE",
    requiresAuth: true,
  },
  GET_SAVED_JOBS: {
    path: "/jobs/saved",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 5 * 60 * 1000, // 5 minutos
  },
};

/**
 * Endpoints de correspondências
 */
export const MATCH_ENDPOINTS: EndpointMap = {
  GET_MATCHES: {
    path: "/matches",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 5 * 60 * 1000, // 5 minutos
  },
  GET_MATCH: {
    path: "/matches/:id",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 10 * 60 * 1000, // 10 minutos
  },
  ANALYZE_MATCH: {
    path: "/matches/analyze",
    method: "POST",
    requiresAuth: true,
  },
  GET_MATCH_RECOMMENDATIONS: {
    path: "/matches/:id/recommendations",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 30 * 60 * 1000, // 30 minutos
  },
  UPDATE_MATCH_STATUS: {
    path: "/matches/:id/status",
    method: "PATCH",
    requiresAuth: true,
  },
};

/**
 * Endpoints de analytics
 */
export const ANALYTICS_ENDPOINTS: EndpointMap = {
  GET_PROFILE_ANALYTICS: {
    path: "/analytics/profile",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 60 * 60 * 1000, // 1 hora
  },
  GET_RESUME_ANALYTICS: {
    path: "/analytics/resume/:id",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 60 * 60 * 1000, // 1 hora
  },
  GET_MARKET_INSIGHTS: {
    path: "/analytics/market",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 24 * 60 * 60 * 1000, // 24 horas
  },
  GET_SKILL_GAP_ANALYSIS: {
    path: "/analytics/skill-gap",
    method: "GET",
    requiresAuth: true,
    cacheable: true,
    cacheTime: 24 * 60 * 60 * 1000, // 24 horas
  },
};

/**
 * Mapeamento completo de todos os endpoints organizados por categoria
 */
export const ENDPOINTS = {
  [EndpointCategory.AUTH]: AUTH_ENDPOINTS,
  [EndpointCategory.PROFILE]: PROFILE_ENDPOINTS,
  [EndpointCategory.RESUME]: RESUME_ENDPOINTS,
  [EndpointCategory.JOBS]: JOB_ENDPOINTS,
  [EndpointCategory.MATCHES]: MATCH_ENDPOINTS,
  [EndpointCategory.ANALYTICS]: ANALYTICS_ENDPOINTS,
};

/**
 * Função auxiliar para construir URLs de endpoint com parâmetros de caminho
 * Ex: buildEndpointUrl('/resume/:id', { id: '123' }) => '/resume/123'
 */
export const buildEndpointUrl = (
  endpoint: string,
  params?: Record<string, string | number>
): string => {
  let url = endpoint;

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url = url.replace(`:${key}`, value.toString());
    });
  }

  return url;
};

export default ENDPOINTS;
