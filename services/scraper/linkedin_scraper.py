"""
Serviço principal de scraping do LinkedIn.

Este módulo contém a classe principal que coordena o scraping de vagas
do LinkedIn, tanto através de listagens oficiais quanto de posts.
"""

import logging
import random
import time
from typing import Dict, List, Optional, Any, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

from .listing_scraper import ListingScraper
from .post_scraper import PostScraper
from .proxy_manager import ProxyManager
from .user_agent_manager import UserAgentManager

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """
    Classe principal para scraping de vagas no LinkedIn.

    Esta classe coordena o scraping de vagas do LinkedIn usando diferentes
    abordagens, gerencia a configuração do navegador e implementa técnicas
    para evitar bloqueios.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o scraper com a configuração necessária.

        Args:
            config: Dicionário de configuração contendo:
                - linkedin_username: Nome de usuário do LinkedIn
                - linkedin_password: Senha do LinkedIn
                - chromedriver_path: Caminho para o executável do ChromeDriver
                - headless: Se True, executa o navegador em modo headless
                - proxy_list: Lista de proxies a serem usados
                - proxy_enabled: Se True, habilita o uso de proxies
                - user_agent_rotation: Se True, habilita a rotação de user-agents
        """
        self.config = config
        self.browser = None
        self.proxy_manager = ProxyManager(config.get('proxy_list', []))
        self.user_agent_manager = UserAgentManager()

        self.listing_scraper = None
        self.post_scraper = None

        self.is_logged_in = False
        self._setup_logging()

    def _setup_logging(self):
        """Configura o logging para o scraper."""
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def setup_browser(self, force_new: bool = False) -> bool:
        """
        Configura o navegador com as opções necessárias.

        Args:
            force_new: Se True, fecha o navegador atual e cria um novo

        Returns:
            True se o navegador foi configurado com sucesso, False caso contrário
        """
        if self.browser and not force_new:
            return True

        if self.browser:
            self.close()

        try:
            chrome_options = Options()

            # Configura o modo headless (sem interface gráfica)
            if self.config.get('headless', True):
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')

            # Configurações adicionais para evitar detecção
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Adiciona um user-agent aleatório
            if self.config.get('user_agent_rotation', True):
                user_agent = self.user_agent_manager.get_random_user_agent()
                chrome_options.add_argument(f'--user-agent={user_agent}')

            # Adiciona um proxy se habilitado
            if self.config.get('proxy_enabled', False):
                proxy = self.proxy_manager.get_next_proxy()
                if proxy:
                    chrome_options.add_argument(f'--proxy-server={proxy}')

            # Inicializa o driver do Chrome
            service = Service(executable_path=self.config.get('chromedriver_path', 'chromedriver'))
            self.browser = webdriver.Chrome(service=service, options=chrome_options)

            # Configura o timeout de página
            self.browser.set_page_load_timeout(30)

            # Inicializa os scrapers específicos
            self.listing_scraper = ListingScraper(self.browser)
            self.post_scraper = PostScraper(self.browser)

            logger.info("Navegador configurado com sucesso")
            return True

        except WebDriverException as e:
            logger.error(f"Erro ao configurar navegador: {str(e)}")
            return False

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Realiza login no LinkedIn.

        Args:
            username: Nome de usuário do LinkedIn (opcional, usa o da configuração se não fornecido)
            password: Senha do LinkedIn (opcional, usa a da configuração se não fornecida)

        Returns:
            True se o login foi bem-sucedido, False caso contrário
        """
        if self.is_logged_in:
            return True

        if not self.browser and not self.setup_browser():
            return False

        username = username or self.config.get('linkedin_username')
        password = password or self.config.get('linkedin_password')

        if not username or not password:
            logger.error("Credenciais do LinkedIn não fornecidas")
            return False

        try:
            # Navega para a página de login
            self.browser.get('https://www.linkedin.com/login')
            time.sleep(random.uniform(2, 4))  # Delay aleatório para parecer humano

            # Preenche o formulário de login
            username_input = self.browser.find_element("id", "username")
            password_input = self.browser.find_element("id", "password")

            # Digita como um humano
            self._type_like_human(username_input, username)
            self._type_like_human(password_input, password)

            # Submete o formulário
            password_input.submit()

            # Espera o login ser processado
            time.sleep(random.uniform(3, 5))

            # Verifica se o login foi bem-sucedido
            if 'feed' in self.browser.current_url:
                self.is_logged_in = True
                logger.info("Login no LinkedIn realizado com sucesso")
                return True
            else:
                logger.error("Falha no login do LinkedIn")
                return False

        except Exception as e:
            logger.error(f"Erro durante o login no LinkedIn: {str(e)}")
            return False

    def scrape_job_listings(
            self,
            keywords: Union[str, List[str]],
            location: str = "",
            filters: Optional[Dict[str, Any]] = None,
            pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Realiza o scraping de listagens oficiais de vagas.

        Args:
            keywords: Palavra(s)-chave para busca
            location: Localização da vaga
            filters: Filtros adicionais (experiência, data de postagem, etc.)
            pages: Número de páginas para coletar

        Returns:
            Lista de vagas encontradas
        """
        if not self.browser and not self.setup_browser():
            return []

        if not self.listing_scraper:
            self.listing_scraper = ListingScraper(self.browser)

        return self.listing_scraper.scrape(keywords, location, filters, pages)

    def scrape_posts(
            self,
            keywords: Union[str, List[str]],
            days_back: int = 7,
            max_posts: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Realiza o scraping de posts do LinkedIn contendo vagas.

        Args:
            keywords: Palavra(s)-chave para busca
            days_back: Quantidade de dias para buscar para trás
            max_posts: Número máximo de posts para coletar

        Returns:
            Lista de posts encontrados contendo possíveis vagas
        """
        if not self.browser and not self.setup_browser():
            return []

        if not self.is_logged_in and not self.login():
            logger.warning("Não foi possível realizar login para scraping de posts")
            return []

        if not self.post_scraper:
            self.post_scraper = PostScraper(self.browser)

        return self.post_scraper.scrape(keywords, days_back, max_posts)

    def extract_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrai detalhes completos de uma vaga específica.

        Args:
            job_url: URL da vaga no LinkedIn

        Returns:
            Dicionário com detalhes da vaga ou None em caso de erro
        """
        if not self.browser and not self.setup_browser():
            return None

        if not self.listing_scraper:
            self.listing_scraper = ListingScraper(self.browser)

        return self.listing_scraper.extract_job_details(job_url)

    def parse_job_from_post(self, post_content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extrai informações de vaga a partir do conteúdo de um post.

        Args:
            post_content: Dicionário contendo o conteúdo do post

        Returns:
            Dicionário com informações da vaga ou None se não for uma vaga
        """
        if not self.post_scraper:
            self.post_scraper = PostScraper(self.browser)

        return self.post_scraper.parse_job_from_post(post_content)

    def rotate_proxy(self) -> bool:
        """
        Altera o proxy atual e reinicia o navegador.

        Returns:
            True se o proxy foi alterado com sucesso, False caso contrário
        """
        if not self.config.get('proxy_enabled', False):
            return False

        proxy = self.proxy_manager.get_next_proxy()
        if not proxy:
            logger.warning("Não há proxies disponíveis para rotação")
            return False

        # Força a criação de um novo navegador com o novo proxy
        return self.setup_browser(force_new=True)

    def rotate_user_agent(self) -> bool:
        """
        Altera o user-agent atual e reinicia o navegador.

        Returns:
            True se o user-agent foi alterado com sucesso, False caso contrário
        """
        if not self.config.get('user_agent_rotation', True):
            return False

        # Força a criação de um novo navegador com novo user-agent
        return self.setup_browser(force_new=True)

    def _type_like_human(self, element, text: str):
        """
        Digita texto em um elemento de forma humanizada.

        Args:
            element: Elemento web onde o texto será digitado
            text: Texto a ser digitado
        """
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Delay aleatório entre teclas

    def close(self):
        """Fecha o navegador e libera os recursos."""
        if self.browser:
            try:
                self.browser.quit()
            except Exception as e:
                logger.error(f"Erro ao fechar navegador: {str(e)}")
            finally:
                self.browser = None
                self.listing_scraper = None
                self.post_scraper = None
                self.is_logged_in = False