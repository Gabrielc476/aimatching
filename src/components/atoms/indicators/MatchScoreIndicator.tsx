import React from "react";
import { cn } from "@/lib/utils";

export interface MatchScoreIndicatorProps {
  /**
   * Match score as a percentage (0-100)
   */
  score: number;
  /**
   * Size of the indicator in pixels
   */
  size?: "sm" | "md" | "lg";
  /**
   * Whether to show the score percentage inside the indicator
   */
  showPercentage?: boolean;
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Additional CSS classes for the text
   */
  textClassName?: string;
}

/**
 * Circular indicator that displays a match score percentage
 */
export const MatchScoreIndicator: React.FC<MatchScoreIndicatorProps> = ({
  score,
  size = "md",
  showPercentage = true,
  className,
  textClassName,
}) => {
  // Ensure score is within 0-100 range
  const normalizedScore = Math.max(0, Math.min(100, score));

  // Calculate the stroke-dashoffset based on the score
  // The circumference of a circle is 2 * PI * radius
  // Using 100 as the circumference for simplicity
  const circumference = 100;
  const offset = circumference - (normalizedScore / 100) * circumference;

  // Determine size-based classes
  const sizeClasses = {
    sm: "w-12 h-12 text-sm",
    md: "w-16 h-16 text-base",
    lg: "w-20 h-20 text-lg",
  };

  // Determine color based on score
  const getColorClass = () => {
    if (normalizedScore >= 85) return "text-green-500";
    if (normalizedScore >= 70) return "text-blue-500";
    if (normalizedScore >= 50) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div
      className={cn(
        "relative inline-flex items-center justify-center",
        sizeClasses[size],
        className
      )}
    >
      {/* Background circle */}
      <svg className="w-full h-full -rotate-90">
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          fill="none"
          stroke="currentColor"
          strokeWidth="10%"
          className="text-gray-200 dark:text-gray-700"
        />

        {/* Foreground circle representing the score */}
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          fill="none"
          stroke="currentColor"
          strokeWidth="10%"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={getColorClass()}
        />
      </svg>

      {/* Score text */}
      {showPercentage && (
        <div
          className={cn(
            "absolute inset-0 flex items-center justify-center font-medium",
            getColorClass(),
            textClassName
          )}
        >
          {Math.round(normalizedScore)}%
        </div>
      )}
    </div>
  );
};
