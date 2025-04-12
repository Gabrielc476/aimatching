import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import JobDetailTemplate from "@/components/templates/JobDetailTemplate";
import { JobProvider } from "@/contexts/JobContext";
import { JobDetailSkeleton } from "@/components/molecules/feedback/JobDetailSkeleton";
import { getJobById } from "@/lib/api/client";

// Metadata dinâmico baseado nos parâmetros da página
export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  try {
    const job = await getJobById(params.id);

    return {
      title: `${job.title} at ${job.company} | LinkedIn Job Matcher`,
      description: job.description.substring(0, 160),
    };
  } catch (error) {
    return {
      title: "Vaga não encontrada | LinkedIn Job Matcher",
      description: "A vaga solicitada não foi encontrada.",
    };
  }
}

/**
 * Parâmetros para a página de detalhes da vaga
 * Usados para buscar os dados específicos da vaga
 */
interface JobDetailPageProps {
  params: {
    id: string;
  };
}

/**
 * Página de detalhes de uma vaga específica.
 *
 * Implementa:
 * - Busca de dados específicos da vaga via API
 * - Tratamento de erros com notFound
 * - Context Provider para gerenciamento de estado
 * - Suspense para carregamento progressivo com skeleton
 */
export default async function JobDetailPage({ params }: JobDetailPageProps) {
  // Busca os dados da vaga pela API
  let job;
  try {
    job = await getJobById(params.id);
  } catch (error) {
    notFound();
  }

  return (
    <JobProvider initialJob={job}>
      <div className="space-y-6">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Link href="/jobs" className="text-indigo-600 hover:text-indigo-500">
            Vagas
          </Link>
          <span>/</span>
          <span className="truncate max-w-[200px]">{job.title}</span>
        </div>

        {/* Suspense para carregamento progressivo */}
        <Suspense fallback={<JobDetailSkeleton />}>
          <JobDetailTemplate />
        </Suspense>
      </div>
    </JobProvider>
  );
}
