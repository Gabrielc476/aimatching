// frontend/components/organisms/matching/MatchDetails.tsx
import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertTriangle,
  Award,
  BookOpen,
  Building,
  CheckCircle2,
  Clock,
  Code,
  Download,
  ExternalLink,
  FileText,
  GraduationCap,
  HelpCircle,
  MapPin,
  MessageSquare,
  PanelRight,
  Share2,
  ShieldCheck,
  Sparkles,
  Star,
  XCircle,
} from "lucide-react";

import { MatchScoreIndicator } from "@/components/atoms/indicators/MatchScoreIndicator";
import { SkillBadge } from "@/components/atoms/badges/SkillBadge";

interface SkillMatch {
  name: string;
  status: "matched" | "missing" | "overqualified";
}

interface EducationMatch {
  degree: {
    required: string;
    yours: string;
    match: boolean;
  };
  field: {
    required: string;
    yours: string;
    match: boolean;
  };
}

interface ExperienceMatch {
  years: {
    required: number;
    yours: number;
    match: boolean;
  };
  relevance: {
    score: number;
    match: boolean;
  };
  seniority: {
    required: string;
    yours: string;
    match: boolean;
  };
}

export interface MatchDetailsProps {
  job: {
    id: string;
    title: string;
    company: string;
    location: string;
    description: string;
    requirements: string[];
    skills: string[];
    jobType: string;
    experienceLevel: string;
    educationLevel?: string;
    educationField?: string;
    postedAt: string;
    salaryRange?: string;
    benefits?: string[];
    url: string;
  };
  resume: {
    id: string;
    name: string;
    lastUpdated: string;
  };
  match: {
    overall: number;
    skillsMatch: {
      score: number;
      details: SkillMatch[];
    };
    educationMatch?: {
      score: number;
      details: EducationMatch;
    };
    experienceMatch: {
      score: number;
      details: ExperienceMatch;
    };
    locationMatch: {
      score: number;
      remote: boolean;
      distance?: number;
    };
  };
  recommendations: {
    strengths: string[];
    improvements: string[];
    applicationTips: string[];
    interviewPrep: string[];
  };
  onApply: () => void;
  onSave: () => void;
  onShare: () => void;
  onDownloadReport: () => void;
  onViewSource: () => void;
  isSaved: boolean;
  isApplied: boolean;
}

