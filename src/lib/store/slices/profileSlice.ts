/**
 * Profile State Slice
 * Gerenciamento de estado para perfil do usuário e currículos
 */
import { SliceCreator } from "../index";
import { Resume, UserPreferences, UserProfile } from "../../types";
import apiClient from "../../api/client";
import { PROFILE_ENDPOINTS, RESUME_ENDPOINTS } from "../../api/endpoints";

/**
 * Interface para o estado do perfil
 */
export interface ProfileState {
  profile: UserProfile | null;
  resumes: Resume[];
  preferences: UserPreferences | null;
  loading: boolean;
  error: string | null;
}

/**
 * Interface para as ações do slice de perfil
 */
export interface ProfileActions {
  fetchProfile: () => Promise<void>;
  updateProfile: (profile: Partial<UserProfile>) => Promise<void>;
  fetchResumes: () => Promise<void>;
  uploadResume: (file: File) => Promise<void>;
  deleteResume: (resumeId: string) => Promise<void>;
  setPrimaryResume: (resumeId: string) => Promise<void>;
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<void>;
}

/**
 * Interface completa do slice de perfil (estado + ações)
 */
export interface ProfileSlice {
  profile: ProfileState;
  fetchProfile: ProfileActions["fetchProfile"];
  updateProfile: ProfileActions["updateProfile"];
  fetchResumes: ProfileActions["fetchResumes"];
  uploadResume: ProfileActions["uploadResume"];
  deleteResume: ProfileActions["deleteResume"];
  setPrimaryResume: ProfileActions["setPrimaryResume"];
  updatePreferences: ProfileActions["updatePreferences"];
}

/**
 * Estado inicial do perfil
 */
const initialState: ProfileState = {
  profile: null,
  resumes: [],
  preferences: null,
  loading: false,
  error: null,
};

/**
 * Criador do slice de perfil
 */
export const createProfileSlice: SliceCreator<ProfileSlice> = (set, get) => ({
  profile: { ...initialState },

  /**
   * Busca dados do perfil do usuário
   */
  fetchProfile: async () => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Busca perfil na API
      const profileData = await apiClient.get<UserProfile>(
        PROFILE_ENDPOINTS.GET_PROFILE.path
      );

      // Atualiza estado com o perfil
      set((state) => ({
        profile: {
          ...state.profile,
          profile: profileData,
          loading: false,
        },
      }));

      // Também busca as preferências, se existirem no perfil
      if (profileData.jobPreferences) {
        set((state) => ({
          profile: {
            ...state.profile,
            preferences: profileData.jobPreferences,
          },
        }));
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao buscar perfil. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching profile:", error);
    }
  },

  /**
   * Atualiza o perfil do usuário
   */
  updateProfile: async (profileData: Partial<UserProfile>) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Atualiza perfil na API
      const updatedProfile = await apiClient.put<UserProfile>(
        PROFILE_ENDPOINTS.UPDATE_PROFILE.path,
        profileData
      );

      // Atualiza estado com o perfil atualizado
      set((state) => ({
        profile: {
          ...state.profile,
          profile: updatedProfile,
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao atualizar perfil. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error updating profile:", error);
      throw error;
    }
  },

  /**
   * Busca currículos do usuário
   */
  fetchResumes: async () => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Busca currículos na API
      const resumes = await apiClient.get<Resume[]>(
        RESUME_ENDPOINTS.GET_RESUMES.path
      );

      // Atualiza estado com os currículos
      set((state) => ({
        profile: {
          ...state.profile,
          resumes,
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao buscar currículos. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error fetching resumes:", error);
    }
  },

  /**
   * Faz upload de um novo currículo
   */
  uploadResume: async (file: File) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Faz upload do currículo na API utilizando o método auxiliar para upload de arquivos
      const resume = await apiClient.uploadFile<Resume>(
        RESUME_ENDPOINTS.UPLOAD_RESUME.path,
        file
      );

      // Atualiza estado com o novo currículo
      set((state) => ({
        profile: {
          ...state.profile,
          resumes: [...state.profile.resumes, resume],
          loading: false,
        },
      }));

      // Se for o primeiro currículo, define como principal
      if (get().profile.resumes.length === 1) {
        await get().setPrimaryResume(resume.id);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao fazer upload do currículo. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error uploading resume:", error);
      throw error;
    }
  },

  /**
   * Exclui um currículo
   */
  deleteResume: async (resumeId: string) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Exclui currículo na API
      await apiClient.delete(
        RESUME_ENDPOINTS.DELETE_RESUME.path.replace(":id", resumeId)
      );

      // Remove currículo do estado
      set((state) => ({
        profile: {
          ...state.profile,
          resumes: state.profile.resumes.filter(
            (resume) => resume.id !== resumeId
          ),
          loading: false,
        },
      }));

      // Se o currículo excluído era o principal e ainda existem outros, define outro como principal
      const deletedResume = get().profile.resumes.find(
        (resume) => resume.id === resumeId
      );
      if (
        deletedResume &&
        deletedResume.isPrimary &&
        get().profile.resumes.length > 0
      ) {
        await get().setPrimaryResume(get().profile.resumes[0].id);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao excluir currículo. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error deleting resume:", error);
      throw error;
    }
  },

  /**
   * Define um currículo como principal
   */
  setPrimaryResume: async (resumeId: string) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Define currículo como principal na API
      await apiClient.patch(
        RESUME_ENDPOINTS.SET_PRIMARY_RESUME.path.replace(":id", resumeId)
      );

      // Atualiza estado para refletir o currículo principal
      set((state) => ({
        profile: {
          ...state.profile,
          resumes: state.profile.resumes.map((resume) => ({
            ...resume,
            isPrimary: resume.id === resumeId,
          })),
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao definir currículo principal. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error setting primary resume:", error);
      throw error;
    }
  },

  /**
   * Atualiza as preferências do usuário
   */
  updatePreferences: async (preferences: Partial<UserPreferences>) => {
    try {
      // Atualiza estado para loading
      set((state) => ({
        profile: {
          ...state.profile,
          loading: true,
          error: null,
        },
      }));

      // Combina preferências existentes com as novas
      const currentPreferences = get().profile.preferences || {};
      const updatedPreferences = { ...currentPreferences, ...preferences };

      // Atualiza preferências na API
      const response = await apiClient.patch<UserPreferences>(
        PROFILE_ENDPOINTS.UPDATE_PREFERENCES.path,
        updatedPreferences
      );

      // Atualiza estado com as preferências atualizadas
      set((state) => ({
        profile: {
          ...state.profile,
          preferences: response,
          loading: false,
        },
      }));

      // Também atualiza as preferências no perfil, se existir
      if (get().profile.profile) {
        set((state) => ({
          profile: {
            ...state.profile,
            profile: state.profile.profile
              ? { ...state.profile.profile, jobPreferences: response }
              : null,
          },
        }));
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro ao atualizar preferências. Tente novamente.";

      // Atualiza estado com erro
      set((state) => ({
        profile: {
          ...state.profile,
          loading: false,
          error: errorMessage,
        },
      }));

      console.error("Error updating preferences:", error);
      throw error;
    }
  },
});
