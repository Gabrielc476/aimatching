// frontend/components/organisms/matching/MatchScore.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Award,
  BarChart,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Download,
  GraduationCap,
  Info,
  Languages,
  MapPin,
  ScanSearch,
  Settings,
  Share2,
  Sparkles,
} from "lucide-react";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export interface MatchScoreData {
  overall: number;
  breakdown: {
    skills: {
      score: number;
      matched: string[];
      missing: string[];
      overqualified: string[];
    };
    experience: {
      score: number;
      years: number;
      relevantExperience: boolean;
      seniorityMatch: number;
    };
    education: {
      score: number;
      degreeMatch: boolean;
      fieldMatch: boolean;
    };
    location: {
      score: number;
      distance?: number;
      remoteMatch?: boolean;
    };
    industry: {
      score: number;
      relevance: number;
    };
    jobType: {
      score: number;
      preference: string;
    };
  };
  resume: {
    id: string;
    name: string;
    lastUpdated: string;
  };
  job: {
    id: string;
    title: string;
    company: string;
    location: string;
    matchDate: string;
  };
  recommendations: {
    strengths: string[];
    improvements: string[];
    actions: string[];
  };
}

export interface MatchScoreProps {
  data: MatchScoreData;
  onUpdateResume?: () => void;
  onShareMatch?: () => void;
  onDownloadReport?: () => void;
}

