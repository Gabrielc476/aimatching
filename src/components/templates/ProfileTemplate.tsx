import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import ProfileForm from "@/components/organisms/profile/ProfileForm";
import ResumeUploader from "@/components/organisms/profile/ResumeUploader";
import Breadcrumbs from "@/components/molecules/navigation/Breadcrumbs";
import InfoCard from "@/components/molecules/cards/InfoCard";
import { SkillBadge } from "@/components/atoms/badges/SkillBadge";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle } from "lucide-react";

interface ProfileData {
  id: string;
  name: string;
  email: string;
  title: string;
  location: string;
  skills: string[];
  experienceLevel: string;
  jobPreferences: {
    jobTypes: string[];
    locations: string[];
    industries: string[];
    minSalary: number;
  };
}

// Interface esperada pelo ProfileForm
interface ProfileFormValues {
  title: string;
  location: string;
  skills: string[];
  experienceLevel: string;
  jobPreferences: {
    remoteOnly: boolean;
    jobTypes: string[];
    desiredSalary?: string;
    desiredLocations?: string[];
  };
  about?: string;
}

interface Resume {
  id: string;
  filename: string;
  uploadedAt: Date;
  isPrimary: boolean;
  parsedContent?: {
    skills: string[];
    experience: Array<{
      company: string;
      title: string;
      startDate: string;
      endDate: string | null;
      description: string;
    }>;
    education: Array<{
      institution: string;
      degree: string;
      field: string;
      startDate: string;
      endDate: string | null;
    }>;
  };
}

// Interface para as informações de upload de currículo
interface ResumeInfo {
  id: string;
  filename: string;
  uploadedAt: string;
  isAnalyzed: boolean;
  isPrimary: boolean;
}

interface ProfileTemplateProps {
  profile: ProfileData;
  resumes: Resume[];
  onProfileUpdate: (profileData: ProfileData) => Promise<void>;
  onResumeUpload: (file: File) => Promise<void>;
  onResumeDelete: (resumeId: string) => Promise<void>;
  onResumeSetPrimary: (resumeId: string) => Promise<void>;
  profileCompletionPercentage: number;
}

/**
 * Profile template for managing user profile and resume data
 */
