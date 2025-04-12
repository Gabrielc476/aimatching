/**
 * Helper Utilities
 * Funções utilitárias diversas para uso em toda a aplicação
 */
import { SkillLevel } from "../types";

/**
 * Gera um UUID v4
 * @returns String contendo um UUID v4
 */
export const generateUUID = (): string => {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

/**
 * Atrasa a execução por um tempo determinado
 * @param ms Tempo em milissegundos
 * @returns Promise que resolve após o tempo especificado
 */
export const delay = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Agrupa um array de objetos por um campo específico
 * @param array Array de objetos a serem agrupados
 * @param key Campo pelo qual agrupar
 * @returns Objeto com os itens agrupados
 */
export const groupBy = <T extends Record<string, any>>(
  array: T[],
  key: keyof T
): Record<string, T[]> => {
  return array.reduce((result: Record<string, T[]>, currentItem: T) => {
    const groupKey = String(currentItem[key]);

    if (!result[groupKey]) {
      result[groupKey] = [];
    }

    result[groupKey].push(currentItem);
    return result;
  }, {});
};

/**
 * Remove acentos de uma string
 * @param text Texto com acentos
 * @returns Texto sem acentos
 */
export const removeAccents = (text: string): string => {
  if (!text) return "";

  return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
};

/**
 * Cria um slug a partir de um texto
 * @param text Texto de origem
 * @returns Slug formatado
 */
export const slugify = (text: string): string => {
  if (!text) return "";

  const withoutAccents = removeAccents(text);

  return withoutAccents
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
};

/**
 * Deep clone de um objeto
 * @param obj Objeto a ser clonado
 * @returns Clone profundo do objeto
 */
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== "object") {
    return obj;
  }

  // Tratamento especial para datas
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }

  // Tratamento para arrays
  if (Array.isArray(obj)) {
    return obj.map((item) => deepClone(item)) as unknown as T;
  }

  // Para objetos regulares
  const clonedObj = {} as T;

  Object.keys(obj).forEach((key) => {
    clonedObj[key as keyof T] = deepClone(obj[key as keyof T]);
  });

  return clonedObj;
};

/**
 * Verifica se dois objetos são iguais (comparação profunda)
 * @param obj1 Primeiro objeto
 * @param obj2 Segundo objeto
 * @returns Booleano indicando se os objetos são iguais
 */
export const isDeepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;

  if (
    obj1 === null ||
    obj2 === null ||
    typeof obj1 !== "object" ||
    typeof obj2 !== "object"
  ) {
    return obj1 === obj2;
  }

  // Tratamento para datas
  if (obj1 instanceof Date && obj2 instanceof Date) {
    return obj1.getTime() === obj2.getTime();
  }

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  return keys1.every(
    (key) => keys2.includes(key) && isDeepEqual(obj1[key], obj2[key])
  );
};

/**
 * Limita a execução de uma função por um período de tempo
 * @param func Função a ser executada
 * @param wait Tempo de espera entre execuções em milissegundos
 * @returns Função com debounce aplicado
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>): void {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout !== null) {
      clearTimeout(timeout);
    }

    timeout = setTimeout(later, wait);
  };
}

/**
 * Limita a frequência de execução de uma função
 * @param func Função a ser executada
 * @param wait Tempo mínimo entre execuções em milissegundos
 * @param immediate Se verdadeiro, executa no início em vez do final do período
 * @returns Função com throttle aplicado
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate: boolean = false
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  let lastArgs: Parameters<T> | null = null;
  let lastCallTime: number | null = null;

  return function (...args: Parameters<T>): void {
    const now = Date.now();

    // Se é a primeira chamada ou immediate é verdadeiro
    if (lastCallTime === null || (immediate && now - lastCallTime >= wait)) {
      lastCallTime = now;
      func(...args);
      return;
    }

    // Armazena os argumentos mais recentes
    lastArgs = args;

    // Se já existe um timeout, não faz nada
    if (timeout !== null) return;

    timeout = setTimeout(() => {
      // Calcula quanto tempo realmente esperou
      const elapsed = Date.now() - (lastCallTime as number);

      // Se esperou mais que wait, executa imediatamente
      if (elapsed >= wait && lastArgs) {
        lastCallTime = Date.now();
        func(...lastArgs);
        lastArgs = null;
      }

      timeout = null;
    }, wait - (now - (lastCallTime as number)));
  };
}

/**
 * Retorna um objeto de mapeamento de nível de habilidade
 * @param customLevels Personalização opcional dos níveis
 * @returns Objeto de mapeamento com rótulos e porcentagens
 */
