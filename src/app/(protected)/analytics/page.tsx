import { Metadata } from "next";
import { Suspense } from "react";
import AnalyticsTemplate from "@/components/templates/AnalyticsTemplate";
import { AnalyticsProvider } from "@/contexts/AnalyticsContext";
import { AnalyticsSkeleton } from "@/components/molecules/feedback/AnalyticsSkeleton";
import { getUserAnalytics } from "@/lib/api/client";

export const metadata: Metadata = {
  title: "Análises | LinkedIn Job Matcher",
  description:
    "Obtenha insights detalhados sobre seu perfil, currículo e correspondências de vagas.",
};

/**
 * Página de analytics que mostra insights e recomendações para melhorar
 * o perfil e as correspondências do usuário.
 *
 * Implementa:
 * - Busca de dados analíticos do usuário via API
 * - Context Provider para gerenciamento de estado
 * - Suspense para carregamento progressivo com skeleton
 * - Delegação de renderização para o template AnalyticsTemplate
 */
export default async function AnalyticsPage({
  searchParams,
}: {
  searchParams?: {
    period?: string;
    resumeId?: string;
  };
}) {
  // Obtem parâmetros da URL
  const period = searchParams?.period || "30days";
  const resumeId = searchParams?.resumeId || "primary";

  // Busca os dados analíticos pela API
  const analyticsData = await getUserAnalytics(period, resumeId);

  return (
    <AnalyticsProvider
      initialData={analyticsData}
      period={period}
      resumeId={resumeId}
    >
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-tight">
            Análises e Insights
          </h1>
        </div>

        {/* Suspense para carregamento progressivo */}
        <Suspense fallback={<AnalyticsSkeleton />}>
          <AnalyticsTemplate />
        </Suspense>
      </div>
    </AnalyticsProvider>
  );
}
