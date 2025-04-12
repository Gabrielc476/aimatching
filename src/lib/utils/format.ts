/**
 * Format Utilities
 * Funções utilitárias para formatação de dados
 */

/**
 * Formata um valor monetário
 * @param value Valor a ser formatado
 * @param currency Código da moeda (padrão: BRL)
 * @param locale Localidade para formatação (padrão: pt-BR)
 * @returns String formatada com o valor monetário
 */
export const formatCurrency = (
  value: number,
  currency: string = "BRL",
  locale: string = "pt-BR"
): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return "";
  }

  try {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  } catch (error) {
    console.error("Error formatting currency:", error);
    return `${value}`;
  }
};

/**
 * Formata um valor numérico com separadores de milhar e casas decimais
 * @param value Valor a ser formatado
 * @param decimals Número de casas decimais (padrão: 2)
 * @param locale Localidade para formatação (padrão: pt-BR)
 * @returns String formatada com o valor numérico
 */
export const formatNumber = (
  value: number,
  decimals: number = 2,
  locale: string = "pt-BR"
): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return "";
  }

  try {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  } catch (error) {
    console.error("Error formatting number:", error);
    return `${value}`;
  }
};

/**
 * Formata um percentual
 * @param value Valor a ser formatado (0-1)
 * @param decimals Número de casas decimais (padrão: 2)
 * @param locale Localidade para formatação (padrão: pt-BR)
 * @returns String formatada com o valor percentual
 */
