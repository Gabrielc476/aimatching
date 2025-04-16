"""
Script para inicializar o banco de dados do LinkedIn Job Matcher.
Cria as tabelas necessárias e um usuário admin inicial.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.extensions import db
from models.user import User
from models.profile import Profile
from models.resume import Resume
from models.job import Job
from models.match import Match
from services.auth.auth_service import AuthService


def init_db():
    """Inicializa o banco de dados com as tabelas e dados iniciais."""
    app = create_app('development')

    with app.app_context():
        # Cria todas as tabelas
        db.create_all()

        # Verifica se já existe um usuário admin
        admin_exists = User.query.filter_by(email='admin@example.com').first()

        if not admin_exists:
            # Cria usuário admin
            auth_service = AuthService()
            user = auth_service.register_user(
                email='admin@example.com',
                password='Admin@123',
                name='Admin User'
            )

            # Cria perfil para o admin
            profile = Profile(
                user_id=user.id,
                title='Administrador',
                location='São Paulo, Brasil',
                skills=['Python', 'Flask', 'Next.js', 'PostgreSQL'],
                experience_level='Senior',
                job_preferences={
                    'remote': True,
                    'job_types': ['full-time', 'contract'],
                    'industries': ['Technology', 'Education']
                }
            )

            db.session.add(profile)
            db.session.commit()

            print("Banco de dados inicializado com sucesso.")
            print("Usuário admin criado:")
            print("  Email: admin@example.com")
            print("  Senha: Admin@123")
        else:
            print("Banco de dados já inicializado.")


if __name__ == '__main__':
    init_db()