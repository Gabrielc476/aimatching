import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Breadcrumbs from "@/components/molecules/navigation/Breadcrumbs";
import TabGroup from "@/components/molecules/navigation/TabGroup";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, ArrowUpDown } from "lucide-react";

// Interface para a estrutura de dados do tipo JobMatch
interface JobMatch {
  id: string;
  jobId: string;
  resumeId: string;
  jobTitle: string;
  company: string;
  location: string;
  jobType: string;
  postedAt: Date;
  url: string;
  salary?: string;
  score: {
    overall: number;
    skills: number;
    experience: number;
    education: number;
  };
  matchDetails: {
    matchedSkills: string[];
    missingSkills: string[];
    strengthAreas: string[];
    improvementAreas: string[];
    recommendations: string[];
  };
  status: "new" | "viewed" | "applied" | "rejected" | "saved";
}

// Interface para o componente TabItem (corrigida para corresponder ao componente real)
interface TabItem {
  value: string;
  label: string;
}

// Interface para as Props do template
interface MatchesTemplateProps {
  matches: JobMatch[];
  isLoading: boolean;
  onStatusChange: (
    matchId: string,
    newStatus: JobMatch["status"]
  ) => Promise<void>;
  onSortChange: (sortField: string, direction: "asc" | "desc") => void;
  onFilterChange: (filter: string) => void;
}

/**
 * Matches template for displaying job matches and their details
 */
