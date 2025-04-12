import React from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { Sidebar } from "@/components/organisms/navigation/Sidebar";
import { Header } from "@/components/organisms/navigation/Header";
import { NotificationCenter } from "@/components/organisms/dashboard/NotificationCenter";
import { WebSocketProvider } from "@/contexts/WebSocketContext";

/**
 * Layout para todas as páginas protegidas que requerem autenticação
 * Inclui o cabeçalho, barra lateral de navegação e verificação de autenticação
 */
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Verifica se existe um token de autenticação nos cookies
  // Se não existir, redireciona para a página de login
  const authToken = cookies().get("auth_token");
  if (!authToken) {
    redirect("/login");
  }

  return (
    <WebSocketProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Barra lateral de navegação para desktop */}
        <Sidebar />

        {/* Conteúdo principal */}
        <div className="flex flex-col lg:pl-64">
          {/* Cabeçalho com barra de pesquisa, perfil e notificações */}
          <Header />

          {/* Área de conteúdo principal */}
          <main className="flex-1 p-6">
            <div className="mx-auto max-w-7xl">{children}</div>
          </main>

          {/* Rodapé */}
          <footer className="border-t border-gray-200 dark:border-gray-800 p-6">
            <div className="mx-auto max-w-7xl flex flex-col sm:flex-row justify-between items-center">
              <div className="flex items-center mb-4 sm:mb-0">
                <Image
                  src="/logo.svg"
                  alt="LinkedIn Job Matcher"
                  width={140}
                  height={30}
                />
                <span className="text-sm text-gray-500 ml-4">
                  &copy; {new Date().getFullYear()} LinkedIn Job Matcher
                </span>
              </div>

              <div className="flex space-x-6">
                <Link
                  href="/terms"
                  className="text-sm text-gray-500 hover:text-indigo-600"
                >
                  Termos de Serviço
                </Link>
                <Link
                  href="/privacy"
                  className="text-sm text-gray-500 hover:text-indigo-600"
                >
                  Privacidade
                </Link>
                <Link
                  href="/help"
                  className="text-sm text-gray-500 hover:text-indigo-600"
                >
                  Ajuda
                </Link>
              </div>
            </div>
          </footer>
        </div>

        {/* Centro de notificações que será exibido como um drawer */}
        <NotificationCenter />
      </div>
    </WebSocketProvider>
  );
}
