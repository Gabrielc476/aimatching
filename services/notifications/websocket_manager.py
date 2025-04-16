"""
Gerenciador de conexões WebSocket.

Este módulo contém a implementação do gerenciador de conexões WebSocket
para comunicação em tempo real com os clientes.
"""

import logging
import json
from typing import Dict, List, Set, Any, Optional, Callable, Union
from datetime import datetime
import asyncio

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
except ImportError:
    SocketIO = None
    emit = None
    join_room = None
    leave_room = None

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Gerenciador de conexões WebSocket.

    Esta classe implementa métodos para gerenciar conexões WebSocket
    e enviar mensagens em tempo real para os clientes.
    """

    def __init__(self, socketio: Optional['SocketIO'] = None):
        """
        Inicializa o gerenciador de WebSockets.

        Args:
            socketio: Instância do SocketIO da aplicação (opcional)
        """
        self.socketio = socketio
        self.connected_users: Dict[int, Set[str]] = {}  # user_id -> set of session_ids
        self.session_to_user: Dict[str, int] = {}  # session_id -> user_id
        self.event_handlers: Dict[str, List[Callable]] = {}  # event_name -> list of handlers

    def init_app(self, app, socketio: 'SocketIO'):
        """
        Inicializa o gerenciador com a aplicação Flask e SocketIO.

        Args:
            app: Aplicação Flask
            socketio: Instância do SocketIO
        """
        self.socketio = socketio

        # Registra handlers para eventos de conexão
        @socketio.on('connect')
        def handle_connect():
            logger.info(f"Cliente conectado: {self._get_sid()}")

        @socketio.on('disconnect')
        def handle_disconnect():
            sid = self._get_sid()
            logger.info(f"Cliente desconectado: {sid}")
            self._remove_session(sid)

        @socketio.on('register')
        def handle_register(data):
            sid = self._get_sid()
            try:
                user_id = data.get('user_id')
                token = data.get('token')

                if not user_id or not token:
                    logger.warning(f"Tentativa de registro sem user_id ou token: {sid}")
                    emit('register_error', {'error': 'ID de usuário e token são obrigatórios'})
                    return

                # Aqui você pode validar o token
                # Este é um exemplo simples; em produção, você deve validar o token
                # com seu serviço de autenticação

                # Registra o usuário
                self._register_user(int(user_id), sid)
                emit('register_success', {'user_id': user_id})
                logger.info(f"Usuário {user_id} registrado com sid {sid}")

            except Exception as e:
                logger.error(f"Erro ao registrar usuário: {str(e)}")
                emit('register_error', {'error': 'Erro ao registrar usuário'})

        @socketio.on_error()
        def handle_error(e):
            logger.error(f"Erro WebSocket: {str(e)}")

        logger.info("WebSocketManager inicializado com aplicação Flask")

    def register_event_handler(self, event_name: str, handler: Callable):
        """
        Registra um handler para um evento específico.

        Args:
            event_name: Nome do evento
            handler: Função a ser chamada quando o evento ocorrer
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

        self.event_handlers[event_name].append(handler)
        logger.info(f"Handler registrado para evento {event_name}")

    def send_to_user(self, user_id: int, event: str, data: Any):
        """
        Envia uma mensagem para um usuário específico.

        Args:
            user_id: ID do usuário
            event: Nome do evento
            data: Dados a serem enviados
        """
        if not self.socketio:
            logger.warning("SocketIO não está inicializado")
            return

        try:
            # Adiciona timestamp
            message_data = {
                **data,
                'timestamp': datetime.utcnow().isoformat() if isinstance(data, dict) else None
            }

            # Verifica se o usuário está conectado
            if user_id in self.connected_users:
                # Emite o evento para a sala do usuário
                self.socketio.emit(event, message_data, room=f"user_{user_id}")
                logger.debug(f"Mensagem enviada para usuário {user_id}: {event}")

                # Executa handlers registrados para o evento
                self._execute_event_handlers(event, user_id, message_data)
            else:
                logger.debug(f"Usuário {user_id} não está conectado, mensagem não enviada")

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para usuário {user_id}: {str(e)}")

    def broadcast(self, event: str, data: Any, include_users: Optional[List[int]] = None,
                  exclude_users: Optional[List[int]] = None):
        """
        Transmite uma mensagem para todos os usuários conectados.

        Args:
            event: Nome do evento
            data: Dados a serem enviados
            include_users: Lista de IDs de usuários para incluir (opcional)
            exclude_users: Lista de IDs de usuários para excluir (opcional)
        """
        if not self.socketio:
            logger.warning("SocketIO não está inicializado")
            return

        try:
            # Adiciona timestamp
            message_data = {
                **data,
                'timestamp': datetime.utcnow().isoformat() if isinstance(data, dict) else None
            }

            if include_users:
                # Envia apenas para usuários específicos
                for user_id in include_users:
                    self.send_to_user(user_id, event, message_data)
            else:
                # Envia para todos, exceto os excluídos
                exclude_rooms = [f"user_{user_id}" for user_id in (exclude_users or [])]

                # Emite o evento para todos
                self.socketio.emit(event, message_data, skip_sid=exclude_rooms)
                logger.debug(f"Mensagem transmitida para todos os usuários: {event}")

                # Executa handlers registrados para o evento
                self._execute_event_handlers(event, None, message_data)

        except Exception as e:
            logger.error(f"Erro ao transmitir mensagem: {str(e)}")

    def get_connected_users(self) -> List[int]:
        """
        Obtém a lista de IDs de usuários conectados.

        Returns:
            Lista de IDs de usuários conectados
        """
        return list(self.connected_users.keys())

    def is_user_connected(self, user_id: int) -> bool:
        """
        Verifica se um usuário está conectado.

        Args:
            user_id: ID do usuário

        Returns:
            True se o usuário está conectado, False caso contrário
        """
        return user_id in self.connected_users and len(self.connected_users[user_id]) > 0

    def disconnect_user(self, user_id: int, reason: Optional[str] = None):
        """
        Desconecta todas as sessões de um usuário.

        Args:
            user_id: ID do usuário
            reason: Motivo da desconexão (opcional)
        """
        if not self.socketio:
            logger.warning("SocketIO não está inicializado")
            return

        if user_id not in self.connected_users:
            logger.debug(f"Usuário {user_id} não está conectado")
            return

        try:
            # Obtém as sessões do usuário
            sessions = list(self.connected_users.get(user_id, set()))

            # Desconecta cada sessão
            for sid in sessions:
                self.socketio.disconnect(sid, namespace='/')

            # Limpa as sessões do usuário
            self.connected_users.pop(user_id, None)

            # Remove os mapeamentos de sessão para usuário
            for sid in sessions:
                self.session_to_user.pop(sid, None)

            logger.info(f"Usuário {user_id} desconectado: {reason or 'sem motivo'}")

        except Exception as e:
            logger.error(f"Erro ao desconectar usuário {user_id}: {str(e)}")

    def _register_user(self, user_id: int, session_id: str):
        """
        Registra um usuário com uma sessão WebSocket.

        Args:
            user_id: ID do usuário
            session_id: ID da sessão WebSocket
        """
        # Cria a entrada para o usuário se não existir
        if user_id not in self.connected_users:
            self.connected_users[user_id] = set()

        # Adiciona a sessão ao conjunto de sessões do usuário
        self.connected_users[user_id].add(session_id)

        # Mapeia a sessão para o usuário
        self.session_to_user[session_id] = user_id

        # Adiciona a sessão à sala do usuário
        if join_room:
            join_room(f"user_{user_id}")

        logger.debug(f"Usuário {user_id} registrado com sessão {session_id}")

    def _remove_session(self, session_id: str):
        """
        Remove uma sessão WebSocket.

        Args:
            session_id: ID da sessão WebSocket
        """
        # Verifica se a sessão está mapeada para um usuário
        if session_id in self.session_to_user:
            user_id = self.session_to_user.pop(session_id)

            # Remove a sessão do conjunto de sessões do usuário
            if user_id in self.connected_users:
                self.connected_users[user_id].discard(session_id)

                # Remove o usuário se não tiver mais sessões
                if not self.connected_users[user_id]:
                    self.connected_users.pop(user_id)

            # Remove a sessão da sala do usuário
            if leave_room:
                leave_room(f"user_{user_id}")

            logger.debug(f"Sessão {session_id} removida do usuário {user_id}")
        else:
            logger.debug(f"Sessão {session_id} não está associada a nenhum usuário")

    def _get_sid(self) -> str:
        """
        Obtém o ID da sessão WebSocket atual.

        Returns:
            ID da sessão WebSocket
        """
        from flask_socketio import request
        return request.sid

    def _execute_event_handlers(self, event: str, user_id: Optional[int], data: Any):
        """
        Executa os handlers registrados para um evento.

        Args:
            event: Nome do evento
            user_id: ID do usuário (None para broadcast)
            data: Dados do evento
        """
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        # Se for uma função assíncrona, agenda sua execução
                        asyncio.create_task(handler(user_id, data))
                    else:
                        # Se for uma função síncrona, executa diretamente
                        handler(user_id, data)
                except Exception as e:
                    logger.error(f"Erro ao executar handler para evento {event}: {str(e)}")