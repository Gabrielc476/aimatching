import React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
  homeHref?: string;
  showHomeIcon?: boolean;
}

/**
 * Breadcrumbs - Componente de navegação para mostrar hierarquia de páginas
 *
 * Exibe o caminho de navegação do usuário com links para níveis anteriores.
 */
const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  className,
  homeHref = "/dashboard",
  showHomeIcon = true,
}) => {
  if (!items || items.length === 0) return null;

  return (
    <nav className={cn("flex", className)} aria-label="Breadcrumbs">
      <ol className="flex items-center space-x-1 text-sm">
        {showHomeIcon && (
          <li>
            <Link
              href={homeHref}
              className="flex items-center text-muted-foreground hover:text-foreground transition-colors"
            >
              <Home size={16} />
              <span className="sr-only">Home</span>
            </Link>
          </li>
        )}

        {showHomeIcon && items.length > 0 && (
          <li className="flex items-center">
            <ChevronRight size={14} className="text-muted-foreground mx-1" />
          </li>
        )}

        {items.map((item, index) => (
          <React.Fragment key={index}>
            <li>
              {item.href ? (
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-1",
                    index === items.length - 1
                      ? "font-medium text-foreground"
                      : "text-muted-foreground hover:text-foreground transition-colors"
                  )}
                >
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}</span>
                </Link>
              ) : (
                <span className="flex items-center gap-1 font-medium text-foreground">
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}</span>
                </span>
              )}
            </li>

            {index < items.length - 1 && (
              <li className="flex items-center">
                <ChevronRight
                  size={14}
                  className="text-muted-foreground mx-1"
                />
              </li>
            )}
          </React.Fragment>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
