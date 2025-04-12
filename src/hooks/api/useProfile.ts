import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "../useToast";
import { UserProfile, UserPreferences, Skill } from "@/lib/types";
import { ENDPOINTS, EndpointCategory } from "@/lib/api/endpoints";

export function useProfile() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Buscar perfil do usuário
  const fetchProfile = async (): Promise<UserProfile> => {
    return await apiClient.get(
      ENDPOINTS[EndpointCategory.PROFILE].GET_PROFILE.path
    );
  };

  // Atualizar perfil do usuário
  const updateProfile = useMutation({
    mutationFn: async (
      profileData: Partial<UserProfile>
    ): Promise<UserProfile> => {
      return await apiClient.put(
        ENDPOINTS[EndpointCategory.PROFILE].UPDATE_PROFILE.path,
        profileData
      );
    },
    onSuccess: () => {
      toast({
        title: "Perfil atualizado",
        description: "Seu perfil foi atualizado com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => {
      toast({
        title: "Erro ao atualizar perfil",
        description:
          "Ocorreu um erro ao atualizar seu perfil. Tente novamente.",
        type: "error",
      });
    },
  });

  // Atualizar preferências de emprego
  const updateJobPreferences = useMutation({
    mutationFn: async (preferences: UserPreferences): Promise<UserProfile> => {
      return await apiClient.patch(
        ENDPOINTS[EndpointCategory.PROFILE].UPDATE_PREFERENCES.path,
        preferences
      );
    },
    onSuccess: () => {
      toast({
        title: "Preferências atualizadas",
        description:
          "Suas preferências de emprego foram atualizadas com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => {
      toast({
        title: "Erro ao atualizar preferências",
        description:
          "Ocorreu um erro ao atualizar suas preferências de emprego.",
        type: "error",
      });
    },
  });

  // Atualizar habilidades
  const updateSkills = useMutation({
    mutationFn: async (skills: Skill[]): Promise<UserProfile> => {
      return await apiClient.patch(
        ENDPOINTS[EndpointCategory.PROFILE].UPDATE_SKILLS.path,
        { skills }
      );
    },
    onSuccess: () => {
      toast({
        title: "Habilidades atualizadas",
        description: "Suas habilidades foram atualizadas com sucesso.",
        type: "success",
      });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => {
      toast({
        title: "Erro ao atualizar habilidades",
        description: "Ocorreu um erro ao atualizar suas habilidades.",
        type: "error",
      });
    },
  });

  // Query para buscar perfil
  const profileQuery = useQuery<UserProfile>({
    queryKey: ["profile"],
    queryFn: fetchProfile,
  });

  return {
    // Query
    profileQuery,

    // Methods
    updateProfile: updateProfile.mutate,
    updateJobPreferences: updateJobPreferences.mutate,
    updateSkills: updateSkills.mutate,

    // Mutation states
    isUpdating: updateProfile.isPending,
    isUpdatingPreferences: updateJobPreferences.isPending,
    isUpdatingSkills: updateSkills.isPending,

    // Query states
    isLoading: profileQuery.isLoading,
    isError: profileQuery.isError,
    profile: profileQuery.data,
    error: profileQuery.error,
  };
}
