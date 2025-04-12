/**
 * Date Utilities
 * Funções utilitárias para manipulação de datas
 */

/**
 * Formata uma data para exibição localizada
 * @param date Data a ser formatada (string ISO, timestamp ou objeto Date)
 * @param locale Localidade para formatação (padrão: navegador)
 * @param options Opções de formatação
 * @returns String formatada da data
 */
export const formatDate = (
  date: string | number | Date,
  locale?: string,
  options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  }
): string => {
  if (!date) return "";

  const dateObj =
    typeof date === "string" || typeof date === "number"
      ? new Date(date)
      : date;

  if (isNaN(dateObj.getTime())) {
    console.error("Invalid date provided to formatDate:", date);
    return "";
  }

  try {
    return new Intl.DateTimeFormat(locale, options).format(dateObj);
  } catch (error) {
    console.error("Error formatting date:", error);
    return "";
  }
};

/**
 * Calcula a diferença relativa entre uma data e agora (ex: "há 2 dias")
 * @param date Data para comparação
 * @param locale Localidade para formatação (padrão: navegador)
 * @returns String com a diferença relativa
 */
export const timeAgo = (
  date: string | number | Date,
  locale?: string
): string => {
  if (!date) return "";

  const dateObj =
    typeof date === "string" || typeof date === "number"
      ? new Date(date)
      : date;

  if (isNaN(dateObj.getTime())) {
    console.error("Invalid date provided to timeAgo:", date);
    return "";
  }

  try {
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });
    const now = new Date();
    const diffInSeconds = Math.floor(
      (dateObj.getTime() - now.getTime()) / 1000
    );
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInMonths = Math.floor(diffInDays / 30);
    const diffInYears = Math.floor(diffInDays / 365);

    if (Math.abs(diffInYears) >= 1) {
      return rtf.format(diffInYears, "year");
    } else if (Math.abs(diffInMonths) >= 1) {
      return rtf.format(diffInMonths, "month");
    } else if (Math.abs(diffInDays) >= 1) {
      return rtf.format(diffInDays, "day");
    } else if (Math.abs(diffInHours) >= 1) {
      return rtf.format(diffInHours, "hour");
    } else if (Math.abs(diffInMinutes) >= 1) {
      return rtf.format(diffInMinutes, "minute");
    } else {
      return rtf.format(diffInSeconds, "second");
    }
  } catch (error) {
    // Fallback para navegadores que não suportam RelativeTimeFormat
    console.warn("RelativeTimeFormat not supported, using fallback:", error);
    return formatDistance(dateObj);
  }
};

/**
 * Implementação de fallback para cálculo de distância relativa
 * @param date Data para comparação
 * @returns String com a diferença relativa
 */
const formatDistance = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return `${diffInSeconds} segundo${diffInSeconds !== 1 ? "s" : ""} atrás`;
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minuto${diffInMinutes !== 1 ? "s" : ""} atrás`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hora${diffInHours !== 1 ? "s" : ""} atrás`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return `${diffInDays} dia${diffInDays !== 1 ? "s" : ""} atrás`;
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} mês${diffInMonths !== 1 ? "es" : ""} atrás`;
  }

  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears} ano${diffInYears !== 1 ? "s" : ""} atrás`;
};

/**
 * Verifica se uma data é hoje
 * @param date Data a verificar
 * @returns Booleano indicando se a data é hoje
 */
export const isToday = (date: string | number | Date): boolean => {
  const dateObj =
    typeof date === "string" || typeof date === "number"
      ? new Date(date)
      : date;

  if (isNaN(dateObj.getTime())) {
    console.error("Invalid date provided to isToday:", date);
    return false;
  }

  const today = new Date();
  return (
    dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear()
  );
};

/**
 * Adiciona duração a uma data
 * @param date Data base
 * @param duration Objeto com duração a adicionar
 * @returns Nova data com duração adicionada
 */
