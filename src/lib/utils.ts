/**
 * Utility Functions
 * Funções utilitárias centrais para uso em toda a aplicação
 */
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { MatchScoreLevel } from "./types";
import { MATCH_SCORE_THRESHOLDS } from "./constants";

/**
 * Função para combinar classes condicionalmente (compatível com TailwindCSS)
 * @param inputs Classes CSS a serem combinadas
 * @returns String de classes combinadas e otimizadas
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Detecta o tema atual (claro/escuro) baseado em preferências do sistema ou configurações do usuário
 * @returns String com o tema detectado ('dark' ou 'light')
 */
export function detectTheme(): "dark" | "light" {
  // Verifica configuração do usuário no localStorage
  const storedTheme = localStorage.getItem("linkedin-job-matcher-theme");
  if (storedTheme) {
    return storedTheme as "dark" | "light";
  }

  // Verifica preferência do sistema
  if (typeof window !== "undefined" && window.matchMedia) {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  // Fallback para tema claro
  return "light";
}

/**
 * Determina o nível da pontuação de correspondência com base na pontuação numérica
 * @param score Pontuação da correspondência (0-100)
 * @returns Nível de pontuação da correspondência
 */
export function getMatchScoreLevel(score: number): MatchScoreLevel {
  if (score >= MATCH_SCORE_THRESHOLDS.EXCELLENT) {
    return MatchScoreLevel.EXCELLENT;
  } else if (score >= MATCH_SCORE_THRESHOLDS.GOOD) {
    return MatchScoreLevel.GOOD;
  } else if (score >= MATCH_SCORE_THRESHOLDS.FAIR) {
    return MatchScoreLevel.FAIR;
  } else {
    return MatchScoreLevel.POOR;
  }
}

/**
 * Obtém a cor da pontuação de correspondência com base no nível
 * @param scoreLevel Nível de pontuação da correspondência
 * @returns String com a classe CSS da cor
 */
export function getMatchScoreColor(
  scoreLevel: MatchScoreLevel | string
): string {
  switch (scoreLevel) {
    case MatchScoreLevel.EXCELLENT:
      return "text-success-600 dark:text-success-400";
    case MatchScoreLevel.GOOD:
      return "text-primary-600 dark:text-primary-400";
    case MatchScoreLevel.FAIR:
      return "text-warning-600 dark:text-warning-400";
    case MatchScoreLevel.POOR:
      return "text-error-600 dark:text-error-400";
    default:
      return "text-neutral-600 dark:text-neutral-400";
  }
}

/**
 * Obtém a cor de fundo da pontuação de correspondência com base no nível
 * @param scoreLevel Nível de pontuação da correspondência
 * @returns String com a classe CSS da cor de fundo
 */
export function getMatchScoreBackgroundColor(
  scoreLevel: MatchScoreLevel | string
): string {
  switch (scoreLevel) {
    case MatchScoreLevel.EXCELLENT:
      return "bg-success-100 dark:bg-success-900/30";
    case MatchScoreLevel.GOOD:
      return "bg-primary-100 dark:bg-primary-900/30";
    case MatchScoreLevel.FAIR:
      return "bg-warning-100 dark:bg-warning-900/30";
    case MatchScoreLevel.POOR:
      return "bg-error-100 dark:bg-error-900/30";
    default:
      return "bg-neutral-100 dark:bg-neutral-800/30";
  }
}

/**
 * Extrai o texto de um arquivo PDF ou DOCX
 * @param file Arquivo para extrair texto
 * @returns Promise com o texto extraído
 */
export async function extractTextFromFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = async (event) => {
      try {
        const arrayBuffer = event.target?.result as ArrayBuffer;

        if (file.type === "application/pdf") {
          // Para arquivos PDF, usamos a biblioteca pdf.js que deve ser importada dinamicamente
          // no componente que usa esta função, para evitar problemas com SSR
          const text = await extractTextFromPDF(arrayBuffer);
          resolve(text);
        } else if (
          file.type === "application/msword" ||
          file.type ===
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ) {
          // Para arquivos DOCX, usamos a biblioteca mammoth que deve ser importada dinamicamente
          // no componente que usa esta função, para evitar problemas com SSR
          const text = await extractTextFromDOCX(arrayBuffer);
          resolve(text);
        } else if (file.type === "text/plain") {
          // Para arquivos TXT, simplesmente lemos como texto
          const text = new TextDecoder().decode(arrayBuffer);
          resolve(text);
        } else {
          reject(new Error(`Tipo de arquivo não suportado: ${file.type}`));
        }
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => {
      reject(new Error("Erro ao ler o arquivo"));
    };

    reader.readAsArrayBuffer(file);
  });
}

