import React from "react";
import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

/**
 * Job status types
 */
export type JobStatus =
  | "new" // Newly scraped job
  | "viewed" // Job viewed by the user
  | "applied" // User has applied to this job
  | "saved" // User saved the job for later
  | "interviewed" // User has interviewed for this job
  | "offered" // User received an offer for this job
  | "rejected" // User was rejected for this job
  | "closed" // Job position was closed/filled
  | "expired"; // Job listing has expired

/**
 * JobStatusIndicator variants
 */
const jobStatusIndicatorVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium",
  {
    variants: {
      status: {
        new: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
        viewed:
          "bg-gray-100 text-gray-800 dark:bg-gray-800/40 dark:text-gray-300",
        applied:
          "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
        saved:
          "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
        interviewed:
          "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400",
        offered:
          "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
        rejected:
          "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
        closed:
          "bg-gray-100 text-gray-800 dark:bg-gray-800/40 dark:text-gray-300",
        expired:
          "bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400",
      },
      withDot: {
        true: "",
        false: "",
      },
      size: {
        sm: "px-1.5 py-0.5 text-xs",
        md: "px-2 py-1 text-xs",
        lg: "px-2.5 py-1.5 text-sm",
      },
    },
    compoundVariants: [
      {
        withDot: true,
        size: "sm",
        class: "pl-5 relative",
      },
      {
        withDot: true,
        size: "md",
        class: "pl-6 relative",
      },
      {
        withDot: true,
        size: "lg",
        class: "pl-7 relative",
      },
    ],
    defaultVariants: {
      status: "new",
      withDot: true,
      size: "md",
    },
  }
);

/**
 * Status label text mapping
 */
const statusLabels: Record<JobStatus, string> = {
  new: "New",
  viewed: "Viewed",
  applied: "Applied",
  saved: "Saved",
  interviewed: "Interviewed",
  offered: "Offered",
  rejected: "Rejected",
  closed: "Closed",
  expired: "Expired",
};

export interface JobStatusIndicatorProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "children">,
    VariantProps<typeof jobStatusIndicatorVariants> {
  /**
   * The job status to display
   */
  status: JobStatus;
  /**
   * Optional custom label to display instead of the default status label
   */
  label?: string;
  /**
   * Date associated with the status (e.g., when it was applied)
   */
  date?: Date | string;
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Component for displaying job application status
 */
export const JobStatusIndicator: React.FC<JobStatusIndicatorProps> = ({
  status,
  label,
  date,
  className,
  withDot = true,
  size = "md",
  ...props
}) => {
  // Format the date if provided
  const formattedDate = date
    ? typeof date === "string"
      ? date
      : date.toLocaleDateString(undefined, { month: "short", day: "numeric" })
    : null;

  return (
    <div
      className={cn(
        jobStatusIndicatorVariants({ status, withDot, size }),
        className
      )}
      {...props}
    >
      {withDot && (
        <span
          className={cn(
            "absolute left-2 top-1/2 -translate-y-1/2 block rounded-full",
            size === "sm"
              ? "h-2 w-2"
              : size === "md"
              ? "h-2.5 w-2.5"
              : "h-3 w-3",
            status === "new" && "bg-blue-500",
            status === "viewed" && "bg-gray-500",
            status === "applied" && "bg-purple-500",
            status === "saved" && "bg-amber-500",
            status === "interviewed" && "bg-indigo-500",
            status === "offered" && "bg-green-500",
            status === "rejected" && "bg-red-500",
            status === "closed" && "bg-gray-500",
            status === "expired" && "bg-rose-500"
          )}
        />
      )}

      <span>{label || statusLabels[status]}</span>

      {formattedDate && (
        <span className="opacity-75 text-2xs">• {formattedDate}</span>
      )}
    </div>
  );
};
