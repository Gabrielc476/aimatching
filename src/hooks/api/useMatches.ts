import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "../useToast";
import {
  ENDPOINTS,
  EndpointCategory,
  buildEndpointUrl,
} from "@/lib/api/endpoints";
import {
  Match,
  MatchStatus,
  ApplicationRecommendation,
  PaginatedResponse,
} from "@/lib/types";

// Como MatchAnalysis não está disponível no módulo types, vamos definir uma interface básica
interface MatchAnalysis {
  score: number;
  skillsScore: number;
  experienceScore: number;
  educationScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export function useMatches() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Buscar todas as correspondências do usuário
  const fetchMatches = async (): Promise<PaginatedResponse<Match>> => {
    return await apiClient.get(
      ENDPOINTS[EndpointCategory.MATCHES].GET_MATCHES.path
    );
  };

  // Buscar detalhes de uma correspondência específica
  const fetchMatchById = async (id: string): Promise<Match> => {
    const url = buildEndpointUrl(
      ENDPOINTS[EndpointCategory.MATCHES].GET_MATCH.path,
      { id }
    );
    return await apiClient.get(url);
  };

  // Solicitar análise detalhada de correspondência entre currículo e vaga
  const analyzeMatch = async (payload: {
    resumeId: string;
    jobId: string;
  }): Promise<MatchAnalysis> => {
    return await apiClient.post(
      ENDPOINTS[EndpointCategory.MATCHES].ANALYZE_MATCH.path,
      payload
    );
  };

  // Atualizar status de uma correspondência (e.g., "applied", "rejected")
  const updateMatchStatus = useMutation({
    mutationFn: async ({
      matchId,
      status,
    }: {
      matchId: string;
      status: MatchStatus;
    }) => {
      const url = buildEndpointUrl(
        ENDPOINTS[EndpointCategory.MATCHES].UPDATE_MATCH_STATUS.path,
        { id: matchId }
      );
      return await apiClient.patch(url, { status });
    },
    onSuccess: () => {
      toast({
        title: "Status atualizado",
        description: "O status da correspondência foi atualizado com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["matches"] });
    },
    onError: () => {
      toast({
        title: "Erro ao atualizar status",
        description:
          "Ocorreu um erro ao atualizar o status da correspondência.",
        type: "error",
      });
    },
  });

  // Buscar recomendações para melhorar correspondência
  const fetchMatchRecommendations = async (
    matchId: string
  ): Promise<ApplicationRecommendation> => {
    const url = buildEndpointUrl(
      ENDPOINTS[EndpointCategory.MATCHES].GET_MATCH_RECOMMENDATIONS.path,
      { id: matchId }
    );
    return await apiClient.get(url);
  };

  // Query para listar correspondências
  const matchesQuery = useQuery<PaginatedResponse<Match>>({
    queryKey: ["matches"],
    queryFn: fetchMatches,
  });

  // Mutation para analisar correspondência
  const analyzeMatchMutation = useMutation({
    mutationFn: analyzeMatch,
    onSuccess: () => {
      toast({
        title: "Análise concluída",
        description: "A análise de compatibilidade foi concluída com sucesso.",
        type: "success",
      });
    },
    onError: () => {
      toast({
        title: "Erro na análise",
        description: "Ocorreu um erro ao analisar a compatibilidade.",
        type: "error",
      });
    },
  });

  return {
    // Queries
    matchesQuery,

    // Methods
    fetchMatchById,
    analyzeMatch: analyzeMatchMutation.mutate,
    updateMatchStatus: updateMatchStatus.mutate,
    fetchMatchRecommendations,

    // Mutation states
    isAnalyzing: analyzeMatchMutation.isPending,
    isUpdatingStatus: updateMatchStatus.isPending,

    // Query states
    isLoading: matchesQuery.isLoading,
    isError: matchesQuery.isError,
    data: matchesQuery.data,
    error: matchesQuery.error,
  };
}
