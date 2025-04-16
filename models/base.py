"""
Modelo base para todos os modelos do LinkedIn Job Matcher.

Este módulo define a classe Base que serve como classe base para todos
os modelos SQLAlchemy no sistema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Cria a classe Base para os modelos SQLAlchemy
Base = declarative_base()


class TimestampMixin:
    """
    Mixin para adicionar campos de timestamp a modelos.

    Adiciona created_at e updated_at automaticamente para
    rastrear quando registros foram criados e atualizados.
    """

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ModelBase(Base):
    """
    Classe base abstrata para todos os modelos.

    Define campos e métodos comuns que devem estar presentes em
    todos os modelos do sistema.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)

    def to_dict(self):
        """
        Converte o modelo para um dicionário.

        Returns:
            dict: Representação do modelo como dicionário
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}