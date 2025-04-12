import { useState, useEffect } from "react";

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // Função para obter o valor inicial
  const readValue = (): T => {
    // Verificar se estamos no ambiente do navegador
    if (typeof window === "undefined") {
      return initialValue;
    }

    try {
      // Tentar recuperar do localStorage
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Erro ao ler localStorage key "${key}":`, error);
      return initialValue;
    }
  };

  // Estado para armazenar o valor atual
  const [storedValue, setStoredValue] = useState<T>(readValue);

  // Função para atualizar o valor no state e localStorage
  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      // Permitir o valor ser uma função para usar o mesmo padrão do useState
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;

      // Salvar no state
      setStoredValue(valueToStore);

      // Salvar no localStorage
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
        // Disparar evento para outros componentes que usam o mesmo localStorage
        window.dispatchEvent(new Event("local-storage"));
      }
    } catch (error) {
      console.warn(`Erro ao salvar localStorage key "${key}":`, error);
    }
  };

  // Escutar mudanças em outras abas/janelas
  useEffect(() => {
    const handleStorageChange = () => {
      setStoredValue(readValue());
    };

    // Adicionar quando o componente montar
    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("local-storage", handleStorageChange);

    // Remover quando o componente desmontar
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("local-storage", handleStorageChange);
    };
  }, [key]);

  return [storedValue, setValue];
}
