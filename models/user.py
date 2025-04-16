"""
Modelo de usuário para o LinkedIn Job Matcher.

Este módulo define o modelo de usuário que representa os usuários
registrados no sistema.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .base import ModelBase, TimestampMixin


class User(ModelBase, TimestampMixin):
    """
    Modelo de usuário do LinkedIn Job Matcher.

    Armazena informações de autenticação e identificação do usuário,
    além de relacionamentos com perfil, currículos e correspondências.
    """

    __tablename__ = 'users'

    # Campos de autenticação e identificação
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    # Status do usuário
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relacionamentos
    profile = relationship('Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    resumes = relationship('Resume', back_populates='user', cascade='all, delete-orphan')
    matches = relationship('Match', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, email, password, name):
        """
        Inicializa uma nova instância de usuário.

        Args:
            email (str): Email do usuário, usado para login
            password (str): Senha do usuário (será hasheada)
            name (str): Nome completo do usuário
        """
        self.email = email
        self.set_password(password)
        self.name = name

    def set_password(self, password):
        """
        Define a senha do usuário, armazenando-a como hash.

        Args:
            password (str): Senha em texto puro
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.

        Args:
            password (str): Senha em texto puro para verificar

        Returns:
            bool: True se a senha está correta, False caso contrário
        """
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Atualiza o timestamp do último login para o momento atual."""
        self.last_login = datetime.utcnow()

    def to_dict(self, include_relationships=False):
        """
        Converte o usuário para um dicionário, excluindo dados sensíveis.

        Args:
            include_relationships (bool): Se deve incluir dados de relacionamentos

        Returns:
            dict: Representação do usuário como dicionário
        """
        user_dict = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

        # Opcionalmente incluir relacionamentos
        if include_relationships and self.profile:
            user_dict['profile'] = self.profile.to_dict()

        return user_dict

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"