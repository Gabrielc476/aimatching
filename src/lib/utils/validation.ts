/**
 * Validation Utilities
 * Funções utilitárias para validação de dados
 */
import jwt_decode from "jwt-decode";
import { JWT_EXPIRATION_MARGIN } from "../constants";

/**
 * Interface para token JWT decodificado
 */
interface DecodedToken {
  exp?: number;
  iat?: number;
  sub?: string;
  [key: string]: any;
}

/**
 * Verifica se um email é válido
 * @param email Email a ser validado
 * @returns Booleano indicando se o email é válido
 */
export const isValidEmail = (email: string): boolean => {
  if (!email) return false;

  // Regex para validação básica de email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Verifica se uma senha atende aos requisitos mínimos de segurança
 * @param password Senha a ser validada
 * @param minLength Comprimento mínimo (padrão: 8)
 * @param requireSpecialChar Indica se deve exigir caractere especial
 * @param requireUppercase Indica se deve exigir letra maiúscula
 * @param requireNumber Indica se deve exigir número
 * @returns Booleano indicando se a senha é válida
 */
export const isValidPassword = (
  password: string,
  minLength: number = 8,
  requireSpecialChar: boolean = true,
  requireUppercase: boolean = true,
  requireNumber: boolean = true
): boolean => {
  if (!password || password.length < minLength) return false;

  if (requireSpecialChar && !/[!@#$%^&*(),.?":{}|<>]/.test(password))
    return false;
  if (requireUppercase && !/[A-Z]/.test(password)) return false;
  if (requireNumber && !/[0-9]/.test(password)) return false;

  return true;
};

/**
 * Verifica os requisitos de uma senha e retorna feedback detalhado
 * @param password Senha a ser validada
 * @param minLength Comprimento mínimo (padrão: 8)
 * @returns Objeto com status de cada requisito e uma mensagem geral
 */
export const validatePasswordStrength = (
  password: string,
  minLength: number = 8
): {
  isValid: boolean;
  hasMinLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
  message: string;
} => {
  const hasMinLength = password.length >= minLength;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  const isValid =
    hasMinLength && hasUppercase && hasLowercase && hasNumber && hasSpecialChar;

  let message = "";
  if (!hasMinLength) {
    message = `A senha deve ter pelo menos ${minLength} caracteres.`;
  } else if (!hasUppercase) {
    message = "A senha deve incluir pelo menos uma letra maiúscula.";
  } else if (!hasLowercase) {
    message = "A senha deve incluir pelo menos uma letra minúscula.";
  } else if (!hasNumber) {
    message = "A senha deve incluir pelo menos um número.";
  } else if (!hasSpecialChar) {
    message = "A senha deve incluir pelo menos um caractere especial.";
  } else {
    message = "Senha válida.";
  }

  return {
    isValid,
    hasMinLength,
    hasUppercase,
    hasLowercase,
    hasNumber,
    hasSpecialChar,
    message,
  };
};

/**
 * Verifica se um CPF é válido
 * @param cpf CPF a ser validado (com ou sem formatação)
 * @returns Booleano indicando se o CPF é válido
 */
export const isValidCPF = (cpf: string): boolean => {
  if (!cpf) return false;

  // Remove caracteres não numéricos
  cpf = cpf.replace(/\D/g, "");

  // Verifica se tem 11 dígitos
  if (cpf.length !== 11) return false;

  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1{10}$/.test(cpf)) return false;

  // Validação do primeiro dígito verificador
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cpf.charAt(i)) * (10 - i);
  }
  let remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.charAt(9))) return false;

  // Validação do segundo dígito verificador
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cpf.charAt(i)) * (11 - i);
  }
  remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.charAt(10))) return false;

  return true;
};

/**
 * Verifica se um CNPJ é válido
 * @param cnpj CNPJ a ser validado (com ou sem formatação)
 * @returns Booleano indicando se o CNPJ é válido
 */
export const isValidCNPJ = (cnpj: string): boolean => {
  if (!cnpj) return false;

  // Remove caracteres não numéricos
  cnpj = cnpj.replace(/\D/g, "");

  // Verifica se tem 14 dígitos
  if (cnpj.length !== 14) return false;

  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1{13}$/.test(cnpj)) return false;

  // Validação do primeiro dígito verificador
  let tamanho = cnpj.length - 2;
  let numeros = cnpj.substring(0, tamanho);
  const digitos = cnpj.substring(tamanho);
  let soma = 0;
  let pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
  if (resultado !== parseInt(digitos.charAt(0))) return false;

  // Validação do segundo dígito verificador
  tamanho = tamanho + 1;
  numeros = cnpj.substring(0, tamanho);
  soma = 0;
  pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
  if (resultado !== parseInt(digitos.charAt(1))) return false;

  return true;
};

