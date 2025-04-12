// frontend/components/organisms/jobs/JobFilters.tsx
import { useState, useEffect } from "react";
import { Briefcase, Award, MapPin, Tag, Clock, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { JobFiltersState } from "./JobList";

interface JobFiltersProps {
  initialFilters?: JobFiltersState;
  onApply: (filters: JobFiltersState) => void;
  onCancel: () => void;
  availableFilters?: {
    jobTypes?: string[];
    experienceLevels?: string[];
    locations?: string[];
    skills?: string[];
  };
}

// Constants for filter options
const DEFAULT_JOB_TYPES = [
  "Tempo integral",
  "Meio período",
  "Freelance",
  "Estágio",
  "Temporário",
  "Remoto",
];
const DEFAULT_EXPERIENCE_LEVELS = [
  "Estágio",
  "Júnior",
  "Pleno",
  "Sênior",
  "Diretor",
  "Executivo",
];
const DEFAULT_LOCATIONS = [
  "São Paulo",
  "Rio de Janeiro",
  "Belo Horizonte",
  "Brasília",
  "Porto Alegre",
  "Remoto",
];
const DEFAULT_SKILLS = [
  "JavaScript",
  "Python",
  "React",
  "Node.js",
  "TypeScript",
  "SQL",
  "Java",
  "C#",
  "AWS",
  "Product Management",
  "Agile",
  "UI/UX",
  "Marketing",
  "Sales",
  "Data Analysis",
  "Excel",
];
const POSTED_WITHIN_OPTIONS = [
  { value: "1d", label: "Último dia" },
  { value: "1w", label: "Última semana" },
  { value: "2w", label: "Últimas 2 semanas" },
  { value: "1m", label: "Último mês" },
  { value: "3m", label: "Últimos 3 meses" },
  { value: "any", label: "Qualquer período" },
];

const JobFilters = ({
  initialFilters = {},
  onApply,
  onCancel,
  availableFilters,
}: JobFiltersProps) => {
  const [filters, setFilters] = useState<JobFiltersState>(initialFilters);
  const [salaryRange, setSalaryRange] = useState<[number, number]>([
    initialFilters.salaryMin || 0,
    initialFilters.salaryMax || 25000,
  ]);

  // Use provided filter options or defaults
  const jobTypes = availableFilters?.jobTypes || DEFAULT_JOB_TYPES;
  const experienceLevels =
    availableFilters?.experienceLevels || DEFAULT_EXPERIENCE_LEVELS;
  const locations = availableFilters?.locations || DEFAULT_LOCATIONS;
  const skills = availableFilters?.skills || DEFAULT_SKILLS;

  useEffect(() => {
    // Format salary filter values into the filters state
    setFilters((prevFilters) => ({
      ...prevFilters,
      salaryMin: salaryRange[0],
      salaryMax: salaryRange[1],
    }));
  }, [salaryRange]);

  const handleToggleFilter = (category: string, value: string) => {
    setFilters((prevFilters) => {
      const currentValues = prevFilters[category] || [];
      const newValues = currentValues.includes(value)
        ? currentValues.filter((v) => v !== value)
        : [...currentValues, value];

      return {
        ...prevFilters,
        [category]: newValues,
      };
    });
  };

  const handlePostedWithinChange = (value: string) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      postedWithin: value,
    }));
  };

  const handleResetFilters = () => {
    setFilters({});
    setSalaryRange([0, 25000]);
  };

  const handleApplyFilters = () => {
    // Remove empty arrays or undefined values
    const cleanedFilters = Object.entries(filters).reduce(
      (acc, [key, value]) => {
        if (Array.isArray(value) && value.length === 0) {
          return acc;
        }
        if (value === undefined) {
          return acc;
        }
        return { ...acc, [key]: value };
      },
      {}
    );

    onApply(cleanedFilters);
  };

  const isFilterSelected = (category: string, value: string): boolean => {
    return (filters[category] || []).includes(value);
  };

  const formatCurrency = (value: number): string => {
    return value.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  };

  return (
    <div className="space-y-4">
      <Accordion type="multiple" defaultValue={["jobType", "salary"]}>
        <AccordionItem value="jobType">
          <AccordionTrigger className="flex items-center">
            <div className="flex items-center">
              <Briefcase className="h-4 w-4 mr-2" />
              <span>Tipo de Vaga</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-2 gap-2">
              {jobTypes.map((type) => (
                <div key={type} className="flex items-center space-x-2">
                  <Checkbox
                    id={`job-type-${type}`}
                    checked={isFilterSelected("jobType", type)}
                    onCheckedChange={() => handleToggleFilter("jobType", type)}
                  />
                  <Label
                    htmlFor={`job-type-${type}`}
                    className="text-sm cursor-pointer"
                  >
                    {type}
                  </Label>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="experience">
          <AccordionTrigger className="flex items-center">
            <div className="flex items-center">
              <Award className="h-4 w-4 mr-2" />
              <span>Nível de Experiência</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-2 gap-2">
              {experienceLevels.map((level) => (
                <div key={level} className="flex items-center space-x-2">
                  <Checkbox
                    id={`experience-${level}`}
                    checked={isFilterSelected("experienceLevel", level)}
                    onCheckedChange={() =>
                      handleToggleFilter("experienceLevel", level)
                    }
                  />
                  <Label
                    htmlFor={`experience-${level}`}
                    className="text-sm cursor-pointer"
                  >
                    {level}
                  </Label>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="location">
          <AccordionTrigger className="flex items-center">
            <div className="flex items-center">
              <MapPin className="h-4 w-4 mr-2" />
              <span>Localização</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <ScrollArea className="h-48">
              <div className="grid grid-cols-1 gap-2 pr-4">
                {locations.map((location) => (
                  <div key={location} className="flex items-center space-x-2">
                    <Checkbox
                      id={`location-${location}`}
                      checked={isFilterSelected("locations", location)}
                      onCheckedChange={() =>
                        handleToggleFilter("locations", location)
                      }
                    />
                    <Label
                      htmlFor={`location-${location}`}
                      className="text-sm cursor-pointer"
                    >
                      {location}
                    </Label>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="skills">
          <AccordionTrigger className="flex items-center">
            <div className="flex items-center">
              <Tag className="h-4 w-4 mr-2" />
              <span>Habilidades</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <ScrollArea className="h-48">
              <div className="grid grid-cols-2 gap-2 pr-4">
                {skills.map((skill) => (
                  <div key={skill} className="flex items-center space-x-2">
                    <Checkbox
                      id={`skill-${skill}`}
                      checked={isFilterSelected("skills", skill)}
                      onCheckedChange={() =>
                        handleToggleFilter("skills", skill)
                      }
                    />
                    <Label
                      htmlFor={`skill-${skill}`}
                      className="text-sm cursor-pointer"
                    >
                      {skill}
                    </Label>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="posted">
          <AccordionTrigger className="flex items-center">
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-2" />
              <span>Data de Publicação</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <Select
              value={filters.postedWithin || "any"}
              onValueChange={handlePostedWithinChange}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione um período" />
              </SelectTrigger>
              <SelectContent>
                {POSTED_WITHIN_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="salary">
          <AccordionTrigger className="flex items-center">
            <div className="flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              <span>Faixa Salarial</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 px-1">
              <Slider
                defaultValue={salaryRange}
                min={0}
                max={25000}
                step={500}
                value={salaryRange}
                onValueChange={(value) => {
                  setSalaryRange([value[0], value[1]]);
                }}
                className="my-6"
              />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{formatCurrency(salaryRange[0])}</span>
                <span>{formatCurrency(salaryRange[1])}</span>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <Separator />

      <div className="flex justify-between">
        <div>
          <Button variant="outline" size="sm" onClick={handleResetFilters}>
            Resetar
          </Button>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={onCancel}>
            Cancelar
          </Button>
          <Button size="sm" onClick={handleApplyFilters}>
            Aplicar Filtros
          </Button>
        </div>
      </div>
    </div>
  );
};

export default JobFilters;
