// frontend/components/organisms/profile/ProfileForm.tsx
import { useState, useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Save, Trash, Plus, Loader2 } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "sonner";

// Define experience levels
const experienceLevels = [
  { value: "entry", label: "Iniciante (0-2 anos)" },
  { value: "mid", label: "Intermediário (2-5 anos)" },
  { value: "senior", label: "Sênior (5-8 anos)" },
  { value: "expert", label: "Especialista (8+ anos)" },
  { value: "executive", label: "Executivo" },
];

// Define form schema using zod
const profileFormSchema = z.object({
  title: z.string().min(3, {
    message: "O título profissional deve ter pelo menos 3 caracteres.",
  }),
  location: z.string().min(2, {
    message: "A localização deve ter pelo menos 2 caracteres.",
  }),
  skills: z.array(z.string()).min(1, {
    message: "Adicione pelo menos uma habilidade.",
  }),
  experienceLevel: z.string({
    required_error: "Selecione seu nível de experiência.",
  }),
  jobPreferences: z.object({
    remoteOnly: z.boolean(),
    jobTypes: z.array(z.string()).min(1, {
      message: "Selecione pelo menos um tipo de trabalho.",
    }),
    desiredSalary: z.string().optional(),
    desiredLocations: z.array(z.string()).optional(),
  }),
  about: z
    .string()
    .max(500, {
      message: "A descrição deve ter no máximo 500 caracteres.",
    })
    .optional(),
});

// Define form types
type ProfileFormValues = z.infer<typeof profileFormSchema>;

// Available job types
const jobTypes = [
  { value: "full-time", label: "Tempo integral" },
  { value: "part-time", label: "Meio período" },
  { value: "contract", label: "Contrato" },
  { value: "temporary", label: "Temporário" },
  { value: "internship", label: "Estágio" },
  { value: "freelance", label: "Freelance" },
];

export interface ProfileFormProps {
  initialData?: Partial<ProfileFormValues>;
  onSubmit: (data: ProfileFormValues) => Promise<void>;
  isLoading?: boolean;
}

