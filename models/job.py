"""
Modelo de vaga para o LinkedIn Job Matcher.

Este módulo define o modelo de vaga de emprego, que armazena informações
sobre vagas extraídas do LinkedIn através de scraping.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import ModelBase, TimestampMixin


class Job(ModelBase, TimestampMixin):
    """
    Modelo de vaga de emprego do LinkedIn Job Matcher.

    Armazena informações sobre vagas coletadas do LinkedIn,
    incluindo requisitos, descrições e metadados.
    """

    __tablename__ = 'jobs'

    # Identificação da vaga
    linkedin_id = Column(String(255), unique=True, nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    company_logo_url = Column(String(512), nullable=True)

    # Localização e tipo de vaga
    location = Column(String(255), nullable=True, index=True)
    job_type = Column(String(50), nullable=True, index=True)  # full-time, part-time, contract, etc.
    work_mode = Column(String(50), nullable=True, index=True)  # remote, hybrid, on-site

    # Detalhes da vaga
    description = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    requirements = Column(JSON, nullable=True)
    benefits = Column(Text, nullable=True)

    # Informações de experiência e salário
    experience_level = Column(String(50), nullable=True, index=True)
    salary_range = Column(String(255), nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), nullable=True)

    # Informações categorizadas
    skills = Column(JSON, nullable=True)
    industry = Column(String(100), nullable=True, index=True)
    department = Column(String(100), nullable=True)
    seniority = Column(String(50), nullable=True, index=True)

    # Metadados da vaga
    url = Column(String(512), nullable=False)
    application_url = Column(String(512), nullable=True)
    posted_at = Column(DateTime, nullable=True, index=True)
    closes_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Fonte da vaga
    source_type = Column(String(50), nullable=True)  # 'linkedin_listing', 'linkedin_post', etc.
    source_id = Column(String(255), nullable=True)

    # Análise
    ai_processed = Column(Boolean, default=False, nullable=False)
    ai_process_version = Column(String(50), nullable=True)

    # Relacionamentos
    matches = relationship('Match', back_populates='job')

    def __init__(self, title, company, url, linkedin_id=None, description=None):
        """
        Inicializa uma nova instância de vaga.

        Args:
            title (str): Título da vaga
            company (str): Nome da empresa
            url (str): URL da vaga no LinkedIn
            linkedin_id (str, optional): ID da vaga no LinkedIn
            description (str, optional): Descrição da vaga
        """
        self.title = title
        self.company = company
        self.url = url
        self.linkedin_id = linkedin_id
        self.description = description
        self.scraped_at = datetime.utcnow()

    def mark_as_inactive(self):
        """Marca a vaga como inativa."""
        self.is_active = False
        self.last_updated_at = datetime.utcnow()

    def update_from_scrape(self, data):
        """
        Atualiza a vaga com dados recém-extraídos.

        Args:
            data (dict): Dados atualizados da vaga
        """
        # Atualizar campos com dados fornecidos
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

        self.last_updated_at = datetime.utcnow()

    def parse_salary_range(self, salary_text):
        """
        Extrai e armazena valores mínimo e máximo de um texto de faixa salarial.

        Args:
            salary_text (str): Texto com faixa salarial (ex: "R$ 5.000 - R$ 7.000")
        """
        if not salary_text:
            return

        self.salary_range = salary_text

        # Implementação simplificada - uma implementação real seria mais robusta
        try:
            # Extração básica de valores numéricos
            import re
            numbers = re.findall(r'[\d.]+', salary_text)
            if len(numbers) >= 2:
                self.salary_min = float(numbers[0].replace('.', ''))
                self.salary_max = float(numbers[1].replace('.', ''))

            # Extração da moeda
            currency_match = re.search(r'([A-Z]{3}|\$|R\$|€|£)', salary_text)
            if currency_match:
                self.salary_currency = currency_match.group(1)
        except Exception:
            # Em caso de erro, mantenha apenas o texto original
            pass

    def to_dict(self):
        """
        Converte a vaga para um dicionário.

        Returns:
            dict: Representação da vaga como dicionário
        """
        return {
            'id': self.id,
            'linkedin_id': self.linkedin_id,
            'title': self.title,
            'company': self.company,
            'company_logo_url': self.company_logo_url,
            'location': self.location,
            'job_type': self.job_type,
            'work_mode': self.work_mode,
            'description': self.description,
            'responsibilities': self.responsibilities,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'experience_level': self.experience_level,
            'salary_range': self.salary_range,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'skills': self.skills,
            'industry': self.industry,
            'department': self.department,
            'seniority': self.seniority,
            'url': self.url,
            'application_url': self.application_url,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'closes_at': self.closes_at.isoformat() if self.closes_at else None,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'last_updated_at': self.last_updated_at.isoformat() if self.last_updated_at else None,
            'is_active': self.is_active,
            'source_type': self.source_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}', active={self.is_active})>"