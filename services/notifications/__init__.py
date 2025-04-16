"""
Serviços de notificações em tempo real.

Este pacote contém os serviços responsáveis por gerenciar notificações
em tempo real, incluindo notificações WebSocket e gestão de eventos.
"""

from .notification_service import NotificationService
from .websocket_manager import WebSocketManager

__all__ = ['NotificationService', 'WebSocketManager']