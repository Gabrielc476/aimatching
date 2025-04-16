"""
Modelo de correspondência para o LinkedIn Job Matcher.

Este módulo define o modelo de correspondência que associa currículos
de usuários a vagas de emprego, junto com métricas de compatibilidade
e detalhes da análise.
"""

from sqlalchemy import Column, Integer, Float, String, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import ModelBase, TimestampMixin


class Match(ModelBase, TimestampMixin):
    """
    Modelo de correspondência do LinkedIn Job Matcher.

    Representa uma correspondência entre um currículo de usuário
    e uma vaga de emprego, incluindo pontuação e detalhes da análise.
    """

    __tablename__ = 'matches'

    # Relacionamentos
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False, index=True)

    user = relationship('User', back_populates='matches')
    job = relationship('Job', back_populates='matches')
    resume = relationship('Resume', back_populates='matches')

    # Pontuações de correspondência
    score = Column(Float, nullable=False, index=True)
    skills_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)

    # Detalhes da correspondência
    match_details = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    matching_skills = Column(JSON, nullable=True)

    # Recomendações e análise
    recommendations = Column(JSON, nullable=True)
    strength_areas = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)

    # Estado da correspondência
    status = Column(String(50), default='new', nullable=False, index=True)
    is_viewed = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_applied = Column(Boolean, default=False, nullable=False)
    application_notes = Column(String(512), nullable=True)

    # Versão do algoritmo
    algorithm_version = Column(String(50), nullable=True)

    def __init__(self, user_id, job_id, resume_id, score):
        """
        Inicializa uma nova instância de correspondência.

        Args:
            user_id (int): ID do usuário
            job_id (int): ID da vaga
            resume_id (int): ID do currículo
            score (float): Pontuação de correspondência (0-100)
        """
        self.user_id = user_id
        self.job_id = job_id
        self.resume_id = resume_id
        self.score = score
        self.status = 'new'
        self.match_details = {}
        self.missing_skills = []
        self.matching_skills = []
        self.recommendations = {}

    def update_scores(self, skills_score=None, experience_score=None, education_score=None):
        """
        Atualiza as pontuações detalhadas da correspondência.

        Args:
            skills_score (float, optional): Pontuação de compatibilidade de habilidades
            experience_score (float, optional): Pontuação de compatibilidade de experiência
            education_score (float, optional): Pontuação de compatibilidade de formação
        """
        if skills_score is not None:
            self.skills_score = skills_score
        if experience_score is not None:
            self.experience_score = experience_score
        if education_score is not None:
            self.education_score = education_score

    def mark_as_viewed(self):
        """Marca a correspondência como visualizada pelo usuário."""
        self.is_viewed = True

    def mark_as_favorite(self):
        """Marca a correspondência como favorita pelo usuário."""
        self.is_favorite = True

    def mark_as_applied(self, notes=None):
        """
        Marca a correspondência como aplicada pelo usuário.

        Args:
            notes (str, optional): Notas sobre a candidatura
        """
        self.is_applied = True
        self.status = 'applied'

        if notes:
            self.application_notes = notes

    def update_status(self, status):
        """
        Atualiza o status da correspondência.

        Args:
            status (str): Novo status ('new', 'viewed', 'applied', 'interview', 'rejected', 'offer', 'hired')
        """
        self.status = status

        # Atualizar flags relacionadas
        if status in ['applied', 'interview', 'offer', 'hired']:
            self.is_applied = True
        if status != 'new':
            self.is_viewed = True

    def update_match_details(self, details):
        """
        Atualiza os detalhes da correspondência.

        Args:
            details (dict): Detalhes da correspondência
        """
        self.match_details = details

        # Atualizar campos específicos se fornecidos
        if 'missing_skills' in details:
            self.missing_skills = details['missing_skills']
        if 'matching_skills' in details:
            self.matching_skills = details['matching_skills']
        if 'recommendations' in details:
            self.recommendations = details['recommendations']
        if 'strength_areas' in details:
            self.strength_areas = details['strength_areas']
        if 'improvement_areas' in details:
            self.improvement_areas = details['improvement_areas']

    def to_dict(self, include_details=True):
        """
        Converte a correspondência para um dicionário.

        Args:
            include_details (bool): Se deve incluir detalhes completos

        Returns:
            dict: Representação da correspondência como dicionário
        """
        match_dict = {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'score': self.score,
            'skills_score': self.skills_score,
            'experience_score': self.experience_score,
            'education_score': self.education_score,
            'status': self.status,
            'is_viewed': self.is_viewed,
            'is_favorite': self.is_favorite,
            'is_applied': self.is_applied,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Incluir detalhes completos se solicitado
        if include_details:
            match_dict.update({
                'match_details': self.match_details,
                'missing_skills': self.missing_skills,
                'matching_skills': self.matching_skills,
                'recommendations': self.recommendations,
                'strength_areas': self.strength_areas,
                'improvement_areas': self.improvement_areas,
                'application_notes': self.application_notes,
                'algorithm_version': self.algorithm_version
            })

        return match_dict

    def __repr__(self):
        return f"<Match(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, score={self.score}, status='{self.status}')>"