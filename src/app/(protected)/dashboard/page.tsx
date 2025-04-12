import { Metadata } from "next";
import DashboardTemplate from "@/components/templates/DashboardTemplate";
import { DashboardProvider } from "@/contexts/DashboardContext";

export const metadata: Metadata = {
  title: "Dashboard | LinkedIn Job Matcher",
  description:
    "Visualize suas correspondências de vagas, estatísticas e recomendações personalizadas.",
};

/**
 * Página de Dashboard principal que mostra uma visão geral das correspondências,
 * estatísticas e recomendações do usuário.
 *
 * Utiliza o padrão de Context para gerenciar o estado específico do dashboard
 * e delega a renderização ao template DashboardTemplate.
 */
export default async function DashboardPage() {
  return (
    <DashboardProvider>
      <DashboardTemplate />
    </DashboardProvider>
  );
}
