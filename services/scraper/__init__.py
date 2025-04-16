"""
Serviços de web scraping para coleta de vagas do LinkedIn.

Este pacote contém os serviços responsáveis por coletar vagas de emprego
do LinkedIn, incluindo vagas de listas oficiais e posts contendo vagas.
"""

from .linkedin_scraper import LinkedInScraper
from .listing_scraper import ListingScraper
from .post_scraper import PostScraper
from .proxy_manager import ProxyManager
from .user_agent_manager import UserAgentManager

__all__ = [
    'LinkedInScraper',
    'ListingScraper',
    'PostScraper',
    'ProxyManager',
    'UserAgentManager'
]