const MatchDetails = ({
  job,
  resume,
  match,
  recommendations,
  onApply,
  onSave,
  onShare,
  onDownloadReport,
  onViewSource,
  isSaved,
  isApplied,
}: MatchDetailsProps) => {
  const [activeTab, setActiveTab] = useState("overview");

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "matched":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "missing":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "overqualified":
        return <ShieldCheck className="h-4 w-4 text-blue-500" />;
      default:
        return <HelpCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "matched":
        return "Você tem esta habilidade";
      case "missing":
        return "Habilidade não encontrada em seu currículo";
      case "overqualified":
        return "Você excede os requisitos para esta habilidade";
      default:
        return "Status desconhecido";
    }
  };

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return new Date(dateString).toLocaleDateString("pt-BR", options);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main content */}
        <div className="flex-1">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl">{job.title}</CardTitle>
                  <div className="flex items-center mt-1">
                    <Building className="h-4 w-4 mr-1 text-muted-foreground" />
                    <span className="text-lg">{job.company}</span>
                  </div>
                </div>
                <MatchScoreIndicator score={match.overall} size="lg" />
              </div>
            </CardHeader>
            <CardContent className="pb-0">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <div className="flex flex-col">
                  <span className="text-sm text-muted-foreground">
                    Localização
                  </span>
                  <div className="flex items-center mt-1">
                    <MapPin className="h-4 w-4 mr-1 text-muted-foreground" />
                    <span className="font-medium">{job.location}</span>
                  </div>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm text-muted-foreground">
                    Tipo de Vaga
                  </span>
                  <div className="flex items-center mt-1">
                    <Clock className="h-4 w-4 mr-1 text-muted-foreground" />
                    <span className="font-medium">{job.jobType}</span>
                  </div>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm text-muted-foreground">Nível</span>
                  <div className="flex items-center mt-1">
                    <Award className="h-4 w-4 mr-1 text-muted-foreground" />
                    <span className="font-medium">{job.experienceLevel}</span>
                  </div>
                </div>
                {job.educationLevel && (
                  <div className="flex flex-col">
                    <span className="text-sm text-muted-foreground">
                      Educação
                    </span>
                    <div className="flex items-center mt-1">
                      <GraduationCap className="h-4 w-4 mr-1 text-muted-foreground" />
                      <span className="font-medium">{job.educationLevel}</span>
                    </div>
                  </div>
                )}
                <div className="flex flex-col">
                  <span className="text-sm text-muted-foreground">
                    Publicado em
                  </span>
                  <div className="flex items-center mt-1">
                    <FileText className="h-4 w-4 mr-1 text-muted-foreground" />
                    <span>{formatDate(job.postedAt)}</span>
                  </div>
                </div>
                {job.salaryRange && (
                  <div className="flex flex-col">
                    <span className="text-sm text-muted-foreground">
                      Faixa Salarial
                    </span>
                    <div className="flex items-center mt-1">
                      <span className="font-medium">{job.salaryRange}</span>
                    </div>
                  </div>
                )}
              </div>

              <Tabs
                defaultValue="overview"
                value={activeTab}
                onValueChange={setActiveTab}
              >
                <TabsList className="grid grid-cols-4">
                  <TabsTrigger value="overview">Visão Geral</TabsTrigger>
                  <TabsTrigger value="match">Compatibilidade</TabsTrigger>
                  <TabsTrigger value="recommendations">
                    Recomendações
                  </TabsTrigger>
                  <TabsTrigger value="apply">Candidatura</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4 py-4">
                  <div>
                    <h3 className="text-lg font-medium mb-2">
                      Descrição da Vaga
                    </h3>
                    <p className="text-muted-foreground whitespace-pre-line">
                      {job.description}
                    </p>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-medium mb-2">Requisitos</h3>
                    <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                      {job.requirements.map((req, index) => (
                        <li key={index}>{req}</li>
                      ))}
                    </ul>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-medium mb-2">
                      Habilidades Necessárias
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {job.skills.map((skill) => (
                        <SkillBadge key={skill} skill={skill} />
                      ))}
                    </div>
                  </div>

                  {job.benefits && job.benefits.length > 0 && (
                    <>
                      <Separator />
                      <div>
                        <h3 className="text-lg font-medium mb-2">Benefícios</h3>
                        <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                          {job.benefits.map((benefit, index) => (
                            <li key={index}>{benefit}</li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}
                </TabsContent>

                <TabsContent value="match" className="space-y-6 py-4">
                  {/* Skills Match */}
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-lg font-medium flex items-center">
                        <Sparkles className="h-5 w-5 mr-2 text-amber-500" />
                        Habilidades
                      </h3>
                      <Badge
                        className={
                          match.skillsMatch.score >= 70
                            ? "bg-green-500"
                            : "bg-amber-500"
                        }
                      >
                        {match.skillsMatch.score}% de compatibilidade
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {match.skillsMatch.details.map((skill, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-md flex items-start space-x-2 ${
                            skill.status === "matched"
                              ? "bg-green-50 dark:bg-green-950/20"
                              : skill.status === "missing"
                              ? "bg-red-50 dark:bg-red-950/20"
                              : "bg-blue-50 dark:bg-blue-950/20"
                          }`}
                        >
                          {getStatusIcon(skill.status)}
                          <div className="flex-1">
                            <div className="font-medium text-sm">
                              {skill.name}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {getStatusText(skill.status)}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Experience Match */}
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-lg font-medium flex items-center">
                        <Award className="h-5 w-5 mr-2 text-blue-500" />
                        Experiência
                      </h3>
                      <Badge
                        className={
                          match.experienceMatch.score >= 70
                            ? "bg-green-500"
                            : "bg-amber-500"
                        }
                      >
                        {match.experienceMatch.score}% de compatibilidade
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div className="p-3 bg-muted/50 rounded-md">
                        <div className="text-sm font-medium mb-1">
                          Anos de Experiência
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">
                            Requisito:
                          </span>
                          <span className="text-sm font-medium">
                            {match.experienceMatch.details.years.required}{" "}
                            ano(s)
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">
                            Você tem:
                          </span>
                          <span className="text-sm font-medium">
                            {match.experienceMatch.details.years.yours} ano(s)
                          </span>
                        </div>
                        <div className="mt-2 flex items-center">
                          {match.experienceMatch.details.years.match ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-amber-500 mr-1" />
                          )}
                          <span className="text-xs">
                            {match.experienceMatch.details.years.match
                              ? "Você atende ao requisito"
                              : match.experienceMatch.details.years.yours >
                                match.experienceMatch.details.years.required
                              ? "Você excede o requisito"
                              : "Abaixo do requisito"}
                          </span>
                        </div>
                      </div>

                      <div className="p-3 bg-muted/50 rounded-md">
                        <div className="text-sm font-medium mb-1">
                          Relevância
                        </div>
                        <div className="text-sm text-muted-foreground mb-2">
                          Quão relevante é sua experiência para esta vaga
                        </div>
                        <div className="flex items-center">
                          <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                match.experienceMatch.details.relevance.match
                                  ? "bg-green-500"
                                  : "bg-amber-500"
                              }`}
                              style={{
                                width: `${match.experienceMatch.details.relevance.score}%`,
                              }}
                            ></div>
                          </div>
                          <span className="ml-2 text-sm font-medium">
                            {match.experienceMatch.details.relevance.score}%
                          </span>
                        </div>
                      </div>

                      <div className="p-3 bg-muted/50 rounded-md">
                        <div className="text-sm font-medium mb-1">
                          Senioridade
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">
                            Requisito:
                          </span>
                          <span className="text-sm font-medium">
                            {match.experienceMatch.details.seniority.required}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">
                            Você tem:
                          </span>
                          <span className="text-sm font-medium">
                            {match.experienceMatch.details.seniority.yours}
                          </span>
                        </div>
                        <div className="mt-2 flex items-center">
                          {match.experienceMatch.details.seniority.match ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-amber-500 mr-1" />
                          )}
                          <span className="text-xs">
                            {match.experienceMatch.details.seniority.match
                              ? "Compatível com o requisito"
                              : "Diferente do requisito"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {match.educationMatch && (
                    <>
                      <Separator />

                      {/* Education Match */}
                      <div>
                        <div className="flex justify-between items-center mb-3">
                          <h3 className="text-lg font-medium flex items-center">
                            <GraduationCap className="h-5 w-5 mr-2 text-purple-500" />
                            Educação
                          </h3>
                          <Badge
                            className={
                              match.educationMatch.score >= 70
                                ? "bg-green-500"
                                : "bg-amber-500"
                            }
                          >
                            {match.educationMatch.score}% de compatibilidade
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="p-3 bg-muted/50 rounded-md">
                            <div className="text-sm font-medium mb-1">
                              Grau Acadêmico
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">
                                Requisito:
                              </span>
                              <span className="text-sm font-medium">
                                {match.educationMatch.details.degree.required}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">
                                Você tem:
                              </span>
                              <span className="text-sm font-medium">
                                {match.educationMatch.details.degree.yours}
                              </span>
                            </div>
                            <div className="mt-2 flex items-center">
                              {match.educationMatch.details.degree.match ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                              ) : (
                                <AlertTriangle className="h-4 w-4 text-amber-500 mr-1" />
                              )}
                              <span className="text-xs">
                                {match.educationMatch.details.degree.match
                                  ? "Você atende ao requisito"
                                  : "Diferente do requisito"}
                              </span>
                            </div>
                          </div>

                          <div className="p-3 bg-muted/50 rounded-md">
                            <div className="text-sm font-medium mb-1">
                              Área de Formação
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">
                                Requisito:
                              </span>
                              <span className="text-sm font-medium">
                                {match.educationMatch.details.field.required}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">
                                Você tem:
                              </span>
                              <span className="text-sm font-medium">
                                {match.educationMatch.details.field.yours}
                              </span>
                            </div>
                            <div className="mt-2 flex items-center">
                              {match.educationMatch.details.field.match ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                              ) : (
                                <AlertTriangle className="h-4 w-4 text-amber-500 mr-1" />
                              )}
                              <span className="text-xs">
                                {match.educationMatch.details.field.match
                                  ? "Área compatível"
                                  : "Área diferente"}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  )}

                  <Separator />

                  {/* Location Match */}
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-lg font-medium flex items-center">
                        <MapPin className="h-5 w-5 mr-2 text-green-500" />
                        Localização
                      </h3>
                      <Badge
                        className={
                          match.locationMatch.score >= 70
                            ? "bg-green-500"
                            : "bg-amber-500"
                        }
                      >
                        {match.locationMatch.score}% de compatibilidade
                      </Badge>
                    </div>

                    <div className="p-3 bg-muted/50 rounded-md">
                      {match.locationMatch.remote ? (
                        <div className="flex items-center">
                          <CheckCircle2 className="h-5 w-5 text-green-500 mr-2" />
                          <div>
                            <div className="font-medium">Trabalho Remoto</div>
                            <div className="text-sm text-muted-foreground">
                              Esta vaga permite trabalho remoto, compatível com
                              suas preferências.
                            </div>
                          </div>
                        </div>
                      ) : match.locationMatch.distance !== undefined ? (
                        <div>
                          <div className="font-medium">
                            Distância: {match.locationMatch.distance} km
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {match.locationMatch.distance <= 20
                              ? "Ótimo! A vaga está próxima da sua localização."
                              : match.locationMatch.distance <= 50
                              ? "A vaga está a uma distância razoável da sua localização."
                              : "A vaga está distante da sua localização."}
                          </div>
                        </div>
                      ) : (
                        <div className="text-muted-foreground">
                          Informações de localização não disponíveis.
                        </div>
                      )}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="recommendations" className="space-y-6 py-4">
                  <div>
                    <h3 className="text-lg font-medium flex items-center mb-3">
                      <Star className="h-5 w-5 mr-2 text-amber-500" />
                      Pontos Fortes
                    </h3>
                    <ul className="list-disc pl-5 space-y-2">
                      {recommendations.strengths.map((strength, index) => (
                        <li key={index} className="text-muted-foreground">
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-medium flex items-center mb-3">
                      <BookOpen className="h-5 w-5 mr-2 text-blue-500" />
                      Áreas para Melhorar
                    </h3>
                    <ul className="list-disc pl-5 space-y-2">
                      {recommendations.improvements.map(
                        (improvement, index) => (
                          <li key={index} className="text-muted-foreground">
                            {improvement}
                          </li>
                        )
                      )}
                    </ul>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-medium flex items-center mb-3">
                      <FileText className="h-5 w-5 mr-2 text-green-500" />
                      Dicas para Candidatura
                    </h3>
                    <ul className="list-disc pl-5 space-y-2">
                      {recommendations.applicationTips.map((tip, index) => (
                        <li key={index} className="text-muted-foreground">
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-medium flex items-center mb-3">
                      <MessageSquare className="h-5 w-5 mr-2 text-purple-500" />
                      Preparação para Entrevista
                    </h3>
                    <ul className="list-disc pl-5 space-y-2">
                      {recommendations.interviewPrep.map((prep, index) => (
                        <li key={index} className="text-muted-foreground">
                          {prep}
                        </li>
                      ))}
                    </ul>
                  </div>
                </TabsContent>

                <TabsContent value="apply" className="space-y-6 py-4">
                  <div className="p-4 bg-muted/50 rounded-md">
                    <h3 className="text-lg font-medium mb-2">
                      Resumo da Candidatura
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Vaga
                        </div>
                        <div className="font-medium">{job.title}</div>
                        <div className="text-sm">{job.company}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Currículo
                        </div>
                        <div className="font-medium">{resume.name}</div>
                        <div className="text-sm">
                          Atualizado em: {formatDate(resume.lastUpdated)}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center mb-4">
                      <div className="text-sm text-muted-foreground mr-2">
                        Compatibilidade:
                      </div>
                      <Badge
                        className={
                          match.overall >= 70 ? "bg-green-500" : "bg-amber-500"
                        }
                      >
                        {match.overall}%
                      </Badge>

                      <div className="text-sm ml-4">
                        {match.overall >= 90
                          ? "Compatibilidade excelente!"
                          : match.overall >= 70
                          ? "Boa compatibilidade."
                          : "Compatibilidade moderada."}
                      </div>
                    </div>

                    {match.overall < 70 && (
                      <div className="flex items-start p-3 bg-amber-50 dark:bg-amber-950/20 rounded-md mb-4 text-sm">
                        <AlertTriangle className="h-5 w-5 text-amber-500 mr-2 shrink-0 mt-0.5" />
                        <div>
                          <div className="font-medium text-amber-700 dark:text-amber-300">
                            Compatibilidade Moderada
                          </div>
                          <p className="mt-1">
                            Sua compatibilidade com esta vaga é moderada.
                            Considere revisar as recomendações antes de se
                            candidatar.
                          </p>
                        </div>
                      </div>
                    )}

                    <div className="text-sm text-muted-foreground mb-4">
                      Ao se candidatar, o sistema enviará seu currículo e uma
                      carta de apresentação personalizada, destacando seus
                      pontos fortes para esta vaga.
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={onApply}
                        disabled={isApplied}
                        className="flex-1 sm:flex-none"
                      >
                        {isApplied ? "Candidatura Enviada" : "Candidatar-me"}
                      </Button>

                      <Button
                        variant="outline"
                        onClick={onSave}
                        className={isSaved ? "text-amber-500" : ""}
                      >
                        {isSaved ? (
                          <>
                            <CheckCircle2 className="mr-2 h-4 w-4" />
                            Vaga Salva
                          </>
                        ) : (
                          <>
                            <Star className="mr-2 h-4 w-4" />
                            Salvar Vaga
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  <div className="text-sm text-muted-foreground mt-2">
                    Currículo utilizado para esta análise:{" "}
                    <span className="font-medium">{resume.name}</span>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>

            <CardFooter className="flex justify-between pt-4">
              <div className="flex space-x-2">
                <Button variant="outline" size="sm" onClick={onShare}>
                  <Share2 className="mr-2 h-4 w-4" />
                  Compartilhar
                </Button>
                <Button variant="outline" size="sm" onClick={onDownloadReport}>
                  <Download className="mr-2 h-4 w-4" />
                  Relatório
                </Button>
              </div>

              <Button variant="outline" size="sm" onClick={onViewSource}>
                <ExternalLink className="mr-2 h-4 w-4" />
                Ver no LinkedIn
              </Button>
            </CardFooter>
          </Card>
        </div>

        {/* Match sidebar - visible on large screens only */}
        <div className="lg:w-80 hidden lg:block">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>Compatibilidade</CardTitle>
              <CardDescription>
                Análise de compatibilidade com seu perfil
              </CardDescription>
            </CardHeader>
            <CardContent className="pb-0">
              <div className="flex flex-col items-center mb-6">
                <div className="text-5xl font-bold mb-2 text-center">
                  <span
                    className={
                      match.overall >= 70 ? "text-green-600" : "text-amber-600"
                    }
                  >
                    {match.overall}%
                  </span>
                </div>
                <div className="text-center text-sm font-medium">
                  {match.overall >= 90
                    ? "Compatibilidade Excelente"
                    : match.overall >= 80
                    ? "Compatibilidade Muito Boa"
                    : match.overall >= 70
                    ? "Boa Compatibilidade"
                    : match.overall >= 60
                    ? "Compatibilidade Razoável"
                    : "Compatibilidade Baixa"}
                </div>
              </div>

              <Separator className="mb-4" />

              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <div className="font-medium flex items-center">
                      <Code className="h-4 w-4 mr-1 text-blue-500" />
                      Habilidades
                    </div>
                    <div
                      className={
                        match.skillsMatch.score >= 70
                          ? "text-green-600"
                          : "text-amber-600"
                      }
                    >
                      {match.skillsMatch.score}%
                    </div>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        match.skillsMatch.score >= 70
                          ? "bg-green-600"
                          : "bg-amber-600"
                      }`}
                      style={{ width: `${match.skillsMatch.score}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <div className="font-medium flex items-center">
                      <Award className="h-4 w-4 mr-1 text-purple-500" />
                      Experiência
                    </div>
                    <div
                      className={
                        match.experienceMatch.score >= 70
                          ? "text-green-600"
                          : "text-amber-600"
                      }
                    >
                      {match.experienceMatch.score}%
                    </div>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        match.experienceMatch.score >= 70
                          ? "bg-green-600"
                          : "bg-amber-600"
                      }`}
                      style={{ width: `${match.experienceMatch.score}%` }}
                    ></div>
                  </div>
                </div>

                {match.educationMatch && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <div className="font-medium flex items-center">
                        <GraduationCap className="h-4 w-4 mr-1 text-amber-500" />
                        Educação
                      </div>
                      <div
                        className={
                          match.educationMatch.score >= 70
                            ? "text-green-600"
                            : "text-amber-600"
                        }
                      >
                        {match.educationMatch.score}%
                      </div>
                    </div>
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          match.educationMatch.score >= 70
                            ? "bg-green-600"
                            : "bg-amber-600"
                        }`}
                        style={{ width: `${match.educationMatch.score}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <div className="font-medium flex items-center">
                      <MapPin className="h-4 w-4 mr-1 text-green-500" />
                      Localização
                    </div>
                    <div
                      className={
                        match.locationMatch.score >= 70
                          ? "text-green-600"
                          : "text-amber-600"
                      }
                    >
                      {match.locationMatch.score}%
                    </div>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        match.locationMatch.score >= 70
                          ? "bg-green-600"
                          : "bg-amber-600"
                      }`}
                      style={{ width: `${match.locationMatch.score}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <Separator className="my-4" />

              <div className="space-y-3">
                <h4 className="text-sm font-medium">Pontos Fortes</h4>
                <ScrollArea className="h-32 rounded-md border p-3">
                  <ul className="space-y-2 text-sm">
                    {recommendations.strengths.map((strength, index) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle2 className="h-4 w-4 text-green-500 mr-2 mt-0.5 shrink-0" />
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </ScrollArea>
              </div>

              <Separator className="my-4" />

              <div>
                <h4 className="text-sm font-medium mb-3">
                  Áreas para Melhorar
                </h4>
                <ScrollArea className="h-32 rounded-md border p-3">
                  <ul className="space-y-2 text-sm">
                    {recommendations.improvements.map((improvement, index) => (
                      <li key={index} className="flex items-start">
                        <PanelRight className="h-4 w-4 text-amber-500 mr-2 mt-0.5 shrink-0" />
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </ScrollArea>
              </div>
            </CardContent>

            <CardFooter className="flex-col space-y-2 pt-6">
              <Button className="w-full" onClick={onApply} disabled={isApplied}>
                {isApplied ? "Candidatura Enviada" : "Candidatar-me"}
              </Button>

              <Button variant="outline" className="w-full" onClick={onSave}>
                {isSaved ? "Vaga Salva" : "Salvar Vaga"}
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MatchDetails;
