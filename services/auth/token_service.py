"""
Serviço de gerenciamento de tokens de autenticação.
"""

import jwt
import redis
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from flask import current_app


class TokenService:
    """
    Serviço responsável pela geração, validação e revogação de tokens JWT.

    Esta classe implementa os métodos necessários para gerenciar o ciclo de vida
    dos tokens de autenticação e atualização.
    """

    def __init__(self, redis_client: redis.Redis = None):
        """
        Inicializa o serviço de tokens.

        Args:
            redis_client: Cliente do Redis para gerenciar tokens revogados
        """
        self.redis_client = redis_client
        self._access_token_expiration = 30  # minutos
        self._refresh_token_expiration = 7  # dias

    @property
    def _secret_key(self) -> str:
        """Obtém a chave secreta para assinatura de tokens."""
        return current_app.config.get('SECRET_KEY')

    @property
    def _token_algorithm(self) -> str:
        """Obtém o algoritmo de assinatura de tokens."""
        return 'HS256'

    def create_access_token(self, user_id: int) -> str:
        """
        Cria um token de acesso JWT para o usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Token JWT assinado
        """
        now = datetime.utcnow()
        payload = {
            'sub': user_id,  # 'sub' é o subject, normalmente o ID do usuário
            'iat': now,  # 'iat' é o issued at time
            'exp': now + timedelta(minutes=self._access_token_expiration),
            'type': 'access'
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._token_algorithm
        )

    def create_refresh_token(self, user_id: int) -> str:
        """
        Cria um token de atualização JWT para o usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Token JWT assinado
        """
        now = datetime.utcnow()
        payload = {
            'sub': user_id,
            'iat': now,
            'exp': now + timedelta(days=self._refresh_token_expiration),
            'type': 'refresh',
            'jti': str(now.timestamp())  # 'jti' é um identificador único para o token
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._token_algorithm
        )

    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Valida um token de acesso e retorna seu payload.

        Args:
            token: Token JWT a ser validado

        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._token_algorithm]
            )

            # Verifica o tipo do token
            if payload.get('type') != 'access':
                return None

            return payload
        except jwt.PyJWTError:
            return None

    def validate_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Valida um token de atualização e retorna seu payload.

        Args:
            token: Token JWT a ser validado

        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._token_algorithm]
            )

            # Verifica o tipo do token
            if payload.get('type') != 'refresh':
                return None

            # Verifica se o token foi revogado
            jti = payload.get('jti')
            if jti and self._is_token_revoked(jti):
                return None

            return payload
        except jwt.PyJWTError:
            return None

    def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoga um token de atualização.

        Args:
            token: Token JWT a ser revogado

        Returns:
            True se o token foi revogado com sucesso, False caso contrário
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._token_algorithm]
            )

            # Verifica o tipo do token
            if payload.get('type') != 'refresh':
                return False

            # Adiciona o token à lista de revogados
            jti = payload.get('jti')
            exp = payload.get('exp')

            if jti and exp and self.redis_client:
                # Calcula o tempo restante até a expiração
                now = datetime.utcnow()
                exp_datetime = datetime.fromtimestamp(exp)
                ttl = max(0, int((exp_datetime - now).total_seconds()))

                # Adiciona o token à lista de revogados pelo tempo restante
                self.redis_client.setex(
                    f'revoked_token:{jti}',
                    ttl,
                    1
                )

                return True

            return False
        except jwt.PyJWTError:
            return False

    def _is_token_revoked(self, jti: str) -> bool:
        """
        Verifica se um token está na lista de revogados.

        Args:
            jti: Identificador único do token

        Returns:
            True se o token estiver revogado, False caso contrário
        """
        if not self.redis_client:
            return False

        return bool(self.redis_client.exists(f'revoked_token:{jti}'))