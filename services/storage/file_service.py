"""
Serviço de gerenciamento de arquivos locais.

Este módulo contém a implementação do serviço de gerenciamento de arquivos
para armazenamento local de arquivos.
"""

import logging
import os
import shutil
import uuid
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
from datetime import datetime
import mimetypes
from werkzeug.utils import secure_filename

from .. import registry

logger = logging.getLogger(__name__)


class FileService:
    """
    Serviço responsável pelo gerenciamento de arquivos locais.

    Esta classe implementa métodos para armazenar, recuperar e gerenciar
    arquivos no sistema de arquivos local.
    """

    def __init__(self, storage_path: str = None, allowed_extensions: List[str] = None):
        """
        Inicializa o serviço de arquivos.

        Args:
            storage_path: Caminho base para armazenamento de arquivos
            allowed_extensions: Lista de extensões de arquivo permitidas
        """
        # Tenta obter o caminho de armazenamento do registro se não for fornecido
        if not storage_path:
            config = registry.get_config()
            storage_path = config.get('storage_path', 'uploads')

        self.storage_path = storage_path
        self.allowed_extensions = allowed_extensions or [
            'pdf', 'doc', 'docx', 'txt', 'rtf', 'png', 'jpg', 'jpeg', 'gif'
        ]

        # Garante que o diretório de armazenamento existe
        self._ensure_directory_exists(self.storage_path)

        # Subdiretórios por tipo de arquivo
        self.subdirs = {
            'resume': os.path.join(self.storage_path, 'resumes'),
            'profile': os.path.join(self.storage_path, 'profiles'),
            'temp': os.path.join(self.storage_path, 'temp')
        }

        # Garante que os subdiretórios existem
        for subdir in self.subdirs.values():
            self._ensure_directory_exists(subdir)

    def save_file(self, file: BinaryIO, filename: str, file_type: str = 'resume', user_id: Optional[int] = None) -> \
    Tuple[bool, str, Optional[str]]:
        """
        Salva um arquivo no sistema de arquivos.

        Args:
            file: Objeto file-like contendo os dados do arquivo
            filename: Nome original do arquivo
            file_type: Tipo de arquivo (resume, profile, temp)
            user_id: ID do usuário (opcional)

        Returns:
            Tupla (sucesso, mensagem, caminho do arquivo)
        """
        try:
            # Verifica se o tipo de arquivo é válido
            if file_type not in self.subdirs:
                return False, f"Tipo de arquivo inválido: {file_type}", None

            # Verifica se a extensão é permitida
            extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if extension not in self.allowed_extensions:
                return False, f"Extensão de arquivo não permitida: {extension}", None

            # Gera um nome seguro para o arquivo
            safe_filename = secure_filename(filename)

            # Adiciona um identificador único para evitar sobrescrever arquivos
            unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"

            # Define o diretório de destino
            target_dir = self.subdirs[file_type]
            if user_id:
                # Se um user_id for fornecido, cria um subdiretório para o usuário
                target_dir = os.path.join(target_dir, str(user_id))
                self._ensure_directory_exists(target_dir)

            # Caminho completo do arquivo
            file_path = os.path.join(target_dir, unique_filename)

            # Salva o arquivo
            file.seek(0)  # Volta para o início do arquivo
            with open(file_path, 'wb') as f:
                f.write(file.read())

            logger.info(f"Arquivo salvo: {file_path}")
            return True, "Arquivo salvo com sucesso", file_path

        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            return False, f"Erro ao salvar arquivo: {str(e)}", None

    def get_file(self, file_path: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Recupera um arquivo do sistema de arquivos.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Tupla (sucesso, dados do arquivo, tipo MIME)
        """
        try:
            # Verifica se o arquivo existe
            if not os.path.isfile(file_path):
                return False, None, None

            # Lê o arquivo
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Determina o tipo MIME
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Tipo padrão para arquivos binários
                mime_type = 'application/octet-stream'

            return True, file_data, mime_type

        except Exception as e:
            logger.error(f"Erro ao recuperar arquivo: {str(e)}")
            return False, None, None

    def delete_file(self, file_path: str) -> bool:
        """
        Exclui um arquivo do sistema de arquivos.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se o arquivo foi excluído com sucesso, False caso contrário
        """
        try:
            # Verifica se o arquivo existe
            if not os.path.isfile(file_path):
                logger.warning(f"Tentativa de excluir arquivo inexistente: {file_path}")
                return False

            # Verifica se o arquivo está dentro do diretório de armazenamento
            # (medida de segurança para evitar excluir arquivos do sistema)
            if not file_path.startswith(self.storage_path):
                logger.error(f"Tentativa de excluir arquivo fora do diretório de armazenamento: {file_path}")
                return False

            # Exclui o arquivo
            os.remove(file_path)
            logger.info(f"Arquivo excluído: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao excluir arquivo: {str(e)}")
            return False

    def list_user_files(self, user_id: int, file_type: str = 'resume') -> List[Dict[str, Any]]:
        """
        Lista os arquivos de um usuário.

        Args:
            user_id: ID do usuário
            file_type: Tipo de arquivo (resume, profile, temp)

        Returns:
            Lista de dicionários com informações de arquivos
        """
        try:
            # Verifica se o tipo de arquivo é válido
            if file_type not in self.subdirs:
                logger.warning(f"Tipo de arquivo inválido: {file_type}")
                return []

            # Define o diretório do usuário
            user_dir = os.path.join(self.subdirs[file_type], str(user_id))

            # Verifica se o diretório existe
            if not os.path.isdir(user_dir):
                logger.debug(f"Diretório de usuário não encontrado: {user_dir}")
                return []

            # Lista os arquivos no diretório
            files = []
            for filename in os.listdir(user_dir):
                filepath = os.path.join(user_dir, filename)

                # Pula diretórios
                if not os.path.isfile(filepath):
                    continue

                # Obtém informações do arquivo
                stats = os.stat(filepath)
                size = stats.st_size
                created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
                modified_at = datetime.fromtimestamp(stats.st_mtime).isoformat()

                # Determina o tipo MIME
                mime_type, _ = mimetypes.guess_type(filepath)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                # Extrai o nome original do arquivo (remove o UUID prefixado)
                original_filename = filename.split('_', 1)[1] if '_' in filename else filename

                # Adiciona informações do arquivo à lista
                files.append({
                    'filename': original_filename,
                    'path': filepath,
                    'size': size,
                    'mime_type': mime_type,
                    'created_at': created_at,
                    'modified_at': modified_at
                })

            return files

        except Exception as e:
            logger.error(f"Erro ao listar arquivos do usuário: {str(e)}")
            return []

    def create_temp_file(self, data: bytes, filename: str = None, extension: str = 'tmp') -> Optional[str]:
        """
        Cria um arquivo temporário.

        Args:
            data: Dados a serem armazenados no arquivo
            filename: Nome base do arquivo (opcional)
            extension: Extensão do arquivo

        Returns:
            Caminho do arquivo temporário ou None em caso de erro
        """
        try:
            # Gera um nome para o arquivo temporário
            if not filename:
                filename = f"temp_{uuid.uuid4().hex}"

            # Adiciona a extensão se não estiver presente
            if '.' not in filename:
                filename = f"{filename}.{extension}"

            # Caminho completo do arquivo
            file_path = os.path.join(self.subdirs['temp'], filename)

            # Salva o arquivo
            with open(file_path, 'wb') as f:
                f.write(data)

            logger.debug(f"Arquivo temporário criado: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Erro ao criar arquivo temporário: {str(e)}")
            return None

    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Limpa arquivos temporários antigos.

        Args:
            max_age_hours: Idade máxima dos arquivos em horas

        Returns:
            Número de arquivos excluídos
        """
        try:
            # Define o diretório temporário
            temp_dir = self.subdirs['temp']

            # Verifica se o diretório existe
            if not os.path.isdir(temp_dir):
                return 0

            # Calcula o timestamp limite
            now = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            limit_timestamp = now - max_age_seconds

            # Conta os arquivos excluídos
            deleted_count = 0

            # Percorre os arquivos no diretório
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)

                # Pula diretórios
                if not os.path.isfile(filepath):
                    continue

                # Verifica a idade do arquivo
                stats = os.stat(filepath)
                modified_time = stats.st_mtime

                if modified_time < limit_timestamp:
                    # Exclui o arquivo
                    os.remove(filepath)
                    deleted_count += 1

            logger.info(f"Limpeza de arquivos temporários: {deleted_count} arquivos excluídos")
            return deleted_count

        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")
            return 0

    def move_file(self, source_path: str, target_type: str, user_id: Optional[int] = None) -> Tuple[
        bool, str, Optional[str]]:
        """
        Move um arquivo para um diretório diferente.

        Args:
            source_path: Caminho do arquivo a ser movido
            target_type: Tipo de destino (resume, profile)
            user_id: ID do usuário (opcional)

        Returns:
            Tupla (sucesso, mensagem, novo caminho)
        """
        try:
            # Verifica se o arquivo existe
            if not os.path.isfile(source_path):
                return False, "Arquivo não encontrado", None

            # Verifica se o tipo de destino é válido
            if target_type not in self.subdirs:
                return False, f"Tipo de destino inválido: {target_type}", None

            # Define o diretório de destino
            target_dir = self.subdirs[target_type]
            if user_id:
                target_dir = os.path.join(target_dir, str(user_id))
                self._ensure_directory_exists(target_dir)

            # Obtém o nome do arquivo
            filename = os.path.basename(source_path)

            # Define o caminho de destino
            target_path = os.path.join(target_dir, filename)

            # Move o arquivo
            shutil.move(source_path, target_path)

            logger.info(f"Arquivo movido: {source_path} -> {target_path}")
            return True, "Arquivo movido com sucesso", target_path

        except Exception as e:
            logger.error(f"Erro ao mover arquivo: {str(e)}")
            return False, f"Erro ao mover arquivo: {str(e)}", None

    def _ensure_directory_exists(self, path: str):
        """
        Garante que um diretório existe, criando-o se necessário.

        Args:
            path: Caminho do diretório
        """
        if not os.path.exists(path):
            os.makedirs(path)
            logger.debug(f"Diretório criado: {path}")