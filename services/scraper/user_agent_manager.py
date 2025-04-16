"""
Gerenciador de User-Agents para o scraper do LinkedIn.

Este módulo implementa um gerenciador de User-Agents que permite rotacionar
entre diferentes strings de User-Agent para evitar bloqueios durante o scraping.
"""

import logging
import random
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class UserAgentManager:
    """
    Gerenciador de User-Agents para scraping.

    Esta classe mantém uma lista de strings de User-Agent e fornece métodos
    para obter User-Agents aleatórios para uso no scraper.
    """

    def __init__(self, user_agents: List[str] = None, user_agents_file: str = None):
        """
        Inicializa o gerenciador de User-Agents.

        Args:
            user_agents: Lista de strings de User-Agent
            user_agents_file: Caminho para um arquivo JSON contendo User-Agents
        """
        self.user_agents = user_agents or []

        # Carrega User-Agents de um arquivo, se fornecido
        if user_agents_file and os.path.exists(user_agents_file):
            self._load_from_file(user_agents_file)

        # Se ainda não tiver User-Agents, carrega a lista padrão
        if not self.user_agents:
            self._load_default_user_agents()

        # Mantém estatísticas de uso
        self.usage_stats = {ua: 0 for ua in self.user_agents}
        self.last_used = None

        logger.info(f"UserAgentManager iniciado com {len(self.user_agents)} User-Agents")

    def _load_from_file(self, file_path: str):
        """
        Carrega User-Agents de um arquivo JSON.

        Args:
            file_path: Caminho para o arquivo JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # O arquivo pode conter uma lista direta ou um objeto com uma chave 'user_agents'
                if isinstance(data, list):
                    self.user_agents = data
                elif isinstance(data, dict) and 'user_agents' in data:
                    self.user_agents = data['user_agents']

            logger.info(f"Carregados {len(self.user_agents)} User-Agents do arquivo {file_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar User-Agents do arquivo {file_path}: {str(e)}")

    def _load_default_user_agents(self):
        """Carrega uma lista padrão de User-Agents comuns."""
        # Lista de User-Agents comuns e modernos para navegadores desktop
        self.user_agents = [
            # Chrome em Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",

            # Chrome em macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",

            # Firefox em Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",

            # Firefox em macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",

            # Safari em macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",

            # Edge em Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",

            # Opera em Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",

            # Brave
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Brave/120.0.0.0",

            # Chrome em Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",

            # Firefox em Linux
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]

        logger.info(f"Carregados {len(self.user_agents)} User-Agents padrão")

    def get_random_user_agent(self) -> str:
        """
        Retorna um User-Agent aleatório da lista.

        Returns:
            String de User-Agent
        """
        if not self.user_agents:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # Seleciona um User-Agent aleatório
        user_agent = random.choice(self.user_agents)

        # Atualiza estatísticas
        self.usage_stats[user_agent] = self.usage_stats.get(user_agent, 0) + 1
        self.last_used = user_agent

        return user_agent

    def get_least_used_user_agent(self) -> str:
        """
        Retorna o User-Agent menos utilizado.

        Returns:
            String de User-Agent menos utilizado
        """
        if not self.user_agents:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # Encontra o User-Agent com menor contagem de uso
        user_agent = min(self.usage_stats.items(), key=lambda x: x[1])[0]

        # Atualiza estatísticas
        self.usage_stats[user_agent] = self.usage_stats.get(user_agent, 0) + 1
        self.last_used = user_agent

        return user_agent

    def get_user_agent_by_type(self, browser_type: str = None, os_type: str = None) -> str:
        """
        Retorna um User-Agent com base no tipo de navegador e sistema operacional.

        Args:
            browser_type: Tipo de navegador (chrome, firefox, safari, edge, opera)
            os_type: Tipo de sistema operacional (windows, mac, linux)

        Returns:
            String de User-Agent correspondente ou aleatório se não houver correspondência
        """
        if not self.user_agents:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # Normaliza os tipos para minúsculas
        browser_type = browser_type.lower() if browser_type else None
        os_type = os_type.lower() if os_type else None

        matches = []

        for ua in self.user_agents:
            ua_lower = ua.lower()

            # Verifica se corresponde ao navegador e SO
            browser_match = not browser_type or (
                    (
                                browser_type == 'chrome' and 'chrome' in ua_lower and 'edg' not in ua_lower and 'opr' not in ua_lower) or
                    (browser_type == 'firefox' and 'firefox' in ua_lower) or
                    (browser_type == 'safari' and 'safari' in ua_lower and 'chrome' not in ua_lower) or
                    (browser_type == 'edge' and 'edg' in ua_lower) or
                    (browser_type == 'opera' and 'opr' in ua_lower) or
                    (browser_type == 'brave' and 'brave' in ua_lower)
            )

            os_match = not os_type or (
                    (os_type == 'windows' and 'windows' in ua_lower) or
                    (os_type == 'mac' and ('macintosh' in ua_lower or 'mac os' in ua_lower)) or
                    (os_type == 'linux' and 'linux' in ua_lower)
            )

            if browser_match and os_match:
                matches.append(ua)

        if matches:
            # Seleciona aleatoriamente entre as correspondências
            user_agent = random.choice(matches)
        else:
            # Se não houver correspondência, retorna aleatório
            user_agent = random.choice(self.user_agents)

        # Atualiza estatísticas
        self.usage_stats[user_agent] = self.usage_stats.get(user_agent, 0) + 1
        self.last_used = user_agent

        return user_agent

    def add_user_agent(self, user_agent: str):
        """
        Adiciona um novo User-Agent à lista.

        Args:
            user_agent: String de User-Agent
        """
        if not user_agent or user_agent in self.user_agents:
            return

        self.user_agents.append(user_agent)
        self.usage_stats[user_agent] = 0

        logger.info(f"User-Agent adicionado: {user_agent}")

    def remove_user_agent(self, user_agent: str):
        """
        Remove um User-Agent da lista.

        Args:
            user_agent: String de User-Agent a ser removido
        """
        if user_agent in self.user_agents:
            self.user_agents.remove(user_agent)
            self.usage_stats.pop(user_agent, None)

            logger.info(f"User-Agent removido: {user_agent}")

    def save_to_file(self, file_path: str):
        """
        Salva a lista de User-Agents em um arquivo JSON.

        Args:
            file_path: Caminho para o arquivo JSON
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'user_agents': self.user_agents,
                        'updated_at': datetime.now().isoformat()
                    },
                    f,
                    indent=2
                )

            logger.info(f"Lista de User-Agents salva em {file_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar User-Agents em {file_path}: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o uso de User-Agents.

        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_user_agents': len(self.user_agents),
            'usage_stats': self.usage_stats,
            'last_used': self.last_used
        }

    def get_all_user_agents(self) -> List[str]:
        """
        Retorna a lista completa de User-Agents.

        Returns:
            Lista de strings de User-Agent
        """
        return self.user_agents.copy()