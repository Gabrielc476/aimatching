import React, { useState } from "react";
import JobList, { JobFiltersState } from "@/components/organisms/jobs/JobList";
import JobFilters from "@/components/organisms/jobs/JobFilters";
import SearchBar from "@/components/molecules/forms/SearchBar";
import Breadcrumbs from "@/components/molecules/navigation/Breadcrumbs";
import TabGroup from "@/components/molecules/navigation/TabGroup";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string[];
  skills: string[];
  salaryRange?: string;
  jobType: string;
  experienceLevel: string;
  postedAt: Date;
  matchScore?: number;
  url: string;
  isActive: boolean;
}

// Interface para o tipo JobCardProps que inclui linkedinId
interface JobCardProps extends Omit<Job, "postedAt"> {
  linkedinId: string;
  postedAt: string; // JobCard espera string, não Date
}

interface JobsTemplateProps {
  jobs: Job[];
  totalJobs: number;
  isLoading: boolean;
  hasNextPage: boolean;
  onLoadMore: () => void;
  onSearch: (searchTerm: string) => void;
  onFilterChange: (filters: JobFiltersState) => void;
}

/**
 * Jobs template for displaying and filtering job listings
 */
export const JobsTemplate: React.FC<JobsTemplateProps> = ({
  jobs,
  totalJobs,
  isLoading,
  hasNextPage,
  onLoadMore,
  onSearch,
  onFilterChange,
}) => {
  const [activeTab, setActiveTab] = useState<string>("all");
  const [filters, setFilters] = useState<JobFiltersState>({
    jobType: [],
    experienceLevel: [],
    locations: [], // Alterado para locations conforme JobFiltersState
    skills: [],
    postedWithin: "any",
    salaryMin: 0,
    salaryMax: 25000, // Valor padrão
  });

  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Jobs", href: "/jobs" },
  ];

  // Definição para TabGroup conforme a interface TabItem esperada
  const tabItems = [
    { value: "all", content: "All Jobs" },
    { value: "matches", content: "Matched Jobs" },
    { value: "saved", content: "Saved Jobs" },
  ];

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  const handleApplyFilters = (newFilters: JobFiltersState) => {
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleCancelFilters = () => {
    // Função necessária para a interface do JobFilters
    // Não é necessário alterar o estado de visibilidade aqui
  };

  const handleSearch = (searchTerm: string) => {
    onSearch(searchTerm);
  };

  // Converte objetos Job para JobCardProps
  const jobsWithLinkedinId: JobCardProps[] = jobs.map((job) => ({
    ...job,
    linkedinId: `linkedin-${job.id}`, // Gera um ID de LinkedIn fictício
    postedAt: job.postedAt.toISOString(), // Converte Date para string
  }));

  return (
    <div className="flex flex-col gap-6 w-full">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Job Listings</h1>
        <Breadcrumbs items={breadcrumbItems} />
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="lg:w-1/4">
          {/* Componente de filtros usando as props corretas */}
          <JobFilters
            initialFilters={filters}
            onApply={handleApplyFilters}
            onCancel={handleCancelFilters}
          />
        </div>

        <div className="flex-1">
          <div className="mb-6">
            <SearchBar
              placeholder="Search jobs by title, company, or keywords..."
              onSearch={handleSearch}
            />
          </div>

          <div className="mb-6">
            {/* TabGroup modificado para usar as props esperadas */}
            <TabGroup
              items={tabItems}
              value={activeTab}
              onValueChange={handleTabChange}
            />
          </div>

          <div className="mb-4 flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              Showing {jobs.length} of {totalJobs} jobs
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Sort By: Relevance
              </Button>
            </div>
          </div>

          <Separator className="mb-6" />

          {/* JobList com o formato de dados correto e props esperadas */}
          <JobList
            jobs={jobsWithLinkedinId}
            isLoading={isLoading}
            totalJobs={totalJobs}
            showMatchScore={true}
            error={null}
            onSearch={handleSearch}
            onFilter={onFilterChange}
            initialFilters={filters}
          />

          {hasNextPage && (
            <div className="mt-6 flex justify-center">
              <Button
                onClick={onLoadMore}
                variant="outline"
                disabled={isLoading}
              >
                {isLoading ? "Loading..." : "Load More Jobs"}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobsTemplate;