export const ProfileTemplate: React.FC<ProfileTemplateProps> = ({
  profile,
  resumes,
  onProfileUpdate,
  onResumeUpload,
  onResumeDelete,
  onResumeSetPrimary,
  profileCompletionPercentage,
}) => {
  const [activeTab, setActiveTab] = useState<string>("profile");
  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Profile", href: "/profile" },
  ];

  const primaryResume = resumes.find((resume) => resume.isPrimary);
  const hasIncompleteProfile = profileCompletionPercentage < 100;

  // Converter ProfileData para o formato esperado pelo ProfileForm
  const adaptProfileToFormData = (
    profileData: ProfileData
  ): Partial<ProfileFormValues> => {
    return {
      title: profileData.title,
      location: profileData.location,
      skills: profileData.skills,
      experienceLevel: profileData.experienceLevel,
      jobPreferences: {
        remoteOnly: profileData.jobPreferences.locations.includes("Remote"),
        jobTypes: profileData.jobPreferences.jobTypes,
        desiredSalary: profileData.jobPreferences.minSalary.toString(),
        desiredLocations: profileData.jobPreferences.locations.filter(
          (loc) => loc !== "Remote"
        ),
      },
      about: "", // Campo opcional não presente no ProfileData
    };
  };

  // Converter do formato do ProfileForm de volta para ProfileData
  const handleProfileUpdate = async (formData: ProfileFormValues) => {
    // Preservar os campos que não estão no formulário
    const updatedProfile: ProfileData = {
      ...profile,
      title: formData.title,
      location: formData.location,
      skills: formData.skills,
      experienceLevel: formData.experienceLevel,
      jobPreferences: {
        ...profile.jobPreferences,
        jobTypes: formData.jobPreferences.jobTypes,
        locations: [
          ...(formData.jobPreferences.desiredLocations || []),
          ...(formData.jobPreferences.remoteOnly ? ["Remote"] : []),
        ],
        minSalary: formData.jobPreferences.desiredSalary
          ? parseInt(formData.jobPreferences.desiredSalary, 10)
          : profile.jobPreferences.minSalary,
      },
    };

    await onProfileUpdate(updatedProfile);
  };

  // Adaptação para o ResumeUploader que espera uma estrutura diferente
  const handleUploadComplete = (resumeInfo: ResumeInfo) => {
    console.log("Currículo enviado com sucesso:", resumeInfo);
    // Aqui você pode fazer algo com as informações do currículo, como atualizar a lista
  };

  // Tratamento de erro de upload
  const handleUploadError = (error: string) => {
    console.error("Erro ao enviar currículo:", error);
    // Aqui você pode mostrar uma mensagem de erro ou fazer outra ação
  };

  // Lista de currículos no formato esperado pelo ResumeUploader
  const formattedResumes = resumes.map((resume) => ({
    id: resume.id,
    filename: resume.filename,
    uploadedAt: resume.uploadedAt.toISOString(),
    isAnalyzed: true, // Assumindo que todos os currículos na lista já foram analisados
    isPrimary: resume.isPrimary,
  }));

  return (
    <div className="flex flex-col gap-6 w-full">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Your Profile</h1>
        <Breadcrumbs items={breadcrumbItems} />
      </div>

      {hasIncompleteProfile && (
        <Alert className="bg-amber-50 border-amber-200">
          <AlertCircle className="h-4 w-4 text-amber-600" />
          <AlertTitle>Complete your profile</AlertTitle>
          <AlertDescription>
            Your profile is {profileCompletionPercentage}% complete. Complete
            your profile to improve job matches.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="resumes">Resumes</TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProfileForm
                    initialData={adaptProfileToFormData(profile)}
                    onSubmit={handleProfileUpdate}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="resumes" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Manage Resumes</CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Use the ResumeUploader with appropriate props */}
                  <ResumeUploader
                    uploadUrl="/api/resume/upload" // URL para o endpoint de upload
                    onUploadComplete={handleUploadComplete}
                    onUploadError={handleUploadError}
                    existingResumes={formattedResumes}
                    maxFileSize={5 * 1024 * 1024} // 5MB
                  />

                  <div className="mt-8">
                    <h3 className="text-lg font-medium mb-4">Your Resumes</h3>

                    {resumes.length === 0 ? (
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>No resumes uploaded</AlertTitle>
                        <AlertDescription>
                          Upload a resume to start getting matched with jobs.
                        </AlertDescription>
                      </Alert>
                    ) : (
                      <div className="space-y-4">
                        {resumes.map((resume) => (
                          <div
                            key={resume.id}
                            className="border rounded-md p-4 flex justify-between items-center"
                          >
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium">
                                  {resume.filename}
                                </span>
                                {resume.isPrimary && (
                                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center">
                                    <CheckCircle className="h-3 w-3 mr-1" />
                                    Primary
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground mt-1">
                                Uploaded on{" "}
                                {resume.uploadedAt.toLocaleDateString()}
                              </p>
                            </div>

                            <div className="flex gap-2">
                              {!resume.isPrimary && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => onResumeSetPrimary(resume.id)}
                                >
                                  Set as Primary
                                </Button>
                              )}
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => onResumeDelete(resume.id)}
                              >
                                Delete
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Completion</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                <div
                  className="bg-primary h-2.5 rounded-full"
                  style={{ width: `${profileCompletionPercentage}%` }}
                />
              </div>
              <p className="text-sm text-muted-foreground">
                {profileCompletionPercentage}% complete
              </p>

              {hasIncompleteProfile && (
                <div className="mt-4 space-y-2">
                  <p className="text-sm font-medium">Next steps:</p>
                  <ul className="text-sm space-y-1">
                    {!profile.title && <li>• Add your professional title</li>}
                    {!profile.location && <li>• Add your location</li>}
                    {profile.skills.length < 3 && (
                      <li>• Add at least 3 skills</li>
                    )}
                    {!primaryResume && <li>• Upload a resume</li>}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {primaryResume && primaryResume.parsedContent && (
            <Card>
              <CardHeader>
                <CardTitle>Skills from Resume</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {primaryResume.parsedContent.skills.map((skill, index) => (
                    <SkillBadge key={index} skill={skill} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <InfoCard
            title="Complete Your Profile"
            description="A complete profile increases your chance of finding the perfect job match by 70%"
            type="info"
          />
        </div>
      </div>
    </div>
  );
};

export default ProfileTemplate;
