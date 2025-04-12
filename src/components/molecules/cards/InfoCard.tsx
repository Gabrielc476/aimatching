import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface InfoCardProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  footer?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
  headerClassName?: string;
  contentClassName?: string;
  footerClassName?: string;
  type?: "default" | "destructive" | "success" | "info";
  onClick?: () => void;
}

/**
 * InfoCard - Componente para exibir informações em formato de cartão
 *
 * Utilizado para exibir informações concisas com título,
 * descrição opcional e conteúdo personalizado.
 */
const InfoCard: React.FC<InfoCardProps> = ({
  title,
  description,
  icon,
  footer,
  children,
  className,
  headerClassName,
  contentClassName,
  footerClassName,
  onClick,
}) => {
  return (
    <Card
      className={cn(
        "overflow-hidden transition-all hover:shadow-md",
        onClick ? "cursor-pointer" : "",
        className
      )}
      onClick={onClick}
    >
      <CardHeader
        className={cn("flex flex-row items-center gap-4", headerClassName)}
      >
        {icon && <div className="flex items-center justify-center">{icon}</div>}
        <div>
          <CardTitle>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </div>
      </CardHeader>

      {children && (
        <CardContent className={cn("pt-0", contentClassName)}>
          {children}
        </CardContent>
      )}

      {footer && (
        <CardFooter
          className={cn("border-t bg-muted/20 px-6 py-4", footerClassName)}
        >
          {footer}
        </CardFooter>
      )}
    </Card>
  );
};

export default InfoCard;
