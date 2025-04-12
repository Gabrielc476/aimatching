/**
 * Common Types
 * Tipos TypeScript comuns para uso em toda a aplicação
 */

/**
 * Enums
 */

// Níveis de habilidade
export enum SkillLevel {
  BEGINNER = "beginner",
  INTERMEDIATE = "intermediate",
  ADVANCED = "advanced",
  EXPERT = "expert",
}

// Tipos de emprego
export enum JobType {
  FULL_TIME = "full_time",
  PART_TIME = "part_time",
  CONTRACT = "contract",
  TEMPORARY = "temporary",
  INTERNSHIP = "internship",
  VOLUNTEER = "volunteer",
  FREELANCE = "freelance",
}

// Níveis de experiência
export enum ExperienceLevel {
  INTERNSHIP = "internship",
  ENTRY_LEVEL = "entry_level",
  MID_LEVEL = "mid_level",
  SENIOR_LEVEL = "senior_level",
  EXECUTIVE = "executive",
}

// Modelos de trabalho
export enum WorkModel {
  ON_SITE = "on_site",
  HYBRID = "hybrid",
  REMOTE = "remote",
}

// Status de correspondência
export enum MatchStatus {
  NEW = "new",
  VIEWED = "viewed",
  APPLIED = "applied",
  SAVED = "saved",
  REJECTED = "rejected",
  INTERVIEW = "interview",
  OFFERED = "offered",
  HIRED = "hired",
  DECLINED = "declined",
}

// Tipos de notificação
export enum NotificationType {
  NEW_MATCH = "new_match",
  JOB_UPDATE = "job_update",
  APPLICATION_UPDATE = "application_update",
  SYSTEM = "system",
  RESUME_ANALYSIS = "resume_analysis",
}

// Níveis de pontuação da correspondência
export enum MatchScoreLevel {
  EXCELLENT = "excellent",
  GOOD = "good",
  FAIR = "fair",
  POOR = "poor",
}

/**
 * Interfaces
 */

// Tokens de Autenticação
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn?: number;
  tokenType?: string;
}

// Usuário
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  profile?: UserProfile;
  resumes?: Resume[];
  preferences?: UserPreferences;
}

// Perfil do usuário
export interface UserProfile {
  id: string;
  userId: string;
  title?: string;
  location?: string;
  skills?: Skill[];
  experienceLevel?: ExperienceLevel;
  jobPreferences?: UserPreferences;
  updatedAt: string;
}

// Preferências do usuário
export interface UserPreferences {
  jobTypes?: JobType[];
  experienceLevels?: ExperienceLevel[];
  workModels?: WorkModel[];
  locations?: string[];
  minSalary?: number;
  industries?: string[];
  notificationFrequency?: "daily" | "weekly" | "realtime";
  emailNotifications?: boolean;
}

// Habilidade
export interface Skill {
  id?: string;
  name: string;
  level?: SkillLevel;
  yearsOfExperience?: number;
  category?: string;
  endorsements?: number;
}

// Currículo
export interface Resume {
  id: string;
  userId: string;
  filename: string;
  contentType: string;
  url?: string;
  parsedContent?: {
    personalInfo?: PersonalInfo;
    skills?: Skill[];
    experience?: Experience[];
    education?: Education[];
    certifications?: Certification[];
    languages?: Language[];
  };
  uploadedAt: string;
  isPrimary: boolean;
}

// Informações pessoais
export interface PersonalInfo {
  name: string;
  email: string;
  phone?: string;
  address?: string;
  linkedIn?: string;
  github?: string;
  website?: string;
  summary?: string;
}

// Experiência profissional
export interface Experience {
  id?: string;
  company: string;
  title: string;
  location?: string;
  startDate: string;
  endDate?: string;
  current?: boolean;
  description?: string;
  skills?: string[];
  highlights?: string[];
}

// Educação
export interface Education {
  id?: string;
  institution: string;
  degree: string;
  fieldOfStudy?: string;
  startDate: string;
  endDate?: string;
  current?: boolean;
  description?: string;
  achievements?: string[];
}

// Certificação
export interface Certification {
  id?: string;
  name: string;
  issuer: string;
  issueDate?: string;
  expirationDate?: string;
  credentialId?: string;
  url?: string;
}

// Idioma
export interface Language {
  name: string;
  proficiency: "basic" | "intermediate" | "advanced" | "fluent" | "native";
}

// Vaga
export interface Job {
  id: string;
  linkedinId: string;
  title: string;
  company: string;
  location?: string;
  description?: string;
  requirements?: {
    skills?: string[];
    education?: string[];
    experience?: string[];
    other?: string[];
  };
  salaryRange?: {
    min?: number;
    max?: number;
    currency?: string;
  };
  jobType?: JobType;
  experienceLevel?: ExperienceLevel;
  workModel?: WorkModel;
  skills?: string[];
  url: string;
  postedAt?: string;
  scrapedAt: string;
  isActive: boolean;
}

