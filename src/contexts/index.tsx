import React, { ReactNode } from "react";
import { AuthProvider } from "./authContext";
import { ThemeProvider } from "./ThemeContext";
import { NotificationProvider } from "./NotificationContext";

// Tipos para o provider composto
interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Componente de Provider composto que engloba todos os contextos da aplicação
 * Permite facilitar a inclusão de todos os contextos necessários no layout principal
 */
export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NotificationProvider>{children}</NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

// Exportações individuais para uso direto
export { useAuth } from "./authContext";
export { useTheme } from "./ThemeContext";
export { useNotifications } from "./NotificationContext";

// Exportações de tipos necessários
export type { Notification } from "./NotificationContext";

// Exportação padrão do provider composto
export default AppProviders;
