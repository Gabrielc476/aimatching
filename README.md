AI-Powered Job Matching Platform
A comprehensive job matching platform that uses AI to analyze resumes and job postings, helping candidates find the most compatible job opportunities based on their skills, experience, and preferences.
Features
For Job Seekers

Resume Upload and Analysis: Upload your resume in PDF format and have AI extract structured information
Profile Management: Edit and update your professional profile with details about your experience, education, skills, languages, and certifications
Job Discovery: Browse and search for job opportunities with advanced filtering options
AI-Powered Compatibility Analysis: Get detailed compatibility analysis between your profile and job postings
Personalized Recommendations: Receive customized suggestions on how to improve your chances with specific job positions

For Employers/Recruiters

Job Posting: Add job listings with detailed requirements
Candidate Matching: Automatically match job postings with qualified candidates
Applicant Tracking: Manage applications and candidate pipelines

Tech Stack
Backend

Python with Flask framework
MongoDB for database
JWT for authentication
PyPDF2 for PDF text extraction
Anthropic Claude API for AI-powered analysis

Frontend

Next.js with React and TypeScript
Tailwind CSS for styling
Shadcn UI component library
React Hook Form for form handling
Axios for API communication

Installation
Prerequisites

Python 3.8+
Node.js 16+
MongoDB
Anthropic API key

Backend Setup

Clone the repository:
bashgit clone https://github.com/yourusername/job-matching-platform.git
cd job-matching-platform

Set up a Python virtual environment:
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Python dependencies:
bashpip install -r requirements.txt

Create a .env file in the root directory with the following variables:
MONGO_DB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
ANTHROPIC_API_KEY=your_anthropic_api_key

Start the Flask server:
bashpython app.py


Frontend Setup

Navigate to the frontend directory:
bashcd src

Install Node.js dependencies:
bashnpm install

Create a .env.local file with the following:
NEXT_PUBLIC_API_URL=http://localhost:5000

Start the development server:
bashnpm run dev

Access the application at http://localhost:3000

Usage
User Registration and Login

Create a new account with your email and password
Log in to access the dashboard

Resume Management

Upload your resume in PDF format
Review the extracted information
Edit and complete your profile as needed

Job Search and Matching

Browse available job listings
Use filters to narrow down your search
View job details and analyze compatibility with your profile
Apply to suitable positions

Project Structure
├── app.py                     # Main Flask application entry point
├── banco_de_dados/            # Database-related code
│   ├── conexao.py             # MongoDB connection setup
│   └── repositorios/          # Repository classes for data access
├── modelos/                   # Data models
├── rotas/                     # API route definitions
├── servicos/                  # Business logic services
├── src/                       # Frontend Next.js application
│   ├── app/                   # Next.js pages and components
│   ├── components/            # React components
│   ├── lib/                   # Utility functions and hooks
│   ├── types/                 # TypeScript type definitions
│   └── ...
└── ...
API Documentation
The platform provides RESTful APIs for all operations:
Authentication

POST /usuario/cadastro - Register a new user
POST /usuario/login - Log in and get JWT token

Resume Management

POST /curriculo/upload - Upload and process a resume
GET /usuario/:id - Get user profile
PUT /usuario/:id - Update user profile

Job Management

GET /vaga/listar - List available jobs
GET /vaga/:id - Get job details
POST /vaga/adicionar - Add a new job posting

Matching

POST /matching/analisar - Analyze compatibility between a user and a job
GET /matching/usuario/:id - Get all matchings for a user
GET /matching/:usuario_id/:vaga_id - Get specific matching details

Future Enhancements

Mobile app support
Interview scheduling
Advanced analytics dashboards
Integration with popular job boards
Optimization of matching algorithms
Expanded resume format support (DOCX, HTML, etc.)

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements

Anthropic for providing the Claude API used for AI-powered analysis
All open-source libraries and frameworks used in this project
Tentar novamenteGCfaça em portguês e inglêsEditarCrafted bilingual README with comprehensive project documentation.1 sEu vou criar duas versões do README do projeto - uma em português e outra em inglês. Vou manter todas as informações importantes sobre o projeto, incluindo recursos, stack de tecnologia, instalação, uso, estrutura do projeto, documentação da API, melhorias futuras e outros detalhes relevantes.Plataforma de Matching de Currículos com IA
Uma plataforma abrangente de matching de currículos que utiliza IA para analisar currículos e vagas de emprego, ajudando candidatos a encontrarem as oportunidades de trabalho mais compatíveis com suas habilidades, experiência e preferências.
Funcionalidades
Para Candidatos