export const formatPercent = (
  value: number,
  decimals: number = 2,
  locale: string = "pt-BR"
): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return "";
  }

  try {
    return new Intl.NumberFormat(locale, {
      style: "percent",
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  } catch (error) {
    console.error("Error formatting percent:", error);
    return `${value * 100}%`;
  }
};

/**
 * Formata um faixa salarial (min-max)
 * @param min Valor mínimo
 * @param max Valor máximo
 * @param currency Código da moeda (padrão: BRL)
 * @param locale Localidade para formatação (padrão: pt-BR)
 * @returns String formatada com a faixa salarial
 */
export const formatSalaryRange = (
  min?: number | null,
  max?: number | null,
  currency: string = "BRL",
  locale: string = "pt-BR"
): string => {
  if (
    (min === null || min === undefined || isNaN(min as number)) &&
    (max === null || max === undefined || isNaN(max as number))
  ) {
    return "A combinar";
  }

  if (
    min !== null &&
    min !== undefined &&
    !isNaN(min) &&
    (max === null || max === undefined || isNaN(max as number) || max === min)
  ) {
    return `A partir de ${formatCurrency(min, currency, locale)}`;
  }

  if (
    (min === null || min === undefined || isNaN(min as number)) &&
    max !== null &&
    max !== undefined &&
    !isNaN(max)
  ) {
    return `Até ${formatCurrency(max, currency, locale)}`;
  }

  return `${formatCurrency(min as number, currency, locale)} - ${formatCurrency(
    max as number,
    currency,
    locale
  )}`;
};

/**
 * Formata um nome com capitalização apropriada
 * @param name Nome a ser formatado
 * @returns Nome formatado com capitalização apropriada
 */
export const formatName = (name: string): string => {
  if (!name) return "";

  const lowerCaseWords = [
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "a",
    "o",
    "em",
    "para",
    "por",
    "com",
    "sem",
    "sob",
  ];

  return name
    .toLowerCase()
    .split(" ")
    .map((word, index, arr) => {
      // Preserva acrônimos (palavras totalmente em maiúsculas no original)
      const originalWord = name.split(" ")[index];
      if (
        originalWord === originalWord.toUpperCase() &&
        originalWord.length > 1
      ) {
        return originalWord;
      }

      // Aplica regras de capitalização para palavras comuns
      if (
        lowerCaseWords.includes(word) &&
        index !== 0 &&
        index !== arr.length - 1
      ) {
        return word;
      }

      return word.charAt(0).toUpperCase() + word.substring(1);
    })
    .join(" ");
};

/**
 * Trunca um texto e adiciona reticências se necessário
 * @param text Texto a ser truncado
 * @param length Comprimento máximo
 * @param suffix Sufixo a ser adicionado (padrão: "...")
 * @returns Texto truncado
 */
export const truncateText = (
  text: string,
  length: number,
  suffix: string = "..."
): string => {
  if (!text || text.length <= length) {
    return text || "";
  }

  return text.substring(0, length).trim() + suffix;
};

/**
 * Formata um número de telefone em formato brasileiro
 * @param phone Número do telefone (apenas dígitos)
 * @returns Telefone formatado
 */
export const formatPhoneNumber = (phone: string): string => {
  if (!phone) return "";

  // Remove caracteres não numéricos
  const cleaned = phone.replace(/\D/g, "");

  if (cleaned.length === 11) {
    // Celular: (XX) 9XXXX-XXXX
    return `(${cleaned.substring(0, 2)}) ${cleaned.substring(
      2,
      7
    )}-${cleaned.substring(7, 11)}`;
  } else if (cleaned.length === 10) {
    // Fixo: (XX) XXXX-XXXX
    return `(${cleaned.substring(0, 2)}) ${cleaned.substring(
      2,
      6
    )}-${cleaned.substring(6, 10)}`;
  } else if (cleaned.length === 9) {
    // Celular sem DDD: 9XXXX-XXXX
    return `${cleaned.substring(0, 5)}-${cleaned.substring(5, 9)}`;
  } else if (cleaned.length === 8) {
    // Fixo sem DDD: XXXX-XXXX
    return `${cleaned.substring(0, 4)}-${cleaned.substring(4, 8)}`;
  }

  // Se não se encaixar em nenhum padrão, retorna como está
  return phone;
};

/**
 * Formata um CEP em formato brasileiro
 * @param cep CEP (apenas dígitos)
 * @returns CEP formatado
 */
export const formatCEP = (cep: string): string => {
  if (!cep) return "";

  // Remove caracteres não numéricos
  const cleaned = cep.replace(/\D/g, "");

  if (cleaned.length === 8) {
    return `${cleaned.substring(0, 5)}-${cleaned.substring(5, 8)}`;
  }

  return cep;
};

/**
 * Formata um CPF em formato brasileiro
 * @param cpf CPF (apenas dígitos)
 * @returns CPF formatado
 */
export const formatCPF = (cpf: string): string => {
  if (!cpf) return "";

  // Remove caracteres não numéricos
  const cleaned = cpf.replace(/\D/g, "");

  if (cleaned.length === 11) {
    return `${cleaned.substring(0, 3)}.${cleaned.substring(
      3,
      6
    )}.${cleaned.substring(6, 9)}-${cleaned.substring(9, 11)}`;
  }

  return cpf;
};

/**
 * Formata um CNPJ em formato brasileiro
 * @param cnpj CNPJ (apenas dígitos)
 * @returns CNPJ formatado
 */
export const formatCNPJ = (cnpj: string): string => {
  if (!cnpj) return "";

  // Remove caracteres não numéricos
  const cleaned = cnpj.replace(/\D/g, "");

  if (cleaned.length === 14) {
    return `${cleaned.substring(0, 2)}.${cleaned.substring(
      2,
      5
    )}.${cleaned.substring(5, 8)}/${cleaned.substring(
      8,
      12
    )}-${cleaned.substring(12, 14)}`;
  }

  return cnpj;
};

/**
 * Formata bytes para representação legível (KB, MB, GB)
 * @param bytes Quantidade de bytes
 * @param decimals Casas decimais (padrão: 2)
 * @returns String formatada com a representação dos bytes
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${
    sizes[i]
  }`;
};

/**
 * Exportação padrão de todas as funções
 */
export default {
  formatCurrency,
  formatNumber,
  formatPercent,
  formatSalaryRange,
  formatName,
  truncateText,
  formatPhoneNumber,
  formatCEP,
  formatCPF,
  formatCNPJ,
  formatBytes,
};
