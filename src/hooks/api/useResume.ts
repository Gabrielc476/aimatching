import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "../useToast";
import { buildEndpointUrl } from "@/lib/api/endpoints";
import { Resume, SkillGapAnalysis } from "@/lib/types";
import { ENDPOINTS, EndpointCategory } from "@/lib/api/endpoints";

export function useResume() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Buscar currículos do usuário
  const fetchResumes = async (): Promise<Resume[]> => {
    return await apiClient.get(
      ENDPOINTS[EndpointCategory.RESUME].GET_RESUMES.path
    );
  };

  // Buscar detalhes de um currículo específico
  const fetchResumeById = async (id: string): Promise<Resume> => {
    const url = buildEndpointUrl(
      ENDPOINTS[EndpointCategory.RESUME].GET_RESUME.path,
      { id }
    );
    return await apiClient.get(url);
  };

  // Fazer upload de um novo currículo
  const uploadResume = useMutation({
    mutationFn: async ({
      file,
      isPrimary = false,
    }: {
      file: File;
      isPrimary?: boolean;
    }): Promise<Resume> => {
      return await apiClient.uploadFile(
        ENDPOINTS[EndpointCategory.RESUME].UPLOAD_RESUME.path,
        file,
        "file",
        { isPrimary: String(isPrimary) }
      );
    },
    onSuccess: () => {
      toast({
        title: "Currículo enviado",
        description: "Seu currículo foi enviado e analisado com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => {
      toast({
        title: "Erro ao enviar currículo",
        description:
          "Ocorreu um erro ao enviar seu currículo. Tente novamente.",
        type: "error",
      });
    },
  });

  // Definir um currículo como principal
  const setPrimaryResume = useMutation({
    mutationFn: async (resumeId: string): Promise<Resume> => {
      const url = buildEndpointUrl(
        ENDPOINTS[EndpointCategory.RESUME].SET_PRIMARY_RESUME.path,
        { id: resumeId }
      );
      return await apiClient.patch(url);
    },
    onSuccess: () => {
      toast({
        title: "Currículo principal definido",
        description: "Seu currículo principal foi atualizado com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
    onError: () => {
      toast({
        title: "Erro ao definir currículo principal",
        description: "Ocorreu um erro ao definir o currículo principal.",
        type: "error",
      });
    },
  });

  // Excluir um currículo
  const deleteResume = useMutation({
    mutationFn: async (resumeId: string): Promise<void> => {
      const url = buildEndpointUrl(
        ENDPOINTS[EndpointCategory.RESUME].DELETE_RESUME.path,
        { id: resumeId }
      );
      return await apiClient.delete(url);
    },
    onSuccess: () => {
      toast({
        title: "Currículo excluído",
        description: "Seu currículo foi excluído com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
    onError: () => {
      toast({
        title: "Erro ao excluir currículo",
        description: "Ocorreu um erro ao excluir seu currículo.",
        type: "error",
      });
    },
  });

  // Analisar currículo para recomendações
  const analyzeResume = useMutation({
    mutationFn: async (resumeId: string): Promise<SkillGapAnalysis> => {
      const url = buildEndpointUrl(
        ENDPOINTS[EndpointCategory.RESUME].ANALYZE_RESUME.path,
        { id: resumeId }
      );
      return await apiClient.post(url);
    },
    onSuccess: () => {
      toast({
        title: "Análise concluída",
        description: "Seu currículo foi analisado com sucesso.",
        type: "success",
      });
    },
    onError: () => {
      toast({
        title: "Erro na análise",
        description: "Ocorreu um erro ao analisar seu currículo.",
        type: "error",
      });
    },
  });

  // Query para listar currículos
  const resumesQuery = useQuery<Resume[]>({
    queryKey: ["resumes"],
    queryFn: fetchResumes,
  });

  return {
    // Query
    resumesQuery,

    // Methods
    fetchResumeById,
    uploadResume: uploadResume.mutate,
    setPrimaryResume: setPrimaryResume.mutate,
    deleteResume: deleteResume.mutate,
    analyzeResume: analyzeResume.mutate,

    // Mutation states
    isUploading: uploadResume.isPending,
    isSettingPrimary: setPrimaryResume.isPending,
    isDeleting: deleteResume.isPending,
    isAnalyzing: analyzeResume.isPending,

    // Query states
    isLoading: resumesQuery.isLoading,
    isError: resumesQuery.isError,
    resumes: resumesQuery.data,
    error: resumesQuery.error,
  };
}