Upload e Análise de Currículo: Faça upload do seu currículo em PDF e tenha as informações extraídas automaticamente pela IA
Gerenciamento de Perfil: Edite e atualize seu perfil profissional com detalhes sobre experiência, educação, habilidades, idiomas e certificações
Descoberta de Vagas: Navegue e pesquise oportunidades de trabalho com opções avançadas de filtragem
Análise de Compatibilidade com IA: Obtenha análises detalhadas de compatibilidade entre seu perfil e as vagas disponíveis
Recomendações Personalizadas: Receba sugestões personalizadas sobre como melhorar suas chances com posições específicas

Para Empregadores/Recrutadores

Publicação de Vagas: Adicione vagas com requisitos detalhados
Matching de Candidatos: Combine automaticamente vagas com candidatos qualificados
Acompanhamento de Candidaturas: Gerencie aplicações e acompanhe candidatos

Stack Tecnológico
Backend

Python com framework Flask
MongoDB para banco de dados
JWT para autenticação
PyPDF2 para extração de texto de PDFs
API Claude da Anthropic para análises baseadas em IA

Frontend

Next.js com React e TypeScript
Tailwind CSS para estilização
Shadcn UI biblioteca de componentes
React Hook Form para gestão de formulários
Axios para comunicação com a API

Instalação
Pré-requisitos

Python 3.8+
Node.js 16+
MongoDB
Chave de API da Anthropic

Configuração do Backend

Clone o repositório:
bashgit clone https://github.com/seuusuario/plataforma-matching-curriculos.git
cd plataforma-matching-curriculos

Configure um ambiente virtual Python:
bashpython -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

Instale as dependências Python:
bashpip install -r requirements.txt

Crie um arquivo .env no diretório raiz com as seguintes variáveis:
MONGO_DB_URI=sua_string_de_conexao_mongodb
JWT_SECRET=seu_segredo_jwt
ANTHROPIC_API_KEY=sua_chave_api_anthropic

Inicie o servidor Flask:
bashpython app.py


Configuração do Frontend

Navegue até o diretório frontend:
bashcd src

Instale as dependências Node.js:
bashnpm install

Crie um arquivo .env.local com o seguinte:
NEXT_PUBLIC_API_URL=http://localhost:5000

Inicie o servidor de desenvolvimento:
bashnpm run dev

Acesse a aplicação em http://localhost:3000

Uso
Registro e Login de Usuário

Crie uma nova conta com seu email e senha
Faça login para acessar o dashboard

Gerenciamento de Currículo

Faça upload do seu currículo em formato PDF
Revise as informações extraídas
Edite e complete seu perfil conforme necessário

Busca de Vagas e Matching

Navegue pelas vagas disponíveis
Use filtros para refinar sua busca
Visualize detalhes da vaga e analise a compatibilidade com seu perfil
Candidate-se às posições adequadas

Estrutura do Projeto
├── app.py                     # Ponto de entrada principal da aplicação Flask
├── banco_de_dados/            # Código relacionado ao banco de dados
│   ├── conexao.py             # Configuração de conexão com MongoDB
│   └── repositorios/          # Classes de repositório para acesso a dados
├── modelos/                   # Modelos de dados
├── rotas/                     # Definições de rotas da API
├── servicos/                  # Serviços de lógica de negócios
├── src/                       # Aplicação frontend Next.js
│   ├── app/                   # Páginas e componentes Next.js
│   ├── components/            # Componentes React
│   ├── lib/                   # Funções e hooks de utilidade
│   ├── types/                 # Definições de tipos TypeScript
│   └── ...
└── ...
Documentação da API
A plataforma fornece APIs RESTful para todas as operações:
Autenticação

POST /usuario/cadastro - Registrar um novo usuário
POST /usuario/login - Fazer login e obter token JWT

Gerenciamento de Currículo

POST /curriculo/upload - Fazer upload e processar um currículo
GET /usuario/:id - Obter perfil do usuário
PUT /usuario/:id - Atualizar perfil do usuário

Gerenciamento de Vagas

GET /vaga/listar - Listar vagas disponíveis
GET /vaga/:id - Obter detalhes da vaga
POST /vaga/adicionar - Adicionar uma nova vaga

Matching

