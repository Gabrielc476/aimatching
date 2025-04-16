"""
Módulo de serviços do LinkedIn Job Matcher.

Este pacote contém os serviços de negócio da aplicação, incluindo:
- Autenticação e gerenciamento de tokens
- Web scraping do LinkedIn
- Correspondência entre currículos e vagas
- Integração com IA (Claude 3.7 Sonnet)
- Notificações em tempo real
- Armazenamento de arquivos
"""

from flask import current_app
from typing import Any, Dict, Optional


# Configuração global compartilhada entre serviços
class ServiceRegistry:
    """Registro central de serviços da aplicação."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
            cls._instance._services = {}
            cls._instance._config = {}
        return cls._instance

    def register(self, name: str, service: Any) -> None:
        """Registra um serviço no registro."""
        self._services[name] = service

    def get(self, name: str) -> Optional[Any]:
        """Obtém um serviço pelo nome."""
        return self._services.get(name)

    def set_config(self, config: Dict[str, Any]) -> None:
        """Define a configuração compartilhada entre serviços."""
        self._config = config

    def get_config(self) -> Dict[str, Any]:
        """Obtém a configuração compartilhada."""
        return self._config


# Instância global do registro de serviços
registry = ServiceRegistry()


def init_app(app):
    """Inicializa os serviços com a aplicação Flask."""
    # Configura o registro com as configurações da aplicação
    config = {
        'linkedin_username': app.config.get('LINKEDIN_USERNAME'),
        'linkedin_password': app.config.get('LINKEDIN_PASSWORD'),
        'claude_api_key': app.config.get('CLAUDE_API_KEY'),
        'storage_path': app.config.get('STORAGE_PATH', 'uploads'),
        's3_bucket': app.config.get('S3_BUCKET'),
        's3_region': app.config.get('S3_REGION'),
        'aws_access_key': app.config.get('AWS_ACCESS_KEY'),
        'aws_secret_key': app.config.get('AWS_SECRET_KEY'),
    }
    registry.set_config(config)

    # Outros serviços podem ser inicializados aqui conforme necessário

    @app.teardown_appcontext
    def teardown_services(exception=None):
        """Limpa recursos dos serviços quando o contexto da aplicação termina."""
        # Implementar limpeza de recursos se necessário
        pass