export const MatchesTemplate: React.FC<MatchesTemplateProps> = ({
  matches,
  isLoading,
  onStatusChange,
  onSortChange,
  onFilterChange,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<string>("all");
  const [selectedMatch, setSelectedMatch] = useState<JobMatch | null>(null);
  const [sortField, setSortField] = useState<string>("score");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Matches", href: "/matches" },
  ];

  // Adaptado para o formato correto de TabItem
  const tabItems: TabItem[] = [
    { value: "all", label: "All Matches" },
    { value: "high", label: "High Matches" },
    { value: "new", label: "New" },
    { value: "applied", label: "Applied" },
    { value: "saved", label: "Saved" },
  ];

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    onFilterChange(tabId === "all" ? "" : tabId);
  };

  const handleSort = (field: string) => {
    const newDirection =
      field === sortField && sortDirection === "desc" ? "asc" : "desc";
    setSortField(field);
    setSortDirection(newDirection);
    onSortChange(field, newDirection);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleSelectMatch = (match: JobMatch) => {
    setSelectedMatch(match);
    if (match.status === "new") {
      onStatusChange(match.id, "viewed");
    }
  };

  const filteredMatches = matches.filter((match) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        match.jobTitle.toLowerCase().includes(query) ||
        match.company.toLowerCase().includes(query) ||
        match.location.toLowerCase().includes(query)
      );
    }
    return true;
  });

  return (
    <div className="flex flex-col gap-6 w-full">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Job Matches</h1>
        <Breadcrumbs items={breadcrumbItems} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xl">Matches</CardTitle>
              <div className="mt-2 relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search matches..."
                  className="pl-8"
                  value={searchQuery}
                  onChange={handleSearch}
                />
              </div>
            </CardHeader>
            <CardContent className="px-2">
              <TabGroup
                items={tabItems}
                value={activeTab}
                onValueChange={handleTabChange}
              />

              <div className="pt-4 pb-2 px-2 flex items-center justify-between">
                <div className="flex items-center space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2"
                    onClick={() => handleSort("score")}
                  >
                    <span
                      className={sortField === "score" ? "font-medium" : ""}
                    >
                      Score
                    </span>
                    {sortField === "score" && (
                      <ArrowUpDown className="ml-1 h-3 w-3" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2"
                    onClick={() => handleSort("postedAt")}
                  >
                    <span
                      className={sortField === "postedAt" ? "font-medium" : ""}
                    >
                      Date
                    </span>
                    {sortField === "postedAt" && (
                      <ArrowUpDown className="ml-1 h-3 w-3" />
                    )}
                  </Button>
                </div>
                <span className="text-xs text-muted-foreground px-2">
                  {filteredMatches.length} matches
                </span>
              </div>

              <Separator className="mb-2" />

              {isLoading ? (
                <div className="py-8 text-center text-muted-foreground">
                  Loading matches...
                </div>
              ) : filteredMatches.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  No matches found. Try adjusting your filters or updating your
                  profile.
                </div>
              ) : (
                <div className="space-y-1 max-h-[calc(100vh-280px)] overflow-y-auto px-2 py-1">
                  {filteredMatches.map((match) => (
                    <div
                      key={match.id}
                      className={`rounded-md p-3 cursor-pointer transition-colors ${
                        selectedMatch?.id === match.id
                          ? "bg-primary/10"
                          : "hover:bg-secondary"
                      }`}
                      onClick={() => handleSelectMatch(match)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-sm truncate">
                            {match.jobTitle}
                          </h3>
                          <p className="text-xs text-muted-foreground truncate">
                            {match.company} • {match.location}
                          </p>
                        </div>
                        {/* Indicador simples de pontuação em vez do componente completo */}
                        <div className="bg-blue-100 text-blue-800 text-xs font-semibold rounded-full px-2 py-1">
                          {match.score.overall}%
                        </div>
                      </div>

                      <div className="flex mt-2 justify-between items-center">
                        <div className="flex items-center gap-1">
                          <Badge variant="outline" className="text-xs">
                            {match.jobType}
                          </Badge>
                          {match.status === "new" && (
                            <Badge className="bg-primary text-xs">New</Badge>
                          )}
                          {match.status === "applied" && (
                            <Badge className="bg-green-600 text-xs">
                              Applied
                            </Badge>
                          )}
                          {match.status === "saved" && (
                            <Badge className="bg-blue-600 text-xs">Saved</Badge>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {new Date(match.postedAt).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          {selectedMatch ? (
            <Card className="h-full p-6">
              <CardHeader>
                <CardTitle>{selectedMatch.jobTitle}</CardTitle>
                <p className="text-muted-foreground">{selectedMatch.company}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium">Match Score</p>
                      <div className="mt-1 text-2xl font-bold">
                        {selectedMatch.score.overall}%
                      </div>
                    </div>

                    <div>
                      <p className="text-sm font-medium">Status</p>
                      <div className="mt-1">
                        <Badge variant="outline">
                          {selectedMatch.status.charAt(0).toUpperCase() +
                            selectedMatch.status.slice(1)}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <p className="text-sm font-medium mb-2">Skills Match</p>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">
                        Matched Skills
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {selectedMatch.matchDetails.matchedSkills.map(
                          (skill, index) => (
                            <Badge key={index} variant="secondary">
                              {skill}
                            </Badge>
                          )
                        )}
                        {selectedMatch.matchDetails.matchedSkills.length ===
                          0 && (
                          <p className="text-sm text-muted-foreground">
                            No matched skills found
                          </p>
                        )}
                      </div>

                      <p className="text-sm text-muted-foreground mb-1">
                        Missing Skills
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {selectedMatch.matchDetails.missingSkills.map(
                          (skill, index) => (
                            <Badge key={index} variant="outline">
                              {skill}
                            </Badge>
                          )
                        )}
                        {selectedMatch.matchDetails.missingSkills.length ===
                          0 && (
                          <p className="text-sm text-muted-foreground">
                            No missing skills found
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <p className="text-sm font-medium mb-2">Actions</p>
                    <div className="flex gap-2">
                      <Button
                        onClick={() =>
                          onStatusChange(selectedMatch.id, "applied")
                        }
                        disabled={selectedMatch.status === "applied"}
                      >
                        {selectedMatch.status === "applied"
                          ? "Applied"
                          : "Apply Now"}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() =>
                          onStatusChange(
                            selectedMatch.id,
                            selectedMatch.status === "saved"
                              ? "viewed"
                              : "saved"
                          )
                        }
                      >
                        {selectedMatch.status === "saved"
                          ? "Unsave"
                          : "Save Job"}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center p-6">
              <div className="text-center">
                <h3 className="font-medium text-lg mb-2">Select a match</h3>
                <p className="text-muted-foreground">
                  Select a job match from the list to view detailed match
                  information
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default MatchesTemplate;
