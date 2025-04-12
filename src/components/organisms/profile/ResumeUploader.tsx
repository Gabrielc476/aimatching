// frontend/components/organisms/profile/ResumeUploader.tsx
import { useState, useRef } from "react";
import {
  Upload,
  File,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export interface ResumeInfo {
  id: string;
  filename: string;
  uploadedAt: string;
  isAnalyzed: boolean;
  isPrimary: boolean;
}

export interface ResumeUploaderProps {
  uploadUrl: string;
  onUploadComplete?: (resumeInfo: ResumeInfo) => void;
  onUploadError?: (error: string) => void;
  existingResumes?: ResumeInfo[];
  maxFileSize?: number; // in bytes
  allowedFileTypes?: string[];
}

const defaultAllowedTypes = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
  "application/msword", // .doc
  "text/plain", // .txt
];

const ResumeUploader = ({
  uploadUrl,
  onUploadComplete,
  onUploadError,
  existingResumes = [],
  maxFileSize = 5 * 1024 * 1024, // 5MB default
  allowedFileTypes = defaultAllowedTypes,
}: ResumeUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const validateFile = (file: File): { isValid: boolean; error?: string } => {
    if (!allowedFileTypes.includes(file.type)) {
      return {
        isValid: false,
        error: `Tipo de arquivo não suportado. Por favor, envie um arquivo ${allowedFileTypes
          .map((type) => type.split("/")[1])
          .join(", ")}.`,
      };
    }

    if (file.size > maxFileSize) {
      return {
        isValid: false,
        error: `Arquivo muito grande. O tamanho máximo permitido é ${Math.floor(
          maxFileSize / (1024 * 1024)
        )}MB.`,
      };
    }

    return { isValid: true };
  };

  const processFile = (file: File) => {
    setError(null);

    const validation = validateFile(file);
    if (!validation.isValid) {
      setError(validation.error || "Arquivo inválido");
      return;
    }

    if (existingResumes.length > 0) {
      setFileToUpload(file);
      setShowConfirmDialog(true);
    } else {
      uploadFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append("resume", file);

    try {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener("progress", (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          const response = JSON.parse(xhr.response);
          setIsUploading(false);

          if (onUploadComplete) {
            onUploadComplete(response);
          }
        } else {
          let errorMessage = "Falha ao enviar o currículo";
          try {
            const response = JSON.parse(xhr.response);
            errorMessage = response.message || errorMessage;
          } catch (e) {
            console.log(e, "erro ao fazer o parsing do arquivo");
          }

          setError(errorMessage);
          setIsUploading(false);

          if (onUploadError) {
            onUploadError(errorMessage);
          }
        }
      });

      xhr.addEventListener("error", () => {
        setError("Erro de conexão ao enviar o arquivo");
        setIsUploading(false);

        if (onUploadError) {
          onUploadError("Erro de conexão ao enviar o arquivo");
        }
      });

      xhr.open("POST", uploadUrl, true);
      xhr.send(formData);
    } catch (err) {
      setError("Ocorreu um erro ao enviar o arquivo");
      console.log(err);
      setIsUploading(false);

      if (onUploadError) {
        onUploadError("Ocorreu um erro ao enviar o arquivo");
      }
    }
  };

  const confirmUpload = () => {
    setShowConfirmDialog(false);
    if (fileToUpload) {
      uploadFile(fileToUpload);
    }
  };

  const cancelUpload = () => {
    setShowConfirmDialog(false);
    setFileToUpload(null);
  };

  const getFileTypeIcon = (filename: string) => {
    const extension = filename.split(".").pop()?.toLowerCase();

    switch (extension) {
      case "pdf":
        return <FileText className="h-4 w-4 text-red-500" />;
      case "doc":
      case "docx":
        return <FileText className="h-4 w-4 text-blue-500" />;
      case "txt":
        return <FileText className="h-4 w-4 text-gray-500" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Upload de Currículo</CardTitle>
          <CardDescription>
            Carregue seu currículo para começar a encontrar correspondências com
            vagas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center transition-colors ${
              isDragging
                ? "border-primary bg-primary/5"
                : "border-muted-foreground/25"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              accept={allowedFileTypes.join(",")}
            />

            <Upload className="h-10 w-10 text-muted-foreground mb-4" />

            <div className="text-center space-y-2">
              <h3 className="font-medium">
                Arraste e solte seu currículo aqui
              </h3>
              <p className="text-sm text-muted-foreground">
                Suporta arquivos PDF, DOCX, DOC ou TXT (máx.{" "}
                {Math.floor(maxFileSize / (1024 * 1024))}MB)
              </p>
            </div>

            <Button
              onClick={handleButtonClick}
              className="mt-4"
              disabled={isUploading}
            >
              Selecionar Arquivo
            </Button>
          </div>

          {isUploading && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center">
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                <span className="text-sm">Enviando arquivo...</span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>
          )}

          {error && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Erro</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {existingResumes.length > 0 && (
            <div className="mt-6 space-y-3">
              <h4 className="text-sm font-medium">Currículos Carregados</h4>
              <div className="space-y-2">
                {existingResumes.map((resume) => (
                  <div
                    key={resume.id}
                    className="flex items-center justify-between p-3 bg-muted/50 rounded-md"
                  >
                    <div className="flex items-center space-x-3">
                      {getFileTypeIcon(resume.filename)}
                      <div>
                        <p className="text-sm font-medium">{resume.filename}</p>
                        <p className="text-xs text-muted-foreground">
                          Enviado em:{" "}
                          {new Date(resume.uploadedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {resume.isAnalyzed ? (
                        <span className="inline-flex items-center text-xs text-green-600">
                          <CheckCircle className="h-3 w-3 mr-1" /> Analisado
                        </span>
                      ) : (
                        <span className="inline-flex items-center text-xs text-amber-600">
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />{" "}
                          Processando
                        </span>
                      )}
                      {resume.isPrimary && (
                        <span className="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full">
                          Principal
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="text-xs text-muted-foreground">
          <p>
            Seu currículo será analisado por nossa IA para identificar suas
            habilidades e experiência. Isso nos ajudará a encontrar as melhores
            correspondências de vagas para o seu perfil.
          </p>
        </CardFooter>
      </Card>

      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enviar novo currículo?</DialogTitle>
            <DialogDescription>
              Você já possui um currículo carregado. Deseja enviar um novo
              currículo? Você poderá gerenciar múltiplos currículos no seu
              perfil.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex space-x-2 justify-end">
            <Button variant="outline" onClick={cancelUpload}>
              Cancelar
            </Button>
            <Button onClick={confirmUpload}>Confirmar Upload</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ResumeUploader;
