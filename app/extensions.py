"""
Extensões Flask para o LinkedIn Job Matcher.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_caching import Cache
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Banco de dados
db = SQLAlchemy()

# Autenticação com JWT
jwt = JWTManager()

# Migrações de banco de dados
migrate = Migrate()

# Cache (Redis)
cache = Cache()

# WebSockets para notificações em tempo real
socketio = SocketIO()

# Limitador de taxa para proteção contra abuso
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)