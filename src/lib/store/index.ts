/**
 * Store Index
 * Ponto de entrada para o gerenciamento de estado global com Zustand
 */
import { StateCreator, create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { createAuthSlice, AuthSlice, AuthState } from "./slices/authSlice";
import { createJobsSlice, JobsSlice } from "./slices/jobsSlice";
import { createProfileSlice, ProfileSlice } from "./slices/profileSlice";
import { createMatchesSlice, MatchesSlice } from "./slices/matchesSlice";
import { createUISlice, UISlice, UIState } from "./slices/uiSlice";

/**
 * Interface do store global que combina todos os slices
 * Usando uma interface explícita em vez de extends para maior clareza
 */
export interface StoreState {
  // Auth slice
  auth: AuthState;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: any) => void;
  setToken: (token: string | null) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  clearAuthError: () => void;

  // Jobs slice
  jobs: {
    jobs: any[];
    filteredJobs: any[];
    selectedJob: any | null;
    savedJobs: any[];
    jobFilters: any;
    pagination: any;
    loading: boolean;
    error: string | null;
  };
  fetchJobs: (filters?: any) => Promise<void>;
  fetchJobById: (id: string) => Promise<any>;
  fetchSavedJobs: () => Promise<void>;
  saveJob: (jobId: string) => Promise<void>;
  unsaveJob: (jobId: string) => Promise<void>;
  setJobFilters: (filters: any) => void;
  clearJobFilters: () => void;
  setSelectedJob: (job: any | null) => void;

  // Profile slice
  profile: {
    profile: any | null;
    resumes: any[];
    preferences: any | null;
    loading: boolean;
    error: string | null;
  };
  fetchProfile: () => Promise<void>;
  updateProfile: (profile: any) => Promise<void>;
  fetchResumes: () => Promise<void>;
  uploadResume: (file: File) => Promise<void>;
  deleteResume: (resumeId: string) => Promise<void>;
  setPrimaryResume: (resumeId: string) => Promise<void>;
  updatePreferences: (preferences: any) => Promise<void>;

  // Matches slice
  matches: {
    matches: any[];
    selectedMatch: any | null;
    matchFilters: any;
    pagination: any;
    loading: boolean;
    error: string | null;
  };
  fetchMatches: (filters?: any) => Promise<void>;
  fetchMatchById: (id: string) => Promise<any>;
  updateMatchStatus: (matchId: string, status: string) => Promise<void>;
  analyzeMatch: (jobId: string, resumeId: string) => Promise<any>;
  setMatchFilters: (filters: any) => void;
  clearMatchFilters: () => void;
  setSelectedMatch: (match: any | null) => void;

  // UI slice
  ui: UIState;
  toggleTheme: () => void;
  setTheme: (theme: "light" | "dark") => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  addNotification: (notification: any) => void;
  markNotificationAsRead: (notificationId: string) => void;
  clearNotifications: () => void;
  showToast: (options: any) => string;
  dismissToast: (id: string) => void;
  showDialog: (options: any) => string;
  dismissDialog: (id: string) => void;
}

/**
 * Tipo para criadores de slice com tipagem adequada
 */
export type SliceCreator<T> = StateCreator<
  StoreState,
  [["zustand/devtools", never], ["zustand/persist", unknown]],
  [],
  T
>;

/**
 * Configurações de persistência para o store
 */
const persistOptions = {
  name: "linkedin-job-matcher-store",
  partialize: (state: StoreState) => ({
    auth: {
      isAuthenticated: state.auth.isAuthenticated,
      user: state.auth.user,
    },
    ui: {
      theme: state.ui.theme,
      sidebarCollapsed: state.ui.sidebarCollapsed,
      notifications: state.ui.notifications,
    },
    profile: {
      profile: state.profile.profile,
      preferences: state.profile.preferences,
    },
  }),
};

/**
 * Criação do store com todos os slices combinados
 */
export const useStore = create<StoreState>()(
  devtools(
    persist(
      (...a) => ({
        // Combina todos os slices em um único store
        ...createAuthSlice(...a),
        ...createJobsSlice(...a),
        ...createProfileSlice(...a),
        ...createMatchesSlice(...a),
        ...createUISlice(...a),
      }),
      persistOptions
    ),
    {
      name: "LinkedInJobMatcherStore",
      enabled: process.env.NODE_ENV !== "production",
    }
  )
);

/**
 * Hooks especializados para cada slice individual
 * Isso permite que componentes usem apenas a parte do estado que precisam,
 * melhorando a performance ao reduzir re-renderizações
 */

/**
 * Hook para acessar e manipular apenas o estado de autenticação
 */
export const useAuthStore = () => {
  return useStore((state) => ({
    ...state.auth,
    login: state.login,
    register: state.register,
    logout: state.logout,
    setUser: state.setUser,
    setToken: state.setToken,
    setIsAuthenticated: state.setIsAuthenticated,
    clearAuthError: state.clearAuthError,
  }));
};

/**
 * Hook para acessar e manipular apenas o estado das vagas
 */
export const useJobsStore = () => {
  return useStore((state) => ({
    ...state.jobs,
    fetchJobs: state.fetchJobs,
    fetchJobById: state.fetchJobById,
    fetchSavedJobs: state.fetchSavedJobs,
    saveJob: state.saveJob,
    unsaveJob: state.unsaveJob,
    setJobFilters: state.setJobFilters,
    clearJobFilters: state.clearJobFilters,
    setSelectedJob: state.setSelectedJob,
  }));
};

/**
 * Hook para acessar e manipular apenas o estado do perfil
 */
export const useProfileStore = () => {
  return useStore((state) => ({
    ...state.profile,
    fetchProfile: state.fetchProfile,
    updateProfile: state.updateProfile,
    fetchResumes: state.fetchResumes,
    uploadResume: state.uploadResume,
    deleteResume: state.deleteResume,
    setPrimaryResume: state.setPrimaryResume,
    updatePreferences: state.updatePreferences,
  }));
};

/**
 * Hook para acessar e manipular apenas o estado das correspondências
 */
export const useMatchesStore = () => {
  return useStore((state) => ({
    ...state.matches,
    fetchMatches: state.fetchMatches,
    fetchMatchById: state.fetchMatchById,
    updateMatchStatus: state.updateMatchStatus,
    analyzeMatch: state.analyzeMatch,
    setMatchFilters: state.setMatchFilters,
    clearMatchFilters: state.clearMatchFilters,
    setSelectedMatch: state.setSelectedMatch,
  }));
};

/**
 * Hook para acessar e manipular apenas o estado da UI
 */
export const useUIStore = () => {
  return useStore((state) => ({
    ...state.ui,
    toggleTheme: state.toggleTheme,
    setTheme: state.setTheme,
    toggleSidebar: state.toggleSidebar,
    setSidebarCollapsed: state.setSidebarCollapsed,
    addNotification: state.addNotification,
    markNotificationAsRead: state.markNotificationAsRead,
    clearNotifications: state.clearNotifications,
    showToast: state.showToast,
    dismissToast: state.dismissToast,
    showDialog: state.showDialog,
    dismissDialog: state.dismissDialog,
  }));
};

export default useStore;
