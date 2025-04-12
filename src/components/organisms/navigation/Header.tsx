"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useWebSocket } from "@/contexts/WebSocketContext";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

/**
 * Cabeçalho principal da aplicação
 * Inclui busca, perfil do usuário e botão de notificações
 */
export function Header() {
  const router = useRouter();
  const { unreadCount } = useWebSocket();
  const [searchQuery, setSearchQuery] = useState("");
  const [userName, setUserName] = useState("Usuário");
  const [userAvatar, setUserAvatar] = useState("");
  const [userInitials, setUserInitials] = useState("U");

  // Função para lidar com logout
  const handleLogout = async () => {
    try {
      // Em um ambiente real, chamaria uma API para realizar o logout
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });

      // Redireciona para a página de login
      document.cookie = "auth_token=; max-age=0; path=/";
      router.push("/login");
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
    }
  };

  // Função para lidar com a busca
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/jobs?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Busca informações do usuário
  useEffect(() => {
    // Em um ambiente real, isso seria uma chamada para API
    // para buscar os dados do usuário logado
    const fetchUserData = async () => {
      try {
        // Simulando uma chamada de API
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Dados de exemplo
        const userData = {
          name: "Ana Silva",
          avatar: "",
        };

        setUserName(userData.name);
        setUserAvatar(userData.avatar);

        // Gera iniciais a partir do nome
        if (userData.name) {
          const names = userData.name.split(" ");
          let initials = "";
          if (names.length >= 2) {
            initials = `${names[0][0]}${names[names.length - 1][0]}`;
          } else {
            initials = names[0].substring(0, 2);
          }
          setUserInitials(initials.toUpperCase());
        }
      } catch (error) {
        console.error("Erro ao buscar dados do usuário:", error);
      }
    };

    fetchUserData();
  }, []);

  // Abre o centro de notificações
  const openNotificationCenter = () => {
    // Este é apenas um stub - a implementação real usaria um
    // estado global ou um contexto para controlar a visibilidade
    // do centro de notificações
    document.dispatchEvent(new CustomEvent("openNotifications"));
  };

  return (
    <header className="sticky top-0 z-10 border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 px-4 py-2 lg:py-0">
      <div className="flex h-12 lg:h-16 items-center justify-between">
        {/* Busca de vagas */}
        <div className="flex flex-1 justify-center px-2 lg:ml-6 lg:justify-end">
          <form onSubmit={handleSearch} className="w-full max-w-lg lg:max-w-xs">
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <svg
                  className="h-5 w-5 text-gray-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <Input
                type="search"
                placeholder="Buscar vagas..."
                className="block w-full rounded-md border-0 bg-white py-1.5 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-gray-800 dark:text-white dark:ring-gray-700"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </form>
        </div>

        {/* Botões de ação */}
        <div className="ml-4 flex items-center space-x-4">
          {/* Botão de notificações */}
          <Button
            variant="ghost"
            size="icon"
            className="relative text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
            onClick={openNotificationCenter}
          >
            <span className="sr-only">Notificações</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>

            {/* Indicador de notificações não lidas */}
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white">
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </Button>

          {/* Menu de perfil do usuário */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={userAvatar} alt={userName} />
                  <AvatarFallback>{userInitials}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>{userName}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/profile">Meu Perfil</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/profile#resume">Meus Currículos</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/settings">Configurações</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>Sair</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
