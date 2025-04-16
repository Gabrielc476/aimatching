"""
Serviço de integração com o Claude 3.7 Sonnet.

Este módulo contém a implementação do serviço de integração com o
modelo Claude 3.7 Sonnet para análise de currículos e vagas.
"""

import logging
import json
import re
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

try:
    from anthropic import Anthropic, RateLimitError
except ImportError:
    Anthropic = None
    RateLimitError = Exception

from .prompts import PromptTemplates
from .response_parser import ResponseParser
from .. import registry

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Serviço de integração com o Claude 3.7 Sonnet.

    Esta classe implementa métodos para interagir com o modelo Claude 3.7 Sonnet
    para análise de currículos, vagas e cálculo de correspondência.
    """

    def __init__(self, api_key: str = None, model: str = "claude-3-7-sonnet-20250219"):
        """
        Inicializa o serviço de integração com o Claude.

        Args:
            api_key: Chave de API para o Claude
            model: String identificadora do modelo Claude a ser utilizado
        """
        # Tenta obter a chave da API do registro de serviços se não for fornecida
        if not api_key:
            config = registry.get_config()
            api_key = config.get('claude_api_key')

        self.api_key = api_key
        self.model = model
        self.client = None
        self.prompt_templates = PromptTemplates()
        self.response_parser = ResponseParser()

        # Configurações de requisição
        self.max_retries = 3
        self.retry_delay = 2  # segundos
        self.temperature = 0.3

        # Inicializa o cliente se possível
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa o cliente Claude se a biblioteca estiver disponível."""
        if not Anthropic:
            logger.warning("Biblioteca Anthropic não está disponível. Instale com 'pip install anthropic'")
            return

        if not self.api_key:
            logger.warning("Chave de API do Claude não foi fornecida")
            return

        try:
            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"Cliente Claude inicializado com o modelo {self.model}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Claude: {str(e)}")

    def _send_request(self, prompt: str, system_prompt: str = None, max_tokens: int = 4000) -> str:
        """
        Envia uma requisição para o Claude e processa a resposta.

        Args:
            prompt: Texto do prompt
            system_prompt: Texto do prompt de sistema (opcional)
            max_tokens: Número máximo de tokens para a resposta

        Returns:
            Texto da resposta do Claude

        Raises:
            Exception: Se ocorrer um erro na requisição
        """
        if not self.client:
            raise Exception("Cliente Claude não está inicializado")

        # Configuração padrão do prompt de sistema
        if not system_prompt:
            system_prompt = "Você é um assistente especializado em análise de currículos e vagas de emprego."

        # Tenta enviar a requisição com retry
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # Extrai o texto da resposta
                return response.content[0].text

            except RateLimitError:
                # Se atingir o rate limit, espera antes de tentar novamente
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Rate limit atingido. Tentando novamente em {wait_time} segundos...")
                time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Erro na requisição ao Claude (tentativa {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay)

        raise Exception("Erro ao processar requisição após múltiplas tentativas")

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analisa um currículo e extrai informações estruturadas.

        Args:
            resume_text: Texto do currículo

        Returns:
            Dicionário com informações estruturadas do currículo

        Raises:
            Exception: Se ocorrer um erro na análise
        """
        logger.info("Analisando currículo com Claude")

        try:
            # Gera o prompt para análise de currículo
            prompt = self.prompt_templates.get_resume_analysis_prompt(resume_text)

            # Envia a requisição
            system_prompt = "Você é um assistente especializado em análise de currículos. Sua tarefa é extrair informações estruturadas de currículos em formato de texto."
            response_text = self._send_request(prompt, system_prompt)

            # Processa a resposta para extrair o JSON
            result = self.response_parser.extract_json(response_text)

            if not result:
                logger.warning("Não foi possível extrair JSON da resposta do Claude")
                result = self._fallback_resume_parsing(response_text)

            return result

        except Exception as e:
            logger.error(f"Erro ao analisar currículo com Claude: {str(e)}")
            raise

    def parse_job_post(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai informações estruturadas de uma vaga.

        Args:
            job_data: Dados da vaga

        Returns:
            Dicionário com informações estruturadas da vaga

        Raises:
            Exception: Se ocorrer um erro na análise
        """
        logger.info(f"Analisando vaga com Claude: {job_data.get('title', 'Sem título')}")

        try:
            # Extrai a descrição da vaga
            description = job_data.get('description', '')
            if not description:
                raise ValueError("Descrição da vaga está vazia")

            # Prepara os dados para o prompt
            input_data = {
                'title': job_data.get('title', 'Sem título'),
                'company': job_data.get('company', 'Empresa não especificada'),
                'description': description
            }

            # Gera o prompt para análise de vaga
            prompt = self.prompt_templates.get_job_analysis_prompt(input_data)

            # Envia a requisição
            system_prompt = "Você é um assistente especializado em análise de vagas de emprego. Sua tarefa é extrair informações estruturadas de descrições de vagas."
            response_text = self._send_request(prompt, system_prompt)

            # Processa a resposta para extrair o JSON
            result = self.response_parser.extract_json(response_text)

            if not result:
                logger.warning("Não foi possível extrair JSON da resposta do Claude")
                result = self._fallback_job_parsing(response_text)

            # Preserva os dados originais da vaga
            for key, value in job_data.items():
                if key not in result:
                    result[key] = value

            return result

        except Exception as e:
            logger.error(f"Erro ao analisar vaga com Claude: {str(e)}")
            raise

    def calculate_match(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula a correspondência entre um currículo e uma vaga.

        Args:
            resume_data: Dados do currículo analisado
            job_data: Dados da vaga analisada

        Returns:
            Dicionário com pontuação e detalhes da correspondência

        Raises:
            Exception: Se ocorrer um erro no cálculo
        """
        logger.info(f"Calculando correspondência entre currículo e vaga: {job_data.get('title', 'Sem título')}")

        try:
            # Gera o prompt para cálculo de correspondência
            prompt = self.prompt_templates.get_match_calculation_prompt(resume_data, job_data)

            # Envia a requisição
            system_prompt = "Você é um assistente especializado em recrutamento e seleção. Sua tarefa é avaliar o grau de compatibilidade entre um currículo e uma vaga de emprego."
            response_text = self._send_request(prompt, system_prompt)

            # Processa a resposta para extrair o JSON
            result = self.response_parser.extract_json(response_text)

            if not result:
                logger.warning("Não foi possível extrair JSON da resposta do Claude")
                result = self._fallback_match_parsing(response_text)

            # Verifica se a pontuação está presente e dentro do intervalo esperado
            if 'score_overall' not in result:
                result['score_overall'] = 0.0
            else:
                # Certifica-se de que a pontuação está entre 0 e 100
                score = float(result['score_overall'])
                if score > 1 and score <= 100:
                    # Já está na escala de 0-100
                    result['score_overall'] = score
                elif score >= 0 and score <= 1:
                    # Converte de 0-1 para 0-100
                    result['score_overall'] = score * 100
                else:
                    # Valor fora do intervalo esperado
                    result['score_overall'] = max(0, min(100, score))

            return result

        except Exception as e:
            logger.error(f"Erro ao calcular correspondência com Claude: {str(e)}")
            raise

    def generate_application_recommendations(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[
        str, Any]:
        """
        Gera recomendações personalizadas para melhorar uma candidatura.

        Args:
            resume_data: Dados do currículo analisado
            job_data: Dados da vaga analisada

        Returns:
            Dicionário com recomendações detalhadas

        Raises:
            Exception: Se ocorrer um erro na geração
        """
        logger.info(f"Gerando recomendações para candidatura: {job_data.get('title', 'Sem título')}")

        try:
            # Gera o prompt para recomendações
            prompt = self.prompt_templates.get_recommendations_prompt(resume_data, job_data)

            # Envia a requisição
            system_prompt = "Você é um especialista em carreira e recrutamento. Sua tarefa é fornecer recomendações detalhadas para melhorar a candidatura de uma pessoa a uma vaga específica."
            response_text = self._send_request(prompt, system_prompt, max_tokens=6000)

            # Processa a resposta para extrair o JSON
            result = self.response_parser.extract_json(response_text)

            if not result:
                # Se não conseguir extrair JSON, tenta estruturar a resposta em texto
                result = {
                    'recommendations': self.response_parser.structure_recommendations(response_text),
                    'raw_response': response_text
                }

            return result

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações com Claude: {str(e)}")
            raise

    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extrai habilidades técnicas e não-técnicas de um texto.

        Args:
            text: Texto a ser analisado

        Returns:
            Dicionário com habilidades técnicas e não-técnicas

        Raises:
            Exception: Se ocorrer um erro na extração
        """
        logger.info("Extraindo habilidades de texto com Claude")

        try:
            # Gera o prompt para extração de habilidades
            prompt = self.prompt_templates.get_skills_extraction_prompt(text)

            # Envia a requisição
            system_prompt = "Você é um assistente especializado na identificação de habilidades profissionais em textos. Sua tarefa é extrair habilidades técnicas e não-técnicas."
            response_text = self._send_request(prompt, system_prompt)

            # Processa a resposta para extrair o JSON
            result = self.response_parser.extract_json(response_text)

            if not result:
                logger.warning("Não foi possível extrair JSON da resposta do Claude")
                # Tenta uma abordagem alternativa
                skills = {'technical': [], 'soft': []}

                # Procura por listas no formato "- Skill"
                skill_lists = re.findall(r'(?:Technical|Hard|Soft|Non-technical) Skills:(?:\s*\n)*(.+?)(?:\n\n|\n*$)',
                                         response_text, re.DOTALL)

                for skill_list in skill_lists:
                    items = re.findall(r'[-*]\s*([^\n]+)', skill_list)
                    for item in items:
                        if 'technical' in skill_list.lower() or 'hard' in skill_list.lower():
                            skills['technical'].append(item.strip())
                        else:
                            skills['soft'].append(item.strip())

                return skills

            # Certifica-se de que o resultado tem a estrutura esperada
            if 'technical' not in result:
                result['technical'] = []
            if 'soft' not in result:
                result['soft'] = []

            return result

        except Exception as e:
            logger.error(f"Erro ao extrair habilidades com Claude: {str(e)}")
            # Retorna um resultado vazio em caso de erro
            return {'technical': [], 'soft': []}

    def summarize_job_description(self, description: str, max_length: int = 200) -> str:
        """
        Gera um resumo conciso de uma descrição de vaga.

        Args:
            description: Texto da descrição da vaga
            max_length: Comprimento máximo do resumo em caracteres

        Returns:
            Resumo da descrição da vaga

        Raises:
            Exception: Se ocorrer um erro na geração
        """
        logger.info("Gerando resumo de descrição de vaga com Claude")

        try:
            # Gera o prompt para resumo
            prompt = self.prompt_templates.get_summary_prompt(description, max_length)

            # Envia a requisição
            system_prompt = "Você é um assistente especializado em resumir textos de forma precisa e concisa."
            response_text = self._send_request(prompt, system_prompt, max_tokens=1000)

            # Remove possíveis citações ou aspas
            summary = response_text.strip('"\'')

            # Limita ao comprimento máximo
            if len(summary) > max_length:
                summary = summary[:max_length].rstrip() + "..."

            return summary

        except Exception as e:
            logger.error(f"Erro ao gerar resumo com Claude: {str(e)}")
            # Retorna um resumo simples em caso de erro
            if len(description) > max_length:
                return description[:max_length].rstrip() + "..."
            return description

    def _fallback_resume_parsing(self, response_text: str) -> Dict[str, Any]:
        """
        Método de fallback para parsear a resposta do Claude quando a extração de JSON falha.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com informações do currículo
        """
        result = {}

        # Tenta encontrar seções comuns no formato "Section: Content"
        sections = {
            'personal_info': ['Personal Information', 'Informações Pessoais'],
            'skills': ['Skills', 'Habilidades', 'Technical Skills', 'Soft Skills'],
            'experience': ['Experience', 'Work Experience', 'Professional Experience', 'Experiência'],
            'education': ['Education', 'Academic Background', 'Formação', 'Educação'],
            'languages': ['Languages', 'Idiomas']
        }

        for key, section_titles in sections.items():
            for title in section_titles:
                pattern = f"{title}:\\s*\\n(.+?)(?:\\n\\n|\\n[A-Z]|$)"
                matches = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    content = matches.group(1).strip()
                    if key == 'skills':
                        # Tenta extrair habilidades em formato de lista
                        skills = []
                        skill_items = re.findall(r'[-*]\s*([^\n]+)', content)
                        skills.extend([s.strip() for s in skill_items if s.strip()])

                        # Se não encontrar itens de lista, divide por vírgulas
                        if not skills:
                            skills = [s.strip() for s in content.split(',') if s.strip()]

                        result[key] = skills
                    else:
                        result[key] = content
                    break

        # Adiciona timestamp
        result['analyzed_at'] = datetime.utcnow().isoformat()

        return result

    def _fallback_job_parsing(self, response_text: str) -> Dict[str, Any]:
        """
        Método de fallback para parsear a resposta do Claude quando a extração de JSON falha.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com informações da vaga
        """
        result = {}

        # Tenta encontrar seções comuns no formato "Section: Content"
        sections = {
            'title': ['Title', 'Job Title', 'Título', 'Cargo'],
            'company': ['Company', 'Organization', 'Empresa', 'Organização'],
            'location': ['Location', 'Localização', 'Local'],
            'job_type': ['Job Type', 'Employment Type', 'Tipo de Contrato', 'Regime'],
            'experience_level': ['Experience Level', 'Nível de Experiência', 'Seniority'],
            'salary_range': ['Salary', 'Compensation', 'Salário', 'Remuneração'],
            'requirements': ['Requirements', 'Requisitos', 'Qualifications'],
            'skills': ['Skills', 'Habilidades', 'Required Skills']
        }

        for key, section_titles in sections.items():
            for title in section_titles:
                pattern = f"{title}:\\s*\\n?(.+?)(?:\\n\\n|\\n[A-Z]|$)"
                matches = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    content = matches.group(1).strip()
                    if key in ['requirements', 'skills']:
                        # Tenta extrair itens em formato de lista
                        items = []
                        list_items = re.findall(r'[-*]\s*([^\n]+)', content)
                        items.extend([s.strip() for s in list_items if s.strip()])

                        # Se não encontrar itens de lista, divide por vírgulas
                        if not items and key == 'skills':
                            items = [s.strip() for s in content.split(',') if s.strip()]

                        result[key] = items
                    else:
                        result[key] = content
                    break

        # Adiciona timestamp
        result['analyzed_at'] = datetime.utcnow().isoformat()

        return result

    def _fallback_match_parsing(self, response_text: str) -> Dict[str, Any]:
        """
        Método de fallback para parsear a resposta do Claude quando a extração de JSON falha.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com informações da correspondência
        """
        result = {
            'score_overall': 0.0,
            'score_details': {},
            'matching_skills': [],
            'missing_skills': [],
            'recommendations': []
        }

        # Tenta extrair a pontuação geral
        score_pattern = r'(?:Score|Pontuação|Compatibilidade|Compatibility|Match)[:\s]*(\d+(?:\.\d+)?)[%\s]*'
        score_match = re.search(score_pattern, response_text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            # Normaliza para 0-100
            if score <= 1:
                score *= 100
            result['score_overall'] = score

        # Tenta extrair habilidades correspondentes
        matching_pattern = r'(?:Matching Skills|Habilidades Correspondentes)[:\s]*\n(.+?)(?:\n\n|\n[A-Z]|$)'
        matching_match = re.search(matching_pattern, response_text, re.IGNORECASE | re.DOTALL)
        if matching_match:
            content = matching_match.group(1).strip()
            skills = []
            skill_items = re.findall(r'[-*]\s*([^\n]+)', content)
            skills.extend([s.strip() for s in skill_items if s.strip()])

            # Se não encontrar itens de lista, divide por vírgulas
            if not skills:
                skills = [s.strip() for s in content.split(',') if s.strip()]

            result['matching_skills'] = skills

        # Tenta extrair habilidades faltantes
        missing_pattern = r'(?:Missing Skills|Habilidades Faltantes)[:\s]*\n(.+?)(?:\n\n|\n[A-Z]|$)'
        missing_match = re.search(missing_pattern, response_text, re.IGNORECASE | re.DOTALL)
        if missing_match:
            content = missing_match.group(1).strip()
            skills = []
            skill_items = re.findall(r'[-*]\s*([^\n]+)', content)
            skills.extend([s.strip() for s in skill_items if s.strip()])

            # Se não encontrar itens de lista, divide por vírgulas
            if not skills:
                skills = [s.strip() for s in content.split(',') if s.strip()]

            result['missing_skills'] = skills

        # Tenta extrair recomendações
        recom_pattern = r'(?:Recommendations|Recomendações)[:\s]*\n(.+?)(?:\n\n|\n[A-Z]|$)'
        recom_match = re.search(recom_pattern, response_text, re.IGNORECASE | re.DOTALL)
        if recom_match:
            content = recom_match.group(1).strip()
            recommendations = []
            recom_items = re.findall(r'[-*]\s*([^\n]+)', content)
            recommendations.extend([s.strip() for s in recom_items if s.strip()])

            # Se não encontrar itens de lista, divide por parágrafos
            if not recommendations:
                recommendations = [s.strip() for s in content.split('\n') if s.strip()]

            result['recommendations'] = recommendations

        # Adiciona timestamp
        result['created_at'] = datetime.utcnow().isoformat()

        return result