export const addDuration = (
  date: string | number | Date,
  duration: {
    years?: number;
    months?: number;
    days?: number;
    hours?: number;
    minutes?: number;
    seconds?: number;
  }
): Date => {
  const dateObj =
    typeof date === "string" || typeof date === "number"
      ? new Date(date)
      : new Date(date.getTime());

  if (isNaN(dateObj.getTime())) {
    console.error("Invalid date provided to addDuration:", date);
    return new Date();
  }

  if (duration.years)
    dateObj.setFullYear(dateObj.getFullYear() + duration.years);
  if (duration.months) dateObj.setMonth(dateObj.getMonth() + duration.months);
  if (duration.days) dateObj.setDate(dateObj.getDate() + duration.days);
  if (duration.hours) dateObj.setHours(dateObj.getHours() + duration.hours);
  if (duration.minutes)
    dateObj.setMinutes(dateObj.getMinutes() + duration.minutes);
  if (duration.seconds)
    dateObj.setSeconds(dateObj.getSeconds() + duration.seconds);

  return dateObj;
};

/**
 * Formata uma duração em meses ou anos (ex: "2 anos, 3 meses")
 * @param startDate Data de início
 * @param endDate Data de fim (opcional, usa a data atual se omitido)
 * @returns String formatada com a duração
 */
export const formatDuration = (
  startDate: string | number | Date,
  endDate?: string | number | Date
): string => {
  const start =
    typeof startDate === "string" || typeof startDate === "number"
      ? new Date(startDate)
      : startDate;

  const end = endDate
    ? typeof endDate === "string" || typeof endDate === "number"
      ? new Date(endDate)
      : endDate
    : new Date();

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    console.error("Invalid date(s) provided to formatDuration:", {
      startDate,
      endDate,
    });
    return "";
  }

  // Calcular diferença em meses
  let months = (end.getFullYear() - start.getFullYear()) * 12;
  months += end.getMonth() - start.getMonth();

  // Ajuste para dia do mês
  if (end.getDate() < start.getDate()) {
    months--;
  }

  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;

  if (years === 0 && remainingMonths === 0) {
    // Menos de um mês
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 1 ? "1 dia" : `${diffDays} dias`;
  } else if (years === 0) {
    // Menos de um ano
    return remainingMonths === 1 ? "1 mês" : `${remainingMonths} meses`;
  } else if (remainingMonths === 0) {
    // Anos completos
    return years === 1 ? "1 ano" : `${years} anos`;
  } else {
    // Anos e meses
    const yearText = years === 1 ? "1 ano" : `${years} anos`;
    const monthText =
      remainingMonths === 1 ? "1 mês" : `${remainingMonths} meses`;
    return `${yearText}, ${monthText}`;
  }
};

/**
 * Converte uma string de data para objeto Date com tratamento de timezone
 * @param dateString String de data para converter
 * @returns Objeto Date
 */
export const parseDate = (dateString: string): Date => {
  if (!dateString) {
    console.error("Empty date string provided to parseDate");
    return new Date();
  }

  try {
    // Tenta analisar várias formatos de data
    if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
      // Formato ISO Date (YYYY-MM-DD)
      const [year, month, day] = dateString
        .split("-")
        .map((n) => parseInt(n, 10));
      return new Date(year, month - 1, day);
    } else if (dateString.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
      // Formato MM/DD/YYYY
      const [month, day, year] = dateString
        .split("/")
        .map((n) => parseInt(n, 10));
      return new Date(year, month - 1, day);
    } else {
      // Tentar com Date.parse
      const timestamp = Date.parse(dateString);
      if (isNaN(timestamp)) {
        throw new Error(`Unparseable date: ${dateString}`);
      }
      return new Date(timestamp);
    }
  } catch (error) {
    console.error("Error parsing date:", error);
    return new Date();
  }
};

/**
 * Exportação padrão de todas as funções
 */
export default {
  formatDate,
  timeAgo,
  isToday,
  addDuration,
  formatDuration,
  parseDate,
};
