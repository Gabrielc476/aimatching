import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

// Tipos dos temas disponíveis
type Theme = "light" | "dark" | "system";

// Tipos para o contexto do tema
interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: "light" | "dark"; // Tema resolvido após considerar preferências do sistema
  toggleTheme: () => void;
}

// Valor padrão do contexto
const defaultThemeContext: ThemeContextType = {
  theme: "system",
  setTheme: () => {},
  resolvedTheme: "light",
  toggleTheme: () => {},
};

// Criação do contexto
const ThemeContext = createContext<ThemeContextType>(defaultThemeContext);

// Hook personalizado para usar o contexto
export const useTheme = () => useContext(ThemeContext);

// Tipos para o provider
interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

// Provider do tema
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = "system",
  storageKey = "linkedin-job-matcher-theme",
}) => {
  // Estado para o tema selecionado
  const [theme, setThemeState] = useState<Theme>(defaultTheme);
  // Estado para o tema resolvido (após considerar preferências do sistema)
  const [resolvedTheme, setResolvedTheme] = useState<"light" | "dark">("light");

  // Efeito para carregar o tema salvo no localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem(storageKey) as Theme | null;
    if (savedTheme) {
      setThemeState(savedTheme);
    }
  }, [storageKey]);

  // Efeito para resolver o tema com base nas preferências do sistema
  useEffect(() => {
    const handleMediaQuery = () => {
      const systemPrefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
      const resolved =
        theme === "system" ? (systemPrefersDark ? "dark" : "light") : theme;
      setResolvedTheme(resolved as "light" | "dark");

      // Aplicar o tema no documento
      const root = window.document.documentElement;
      root.classList.remove("light", "dark");
      root.classList.add(resolved);
    };

    // Adicionar listener para mudanças na preferência do sistema
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    mediaQuery.addEventListener("change", handleMediaQuery);

    // Resolver o tema inicialmente
    handleMediaQuery();

    return () => mediaQuery.removeEventListener("change", handleMediaQuery);
  }, [theme]);

  // Função para definir o tema
  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(storageKey, newTheme);
    setThemeState(newTheme);
  };

  // Função para alternar entre temas
  const toggleTheme = () => {
    setTheme(resolvedTheme === "light" ? "dark" : "light");
  };

  // Valor do contexto
  const themeContextValue: ThemeContextType = {
    theme,
    setTheme,
    resolvedTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={themeContextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
