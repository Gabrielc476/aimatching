"use client";

import { toast as sonnerToast } from "sonner";
import { ToastOptions as AppToastOptions } from "@/lib/types";

export function useToast() {
  const showToast = ({
    title,
    description,
    action,
    type = "default",
    duration = 5000,
  }: AppToastOptions) => {
    const options = {
      duration,
      // Mapear o tipo para as propriedades do Sonner
      ...(action && { action }),
      ...(type === "error" && {
        style: {
          backgroundColor: "var(--destructive)",
          color: "var(--destructive-foreground)",
        },
      }),
      ...(type === "success" && { style: getStyleForType("success") }),
      ...(type === "warning" && { style: getStyleForType("warning") }),
      ...(type === "info" && { style: getStyleForType("info") }),
    };

    // O Sonner tem diferentes funções para diferentes tipos de toast
    if (type === "error") {
      return sonnerToast.error(title || "Erro", {
        description,
        ...options,
      });
    } else if (type === "success") {
      return sonnerToast.success(title || "Sucesso", {
        description,
        ...options,
      });
    } else if (type === "info" || type === "warning") {
      // Sonner não tem métodos específicos para info/warning, então usamos o toast normal
      // com estilos customizados
      return sonnerToast(
        title || (type === "warning" ? "Atenção" : "Informação"),
        {
          description,
          ...options,
        }
      );
    } else {
      // Default toast
      return sonnerToast(title || "", {
        description,
        ...options,
      });
    }
  };

  // Helpers para tipos específicos de toasts
  const success = (options: Omit<AppToastOptions, "type">) =>
    showToast({ ...options, type: "success" });

  const error = (options: Omit<AppToastOptions, "type">) =>
    showToast({ ...options, type: "error" });

  const warning = (options: Omit<AppToastOptions, "type">) =>
    showToast({ ...options, type: "warning" });

  const info = (options: Omit<AppToastOptions, "type">) =>
    showToast({ ...options, type: "info" });

  return {
    toast: showToast,
    success,
    error,
    warning,
    info,
  };
}

// Função auxiliar para obter o estilo CSS com base no tipo
function getStyleForType(type: string): React.CSSProperties {
  switch (type) {
    case "success":
      return {
        backgroundColor: "hsl(var(--success))",
        color: "hsl(var(--success-foreground))",
        border: "1px solid hsl(var(--success-border))",
      };
    case "warning":
      return {
        backgroundColor: "hsl(var(--warning))",
        color: "hsl(var(--warning-foreground))",
        border: "1px solid hsl(var(--warning-border))",
      };
    case "info":
      return {
        backgroundColor: "hsl(var(--info))",
        color: "hsl(var(--info-foreground))",
        border: "1px solid hsl(var(--info-border))",
      };
    default:
      return {};
  }
}
