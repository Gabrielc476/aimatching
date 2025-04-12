import React from "react";
import {
  FormControl,
  FormDescription,
  FormField as FormFieldUI,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { UseFormReturn } from "react-hook-form";

interface FormFieldProps {
  form: UseFormReturn<any>;
  name: string;
  label?: string;
  description?: string;
  placeholder?: string;
  type?: string;
  autoComplete?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  render?: (props: { field: any }) => React.ReactNode;
}

/**
 * FormField - Um componente reutilizável para campos de formulário
 *
 * Este componente encapsula a lógica de um campo de formulário completo,
 * incluindo label, input, mensagens de erro e descrição.
 */
const FormField: React.FC<FormFieldProps> = ({
  form,
  name,
  label,
  description,
  placeholder,
  type = "text",
  autoComplete,
  disabled = false,
  required = false,
  className,
  render,
}) => {
  return (
    <FormFieldUI
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          {label && (
            <FormLabel>
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
            </FormLabel>
          )}
          <FormControl>
            {render ? (
              render({ field })
            ) : (
              <Input
                {...field}
                type={type}
                placeholder={placeholder}
                autoComplete={autoComplete}
                disabled={disabled}
                className="w-full"
              />
            )}
          </FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
};

export default FormField;
