"""
Serviços de correspondência entre currículos e vagas.

Este pacote contém os serviços responsáveis por analisar currículos e vagas
e calcular a correspondência entre eles, utilizando algoritmos de processamento
de linguagem natural e o modelo Claude 3.7 Sonnet.
"""

from .match_service import MatchService
from .resume_analyzer import ResumeAnalyzer
from .job_analyzer import JobAnalyzer
from .skill_mapper import SkillMapper

__all__ = [
    'MatchService',
    'ResumeAnalyzer',
    'JobAnalyzer',
    'SkillMapper'
]