"""
Serviço de autenticação de usuários.
"""

import bcrypt
from typing import Dict, Optional, Tuple
from datetime import datetime

from .token_service import TokenService


class AuthService:
    """
    Serviço responsável pela autenticação e gerenciamento de usuários.

    Esta classe implementa os métodos necessários para registro, login,
    verificação e atualização de usuários.
    """

    def __init__(self, user_repository, token_service: TokenService = None):
        """
        Inicializa o serviço de autenticação.

        Args:
            user_repository: Repositório de usuários para acesso ao banco de dados
            token_service: Serviço para geração e validação de tokens
        """
        self.user_repository = user_repository
        self.token_service = token_service or TokenService()

    def register(self, email: str, password: str, name: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Registra um novo usuário no sistema.

        Args:
            email: Email do usuário (será o username)
            password: Senha do usuário
            name: Nome completo do usuário

        Returns:
            Tupla contendo (sucesso, mensagem, dados do usuário)
        """
        # Verifica se o usuário já existe
        existing_user = self.user_repository.find_by_email(email)
        if existing_user:
            return False, "Email já cadastrado", None

        # Gera o hash da senha
        password_hash = self._hash_password(password)

        # Cria o novo usuário
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "created_at": datetime.utcnow()
        }

        # Salva o usuário no banco de dados
        user_id = self.user_repository.create(user_data)

        if not user_id:
            return False, "Erro ao criar usuário", None

        # Omite a senha no retorno
        user_data.pop("password_hash")
        user_data["id"] = user_id

        return True, "Usuário registrado com sucesso", user_data

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Autentica um usuário e gera tokens de acesso.

        Args:
            email: Email do usuário
            password: Senha do usuário

        Returns:
            Tupla contendo (sucesso, mensagem, tokens de acesso)
        """
        user = self.user_repository.find_by_email(email)

        if not user:
            return False, "Usuário não encontrado", None

        # Verifica a senha
        if not self._check_password(password, user["password_hash"]):
            return False, "Senha incorreta", None

        # Gera tokens de acesso
        access_token = self.token_service.create_access_token(user["id"])
        refresh_token = self.token_service.create_refresh_token(user["id"])

        return True, "Login realizado com sucesso", {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        }

    def refresh_token(self, refresh_token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Gera um novo access token a partir de um refresh token.

        Args:
            refresh_token: Token de atualização

        Returns:
            Tupla contendo (sucesso, mensagem, novo access token)
        """
        # Verifica o refresh token
        payload = self.token_service.validate_refresh_token(refresh_token)
        if not payload:
            return False, "Token de atualização inválido ou expirado", None

        user_id = payload.get("sub")
        user = self.user_repository.find_by_id(user_id)

        if not user:
            return False, "Usuário não encontrado", None

        # Gera um novo access token
        access_token = self.token_service.create_access_token(user["id"])

        return True, "Token atualizado com sucesso", {
            "access_token": access_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        }

    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Valida um token de acesso e retorna o payload.

        Args:
            token: Token de acesso a ser validado

        Returns:
            Tupla contendo (válido, payload)
        """
        payload = self.token_service.validate_access_token(token)
        if not payload:
            return False, None

        return True, payload

    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """
        Obtém os dados do usuário a partir de um token.

        Args:
            token: Token de acesso

        Returns:
            Dados do usuário ou None se o token for inválido
        """
        valid, payload = self.validate_token(token)
        if not valid:
            return None

        user_id = payload.get("sub")
        user = self.user_repository.find_by_id(user_id)

        if not user:
            return None

        # Omite a senha no retorno
        user.pop("password_hash", None)

        return user

    def logout(self, refresh_token: str) -> bool:
        """
        Realiza o logout do usuário, invalidando o refresh token.

        Args:
            refresh_token: Token de atualização a ser invalidado

        Returns:
            True se o logout foi bem-sucedido, False caso contrário
        """
        return self.token_service.revoke_refresh_token(refresh_token)

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Altera a senha de um usuário.

        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha

        Returns:
            Tupla contendo (sucesso, mensagem)
        """
        user = self.user_repository.find_by_id(user_id)

        if not user:
            return False, "Usuário não encontrado"

        # Verifica a senha atual
        if not self._check_password(current_password, user["password_hash"]):
            return False, "Senha atual incorreta"

        # Gera o hash da nova senha
        new_password_hash = self._hash_password(new_password)

        # Atualiza a senha no banco de dados
        success = self.user_repository.update(user_id, {
            "password_hash": new_password_hash
        })

        if not success:
            return False, "Erro ao atualizar senha"

        return True, "Senha alterada com sucesso"

    def _hash_password(self, password: str) -> str:
        """
        Gera um hash seguro para a senha.

        Args:
            password: Senha em texto plano

        Returns:
            Hash da senha
        """
        # Gera um salt aleatório
        salt = bcrypt.gensalt()

        # Gera o hash da senha com o salt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

        return password_hash.decode('utf-8')

    def _check_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash armazenado.

        Args:
            password: Senha em texto plano
            password_hash: Hash da senha armazenada

        Returns:
            True se a senha corresponder ao hash, False caso contrário
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )