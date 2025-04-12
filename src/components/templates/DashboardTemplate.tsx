import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import StatsOverview from "@/components/organisms/dashboard/StatsOverview";
import RecentMatches from "@/components/organisms/dashboard/RecentMatches";
import Breadcrumbs from "@/components/molecules/navigation/Breadcrumbs";
import InfoCard from "@/components/molecules/cards/InfoCard";
import { TimeAgo } from "@/components/atoms/display/TimeAgo";
import { BadgeInfo, AlertTriangle, CheckCircle } from "lucide-react";

// Interface para as props do DashboardTemplate
interface DashboardTemplateProps {
  userName: string;
  lastResumeUpdate?: Date;
  profileCompletion: number;
  applicationStats: {
    applicationsToday: number;
    totalApplications: number;
    viewedJobs: number;
    suggestedJobs: number;
  };
  topJobMatches: Array<{
    id: string;
    title: string;
    company: string;
    score: number;
  }>;
  recentMatches: Array<{
    id: string;
    title: string;
    company: string;
    location: string;
    matchScore: number;
    postedAt: Date;
    status: "new" | "viewed" | "applied" | "saved";
    jobType: string;
    skills: string[];
    matchDetails?: {
      skillsMatch: number;
      experienceMatch: number;
      educationMatch: number;
      locationMatch: number;
    };
    salaryRange?: string;
  }>;
  insights: Array<{
    id: string;
    title: string;
    description: string;
    type: "default" | "destructive" | "success" | "info";
  }>;
  onViewAllMatches?: () => void;
  onViewMatch?: (id: string) => void;
  onSaveMatch?: (id: string) => void;
  onApplyMatch?: (id: string) => void;
  onPeriodChange?: (period: "today" | "week" | "month" | "all") => void;
  onViewJob?: (id: string) => void;
}

/**
 * Dashboard template - main hub for the user to view their job matching information
 * Displays statistics, recent matches, and insights for improvement
 */
export const DashboardTemplate: React.FC<DashboardTemplateProps> = ({
  lastResumeUpdate,
  profileCompletion,
  applicationStats,
  topJobMatches,
  recentMatches,
  insights,
  onViewAllMatches,
  onViewMatch,
  onSaveMatch,
  onApplyMatch,
  onPeriodChange,
  onViewJob,
}) => {
  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Dashboard", href: "/dashboard" },
  ];

  const renderInsights = () => {
    // Função para determinar ícone com base no tipo
    const getIconForType = (
      type: "default" | "destructive" | "success" | "info"
    ) => {
      switch (type) {
        case "info":
          return <BadgeInfo className="h-5 w-5 text-blue-500" />;
        case "destructive":
          return <AlertTriangle className="h-5 w-5 text-red-500" />;
        case "success":
          return <CheckCircle className="h-5 w-5 text-green-500" />;
        default:
          return null;
      }
    };

    return (
      <div className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold">Insights & Tips</h2>
        {insights.map((insight) => (
          <InfoCard
            key={insight.id}
            title={insight.title}
            description={insight.description}
            type={insight.type}
            icon={getIconForType(insight.type)}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <Breadcrumbs items={breadcrumbItems} />
        </div>

        {lastResumeUpdate && (
          <div className="text-sm text-muted-foreground">
            Resume last updated <TimeAgo date={lastResumeUpdate} />
          </div>
        )}
      </div>

      <StatsOverview
        profileCompletion={profileCompletion}
        stats={applicationStats}
        topMatches={topJobMatches}
        period="week"
        onPeriodChange={onPeriodChange}
        onViewJob={onViewJob}
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="col-span-2">
          <Tabs defaultValue="recent" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="recent">Recent Matches</TabsTrigger>
              <TabsTrigger value="high">High Matches</TabsTrigger>
            </TabsList>
            <TabsContent value="recent" className="space-y-4">
              <RecentMatches
                matches={recentMatches.map((match) => ({
                  ...match,
                  postedAt: match.postedAt.toISOString(),
                }))}
                onViewAllMatches={onViewAllMatches}
                onViewMatch={onViewMatch}
                onSaveMatch={onSaveMatch}
                onApplyMatch={onApplyMatch}
              />
            </TabsContent>
            <TabsContent value="high" className="space-y-4">
              <RecentMatches
                matches={recentMatches
                  .filter((match) => match.matchScore >= 80)
                  .map((match) => ({
                    ...match,
                    postedAt: match.postedAt.toISOString(),
                  }))}
                onViewAllMatches={onViewAllMatches}
                onViewMatch={onViewMatch}
                onSaveMatch={onSaveMatch}
                onApplyMatch={onApplyMatch}
              />
            </TabsContent>
          </Tabs>
        </Card>

        <div className="flex flex-col gap-4">
          <h2 className="text-xl font-semibold">Insights & Tips</h2>
          {renderInsights()}
        </div>
      </div>
    </div>
  );
};

export default DashboardTemplate;
