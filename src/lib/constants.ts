/**
 * Application Constants
 * Constantes globais para uso em toda a aplicação
 */

// API e Configuração
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
export const API_TIMEOUT = 30000; // 30 segundos
export const WEBSOCKET_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:5000/ws";

// Autenticação
export const ACCESS_TOKEN_KEY = "linkedin_job_matcher_access_token";
export const REFRESH_TOKEN_KEY = "linkedin_job_matcher_refresh_token";
export const USER_DATA_KEY = "linkedin_job_matcher_user";
export const AUTH_STATE_KEY = "linkedin_job_matcher_auth_state";
export const JWT_EXPIRATION_MARGIN = 300; // 5 minutos em segundos

// Paginação e Limites
export const DEFAULT_PAGE_SIZE = 10;
export const MAX_PAGE_SIZE = 50;
export const SEARCH_DEBOUNCE_TIME = 300; // 300ms

// Tipos de Arquivo
export const ALLOWED_RESUME_FILE_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
];
export const MAX_RESUME_FILE_SIZE = 5; // 5MB

// Cores do Sistema
export const COLORS = {
  primary: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49",
  },
  secondary: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065",
  },
  success: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16",
  },
  warning: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03",
  },
  error: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a",
  },
  neutral: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712",
  },
};

// Match Scores (pontuações de correspondência)
export const MATCH_SCORE_THRESHOLDS = {
  EXCELLENT: 85,
  GOOD: 70,
  FAIR: 50,
  POOR: 0,
};

export const MATCH_SCORE_LABELS = {
  EXCELLENT: "Excelente",
  GOOD: "Bom",
  FAIR: "Razoável",
  POOR: "Baixo",
};

// Filtros e Opções
export const JOB_TYPES = [
  { value: "full_time", label: "Tempo Integral" },
  { value: "part_time", label: "Meio Período" },
  { value: "contract", label: "Contrato" },
  { value: "temporary", label: "Temporário" },
  { value: "internship", label: "Estágio" },
  { value: "volunteer", label: "Voluntário" },
  { value: "freelance", label: "Freelance" },
];

export const EXPERIENCE_LEVELS = [
  { value: "internship", label: "Estágio" },
  { value: "entry_level", label: "Júnior" },
  { value: "mid_level", label: "Pleno" },
  { value: "senior_level", label: "Sênior" },
  { value: "executive", label: "Executivo" },
];

export const WORK_MODELS = [
  { value: "on_site", label: "Presencial" },
  { value: "hybrid", label: "Híbrido" },
  { value: "remote", label: "Remoto" },
];

// Estados e cidades do Brasil (simplificado)
export const BRAZILIAN_STATES = [
  { value: "AC", label: "Acre" },
  { value: "AL", label: "Alagoas" },
  { value: "AP", label: "Amapá" },
  { value: "AM", label: "Amazonas" },
  { value: "BA", label: "Bahia" },
  { value: "CE", label: "Ceará" },
  { value: "DF", label: "Distrito Federal" },
  { value: "ES", label: "Espírito Santo" },
  { value: "GO", label: "Goiás" },
  { value: "MA", label: "Maranhão" },
  { value: "MT", label: "Mato Grosso" },
  { value: "MS", label: "Mato Grosso do Sul" },
  { value: "MG", label: "Minas Gerais" },
  { value: "PA", label: "Pará" },
  { value: "PB", label: "Paraíba" },
  { value: "PR", label: "Paraná" },
  { value: "PE", label: "Pernambuco" },
  { value: "PI", label: "Piauí" },
  { value: "RJ", label: "Rio de Janeiro" },
  { value: "RN", label: "Rio Grande do Norte" },
  { value: "RS", label: "Rio Grande do Sul" },
  { value: "RO", label: "Rondônia" },
  { value: "RR", label: "Roraima" },
  { value: "SC", label: "Santa Catarina" },
  { value: "SP", label: "São Paulo" },
  { value: "SE", label: "Sergipe" },
  { value: "TO", label: "Tocantins" },
];

export const MAJOR_BRAZILIAN_CITIES = [
  { value: "sao_paulo", label: "São Paulo", state: "SP" },
  { value: "rio_de_janeiro", label: "Rio de Janeiro", state: "RJ" },
  { value: "brasilia", label: "Brasília", state: "DF" },
  { value: "salvador", label: "Salvador", state: "BA" },
  { value: "fortaleza", label: "Fortaleza", state: "CE" },
  { value: "belo_horizonte", label: "Belo Horizonte", state: "MG" },
  { value: "manaus", label: "Manaus", state: "AM" },
  { value: "curitiba", label: "Curitiba", state: "PR" },
  { value: "recife", label: "Recife", state: "PE" },
  { value: "porto_alegre", label: "Porto Alegre", state: "RS" },
  { value: "belem", label: "Belém", state: "PA" },
  { value: "goiania", label: "Goiânia", state: "GO" },
  { value: "guarulhos", label: "Guarulhos", state: "SP" },
  { value: "campinas", label: "Campinas", state: "SP" },
  { value: "sao_luis", label: "São Luís", state: "MA" },
  { value: "sao_goncalo", label: "São Gonçalo", state: "RJ" },
];

// Rotas da Aplicação
export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/dashboard",
  JOBS: "/jobs",
  JOB_DETAIL: (id: string) => `/jobs/${id}`,
  PROFILE: "/profile",
  MATCHES: "/matches",
  MATCH_DETAIL: (id: string) => `/matches/${id}`,
  ANALYTICS: "/analytics",
  SETTINGS: "/settings",
  PRIVACY_POLICY: "/privacy-policy",
  TERMS_OF_SERVICE: "/terms-of-service",
  HELP: "/help",
};

// BreakPoints (usados com TailwindCSS)
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
};

// Constantes de Tempo
export const TIME_CONSTANTS = {
  SECOND: 1,
  MINUTE: 60,
  HOUR: 60 * 60,
  DAY: 24 * 60 * 60,
  WEEK: 7 * 24 * 60 * 60,
  MONTH: 30 * 24 * 60 * 60,
  YEAR: 365 * 24 * 60 * 60,
};

// Exportação padrão
export default {
  API_BASE_URL,
  API_TIMEOUT,
  WEBSOCKET_URL,
  ACCESS_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  USER_DATA_KEY,
  AUTH_STATE_KEY,
  JWT_EXPIRATION_MARGIN,
  DEFAULT_PAGE_SIZE,
  MAX_PAGE_SIZE,
  SEARCH_DEBOUNCE_TIME,
  ALLOWED_RESUME_FILE_TYPES,
  MAX_RESUME_FILE_SIZE,
  COLORS,
  MATCH_SCORE_THRESHOLDS,
  MATCH_SCORE_LABELS,
  JOB_TYPES,
  EXPERIENCE_LEVELS,
  WORK_MODELS,
  BRAZILIAN_STATES,
  MAJOR_BRAZILIAN_CITIES,
  ROUTES,
  BREAKPOINTS,
  TIME_CONSTANTS,
};
