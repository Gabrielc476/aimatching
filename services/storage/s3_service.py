"""
Serviço de armazenamento em AWS S3.

Este módulo contém a implementação do serviço de armazenamento em nuvem
utilizando o Amazon S3 para armazenamento de arquivos.
"""

import logging
import os
import uuid
import io
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
from datetime import datetime, timedelta
import mimetypes
from werkzeug.utils import secure_filename

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = Exception

from .. import registry

logger = logging.getLogger(__name__)


class S3Service:
    """
    Serviço responsável pelo armazenamento de arquivos no Amazon S3.

    Esta classe implementa métodos para armazenar, recuperar e gerenciar
    arquivos no serviço de armazenamento em nuvem Amazon S3.
    """

    def __init__(self,
                 aws_access_key: str = None,
                 aws_secret_key: str = None,
                 bucket_name: str = None,
                 region_name: str = None,
                 allowed_extensions: List[str] = None):
        """
        Inicializa o serviço de armazenamento S3.

        Args:
            aws_access_key: Chave de acesso AWS
            aws_secret_key: Chave secreta AWS
            bucket_name: Nome do bucket S3
            region_name: Nome da região AWS
            allowed_extensions: Lista de extensões de arquivo permitidas
        """
        # Tenta obter as credenciais do registro se não forem fornecidas
        if not aws_access_key or not aws_secret_key or not bucket_name:
            config = registry.get_config()
            aws_access_key = aws_access_key or config.get('aws_access_key')
            aws_secret_key = aws_secret_key or config.get('aws_secret_key')
            bucket_name = bucket_name or config.get('s3_bucket')
            region_name = region_name or config.get('s3_region', 'us-east-1')

        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = None
        self.s3_resource = None

        self.allowed_extensions = allowed_extensions or [
            'pdf', 'doc', 'docx', 'txt', 'rtf', 'png', 'jpg', 'jpeg', 'gif'
        ]

        # Prefixos para organizar os arquivos no bucket
        self.prefixes = {
            'resume': 'resumes/',
            'profile': 'profiles/',
            'temp': 'temp/'
        }

        # Inicializa o cliente S3 se possível
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa o cliente S3 se as credenciais estiverem disponíveis."""
        if not boto3:
            logger.warning("Biblioteca boto3 não está disponível. Instale com 'pip install boto3'")
            return

        if not self.aws_access_key or not self.aws_secret_key or not self.bucket_name:
            logger.warning("Credenciais ou bucket AWS S3 não foram fornecidos")
            return

        try:
            # Inicializa o cliente S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region_name
            )

            # Inicializa o recurso S3 (para operações de alto nível)
            self.s3_resource = boto3.resource(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region_name
            )

            logger.info(f"Cliente S3 inicializado para bucket {self.bucket_name}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente S3: {str(e)}")
            self.s3_client = None
            self.s3_resource = None

    def save_file(self, file: BinaryIO, filename: str, file_type: str = 'resume', user_id: Optional[int] = None) -> \
    Tuple[bool, str, Optional[str]]:
        """
        Salva um arquivo no S3.

        Args:
            file: Objeto file-like contendo os dados do arquivo
            filename: Nome original do arquivo
            file_type: Tipo de arquivo (resume, profile, temp)
            user_id: ID do usuário (opcional)

        Returns:
            Tupla (sucesso, mensagem, URL do arquivo)
        """
        if not self.s3_client:
            return False, "Cliente S3 não inicializado", None

        try:
            # Verifica se o tipo de arquivo é válido
            if file_type not in self.prefixes:
                return False, f"Tipo de arquivo inválido: {file_type}", None

            # Verifica se a extensão é permitida
            extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if extension not in self.allowed_extensions:
                return False, f"Extensão de arquivo não permitida: {extension}", None

            # Gera um nome seguro para o arquivo
            safe_filename = secure_filename(filename)

            # Adiciona um identificador único para evitar sobrescrever arquivos
            unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"

            # Define o caminho dentro do bucket
            key = self.prefixes[file_type]
            if user_id:
                key += f"user_{user_id}/"
            key += unique_filename

            # Determina o tipo MIME
            mime_type, _ = mimetypes.guess_type(filename)
            content_type = mime_type or 'application/octet-stream'

            # Faz upload do arquivo para o S3
            file.seek(0)  # Volta para o início do arquivo
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'private'  # Por segurança, define como privado
                }
            )

            # Gera a URL do arquivo
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}"

            logger.info(f"Arquivo salvo no S3: {url}")
            return True, "Arquivo salvo com sucesso", url

        except Exception as e:
            logger.error(f"Erro ao salvar arquivo no S3: {str(e)}")
            return False, f"Erro ao salvar arquivo: {str(e)}", None

    def get_file(self, key: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Recupera um arquivo do S3.

        Args:
            key: Chave do arquivo no S3

        Returns:
            Tupla (sucesso, dados do arquivo, tipo MIME)
        """
        if not self.s3_client:
            return False, None, None

        try:
            # Cria um buffer para receber os dados
            buffer = io.BytesIO()

            # Baixa o arquivo do S3
            self.s3_client.download_fileobj(self.bucket_name, key, buffer)

            # Volta para o início do buffer
            buffer.seek(0)

            # Lê os dados do buffer
            file_data = buffer.read()

            # Determina o tipo MIME
            mime_type, _ = mimetypes.guess_type(key)
            if not mime_type:
                # Tipo padrão para arquivos binários
                mime_type = 'application/octet-stream'

            return True, file_data, mime_type

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Arquivo não encontrado no S3: {key}")
            else:
                logger.error(f"Erro ao recuperar arquivo do S3: {str(e)}")
            return False, None, None
        except Exception as e:
            logger.error(f"Erro ao recuperar arquivo do S3: {str(e)}")
            return False, None, None

    def get_file_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Gera uma URL pré-assinada para acesso temporário a um arquivo.

        Args:
            key: Chave do arquivo no S3
            expires_in: Tempo de expiração em segundos

        Returns:
            URL pré-assinada ou None em caso de erro
        """
        if not self.s3_client:
            return None

        try:
            # Gera a URL pré-assinada
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )

            return url

        except Exception as e:
            logger.error(f"Erro ao gerar URL pré-assinada: {str(e)}")
            return None

    def delete_file(self, key: str) -> bool:
        """
        Exclui um arquivo do S3.

        Args:
            key: Chave do arquivo no S3

        Returns:
            True se o arquivo foi excluído com sucesso, False caso contrário
        """
        if not self.s3_client:
            return False

        try:
            # Exclui o arquivo do S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            logger.info(f"Arquivo excluído do S3: {key}")
            return True

        except Exception as e:
            logger.error(f"Erro ao excluir arquivo do S3: {str(e)}")
            return False

    def list_user_files(self, user_id: int, file_type: str = 'resume') -> List[Dict[str, Any]]:
        """
        Lista os arquivos de um usuário no S3.

        Args:
            user_id: ID do usuário
            file_type: Tipo de arquivo (resume, profile, temp)

        Returns:
            Lista de dicionários com informações de arquivos
        """
        if not self.s3_client:
            return []

        try:
            # Verifica se o tipo de arquivo é válido
            if file_type not in self.prefixes:
                logger.warning(f"Tipo de arquivo inválido: {file_type}")
                return []

            # Define o prefixo para busca
            prefix = f"{self.prefixes[file_type]}user_{user_id}/"

            # Lista os objetos no bucket com o prefixo especificado
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            # Verifica se há conteúdo
            if 'Contents' not in response:
                return []

            # Processa cada objeto
            files = []
            for obj in response['Contents']:
                key = obj['Key']
                size = obj['Size']
                last_modified = obj['LastModified']

                # Extrai o nome do arquivo do key
                filename = key.split('/')[-1]
                original_filename = filename.split('_', 1)[1] if '_' in filename else filename

                # Determina o tipo MIME
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                # Gera uma URL pré-assinada para acesso temporário
                url = self.get_file_url(key)

                # Adiciona informações do arquivo à lista
                files.append({
                    'filename': original_filename,
                    'key': key,
                    'size': size,
                    'mime_type': mime_type,
                    'last_modified': last_modified.isoformat(),
                    'url': url
                })

            return files

        except Exception as e:
            logger.error(f"Erro ao listar arquivos do usuário no S3: {str(e)}")
            return []

    def create_temp_file(self, data: bytes, filename: str = None, extension: str = 'tmp') -> Optional[str]:
        """
        Cria um arquivo temporário no S3.

        Args:
            data: Dados a serem armazenados no arquivo
            filename: Nome base do arquivo (opcional)
            extension: Extensão do arquivo

        Returns:
            Chave do arquivo temporário ou None em caso de erro
        """
        if not self.s3_client:
            return None

        try:
            # Gera um nome para o arquivo temporário
            if not filename:
                filename = f"temp_{uuid.uuid4().hex}"

            # Adiciona a extensão se não estiver presente
            if '.' not in filename:
                filename = f"{filename}.{extension}"

            # Define a chave para o arquivo
            key = f"{self.prefixes['temp']}{filename}"

            # Determina o tipo MIME
            mime_type, _ = mimetypes.guess_type(filename)
            content_type = mime_type or 'application/octet-stream'

            # Cria um buffer com os dados
            buffer = io.BytesIO(data)

            # Faz upload do arquivo para o S3
            self.s3_client.upload_fileobj(
                buffer,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'private'
                }
            )

            logger.debug(f"Arquivo temporário criado no S3: {key}")
            return key

        except Exception as e:
            logger.error(f"Erro ao criar arquivo temporário no S3: {str(e)}")
            return None

    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Limpa arquivos temporários antigos no S3.

        Args:
            max_age_hours: Idade máxima dos arquivos em horas

        Returns:
            Número de arquivos excluídos
        """
        if not self.s3_client:
            return 0

        try:
            # Define o prefixo para busca
            prefix = self.prefixes['temp']

            # Lista os objetos no bucket com o prefixo especificado
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            # Verifica se há conteúdo
            if 'Contents' not in response:
                return 0

            # Calcula o limite de tempo
            limit_time = datetime.now() - timedelta(hours=max_age_hours)

            # Coleta as chaves dos arquivos antigos
            delete_keys = []
            for obj in response['Contents']:
                key = obj['Key']
                last_modified = obj['LastModified']

                if last_modified.replace(tzinfo=None) < limit_time:
                    delete_keys.append({'Key': key})

            # Se não houver arquivos para excluir, retorna
            if not delete_keys:
                return 0

            # Exclui os arquivos em lote
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': delete_keys,
                    'Quiet': True
                }
            )

            deleted_count = len(delete_keys)
            logger.info(f"Limpeza de arquivos temporários no S3: {deleted_count} arquivos excluídos")
            return deleted_count

        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários no S3: {str(e)}")
            return 0

    def move_file(self, source_key: str, target_type: str, user_id: Optional[int] = None) -> Tuple[
        bool, str, Optional[str]]:
        """
        Move um arquivo para um prefixo diferente no S3.

        Args:
            source_key: Chave do arquivo a ser movido
            target_type: Tipo de destino (resume, profile)
            user_id: ID do usuário (opcional)

        Returns:
            Tupla (sucesso, mensagem, nova chave)
        """
        if not self.s3_client:
            return False, "Cliente S3 não inicializado", None

        try:
            # Verifica se o tipo de destino é válido
            if target_type not in self.prefixes:
                return False, f"Tipo de destino inválido: {target_type}", None

            # Verifica se o arquivo existe
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=source_key
                )
            except ClientError:
                return False, "Arquivo não encontrado", None

            # Obtém o nome do arquivo da chave
            filename = source_key.split('/')[-1]

            # Define a nova chave
            target_key = self.prefixes[target_type]
            if user_id:
                target_key += f"user_{user_id}/"
            target_key += filename

            # Copia o arquivo para o novo local
            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=target_key,
                ACL='private'
            )

            # Exclui o arquivo original
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=source_key
            )

            logger.info(f"Arquivo movido no S3: {source_key} -> {target_key}")
            return True, "Arquivo movido com sucesso", target_key

        except Exception as e:
            logger.error(f"Erro ao mover arquivo no S3: {str(e)}")
            return False, f"Erro ao mover arquivo: {str(e)}", None

    def check_bucket_exists(self) -> bool:
        """
        Verifica se o bucket S3 existe e está acessível.

        Returns:
            True se o bucket existe e está acessível, False caso contrário
        """
        if not self.s3_client:
            return False

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar bucket S3: {str(e)}")
            return False