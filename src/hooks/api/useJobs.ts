import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "../useToast";
import {
  buildEndpointUrl,
  ENDPOINTS,
  EndpointCategory, // Agora importando do local correto
} from "@/lib/api/endpoints";
import { Job, JobFilters, PaginatedResponse } from "@/lib/types";

export function useJobs(filters?: JobFilters) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Buscar vagas com filtros (paginada)
  const fetchJobs = async (
    filters?: JobFilters
  ): Promise<PaginatedResponse<Job>> => {
    if (filters) {
      return await apiClient.post(
        ENDPOINTS[EndpointCategory.JOBS].SEARCH_JOBS.path,
        filters
      );
    } else {
      return await apiClient.get(
        ENDPOINTS[EndpointCategory.JOBS].GET_JOBS.path
      );
    }
  };

  // Buscar detalhes de uma vaga específica
  const fetchJobById = async (id: string): Promise<Job> => {
    const url = buildEndpointUrl(
      ENDPOINTS[EndpointCategory.JOBS].GET_JOB.path,
      { id }
    );
    return await apiClient.get(url);
  };

  // Salvar uma vaga (favoritar)
  const saveJob = useMutation({
    mutationFn: async (jobId: string) => {
      const url = buildEndpointUrl(
        ENDPOINTS[EndpointCategory.JOBS].SAVE_JOB.path,
        { id: jobId }
      );
      return await apiClient.post(url);
    },
    onSuccess: () => {
      toast({
        title: "Vaga salva",
        description: "Vaga adicionada às suas vagas salvas.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["savedJobs"] });
    },
    onError: () => {
      toast({
        title: "Erro ao salvar vaga",
        description: "Ocorreu um erro ao salvar a vaga. Tente novamente.",
        type: "error",
      });
    },
  });

  // Remover uma vaga dos salvos
  const unsaveJob = useMutation({
    mutationFn: async (jobId: string) => {
      const url = buildEndpointUrl(
        ENDPOINTS[EndpointCategory.JOBS].UNSAVE_JOB.path,
        { id: jobId }
      );
      return await apiClient.delete(url);
    },
    onSuccess: () => {
      toast({
        title: "Vaga removida",
        description: "Vaga removida das suas vagas salvas.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["savedJobs"] });
    },
    onError: () => {
      toast({
        title: "Erro ao remover vaga",
        description:
          "Ocorreu um erro ao remover a vaga salva. Tente novamente.",
        type: "error",
      });
    },
  });

  // Buscar vagas salvas
  const fetchSavedJobs = async (): Promise<PaginatedResponse<Job>> => {
    return await apiClient.get(
      ENDPOINTS[EndpointCategory.JOBS].GET_SAVED_JOBS.path
    );
  };

  // Query para listar vagas
  const jobsQuery = useQuery<PaginatedResponse<Job>>({
    queryKey: ["jobs", filters],
    queryFn: () => fetchJobs(filters),
  });

  // Query para vagas salvas
  const savedJobsQuery = useQuery<PaginatedResponse<Job>>({
    queryKey: ["savedJobs"],
    queryFn: fetchSavedJobs,
    enabled: false, // Não busca automaticamente, apenas quando solicitado
  });

  return {
    // Queries
    jobsQuery,
    savedJobsQuery,

    // Methods
    fetchJobById,
    saveJob,
    unsaveJob,

    // State
    isLoading: jobsQuery.isLoading,
    isError: jobsQuery.isError,
    data: jobsQuery.data,
    error: jobsQuery.error,
  };
}
