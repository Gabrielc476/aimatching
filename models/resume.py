"""
Modelo de currículo para o LinkedIn Job Matcher.

Este módulo define o modelo de currículo que armazena documentos
de currículo enviados pelos usuários, junto com metadados e conteúdo
analisado pelo sistema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, JSON, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from .base import ModelBase, TimestampMixin


class Resume(ModelBase, TimestampMixin):
    """
    Modelo de currículo do LinkedIn Job Matcher.

    Armazena arquivos de currículo enviados pelos usuários junto com
    informações extraídas e estruturadas pela análise de IA.
    """

    __tablename__ = 'resumes'

    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', back_populates='resumes')

    # Informações do arquivo
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    content = Column(LargeBinary, nullable=True)  # Conteúdo binário do arquivo

    # Texto extraído e análise
    raw_text = Column(Text, nullable=True)  # Texto extraído do arquivo
    parsed_content = Column(JSON, nullable=True)  # Conteúdo estruturado após análise

    # Informações estruturadas
    skills = Column(JSON, nullable=True)
    experience = Column(JSON, nullable=True)
    education = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)

    # Status e preferências
    is_primary = Column(Boolean, default=False, nullable=False)
    analysis_status = Column(String(50), default='pending', nullable=False)
    last_analyzed_at = Column(DateTime, nullable=True)

    # Relacionamentos
    matches = relationship('Match', back_populates='resume')

    def __init__(self, user_id, filename, content_type, content=None):
        """
        Inicializa uma nova instância de currículo.

        Args:
            user_id (int): ID do usuário proprietário do currículo
            filename (str): Nome do arquivo de currículo
            content_type (str): Tipo MIME do arquivo
            content (bytes, optional): Conteúdo binário do arquivo
        """
        self.user_id = user_id
        self.filename = filename
        self.content_type = content_type
        self.content = content
        self.skills = {}
        self.experience = []
        self.education = []
        self.certifications = []
        self.languages = []

    def set_as_primary(self):
        """Define este currículo como o principal do usuário."""
        self.is_primary = True

    def update_analysis_status(self, status):
        """
        Atualiza o status de análise do currículo.

        Args:
            status (str): Novo status ('pending', 'processing', 'completed', 'failed')
        """
        self.analysis_status = status
        if status == 'completed':
            self.last_analyzed_at = datetime.utcnow()

    def update_parsed_content(self, parsed_data):
        """
        Atualiza o conteúdo analisado do currículo.

        Args:
            parsed_data (dict): Dados estruturados extraídos do currículo
        """
        self.parsed_content = parsed_data

        # Atualizar campos específicos se fornecidos
        if 'skills' in parsed_data:
            self.skills = parsed_data['skills']
        if 'experience' in parsed_data:
            self.experience = parsed_data['experience']
        if 'education' in parsed_data:
            self.education = parsed_data['education']
        if 'certifications' in parsed_data:
            self.certifications = parsed_data['certifications']
        if 'languages' in parsed_data:
            self.languages = parsed_data['languages']

    def to_dict(self, include_content=False):
        """
        Converte o currículo para um dicionário.

        Args:
            include_content (bool): Se deve incluir o conteúdo binário

        Returns:
            dict: Representação do currículo como dicionário
        """
        resume_dict = {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'content_type': self.content_type,
            'is_primary': self.is_primary,
            'analysis_status': self.analysis_status,
            'skills': self.skills,
            'experience': self.experience,
            'education': self.education,
            'certifications': self.certifications,
            'languages': self.languages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_analyzed_at': self.last_analyzed_at.isoformat() if self.last_analyzed_at else None
        }

        # Incluir conteúdo apenas se solicitado
        if include_content and self.content:
            resume_dict['content'] = self.content

        return resume_dict

    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename='{self.filename}', status='{self.analysis_status}')>"