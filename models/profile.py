"""
Modelo de perfil para o LinkedIn Job Matcher.

Este módulo define o modelo de perfil que armazena informações adicionais
sobre os usuários, incluindo suas preferências e habilidades.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import ModelBase, TimestampMixin


class Profile(ModelBase, TimestampMixin):
    """
    Modelo de perfil do usuário no LinkedIn Job Matcher.

    Armazena informações profissionais e de preferências do usuário,
    complementando as informações básicas do modelo User.
    """

    __tablename__ = 'profiles'

    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    user = relationship('User', back_populates='profile')

    # Informações profissionais
    title = Column(String(255), nullable=True)
    headline = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)

    # Experiência e habilidades
    experience_level = Column(String(50), nullable=True)
    skills = Column(JSON, nullable=True)

    # Preferências de vaga
    job_preferences = Column(JSON, nullable=True)
    salary_expectations = Column(JSON, nullable=True)
    remote_preference = Column(String(50), nullable=True)

    # Visibilidade do perfil
    is_public = Column(Integer, default=0, nullable=False)  # 0: Privado, 1: Público, 2: Apenas Recrutadores

    def __init__(self, user_id, title=None, location=None, skills=None, experience_level=None):
        """
        Inicializa uma nova instância de perfil.

        Args:
            user_id (int): ID do usuário proprietário do perfil
            title (str, optional): Título profissional
            location (str, optional): Localização geográfica
            skills (dict, optional): Habilidades do usuário
            experience_level (str, optional): Nível de experiência
        """
        self.user_id = user_id
        self.title = title
        self.location = location
        self.skills = skills or {}
        self.experience_level = experience_level
        self.job_preferences = {}
        self.salary_expectations = {}

    def update_skills(self, skills):
        """
        Atualiza as habilidades do usuário.

        Args:
            skills (dict): Dicionário de habilidades com níveis
        """
        self.skills = skills

    def update_job_preferences(self, preferences):
        """
        Atualiza as preferências de vaga do usuário.

        Args:
            preferences (dict): Preferências de vaga
        """
        self.job_preferences = preferences

    def update_salary_expectations(self, salary_data):
        """
        Atualiza as expectativas salariais do usuário.

        Args:
            salary_data (dict): Dados de expectativa salarial
        """
        self.salary_expectations = salary_data

    def to_dict(self):
        """
        Converte o perfil para um dicionário.

        Returns:
            dict: Representação do perfil como dicionário
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'headline': self.headline,
            'location': self.location,
            'industry': self.industry,
            'experience_level': self.experience_level,
            'skills': self.skills,
            'job_preferences': self.job_preferences,
            'salary_expectations': self.salary_expectations,
            'remote_preference': self.remote_preference,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Profile(id={self.id}, user_id={self.user_id}, title='{self.title}')>"