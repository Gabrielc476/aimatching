"""
Analisador de vagas para extração de informações estruturadas.

Este módulo contém a implementação do analisador de vagas que extrai
informações estruturadas de descrições de vagas.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

# NLP
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords

    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except ImportError:
    nltk = None

from ..ai.claude_service import ClaudeService

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """
    Analisador de vagas para extração de informações estruturadas.

    Esta classe implementa métodos para extrair dados estruturados
    de descrições de vagas de emprego.
    """

    def __init__(self, claude_service: ClaudeService = None):
        """
        Inicializa o analisador de vagas.

        Args:
            claude_service: Serviço de integração com Claude 3.7 Sonnet
        """
        self.claude_service = claude_service

        # Expressões regulares para extração de informações
        self.regex_patterns = {
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'location': r'\b(?:Local|Location|Localização)[\s:]+([\w\s,-]+)(?:\.|\n|$)',
            'salary': r'\b(?:Salário|Salary|Remuneração)[\s:]+([\w\s$.,R€£-]+)(?:\.|\n|$)',
            'job_type': r'\b(?:Tipo|Type|Regime|Contrato)[\s:]+([\w\s-]+)(?:\.|\n|$)',
            'experience': r'\b(?:Experiência|Experience|Nível)[\s:]+([\w\s-]+)(?:\.|\n|$)',
            'education': r'\b(?:Formação|Education|Educação)[\s:]+([\w\s-]+)(?:\.|\n|$)',
            'requirements': r'(?:Requisitos|Requirements|Qualificações|Qualifications|Exigências)[:\s]+([\s\S]+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
            'benefits': r'(?:Benefícios|Benefits|Oferecemos|We offer)[:\s]+([\s\S]+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)'
        }

        # Listas de habilidades técnicas e não-técnicas comuns
        self.technical_skills = [
            'python', 'java', 'javascript', 'typescript', 'c#', 'c\+\+', 'php', 'ruby', 'swift',
            'kotlin', 'go', 'rust', 'html', 'css', 'sql', 'nosql', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'spring', 'asp\.net', 'laravel', 'rails', 'express',
            'mongodb', 'postgresql', 'mysql', 'oracle', 'sqlite', 'redis', 'aws', 'azure',
            'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'git', 'github', 'gitlab',
            'jira', 'scrum', 'kanban', 'agile', 'machine learning', 'ml', 'ai', 'deep learning',
            'data science', 'big data', 'hadoop', 'spark', 'tableau', 'power bi', 'excel',
            'word', 'powerpoint', 'photoshop', 'illustrator', 'figma', 'sketch'
        ]

        self.soft_skills = [
            'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
            'decision making', 'time management', 'organization', 'adaptability', 'flexibility',
            'creativity', 'emotional intelligence', 'conflict resolution', 'negotiation',
            'persuasion', 'collaboration', 'interpersonal', 'trabalho em equipe', 'liderança',
            'resolução de problemas', 'pensamento crítico', 'tomada de decisão', 'gestão de tempo',
            'organização', 'adaptabilidade', 'flexibilidade', 'criatividade', 'inteligência emocional',
            'resolução de conflitos', 'negociação', 'persuasão', 'colaboração', 'interpessoal',
            'comunicação', 'proatividade', 'empatia', 'resiliência'
        ]

    def analyze(self, job_data: Dict[str, Any], use_claude: bool = True) -> Dict[str, Any]:
        """
        Analisa uma vaga e extrai informações estruturadas.

        Args:
            job_data: Dados básicos da vaga (título, empresa, descrição, etc.)
            use_claude: Se True, usa o Claude 3.7 para análise

        Returns:
            Dicionário com informações estruturadas da vaga
        """
        logger.info(f"Analisando vaga: {job_data.get('title', 'Sem título')}")

        description = job_data.get('description', '')
        if not description:
            logger.error("Descrição da vaga está vazia")
            return {
                'error': "Descrição da vaga está vazia",
                'original_data': job_data
            }

        # Se utilizarmos o Claude para análise, delegamos a extração
        if use_claude and self.claude_service:
            try:
                analyzed_job = self.claude_service.parse_job_post(job_data)

                # Preserva os dados originais da vaga
                for key, value in job_data.items():
                    if key not in analyzed_job:
                        analyzed_job[key] = value

                logger.info(f"Vaga analisada pelo Claude: {job_data.get('title', 'Sem título')}")
                return analyzed_job

            except Exception as e:
                logger.error(f"Erro ao analisar vaga com Claude: {str(e)}")
                logger.info("Recorrendo ao algoritmo de análise interno")
                # Continua com o algoritmo interno em caso de falha

        # Caso contrário, usamos o algoritmo interno
        try:
            # Inicializa com os dados existentes
            analyzed_job = job_data.copy()

            # Extrai informações adicionais da descrição
            extracted_data = self._extract_job_data(description)

            # Atualiza os dados da vaga com as informações extraídas
            for key, value in extracted_data.items():
                # Não sobrescreve campos existentes, a menos que estejam vazios
                if key not in analyzed_job or not analyzed_job[key]:
                    analyzed_job[key] = value

            # Extrai habilidades da descrição, se não existirem
            if 'skills' not in analyzed_job or not analyzed_job['skills']:
                analyzed_job['skills'] = self._extract_skills(description)

            # Adiciona timestamp de análise
            analyzed_job['analyzed_at'] = datetime.utcnow().isoformat()

            logger.info(f"Vaga analisada internamente: {job_data.get('title', 'Sem título')}")
            return analyzed_job

        except Exception as e:
            logger.error(f"Erro ao analisar vaga internamente: {str(e)}")

            # Retorna os dados originais em caso de erro
            job_data['error'] = str(e)
            return job_data

    def analyze_job_batch(self, job_list: List[Dict[str, Any]], use_claude: bool = False) -> List[Dict[str, Any]]:
        """
        Analisa um lote de vagas em uma única operação.

        Args:
            job_list: Lista de dados básicos de vagas
            use_claude: Se True, usa o Claude 3.7 para análise (não recomendado para lotes grandes)

        Returns:
            Lista de vagas com informações estruturadas
        """
        logger.info(f"Analisando lote de {len(job_list)} vagas")

        # Para lotes grandes, é mais eficiente usar o algoritmo interno
        # Claude pode ser muito custoso para múltiplas chamadas
        analyzed_jobs = []

        for job_data in job_list:
            try:
                # Usa o modo apropriado de análise
                analyzed_job = self.analyze(job_data, use_claude=use_claude)
                analyzed_jobs.append(analyzed_job)
            except Exception as e:
                logger.error(f"Erro ao analisar vaga no lote: {str(e)}")
                job_data['error'] = str(e)
                analyzed_jobs.append(job_data)

        return analyzed_jobs

    def _extract_job_data(self, description: str) -> Dict[str, Any]:
        """
        Extrai informações estruturadas da descrição da vaga.

        Args:
            description: Texto da descrição da vaga

        Returns:
            Dicionário com informações extraídas
        """
        extracted_data = {}

        # Extrai localização
        location_match = re.search(self.regex_patterns['location'], description)
        if location_match:
            extracted_data['location'] = location_match.group(1).strip()

        # Extrai faixa salarial
        salary_match = re.search(self.regex_patterns['salary'], description)
        if salary_match:
            extracted_data['salary_range'] = salary_match.group(1).strip()

        # Extrai tipo de emprego
        job_type_match = re.search(self.regex_patterns['job_type'], description)
        if job_type_match:
            extracted_data['job_type'] = job_type_match.group(1).strip()
        else:
            # Tenta identificar o tipo de emprego por padrões comuns
            job_types = {
                'CLT': ['clt', 'carteira assinada', 'regime clt', 'efetivo'],
                'PJ': ['pj', 'pessoa jurídica', 'regime pj', 'cnpj'],
                'Freelance': ['freelance', 'freela', 'projeto', 'temporário'],
                'Estágio': ['estágio', 'estagiário', 'trainee', 'estudante'],
                'Tempo integral': ['tempo integral', 'full time', 'full-time', '40h', '44h'],
                'Meio período': ['meio período', 'part time', 'part-time', '20h', '30h']
            }

            for job_type, keywords in job_types.items():
                if any(keyword in description.lower() for keyword in keywords):
                    extracted_data['job_type'] = job_type
                    break

        # Extrai nível de experiência
        experience_match = re.search(self.regex_patterns['experience'], description)
        if experience_match:
            extracted_data['experience_level'] = experience_match.group(1).strip()
        else:
            # Tenta identificar o nível de experiência por padrões comuns
            experience_patterns = {
                'Estágio': ['estágio', 'estagiário', 'trainee', 'estudante'],
                'Júnior': ['júnior', 'junior', 'jr', 'jr.', 'iniciante'],
                'Pleno': ['pleno', 'mid-level', 'intermediário'],
                'Sênior': ['sênior', 'senior', 'sr', 'sr.', 'especialista'],
                'Gerente': ['gerente', 'manager', 'coordenador', 'líder', 'gestor']
            }

            for level, keywords in experience_patterns.items():
                if any(keyword in description.lower() for keyword in keywords):
                    extracted_data['experience_level'] = level
                    break

        # Extrai requisitos de formação
        education_match = re.search(self.regex_patterns['education'], description)
        if education_match:
            extracted_data['education_requirements'] = education_match.group(1).strip()

        # Extrai requisitos
        requirements_match = re.search(self.regex_patterns['requirements'], description)
        if requirements_match:
            requirements_text = requirements_match.group(1).strip()
            extracted_data['requirements'] = self._parse_list_items(requirements_text)
        else:
            # Se não encontrar uma seção específica, tenta extrair de marcadores
            extracted_data['requirements'] = self._extract_bullet_points(description)

        # Extrai benefícios
        benefits_match = re.search(self.regex_patterns['benefits'], description)
        if benefits_match:
            benefits_text = benefits_match.group(1).strip()
            extracted_data['benefits'] = self._parse_list_items(benefits_text)

        return extracted_data

    def _extract_skills(self, description: str) -> Dict[str, List[str]]:
        """
        Extrai habilidades da descrição da vaga.

        Args:
            description: Texto da descrição da vaga

        Returns:
            Dicionário com habilidades técnicas e não-técnicas
        """
        skills = {'technical': [], 'soft': []}
        description_lower = description.lower()

        # Extrai habilidades técnicas
        for skill in self.technical_skills:
            if re.search(r'\b' + skill + r'\b', description_lower):
                # Normaliza a habilidade (primeira letra maiúscula)
                normalized_skill = skill.capitalize()
                if normalized_skill not in skills['technical']:
                    skills['technical'].append(normalized_skill)

        # Extrai habilidades não-técnicas
        for skill in self.soft_skills:
            if re.search(r'\b' + skill + r'\b', description_lower):
                # Normaliza a habilidade (primeira letra maiúscula)
                normalized_skill = skill.capitalize()
                if normalized_skill not in skills['soft']:
                    skills['soft'].append(normalized_skill)

        return skills

    def _parse_list_items(self, text: str) -> List[str]:
        """
        Parseia itens de lista de um texto.

        Args:
            text: Texto contendo itens de lista

        Returns:
            Lista de itens
        """
        items = []

        # Divide o texto em linhas
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # Pula linhas vazias
            if not line:
                continue

            # Verifica se a linha começa com um marcador
            if line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line):
                # Remove o marcador
                cleaned_line = re.sub(r'^[-•*\d\.]+\s*', '', line).strip()
                if cleaned_line:
                    items.append(cleaned_line)
            else:
                # Se não começar com marcador, adiciona a linha inteira
                items.append(line)

        return items

    def _extract_bullet_points(self, text: str) -> List[str]:
        """
        Extrai pontos marcados de um texto.

        Args:
            text: Texto completo

        Returns:
            Lista de pontos marcados
        """
        bullet_points = []

        # Divide o texto em linhas
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # Pula linhas vazias
            if not line:
                continue

            # Verifica se a linha começa com um marcador
            if line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line):
                # Remove o marcador
                cleaned_line = re.sub(r'^[-•*\d\.]+\s*', '', line).strip()
                if cleaned_line and len(cleaned_line) > 10:  # Evita itens muito curtos
                    bullet_points.append(cleaned_line)

        return bullet_points

    def extract_keywords(self, description: str, max_keywords: int = 10) -> List[str]:
        """
        Extrai palavras-chave da descrição da vaga.

        Args:
            description: Texto da descrição da vaga
            max_keywords: Número máximo de palavras-chave a retornar

        Returns:
            Lista de palavras-chave
        """
        if not nltk:
            logger.warning("NLTK não está disponível para extração de palavras-chave")
            return []

        try:
            # Tokeniza o texto
            tokens = word_tokenize(description.lower())

            # Remove stopwords
            stop_words = set(stopwords.words('english') + stopwords.words('portuguese'))
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]

            # Conta a frequência das palavras
            word_freq = {}
            for token in filtered_tokens:
                if len(token) > 3:  # Ignora palavras muito curtas
                    word_freq[token] = word_freq.get(token, 0) + 1

            # Ordena por frequência
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

            # Retorna as palavras mais frequentes
            return [word for word, freq in sorted_words[:max_keywords]]

        except Exception as e:
            logger.error(f"Erro ao extrair palavras-chave: {str(e)}")
            return []

    def categorize_job(self, job_data: Dict[str, Any]) -> str:
        """
        Categoriza a vaga em uma área profissional.

        Args:
            job_data: Dados da vaga

        Returns:
            Categoria profissional
        """
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        skills = []

        if 'skills' in job_data:
            skills_data = job_data['skills']
            if isinstance(skills_data, dict):
                # Se for um dicionário com 'technical' e 'soft'
                skills.extend([s.lower() for s in skills_data.get('technical', [])])
                skills.extend([s.lower() for s in skills_data.get('soft', [])])
            elif isinstance(skills_data, list):
                # Se for uma lista direta
                skills.extend([s.lower() for s in skills_data])

        # Categorias e suas palavras-chave
        categories = {
            'Desenvolvimento de Software': [
                'desenvolvedor', 'programador', 'software', 'developer', 'programmer',
                'python', 'java', 'javascript', 'typescript', 'c#', 'c++', 'react',
                'angular', 'vue', 'node', 'backend', 'frontend', 'full stack', 'web',
                'mobile', 'app', 'código', 'code', 'engenheiro de software'
            ],
            'Dados e Analytics': [
                'dados', 'data', 'scientist', 'analytics', 'analista de dados',
                'business intelligence', 'bi', 'big data', 'machine learning', 'ml',
                'estatística', 'statistics', 'sql', 'tableau', 'power bi', 'excel',
                'análise de dados', 'data engineer', 'database', 'banco de dados'
            ],
            'Design e UX': [
                'design', 'ux', 'ui', 'user experience', 'experiência do usuário',
                'interface', 'gráfico', 'graphic', 'web design', 'photoshop', 'illustrator',
                'figma', 'sketch', 'adobe', 'produto', 'product'
            ],
            'Marketing Digital': [
                'marketing', 'digital', 'seo', 'sem', 'social media', 'mídia social',
                'conteúdo', 'content', 'adwords', 'google analytics', 'facebook ads',
                'instagram', 'campanha', 'campaign', 'inbound', 'outbound', 'copywriter'
            ],
            'Vendas e Comercial': [
                'vendas', 'sales', 'comercial', 'account', 'cliente', 'customer',
                'representante', 'inside sales', 'hunter', 'closer', 'pré-venda',
                'presales', 'negociação', 'negotiation', 'b2b', 'b2c', 'consultoria'
            ],
            'Operações e Logística': [
                'operações', 'operations', 'logística', 'logistics', 'supply chain',
                'cadeia de suprimentos', 'compras', 'purchasing', 'estoque', 'inventory',
                'armazém', 'warehouse', 'planejamento', 'planning', 'produção', 'production'
            ],
            'Recursos Humanos': [
                'rh', 'recursos humanos', 'hr', 'human resources', 'recrutamento',
                'recruitment', 'seleção', 'selection', 'people', 'pessoas', 'talentos',
                'talent', 'treinamento', 'training', 'desenvolvimento', 'development'
            ],
            'Finanças e Contabilidade': [
                'finanças', 'finance', 'contabilidade', 'accounting', 'contador',
                'accountant', 'financeiro', 'financial', 'controladoria', 'controller',
                'auditor', 'fiscal', 'tax', 'impostos', 'compliance', 'regulatório'
            ],
            'Administrativo e Suporte': [
                'administrativo', 'administrative', 'suporte', 'support', 'assistente',
                'assistant', 'recepcionista', 'receptionist', 'atendimento', 'customer service',
                'secretário', 'secretary', 'auxiliar', 'help desk', 'office'
            ]
        }

        # Pontuação para cada categoria
        scores = {category: 0 for category in categories}

        # Calcula a pontuação para cada categoria
        for category, keywords in categories.items():
            for keyword in keywords:
                # Pontuação no título tem peso maior
                if keyword in title:
                    scores[category] += 3

                # Pontuação na descrição
                if keyword in description:
                    scores[category] += 1

                # Pontuação nas habilidades
                if keyword in skills:
                    scores[category] += 2

        # Retorna a categoria com maior pontuação
        max_score = 0
        best_category = "Outros"

        for category, score in scores.items():
            if score > max_score:
                max_score = score
                best_category = category

        return best_category