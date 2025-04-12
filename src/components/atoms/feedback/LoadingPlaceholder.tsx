import React from "react";
import { cn } from "@/lib/utils";

export interface LoadingPlaceholderProps {
  /**
   * Visual style of the placeholder
   */
  variant?: "pulse" | "shimmer" | "skeleton";
  /**
   * Width of the placeholder
   */
  width?: string | number;
  /**
   * Height of the placeholder
   */
  height?: string | number;
  /**
   * Border radius of the placeholder
   */
  radius?: "none" | "sm" | "md" | "lg" | "full";
  /**
   * Make width 100% of parent
   */
  fullWidth?: boolean;
  /**
   * Dark mode invert colors
   */
  darkInvert?: boolean;
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Component for showing loading state as a placeholder
 */
export const LoadingPlaceholder: React.FC<LoadingPlaceholderProps> = ({
  variant = "pulse",
  width,
  height = "1rem",
  radius = "md",
  fullWidth = false,
  darkInvert = true,
  className,
}) => {
  const radiusMap = {
    none: "rounded-none",
    sm: "rounded-sm",
    md: "rounded-md",
    lg: "rounded-lg",
    full: "rounded-full",
  };

  // Shimmer animation style
  const shimmerStyle = {
    backgroundImage: `linear-gradient(
      to right,
      rgba(0,0,0,0) 0%,
      rgba(255,255,255,0.15) 50%,
      rgba(0,0,0,0) 100%
    )`,
    backgroundSize: "200% 100%",
    animation: "shimmer 2s infinite",
  };

  // Generate the base style based on the variant
  const getBaseStyle = () => {
    switch (variant) {
      case "shimmer":
        return cn(
          "relative overflow-hidden",
          "before:absolute before:inset-0 before:translate-x-full before:animate-shimmer",
          "before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent"
        );
      case "skeleton":
        return "animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 bg-[length:400%_100%] animate-skeleton";
      case "pulse":
      default:
        return "animate-pulse";
    }
  };

  const style: React.CSSProperties = {
    width: fullWidth ? "100%" : width,
    height: typeof height === "number" ? `${height}px` : height,
    ...(variant === "shimmer" ? shimmerStyle : {}),
  };

  return (
    <div
      className={cn(
        getBaseStyle(),
        radiusMap[radius],
        "bg-gray-200",
        darkInvert && "dark:bg-gray-700",
        className
      )}
      style={style}
      aria-hidden="true"
    />
  );
};
