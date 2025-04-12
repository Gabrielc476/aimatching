// frontend/components/organisms/jobs/JobCard.tsx
import { useState } from "react";
import {
  Calendar,
  MapPin,
  Building,
  Clock,
  Briefcase,
  ArrowUpRight,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import { SkillBadge } from "@/components/atoms/badges/SkillBadge";
import { SalaryRange } from "@/components/atoms/display/SalaryRange";
import { TimeAgo } from "@/components/atoms/display/TimeAgo";
import { MatchScoreIndicator } from "@/components/atoms/indicators/MatchScoreIndicator";

export interface JobCardProps {
  id: string;
  linkedinId: string;
  title: string;
  company: string;
  location: string;
  description: string;
  salaryRange?: string;
  jobType: string;
  experienceLevel: string;
  skills: string[];
  url: string;
  postedAt: string;
  matchScore?: number;
  onSaveJob?: (id: string) => void;
  onViewDetails?: (id: string) => void;
  saved?: boolean;
}

const JobCard = ({
  id,
  title,
  company,
  location,
  description,
  salaryRange,
  jobType,
  experienceLevel,
  skills,

  postedAt,
  matchScore,
  onSaveJob,
  onViewDetails,
  saved = false,
}: JobCardProps) => {
  const [isSaved, setIsSaved] = useState(saved);

  const truncateDescription = (text: string, maxLength = 160) => {
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength).trim()}...`;
  };

  const handleSaveJob = () => {
    setIsSaved(!isSaved);
    if (onSaveJob) {
      onSaveJob(id);
    }
  };

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(id);
    }
  };

  return (
    <Card className="w-full hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl font-bold line-clamp-2">
              {title}
            </CardTitle>
            <div className="flex items-center mt-1 text-muted-foreground">
              <Building className="h-4 w-4 mr-1" />
              <span className="font-medium">{company}</span>
            </div>
          </div>
          {matchScore !== undefined && (
            <div className="ml-2">
              <MatchScoreIndicator score={matchScore} size="md" />
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="pb-2">
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="flex items-center text-sm text-muted-foreground">
            <MapPin className="h-4 w-4 mr-1" />
            <span>{location}</span>
          </div>
          <div className="flex items-center text-sm text-muted-foreground">
            <Clock className="h-4 w-4 mr-1" />
            <TimeAgo date={postedAt} />
          </div>
          <div className="flex items-center text-sm text-muted-foreground">
            <Briefcase className="h-4 w-4 mr-1" />
            <span>{jobType}</span>
          </div>
          <div className="flex items-center text-sm text-muted-foreground">
            <Calendar className="h-4 w-4 mr-1" />
            <span>{experienceLevel}</span>
          </div>
        </div>

        {salaryRange && (
          <div className="mb-3">
            <SalaryRange salaryText={salaryRange} />
          </div>
        )}

        <p className="text-sm text-muted-foreground mb-3">
          {truncateDescription(description)}
        </p>

        <div className="flex flex-wrap gap-2 mb-3">
          {skills.slice(0, 5).map((skill) => (
            <SkillBadge key={skill} skill={skill} />
          ))}
          {skills.length > 5 && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge variant="outline" className="cursor-help">
                    +{skills.length - 5} mais
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <div className="flex flex-col gap-1">
                    {skills.slice(5).map((skill) => (
                      <span key={skill}>{skill}</span>
                    ))}
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex justify-between pt-2">
        <Button
          variant={isSaved ? "default" : "outline"}
          size="sm"
          onClick={handleSaveJob}
        >
          {isSaved ? "Salvo" : "Salvar"}
        </Button>
        <Button
          variant="default"
          size="sm"
          className="flex items-center gap-1"
          onClick={handleViewDetails}
        >
          Ver detalhes <ArrowUpRight className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
};

export default JobCard;