const MatchScore = ({
  data,
  onUpdateResume,
  onShareMatch,
  onDownloadReport,
}: MatchScoreProps) => {
  const [showDetails, setShowDetails] = useState(false);
  const [activeTab, setActiveTab] = useState("breakdown");

  const getScoreColor = (score: number): string => {
    if (score >= 90) return "text-green-600";
    if (score >= 80) return "text-emerald-600";
    if (score >= 70) return "text-blue-600";
    if (score >= 60) return "text-amber-600";
    return "text-red-600";
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 90) return "Excelente";
    if (score >= 80) return "Muito Bom";
    if (score >= 70) return "Bom";
    if (score >= 60) return "Razoável";
    return "Baixo";
  };

  const getProgressColor = (score: number): string => {
    if (score >= 90) return "bg-green-600";
    if (score >= 80) return "bg-emerald-600";
    if (score >= 70) return "bg-blue-600";
    if (score >= 60) return "bg-amber-600";
    return "bg-red-600";
  };

  const sortedBreakdown = Object.entries(data.breakdown)
    .map(([key, value]) => ({ key, score: value.score }))
    .sort((a, b) => b.score - a.score);

  const getBreakdownIcon = (key: string) => {
    switch (key) {
      case "skills":
        return <Sparkles className="h-4 w-4 mr-2" />;
      case "experience":
        return <Award className="h-4 w-4 mr-2" />;
      case "education":
        return <GraduationCap className="h-4 w-4 mr-2" />;
      case "location":
        return <MapPin className="h-4 w-4 mr-2" />;
      case "industry":
        return <BookOpen className="h-4 w-4 mr-2" />;
      case "jobType":
        return <Settings className="h-4 w-4 mr-2" />;
      default:
        return <Info className="h-4 w-4 mr-2" />;
    }
  };

  const getBreakdownLabel = (key: string): string => {
    switch (key) {
      case "skills":
        return "Habilidades";
      case "experience":
        return "Experiência";
      case "education":
        return "Educação";
      case "location":
        return "Localização";
      case "industry":
        return "Indústria";
      case "jobType":
        return "Tipo de Vaga";
      default:
        return key;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-0">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Análise de Compatibilidade</CardTitle>
            <CardDescription>
              Análise detalhada da compatibilidade entre seu currículo e a vaga
            </CardDescription>
          </div>
          <div className="flex space-x-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="icon" onClick={onShareMatch}>
                    <Share2 className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Compartilhar análise</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={onDownloadReport}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Baixar relatório</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-6 pb-2">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          <div className="md:w-1/4 flex flex-col items-center justify-center pb-4 md:pb-0 md:border-r">
            <div className="text-6xl font-bold mb-2 flex items-center">
              <span className={getScoreColor(data.overall)}>
                {data.overall}%
              </span>
            </div>
            <div className="text-lg font-medium">
              {getScoreLabel(data.overall)}
            </div>
            <div className="text-sm text-muted-foreground">
              Compatibilidade Geral
            </div>
          </div>

          <div className="md:w-3/4 space-y-4">
            <div className="flex flex-col space-y-1">
              <div className="flex justify-between text-sm">
                <div className="text-muted-foreground">Vaga</div>
                <div className="font-medium">
                  {data.job.title} - {data.job.company}
                </div>
              </div>
              <div className="flex justify-between text-sm">
                <div className="text-muted-foreground">Currículo</div>
                <div className="font-medium">{data.resume.name}</div>
              </div>
              <div className="flex justify-between text-sm">
                <div className="text-muted-foreground">Analisado em</div>
                <div>{new Date(data.job.matchDate).toLocaleDateString()}</div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="font-medium flex items-center">
                  {getBreakdownIcon("skills")}
                  Habilidades
                </span>
                <span className={getScoreColor(data.breakdown.skills.score)}>
                  {data.breakdown.skills.score}%
                </span>
              </div>
              <Progress
                value={data.breakdown.skills.score}
                className="h-2"
                indicatorClassName={getProgressColor(
                  data.breakdown.skills.score
                )}
              />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="font-medium flex items-center">
                  {getBreakdownIcon("experience")}
                  Experiência
                </span>
                <span
                  className={getScoreColor(data.breakdown.experience.score)}
                >
                  {data.breakdown.experience.score}%
                </span>
              </div>
              <Progress
                value={data.breakdown.experience.score}
                className="h-2"
                indicatorClassName={getProgressColor(
                  data.breakdown.experience.score
                )}
              />
            </div>

            <Button
              variant="ghost"
              className="w-full mt-2 text-sm flex items-center justify-center"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Esconder detalhes
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  Ver análise detalhada
                </>
              )}
            </Button>
          </div>
        </div>

        {showDetails && (
          <>
            <Separator className="my-6" />

            <Tabs
              defaultValue="breakdown"
              value={activeTab}
              onValueChange={setActiveTab}
            >
              <TabsList className="grid grid-cols-3 mb-4">
                <TabsTrigger value="breakdown" className="text-sm">
                  <BarChart className="h-4 w-4 mr-2" />
                  <span>Detalhamento</span>
                </TabsTrigger>
                <TabsTrigger value="strengths" className="text-sm">
                  <ScanSearch className="h-4 w-4 mr-2" />
                  <span>Análise</span>
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="text-sm">
                  <Languages className="h-4 w-4 mr-2" />
                  <span>Recomendações</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="breakdown" className="space-y-6 pt-2">
                <div className="space-y-4">
                  {sortedBreakdown.map(({ key, score }) => (
                    <div key={key} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium flex items-center">
                          {getBreakdownIcon(key)}
                          {getBreakdownLabel(key)}
                        </span>
                        <span className={getScoreColor(score)}>{score}%</span>
                      </div>
                      <Progress
                        value={score}
                        className="h-2"
                        indicatorClassName={getProgressColor(score)}
                      />

                      {key === "skills" && (
                        <div className="p-3 bg-muted/50 rounded-md text-sm mt-1">
                          <div className="font-medium mb-2">
                            Compatibilidade de Habilidades
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            <div>
                              <div className="text-xs font-medium text-green-600 mb-1">
                                Pontos Fortes (
                                {data.breakdown.skills.matched.length})
                              </div>
                              <ul className="space-y-1 pl-4 list-disc text-xs">
                                {data.breakdown.skills.matched.map(
                                  (skill, index) => (
                                    <li key={index}>{skill}</li>
                                  )
                                )}
                                {data.breakdown.skills.matched.length === 0 && (
                                  <li className="text-muted-foreground">
                                    Nenhuma habilidade correspondente
                                  </li>
                                )}
                              </ul>
                            </div>
                            <div>
                              <div className="text-xs font-medium text-red-600 mb-1">
                                Lacunas ({data.breakdown.skills.missing.length})
                              </div>
                              <ul className="space-y-1 pl-4 list-disc text-xs">
                                {data.breakdown.skills.missing.map(
                                  (skill, index) => (
                                    <li key={index}>{skill}</li>
                                  )
                                )}
                                {data.breakdown.skills.missing.length === 0 && (
                                  <li className="text-muted-foreground">
                                    Nenhuma lacuna de habilidade
                                  </li>
                                )}
                              </ul>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="strengths" className="space-y-4 pt-2">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-muted/50 rounded-md">
                    <h4 className="font-medium mb-2 flex items-center text-green-600">
                      <Award className="h-4 w-4 mr-2" />
                      Pontos Fortes
                    </h4>
                    <ul className="space-y-2 pl-4 list-disc text-sm">
                      {data.recommendations.strengths.map((strength, index) => (
                        <li key={index}>{strength}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 bg-muted/50 rounded-md">
                    <h4 className="font-medium mb-2 flex items-center text-amber-600">
                      <Info className="h-4 w-4 mr-2" />
                      Áreas para Melhorar
                    </h4>
                    <ul className="space-y-2 pl-4 list-disc text-sm">
                      {data.recommendations.improvements.map(
                        (improvement, index) => (
                          <li key={index}>{improvement}</li>
                        )
                      )}
                    </ul>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4 pt-2">
                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-medium mb-2 flex items-center">
                    <Settings className="h-4 w-4 mr-2" />
                    Ações Recomendadas
                  </h4>
                  <ul className="space-y-2 pl-4 list-disc text-sm">
                    {data.recommendations.actions.map((action, index) => (
                      <li key={index}>{action}</li>
                    ))}
                  </ul>
                </div>

                <div className="mt-2 flex justify-center">
                  <Button onClick={onUpdateResume}>
                    Atualizar meu currículo
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
          </>
        )}
      </CardContent>

      <CardFooter className="pt-4 text-xs text-muted-foreground">
        <p>
          Esta análise é baseada na comparação entre seu currículo e os
          requisitos da vaga, utilizando tecnologia de inteligência artificial.
        </p>
      </CardFooter>
    </Card>
  );
};

export default MatchScore;