POST /matching/analisar - Analisar compatibilidade entre um usuário e uma vaga
GET /matching/usuario/:id - Obter todos os matchings para um usuário
GET /matching/:usuario_id/:vaga_id - Obter detalhes de matching específico

Melhorias Futuras

Suporte para aplicativo móvel
Agendamento de entrevistas
Painéis avançados de análise
Integração com portais de emprego populares
Otimização dos algoritmos de matching
Suporte expandido para formatos de currículo (DOCX, HTML, etc.)

Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.
Agradecimentos

Anthropic por fornecer a API Claude usada para análise com IA
Todas as bibliotecas e frameworks de código aberto utilizados neste projeto


AI-Powered Resume Matching Platform
A comprehensive resume matching platform that uses AI to analyze resumes and job postings, helping candidates find the most compatible job opportunities based on their skills, experience, and preferences.
Features
For Job Seekers

Resume Upload and Analysis: Upload your resume in PDF format and have AI extract structured information
Profile Management: Edit and update your professional profile with details about your experience, education, skills, languages, and certifications
Job Discovery: Browse and search for job opportunities with advanced filtering options
AI-Powered Compatibility Analysis: Get detailed compatibility analysis between your profile and job postings
Personalized Recommendations: Receive customized suggestions on how to improve your chances with specific job positions

For Employers/Recruiters

Job Posting: Add job listings with detailed requirements
Candidate Matching: Automatically match job postings with qualified candidates
Applicant Tracking: Manage applications and candidate pipelines

Tech Stack
Backend

Python with Flask framework
MongoDB for database
JWT for authentication
PyPDF2 for PDF text extraction
Anthropic Claude API for AI-powered analysis

Frontend

Next.js with React and TypeScript
Tailwind CSS for styling
Shadcn UI component library
React Hook Form for form handling
Axios for API communication

Installation
Prerequisites

Python 3.8+
Node.js 16+
MongoDB
Anthropic API key

Backend Setup

Clone the repository:
bashgit clone https://github.com/yourusername/resume-matching-platform.git
cd resume-matching-platform

Set up a Python virtual environment:
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Python dependencies:
bashpip install -r requirements.txt

Create a .env file in the root directory with the following variables:
MONGO_DB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
ANTHROPIC_API_KEY=your_anthropic_api_key

Start the Flask server:
bashpython app.py


Frontend Setup

Navigate to the frontend directory:
bashcd src

Install Node.js dependencies:
bashnpm install

Create a .env.local file with the following:
NEXT_PUBLIC_API_URL=http://localhost:5000

Start the development server:
bashnpm run dev

Access the application at http://localhost:3000

Usage
User Registration and Login

Create a new account with your email and password
Log in to access the dashboard

Resume Management

Upload your resume in PDF format
Review the extracted information
Edit and complete your profile as needed

Job Search and Matching

Browse available job listings
Use filters to narrow down your search
View job details and analyze compatibility with your profile
Apply to suitable positions

Project Structure
├── app.py                     # Main Flask application entry point
├── banco_de_dados/            # Database-related code
│   ├── conexao.py             # MongoDB connection setup
│   └── repositorios/          # Repository classes for data access
├── modelos/                   # Data models
├── rotas/                     # API route definitions
├── servicos/                  # Business logic services
├── src/                       # Frontend Next.js application
│   ├── app/                   # Next.js pages and components
│   ├── components/            # React components
│   ├── lib/                   # Utility functions and hooks
│   ├── types/                 # TypeScript type definitions
│   └── ...
└── ...
API Documentation
The platform provides RESTful APIs for all operations:
Authentication

POST /usuario/cadastro - Register a new user
POST /usuario/login - Log in and get JWT token

Resume Management

POST /curriculo/upload - Upload and process a resume
GET /usuario/:id - Get user profile
PUT /usuario/:id - Update user profile

Job Management

GET /vaga/listar - List available jobs
GET /vaga/:id - Get job details
POST /vaga/adicionar - Add a new job posting

Matching

POST /matching/analisar - Analyze compatibility between a user and a job
GET /matching/usuario/:id - Get all matchings for a user
GET /matching/:usuario_id/:vaga_id - Get specific matching details

Future Enhancements

Mobile app support
Interview scheduling
Advanced analytics dashboards
Integration with popular job boards
Optimization of matching algorithms
Expanded resume format support (DOCX, HTML, etc.)

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements

Anthropic for providing the Claude API used for AI-powered analysis
All open-source libraries and frameworks used in this project
