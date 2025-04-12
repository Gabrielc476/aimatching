// frontend/components/organisms/dashboard/RecentMatches.tsx
import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ArrowRight,
  Check,
  Clock,
  Clock3,
  Filter,
  Loader2,
  MapPin,
  Star,
  StarOff,
  Building,
  BarChart,
} from "lucide-react";

import { MatchScoreIndicator } from "@/components/atoms/indicators/MatchScoreIndicator";
import { TimeAgo } from "@/components/atoms/display/TimeAgo";
const getStatusBadge = (status: string) => {
  switch (status) {
    case "new":
      return (
        <Badge variant="default" className="bg-blue-500">
          Nova
        </Badge>
      );
    case "viewed":
      return (
        <Badge variant="outline" className="text-muted-foreground">
          Visualizada
        </Badge>
      );
    case "applied":
      return (
        <Badge variant="default" className="bg-green-500">
          Aplicada
        </Badge>
      );
    default:
      return null;
  }
};

export interface JobMatch {
  id: string;
  title: string;
  company: string;
  location: string;
  jobType: string;
  matchScore: number;
  matchDetails?: {
    skillsMatch: number;
    experienceMatch: number;
    educationMatch: number;
    locationMatch: number;
  };
  postedAt: string;
  savedAt?: string;
  status: "new" | "viewed" | "applied" | "saved";
  salaryRange?: string;
  skills: string[];
}

export interface RecentMatchesProps {
  matches: JobMatch[];
  isLoading?: boolean;
  onViewMatch?: (id: string) => void;
  onSaveMatch?: (id: string) => void;
  onApplyMatch?: (id: string) => void;
  onViewAllMatches?: () => void;
}

