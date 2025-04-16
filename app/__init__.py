"""
Inicialização do aplicativo Flask para o LinkedIn Job Matcher.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api  # Import Flask-RESTful Api

from .config import config_by_name
from .extensions import db, jwt, migrate, cache, socketio, limiter


def create_app(config_name=None):
    """
    Cria e configura a aplicação Flask.

    Args:
        config_name: Nome da configuração a ser usada (development, production, testing)

    Returns:
        Flask app configurado
    """
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = config_by_name[config_name].get_db_uri_with_encoding()

    # Inicializa extensões
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    limiter.init_app(app)

    # Cria uma instância da API Flask-RESTful
    api = Api(app)

    # Registra blueprints e rotas da API
    from api.routes import register_routes
    register_routes(api)  # Passa a instância da API, não o app

    # Registra manipuladores de erro
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """Registra os manipuladores de erro da aplicação."""
    from flask import jsonify

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Forbidden", "message": "You don't have permission to access this resource"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "The requested resource was not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(
            {"error": "Method Not Allowed", "message": "The method is not allowed for the requested URL"}), 405

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({"error": "Too Many Requests", "message": "Rate limit exceeded"}), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal Server Error", "message": "An internal server error occurred"}), 500