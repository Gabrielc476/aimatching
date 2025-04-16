"""
Serviço de scraping de listagens de vagas do LinkedIn.

Este módulo contém a implementação do scraper especializado em coletar
vagas das páginas de listagem oficiais do LinkedIn.
"""

import logging
import random
import time
import re
import json
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ListingScraper:
    """
    Scraper especializado em coletar vagas das páginas de listagem do LinkedIn.

    Esta classe implementa métodos para navegar pelas páginas de resultados
    de busca de vagas e extrair informações detalhadas.
    """

    def __init__(self, browser: webdriver.Chrome):
        """
        Inicializa o scraper de listagens.

        Args:
            browser: Instância do navegador Chrome
        """
        self.browser = browser
        self.base_url = "https://www.linkedin.com/jobs/search"

    def scrape(
            self,
            keywords: Union[str, List[str]],
            location: str = "",
            filters: Optional[Dict[str, Any]] = None,
            pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Realiza o scraping de listagens de vagas.

        Args:
            keywords: Palavra(s)-chave para busca
            location: Localização da vaga
            filters: Filtros adicionais (experiência, data de postagem, etc.)
            pages: Número de páginas para coletar

        Returns:
            Lista de vagas encontradas
        """
        if isinstance(keywords, list):
            keywords = " ".join(keywords)

        url = self._build_search_url(keywords, location, filters)
        logger.info(f"Iniciando scraping de vagas com URL: {url}")

        job_listings = []
        current_page = 1

        try:
            # Acessa a URL de busca
            self.browser.get(url)
            time.sleep(random.uniform(2, 4))

            # Loop através das páginas
            while current_page <= pages:
                logger.info(f"Processando página {current_page} de {pages}")

                # Espera os resultados carregarem
                try:
                    WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list"))
                    )
                except TimeoutException:
                    logger.warning("Timeout ao esperar resultados de busca")
                    break

                # Adiciona um delay aleatório para simular comportamento humano
                time.sleep(random.uniform(2, 4))

                # Extrai os cartões de vaga da página atual
                job_cards = self._extract_job_cards()
                if not job_cards:
                    logger.warning("Nenhum cartão de vaga encontrado na página")
                    break

                job_listings.extend(job_cards)
                logger.info(f"Extraídos {len(job_cards)} cartões de vaga da página {current_page}")

                # Vai para a próxima página se não for a última
                if current_page < pages:
                    if not self._go_to_next_page():
                        logger.info("Não há mais páginas disponíveis")
                        break
                    current_page += 1
                else:
                    break

            logger.info(f"Scraping concluído. Total de vagas encontradas: {len(job_listings)}")
            return job_listings

        except Exception as e:
            logger.error(f"Erro durante o scraping de vagas: {str(e)}")
            return job_listings

    def extract_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrai detalhes completos de uma vaga específica.

        Args:
            job_url: URL da vaga no LinkedIn

        Returns:
            Dicionário com detalhes da vaga ou None em caso de erro
        """
        try:
            logger.info(f"Extraindo detalhes da vaga: {job_url}")

            # Navega para a URL da vaga
            self.browser.get(job_url)
            time.sleep(random.uniform(2, 4))

            # Espera a página de detalhes carregar
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobs-description"))
                )
            except TimeoutException:
                logger.warning("Timeout ao esperar detalhes da vaga")
                return None

            # Obtém a ID da vaga a partir da URL
            linkedin_id = job_url.split('/')[-1].split('?')[0]

            # Extrai as informações básicas
            job_details = {}

            try:
                job_details['linkedin_id'] = linkedin_id
                job_details['url'] = job_url

                # Título da vaga
                title_element = self.browser.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__job-title")
                job_details['title'] = title_element.text.strip()

                # Empresa
                company_element = self.browser.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__company-name")
                job_details['company'] = company_element.text.strip()

                # Localização
                location_element = self.browser.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__bullet")
                job_details['location'] = location_element.text.strip()

                # Data de postagem (formato relativo, como "há 3 dias")
                try:
                    posted_element = self.browser.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__posted-date")
                    posted_text = posted_element.text.strip()
                    job_details['posted_at'] = self._parse_relative_date(posted_text)
                except NoSuchElementException:
                    job_details['posted_at'] = None

                # Descrição completa da vaga
                description_element = self.browser.find_element(By.CSS_SELECTOR, ".jobs-description-content__text")
                job_details['description'] = description_element.text.strip()

                # Nível de experiência, tipo de emprego, etc.
                criteria_elements = self.browser.find_elements(By.CSS_SELECTOR, ".jobs-description-details__list-item")
                for element in criteria_elements:
                    label = element.find_element(By.CSS_SELECTOR,
                                                 ".jobs-description-details__list-item-label").text.strip()
                    value = element.find_element(By.CSS_SELECTOR,
                                                 ".jobs-description-details__list-item-value").text.strip()

                    # Mapeamento de rótulos para campos do modelo
                    if "Nível de experiência" in label or "Experience level" in label:
                        job_details['experience_level'] = value
                    elif "Tipo de emprego" in label or "Employment type" in label:
                        job_details['job_type'] = value
                    elif "Função" in label or "Job function" in label:
                        job_details['job_function'] = value
                    elif "Setores" in label or "Industries" in label:
                        job_details['industry'] = value

                # Obtém requisitos e habilidades
                requirements = []
                skills = []

                # Tenta extrair habilidades do bloco específico, se existir
                try:
                    skills_elements = self.browser.find_elements(By.CSS_SELECTOR,
                                                                 ".job-details-skill-match-status-list__skill-entity")
                    for skill_element in skills_elements:
                        skills.append(skill_element.text.strip())
                except Exception:
                    # Se não encontrar o bloco específico, tenta extrair da descrição
                    skills = self._extract_skills_from_description(job_details['description'])

                # Extrai requisitos da descrição
                requirements = self._extract_requirements_from_description(job_details['description'])

                job_details['requirements'] = requirements
                job_details['skills'] = skills

                # Tenta extrair faixa salarial, se disponível
                try:
                    salary_element = self.browser.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__salary-range")
                    job_details['salary_range'] = salary_element.text.strip()
                except NoSuchElementException:
                    job_details['salary_range'] = None

                # Adiciona timestamp de scraping
                job_details['scraped_at'] = datetime.utcnow().isoformat()

                logger.info(
                    f"Detalhes da vaga extraídos com sucesso: {job_details['title']} at {job_details['company']}")
                return job_details

            except NoSuchElementException as e:
                logger.error(f"Elemento não encontrado ao extrair detalhes da vaga: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Erro ao extrair detalhes da vaga: {str(e)}")
            return None

    def _build_search_url(
            self,
            keywords: str,
            location: str,
            filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Constrói a URL de busca de vagas com os parâmetros especificados.

        Args:
            keywords: Palavras-chave para busca
            location: Localização da vaga
            filters: Filtros adicionais

        Returns:
            URL formatada para busca de vagas
        """
        params = {
            'keywords': keywords,
            'sortBy': 'R'  # Relevância (R) como padrão
        }

        if location:
            params['location'] = location

        # Adiciona filtros adicionais, se fornecidos
        if filters:
            for key, value in filters.items():
                # Mapeamento de chaves amigáveis para parâmetros do LinkedIn
                param_map = {
                    'date_posted': 'f_TPR',
                    'experience': 'f_E',
                    'job_type': 'f_JT',
                    'remote': 'f_WT',
                    'industry': 'f_I',
                    'company': 'f_C',
                    'distance': 'distance'
                }

                if key in param_map:
                    params[param_map[key]] = value

        # Constrói a URL com os parâmetros
        return f"{self.base_url}?{urlencode(params)}"

    def _extract_job_cards(self) -> List[Dict[str, Any]]:
        """
        Extrai informações básicas dos cartões de vaga na página atual.

        Returns:
            Lista de dicionários com informações básicas das vagas
        """
        job_cards = []

        try:
            # Obtem todos os cartões de vaga na página
            cards = self.browser.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")

            for card in cards:
                try:
                    # Para cada cartão, tenta extrair as informações básicas
                    job_data = {}

                    # Obtém o link e a ID da vaga
                    job_link_element = card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                    job_data['url'] = job_link_element.get_attribute('href')
                    job_data['linkedin_id'] = job_data['url'].split('/')[-1].split('?')[0]

                    # Título da vaga
                    title_element = card.find_element(By.CSS_SELECTOR, ".job-card-list__title")
                    job_data['title'] = title_element.text.strip()

                    # Empresa
                    company_element = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name")
                    job_data['company'] = company_element.text.strip()

                    # Localização
                    location_element = card.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-item")
                    job_data['location'] = location_element.text.strip()

                    # Data de postagem (se disponível)
                    try:
                        date_element = card.find_element(By.CSS_SELECTOR, ".job-card-container__listed-time")
                        date_text = date_element.text.strip()
                        job_data['posted_at'] = self._parse_relative_date(date_text)
                    except NoSuchElementException:
                        job_data['posted_at'] = None

                    # Adiciona timestamp de scraping
                    job_data['scraped_at'] = datetime.utcnow().isoformat()

                    # Marca a vaga como ativa
                    job_data['is_active'] = True

                    job_cards.append(job_data)

                except (NoSuchElementException, StaleElementReferenceException) as e:
                    logger.warning(f"Erro ao extrair cartão de vaga individual: {str(e)}")
                    continue

            return job_cards

        except Exception as e:
            logger.error(f"Erro ao extrair cartões de vaga: {str(e)}")
            return job_cards

    def _go_to_next_page(self) -> bool:
        """
        Navega para a próxima página de resultados.

        Returns:
            True se navegou com sucesso, False caso contrário
        """
        try:
            # Tenta encontrar o botão de próxima página
            next_button = self.browser.find_element(By.CSS_SELECTOR, "button[aria-label='Próxima']")

            # Verifica se o botão está desabilitado
            if next_button.get_attribute('disabled'):
                return False

            # Clica no botão
            next_button.click()

            # Espera a página carregar
            time.sleep(random.uniform(2, 4))

            # Espera que o spinner de carregamento desapareça
            try:
                WebDriverWait(self.browser, 10).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results__list-loading-indicator"))
                )
            except TimeoutException:
                # Mesmo com timeout, continuamos pois a página pode ter carregado
                pass

            return True

        except NoSuchElementException:
            # Tentativa alternativa: procurar pelo número da página atual
            try:
                pagination = self.browser.find_element(By.CSS_SELECTOR, ".artdeco-pagination__pages")
                page_buttons = pagination.find_elements(By.TAG_NAME, "button")

                # Encontra o botão da página atual
                current_page = None
                for button in page_buttons:
                    if "active" in button.get_attribute("class"):
                        current_page = int(button.text.strip())
                        break

                if current_page is None:
                    return False

                # Tenta clicar no botão da próxima página
                for button in page_buttons:
                    if button.text.strip().isdigit() and int(button.text.strip()) == current_page + 1:
                        button.click()
                        time.sleep(random.uniform(2, 4))
                        return True

                return False

            except Exception:
                return False
        except Exception as e:
            logger.error(f"Erro ao navegar para a próxima página: {str(e)}")
            return False

    def _parse_relative_date(self, date_text: str) -> Optional[str]:
        """
        Converte uma data relativa (ex: "há 2 dias") para timestamp.

        Args:
            date_text: Texto contendo a data relativa

        Returns:
            String ISO 8601 representando a data ou None se não for possível parsear
        """
        try:
            now = datetime.utcnow()

            # Expressões regulares para diferentes formatos de data
            hour_pattern = r'há (\d+) hora'
            day_pattern = r'há (\d+) dia'
            week_pattern = r'há (\d+) semana'
            month_pattern = r'há (\d+) m[êe]s'

            # Versões em inglês
            hour_pattern_en = r'(\d+) hour'
            day_pattern_en = r'(\d+) day'
            week_pattern_en = r'(\d+) week'
            month_pattern_en = r'(\d+) month'

            # Verificar cada padrão
            if re.search(hour_pattern, date_text) or re.search(hour_pattern_en, date_text):
                match = re.search(hour_pattern, date_text) or re.search(hour_pattern_en, date_text)
                hours = int(match.group(1))
                return (now - timedelta(hours=hours)).isoformat()

            elif re.search(day_pattern, date_text) or re.search(day_pattern_en, date_text):
                match = re.search(day_pattern, date_text) or re.search(day_pattern_en, date_text)
                days = int(match.group(1))
                return (now - timedelta(days=days)).isoformat()

            elif re.search(week_pattern, date_text) or re.search(week_pattern_en, date_text):
                match = re.search(week_pattern, date_text) or re.search(week_pattern_en, date_text)
                weeks = int(match.group(1))
                return (now - timedelta(weeks=weeks)).isoformat()

            elif re.search(month_pattern, date_text) or re.search(month_pattern_en, date_text):
                match = re.search(month_pattern, date_text) or re.search(month_pattern_en, date_text)
                months = int(match.group(1))
                # Aproximação de um mês como 30 dias
                return (now - timedelta(days=30 * months)).isoformat()

            # Se for "há 1 hora" ou similar sem número
            elif "há 1 hora" in date_text or "1 hour ago" in date_text:
                return (now - timedelta(hours=1)).isoformat()
            elif "há 1 dia" in date_text or "1 day ago" in date_text:
                return (now - timedelta(days=1)).isoformat()
            elif "há 1 semana" in date_text or "1 week ago" in date_text:
                return (now - timedelta(weeks=1)).isoformat()
            elif "há 1 mês" in date_text or "1 month ago" in date_text:
                return (now - timedelta(days=30)).isoformat()

            # Se for "hoje" ou "yesterday"
            elif "hoje" in date_text.lower() or "today" in date_text.lower():
                return now.isoformat()
            elif "ontem" in date_text.lower() or "yesterday" in date_text.lower():
                return (now - timedelta(days=1)).isoformat()

            return None

        except Exception as e:
            logger.error(f"Erro ao parsear data relativa '{date_text}': {str(e)}")
            return None

    def _extract_skills_from_description(self, description: str) -> List[str]:
        """
        Extrai possíveis habilidades da descrição da vaga.

        Args:
            description: Texto da descrição da vaga

        Returns:
            Lista de habilidades extraídas
        """
        # Aqui poderíamos implementar uma extração mais sofisticada usando NLP,
        # mas por enquanto usaremos uma abordagem simples baseada em palavras-chave comuns

        common_skills = [
            "python", "java", "javascript", "js", "html", "css", "react",
            "angular", "vue", "node", "nodejs", "sql", "nosql", "mongodb",
            "postgresql", "mysql", "oracle", "aws", "azure", "gcp", "docker",
            "kubernetes", "git", "devops", "agile", "scrum", "kanban",
            "machine learning", "ml", "ai", "data science", "data analysis",
            "excel", "powerbi", "tableau", "power bi", "marketing", "seo",
            "sem", "social media", "design", "ui", "ux", "photoshop",
            "illustrator", "indesign", "figma", "sketch", "adobe",
            "project management", "jira", "confluence", "salesforce",
            "communication", "teamwork", "leadership", "problem solving",
            "critical thinking", "analytical", "detail-oriented", "creativity",
            "time management", "organization", "adaptability", "flexibility"
        ]

        # Normaliza o texto para comparação
        desc_lower = description.lower()

        # Encontra as habilidades no texto
        found_skills = []
        for skill in common_skills:
            if skill in desc_lower:
                # Evita duplicatas que sejam abreviações
                # (ex: evita adicionar "js" se "javascript" já foi adicionado)
                is_duplicate = False
                for found in found_skills:
                    if skill in found or found in skill:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    found_skills.append(skill)

        return found_skills

    def _extract_requirements_from_description(self, description: str) -> List[str]:
        """
        Extrai requisitos da descrição da vaga.

        Args:
            description: Texto da descrição da vaga

        Returns:
            Lista de requisitos extraídos
        """
        # Procura por seções comuns que contêm requisitos
        requirement_sections = [
            "Requisitos", "Requirements", "Qualificações", "Qualifications",
            "O que buscamos", "What we're looking for", "Perfil desejado",
            "Desired profile", "Experiência", "Experience"
        ]

        # Divide a descrição em linhas
        lines = description.split('\n')

        requirements = []
        in_requirements_section = False

        for line in lines:
            line = line.strip()

            # Pula linhas vazias
            if not line:
                continue

            # Verifica se estamos entrando em uma seção de requisitos
            for section in requirement_sections:
                if section in line and len(line) < 50:  # Evita falsos positivos em linhas longas
                    in_requirements_section = True
                    break

            # Se estamos em uma seção de requisitos, verifica se a linha contém um requisito
            if in_requirements_section:
                # Procura por linhas que começam com marcadores ou números
                if line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
                    # Remove o marcador e espaços
                    cleaned_line = re.sub(r'^[-•\d\.]+\s*', '', line).strip()
                    if cleaned_line:
                        requirements.append(cleaned_line)

                # Verifica se saímos da seção de requisitos
                if line.startswith('Benefícios') or line.startswith('Benefits') or line.startswith('Sobre '):
                    in_requirements_section = False

        # Se não encontrou requisitos específicos, tenta extrair de listas gerais na descrição
        if not requirements:
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
                    cleaned_line = re.sub(r'^[-•\d\.]+\s*', '', line).strip()
                    if cleaned_line and len(cleaned_line) > 15:  # Filtra itens muito curtos
                        requirements.append(cleaned_line)

        return requirements