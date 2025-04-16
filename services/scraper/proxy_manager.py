"""
Gerenciador de proxies para o scraper do LinkedIn.

Este módulo implementa um gerenciador de proxies que permite rotacionar
entre diferentes servidores proxy para evitar bloqueios durante o scraping.
"""

import logging
import random
import time
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProxyManager:
    """
    Gerenciador de proxies para scraping.

    Esta classe gerencia uma lista de proxies, monitora sua disponibilidade
    e performance, e fornece proxies funcionais para o scraper.
    """

    def __init__(self, proxy_list: List[str] = None, proxy_api_url: str = None, proxy_api_key: str = None):
        """
        Inicializa o gerenciador de proxies.

        Args:
            proxy_list: Lista de proxies no formato "ip:porta" ou "protocolo://ip:porta"
            proxy_api_url: URL da API de proxy (se estiver usando um serviço)
            proxy_api_key: Chave de API para o serviço de proxy
        """
        self.proxies = proxy_list or []
        self.proxy_api_url = proxy_api_url
        self.proxy_api_key = proxy_api_key
        self.proxy_status = {}  # Armazena status de cada proxy
        self.current_index = 0
        self.last_rotation_time = datetime.now()
        self.rotation_interval = timedelta(minutes=30)  # Tempo padrão de rotação

        # Inicializa o status dos proxies
        self._initialize_proxy_status()

        logger.info(f"ProxyManager iniciado com {len(self.proxies)} proxies")

    def _initialize_proxy_status(self):
        """Inicializa o status de cada proxy na lista."""
        for proxy in self.proxies:
            self.proxy_status[proxy] = {
                'is_working': True,
                'failures': 0,
                'success': 0,
                'last_used': None,
                'avg_response_time': None,
                'last_checked': None
            }

    def get_next_proxy(self) -> Optional[str]:
        """
        Obtém o próximo proxy disponível da lista.

        Returns:
            String do proxy no formato adequado ou None se não houver proxies disponíveis
        """
        if not self.proxies:
            if self.proxy_api_url:
                self._fetch_proxies_from_api()

            if not self.proxies:
                logger.warning("Nenhum proxy disponível")
                return None

        # Verifica se é hora de rotacionar automaticamente
        current_time = datetime.now()
        if (current_time - self.last_rotation_time) > self.rotation_interval:
            logger.info("Rotação de proxy automática por tempo")
            self._rotate_proxy_index()
            self.last_rotation_time = current_time

        # Tenta até 3 vezes encontrar um proxy funcionando
        for _ in range(min(3, len(self.proxies))):
            proxy = self.proxies[self.current_index]
            status = self.proxy_status.get(proxy, {})

            # Se o proxy está marcado como não funcionando ou tem muitas falhas, pula
            if not status.get('is_working', True) or status.get('failures', 0) > 5:
                self._rotate_proxy_index()
                continue

            # Atualiza o status do proxy
            status['last_used'] = datetime.now()
            self.proxy_status[proxy] = status

            # Formata o proxy adequadamente, adicionando protocolo se necessário
            if not (proxy.startswith('http://') or proxy.startswith('https://') or proxy.startswith('socks://')):
                formatted_proxy = f"http://{proxy}"
            else:
                formatted_proxy = proxy

            logger.info(f"Usando proxy: {formatted_proxy}")
            return formatted_proxy

        logger.warning("Não foi possível encontrar um proxy funcionando")
        return None

    def _rotate_proxy_index(self):
        """Avança para o próximo proxy na lista."""
        self.current_index = (self.current_index + 1) % len(self.proxies)

    def report_success(self, proxy: str, response_time: float = None):
        """
        Registra um uso bem-sucedido do proxy.

        Args:
            proxy: String do proxy usado
            response_time: Tempo de resposta em segundos
        """
        if not proxy or proxy not in self.proxy_status:
            return

        status = self.proxy_status[proxy]

        # Remove o protocolo para checagem
        clean_proxy = proxy.replace('http://', '').replace('https://', '').replace('socks://', '')
        if clean_proxy in self.proxies:
            proxy = clean_proxy

        status['success'] = status.get('success', 0) + 1
        status['is_working'] = True
        status['last_checked'] = datetime.now()

        # Atualiza o tempo médio de resposta
        if response_time is not None:
            if status.get('avg_response_time') is None:
                status['avg_response_time'] = response_time
            else:
                # Média móvel simples
                status['avg_response_time'] = (status['avg_response_time'] * 0.7) + (response_time * 0.3)

        self.proxy_status[proxy] = status

    def report_failure(self, proxy: str, error_type: str = None):
        """
        Registra uma falha no uso do proxy.

        Args:
            proxy: String do proxy usado
            error_type: Tipo de erro encontrado
        """
        if not proxy:
            return

        # Remove o protocolo para checagem
        clean_proxy = proxy.replace('http://', '').replace('https://', '').replace('socks://', '')
        if clean_proxy in self.proxies:
            proxy = clean_proxy
        elif proxy not in self.proxy_status:
            return

        status = self.proxy_status[proxy]
        status['failures'] = status.get('failures', 0) + 1
        status['last_checked'] = datetime.now()

        # Marca como não funcionando após várias falhas
        if status['failures'] >= 3:
            status['is_working'] = False
            logger.warning(f"Proxy {proxy} marcado como não funcionando após {status['failures']} falhas")

        self.proxy_status[proxy] = status

        # Rotaciona para o próximo proxy
        self._rotate_proxy_index()

    def add_proxy(self, proxy: str):
        """
        Adiciona um novo proxy à lista.

        Args:
            proxy: String do proxy no formato "ip:porta" ou "protocolo://ip:porta"
        """
        if not proxy:
            return

        # Verifica se o proxy já existe
        if proxy in self.proxies:
            return

        # Remove o protocolo para evitar duplicatas
        clean_proxy = proxy.replace('http://', '').replace('https://', '').replace('socks://', '')

        for existing in self.proxies:
            if existing.replace('http://', '').replace('https://', '').replace('socks://', '') == clean_proxy:
                return

        # Adiciona o proxy
        self.proxies.append(proxy)

        # Inicializa o status
        self.proxy_status[proxy] = {
            'is_working': True,
            'failures': 0,
            'success': 0,
            'last_used': None,
            'avg_response_time': None,
            'last_checked': None
        }

        logger.info(f"Proxy adicionado: {proxy}")

    def remove_proxy(self, proxy: str):
        """
        Remove um proxy da lista.

        Args:
            proxy: String do proxy a ser removido
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.proxy_status.pop(proxy, None)

            # Ajusta o índice se necessário
            if self.current_index >= len(self.proxies) and self.proxies:
                self.current_index = 0

            logger.info(f"Proxy removido: {proxy}")

    def get_working_proxies(self) -> List[str]:
        """
        Retorna a lista de proxies funcionando.

        Returns:
            Lista de strings de proxies marcados como funcionando
        """
        return [p for p in self.proxies if self.proxy_status.get(p, {}).get('is_working', True)]

    def _fetch_proxies_from_api(self):
        """Obtém proxies de um serviço de API externo."""
        if not self.proxy_api_url:
            return

        try:
            headers = {}
            if self.proxy_api_key:
                headers['Authorization'] = f"Bearer {self.proxy_api_key}"

            response = requests.get(self.proxy_api_url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # O formato da resposta depende do serviço específico
                # Aqui presumimos um formato simples de lista de strings
                new_proxies = data.get('proxies', [])

                if not new_proxies and isinstance(data, list):
                    new_proxies = data

                for proxy in new_proxies:
                    self.add_proxy(proxy)

                logger.info(f"Obtidos {len(new_proxies)} proxies da API")
            else:
                logger.error(f"Falha ao obter proxies da API: {response.status_code}")

        except Exception as e:
            logger.error(f"Erro ao buscar proxies da API: {str(e)}")

    def check_proxies(self, test_url: str = 'https://www.google.com', timeout: int = 5):
        """
        Verifica quais proxies estão funcionando.

        Args:
            test_url: URL para testar os proxies
            timeout: Tempo limite em segundos para o teste
        """
        for proxy in self.proxies:
            try:
                # Formata o proxy adequadamente
                if not (proxy.startswith('http://') or proxy.startswith('https://') or proxy.startswith('socks://')):
                    formatted_proxy = f"http://{proxy}"
                else:
                    formatted_proxy = proxy

                proxies = {
                    'http': formatted_proxy,
                    'https': formatted_proxy
                }

                start_time = time.time()
                response = requests.get(test_url, proxies=proxies, timeout=timeout)
                response_time = time.time() - start_time

                if response.status_code == 200:
                    self.report_success(proxy, response_time)
                    logger.info(f"Proxy {proxy} está funcionando (tempo: {response_time:.2f}s)")
                else:
                    self.report_failure(proxy, f"HTTP {response.status_code}")
                    logger.warning(f"Proxy {proxy} retornou status {response.status_code}")

            except requests.RequestException as e:
                self.report_failure(proxy, str(e))
                logger.warning(f"Proxy {proxy} falhou: {str(e)}")

            # Pequeno delay entre testes para não sobrecarregar
            time.sleep(0.5)

    def get_proxy_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna estatísticas sobre os proxies.

        Returns:
            Dicionário com estatísticas de cada proxy
        """
        return self.proxy_status

    def set_rotation_interval(self, minutes: int):
        """
        Define o intervalo de rotação automática de proxies.

        Args:
            minutes: Intervalo em minutos para rotação automática
        """
        self.rotation_interval = timedelta(minutes=minutes)