# LinkedIn Job Matcher - Backend

## Visão Geral

O LinkedIn Job Matcher é uma plataforma inovadora que conecta candidatos a vagas de emprego através de tecnologia avançada de correspondência baseada em IA. O backend desta aplicação é responsável por coletar vagas do LinkedIn em tempo real, processar currículos e realizar a correspondência entre perfis e oportunidades usando o modelo Claude 3.7 Sonnet.

## Arquitetura

O backend segue uma arquitetura modular baseada em Flask, utilizando diversos componentes para oferecer uma solução robusta:

```
Backend (Flask)
  ├── API RESTful
  ├── Segurança (JWT/Rate Limiting)
  ├── Módulos (Usuários, Currículos, Vagas, Correspondência)
  ├── Camada de Dados (PostgreSQL, Redis)
  ├── Workers (Celery)
  ├── LinkedIn Scraping
  └── Serviços de IA (Claude 3.7 Sonnet API)
```

## Principais Recursos

- **API RESTful**: Endpoints para gerenciamento de usuários, currículos, vagas e correspondências
- **Web Scraping**: Coleta automatizada de vagas do LinkedIn
- **Análise de Currículos**: Processamento e extração de informações de currículos
- **IA para Correspondência**: Uso do Claude 3.7 Sonnet para analisar compatibilidade
- **Tarefas Assíncronas**: Processamento em background com Celery
- **WebSockets**: Notificações em tempo real para os usuários

## Tecnologias Utilizadas

- **Python 3.11+**
- **Flask**: Framework web
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache e filas de tarefas
- **Celery**: Processamento assíncrono
- **Selenium/Playwright**: Web scraping
- **Claude 3.7 Sonnet API**: Modelo de IA para análise e correspondência
- **SQLAlchemy**: ORM para banco de dados
- **Flask-SocketIO**: Comunicação em tempo real

## Configuração do Ambiente

### Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/linkedin-job-matcher.git
   cd linkedin-job-matcher/backend
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. Inicialize o banco de dados:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Execute a aplicação:
   ```bash
   flask run
   ```

7. Em outro terminal, inicie os workers do Celery:
   ```bash
   celery -A app.celery worker --loglevel=info
   celery -A app.celery beat --loglevel=info
   ```

## Estrutura do Projeto

```
backend/
├── app/                  # Aplicação principal
├── api/                  # Camada de API
├── models/               # Modelos de dados
├── services/             # Serviços de negócio
├── tasks/                # Tarefas assíncronas
├── database/             # Camada de persistência
├── utils/                # Utilitários
├── config/               # Configurações
└── tests/                # Testes
```

## API Endpoints

A documentação completa da API pode ser encontrada em `/docs/api/API_DOCUMENTATION.md`, mas aqui estão os principais endpoints:

- **Autenticação**
  - `POST /api/auth/register`: Registro de usuário
  - `POST /api/auth/login`: Login de usuário

- **Perfil e Currículo**
  - `GET /api/profile`: Obter perfil do usuário
  - `POST /api/resume/upload`: Upload de currículo

- **Vagas**
  - `GET /api/jobs`: Listar vagas
  - `GET /api/jobs/matches`: Obter vagas compatíveis

- **Correspondência**
  - `POST /api/match/analyze`: Analisar correspondência específica
  - `GET /api/match/recommendations`: Obter recomendações

## Web Scraping

O sistema utiliza técnicas avançadas para coletar vagas do LinkedIn:

- Scraping de listagens oficiais de vagas
- Coleta de posts contendo oportunidades de emprego
- Rotação de proxies e user-agents para evitar bloqueios
- Processamento assíncrono das tarefas de scraping

## Análise de IA

O Claude 3.7 Sonnet é utilizado para:

- Análise e extração de informações de currículos
- Processamento do conteúdo das vagas
- Cálculo de compatibilidade entre candidatos e oportunidades
- Geração de recomendações personalizadas

## Testes

Execute os testes com o comando:
```bash
pytest
```

Para testes com relatório de cobertura:
```bash
pytest --cov=app
```

## Desenvolvimento

Para configurar o ambiente de desenvolvimento:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.