// frontend/components/organisms/auth/RegisterForm.tsx
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import Link from "next/link";
import { Eye, EyeOff, Loader2, UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

// Password validation schema
const passwordSchema = z
  .string()
  .min(8, {
    message: "A senha deve ter pelo menos 8 caracteres.",
  })
  .regex(/[A-Z]/, {
    message: "A senha deve conter pelo menos uma letra maiúscula.",
  })
  .regex(/[a-z]/, {
    message: "A senha deve conter pelo menos uma letra minúscula.",
  })
  .regex(/[0-9]/, {
    message: "A senha deve conter pelo menos um número.",
  })
  .regex(/[^A-Za-z0-9]/, {
    message: "A senha deve conter pelo menos um caractere especial.",
  });

// Registration form schema
const registerFormSchema = z
  .object({
    name: z.string().min(3, {
      message: "O nome deve ter pelo menos 3 caracteres.",
    }),
    email: z.string().email({
      message: "Por favor, informe um email válido.",
    }),
    password: passwordSchema,
    confirmPassword: z.string().min(1, {
      message: "Por favor, confirme sua senha.",
    }),
    agreeTerms: z.boolean().refine((val) => val === true, {
      message: "Você deve concordar com os termos e condições.",
    }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "As senhas não correspondem.",
    path: ["confirmPassword"],
  });

type RegisterFormValues = z.infer<typeof registerFormSchema>;

export interface RegisterFormProps {
  onSubmit: (
    values: Omit<RegisterFormValues, "confirmPassword" | "agreeTerms">
  ) => Promise<void>;
  error?: string | null;
  isLoading?: boolean;
}

const RegisterForm = ({
  onSubmit,
  error = null,
  isLoading = false,
}: RegisterFormProps) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Define form
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerFormSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      agreeTerms: false,
    },
  });

  // Form submission handler
  const handleSubmit = async (values: RegisterFormValues) => {
    setSubmitting(true);
    try {
      // We don't need to send confirmPassword and agreeTerms to the API
      const { confirmPassword, agreeTerms, ...registrationData } = values;
      await onSubmit(registrationData);
    } catch (error) {
      // Error is handled in the parent component
      console.error("Registration error:", error);
    } finally {
      setSubmitting(false);
    }
  };

  // Password strength indicator
  const getPasswordStrength = (
    password: string
  ): { strength: number; label: string; color: string } => {
    if (!password) {
      return { strength: 0, label: "Muito fraca", color: "bg-destructive" };
    }

    let strength = 0;

    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;

    const labels = ["Muito fraca", "Fraca", "Média", "Boa", "Forte"];
    const colors = [
      "bg-destructive",
      "bg-destructive",
      "bg-amber-500",
      "bg-amber-500",
      "bg-green-500",
    ];

    return {
      strength,
      label: labels[Math.min(strength, 4)],
      color: colors[Math.min(strength, 4)],
    };
  };

  const passwordValue = form.watch("password");
  const passwordStrength = getPasswordStrength(passwordValue);

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">
          Criar Conta
        </CardTitle>
        <CardDescription className="text-center">
          Cadastre-se para encontrar as melhores vagas para o seu perfil
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome completo</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Seu nome completo"
                      autoComplete="name"
                      disabled={isLoading || submitting}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="seu.email@exemplo.com"
                      type="email"
                      autoComplete="email"
                      disabled={isLoading || submitting}
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Usaremos seu email para login e comunicações importantes
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Senha</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        placeholder="••••••••"
                        type={showPassword ? "text" : "password"}
                        autoComplete="new-password"
                        disabled={isLoading || submitting}
                        {...field}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0 h-full px-3"
                        onClick={() => setShowPassword(!showPassword)}
                        tabIndex={-1}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                  </FormControl>
                  {passwordValue && (
                    <>
                      <div className="mt-2 space-y-1">
                        <div className="flex justify-between text-xs">
                          <span>Força da senha: </span>
                          <span
                            className={
                              passwordStrength.strength >= 4
                                ? "text-green-500"
                                : "text-muted-foreground"
                            }
                          >
                            {passwordStrength.label}
                          </span>
                        </div>
                        <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${passwordStrength.color} transition-all`}
                            style={{
                              width: `${
                                (passwordStrength.strength / 5) * 100
                              }%`,
                            }}
                          ></div>
                        </div>
                      </div>
                      <ul className="text-xs space-y-1 mt-1 text-muted-foreground">
                        <li
                          className={
                            /[A-Z]/.test(passwordValue) ? "text-green-500" : ""
                          }
                        >
                          ✓ Pelo menos uma letra maiúscula
                        </li>
                        <li
                          className={
                            /[a-z]/.test(passwordValue) ? "text-green-500" : ""
                          }
                        >
                          ✓ Pelo menos uma letra minúscula
                        </li>
                        <li
                          className={
                            /[0-9]/.test(passwordValue) ? "text-green-500" : ""
                          }
                        >
                          ✓ Pelo menos um número
                        </li>
                        <li
                          className={
                            /[^A-Za-z0-9]/.test(passwordValue)
                              ? "text-green-500"
                              : ""
                          }
                        >
                          ✓ Pelo menos um caractere especial
                        </li>
                        <li
                          className={
                            passwordValue.length >= 8 ? "text-green-500" : ""
                          }
                        >
                          ✓ Mínimo de 8 caracteres
                        </li>
                      </ul>
                    </>
                  )}
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirmar Senha</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        placeholder="••••••••"
                        type={showConfirmPassword ? "text" : "password"}
                        autoComplete="new-password"
                        disabled={isLoading || submitting}
                        {...field}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0 h-full px-3"
                        onClick={() =>
                          setShowConfirmPassword(!showConfirmPassword)
                        }
                        tabIndex={-1}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="agreeTerms"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0 py-2">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={isLoading || submitting}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel className="text-sm">
                      Concordo com os{" "}
                      <Link
                        href="/terms"
                        className="text-primary hover:underline"
                        target="_blank"
                      >
                        Termos de Serviço
                      </Link>{" "}
                      e{" "}
                      <Link
                        href="/privacy"
                        className="text-primary hover:underline"
                        target="_blank"
                      >
                        Política de Privacidade
                      </Link>
                    </FormLabel>
                    <FormMessage />
                  </div>
                </FormItem>
              )}
            />

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || submitting}
            >
              {isLoading || submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processando...
                </>
              ) : (
                <>
                  <UserPlus className="mr-2 h-4 w-4" />
                  Criar Conta
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex justify-center">
        <p className="text-sm text-muted-foreground">
          Já tem uma conta?{" "}
          <Link href="/auth/login" className="text-primary hover:underline">
            Faça login
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
};

export default RegisterForm;