const RecentMatches = ({
  matches,
  isLoading = false,
  onViewMatch,
  onSaveMatch,
  onApplyMatch,
  onViewAllMatches,
}: RecentMatchesProps) => {
  const [activeTab, setActiveTab] = useState("all");
  const [savedJobs, setSavedJobs] = useState<string[]>(
    matches.filter((match) => match.status === "saved").map((match) => match.id)
  );

  const handleToggleSave = (id: string) => {
    const isSaved = savedJobs.includes(id);

    if (isSaved) {
      setSavedJobs((prev) => prev.filter((jobId) => jobId !== id));
    } else {
      setSavedJobs((prev) => [...prev, id]);
    }

    if (onSaveMatch) {
      onSaveMatch(id);
    }
  };

  const handleViewMatch = (id: string) => {
    if (onViewMatch) {
      onViewMatch(id);
    }
  };

  const handleApplyMatch = (id: string) => {
    if (onApplyMatch) {
      onApplyMatch(id);
    }
  };

  const filteredMatches = matches.filter((match) => {
    if (activeTab === "all") return true;
    if (activeTab === "new") return match.status === "new";
    if (activeTab === "saved") return savedJobs.includes(match.id);
    if (activeTab === "applied") return match.status === "applied";
    return true;
  });

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-2 sm:space-y-0">
          <div>
            <CardTitle className="text-lg">Correspondências Recentes</CardTitle>
            <CardDescription>
              Vagas que correspondem ao seu perfil e currículo
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={onViewAllMatches}>
            <Filter className="mr-2 h-4 w-4" />
            Filtrar
          </Button>
        </div>
      </CardHeader>
      <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
        <div className="px-6">
          <TabsList className="w-full">
            <TabsTrigger value="all" className="flex-1">
              Todas
            </TabsTrigger>
            <TabsTrigger value="new" className="flex-1">
              Novas
              {matches.filter((m) => m.status === "new").length > 0 && (
                <Badge variant="default" className="ml-2 bg-blue-500">
                  {matches.filter((m) => m.status === "new").length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="saved" className="flex-1">
              Salvas
            </TabsTrigger>
            <TabsTrigger value="applied" className="flex-1">
              Aplicadas
            </TabsTrigger>
          </TabsList>
        </div>

        <CardContent className="pt-6">
          <TabsContent value="all" className="m-0">
            <MatchesList
              matches={filteredMatches}
              isLoading={isLoading}
              savedJobs={savedJobs}
              onToggleSave={handleToggleSave}
              onViewMatch={handleViewMatch}
              onApplyMatch={handleApplyMatch}
            />
          </TabsContent>

          <TabsContent value="new" className="m-0">
            <MatchesList
              matches={filteredMatches}
              isLoading={isLoading}
              savedJobs={savedJobs}
              onToggleSave={handleToggleSave}
              onViewMatch={handleViewMatch}
              onApplyMatch={handleApplyMatch}
            />
          </TabsContent>

          <TabsContent value="saved" className="m-0">
            <MatchesList
              matches={filteredMatches}
              isLoading={isLoading}
              savedJobs={savedJobs}
              onToggleSave={handleToggleSave}
              onViewMatch={handleViewMatch}
              onApplyMatch={handleApplyMatch}
            />
          </TabsContent>

          <TabsContent value="applied" className="m-0">
            <MatchesList
              matches={filteredMatches}
              isLoading={isLoading}
              savedJobs={savedJobs}
              onToggleSave={handleToggleSave}
              onViewMatch={handleViewMatch}
              onApplyMatch={handleApplyMatch}
            />
          </TabsContent>
        </CardContent>
      </Tabs>

      <CardFooter className="flex justify-between">
        <div className="text-sm text-muted-foreground">
          Mostrando {filteredMatches.length} de {matches.length} vagas
        </div>
        <Button variant="link" onClick={onViewAllMatches}>
          Ver todas as correspondências
          <ArrowRight className="ml-1 h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
};

interface MatchesListProps {
  matches: JobMatch[];
  isLoading: boolean;
  savedJobs: string[];
  onToggleSave: (id: string) => void;
  onViewMatch: (id: string) => void;
  onApplyMatch: (id: string) => void;
}

const MatchesList = ({
  matches,
  isLoading,
  savedJobs,
  onToggleSave,
  onViewMatch,
  onApplyMatch,
}: MatchesListProps) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-sm text-muted-foreground">
          Carregando correspondências...
        </p>
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-center">
        <Clock3 className="h-12 w-12 text-muted-foreground opacity-20" />
        <h3 className="mt-4 text-lg font-medium">
          Nenhuma correspondência encontrada
        </h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-md">
          Não encontramos correspondências nesta categoria. Complete seu perfil
          ou verifique os filtros.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {matches.map((match) => (
        <div
          key={match.id}
          className="rounded-lg border p-4 transition-all hover:bg-accent/50"
        >
          <div className="flex justify-between">
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h3
                    className="font-medium text-lg hover:text-primary cursor-pointer transition-colors"
                    onClick={() => onViewMatch(match.id)}
                  >
                    {match.title}
                  </h3>
                  <div className="flex items-center text-muted-foreground mt-1">
                    <Building className="h-3.5 w-3.5 mr-1" />
                    <span className="text-sm">{match.company}</span>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  {getStatusBadge(match.status)}
                  <MatchScoreIndicator score={match.matchScore} />
                </div>
              </div>

              <div className="flex flex-wrap gap-4 mt-3">
                <div className="flex items-center text-sm text-muted-foreground">
                  <MapPin className="h-3.5 w-3.5 mr-1" />
                  <span>{match.location}</span>
                </div>
                <div className="flex items-center text-sm text-muted-foreground">
                  <Clock className="h-3.5 w-3.5 mr-1" />
                  <TimeAgo date={match.postedAt} />
                </div>
                <div className="flex items-center text-sm font-medium">
                  <Badge variant="outline" className="font-normal">
                    {match.jobType}
                  </Badge>
                </div>
              </div>

              {match.matchDetails && (
                <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                  <div className="flex flex-col">
                    <span className="text-xs text-muted-foreground">
                      Habilidades
                    </span>
                    <div className="flex items-center mt-1">
                      <BarChart className="h-3.5 w-3.5 mr-1 text-blue-500" />
                      <span className="text-sm font-medium">
                        {match.matchDetails.skillsMatch}%
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-muted-foreground">
                      Experiência
                    </span>
                    <div className="flex items-center mt-1">
                      <BarChart className="h-3.5 w-3.5 mr-1 text-green-500" />
                      <span className="text-sm font-medium">
                        {match.matchDetails.experienceMatch}%
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-muted-foreground">
                      Formação
                    </span>
                    <div className="flex items-center mt-1">
                      <BarChart className="h-3.5 w-3.5 mr-1 text-purple-500" />
                      <span className="text-sm font-medium">
                        {match.matchDetails.educationMatch}%
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-muted-foreground">
                      Localização
                    </span>
                    <div className="flex items-center mt-1">
                      <BarChart className="h-3.5 w-3.5 mr-1 text-amber-500" />
                      <span className="text-sm font-medium">
                        {match.matchDetails.locationMatch}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-2 mt-3">
                {match.skills.slice(0, 3).map((skill) => (
                  <Badge
                    key={skill}
                    variant="secondary"
                    className="font-normal"
                  >
                    {skill}
                  </Badge>
                ))}
                {match.skills.length > 3 && (
                  <Badge variant="outline" className="font-normal">
                    +{match.skills.length - 3} mais
                  </Badge>
                )}
              </div>
            </div>
          </div>

          <Separator className="my-3" />

          <div className="flex justify-between items-center">
            {match.salaryRange ? (
              <div className="text-sm">
                <span className="text-muted-foreground">Faixa salarial: </span>
                <span className="font-medium">{match.salaryRange}</span>
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                Salário não informado
              </div>
            )}

            <div className="flex space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onToggleSave(match.id)}
                className={savedJobs.includes(match.id) ? "text-amber-500" : ""}
              >
                {savedJobs.includes(match.id) ? (
                  <Star className="h-4 w-4" />
                ) : (
                  <StarOff className="h-4 w-4" />
                )}
              </Button>

              <Button
                variant="outline"
                size="sm"
                className="flex items-center space-x-1"
                onClick={() => onViewMatch(match.id)}
              >
                Ver detalhes
              </Button>

              <Button
                variant={match.status === "applied" ? "secondary" : "default"}
                size="sm"
                className="flex items-center space-x-1"
                onClick={() => onApplyMatch(match.id)}
                disabled={match.status === "applied"}
              >
                {match.status === "applied" ? (
                  <>
                    <Check className="mr-1 h-4 w-4" />
                    Aplicado
                  </>
                ) : (
                  "Aplicar"
                )}
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecentMatches;
