import React from "react";
import Image from "next/image";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

/**
 * Layout para as páginas de autenticação (login e registro)
 * Inclui um design específico para páginas não autenticadas com
 * layout dividido e verificação de autenticação para redirecionar
 * usuários já logados.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Verifica se já existe um token de autenticação nos cookies
  // Se existir, redireciona para o dashboard
  const authToken = cookies().get("auth_token");
  if (authToken) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-screen">
      {/* Painel esquerdo com imagem e informações */}
      <div className="hidden lg:flex lg:w-1/2 bg-indigo-600 text-white flex-col">
        <div className="relative flex-1 flex flex-col justify-center px-12">
          <div className="absolute top-6 left-6">
            <Image
              src="/logo.svg"
              alt="LinkedIn Job Matcher"
              width={180}
              height={40}
              priority
            />
          </div>

          <h1 className="text-4xl font-bold mb-4">LinkedIn Job Matcher</h1>
          <p className="text-lg mb-8">
            Encontre as melhores vagas compatíveis com seu perfil usando nossa
            tecnologia de correspondência baseada em IA.
          </p>

          <div className="space-y-4">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center mr-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">
                  Upload de currículo simplificado
                </h3>
                <p className="text-indigo-200">
                  Análise inteligente do seu CV em segundos
                </p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center mr-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Vagas em tempo real</h3>
                <p className="text-indigo-200">
                  Coleta automática das vagas mais recentes
                </p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center mr-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Inteligência Artificial</h3>
                <p className="text-indigo-200">
                  Correspondência inteligente com Claude 3.7 Sonnet
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Painel direito com formulário de autenticação */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8">
            <Image
              src="/logo.svg"
              alt="LinkedIn Job Matcher"
              width={180}
              height={40}
              priority
            />
          </div>

          {children}
        </div>
      </div>
    </div>
  );
}
