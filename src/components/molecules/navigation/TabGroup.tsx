import React from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

export interface TabItem {
  value: string;
  label: string;
  content: React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
}

interface TabGroupProps {
  items: TabItem[];
  defaultValue?: string;
  onChange?: (value: string) => void;
  className?: string;
  tabsListClassName?: string;
  tabsContentClassName?: string;
  variant?: "default" | "outline" | "underline";
  orientation?: "horizontal" | "vertical";
}

/**
 * TabGroup - Componente de navegação por abas
 *
 * Permite navegar entre diferentes seções de conteúdo através de abas.
 */
const TabGroup: React.FC<TabGroupProps> = ({
  items,
  defaultValue,
  onChange,
  className,
  tabsListClassName,
  tabsContentClassName,
  variant = "default",
  orientation = "horizontal",
}) => {
  if (!items || items.length === 0) return null;

  // Use o valor da primeira aba como padrão se não for fornecido
  const defaultTab = defaultValue || items[0]?.value;

  // Mapeia as variantes para classes CSS
  const variantClasses = {
    default: "",
    outline: "tabs-outline",
    underline: "tabs-underline",
  };

  // Mapeia a orientação para classes CSS
  const orientationClasses = {
    horizontal: "",
    vertical: "flex-col items-start",
  };

  return (
    <Tabs
      defaultValue={defaultTab}
      onValueChange={onChange}
      className={cn(variantClasses[variant], className)}
    >
      <TabsList
        className={cn(orientationClasses[orientation], tabsListClassName)}
      >
        {items.map((tab) => (
          <TabsTrigger
            key={tab.value}
            value={tab.value}
            disabled={tab.disabled}
            className="flex items-center gap-2"
          >
            {tab.icon && <span>{tab.icon}</span>}
            <span>{tab.label}</span>
          </TabsTrigger>
        ))}
      </TabsList>

      {items.map((tab) => (
        <TabsContent
          key={tab.value}
          value={tab.value}
          className={tabsContentClassName}
        >
          {tab.content}
        </TabsContent>
      ))}
    </Tabs>
  );
};

export default TabGroup;
