"""
Serviço de gerenciamento de notificações.

Este módulo contém a implementação do serviço de notificações responsável
por criar, gerenciar e entregar notificações aos usuários.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Serviço responsável por gerenciar notificações.

    Esta classe implementa métodos para criar, gerenciar e entregar
    notificações aos usuários através de diferentes canais.
    """

    def __init__(self,
                 websocket_manager: WebSocketManager = None,
                 notification_repository=None,
                 max_notifications_per_user: int = 100):
        """
        Inicializa o serviço de notificações.

        Args:
            websocket_manager: Gerenciador de WebSockets para entrega em tempo real
            notification_repository: Repositório para persistência de notificações
            max_notifications_per_user: Número máximo de notificações por usuário
        """
        self.websocket_manager = websocket_manager or WebSocketManager()
        self.notification_repository = notification_repository
        self.max_notifications_per_user = max_notifications_per_user

        # Tipos de notificação
        self.notification_types = {
            'new_match': {
                'title': 'Nova correspondência',
                'description': 'Uma nova vaga compatível com seu perfil foi encontrada.',
                'icon': 'match',
                'priority': 'high'
            },
            'job_update': {
                'title': 'Vaga atualizada',
                'description': 'Uma vaga compatível foi atualizada.',
                'icon': 'update',
                'priority': 'medium'
            },
            'match_recommendation': {
                'title': 'Recomendação de candidatura',
                'description': 'Recebemos recomendações para melhorar sua candidatura.',
                'icon': 'recommendation',
                'priority': 'medium'
            },
            'job_expired': {
                'title': 'Vaga expirada',
                'description': 'Uma vaga compatível expirou.',
                'icon': 'expired',
                'priority': 'low'
            },
            'system': {
                'title': 'Notificação do sistema',
                'description': 'Informação importante do sistema.',
                'icon': 'system',
                'priority': 'high'
            },
            'profile_recommendation': {
                'title': 'Melhore seu perfil',
                'description': 'Sugestões para melhorar seu perfil e aumentar suas chances.',
                'icon': 'profile',
                'priority': 'medium'
            }
        }

    def create_notification(self,
                            user_id: int,
                            notification_type: str,
                            title: Optional[str] = None,
                            message: Optional[str] = None,
                            data: Optional[Dict[str, Any]] = None,
                            send_realtime: bool = True) -> Optional[int]:
        """
        Cria uma nova notificação para um usuário.

        Args:
            user_id: ID do usuário destinatário
            notification_type: Tipo de notificação
            title: Título da notificação (opcional)
            message: Mensagem da notificação (opcional)
            data: Dados adicionais da notificação (opcional)
            send_realtime: Se True, envia em tempo real por WebSocket

        Returns:
            ID da notificação criada ou None em caso de erro
        """
        try:
            # Obtém o template do tipo de notificação
            notification_template = self.notification_types.get(notification_type)
            if not notification_template:
                logger.warning(f"Tipo de notificação desconhecido: {notification_type}")
                notification_template = {
                    'title': 'Notificação',
                    'description': 'Nova notificação do sistema.',
                    'icon': 'default',
                    'priority': 'medium'
                }

            # Cria a notificação
            notification = {
                'user_id': user_id,
                'type': notification_type,
                'title': title or notification_template['title'],
                'message': message or notification_template['description'],
                'data': data or {},
                'icon': notification_template['icon'],
                'priority': notification_template['priority'],
                'created_at': datetime.utcnow().isoformat(),
                'read': False
            }

            # Salva a notificação no repositório, se disponível
            notification_id = None
            if self.notification_repository:
                notification_id = self.notification_repository.create(notification)
                notification['id'] = notification_id

                # Limpa notificações antigas se exceder o limite
                self._cleanup_old_notifications(user_id)

            # Envia a notificação em tempo real, se solicitado
            if send_realtime and self.websocket_manager:
                self.websocket_manager.send_to_user(
                    user_id,
                    'notification',
                    notification
                )
                logger.info(f"Notificação enviada em tempo real para o usuário {user_id}")

            logger.info(f"Notificação criada para o usuário {user_id}: {notification_type}")
            return notification_id

        except Exception as e:
            logger.error(f"Erro ao criar notificação: {str(e)}")
            return None

    def send_match_notification(self, user_id: int, match_data: Dict[str, Any]) -> Optional[int]:
        """
        Envia uma notificação de nova correspondência para um usuário.

        Args:
            user_id: ID do usuário
            match_data: Dados da correspondência

        Returns:
            ID da notificação criada ou None em caso de erro
        """
        try:
            job_title = match_data.get('job', {}).get('title', 'uma vaga')
            company = match_data.get('job', {}).get('company', '')
            score = match_data.get('score', 0)

            # Formata a mensagem
            message = f"Encontramos uma correspondência de {score:.0f}% para {job_title}"
            if company:
                message += f" na {company}"

            # Cria a notificação
            notification_id = self.create_notification(
                user_id=user_id,
                notification_type='new_match',
                title='Nova vaga compatível',
                message=message,
                data={
                    'match_id': match_data.get('id'),
                    'job_id': match_data.get('job_id'),
                    'score': score
                }
            )

            return notification_id

        except Exception as e:
            logger.error(f"Erro ao enviar notificação de correspondência: {str(e)}")
            return None

    def send_recommendation_notification(self, user_id: int, job_id: int, recommendation_data: Dict[str, Any]) -> \
    Optional[int]:
        """
        Envia uma notificação de recomendação para um usuário.

        Args:
            user_id: ID do usuário
            job_id: ID da vaga
            recommendation_data: Dados da recomendação

        Returns:
            ID da notificação criada ou None em caso de erro
        """
        try:
            job_title = recommendation_data.get('job_title', 'uma vaga')

            # Cria a notificação
            notification_id = self.create_notification(
                user_id=user_id,
                notification_type='match_recommendation',
                title='Recomendações para candidatura',
                message=f"Temos sugestões para melhorar sua candidatura para {job_title}",
                data={
                    'job_id': job_id,
                    'recommendation_id': recommendation_data.get('id')
                }
            )

            return notification_id

        except Exception as e:
            logger.error(f"Erro ao enviar notificação de recomendação: {str(e)}")
            return None

    def send_profile_recommendation_notification(self, user_id: int, recommendations: List[str]) -> Optional[int]:
        """
        Envia uma notificação de recomendação de perfil para um usuário.

        Args:
            user_id: ID do usuário
            recommendations: Lista de recomendações

        Returns:
            ID da notificação criada ou None em caso de erro
        """
        try:
            # Limita o número de recomendações
            if len(recommendations) > 3:
                recommendations = recommendations[:3]

            # Cria a notificação
            notification_id = self.create_notification(
                user_id=user_id,
                notification_type='profile_recommendation',
                title='Melhore seu perfil',
                message=f"Temos {len(recommendations)} sugestões para melhorar seu perfil",
                data={
                    'recommendations': recommendations
                }
            )

            return notification_id

        except Exception as e:
            logger.error(f"Erro ao enviar notificação de recomendação de perfil: {str(e)}")
            return None

    def send_job_update_notification(self, user_id: int, job_data: Dict[str, Any]) -> Optional[int]:
        """
        Envia uma notificação de atualização de vaga para um usuário.

        Args:
            user_id: ID do usuário
            job_data: Dados da vaga atualizada

        Returns:
            ID da notificação criada ou None em caso de erro
        """
        try:
            job_title = job_data.get('title', 'Uma vaga')
            company = job_data.get('company', '')

            # Formata a mensagem
            message = f"{job_title}"
            if company:
                message += f" na {company}"
            message += " foi atualizada"

            # Cria a notificação
            notification_id = self.create_notification(
                user_id=user_id,
                notification_type='job_update',
                title='Vaga atualizada',
                message=message,
                data={
                    'job_id': job_data.get('id')
                }
            )

            return notification_id

        except Exception as e:
            logger.error(f"Erro ao enviar notificação de atualização de vaga: {str(e)}")
            return None

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Marca uma notificação como lida.

        Args:
            notification_id: ID da notificação
            user_id: ID do usuário (para verificação)

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.notification_repository:
            logger.warning("Repositório de notificações não disponível")
            return False

        try:
            # Busca a notificação
            notification = self.notification_repository.find_by_id(notification_id)

            if not notification:
                logger.warning(f"Notificação não encontrada: {notification_id}")
                return False

            # Verifica se a notificação pertence ao usuário
            if notification.get('user_id') != user_id:
                logger.warning(f"Tentativa de acesso a notificação de outro usuário: {notification_id}")
                return False

            # Atualiza a notificação
            success = self.notification_repository.update(
                notification_id,
                {'read': True}
            )

            return success

        except Exception as e:
            logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
            return False

    def mark_all_as_read(self, user_id: int) -> bool:
        """
        Marca todas as notificações de um usuário como lidas.

        Args:
            user_id: ID do usuário

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.notification_repository:
            logger.warning("Repositório de notificações não disponível")
            return False

        try:
            # Atualiza todas as notificações do usuário
            success = self.notification_repository.mark_all_as_read(user_id)

            # Notifica clientes conectados
            if success and self.websocket_manager:
                self.websocket_manager.send_to_user(
                    user_id,
                    'notifications_read_all',
                    {'status': 'success'}
                )

            return success

        except Exception as e:
            logger.error(f"Erro ao marcar todas notificações como lidas: {str(e)}")
            return False

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        Exclui uma notificação.

        Args:
            notification_id: ID da notificação
            user_id: ID do usuário (para verificação)

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.notification_repository:
            logger.warning("Repositório de notificações não disponível")
            return False

        try:
            # Busca a notificação
            notification = self.notification_repository.find_by_id(notification_id)

            if not notification:
                logger.warning(f"Notificação não encontrada: {notification_id}")
                return False

            # Verifica se a notificação pertence ao usuário
            if notification.get('user_id') != user_id:
                logger.warning(f"Tentativa de excluir notificação de outro usuário: {notification_id}")
                return False

            # Exclui a notificação
            success = self.notification_repository.delete(notification_id)

            # Notifica clientes conectados
            if success and self.websocket_manager:
                self.websocket_manager.send_to_user(
                    user_id,
                    'notification_deleted',
                    {'id': notification_id}
                )

            return success

        except Exception as e:
            logger.error(f"Erro ao excluir notificação: {str(e)}")
            return False

    def get_user_notifications(self, user_id: int, limit: int = 20, offset: int = 0, unread_only: bool = False) -> List[
        Dict[str, Any]]:
        """
        Obtém as notificações de um usuário.

        Args:
            user_id: ID do usuário
            limit: Número máximo de notificações a retornar
            offset: Deslocamento para paginação
            unread_only: Se True, retorna apenas notificações não lidas

        Returns:
            Lista de notificações do usuário
        """
        if not self.notification_repository:
            logger.warning("Repositório de notificações não disponível")
            return []

        try:
            # Busca as notificações do usuário
            notifications = self.notification_repository.find_by_user(
                user_id,
                limit=limit,
                offset=offset,
                unread_only=unread_only
            )

            return notifications

        except Exception as e:
            logger.error(f"Erro ao buscar notificações do usuário: {str(e)}")
            return []

    def get_unread_count(self, user_id: int) -> int:
        """
        Obtém o número de notificações não lidas de um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Número de notificações não lidas
        """
        if not self.notification_repository:
            logger.warning("Repositório de notificações não disponível")
            return 0

        try:
            # Busca o número de notificações não lidas
            count = self.notification_repository.count_unread(user_id)

            return count

        except Exception as e:
            logger.error(f"Erro ao contar notificações não lidas: {str(e)}")
            return 0

    def broadcast_notification(self, users: List[int], notification_type: str, title: str, message: str,
                               data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Envia uma notificação para múltiplos usuários.

        Args:
            users: Lista de IDs de usuários
            notification_type: Tipo de notificação
            title: Título da notificação
            message: Mensagem da notificação
            data: Dados adicionais da notificação (opcional)

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            success = True

            for user_id in users:
                notification_id = self.create_notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    data=data
                )

                if not notification_id:
                    success = False

            return success

        except Exception as e:
            logger.error(f"Erro ao transmitir notificação: {str(e)}")
            return False

    def _cleanup_old_notifications(self, user_id: int) -> bool:
        """
        Limpa notificações antigas de um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.notification_repository:
            return False

        try:
            # Conta o número de notificações do usuário
            count = self.notification_repository.count_by_user(user_id)

            # Se exceder o limite, remove as mais antigas
            if count > self.max_notifications_per_user:
                excess = count - self.max_notifications_per_user
                self.notification_repository.delete_oldest(user_id, excess)
                logger.info(f"Removidas {excess} notificações antigas do usuário {user_id}")

            return True

        except Exception as e:
            logger.error(f"Erro ao limpar notificações antigas: {str(e)}")
            return False