// Correspondência
export interface Match {
  id: string;
  userId: string;
  jobId: string;
  resumeId: string;
  score: number;
  scoreLevel?: MatchScoreLevel;
  matchDetails: {
    skillsScore: number;
    experienceScore: number;
    educationScore: number;
    strengths?: string[];
    weaknesses?: string[];
    recommendations?: string[];
    matchedSkills?: string[];
    missingSkills?: string[];
  };
  createdAt: string;
  status: MatchStatus;
  job?: Job;
  resume?: Resume;
}

// Notificação
export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  link?: string;
  isRead: boolean;
  relatedEntityId?: string;
  relatedEntityType?: "job" | "match" | "resume";
  createdAt: string;
}

// Filtros de busca de vagas
export interface JobFilters {
  query?: string;
  location?: string[];
  jobTypes?: JobType[];
  experienceLevels?: ExperienceLevel[];
  workModels?: WorkModel[];
  skills?: string[];
  postedAfter?: string;
  minSalary?: number;
  maxSalary?: number;
  company?: string[];
  isRemote?: boolean;
  page?: number;
  pageSize?: number;
  sortBy?: "relevance" | "date" | "salary";
  sortOrder?: "asc" | "desc";
}

// Filtros de busca de correspondências
export interface MatchFilters {
  scoreLevel?: MatchScoreLevel[];
  status?: MatchStatus[];
  jobTypes?: JobType[];
  experienceLevels?: ExperienceLevel[];
  workModels?: WorkModel[];
  matchedAfter?: string;
  page?: number;
  pageSize?: number;
  sortBy?: "score" | "date";
  sortOrder?: "asc" | "desc";
}

// Resposta paginada
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// Análise de mercado
export interface MarketInsight {
  skill: string;
  demandLevel: "high" | "medium" | "low";
  averageSalary?: number;
  growthRate?: number;
  jobCount: number;
  topCompanies?: { name: string; count: number }[];
  relatedSkills?: { name: string; correlation: number }[];
}

// Análise de lacuna de habilidades
export interface SkillGapAnalysis {
  missingSkills: {
    name: string;
    demandLevel: "high" | "medium" | "low";
    matchImpact: number;
    recommendedResources?: string[];
  }[];
  improvableSkills: {
    name: string;
    currentLevel?: SkillLevel;
    recommendedLevel: SkillLevel;
    matchImpact: number;
  }[];
  strongSkills: {
    name: string;
    level?: SkillLevel;
    marketValue: "high" | "medium" | "low";
  }[];
}

// Recomendação para candidatura
export interface ApplicationRecommendation {
  matchId: string;
  jobId: string;
  resumeTweaks?: {
    section: "summary" | "experience" | "skills" | "education";
    suggestion: string;
    reason: string;
    priority: "high" | "medium" | "low";
  }[];
  coverLetterSuggestions?: {
    keyPoints: string[];
    skillsToHighlight: string[];
    experienceToEmphasize: string[];
    template?: string;
  };
  preparationTips?: string[];
}

// Meta Tags para SEO
export interface MetaTags {
  title: string;
  description: string;
  keywords?: string[];
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  canonical?: string;
}

// Opções de Toast
export interface ToastOptions {
  title?: string;
  description: string;
  type?: "default" | "success" | "error" | "warning" | "info";
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  position?:
    | "top-right"
    | "top-left"
    | "bottom-right"
    | "bottom-left"
    | "top-center"
    | "bottom-center";
}

// Opções para componente de diálogo
export interface DialogOptions {
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
  type?: "default" | "danger" | "warning" | "info";
  isDismissable?: boolean;
}

// Navegação do breadcrumb
export interface BreadcrumbItem {
  label: string;
  href?: string;
  isCurrent?: boolean;
}

// Parâmetros para componente de paginação
export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  siblingsCount?: number;
  boundaryCount?: number;
}

// Parâmetros para componentes de tabela
export interface TableColumn<T> {
  header: string;
  accessor: keyof T | ((row: T) => any);
  cell?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
  width?: string | number;
}

// Parâmetros para componentes de gráfico
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
  }[];
}

/**
 * Types
 */

// Tipo para funções de retorno de chamada
export type VoidFunction = () => void;
export type PromiseVoidFunction = () => Promise<void>;
export type CallbackFunction<T = any, R = any> = (param: T) => R;

// Tipo para componentes com crianças
export type WithChildren<T = {}> = T & { children?: React.ReactNode };
