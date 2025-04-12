/**
 * Matches State Slice
 * Gerenciamento de estado para correspondências entre currículos e vagas
 */
import { SliceCreator } from "../index";
import {
  Match,
  MatchFilters,
  MatchStatus,
  PaginatedResponse,
} from "../../types";
import apiClient from "../../api/client";
import { MATCH_ENDPOINTS } from "../../api/endpoints";
import { DEFAULT_PAGE_SIZE } from "../../constants";
import { PaginationState } from "./jobsSlice";

/**
 * Interface para o estado de correspondências
 */
export interface MatchesState {
  matches: Match[];
  selectedMatch: Match | null;
  matchFilters: MatchFilters;
  pagination: PaginationState;
  loading: boolean;
  error: string | null;
}

/**
 * Interface para as ações do slice de correspondências
 */
export interface MatchesActions {
  fetchMatches: (filters?: MatchFilters) => Promise<void>;
  fetchMatchById: (id: string) => Promise<Match>;
  updateMatchStatus: (matchId: string, status: MatchStatus) => Promise<void>;
  analyzeMatch: (jobId: string, resumeId: string) => Promise<Match>;
  setMatchFilters: (filters: Partial<MatchFilters>) => void;
  clearMatchFilters: () => void;
  setSelectedMatch: (match: Match | null) => void;
}

/**
 * Interface completa do slice de correspondências (estado + ações)
 */
export interface MatchesSlice {
  matches: MatchesState;
  fetchMatches: MatchesActions["fetchMatches"];
  fetchMatchById: MatchesActions["fetchMatchById"];
  updateMatchStatus: MatchesActions["updateMatchStatus"];
  analyzeMatch: MatchesActions["analyzeMatch"];
  setMatchFilters: MatchesActions["setMatchFilters"];
  clearMatchFilters: MatchesActions["clearMatchFilters"];
  setSelectedMatch: MatchesActions["setSelectedMatch"];
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
 * Estado inicial de correspondências
 */
const initialState: MatchesState = {
  matches: [],
  selectedMatch: null,
  matchFilters: {
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
  },
  pagination: initialPagination,
  loading: false,
  error: null,
};

/**
 * Criador do slice de correspondências
 */
export const createMatchesSlice: SliceCreator<MatchesSlice> = (set, get) => ({
  matches: { ...initialState },

  /**
   * Busca correspondências com filtros opcionais
   */
  fetchMatches: async (filters?: MatchFilters) => {
    try {
      // Combina filtros atuais com novos filtros, se houver
      const currentFilters = get().matches.matchFilters;
      const mergedFilters = filters
        ? { ...currentFilters, ...filters }
        : currentFilters;

      // Atualiza estado para loading
      set((state) => ({
        matches: {
          ...state.matches,
          loading: true,
          error: null,
          matchFilters: mergedFilters,
        },
      }));

      // Busca correspondências na API
      const response = await apiClient.get<PaginatedResponse<Match>>(
        MATCH_ENDPOINTS.GET_MATCHES.path,
        {
          params: mergedFilters,
        }
      );

      // Atualiza estado com os resultados
      set((state) => ({
        matches: {
          ...state.matches,
          matches: response.items,
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
          : "Erro ao buscar correspondências. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        matches: {
          ...state.matches,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching matches:", error);
    }
  },

  /**
   * Busca uma correspondência específica pelo ID
   */
  fetchMatchById: async (id: string) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        matches: {
          ...state.matches,
          loading: true,
          error: null,
        },
      }));

      // Busca correspondência na API
      const match = await apiClient.get<Match>(
        MATCH_ENDPOINTS.GET_MATCH.path.replace(":id", id)
      );

      // Atualiza estado com a correspondência selecionada
      set((state) => ({
        matches: {
          ...state.matches,
          selectedMatch: match,
          loading: false,
        },
      }));

      return match;
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao buscar detalhes da correspondência. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        matches: {
          ...state.matches,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching match by ID:", error);
      throw error;
    }
  },

  /**
   * Atualiza o status de uma correspondência
   */
  updateMatchStatus: async (matchId: string, status: MatchStatus) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        matches: {
          ...state.matches,
          loading: true,
          error: null,
        },
      }));

      // Atualiza status na API
      await apiClient.patch(
        MATCH_ENDPOINTS.UPDATE_MATCH_STATUS.path.replace(":id", matchId),
        { status }
      );

      // Atualiza estado local
      set((state) => ({
        matches: {
          ...state.matches,
          // Atualiza nos matches gerais
          matches: state.matches.matches.map((match) =>
            match.id === matchId ? { ...match, status } : match
          ),
          // Atualiza no match selecionado, se for o mesmo
          selectedMatch:
            state.matches.selectedMatch &&
            state.matches.selectedMatch.id === matchId
              ? { ...state.matches.selectedMatch, status }
              : state.matches.selectedMatch,
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao atualizar status da correspondência. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        matches: {
          ...state.matches,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error updating match status:", error);
      throw error;
    }
  },

  /**
   * Analisa a correspondência entre um currículo e uma vaga
   */
  analyzeMatch: async (jobId: string, resumeId: string) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        matches: {
          ...state.matches,
          loading: true,
          error: null,
        },
      }));

      // Solicita análise na API
      const match = await apiClient.post<Match>(
        MATCH_ENDPOINTS.ANALYZE_MATCH.path,
        { jobId, resumeId }
      );

      // Atualiza estado com a nova correspondência
      set((state) => ({
        matches: {
          ...state.matches,
          // Adiciona aos matches se não existir
          matches: state.matches.matches.some((m) => m.id === match.id)
            ? state.matches.matches.map((m) => (m.id === match.id ? match : m))
            : [match, ...state.matches.matches],
          selectedMatch: match,
          loading: false,
        },
      }));

      return match;
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao analisar correspondência. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        matches: {
          ...state.matches,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error analyzing match:", error);
      throw error;
    }
  },

  /**
   * Define filtros de busca de correspondências
   */
  setMatchFilters: (filters: Partial<MatchFilters>) => {
    set((state) => ({
      matches: {
        ...state.matches,
        matchFilters: { ...state.matches.matchFilters, ...filters },
      },
    }));

    // Refaz a busca com os novos filtros
    get().fetchMatches();
  },

  /**
   * Limpa todos os filtros de busca
   */
  clearMatchFilters: () => {
    const defaultFilters = {
      page: 1,
      pageSize: DEFAULT_PAGE_SIZE,
    };

    set((state) => ({
      matches: {
        ...state.matches,
        matchFilters: defaultFilters,
      },
    }));

    // Refaz a busca sem filtros
    get().fetchMatches(defaultFilters);
  },

  /**
   * Define a correspondência selecionada
   */
  setSelectedMatch: (match: Match | null) => {
    set((state) => ({
      matches: {
        ...state.matches,
        selectedMatch: match,
      },
    }));
  },
});