/**
 * Extrai texto de um arquivo PDF
 * @param arrayBuffer ArrayBuffer contendo o arquivo PDF
 * @returns Promise com o texto extraído
 */
async function extractTextFromPDF(arrayBuffer: ArrayBuffer): Promise<string> {
  // Esta função deve ser implementada no componente que usa extractTextFromFile,
  // importando a biblioteca pdf.js dinamicamente
  // Exemplo de código que seria usado no componente:
  /*
  import * as pdfjsLib from 'pdfjs-dist';
  
  async function extractTextFromPDF(arrayBuffer: ArrayBuffer): Promise<string> {
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let text = '';
    
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const pageText = content.items.map((item: any) => item.str).join(' ');
      text += pageText + '\n';
    }
    
    return text;
  }
  */

  // Placeholder para a implementação real
  console.warn(
    "extractTextFromPDF deve ser implementado com pdf.js no componente"
  );
  return "Texto extraído do PDF (placeholder)";
}

/**
 * Extrai texto de um arquivo DOCX
 * @param arrayBuffer ArrayBuffer contendo o arquivo DOCX
 * @returns Promise com o texto extraído
 */
async function extractTextFromDOCX(arrayBuffer: ArrayBuffer): Promise<string> {
  // Esta função deve ser implementada no componente que usa extractTextFromFile,
  // importando a biblioteca mammoth dinamicamente
  // Exemplo de código que seria usado no componente:
  /*
  import mammoth from 'mammoth';
  
  async function extractTextFromDOCX(arrayBuffer: ArrayBuffer): Promise<string> {
    const result = await mammoth.extractRawText({ arrayBuffer });
    return result.value;
  }
  */

  // Placeholder para a implementação real
  console.warn(
    "extractTextFromDOCX deve ser implementado com mammoth no componente"
  );
  return "Texto extraído do DOCX (placeholder)";
}

/**
 * Converte milissegundos para um formato legível
 * @param ms Tempo em milissegundos
 * @returns String formatada do tempo (ex: "2h 30m")
 */
export function formatTimeFromMs(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`;
  }

  const seconds = Math.floor(ms / 1000);

  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / 60);

  if (minutes < 60) {
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (hours < 24) {
    return remainingMinutes > 0
      ? `${hours}h ${remainingMinutes}m`
      : `${hours}h`;
  }

  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;

  return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

/**
 * Valida a força de uma senha
 * @param password Senha a ser validada
 * @returns Objeto com informações sobre a validação
 */
export function validatePasswordStrength(password: string): {
  score: number;
  feedback: string[];
  isStrong: boolean;
} {
  const feedback: string[] = [];
  let score = 0;

  // Critérios básicos
  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push("A senha deve ter pelo menos 8 caracteres");
  }

  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push("A senha deve incluir pelo menos uma letra maiúscula");
  }

  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push("A senha deve incluir pelo menos uma letra minúscula");
  }

  if (/[0-9]/.test(password)) {
    score += 1;
  } else {
    feedback.push("A senha deve incluir pelo menos um número");
  }

  if (/[^A-Za-z0-9]/.test(password)) {
    score += 1;
  } else {
    feedback.push("A senha deve incluir pelo menos um caractere especial");
  }

  // Critérios avançados
  if (password.length >= 12) {
    score += 1;
  }

  if (/^(?!.*(.)\1{2,}).*$/.test(password)) {
    // Sem repetições de caracteres
    score += 1;
  } else {
    feedback.push("Evite repetir caracteres sequencialmente");
  }

  const isStrong = score >= 5;

  return {
    score,
    feedback,
    isStrong,
  };
}

/**
 * Gera uma string aleatória de comprimento especificado
 * @param length Comprimento da string (padrão: 10)
 * @param includeSpecialChars Se deve incluir caracteres especiais (padrão: false)
 * @returns String aleatória
 */
export function generateRandomString(
  length: number = 10,
  includeSpecialChars: boolean = false
): string {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const specialChars = "!@#$%^&*()_+-=[]{}|;:,.<>?";

  const allChars = includeSpecialChars ? chars + specialChars : chars;

  let result = "";
  const charLength = allChars.length;

  for (let i = 0; i < length; i++) {
    result += allChars.charAt(Math.floor(Math.random() * charLength));
  }

  return result;
}

/**
 * Normaliza strings para comparação (remove acentos, converte para minúsculo, etc.)
 * @param str String a ser normalizada
 * @returns String normalizada
 */
export function normalizeString(str: string): string {
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, " ");
}

/**
 * Exportação padrão de todas as funções
 */
export default {
  cn,
  detectTheme,
  getMatchScoreLevel,
  getMatchScoreColor,
  getMatchScoreBackgroundColor,
  extractTextFromFile,
  formatTimeFromMs,
  validatePasswordStrength,
  generateRandomString,
  normalizeString,
};