export const getSkillLevelMapping = (
  customLevels?: Record<string, { label: string; percentage: number }>
): Record<string, { label: string; percentage: number }> => {
  const defaultLevels: Record<string, { label: string; percentage: number }> = {
    [SkillLevel.BEGINNER]: { label: "Iniciante", percentage: 25 },
    [SkillLevel.INTERMEDIATE]: { label: "Intermediário", percentage: 50 },
    [SkillLevel.ADVANCED]: { label: "Avançado", percentage: 75 },
    [SkillLevel.EXPERT]: { label: "Especialista", percentage: 100 },
  };

  return customLevels ? { ...defaultLevels, ...customLevels } : defaultLevels;
};

/**
 * Função para esconder partes de uma string (útil para dados sensíveis)
 * @param str String a ser parcialmente oculta
 * @param visibleStart Número de caracteres visíveis no início
 * @param visibleEnd Número de caracteres visíveis no final
 * @param mask Caractere usado para mascarar (padrão: '*')
 * @returns String mascarada
 */
export const maskString = (
  str: string,
  visibleStart: number = 4,
  visibleEnd: number = 4,
  mask: string = "*"
): string => {
  if (!str) return "";

  const len = str.length;

  if (len <= visibleStart + visibleEnd) {
    return str;
  }

  const start = str.substring(0, visibleStart);
  const middle = mask.repeat(len - visibleStart - visibleEnd);
  const end = str.substring(len - visibleEnd);

  return `${start}${middle}${end}`;
};

/**
 * Converte um objeto em parâmetros de URL
 * @param params Objeto com parâmetros
 * @returns String formatada para URL
 */
export const objectToQueryString = (params: Record<string, any>): string => {
  if (!params || Object.keys(params).length === 0) {
    return "";
  }

  return Object.entries(params)
    .filter(
      ([_, value]) => value !== undefined && value !== null && value !== ""
    )
    .map(([key, value]) => {
      // Trata arrays para formato de URL apropriado
      if (Array.isArray(value)) {
        return value
          .map(
            (item) => `${encodeURIComponent(key)}=${encodeURIComponent(item)}`
          )
          .join("&");
      }

      // Trata objetos Date
      if (value instanceof Date) {
        return `${encodeURIComponent(key)}=${encodeURIComponent(
          value.toISOString()
        )}`;
      }

      // Trata valores booleanos
      if (typeof value === "boolean") {
        return `${encodeURIComponent(key)}=${value ? "true" : "false"}`;
      }

      // Caso padrão para strings e números
      return `${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
    })
    .join("&");
};

/**
 * Extrai um valor de um objeto usando uma notação de caminho
 * @param obj Objeto de origem
 * @param path Caminho para o valor (ex: "user.address.street")
 * @param defaultValue Valor padrão caso o caminho não exista
 * @returns Valor encontrado no caminho ou valor padrão
 */
export const getValueByPath = <T>(
  obj: Record<string, any>,
  path: string,
  defaultValue: T
): T => {
  if (!obj || !path) return defaultValue;

  const parts = path.split(".");
  let current = obj;

  for (const part of parts) {
    if (
      current === null ||
      current === undefined ||
      typeof current !== "object"
    ) {
      return defaultValue;
    }

    current = current[part];
  }

  return current === undefined ? defaultValue : (current as T);
};

/**
 * Exportação padrão de todas as funções
 */
export default {
  generateUUID,
  delay,
  groupBy,
  removeAccents,
  slugify,
  deepClone,
  isDeepEqual,
  debounce,
  throttle,
  getSkillLevelMapping,
  maskString,
  objectToQueryString,
  getValueByPath,
};
