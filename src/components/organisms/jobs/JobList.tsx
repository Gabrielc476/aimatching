// frontend/components/organisms/jobs/JobList.tsx
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Filter, XCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";

import JobCard, { JobCardProps } from "./JobCard";
import JobFilters from "./JobFilters";
import { LoadingPlaceholder } from "@/components/atoms/feedback/LoadingPlaceholder";

export interface JobListProps {
  jobs: JobCardProps[];
  isLoading?: boolean;
  error?: string | null;
  onSearch?: (term: string) => void;
  onFilter?: (filters: JobFiltersState) => void;
  onSaveJob?: (id: string) => void;
  initialFilters?: JobFiltersState;
  totalJobs?: number;
  showMatchScore?: boolean;
}

export interface JobFiltersState {
  jobType?: string[];
  experienceLevel?: string[];
  locations?: string[];
  skills?: string[];
  postedWithin?: string;
  salaryMin?: number;
  salaryMax?: number;
}

const JobList = ({
  jobs,
  isLoading = false,
  error = null,
  onSearch,
  onFilter,
  onSaveJob,
  initialFilters,
  totalJobs,
  showMatchScore = false,
}: JobListProps) => {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<JobFiltersState>(
    initialFilters || {}
  );
  const [activeFilterCount, setActiveFilterCount] = useState(0);

  useEffect(() => {
    // Calculate number of active filters
    const count = Object.entries(activeFilters).reduce(
      (count, [key, value]) => {
        if (Array.isArray(value)) {
          return count + (value.length > 0 ? 1 : 0);
        }
        return count + (value ? 1 : 0);
      },
      0
    );

    setActiveFilterCount(count);
  }, [activeFilters]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchTerm);
    }
  };

  const handleApplyFilters = (filters: JobFiltersState) => {
    setActiveFilters(filters);
    setShowFilters(false);
    if (onFilter) {
      onFilter(filters);
    }
  };

  const handleClearFilters = () => {
    setActiveFilters({});
    if (onFilter) {
      onFilter({});
    }
  };

  const handleViewDetails = (id: string) => {
    router.push(`/jobs/${id}`);
  };

  return (
    <div className="w-full space-y-6">
      <div className="space-y-3">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Pesquisar vagas por título, empresa ou habilidade"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button type="submit">Buscar</Button>
          <Button
            type="button"
            variant={showFilters ? "default" : "outline"}
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-1"
          >
            <Filter className="h-4 w-4" />
            Filtros
            {activeFilterCount > 0 && (
              <span className="ml-1 rounded-full bg-primary-foreground px-2 py-0.5 text-xs text-primary">
                {activeFilterCount}
              </span>
            )}
          </Button>
        </form>

        {showFilters && (
          <div className="bg-card rounded-md border p-4">
            <JobFilters
              initialFilters={activeFilters}
              onApply={handleApplyFilters}
              onCancel={() => setShowFilters(false)}
            />
          </div>
        )}

        {activeFilterCount > 0 && (
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground">
              Filtros ativos
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearFilters}
              className="ml-2 flex items-center"
            >
              <XCircle className="h-4 w-4 mr-1" />
              Limpar todos
            </Button>
          </div>
        )}

        {totalJobs !== undefined && (
          <div className="text-sm text-muted-foreground">
            {totalJobs} vagas encontradas
          </div>
        )}
      </div>

      <Separator />

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <LoadingPlaceholder key={i} height="h-52" />
          ))}
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : jobs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h3 className="text-lg font-medium">Nenhuma vaga encontrada</h3>
          <p className="text-muted-foreground mt-1">
            Tente ajustar seus filtros ou termos de busca
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              {...job}
              onSaveJob={onSaveJob}
              onViewDetails={handleViewDetails}
              matchScore={showMatchScore ? job.matchScore : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default JobList;
