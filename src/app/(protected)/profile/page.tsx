import { Metadata } from "next";
import { Suspense } from "react";
import ProfileTemplate from "@/components/templates/ProfileTemplate";
import { ProfileProvider } from "@/contexts/ProfileContext";
import { ProfileSkeleton } from "@/components/molecules/feedback/ProfileSkeleton";
import { getUserProfile } from "@/lib/api/client";

export const metadata: Metadata = {
  title: "Perfil | LinkedIn Job Matcher",
  description:
    "Gerencie seu perfil e currículos para melhorar sua correspondência com vagas.",
};

/**
 * Página de perfil do usuário que permite gerenciar dados pessoais e currículos.
 *
 * Implementa:
 * - Busca de dados do perfil do usuário via API
 * - Context Provider para gerenciamento de estado
 * - Suspense para carregamento progressivo com skeleton
 * - Delegação de renderização para o template ProfileTemplate
 */
export default async function ProfilePage() {
  // Busca os dados do perfil do usuário pela API
  const profileData = await getUserProfile();

  return (
    <ProfileProvider initialData={profileData}>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-tight">Seu Perfil</h1>
        </div>

        {/* Suspense para carregamento progressivo */}
        <Suspense fallback={<ProfileSkeleton />}>
          <ProfileTemplate />
        </Suspense>
      </div>
    </ProfileProvider>
  );
}
