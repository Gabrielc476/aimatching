import React from "react";
import { cn } from "@/lib/utils";

export interface SalaryRangeProps {
  /**
   * Minimum salary value
   */
  min?: number;
  /**
   * Maximum salary value
   */
  max?: number;
  /**
   * Raw salary string (used when min/max are not available)
   */
  salaryText?: string;
  /**
   * Currency symbol, defaults to '$'
   */
  currency?: string;
  /**
   * Time period (yearly, monthly, hourly)
   */
  period?: "yearly" | "monthly" | "hourly" | "weekly";
  /**
   * Show the time period text
   */
  showPeriod?: boolean;
  /**
   * Format of displayed value
   */
  format?: "compact" | "full";
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Set to true to show average in addition to range
   */
  showAverage?: boolean;
  /**
   * Custom class for the currency symbol
   */
  currencyClassName?: string;
  /**
   * Custom class for the amount
   */
  amountClassName?: string;
  /**
   * Custom class for the period
   */
  periodClassName?: string;
}

/**
 * Utility to format salary numbers
 */
const formatSalary = (
  value: number,
  format: "compact" | "full",
  currency: string
): string => {
  if (format === "compact") {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${currency}${(value / 1000).toFixed(0)}K`;
    }
  }

  // Default to full format with locale formatting
  return `${currency}${value.toLocaleString()}`;
};

/**
 * Component to display salary information in consistent format
 */
export const SalaryRange: React.FC<SalaryRangeProps> = ({
  min,
  max,
  salaryText,
  currency = "$",
  period = "yearly",
  showPeriod = true,
  format = "full",
  className,
  showAverage = false,
  currencyClassName,
  amountClassName,
  periodClassName,
}) => {
  // Handle case when both min and max are not provided
  if (min === undefined && max === undefined && !salaryText) {
    return <span className={className}>Salary not disclosed</span>;
  }

  // If raw salary text is provided and no min/max, display it directly
  if (salaryText && min === undefined && max === undefined) {
    return <span className={className}>{salaryText}</span>;
  }

  // Only one of min/max is provided
  if (min !== undefined && max === undefined) {
    return (
      <span className={cn("whitespace-nowrap", className)}>
        <span className={cn("text-muted-foreground", currencyClassName)}>
          {currency}
        </span>
        <span className={amountClassName}>
          {formatSalary(min, format, "").substring(1)}
        </span>
        {showPeriod && (
          <span
            className={cn(
              "text-xs text-muted-foreground ml-1",
              periodClassName
            )}
          >
            {period === "yearly"
              ? "/year"
              : period === "monthly"
              ? "/month"
              : period === "weekly"
              ? "/week"
              : "/hour"}
          </span>
        )}
      </span>
    );
  }

  if (min === undefined && max !== undefined) {
    return (
      <span className={cn("whitespace-nowrap", className)}>
        Up to{" "}
        <span className={cn("text-muted-foreground", currencyClassName)}>
          {currency}
        </span>
        <span className={amountClassName}>
          {formatSalary(max, format, "").substring(1)}
        </span>
        {showPeriod && (
          <span
            className={cn(
              "text-xs text-muted-foreground ml-1",
              periodClassName
            )}
          >
            {period === "yearly"
              ? "/year"
              : period === "monthly"
              ? "/month"
              : period === "weekly"
              ? "/week"
              : "/hour"}
          </span>
        )}
      </span>
    );
  }

  // Both min and max are provided
  if (min !== undefined && max !== undefined) {
    const average = showAverage ? Math.round((min + max) / 2) : undefined;

    return (
      <span className={cn("whitespace-nowrap", className)}>
        <span className={cn("text-muted-foreground", currencyClassName)}>
          {currency}
        </span>
        <span className={amountClassName}>
          {formatSalary(min, format, "").substring(1)} -{" "}
          {formatSalary(max, format, "").substring(1)}
        </span>
        {average && (
          <span className={cn("text-xs text-muted-foreground mx-1")}>
            (avg: {currency}
            {formatSalary(average, format, "").substring(1)})
          </span>
        )}
        {showPeriod && (
          <span
            className={cn(
              "text-xs text-muted-foreground ml-1",
              periodClassName
            )}
          >
            {period === "yearly"
              ? "/year"
              : period === "monthly"
              ? "/month"
              : period === "weekly"
              ? "/week"
              : "/hour"}
          </span>
        )}
      </span>
    );
  }

  // Fallback for unexpected state
  return <span className={className}>Salary not disclosed</span>;
};
