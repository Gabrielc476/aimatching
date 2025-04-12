import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Breadcrumbs from "@/components/molecules/navigation/Breadcrumbs";
import StatCard from "@/components/molecules/cards/StatCard";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { SkillBadge } from "@/components/atoms/badges/SkillBadge";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  ArrowUpRight,
  TrendingUp,
  BarChart3,
  PieChart as PieChartIcon,
  Download,
} from "lucide-react";

interface SkillGap {
  skill: string;
  demandScore: number;
  proficiencyScore: number;
  gapScore: number;
}

interface JobMatchTrend {
  date: string;
  matchCount: number;
  averageScore: number;
}

interface MatchDistribution {
  range: string;
  count: number;
  percentage: number;
}

interface TopSkill {
  skill: string;
  occurrences: number;
  percentage: number;
}

interface AnalyticsTemplateProps {
  skillGaps: SkillGap[];
  matchTrends: JobMatchTrend[];
  matchDistribution: MatchDistribution[];
  topSkillsMarket: TopSkill[];
  topSkillsMatched: TopSkill[];
  resumeStrengths: string[];
  resumeWeaknesses: string[];
  improvementSuggestions: Array<{
    id: string;
    title: string;
    description: string;
    impact: "high" | "medium" | "low";
  }>;
  onExportData: () => void;
}

/**
 * Analytics template for displaying insights and job market analytics
 */
export const AnalyticsTemplate: React.FC<AnalyticsTemplateProps> = ({
  skillGaps,
  matchTrends,
  matchDistribution,
  topSkillsMarket,
  topSkillsMatched,
  resumeStrengths,
  resumeWeaknesses,
  improvementSuggestions,
  onExportData,
}) => {
  const [activeTab, setActiveTab] = useState<string>("insights");

  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Analytics", href: "/analytics" },
  ];

  // Calculate analytics overview stats
  const totalMatches = matchTrends.reduce(
    (sum, item) => sum + item.matchCount,
    0
  );
  const averageScore =
    matchTrends.length > 0
      ? matchTrends.reduce((sum, item) => sum + item.averageScore, 0) /
        matchTrends.length
      : 0;
  const topGapSkill =
    skillGaps.length > 0
      ? [...skillGaps].sort((a, b) => b.gapScore - a.gapScore)[0]
      : null;

  // Colors for charts
  const COLORS = [
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
    "#A28CFF",
    "#FF6B6B",
  ];

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Analytics & Insights
          </h1>
          <Breadcrumbs items={breadcrumbItems} />
        </div>
        <Button onClick={onExportData} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export Report
        </Button>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Job Matches"
          value={totalMatches}
          icon={<BarChart3 className="h-4 w-4" />}
          description="Last 30 days"
          trend={{
            value: 12,
            isPositive: true,
          }}
        />

        <StatCard
          title="Average Match Score"
          value={`${Math.round(averageScore)}%`}
          icon={<PieChartIcon className="h-4 w-4" />}
          description="Based on your profile"
          trend={{
            value: 5,
            isPositive: true,
          }}
        />

        <StatCard
          title="Top Skill Gap"
          value={topGapSkill?.skill || "N/A"}
          icon={<TrendingUp className="h-4 w-4" />}
          description="High demand in market"
        />

        <StatCard
          title="Improvement Potential"
          value={`${Math.min(100, Math.round(averageScore + 20))}%`}
          icon={<ArrowUpRight className="h-4 w-4" />}
          description="After addressing gaps"
          trend={{
            value: 20,
            isPositive: true,
          }}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="insights">Profile Insights</TabsTrigger>
          <TabsTrigger value="market">Market Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="insights" className="mt-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Skill Gap Analysis</CardTitle>
                <CardDescription>
                  Compare your skills with job market demand
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={skillGaps}
                      layout="vertical"
                      margin={{ top: 20, right: 30, left: 30, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="skill" type="category" width={100} />
                      <Tooltip />
                      <Legend />
                      <Bar
                        dataKey="demandScore"
                        name="Market Demand"
                        fill="#0088FE"
                      />
                      <Bar
                        dataKey="proficiencyScore"
                        name="Your Proficiency"
                        fill="#00C49F"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Match Score Distribution</CardTitle>
                <CardDescription>
                  Distribution of your job match scores
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={matchDistribution}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) =>
                          `${name} (${(percent * 100).toFixed(0)}%)`
                        }
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="percentage"
                        nameKey="range"
                      >
                        {matchDistribution.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) =>
                          `${(Number(value) * 100).toFixed(1)}%`
                        }
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Resume Strengths & Weaknesses</CardTitle>
                <CardDescription>
                  Analysis of your current resume
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <h3 className="font-medium mb-3">Strengths</h3>
                    <ul className="space-y-2">
                      {resumeStrengths.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-500 mr-2">✓</span>
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-medium mb-3">Areas for Improvement</h3>
                    <ul className="space-y-2">
                      {resumeWeaknesses.map((weakness, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-amber-500 mr-2">!</span>
                          <span>{weakness}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Improvement Suggestions</CardTitle>
                <CardDescription>
                  Actionable recommendations to improve your job matches
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {improvementSuggestions.map((suggestion) => (
                    <div key={suggestion.id} className="border rounded-md p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium">{suggestion.title}</h3>
                        <Badge impact={suggestion.impact} className="ml-auto" />
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {suggestion.description}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="market" className="mt-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Job Match Trends</CardTitle>
                <CardDescription>
                  Match count and average score over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={matchTrends}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis
                        yAxisId="right"
                        orientation="right"
                        domain={[0, 100]}
                      />
                      <Tooltip />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="matchCount"
                        name="Match Count"
                        stroke="#0088FE"
                        activeDot={{ r: 8 }}
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="averageScore"
                        name="Avg. Score (%)"
                        stroke="#00C49F"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Skills in Market</CardTitle>
                <CardDescription>
                  Most demanded skills in your industry
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={topSkillsMarket}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="skill" />
                      <YAxis />
                      <Tooltip />
                      <Bar
                        dataKey="occurrences"
                        name="Occurrences"
                        fill="#8884d8"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <Separator className="my-4" />

                <div className="flex flex-wrap gap-2 mt-4">
                  {topSkillsMarket.map((skill) => (
                    <SkillBadge key={skill.skill} skill={skill.skill} />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Your Matched Skills</CardTitle>
                <CardDescription>
                  Skills from your profile that match job requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={topSkillsMatched}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="skill" />
                      <YAxis />
                      <Tooltip />
                      <Bar
                        dataKey="occurrences"
                        name="Occurrences"
                        fill="#82ca9d"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <Separator className="my-4" />

                <div className="flex flex-wrap gap-2 mt-4">
                  {topSkillsMatched.map((skill) => (
                    <SkillBadge key={skill.skill} skill={skill.skill} />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Helper component for impact badges
interface BadgeProps {
  impact: "high" | "medium" | "low";
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ impact, className }) => {
  const getImpactColor = () => {
    switch (impact) {
      case "high":
        return "bg-red-100 text-red-800";
      case "medium":
        return "bg-amber-100 text-amber-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <span
      className={`text-xs px-2 py-1 rounded-full ${getImpactColor()} ${className}`}
    >
      {impact.charAt(0).toUpperCase() + impact.slice(1)} Impact
    </span>
  );
};

export default AnalyticsTemplate;
