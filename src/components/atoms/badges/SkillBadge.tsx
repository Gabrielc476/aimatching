import React from "react";
import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

/**
 * SkillBadge variants
 */
const skillBadgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "bg-primary/10 text-primary hover:bg-primary/20",
        secondary: "bg-secondary/10 text-secondary hover:bg-secondary/20",
        tech: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/40",
        soft: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400 hover:bg-purple-200 dark:hover:bg-purple-900/40",
        language:
          "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/40",
        tool: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 hover:bg-amber-200 dark:hover:bg-amber-900/40",
        certification:
          "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400 hover:bg-indigo-200 dark:hover:bg-indigo-900/40",
        matched:
          "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-900/40 ring-1 ring-emerald-500/50",
        missing:
          "bg-gray-100 text-gray-800 dark:bg-gray-800/50 dark:text-gray-400 line-through decoration-gray-500",
      },
      hasTooltip: {
        true: "cursor-help",
      },
      interactive: {
        true: "cursor-pointer",
        false: "cursor-default",
      },
      size: {
        sm: "px-1.5 py-0.25 text-xs",
        md: "px-2.5 py-0.5 text-xs",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      hasTooltip: false,
      interactive: false,
      size: "md",
    },
  }
);

export interface SkillBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof skillBadgeVariants> {
  /**
   * The skill name to display
   */
  skill: string;
  /**
   * Optional icon to display before the skill name
   */
  icon?: React.ReactNode;
  /**
   * Optional weight/experience level (1-5) shown as filled dots
   */
  proficiencyLevel?: number;
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Tooltip content to show on hover
   */
  tooltip?: string;
  /**
   * Handler for click events when interactive is true
   */
  onClick?: React.MouseEventHandler<HTMLSpanElement>;
}

/**
 * Component for displaying skills, technologies, languages and certifications
 */
export const SkillBadge: React.FC<SkillBadgeProps> = ({
  skill,
  icon,
  proficiencyLevel,
  className,
  variant = "default",
  hasTooltip = false,
  interactive = false,
  size = "md",
  tooltip,
  onClick,
  ...props
}) => {
  // Generate proficiency dots if proficiencyLevel is provided
  const renderProficiencyDots = () => {
    if (typeof proficiencyLevel !== "number") return null;

    // Ensure proficiencyLevel is between 1-5
    const level = Math.max(1, Math.min(5, proficiencyLevel));

    return (
      <div className="ml-1.5 flex items-center space-x-0.5">
        {[...Array(5)].map((_, index) => (
          <div
            key={index}
            className={cn(
              "rounded-full",
              size === "sm"
                ? "h-1 w-1"
                : size === "md"
                ? "h-1.5 w-1.5"
                : "h-2 w-2",
              index < level ? "bg-current opacity-90" : "bg-current opacity-20"
            )}
          />
        ))}
      </div>
    );
  };

  return (
    <span
      className={cn(
        skillBadgeVariants({
          variant,
          hasTooltip: !!tooltip || hasTooltip,
          interactive,
          size,
          className,
        })
      )}
      title={tooltip}
      onClick={interactive ? onClick : undefined}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      {...props}
    >
      {icon && <span className="mr-1">{icon}</span>}
      {skill}
      {proficiencyLevel && renderProficiencyDots()}
    </span>
  );
};
