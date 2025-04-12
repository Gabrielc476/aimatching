// frontend/components/organisms/dashboard/StatsOverview.tsx
import { useState } from "react";
import {
  BarChart3,
  Briefcase,
  Calendar,
  ChevronDown,
  Eye,
  FileSearch,
  Star,
  Zap,
  Info,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface Stat {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  change?: {
    value: number;
    trend: "up" | "down" | "neutral";
  };
}

interface MatchStat {
  score: number;
  title: string;
  company: string;
  id: string;
}

export interface StatsOverviewProps {
  profileCompletion: number;
  stats: {
    applicationsToday: number;
    totalApplications: number;
    viewedJobs: number;
    suggestedJobs: number;
  };
  topMatches: MatchStat[];
  period?: "today" | "week" | "month" | "all";
  onPeriodChange?: (period: "today" | "week" | "month" | "all") => void;
  onViewJob?: (id: string) => void;
}

const StatsOverview = ({
  profileCompletion,
  stats,
  topMatches,
  period = "week",
  onPeriodChange,
  onViewJob,
}: StatsOverviewProps) => {
  const [selectedPeriod, setSelectedPeriod] = useState<
    "today" | "week" | "month" | "all"
  >(period);

  const handlePeriodChange = (
    newPeriod: "today" | "week" | "month" | "all"
  ) => {
    setSelectedPeriod(newPeriod);
    if (onPeriodChange) {
      onPeriodChange(newPeriod);
    }
  };

  const periodLabels = {
    today: "Hoje",
    week: "Esta semana",
    month: "Este mês",
    all: "Todo período",
  };

  const statCards: Stat[] = [
    {
      title: "Candidaturas",
      value: stats.applicationsToday,
      description: "hoje",
      icon: <FileSearch className="h-5 w-5 text-blue-500" />,
      change: {
        value: 12,
        trend: "up",
      },
    },
    {
      title: "Total de Candidaturas",
      value: stats.totalApplications,
      description: "desde o início",
      icon: <Calendar className="h-5 w-5 text-green-500" />,
    },
    {
      title: "Vagas Visualizadas",
      value: stats.viewedJobs,
      description: `em ${periodLabels[selectedPeriod].toLowerCase()}`,
      icon: <Eye className="h-5 w-5 text-purple-500" />,
    },
    {
      title: "Vagas Sugeridas",
      value: stats.suggestedJobs,
      description: "em alta correspondência",
      icon: <Briefcase className="h-5 w-5 text-amber-500" />,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Profile Completion */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-lg">Perfil Profissional</CardTitle>
              <CardDescription>
                Complete seu perfil para melhorar suas correspondências
              </CardDescription>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex items-center justify-center rounded-full w-10 h-10 bg-primary/10">
                    <BarChart3 className="h-5 w-5 text-primary" />
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    Um perfil completo aumenta suas chances de correspondências
                    de qualidade.
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Completude do perfil</span>
              <span className="text-sm font-bold">{profileCompletion}%</span>
            </div>
            <Progress value={profileCompletion} className="h-2" />

            {profileCompletion < 100 && (
              <div className="flex justify-between items-center mt-4">
                <div className="flex items-center text-sm text-muted-foreground">
                  <Info className="h-4 w-4 mr-1" />
                  <span>
                    Complete seu perfil para melhores correspondências
                  </span>
                </div>
                <Button size="sm" variant="outline">
                  Completar Perfil
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="pb-2 flex flex-row items-start justify-between space-y-0">
              <div>
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <CardDescription>{stat.description}</CardDescription>
              </div>
              {stat.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              {stat.change && (
                <p
                  className={`text-xs ${
                    stat.change.trend === "up"
                      ? "text-green-500"
                      : stat.change.trend === "down"
                      ? "text-red-500"
                      : "text-muted-foreground"
                  } flex items-center mt-1`}
                >
                  {stat.change.trend === "up"
                    ? "↑"
                    : stat.change.trend === "down"
                    ? "↓"
                    : "–"}
                  {stat.change.value}% em relação ao período anterior
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Top Matches */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-lg">
                Melhores Correspondências
              </CardTitle>
              <CardDescription>
                Vagas com maior índice de compatibilidade com seu perfil
              </CardDescription>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center"
                >
                  {periodLabels[selectedPeriod]}
                  <ChevronDown className="ml-2 h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handlePeriodChange("today")}>
                  Hoje
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handlePeriodChange("week")}>
                  Esta semana
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handlePeriodChange("month")}>
                  Este mês
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handlePeriodChange("all")}>
                  Todo período
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topMatches.length > 0 ? (
              topMatches.map((match, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center border-b pb-3 last:border-0 last:pb-0"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        match.score >= 90
                          ? "bg-green-100 text-green-700"
                          : match.score >= 80
                          ? "bg-emerald-100 text-emerald-700"
                          : match.score >= 70
                          ? "bg-blue-100 text-blue-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {match.score}%
                    </div>
                    <div>
                      <div className="font-medium">{match.title}</div>
                      <div className="text-sm text-muted-foreground">
                        {match.company}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                          >
                            <Star className="h-4 w-4" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Salvar vaga</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>

                    <Button
                      variant="outline"
                      size="sm"
                      className="flex items-center space-x-1"
                      onClick={() => onViewJob && onViewJob(match.id)}
                    >
                      <Zap className="h-4 w-4" />
                      <span>Ver vaga</span>
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-6 text-muted-foreground">
                <Briefcase className="h-12 w-12 mx-auto mb-3 opacity-20" />
                <p>Nenhuma correspondência encontrada neste período</p>
                <p className="text-sm mt-1">
                  Complete seu perfil para melhorar suas correspondências
                </p>
                <Button className="mt-3" variant="outline" size="sm">
                  Ver todas as vagas
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StatsOverview;
