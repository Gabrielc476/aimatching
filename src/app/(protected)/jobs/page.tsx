import { Metadata } from "next";
import { Suspense } from "react";
import JobsTemplate from "@/components/templates/JobsTemplate";
import { JobsProvider } from "@/contexts/JobsContext";
import { JobsListSkeleton } from "@/components/molecules/feedback/JobsListSkeleton";

export const metadata: Metadata = {
  title: "Vagas | LinkedIn Job Matcher",
  description:
    "Explore as vagas disponíveis e encontre as que melhor se adequam ao seu perfil.",
};

/**
 * Página de listagem e busca de vagas.
 *
 * Implementa:
 * - Suspense para carregamento progressivo com skeleton
 * - Context Provider para gerenciamento de estado específico da página
 * - Delegação de renderização para o template JobsTemplate
 */
export default function JobsPage({
  searchParams,
}: {
  searchParams?: {
    q?: string;
    location?: string;
    page?: string;
    skills?: string;
    jobType?: string;
    experienceLevel?: string;
    sortBy?: string;
  };
}) {
  // Obtem e converte parâmetros de busca da URL
  const currentPage = searchParams?.page ? parseInt(searchParams.page) : 1;
  const query = searchParams?.q || "";
  const location = searchParams?.location || "";
  const skills = searchParams?.skills?.split(",") || [];
  const jobType = searchParams?.jobType || "";
  const experienceLevel = searchParams?.experienceLevel || "";
  const sortBy = searchParams?.sortBy || "relevance";

  // Parâmetros para filtragem e paginação
  const filters = {
    query,
    location,
    skills,
    jobType,
    experienceLevel,
    sortBy,
    page: currentPage,
  };

  return (
    <JobsProvider initialFilters={filters}>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-tight">
            Vagas Disponíveis
          </h1>
        </div>

        {/* Suspense para carregar progressivamente a interface com skeleton */}
        <Suspense fallback={<JobsListSkeleton />}>
          <JobsTemplate />
        </Suspense>
      </div>
    </JobsProvider>
  );
}
