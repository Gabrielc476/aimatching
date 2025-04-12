/**
 * Jobs State Slice
 * Gerenciamento de estado para vagas de emprego
 */
import { SliceCreator } from "../index";
import { Job, JobFilters, PaginatedResponse } from "../../types";
import apiClient from "../../api/client";
import { JOB_ENDPOINTS } from "../../api/endpoints";
import { DEFAULT_PAGE_SIZE } from "../../constants";

/**
 * Interface para o estado de paginação
 */
export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

/**
 * Interface para o estado de vagas
 */
export interface JobsState {
  jobs: Job[];
  filteredJobs: Job[];
  selectedJob: Job | null;
  savedJobs: Job[];
  jobFilters: JobFilters;
  pagination: PaginationState;
  loading: boolean;
  error: string | null;
}

/**
 * Interface para as ações do slice de vagas
 */
export interface JobsActions {
  fetchJobs: (filters?: JobFilters) => Promise<void>;
  fetchJobById: (id: string) => Promise<Job>;
  fetchSavedJobs: () => Promise<void>;
  saveJob: (jobId: string) => Promise<void>;
  unsaveJob: (jobId: string) => Promise<void>;
  setJobFilters: (filters: Partial<JobFilters>) => void;
  clearJobFilters: () => void;
  setSelectedJob: (job: Job | null) => void;
}

/**
 * Interface completa do slice de vagas (estado + ações)
 */
export interface JobsSlice {
  jobs: JobsState;
  fetchJobs: JobsActions["fetchJobs"];
  fetchJobById: JobsActions["fetchJobById"];
  fetchSavedJobs: JobsActions["fetchSavedJobs"];
  saveJob: JobsActions["saveJob"];
  unsaveJob: JobsActions["unsaveJob"];
  setJobFilters: JobsActions["setJobFilters"];
  clearJobFilters: JobsActions["clearJobFilters"];
  setSelectedJob: JobsActions["setSelectedJob"];
}

/**
 * Estado de paginação inicial
 */
const initialPagination: PaginationState = {
  page: 1,
  pageSize: DEFAULT_PAGE_SIZE,
  total: 0,
  totalPages: 0,
};

/**
 * Estado inicial de vagas
 */
const initialState: JobsState = {
  jobs: [],
  filteredJobs: [],
  selectedJob: null,
  savedJobs: [],
  jobFilters: {
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
  },
  pagination: initialPagination,
  loading: false,
  error: null,
};

/**
 * Criador do slice de vagas
 */
export const createJobsSlice: SliceCreator<JobsSlice> = (set, get) => ({
  jobs: { ...initialState },

  /**
   * Busca vagas com filtros opcionais
   */
  fetchJobs: async (filters?: JobFilters) => {
    try {
      // Combina filtros atuais com novos filtros, se houver
      const currentFilters = get().jobs.jobFilters;
      const mergedFilters = filters
        ? { ...currentFilters, ...filters }
        : currentFilters;

      // Atualiza estado para loading
      set((state) => ({
        jobs: {
          ...state.jobs,
          loading: true,
          error: null,
          jobFilters: mergedFilters,
        },
      }));

      // Busca vagas na API
      const response = await apiClient.post<PaginatedResponse<Job>>(
        JOB_ENDPOINTS.SEARCH_JOBS.path,
        mergedFilters
      );

      // Atualiza estado com os resultados
      set((state) => ({
        jobs: {
          ...state.jobs,
          jobs: response.items,
          filteredJobs: response.items,
          pagination: {
            page: response.page,
            pageSize: response.pageSize,
            total: response.total,
            totalPages: response.totalPages,
          },
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao buscar vagas. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        jobs: {
          ...state.jobs,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching jobs:", error);
    }
  },

  /**
   * Busca uma vaga específica pelo ID
   */
  fetchJobById: async (id: string) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        jobs: {
          ...state.jobs,
          loading: true,
          error: null,
        },
      }));

      // Busca vaga na API
      const job = await apiClient.get<Job>(
        JOB_ENDPOINTS.GET_JOB.path.replace(":id", id)
      );

      // Atualiza estado com a vaga selecionada
      set((state) => ({
        jobs: {
          ...state.jobs,
          selectedJob: job,
          loading: false,
        },
      }));

      return job;
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao buscar detalhes da vaga. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        jobs: {
          ...state.jobs,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching job by ID:", error);
      throw error;
    }
  },

  /**
   * Busca vagas salvas pelo usuário
   */
  fetchSavedJobs: async () => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        jobs: {
          ...state.jobs,
          loading: true,
          error: null,
        },
      }));

      // Busca vagas salvas na API
      const savedJobs = await apiClient.get<Job[]>(
        JOB_ENDPOINTS.GET_SAVED_JOBS.path
      );

      // Atualiza estado com as vagas salvas
      set((state) => ({
        jobs: {
          ...state.jobs,
          savedJobs,
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao buscar vagas salvas. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        jobs: {
          ...state.jobs,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching saved jobs:", error);
    }
  },

  /**
   * Salva uma vaga
   */
  saveJob: async (jobId: string) => {
    try {
      // Envia requisição para salvar vaga
      await apiClient.post(JOB_ENDPOINTS.SAVE_JOB.path.replace(":id", jobId));

      // Busca a vaga nos jobs atuais
      const jobToSave = get().jobs.jobs.find((job) => job.id === jobId);

      if (jobToSave) {
        // Atualiza estado com a nova vaga salva
        set((state) => ({
          jobs: {
            ...state.jobs,
            savedJobs: [...state.jobs.savedJobs, jobToSave],
          },
        }));
      } else {
        // Se a vaga não estiver nos jobs atuais, busca detalhes e adiciona
        const job = await get().fetchJobById(jobId);

        set((state) => ({
          jobs: {
            ...state.jobs,
            savedJobs: [...state.jobs.savedJobs, job],
          },
        }));
      }
    } catch (error) {
      console.error("Error saving job:", error);
      throw error;
    }
  },

  /**
   * Remove uma vaga das salvas
   */
  unsaveJob: async (jobId: string) => {
    try {
      // Envia requisição para remover vaga
      await apiClient.delete(
        JOB_ENDPOINTS.UNSAVE_JOB.path.replace(":id", jobId)
      );

      // Atualiza estado removendo a vaga das salvas
      set((state) => ({
        jobs: {
          ...state.jobs,
          savedJobs: state.jobs.savedJobs.filter((job) => job.id !== jobId),
        },
      }));
    } catch (error) {
      console.error("Error unsaving job:", error);
      throw error;
    }
  },

  /**
   * Define filtros de busca de vagas
   */
  setJobFilters: (filters: Partial<JobFilters>) => {
    set((state) => ({
      jobs: {
        ...state.jobs,
        jobFilters: { ...state.jobs.jobFilters, ...filters },
      },
    }));

    // Refaz a busca com os novos filtros
    get().fetchJobs();
  },

  /**
   * Limpa todos os filtros de busca
   */
  clearJobFilters: () => {
    const defaultFilters = {
      page: 1,
      pageSize: DEFAULT_PAGE_SIZE,
    };

    set((state) => ({
      jobs: {
        ...state.jobs,
        jobFilters: defaultFilters,
      },
    }));

    // Refaz a busca sem filtros
    get().fetchJobs(defaultFilters);
  },

  /**
   * Define a vaga selecionada
   */
  setSelectedJob: (job: Job | null) => {
    set((state) => ({
      jobs: {
        ...state.jobs,
        selectedJob: job,
      },
    }));
  },
});
