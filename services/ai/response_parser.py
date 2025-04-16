"""
Parser de respostas do Claude 3.7 Sonnet.

Este módulo contém a implementação do parser de respostas do Claude,
responsável por extrair e estruturar informações das respostas do modelo.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ResponseParser:
    """
    Parser de respostas do Claude 3.7 Sonnet.

    Esta classe implementa métodos para extrair e estruturar informações
    das respostas do modelo Claude 3.7 Sonnet.
    """

    def extract_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extrai um objeto JSON de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com o JSON extraído ou None se não encontrar
        """
        try:
            # Verifica se há um bloco JSON explícito
            json_pattern = r'```(?:json)?\s*({\s*.*?\s*})```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)

            # Tenta encontrar JSON sem marcadores de código
            json_pattern_alt = r'({(?:[^{}]|(?R))*})'
            json_match_alt = re.search(json_pattern_alt, response_text, re.DOTALL)

            if json_match_alt:
                json_str = json_match_alt.group(1)
                return json.loads(json_str)

            # Tenta encontrar todo o texto como JSON
            try:
                json_data = json.loads(response_text)
                if isinstance(json_data, dict):
                    return json_data
            except json.JSONDecodeError:
                pass

            # Se não encontrar JSON, retorna None
            logger.warning("Não foi possível extrair JSON da resposta")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair JSON: {str(e)}")
            return None

    def extract_lists(self, response_text: str) -> Dict[str, List[str]]:
        """
        Extrai listas de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com listas extraídas por seção
        """
        lists = {}

        # Procura por seções com listas
        section_pattern = r'(?:^|\n)([A-Z][^:]+):\s*\n((?:\s*[-*]\s+[^\n]+\n?)+)'
        section_matches = re.finditer(section_pattern, response_text, re.MULTILINE)

        for match in section_matches:
            section_name = match.group(1).strip()
            list_text = match.group(2)

            # Extrai itens da lista
            items = []
            item_pattern = r'[-*]\s+([^\n]+)'
            item_matches = re.finditer(item_pattern, list_text)

            for item_match in item_matches:
                items.append(item_match.group(1).strip())

            lists[section_name] = items

        # Se não encontrar seções, procura por listas isoladas
        if not lists:
            items = []
            item_pattern = r'[-*]\s+([^\n]+)'
            item_matches = re.finditer(item_pattern, response_text)

            for item_match in item_matches:
                items.append(item_match.group(1).strip())

            if items:
                lists['Items'] = items

        return lists

    def extract_sections(self, response_text: str) -> Dict[str, str]:
        """
        Extrai seções de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com seções extraídas
        """
        sections = {}

        # Procura por seções no formato "Título: Conteúdo"
        section_pattern = r'(?:^|\n)([A-Z][^:]+):\s*\n((?:.+\n?)+?)(?=\n[A-Z][^:]+:|\n\n|\Z)'
        section_matches = re.finditer(section_pattern, response_text, re.MULTILINE)

        for match in section_matches:
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_name] = section_content

        return sections

    def structure_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Estrutura recomendações de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Lista de recomendações estruturadas
        """
        recommendations = []

        # Extrai seções
        sections = self.extract_sections(response_text)

        # Procura por recomendações específicas
        recom_pattern = r'(?:^|\n)(\d+|\*)\.\s+(.+?)(?=\n(?:\d+|\*)\.|$)'

        for section_name, section_content in sections.items():
            recom_matches = re.finditer(recom_pattern, section_content, re.DOTALL)

            for match in recom_matches:
                number = match.group(1)
                content = match.group(2).strip()

                # Verifica se há um título na recomendação
                title_match = re.match(r'([^:.]+)[:.-]\s*(.*)', content)

                if title_match:
                    title = title_match.group(1).strip()
                    description = title_match.group(2).strip()

                    recommendations.append({
                        'category': section_name,
                        'title': title,
                        'description': description
                    })
                else:
                    recommendations.append({
                        'category': section_name,
                        'description': content
                    })

        # Se não encontrar recomendações estruturadas, tenta extrair de listas
        if not recommendations:
            lists = self.extract_lists(response_text)

            for category, items in lists.items():
                for item in items:
                    # Verifica se há um título na recomendação
                    title_match = re.match(r'([^:.]+)[:.-]\s*(.*)', item)

                    if title_match:
                        title = title_match.group(1).strip()
                        description = title_match.group(2).strip()

                        recommendations.append({
                            'category': category,
                            'title': title,
                            'description': description
                        })
                    else:
                        recommendations.append({
                            'category': category,
                            'description': item
                        })

        # Se ainda não encontrar, cria uma única recomendação com o texto completo
        if not recommendations:
            recommendations.append({
                'category': 'Geral',
                'description': response_text.strip()
            })

        return recommendations

    def extract_scores(self, response_text: str) -> Dict[str, float]:
        """
        Extrai pontuações de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com pontuações extraídas
        """
        scores = {}

        # Procura por pontuações no formato "Categoria: XX%" ou "Categoria: XX/100"
        score_pattern = r'([A-Za-z\s]+):\s*(\d+(?:\.\d+)?)(?:\s*%|\s*/\s*100)?'
        score_matches = re.finditer(score_pattern, response_text)

        for match in score_matches:
            category = match.group(1).strip()
            score = float(match.group(2))

            # Normaliza para 0-100
            if score <= 1:
                score *= 100

            scores[category] = score

        return scores

    def extract_key_value_pairs(self, response_text: str) -> Dict[str, str]:
        """
        Extrai pares chave-valor de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com pares chave-valor extraídos
        """
        pairs = {}

        # Procura por pares no formato "Chave: Valor"
        pair_pattern = r'([A-Za-z\s]+):\s*(.+?)(?=\n[A-Za-z][^:]+:|\n\n|\Z)'
        pair_matches = re.finditer(pair_pattern, response_text, re.MULTILINE)

        for match in pair_matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            pairs[key] = value

        return pairs

    def parse_skills(self, response_text: str) -> Dict[str, List[str]]:
        """
        Extrai habilidades de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com habilidades técnicas e não-técnicas
        """
        skills = {
            'technical': [],
            'soft': []
        }

        # Procura por seções de habilidades
        technical_patterns = [
            r'(?:Technical|Hard|Tech|Programming|Tecnol[óo]gicas) Skills?:?\s*\n((?:\s*[-*]\s+[^\n]+\n?)+)',
            r'(?:Technical|Hard|Tech|Programming|Tecnol[óo]gicas) Skills?:?\s*\n((?:.+\n?)+?)(?=\n[A-Z][^:]+:|\n\n|\Z)'
        ]

        soft_patterns = [
            r'(?:Soft|Non-technical|Interpersonal|Non[- ]?tech|Comportamentais) Skills?:?\s*\n((?:\s*[-*]\s+[^\n]+\n?)+)',
            r'(?:Soft|Non-technical|Interpersonal|Non[- ]?tech|Comportamentais) Skills?:?\s*\n((?:.+\n?)+?)(?=\n[A-Z][^:]+:|\n\n|\Z)'
        ]

        # Extrai habilidades técnicas
        for pattern in technical_patterns:
            match = re.search(pattern, response_text, re.MULTILINE | re.IGNORECASE)
            if match:
                content = match.group(1)

                # Tenta extrair itens de lista
                item_pattern = r'[-*]\s+([^\n]+)'
                item_matches = re.finditer(item_pattern, content)

                for item_match in item_matches:
                    skill = item_match.group(1).strip()
                    if skill and skill not in skills['technical']:
                        skills['technical'].append(skill)

                # Se não encontrar itens de lista, divide por vírgulas
                if not skills['technical']:
                    comma_items = content.split(',')
                    skills['technical'] = [item.strip() for item in comma_items if item.strip()]

                break

        # Extrai habilidades não-técnicas
        for pattern in soft_patterns:
            match = re.search(pattern, response_text, re.MULTILINE | re.IGNORECASE)
            if match:
                content = match.group(1)

                # Tenta extrair itens de lista
                item_pattern = r'[-*]\s+([^\n]+)'
                item_matches = re.finditer(item_pattern, content)

                for item_match in item_matches:
                    skill = item_match.group(1).strip()
                    if skill and skill not in skills['soft']:
                        skills['soft'].append(skill)

                # Se não encontrar itens de lista, divide por vírgulas
                if not skills['soft']:
                    comma_items = content.split(',')
                    skills['soft'] = [item.strip() for item in comma_items if item.strip()]

                break

        return skills

    def parse_match_result(self, response_text: str) -> Dict[str, Any]:
        """
        Parseia um resultado de correspondência de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com resultado de correspondência estruturado
        """
        # Tenta extrair JSON primeiro
        json_result = self.extract_json(response_text)
        if json_result:
            return json_result

        # Se não encontrar JSON, tenta extrair manualmente
        result = {
            'score_overall': 0.0,
            'score_details': {},
            'matching_skills': [],
            'missing_skills': [],
            'strengths': [],
            'recommendations': []
        }

        # Extrai pontuações
        scores = self.extract_scores(response_text)

        for key, score in scores.items():
            key_lower = key.lower()

            if 'overall' in key_lower or 'geral' in key_lower or 'total' in key_lower:
                result['score_overall'] = score
            elif 'technical' in key_lower or 'técnicas' in key_lower:
                result['score_details']['technical_skills'] = score
            elif 'soft' in key_lower or 'não-técnicas' in key_lower:
                result['score_details']['soft_skills'] = score
            elif 'experience' in key_lower or 'experiência' in key_lower:
                result['score_details']['experience'] = score
            elif 'education' in key_lower or 'formação' in key_lower or 'educação' in key_lower:
                result['score_details']['education'] = score
            else:
                # Outras pontuações
                normalized_key = key.lower().replace(' ', '_')
                result['score_details'][normalized_key] = score

        # Extrai listas
        lists = self.extract_lists(response_text)

        for section, items in lists.items():
            section_lower = section.lower()

            if 'matching' in section_lower or 'correspondente' in section_lower:
                result['matching_skills'] = items
            elif 'missing' in section_lower or 'faltante' in section_lower or 'gap' in section_lower:
                result['missing_skills'] = items
            elif 'strength' in section_lower or 'forte' in section_lower or 'positive' in section_lower:
                result['strengths'] = items
            elif 'recommendation' in section_lower or 'recomendação' in section_lower or 'suggest' in section_lower:
                result['recommendations'] = items

        return result

    def parse_resume_analysis(self, response_text: str) -> Dict[str, Any]:
        """
        Parseia uma análise de currículo de uma resposta em texto.

        Args:
            response_text: Texto da resposta do Claude

        Returns:
            Dicionário com análise de currículo estruturada
        """
        # Tenta extrair JSON primeiro
        json_result = self.extract_json(response_text)
        if json_result:
            return json_result

        # Se não encontrar JSON, tenta extrair manualmente
        result = {
            'personal_info': {},
            'skills': {
                'technical': [],
                'soft': []
            },
            'experience': [],
            'education': [],
            'certifications': [],
            'languages': []
        }

        # Extrai seções
        sections = self.extract_sections(response_text)

        # Processa cada seção
        for section_name, section_content in sections.items():
            section_lower = section_name.lower()

            if 'personal' in section_lower or 'pessoal' in section_lower:
                # Extrai informações pessoais
                pairs = self.extract_key_value_pairs(section_content)
                result['personal_info'] = pairs

            elif 'skill' in section_lower or 'habilidade' in section_lower:
                # Extrai habilidades
                skills = self.parse_skills(section_content)
                result['skills'] = skills

            elif 'experience' in section_lower or 'experiência' in section_lower:
                # Extrai experiência
                experiences = []

                # Tenta dividir experiências por padrões comuns
                exp_pattern = r'(?:^|\n)([^:\n]+):\s*([^:\n]+)(?:(?:\n|,\s*)([^:\n]+))?(?:\n|,\s*)(?:(\d{4})\s*-\s*(\d{4}|\w+))?'
                exp_matches = re.finditer(exp_pattern, section_content)

                for match in exp_matches:
                    title = match.group(1).strip() if match.group(1) else ""
                    company = match.group(2).strip() if match.group(2) else ""
                    location = match.group(3).strip() if match.group(3) else ""
                    start_date = match.group(4) if match.group(4) else ""
                    end_date = match.group(5) if match.group(5) else ""

                    exp = {
                        'title': title,
                        'company': company
                    }

                    if location:
                        exp['location'] = location
                    if start_date:
                        exp['start_date'] = start_date
                    if end_date:
                        exp['end_date'] = end_date

                    experiences.append(exp)

                result['experience'] = experiences

            elif 'education' in section_lower or 'formação' in section_lower or 'educação' in section_lower:
                # Extrai educação
                education = []

                # Tenta dividir educação por padrões comuns
                edu_pattern = r'(?:^|\n)([^:\n]+):\s*([^:\n]+)(?:(?:\n|,\s*)([^:\n]+))?(?:\n|,\s*)(?:(\d{4})\s*-\s*(\d{4}|\w+))?'
                edu_matches = re.finditer(edu_pattern, section_content)

                for match in edu_matches:
                    degree = match.group(1).strip() if match.group(1) else ""
                    institution = match.group(2).strip() if match.group(2) else ""
                    field = match.group(3).strip() if match.group(3) else ""
                    start_date = match.group(4) if match.group(4) else ""
                    end_date = match.group(5) if match.group(5) else ""

                    edu = {
                        'degree': degree,
                        'institution': institution
                    }

                    if field:
                        edu['field_of_study'] = field
                    if start_date:
                        edu['start_date'] = start_date
                    if end_date:
                        edu['end_date'] = end_date

                    education.append(edu)

                result['education'] = education

            elif 'certification' in section_lower or 'certificação' in section_lower:
                # Extrai certificações
                certifications = []

                # Tenta extrair certificações de lista
                cert_pattern = r'[-*]\s+([^\n]+)'
                cert_matches = re.finditer(cert_pattern, section_content)

                for match in cert_matches:
                    cert = match.group(1).strip()
                    if cert:
                        certifications.append({'name': cert})

                result['certifications'] = certifications

            elif 'language' in section_lower or 'idioma' in section_lower:
                # Extrai idiomas
                languages = []

                # Tenta extrair idiomas de lista
                lang_pattern = r'[-*]\s+([^\n]+)'
                lang_matches = re.finditer(lang_pattern, section_content)

                for match in lang_matches:
                    lang = match.group(1).strip()

                    # Tenta separar idioma e proficiência
                    parts = lang.split('-', 1)

                    if len(parts) > 1:
                        language = parts[0].strip()
                        proficiency = parts[1].strip()
                        languages.append({
                            'language': language,
                            'proficiency': proficiency
                        })
                    else:
                        languages.append({
                            'language': lang,
                            'proficiency': "Não especificado"
                        })

                result['languages'] = languages

        return result