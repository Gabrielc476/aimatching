"""
Serviço de scraping de posts do LinkedIn contendo vagas.

Este módulo contém a implementação do scraper especializado em coletar
posts do LinkedIn que contenham anúncios de vagas de emprego.
"""

import logging
import random
import time
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PostScraper:
    """
    Scraper especializado em coletar posts do LinkedIn contendo vagas.

    Esta classe implementa métodos para buscar e analisar posts
    que contenham anúncios de vagas de emprego.
    """

    def __init__(self, browser: webdriver.Chrome):
        """
        Inicializa o scraper de posts.

        Args:
            browser: Instância do navegador Chrome
        """
        self.browser = browser
        self.base_url = "https://www.linkedin.com/search/results/content/"

        # Lista de palavras-chave que indicam que um post contém vaga
        self.job_indicators = [
            "estamos contratando", "vaga aberta", "oportunidade de emprego",
            "processo seletivo", "we're hiring", "job opening", "job opportunity",
            "open position", "aplicar", "cadastre seu currículo", "envie seu cv",
            "candidate-se", "apply now", "submit your resume", "link na bio",
            "link in bio", "apply here", "enviar currículo para", "novo talento"
        ]

        # Expressões regulares para extrair informações de vagas
        self.re_salary = re.compile(r'(?:salário|remuneração|salary|pay)[\s:]*(R\$\s*[\d\.,]+|[\d\.,]+\s*(?:mil|k))')
        self.re_location = re.compile(r'(?:local|localização|location|cidade|city)[\s:]*([\w\s]+)(?:,|\.|\n|$)')
        self.re_job_type = re.compile(
            r'(?:regime|contrato|contract|job type)[\s:]*(CLT|PJ|Freelance|Tempo integral|Full[ -]time|Part[ -]time)')
        self.re_email = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    def scrape(
            self,
            keywords: Union[str, List[str]],
            days_back: int = 7,
            max_posts: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Realiza o scraping de posts contendo possíveis vagas.

        Args:
            keywords: Palavras-chave para busca
            days_back: Quantidade de dias para buscar para trás
            max_posts: Número máximo de posts para coletar

        Returns:
            Lista de posts encontrados contendo possíveis vagas
        """
        if isinstance(keywords, list):
            keywords = " OR ".join(keywords)

        # Adiciona os indicadores de vaga às palavras-chave
        job_keywords = keywords
        for indicator in self.job_indicators:
            job_keywords += f" OR \"{indicator}\""

        url = self._build_search_url(job_keywords, days_back)
        logger.info(f"Iniciando scraping de posts com URL: {url}")

        job_posts = []

        try:
            # Acessa a URL de busca
            self.browser.get(url)
            time.sleep(random.uniform(2, 4))

            # Espera os resultados carregarem
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results__list"))
                )
            except TimeoutException:
                logger.warning("Timeout ao esperar resultados de busca de posts")
                return job_posts

            # Extrai os posts e realiza scroll até atingir o número máximo
            posts_collected = 0
            last_height = self.browser.execute_script("return document.body.scrollHeight")

            while posts_collected < max_posts:
                # Extrai os posts visíveis na página
                new_posts = self._extract_posts()

                for post in new_posts:
                    if post not in job_posts:  # Evita duplicatas
                        # Verifica se o post contém indicadores de vaga
                        if self._is_job_post(post):
                            job_posts.append(post)
                            posts_collected += 1

                            if posts_collected >= max_posts:
                                break

                if posts_collected >= max_posts:
                    break

                # Scroll down para carregar mais posts
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 3))

                # Verifica se chegou ao final da página
                new_height = self.browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # Tenta clicar em "Ver mais" se existir
                    try:
                        load_more = self.browser.find_element(By.CSS_SELECTOR,
                                                              ".artdeco-button.search-results__pagination-button")
                        load_more.click()
                        time.sleep(random.uniform(2, 4))
                    except (NoSuchElementException, ElementClickInterceptedException):
                        break  # Não há mais posts para carregar

                last_height = new_height

            logger.info(f"Scraping de posts concluído. Total de posts encontrados: {len(job_posts)}")
            return job_posts

        except Exception as e:
            logger.error(f"Erro durante o scraping de posts: {str(e)}")
            return job_posts

    def parse_job_from_post(self, post_content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extrai informações de vaga a partir do conteúdo de um post.

        Args:
            post_content: Dicionário contendo o conteúdo do post

        Returns:
            Dicionário com informações da vaga ou None se não for uma vaga
        """
        try:
            if not post_content or not post_content.get('text'):
                return None

            # Verifica novamente se é um post de vaga
            if not self._is_job_post(post_content):
                return None

            text = post_content['text']

            # Inicializa o dicionário de vaga
            job = {
                'linkedin_id': f"post_{post_content.get('id', '')}",
                'url': post_content.get('url', ''),
                'company': post_content.get('author_company', ''),
                'posted_at': post_content.get('date', datetime.utcnow().isoformat()),
                'description': text,
                'scraped_at': datetime.utcnow().isoformat(),
                'is_active': True,
                'source_type': 'post'
            }

            # Extrai o título da vaga
            job['title'] = self._extract_job_title(text)

            # Extrai a localização
            location_match = self.re_location.search(text)
            if location_match:
                job['location'] = location_match.group(1).strip()
            else:
                # Tenta encontrar cidades brasileiras comuns no texto
                cities = ["São Paulo", "Rio de Janeiro", "Brasília", "Belo Horizonte",
                          "Salvador", "Curitiba", "Recife", "Porto Alegre", "Manaus",
                          "Campinas", "Goiânia", "Florianópolis", "Vitória", "Santos"]

                for city in cities:
                    if city in text:
                        job['location'] = city
                        break
                else:
                    # Caso não encontre, verifica se há indicação de remoto
                    if re.search(r'\b(remoto|remota|remote|home office|trabalho remoto|anywhere)\b', text,
                                 re.IGNORECASE):
                        job['location'] = 'Remoto'
                    else:
                        job['location'] = 'Não especificado'

            # Extrai a faixa salarial
            salary_match = self.re_salary.search(text)
            if salary_match:
                job['salary_range'] = salary_match.group(1).strip()
            else:
                job['salary_range'] = None

            # Extrai o tipo de emprego
            job_type_match = self.re_job_type.search(text)
            if job_type_match:
                job['job_type'] = job_type_match.group(1).strip()
            else:
                # Tenta identificar padrões comuns
                job_types = {
                    'CLT': ['clt', 'carteira assinada', 'regime clt', 'efetivo'],
                    'PJ': ['pj', 'pessoa jurídica', 'regime pj', 'cnpj'],
                    'Freelance': ['freelance', 'freela', 'projeto', 'temporário'],
                    'Estágio': ['estágio', 'estagiário', 'trainee', 'estudante'],
                    'Tempo integral': ['tempo integral', 'full time', 'full-time', '40h', '44h'],
                    'Meio período': ['meio período', 'part time', 'part-time', '20h', '30h']
                }

                for job_type, keywords in job_types.items():
                    if any(keyword in text.lower() for keyword in keywords):
                        job['job_type'] = job_type
                        break
                else:
                    job['job_type'] = 'Não especificado'

            # Extrai o nível de experiência
            experience_patterns = {
                'Estágio': ['estágio', 'estagiário', 'trainee', 'estudante'],
                'Júnior': ['júnior', 'junior', 'jr', 'jr.', 'iniciante'],
                'Pleno': ['pleno', 'mid-level', 'intermediário'],
                'Sênior': ['sênior', 'senior', 'sr', 'sr.', 'especialista'],
                'Gerente': ['gerente', 'manager', 'coordenador', 'líder', 'gestor']
            }

            for level, keywords in experience_patterns.items():
                if any(keyword in text.lower() for keyword in keywords):
                    job['experience_level'] = level
                    break
            else:
                job['experience_level'] = 'Não especificado'

            # Extrai possíveis habilidades do texto
            job['skills'] = self._extract_skills_from_text(text)

            # Extrai requisitos (trechos que começam com marcadores)
            job['requirements'] = self._extract_requirements_from_text(text)

            # Extrai um possível email de contato
            email_match = self.re_email.search(text)
            if email_match:
                job['contact_email'] = email_match.group(0)
            else:
                job['contact_email'] = None

            return job

        except Exception as e:
            logger.error(f"Erro ao extrair informações de vaga do post: {str(e)}")
            return None

    def _build_search_url(self, keywords: str, days_back: int) -> str:
        """
        Constrói a URL de busca de posts com os parâmetros especificados.

        Args:
            keywords: Palavras-chave para busca
            days_back: Quantidade de dias para buscar para trás

        Returns:
            URL formatada para busca de posts
        """
        date_filter = ""
        if days_back > 0:
            # Mapeamento de filtros de data do LinkedIn
            if days_back <= 1:
                date_filter = "past-24h"
            elif days_back <= 7:
                date_filter = "past-week"
            elif days_back <= 30:
                date_filter = "past-month"
            else:
                date_filter = "past-year"

        params = {
            'keywords': keywords,
            'sortBy': 'date_posted',
            'origin': 'GLOBAL_SEARCH_HEADER'
        }

        if date_filter:
            params['datePosted'] = date_filter

        # Constrói a URL com os parâmetros
        return f"{self.base_url}?{urlencode(params)}"

    def _extract_posts(self) -> List[Dict[str, Any]]:
        """
        Extrai os posts visíveis na página atual.

        Returns:
            Lista de dicionários com informações dos posts
        """
        posts = []

        try:
            # Obtém todos os posts na página
            post_elements = self.browser.find_elements(By.CSS_SELECTOR, ".search-results__list .feed-shared-update-v2")

            for post_element in post_elements:
                try:
                    post_data = {}

                    # Obtém o ID do post
                    try:
                        post_id = post_element.get_attribute('data-urn').split(':')[-1]
                        post_data['id'] = post_id
                    except:
                        post_data['id'] = f"post_{len(posts)}"

                    # Obtém o link do post
                    try:
                        post_link = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2__meta-wrapper a")
                        post_data['url'] = post_link.get_attribute('href')
                    except NoSuchElementException:
                        post_data['url'] = f"https://www.linkedin.com/feed/update/{post_data['id']}"

                    # Obtém o autor do post
                    try:
                        author_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-actor__name")
                        post_data['author'] = author_element.text.strip()
                    except NoSuchElementException:
                        post_data['author'] = "Autor desconhecido"

                    # Obtém a empresa do autor (se disponível)
                    try:
                        company_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-actor__description")
                        post_data['author_company'] = company_element.text.strip()
                    except NoSuchElementException:
                        post_data['author_company'] = None

                    # Obtém a data do post
                    try:
                        date_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-actor__sub-description")
                        date_text = date_element.text.strip()
                        post_data['date'] = self._parse_relative_date(date_text)
                    except NoSuchElementException:
                        post_data['date'] = datetime.utcnow().isoformat()

                    # Obtém o texto do post
                    try:
                        text_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2__description")
                        post_data['text'] = text_element.text.strip()

                        # Tenta expandir o texto se houver "ver mais"
                        try:
                            see_more = text_element.find_element(By.CSS_SELECTOR,
                                                                 ".feed-shared-inline-show-more-text__see-more-link")
                            see_more.click()
                            time.sleep(0.5)
                            # Obtém o texto expandido
                            post_data['text'] = text_element.text.strip()
                        except NoSuchElementException:
                            pass

                    except NoSuchElementException:
                        post_data['text'] = ""

                    # Obtém as imagens do post (se houver)
                    try:
                        image_elements = post_element.find_elements(By.CSS_SELECTOR, ".feed-shared-image__image")
                        post_data['images'] = [img.get_attribute('src') for img in image_elements if
                                               img.get_attribute('src')]
                    except:
                        post_data['images'] = []

                    # Obtém os links no post (se houver)
                    try:
                        link_elements = post_element.find_elements(By.CSS_SELECTOR, ".feed-shared-text a")
                        post_data['links'] = [link.get_attribute('href') for link in link_elements if
                                              link.get_attribute('href')]
                    except:
                        post_data['links'] = []

                    posts.append(post_data)

                except (NoSuchElementException, StaleElementReferenceException) as e:
                    logger.warning(f"Erro ao extrair post individual: {str(e)}")
                    continue

            return posts

        except Exception as e:
            logger.error(f"Erro ao extrair posts: {str(e)}")
            return posts

    def _is_job_post(self, post: Dict[str, Any]) -> bool:
        """
        Verifica se um post contém um anúncio de vaga.

        Args:
            post: Dicionário contendo informações do post

        Returns:
            True se o post contém um anúncio de vaga, False caso contrário
        """
        if not post or not post.get('text'):
            return False

        text = post['text'].lower()

        # Verifica se o texto contém indicadores de vaga
        for indicator in self.job_indicators:
            if indicator.lower() in text:
                return True

        # Verifica padrões comuns em títulos de vagas
        job_title_patterns = [
            r'\b(contrata(?:-se)?|estamos contratando)\b',
            r'\b(vaga|oportunidade)(?:\s+de)?\s+(emprego|trabalho)\b',
            r'\bopen(?:ing)?\s+(?:for|position)\b',
            r'\bwe\'re\s+(?:hiring|looking)\b',
            r'\bjob\s+(?:opening|opportunity|position)\b',
            r'\b(?:novo|nova)\s+(?:vaga|oportunidade)\b'
        ]

        for pattern in job_title_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Verifica se há menção a envio de currículo
        cv_patterns = [
            r'(?:envie|enviar|mande)[\s\w]*(?:cv|curriculo|currículo)',
            r'(?:submit|send)[\s\w]*(?:cv|resume|application)',
            r'curriculo(?:s)?\s+para\s+(?:o\s+)?e-?mail',
            r'resumes?\s+to\s+(?:the\s+)?e-?mail'
        ]

        for pattern in cv_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _extract_job_title(self, text: str) -> str:
        """
        Extrai o título da vaga a partir do texto do post.

        Args:
            text: Texto do post

        Returns:
            Título da vaga ou string genérica se não for encontrado
        """
        # Padrões comuns para títulos de vagas
        title_patterns = [
            r'(?:vaga|oportunidade)(?:\s+de|\s+para)?\s+([\w\s\-\./]+?)(?:\s+(?:para|em|na|no|@)|\s*[,:\.]|$)',
            r'(?:contratando|contrata(?:-se)?)(?:\s+(?:para|de))?\s+([\w\s\-\./]+?)(?:\s+(?:para|em|na|no|@)|\s*[,:\.]|$)',
            r'(?:estamos\s+)?(?:com\s+vaga\s+(?:aberta|disponível)\s+(?:para|de))?\s+([\w\s\-\./]+?)(?:\s+(?:para|em|na|no|@)|\s*[,:\.]|$)',
            r'(?:job\s+opening|we\'re\s+hiring)(?:\s+(?:for|a))?\s+([\w\s\-\./]+?)(?:\s+(?:at|in|for)|\s*[,:\.]|$)'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Limita o tamanho do título
                if len(title) > 5 and len(title) < 100:
                    return title.capitalize()

        # Verifica linhas que começam com formato de título
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Procura por linhas curtas que podem ser títulos
            if 5 < len(line) < 60 and ':' not in line:
                words = line.split()
                if 1 < len(words) < 8:
                    # Verifica se a linha contém palavras-chave comuns em títulos
                    title_keywords = ['desenvolvedor', 'analista', 'gerente', 'coordenador', 'especialista',
                                      'engenheiro', 'designer', 'assistente', 'consultor', 'programador',
                                      'developer', 'analyst', 'manager', 'coordinator', 'specialist',
                                      'engineer', 'assistant', 'consultant', 'programmer']

                    if any(keyword in line.lower() for keyword in title_keywords):
                        return line.capitalize()

        # Se não encontrar um padrão específico, tenta determinar com base no conteúdo
        text_lower = text.lower()

        # Lista de possíveis cargos
        job_roles = [
            "desenvolvedor", "programador", "engenheiro", "analista", "designer",
            "gerente", "coordenador", "diretor", "técnico", "consultor", "especialista",
            "assistente", "atendente", "vendedor", "representante", "supervisor"
        ]

        # Lista de possíveis áreas/tecnologias
        areas = [
            "front-end", "back-end", "full stack", "web", "mobile", "ios", "android",
            "python", "java", "javascript", "react", "angular", "node", "php", ".net",
            "dados", "marketing", "vendas", "rh", "recursos humanos", "ti", "suporte",
            "administrativo", "financeiro", "contábil", "jurídico", "comercial"
        ]

        # Tenta construir um título baseado no conteúdo
        for role in job_roles:
            if role in text_lower:
                for area in areas:
                    if area in text_lower:
                        return f"{role.capitalize()} {area}"
                return f"{role.capitalize()}"

        # Se não encontrar nada específico, retorna um título genérico
        return "Vaga de Emprego"

    def _parse_relative_date(self, date_text: str) -> str:
        """
        Converte uma data relativa (ex: "há 2 dias") para timestamp.

        Args:
            date_text: Texto contendo a data relativa

        Returns:
            String ISO 8601 representando a data
        """
        try:
            now = datetime.utcnow()

            # Expressões regulares para diferentes formatos de data
            hour_pattern = r'(\d+)\s*h(?:ora)?'
            day_pattern = r'(\d+)\s*d(?:ia)?'
            week_pattern = r'(\d+)\s*sem(?:ana)?'
            month_pattern = r'(\d+)\s*m[êe]s'

            # Versões em inglês
            hour_pattern_en = r'(\d+)\s*hour'
            day_pattern_en = r'(\d+)\s*day'
            week_pattern_en = r'(\d+)\s*week'
            month_pattern_en = r'(\d+)\s*month'

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

            # Se for "1h" ou similar sem "há"
            elif "1h" in date_text or "1 h" in date_text:
                return (now - timedelta(hours=1)).isoformat()
            elif "1d" in date_text or "1 d" in date_text:
                return (now - timedelta(days=1)).isoformat()
            elif "1sem" in date_text or "1 sem" in date_text:
                return (now - timedelta(weeks=1)).isoformat()
            elif "1mês" in date_text or "1 mês" in date_text:
                return (now - timedelta(days=30)).isoformat()

            # Se for "hoje" ou "yesterday"
            elif "hoje" in date_text.lower() or "today" in date_text.lower():
                return now.isoformat()
            elif "ontem" in date_text.lower() or "yesterday" in date_text.lower():
                return (now - timedelta(days=1)).isoformat()

            # Se não conseguir parsear, retorna a data atual
            return now.isoformat()

        except Exception as e:
            logger.error(f"Erro ao parsear data relativa '{date_text}': {str(e)}")
            return datetime.utcnow().isoformat()

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extrai possíveis habilidades do texto do post.

        Args:
            text: Texto do post

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
        text_lower = text.lower()

        # Encontra as habilidades no texto
        found_skills = []
        for skill in common_skills:
            if skill in text_lower:
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

    def _extract_requirements_from_text(self, text: str) -> List[str]:
        """
        Extrai requisitos do texto do post.

        Args:
            text: Texto do post

        Returns:
            Lista de requisitos extraídos
        """
        requirements = []

        # Divide o texto em linhas
        lines = text.split('\n')

        # Identifica seções de requisitos
        requirement_section = False

        for line in lines:
            line = line.strip()

            # Pula linhas vazias
            if not line:
                continue

            # Verifica se estamos entrando em uma seção de requisitos
            if re.search(r'\b(requisitos|requirements|qualifica[çc][õo]es|perfil|buscamos|procuramos|precisa ter)\b',
                         line.lower()):
                requirement_section = True
                continue

            # Verifica se estamos saindo de uma seção de requisitos
            if requirement_section and re.search(
                    r'\b(benef[íi]cios|sal[áa]rio|contrata[çc][ãa]o|oferecemos|enviar curr[íi]culo)\b', line.lower()):
                requirement_section = False
                continue

            # Se estamos em uma seção de requisitos, verifica se a linha é um requisito
            if requirement_section:
                # Procura por linhas que começam com marcadores ou números
                if line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line):
                    # Remove o marcador e espaços
                    cleaned_line = re.sub(r'^[-•*\d\.]+\s*', '', line).strip()
                    if cleaned_line:
                        requirements.append(cleaned_line)

        # Se não encontrou requisitos específicos, procura por linhas com marcadores em todo o texto
        if not requirements:
            for line in lines:
                line = line.strip()
                if (line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.',
                                                                                                     line)) and len(
                        line) > 10:
                    cleaned_line = re.sub(r'^[-•*\d\.]+\s*', '', line).strip()
                    if cleaned_line:
                        requirements.append(cleaned_line)

        return requirements