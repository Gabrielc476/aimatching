import { Metadata } from "next";
import { Suspense } from "react";
import MatchesTemplate from "@/components/templates/MatchesTemplate";
import { MatchesProvider } from "@/contexts/MatchesContext";
import { MatchesListSkeleton } from "@/components/molecules/feedback/MatchesListSkeleton";

export const metadata: Metadata = {
  title: "Correspondências | LinkedIn Job Matcher",
  description:
    "Visualize as vagas com melhor correspondência para seu perfil e currículo.",
};

/**
 * Página de correspondências que mostra as vagas mais compatíveis com o perfil do usuário.
 *
 * Implementa:
 * - Filtros e parâmetros de busca via searchParams
 * - Context Provider para gerenciamento de estado
 * - Suspense para carregamento progressivo com skeleton
 * - Delegação de renderização para o template MatchesTemplate
 */
export default function MatchesPage({
  searchParams,
}: {
  searchParams?: {
    minScore?: string;
    resumeId?: string;
    sortBy?: string;
    page?: string;
    status?: string;
  };
}) {
  // Obtem e converte parâmetros de busca da URL
  const currentPage = searchParams?.page ? parseInt(searchParams.page) : 1;
  const minScore = searchParams?.minScore
    ? parseInt(searchParams.minScore)
    : 70;
  const resumeId = searchParams?.resumeId || "all";
  const sortBy = searchParams?.sortBy || "score";
  const status = searchParams?.status || "all";

  // Parâmetros para filtragem e paginação
  const filters = {
    minScore,
    resumeId,
    sortBy,
    status,
    page: currentPage,
  };

  return (
    <MatchesProvider initialFilters={filters}>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-tight">
            Suas Correspondências
          </h1>
        </div>

        {/* Suspense para carregamento progressivo */}
        <Suspense fallback={<MatchesListSkeleton />}>
          <MatchesTemplate />
        </Suspense>
      </div>
    </MatchesProvider>
  );
}
