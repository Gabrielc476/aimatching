"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useWebSocket } from "@/contexts/WebSocketContext";
import { formatDistanceToNow } from "date-fns";
import { ptBR } from "date-fns/locale";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
  SheetClose,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

/**
 * Centro de notificações que exibe as notificações do usuário
 * em formato de painel lateral.
 */
export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, unreadCount, markAsRead, markAllAsRead } =
    useWebSocket();

  // Agrupar notificações por tipo para as abas
  const matchNotifications = notifications.filter((n) => n.type === "match");
  const jobNotifications = notifications.filter((n) => n.type === "job");
  const systemNotifications = notifications.filter((n) => n.type === "system");

  // Formatar data relativa (ex: "há 5 minutos")
  const formatRelativeTime = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), {
        addSuffix: true,
        locale: ptBR,
      });
    } catch (error) {
      return "recentemente";
    }
  };

  // Ouvir evento para abrir o centro de notificações
  useEffect(() => {
    const handleOpenNotifications = () => {
      setIsOpen(true);
    };

    document.addEventListener("openNotifications", handleOpenNotifications);
    return () => {
      document.removeEventListener(
        "openNotifications",
        handleOpenNotifications
      );
    };
  }, []);

  // Função para renderizar um item de notificação
  const renderNotificationItem = (notification: any) => {
    // Determinar a cor de destaque baseada no tipo de notificação
    let highlightColor = "bg-gray-200 dark:bg-gray-700";
    if (notification.type === "match")
      highlightColor = "bg-green-100 dark:bg-green-900/20";
    if (notification.type === "job")
      highlightColor = "bg-blue-100 dark:bg-blue-900/20";
    if (notification.type === "system")
      highlightColor = "bg-orange-100 dark:bg-orange-900/20";

    return (
      <div
        key={notification.id}
        className={`p-4 border-b border-gray-200 dark:border-gray-800 ${
          !notification.read ? "bg-blue-50 dark:bg-blue-900/10" : ""
        }`}
        onClick={() => markAsRead(notification.id)}
      >
        <div className="flex items-start gap-3">
          {/* Ícone ou indicador do tipo de notificação */}
          <div
            className={`w-2 h-12 rounded-full flex-shrink-0 ${highlightColor}`}
          />

          <div className="flex-1 min-w-0">
            {/* Título da notificação */}
            <p className="font-medium text-gray-900 dark:text-white truncate">
              {notification.title}
            </p>

            {/* Mensagem da notificação */}
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
              {notification.message}
            </p>

            {/* Data da notificação */}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {formatRelativeTime(notification.timestamp)}
            </p>

            {/* Botões de ação baseados no tipo de notificação */}
            {notification.type === "match" && notification.data?.jobId && (
              <div className="mt-2">
                <Link
                  href={`/jobs/${notification.data.jobId}`}
                  className="text-sm text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
                  onClick={() => setIsOpen(false)}
                >
                  Ver vaga
                </Link>
              </div>
            )}
          </div>

          {/* Indicador de não lido */}
          {!notification.read && (
            <Badge
              variant="secondary"
              className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
            >
              Nova
            </Badge>
          )}
        </div>
      </div>
    );
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-md p-0 flex flex-col"
      >
        <SheetHeader className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            <SheetTitle className="text-xl">Notificações</SheetTitle>
            {unreadCount > 0 && (
              <Badge
                variant="secondary"
                className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
              >
                {unreadCount} {unreadCount === 1 ? "nova" : "novas"}
              </Badge>
            )}
          </div>
        </SheetHeader>

        <Tabs defaultValue="all" className="flex-1 flex flex-col">
          <TabsList className="px-6 py-2 border-b border-gray-200 dark:border-gray-800 justify-start">
            <TabsTrigger value="all" className="relative">
              Todas
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white">
                  {unreadCount}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="matches" className="relative">
              Correspondências
              {matchNotifications.filter((n) => !n.read).length > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white">
                  {matchNotifications.filter((n) => !n.read).length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="jobs" className="relative">
              Vagas
              {jobNotifications.filter((n) => !n.read).length > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white">
                  {jobNotifications.filter((n) => !n.read).length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Conteúdo das abas */}
          <ScrollArea className="flex-1">
            <TabsContent value="all" className="mt-0 h-full">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-12 w-12 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                  </svg>
                  <p className="text-center">Você não tem notificações</p>
                </div>
              ) : (
                notifications.map(renderNotificationItem)
              )}
            </TabsContent>

            <TabsContent value="matches" className="mt-0 h-full">
              {matchNotifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
                  <p className="text-center">
                    Nenhuma notificação de correspondência
                  </p>
                </div>
              ) : (
                matchNotifications.map(renderNotificationItem)
              )}
            </TabsContent>

            <TabsContent value="jobs" className="mt-0 h-full">
              {jobNotifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
                  <p className="text-center">Nenhuma notificação de vagas</p>
                </div>
              ) : (
                jobNotifications.map(renderNotificationItem)
              )}
            </TabsContent>
          </ScrollArea>
        </Tabs>

        {/* Rodapé com botões de ação */}
        <SheetFooter className="px-6 py-4 border-t border-gray-200 dark:border-gray-800">
          <div className="flex justify-between w-full">
            <Button
              variant="outline"
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
            >
              Marcar todas como lidas
            </Button>
            <SheetClose asChild>
              <Button>Fechar</Button>
            </SheetClose>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
