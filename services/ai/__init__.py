"""
Serviços de integração com IA.

Este pacote contém os serviços responsáveis pela integração com o modelo
Claude 3.7 Sonnet para análise de currículos, vagas e correspondência.
"""

from .claude_service import ClaudeService
from .prompts import PromptTemplates
from .response_parser import ResponseParser

__all__ = ['ClaudeService', 'PromptTemplates', 'ResponseParser']