const ProfileForm = ({
  initialData,
  onSubmit,
  isLoading = false,
}: ProfileFormProps) => {
  const [newSkill, setNewSkill] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form with defaults or initial data
  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      title: initialData?.title || "",
      location: initialData?.location || "",
      skills: initialData?.skills || [],
      experienceLevel: initialData?.experienceLevel || "",
      jobPreferences: {
        remoteOnly: initialData?.jobPreferences?.remoteOnly || false,
        jobTypes: initialData?.jobPreferences?.jobTypes || ["full-time"],
        desiredSalary: initialData?.jobPreferences?.desiredSalary || "",
        desiredLocations: initialData?.jobPreferences?.desiredLocations || [],
      },
      about: initialData?.about || "",
    },
  });

  // For controlled components that aren't part of react-hook-form
  useEffect(() => {
    if (initialData) {
      form.reset({
        title: initialData.title || "",
        location: initialData.location || "",
        skills: initialData.skills || [],
        experienceLevel: initialData.experienceLevel || "",
        jobPreferences: {
          remoteOnly: initialData.jobPreferences?.remoteOnly || false,
          jobTypes: initialData.jobPreferences?.jobTypes || ["full-time"],
          desiredSalary: initialData.jobPreferences?.desiredSalary || "",
          desiredLocations: initialData.jobPreferences?.desiredLocations || [],
        },
        about: initialData.about || "",
      });
    }
  }, [initialData, form]);

  // Add a new skill
  const handleAddSkill = () => {
    if (!newSkill.trim()) return;

    const currentSkills = form.getValues("skills") || [];
    // Check if skill already exists (case insensitive)
    if (
      currentSkills.some(
        (skill) => skill.toLowerCase() === newSkill.trim().toLowerCase()
      )
    ) {
      // Atualizar para usar a API do Sonner
      toast.error("Habilidade já adicionada", {
        description: "Esta habilidade já está na sua lista.",
      });
      return;
    }

    form.setValue("skills", [...currentSkills, newSkill.trim()]);
    setNewSkill("");
  };

  // Remove a skill
  const handleRemoveSkill = (skillToRemove: string) => {
    const currentSkills = form.getValues("skills") || [];
    form.setValue(
      "skills",
      currentSkills.filter((skill) => skill !== skillToRemove)
    );
  };

  // Handle form submission
  const handleFormSubmit = async (data: ProfileFormValues) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      // Atualizar para usar a API do Sonner
      toast.success("Perfil atualizado", {
        description: "Suas informações foram salvas com sucesso.",
      });
    } catch (error) {
      // Atualizar para usar a API do Sonner
      toast.error("Erro ao salvar", {
        description:
          "Ocorreu um erro ao atualizar seu perfil. Tente novamente.",
      });
      console.error("Error saving profile:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Perfil Profissional</CardTitle>
        <CardDescription>
          Atualize suas informações profissionais para melhorar a
          correspondência com vagas
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleFormSubmit)}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Título Profissional</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Ex: Desenvolvedor Full-Stack"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      O título que melhor descreve sua função atual ou desejada
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="location"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Localização</FormLabel>
                    <FormControl>
                      <Input placeholder="Ex: São Paulo, SP" {...field} />
                    </FormControl>
                    <FormDescription>Sua cidade e estado atual</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="skills"
              render={() => (
                <FormItem>
                  <FormLabel>Habilidades</FormLabel>
                  <div className="flex space-x-2">
                    <Input
                      placeholder="Adicione uma habilidade"
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddSkill();
                        }
                      }}
                    />
                    <Button type="button" onClick={handleAddSkill} size="icon">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {form.getValues("skills")?.map((skill) => (
                      <Badge
                        key={skill}
                        variant="secondary"
                        className="flex items-center gap-1"
                      >
                        {skill}
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <button
                                type="button"
                                onClick={() => handleRemoveSkill(skill)}
                                className="ml-1 text-muted-foreground hover:text-destructive transition-colors"
                              >
                                <Trash className="h-3 w-3" />
                              </button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Remover habilidade</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </Badge>
                    ))}
                  </div>
                  <FormDescription>
                    Adicione suas habilidades técnicas e pessoais
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="experienceLevel"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nível de Experiência</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    value={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione seu nível de experiência" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {experienceLevels.map((level) => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Seu nível de experiência profissional
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="border p-4 rounded-md space-y-4">
              <h3 className="text-md font-medium">Preferências de Trabalho</h3>

              <FormField
                control={form.control}
                name="jobPreferences.jobTypes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tipos de Trabalho</FormLabel>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {jobTypes.map((type) => (
                        <div
                          key={type.value}
                          className="flex items-center space-x-2"
                        >
                          <input
                            type="checkbox"
                            id={`job-type-${type.value}`}
                            checked={field.value?.includes(type.value)}
                            onChange={(e) => {
                              const updatedTypes = e.target.checked
                                ? [...(field.value || []), type.value]
                                : field.value?.filter(
                                    (t) => t !== type.value
                                  ) || [];
                              field.onChange(updatedTypes);
                            }}
                            className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                          />
                          <label
                            htmlFor={`job-type-${type.value}`}
                            className="text-sm"
                          >
                            {type.label}
                          </label>
                        </div>
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="jobPreferences.desiredSalary"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Pretensão Salarial (opcional)</FormLabel>
                    <FormControl>
                      <Input placeholder="Ex: R$ 5.000 - R$ 7.000" {...field} />
                    </FormControl>
                    <FormDescription>
                      Informe sua expectativa salarial mensal
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="jobPreferences.remoteOnly"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <input
                        type="checkbox"
                        checked={field.value}
                        onChange={field.onChange}
                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Apenas Trabalho Remoto</FormLabel>
                      <FormDescription>
                        Marque esta opção se você está procurando apenas
                        oportunidades remotas
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="about"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Sobre Você (opcional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Compartilhe um pouco sobre sua trajetória profissional, objetivos e interesses..."
                      className="resize-none min-h-[120px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Uma breve descrição sobre você e seus objetivos
                    profissionais
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <CardFooter className="px-0 pt-4">
              <Button
                type="submit"
                disabled={isSubmitting || isLoading}
                className="w-full md:w-auto"
              >
                {isSubmitting || isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Salvando...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Salvar Perfil
                  </>
                )}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default ProfileForm;
