import React, { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

export interface TimeAgoProps {
  /**
   * The date to calculate time ago from
   */
  date: Date | string | number;
  /**
   * Time period (in ms) to update the displayed time
   * Set to 0 to disable auto-updates
   */
  updateInterval?: number;
  /**
   * Format to use for showing time
   */
  format?: "short" | "long" | "mini";
  /**
   * Maximum time period (in ms) after which to display the actual date
   * Set to 0 to always display relative time
   */
  maxRelativeTime?: number;
  /**
   * Format to use when displaying the actual date
   */
  dateFormat?: Intl.DateTimeFormatOptions;
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Whether to include "ago" suffix in long format
   */
  includeAgoSuffix?: boolean;
}

/**
 * Component that displays relative time (e.g., "5 minutes ago", "2 days ago")
 */
export const TimeAgo: React.FC<TimeAgoProps> = ({
  date,
  updateInterval = 60000, // Default to update every minute
  format = "long",
  maxRelativeTime = 30 * 24 * 60 * 60 * 1000, // Default to 30 days
  dateFormat = { year: "numeric", month: "short", day: "numeric" },
  className,
  includeAgoSuffix = true,
}) => {
  const [timeAgo, setTimeAgo] = useState<string>("");

  // Convert input date to Date object
  const getDateObject = (input: Date | string | number): Date => {
    if (input instanceof Date) return input;
    if (typeof input === "string" || typeof input === "number") {
      return new Date(input);
    }
    return new Date();
  };

  // Format the time ago string
  const formatTimeAgo = () => {
    const dateObj = getDateObject(date);
    const now = new Date();
    const diffMs = now.getTime() - dateObj.getTime();

    // If the difference is greater than maxRelativeTime, show the actual date
    if (maxRelativeTime > 0 && diffMs > maxRelativeTime) {
      return dateObj.toLocaleDateString(undefined, dateFormat);
    }

    // Calculate the time units
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    const diffWeek = Math.floor(diffDay / 7);
    const diffMonth = Math.floor(diffDay / 30);
    const diffYear = Math.floor(diffDay / 365);

    // Format based on the requested format
    if (format === "short") {
      if (diffSec < 60) return `${diffSec}s`;
      if (diffMin < 60) return `${diffMin}m`;
      if (diffHour < 24) return `${diffHour}h`;
      if (diffDay < 7) return `${diffDay}d`;
      if (diffWeek < 5) return `${diffWeek}w`;
      if (diffMonth < 12) return `${diffMonth}mo`;
      return `${diffYear}y`;
    } else if (format === "mini") {
      if (diffSec < 60) return `${diffSec}s`;
      if (diffMin < 60) return `${diffMin}m`;
      if (diffHour < 24) return `${diffHour}h`;
      if (diffDay < 31) return `${diffDay}d`;
      return `${diffMonth}mo`;
    } else {
      // Long format
      const suffix = includeAgoSuffix ? " ago" : "";
      if (diffSec < 60)
        return diffSec === 1
          ? `1 second${suffix}`
          : `${diffSec} seconds${suffix}`;
      if (diffMin < 60)
        return diffMin === 1
          ? `1 minute${suffix}`
          : `${diffMin} minutes${suffix}`;
      if (diffHour < 24)
        return diffHour === 1
          ? `1 hour${suffix}`
          : `${diffHour} hours${suffix}`;
      if (diffDay < 7)
        return diffDay === 1 ? `1 day${suffix}` : `${diffDay} days${suffix}`;
      if (diffWeek < 5)
        return diffWeek === 1
          ? `1 week${suffix}`
          : `${diffWeek} weeks${suffix}`;
      if (diffMonth < 12)
        return diffMonth === 1
          ? `1 month${suffix}`
          : `${diffMonth} months${suffix}`;
      return diffYear === 1 ? `1 year${suffix}` : `${diffYear} years${suffix}`;
    }
  };

  useEffect(() => {
    // Format time immediately
    setTimeAgo(formatTimeAgo());

    // Set up interval for updates if requested
    if (updateInterval > 0) {
      const interval = setInterval(() => {
        setTimeAgo(formatTimeAgo());
      }, updateInterval);

      // Clean up interval on unmount
      return () => clearInterval(interval);
    }
  }, [
    date,
    updateInterval,
    format,
    maxRelativeTime,
    dateFormat,
    includeAgoSuffix,
  ]);

  return (
    <time
      dateTime={getDateObject(date).toISOString()}
      title={getDateObject(date).toLocaleString()}
      className={cn("whitespace-nowrap", className)}
    >
      {timeAgo}
    </time>
  );
};
