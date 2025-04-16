"""
Serviço principal de correspondência entre currículos e vagas.

Este módulo contém a implementação do serviço de correspondência que coordena
a análise de currículos e vagas e calcula a pontuação de compatibilidade.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .resume_analyzer import ResumeAnalyzer
from .job_analyzer import JobAnalyzer
from .skill_mapper import SkillMapper
from ..ai.claude_service import ClaudeService

logger = logging.getLogger(__name__)


class MatchService:
    """
    Serviço responsável por calcular a correspondência entre currículos e vagas.

    Esta classe coordena o processo de análise de currículos e vagas,
    mapeamento de habilidades e cálculo de pontuação de compatibilidade.
    """

    def __init__(self,
                 resume_analyzer: ResumeAnalyzer = None,
                 job_analyzer: JobAnalyzer = None,
                 skill_mapper: SkillMapper = None,
                 claude_service: ClaudeService = None,
                 match_repository=None):
        """
        Inicializa o serviço de correspondência.

        Args:
            resume_analyzer: Analisador de currículos
            job_analyzer: Analisador de vagas
            skill_mapper: Mapeador de habilidades
            claude_service: Serviço de integração com Claude 3.7 Sonnet
            match_repository: Repositório para persistência de correspondências
        """
        self.resume_analyzer = resume_analyzer or ResumeAnalyzer()
        self.job_analyzer = job_analyzer or JobAnalyzer()
        self.skill_mapper = skill_mapper or SkillMapper()
        self.claude_service = claude_service or ClaudeService()
        self.match_repository = match_repository

        # Pesos para diferentes componentes da correspondência
        self.weights = {
            'skills_technical': 0.35,
            'skills_soft': 0.15,
            'experience': 0.25,
            'education': 0.15,
            'job_title_match': 0.10
        }

    def calculate_match(
            self,
            resume_data: Dict[str, Any],
            job_data: Dict[str, Any],
            use_claude: bool = True
    ) -> Dict[str, Any]:
        """
        Calcula a correspondência entre um currículo e uma vaga.

        Args:
            resume_data: Dados do currículo analisado
            job_data: Dados da vaga analisada
            use_claude: Se True, usa o Claude 3.7 para calcular a correspondência

        Returns:
            Dicionário com pontuação e detalhes da correspondência
        """
        logger.info(f"Calculando correspondência entre currículo e vaga: {job_data.get('title', 'Sem título')}")

        # Se utilizarmos o Claude para correspondência, delegamos o cálculo
        if use_claude and self.claude_service:
            try:
                match_result = self.claude_service.calculate_match(resume_data, job_data)

                # Adiciona timestamp
                match_result['created_at'] = datetime.utcnow().isoformat()

                logger.info(
                    f"Correspondência calculada pelo Claude com pontuação: {match_result.get('score_overall', 0)}")
                return match_result

            except Exception as e:
                logger.error(f"Erro ao calcular correspondência com Claude: {str(e)}")
                logger.info("Recorrendo ao algoritmo de correspondência interno")
                # Continua com o algoritmo interno em caso de falha

        # Caso contrário, usamos o algoritmo interno
        try:
            # Mapeia as habilidades para facilitar a comparação
            mapped_resume_skills = self.skill_mapper.normalize_skills(resume_data.get('skills', []))
            mapped_job_skills = self.skill_mapper.normalize_skills(job_data.get('skills', []))

            # Calcula a pontuação de correspondência de habilidades técnicas
            technical_skills_score = self._calculate_skills_match(
                mapped_resume_skills.get('technical', []),
                mapped_job_skills.get('technical', [])
            )

            # Calcula a pontuação de correspondência de habilidades não-técnicas
            soft_skills_score = self._calculate_skills_match(
                mapped_resume_skills.get('soft', []),
                mapped_job_skills.get('soft', [])
            )

            # Calcula a pontuação de correspondência de experiência
            experience_score = self._calculate_experience_match(
                resume_data.get('experience', []),
                job_data
            )

            # Calcula a pontuação de correspondência de formação
            education_score = self._calculate_education_match(
                resume_data.get('education', []),
                job_data
            )

            # Calcula a pontuação de correspondência de título da vaga
            job_title_score = self._calculate_job_title_match(
                resume_data.get('title', ''),
                job_data.get('title', '')
            )

            # Calcula a pontuação geral ponderada
            overall_score = (
                    technical_skills_score * self.weights['skills_technical'] +
                    soft_skills_score * self.weights['skills_soft'] +
                    experience_score * self.weights['experience'] +
                    education_score * self.weights['education'] +
                    job_title_score * self.weights['job_title_match']
            )

            # Normaliza para 0-100
            overall_score = min(100, max(0, overall_score * 100))

            # Identifica habilidades correspondentes e faltantes
            matching_skills, missing_skills = self._identify_skill_gaps(
                mapped_resume_skills.get('technical', []) + mapped_resume_skills.get('soft', []),
                mapped_job_skills.get('technical', []) + mapped_job_skills.get('soft', [])
            )

            # Gera recomendações básicas
            recommendations = self._generate_recommendations(missing_skills, job_data)

            # Constrói o resultado da correspondência
            match_result = {
                'score_overall': round(overall_score, 2),
                'score_details': {
                    'technical_skills': round(technical_skills_score * 100, 2),
                    'soft_skills': round(soft_skills_score * 100, 2),
                    'experience': round(experience_score * 100, 2),
                    'education': round(education_score * 100, 2),
                    'job_title': round(job_title_score * 100, 2)
                },
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'recommendations': recommendations,
                'created_at': datetime.utcnow().isoformat()
            }

            logger.info(f"Correspondência calculada internamente com pontuação: {match_result['score_overall']}")
            return match_result

        except Exception as e:
            logger.error(f"Erro ao calcular correspondência internamente: {str(e)}")

            # Retorna um resultado básico em caso de erro
            return {
                'score_overall': 0,
                'error': str(e),
                'created_at': datetime.utcnow().isoformat()
            }

    def save_match(self, user_id: int, job_id: int, resume_id: int, match_data: Dict[str, Any]) -> Optional[int]:
        """
        Salva o resultado de uma correspondência no banco de dados.

        Args:
            user_id: ID do usuário
            job_id: ID da vaga
            resume_id: ID do currículo
            match_data: Dados da correspondência

        Returns:
            ID da correspondência salva ou None em caso de erro
        """
        if not self.match_repository:
            logger.warning("Repositório de correspondências não configurado")
            return None

        try:
            match_record = {
                'user_id': user_id,
                'job_id': job_id,
                'resume_id': resume_id,
                'score': match_data.get('score_overall', 0),
                'match_details': json.dumps(match_data),
                'created_at': datetime.utcnow(),
                'status': 'new'
            }

            match_id = self.match_repository.create(match_record)
            logger.info(f"Correspondência salva com ID: {match_id}")

            return match_id

        except Exception as e:
            logger.error(f"Erro ao salvar correspondência: {str(e)}")
            return None

    def get_jobs_for_resume(self, resume_id: int, min_score: float = 50.0, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retorna as vagas com melhor correspondência para um currículo.

        Args:
            resume_id: ID do currículo
            min_score: Pontuação mínima para incluir a vaga
            limit: Número máximo de vagas a retornar

        Returns:
            Lista de vagas com suas pontuações de correspondência
        """
        if not self.match_repository:
            logger.warning("Repositório de correspondências não configurado")
            return []

        try:
            matches = self.match_repository.find_by_resume(
                resume_id,
                min_score=min_score,
                limit=limit
            )

            return matches

        except Exception as e:
            logger.error(f"Erro ao buscar vagas para currículo: {str(e)}")
            return []

    def get_resumes_for_job(self, job_id: int, min_score: float = 50.0, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retorna os currículos com melhor correspondência para uma vaga.

        Args:
            job_id: ID da vaga
            min_score: Pontuação mínima para incluir o currículo
            limit: Número máximo de currículos a retornar

        Returns:
            Lista de currículos com suas pontuações de correspondência
        """
        if not self.match_repository:
            logger.warning("Repositório de correspondências não configurado")
            return []

        try:
            matches = self.match_repository.find_by_job(
                job_id,
                min_score=min_score,
                limit=limit
            )

            return matches

        except Exception as e:
            logger.error(f"Erro ao buscar currículos para vaga: {str(e)}")
            return []

    def generate_detailed_recommendations(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[
        str, Any]:
        """
        Gera recomendações detalhadas para melhorar a candidatura a uma vaga.

        Args:
            resume_data: Dados do currículo analisado
            job_data: Dados da vaga analisada

        Returns:
            Dicionário com recomendações detalhadas
        """
        if not self.claude_service:
            logger.warning("Serviço Claude não configurado")
            return {"error": "Serviço de recomendações não disponível"}

        try:
            recommendations = self.claude_service.generate_application_recommendations(
                resume_data,
                job_data
            )

            return recommendations

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações detalhadas: {str(e)}")
            return {"error": f"Erro ao gerar recomendações: {str(e)}"}

    def _calculate_skills_match(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """
        Calcula a correspondência entre as habilidades do currículo e da vaga.

        Args:
            resume_skills: Lista de habilidades do currículo
            job_skills: Lista de habilidades da vaga

        Returns:
            Pontuação entre 0 e 1
        """
        if not job_skills:
            return 1.0  # Se a vaga não especifica habilidades, pontuação máxima

        if not resume_skills:
            return 0.0  # Se o currículo não tem habilidades, pontuação mínima

        # Normaliza todas as habilidades para comparação
        resume_skills_norm = [s.lower() for s in resume_skills]
        job_skills_norm = [s.lower() for s in job_skills]

        # Conta quantas habilidades da vaga estão presentes no currículo
        matches = sum(1 for skill in job_skills_norm if any(s in skill or skill in s for s in resume_skills_norm))

        # Pontuação baseada na proporção de habilidades correspondentes
        score = matches / len(job_skills_norm)

        # Bônus para currículos que têm mais habilidades do que o necessário
        if len(resume_skills_norm) > len(job_skills_norm):
            bonus = min(0.15, (len(resume_skills_norm) - len(job_skills_norm)) / len(job_skills_norm) * 0.15)
            score = min(1.0, score + bonus)

        return score

    def _calculate_experience_match(self, resume_experience: List[Dict[str, Any]], job_data: Dict[str, Any]) -> float:
        """
        Calcula a correspondência entre a experiência do currículo e requisitos da vaga.

        Args:
            resume_experience: Lista de experiências profissionais do currículo
            job_data: Dados da vaga

        Returns:
            Pontuação entre 0 e 1
        """
        if not resume_experience:
            return 0.0

        # Extrai o nível de experiência requerido pela vaga
        job_experience_level = job_data.get('experience_level', '').lower()

        # Mapeia níveis de experiência para valores numéricos
        experience_levels = {
            'estágio': 0,
            'júnior': 1,
            'junior': 1,
            'pleno': 2,
            'sênior': 3,
            'senior': 3,
            'especialista': 3,
            'gerente': 4,
            'diretor': 5,
            'executivo': 6
        }

        # Determina o nível numérico da vaga
        job_level_value = 0
        for level, value in experience_levels.items():
            if level in job_experience_level:
                job_level_value = value
                break

        # Calcula o total de meses de experiência do candidato
        total_months = 0
        relevant_experience = 0

        for exp in resume_experience:
            # Tenta extrair datas de início e fim
            start_date = exp.get('start_date')
            end_date = exp.get('end_date', datetime.utcnow().isoformat())

            # Se não tiver data de início, pula
            if not start_date:
                continue

            # Converte strings ISO para datetime
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

                # Calcula a duração em meses
                months = (end.year - start.year) * 12 + (end.month - start.month)

                total_months += months

                # Verifica se a experiência é relevante para a vaga
                if exp.get('title', '').lower() in job_data.get('title', '').lower() or \
                        job_data.get('title', '').lower() in exp.get('title', '').lower():
                    relevant_experience += months

            except (ValueError, TypeError):
                # Se não conseguir converter as datas, assume 12 meses
                total_months += 12

        # Determina o nível de experiência do candidato
        candidate_level = 0
        if total_months < 6:
            candidate_level = 0  # Estágio
        elif total_months < 24:
            candidate_level = 1  # Júnior
        elif total_months < 60:
            candidate_level = 2  # Pleno
        elif total_months < 96:
            candidate_level = 3  # Sênior
        elif total_months < 120:
            candidate_level = 4  # Gerente
        else:
            candidate_level = 5  # Diretor/Executivo

        # Calcula a pontuação com base na diferença de níveis
        if candidate_level >= job_level_value:
            # Candidato tem experiência igual ou superior ao requerido
            score = 1.0
        else:
            # Candidato tem menos experiência que o requerido
            level_diff = job_level_value - candidate_level
            score = max(0, 1.0 - (level_diff * 0.25))

        # Adiciona bônus por experiência relevante
        if relevant_experience > 0:
            relevance_bonus = min(0.2, relevant_experience / 36 * 0.2)  # Máximo de 20% de bônus
            score = min(1.0, score + relevance_bonus)

        return score

    def _calculate_education_match(self, resume_education: List[Dict[str, Any]], job_data: Dict[str, Any]) -> float:
        """
        Calcula a correspondência entre a formação do currículo e requisitos da vaga.

        Args:
            resume_education: Lista de formações acadêmicas do currículo
            job_data: Dados da vaga

        Returns:
            Pontuação entre 0 e 1
        """
        if not resume_education:
            return 0.0

        # Extrai requisitos de formação da vaga
        job_requirements = job_data.get('requirements', [])
        education_required = False
        required_degree = None
        required_field = None

        # Procura por requisitos de formação nas descrições
        for req in job_requirements:
            req_lower = req.lower()

            # Verifica se há menção a formação
            if any(term in req_lower for term in ['formação', 'graduação', 'ensino', 'degree', 'education']):
                education_required = True

                # Tenta identificar o nível de formação requerido
                if 'superior' in req_lower or 'graduação' in req_lower or 'bachelor' in req_lower:
                    required_degree = 'superior'
                elif 'pós' in req_lower or 'especialização' in req_lower or 'post-grad' in req_lower:
                    required_degree = 'pos'
                elif 'mestrado' in req_lower or 'master' in req_lower:
                    required_degree = 'mestrado'
                elif 'doutorado' in req_lower or 'phd' in req_lower:
                    required_degree = 'doutorado'
                elif 'técnico' in req_lower or 'technical' in req_lower:
                    required_degree = 'tecnico'

                # Tenta identificar a área de formação
                fields = [
                    'computação', 'sistemas', 'ti', 'informática', 'software',
                    'engenharia', 'administração', 'negócios', 'marketing',
                    'design', 'comunicação', 'direito', 'economia',
                    'contabilidade', 'finanças', 'recursos humanos', 'rh'
                ]

                for field in fields:
                    if field in req_lower:
                        required_field = field
                        break

                break

        # Se não há requisito explícito de formação, assume pontuação máxima
        if not education_required:
            return 1.0

        # Mapeia níveis de formação para valores numéricos
        degree_levels = {
            'ensino médio': 1,
            'técnico': 2,
            'superior': 3,
            'graduação': 3,
            'bacharelado': 3,
            'licenciatura': 3,
            'tecnólogo': 3,
            'pós-graduação': 4,
            'especialização': 4,
            'mba': 4,
            'mestrado': 5,
            'doutorado': 6,
            'phd': 6
        }

        # Nível requerido
        required_level = 3  # Assume superior como padrão
        if required_degree:
            for level, value in degree_levels.items():
                if required_degree in level:
                    required_level = value
                    break

        # Verifica a formação do candidato
        candidate_level = 0
        field_match = False

        for edu in resume_education:
            degree = edu.get('degree', '').lower()
            field = edu.get('field_of_study', '').lower()

            # Determina o nível da formação
            level = 0
            for level_name, level_value in degree_levels.items():
                if level_name in degree:
                    level = level_value
                    break

            # Atualiza o nível máximo do candidato
            candidate_level = max(candidate_level, level)

            # Verifica se há correspondência na área de formação
            if required_field and (required_field in field or field in required_field):
                field_match = True

        # Calcula a pontuação com base na diferença de níveis
        if candidate_level >= required_level:
            # Candidato tem formação igual ou superior ao requerido
            level_score = 1.0
        else:
            # Candidato tem formação inferior ao requerido
            level_diff = required_level - candidate_level
            level_score = max(0, 1.0 - (level_diff * 0.3))

        # Ajusta a pontuação com base na correspondência da área
        final_score = level_score
        if required_field:
            if field_match:
                # Bônus por correspondência na área
                final_score = min(1.0, level_score + 0.2)
            else:
                # Penalidade por não corresponder à área
                final_score = max(0, level_score - 0.2)

        return final_score

    def _calculate_job_title_match(self, resume_title: str, job_title: str) -> float:
        """
        Calcula a correspondência entre o título do currículo e o título da vaga.

        Args:
            resume_title: Título ou cargo do candidato no currículo
            job_title: Título da vaga

        Returns:
            Pontuação entre 0 e 1
        """
        if not resume_title or not job_title:
            return 0.5  # Pontuação neutra se faltam informações

        # Normaliza os títulos
        resume_title_norm = resume_title.lower()
        job_title_norm = job_title.lower()

        # Divide os títulos em palavras
        resume_words = set(resume_title_norm.split())
        job_words = set(job_title_norm.split())

        # Remove palavras comuns que não agregam significado
        stop_words = {'de', 'da', 'do', 'e', 'para', 'no', 'na', 'em', 'com', 'o', 'a', 'os', 'as'}
        resume_words = resume_words - stop_words
        job_words = job_words - stop_words

        if not resume_words or not job_words:
            return 0.5

        # Calcula a interseção e união das palavras
        intersection = resume_words.intersection(job_words)
        union = resume_words.union(job_words)

        # Calcula o coeficiente de Jaccard
        jaccard = len(intersection) / len(union)

        # Verifica correspondência direta
        direct_match = False
        for word in resume_words:
            if len(word) > 3 and word in job_title_norm:
                direct_match = True
                break

        # Ajusta a pontuação com base na correspondência direta
        if direct_match:
            return min(1.0, jaccard + 0.3)

        return jaccard

    def _identify_skill_gaps(self, resume_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str]]:
        """
        Identifica habilidades correspondentes e faltantes.

        Args:
            resume_skills: Lista de habilidades do currículo
            job_skills: Lista de habilidades da vaga

        Returns:
            Tupla de (habilidades correspondentes, habilidades faltantes)
        """
        # Normaliza todas as habilidades para comparação
        resume_skills_norm = [s.lower() for s in resume_skills]
        job_skills_norm = [s.lower() for s in job_skills]

        # Identifica habilidades correspondentes
        matching_skills = []
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            for resume_skill in resume_skills:
                resume_skill_lower = resume_skill.lower()
                if job_skill_lower in resume_skill_lower or resume_skill_lower in job_skill_lower:
                    if job_skill not in matching_skills:
                        matching_skills.append(job_skill)
                    break

        # Identifica habilidades faltantes
        missing_skills = []
        for job_skill in job_skills:
            if job_skill not in matching_skills:
                missing_skills.append(job_skill)

        return matching_skills, missing_skills

    def _generate_recommendations(self, missing_skills: List[str], job_data: Dict[str, Any]) -> List[str]:
        """
        Gera recomendações básicas com base nas habilidades faltantes.

        Args:
            missing_skills: Lista de habilidades faltantes
            job_data: Dados da vaga

        Returns:
            Lista de recomendações
        """
        recommendations = []

        # Recomendações baseadas em habilidades faltantes
        if missing_skills:
            recommendations.append(
                f"Adicione ao seu currículo as seguintes habilidades (caso você as possua): {', '.join(missing_skills[:5])}")

            if len(missing_skills) > 5:
                recommendations.append(
                    f"Considere desenvolver conhecimento nas demais habilidades: {', '.join(missing_skills[5:])}")

        # Recomendações baseadas no título da vaga
        job_title = job_data.get('title', '')
        if job_title:
            recommendations.append(f"Adapte seu objetivo profissional para alinhar-se ao cargo de '{job_title}'")

        # Recomendação sobre a experiência
        experience_level = job_data.get('experience_level', '')
        if experience_level and experience_level.lower() in ['pleno', 'sênior', 'senior', 'gerente']:
            recommendations.append("Destaque suas realizações e resultados quantificáveis nas experiências anteriores")

        # Recomendação geral
        recommendations.append(
            "Personalize sua carta de apresentação mencionando especificamente como suas habilidades se alinham com os requisitos desta vaga")

        return recommendations