/**
 * Verifica se um CEP é válido
 * @param cep CEP a ser validado (com ou sem formatação)
 * @returns Booleano indicando se o CEP é válido
 */
export const isValidCEP = (cep: string): boolean => {
  if (!cep) return false;

  // Remove caracteres não numéricos
  const cleanCep = cep.replace(/\D/g, "");

  // Verifica se tem 8 dígitos
  return cleanCep.length === 8 && /^\d{8}$/.test(cleanCep);
};

/**
 * Verifica se um número de telefone é válido
 * @param phone Número de telefone (com ou sem formatação)
 * @returns Booleano indicando se o telefone é válido
 */
export const isValidPhone = (phone: string): boolean => {
  if (!phone) return false;

  // Remove caracteres não numéricos
  const cleanPhone = phone.replace(/\D/g, "");

  // Verifica se o telefone tem entre 10 e 11 dígitos (com DDD)
  return (
    cleanPhone.length >= 10 &&
    cleanPhone.length <= 11 &&
    /^\d+$/.test(cleanPhone)
  );
};

/**
 * Valida se um URL é válido
 * @param url URL a ser validado
 * @returns Booleano indicando se o URL é válido
 */
export const isValidURL = (url: string): boolean => {
  if (!url) return false;

  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Verifica se um valor é um número válido
 * @param value Valor a ser verificado
 * @returns Booleano indicando se é um número válido
 */
export const isValidNumber = (value: any): boolean => {
  if (value === null || value === undefined || value === "") return false;

  // Para strings, tenta converter para número
  if (typeof value === "string") {
    value = value.trim().replace(",", ".");
  }

  return !isNaN(Number(value)) && isFinite(Number(value));
};

/**
 * Verifica se um objeto é vazio
 * @param obj Objeto a ser verificado
 * @returns Booleano indicando se o objeto é vazio
 */
export const isEmptyObject = (obj: any): boolean => {
  if (!obj) return true;
  if (typeof obj !== "object") return false;
  if (Array.isArray(obj)) return obj.length === 0;

  return Object.keys(obj).length === 0;
};

/**
 * Verifica se um token JWT está expirado
 * @param token Token JWT
 * @param margin Margem de segurança em segundos (padrão: definido em constants)
 * @returns Booleano indicando se o token está expirado
 */
export const isTokenExpired = (
  token: string,
  margin: number = JWT_EXPIRATION_MARGIN
): boolean => {
  if (!token) return true;

  try {
    const decoded = jwt_decode<DecodedToken>(token);
    if (!decoded.exp) return true;

    // Compara com o tempo atual, considerando uma margem de segurança
    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime + margin;
  } catch (error) {
    console.error("Error decoding token:", error);
    return true;
  }
};

/**
 * Verifica se um arquivo atende aos critérios de tamanho e tipo
 * @param file Arquivo a ser validado
 * @param allowedTypes Array de tipos MIME permitidos
 * @param maxSizeInMB Tamanho máximo em MB
 * @returns Objeto com resultado da validação e mensagem
 */
export const validateFile = (
  file: File,
  allowedTypes: string[] = [],
  maxSizeInMB: number = 5
): { isValid: boolean; message: string } => {
  if (!file) {
    return { isValid: false, message: "Nenhum arquivo selecionado." };
  }

  // Validação de tamanho
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
  if (file.size > maxSizeInBytes) {
    return {
      isValid: false,
      message: `O arquivo excede o tamanho máximo de ${maxSizeInMB}MB.`,
    };
  }

  // Validação de tipo se especificado
  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
    const formattedTypes = allowedTypes
      .map((type) => type.replace("application/", "").replace("image/", ""))
      .join(", ");

    return {
      isValid: false,
      message: `Tipo de arquivo não permitido. Use: ${formattedTypes}.`,
    };
  }

  return { isValid: true, message: "Arquivo válido." };
};

/**
 * Exportação padrão de todas as funções
 */
export default {
  isValidEmail,
  isValidPassword,
  validatePasswordStrength,
  isValidCPF,
  isValidCNPJ,
  isValidCEP,
  isValidPhone,
  isValidURL,
  isValidNumber,
  isEmptyObject,
  isTokenExpired,
  validateFile,
};
