"""
Mapeador de habilidades para normalização e categorização.

Este módulo contém a implementação do mapeador de habilidades que normaliza
e categoriza habilidades para facilitar a correspondência entre currículos e vagas.
"""

import logging
import json
import re
import os
from typing import Dict, List, Set, Union, Any, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class SkillMapper:
    """
    Mapeador de habilidades para normalização e categorização.

    Esta classe implementa métodos para normalizar, categorizar e mapear
    habilidades de currículos e vagas, facilitando a correspondência.
    """

    def __init__(self, skill_map_file: str = None):
        """
        Inicializa o mapeador de habilidades.

        Args:
            skill_map_file: Caminho para o arquivo JSON com o mapeamento de habilidades
        """
        # Dicionário de normalização: variações -> forma normalizada
        self.skill_map = {}

        # Mapeamento de categorias de habilidades
        self.categories = {
            'technical': set(),  # Habilidades técnicas
            'soft': set(),  # Habilidades não-técnicas
            'languages': set(),  # Idiomas
            'tools': set(),  # Ferramentas e software
            'frameworks': set(),  # Frameworks
            'databases': set(),  # Bancos de dados
            'platforms': set(),  # Plataformas e serviços
            'certifications': set(),  # Certificações
            'methodologies': set()  # Metodologias
        }

        # Lista de sinônimos para cada habilidade
        self.synonyms = {}

        # Carrega o mapeamento de habilidades
        if skill_map_file and os.path.exists(skill_map_file):
            self._load_from_file(skill_map_file)
        else:
            self._load_default_mappings()

    def _load_from_file(self, file_path: str):
        """
        Carrega o mapeamento de habilidades de um arquivo JSON.

        Args:
            file_path: Caminho para o arquivo JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Carrega o mapa de normalização
                if 'skill_map' in data:
                    self.skill_map = data['skill_map']

                # Carrega as categorias
                if 'categories' in data:
                    for category, skills in data['categories'].items():
                        self.categories[category] = set(skills)

                # Carrega os sinônimos
                if 'synonyms' in data:
                    self.synonyms = data['synonyms']

            logger.info(f"Mapeamento de habilidades carregado de {file_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar mapeamento de habilidades: {str(e)}")
            # Carrega o mapeamento padrão em caso de erro
            self._load_default_mappings()

    def _load_default_mappings(self):
        """Carrega um mapeamento padrão de habilidades."""
        # Normalização de linguagens de programação
        self.skill_map.update({
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'typescript': 'TypeScript',
            'ts': 'TypeScript',
            'python': 'Python',
            'py': 'Python',
            'java': 'Java',
            'c#': 'C#',
            'csharp': 'C#',
            'c++': 'C++',
            'cpp': 'C++',
            'php': 'PHP',
            'ruby': 'Ruby',
            'go': 'Go',
            'golang': 'Go',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'rust': 'Rust',
            'scala': 'Scala',
            'perl': 'Perl',
            'r': 'R (language)',
        })

        # Normalização de frameworks e bibliotecas
        self.skill_map.update({
            'react': 'React',
            'reactjs': 'React',
            'react.js': 'React',
            'angular': 'Angular',
            'angularjs': 'AngularJS',
            'angular.js': 'AngularJS',
            'vue': 'Vue.js',
            'vuejs': 'Vue.js',
            'vue.js': 'Vue.js',
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'node.js': 'Node.js',
            'express': 'Express.js',
            'expressjs': 'Express.js',
            'django': 'Django',
            'flask': 'Flask',
            'spring': 'Spring',
            'spring boot': 'Spring Boot',
            '.net': '.NET',
            'dotnet': '.NET',
            'laravel': 'Laravel',
            'rails': 'Ruby on Rails',
            'ror': 'Ruby on Rails',
            'ruby on rails': 'Ruby on Rails',
        })

        # Normalização de bancos de dados
        self.skill_map.update({
            'sql': 'SQL',
            'nosql': 'NoSQL',
            'postgresql': 'PostgreSQL',
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongo': 'MongoDB',
            'mongodb': 'MongoDB',
            'oracle': 'Oracle',
            'sqlserver': 'SQL Server',
            'sql server': 'SQL Server',
            'sqlite': 'SQLite',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'elastic search': 'Elasticsearch',
            'dynamo': 'DynamoDB',
            'dynamodb': 'DynamoDB',
        })

        # Normalização de plataformas e serviços
        self.skill_map.update({
            'aws': 'AWS',
            'amazon web services': 'AWS',
            'azure': 'Azure',
            'microsoft azure': 'Azure',
            'gcp': 'Google Cloud',
            'google cloud': 'Google Cloud',
            'firebase': 'Firebase',
            'heroku': 'Heroku',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'jenkins': 'Jenkins',
            'git': 'Git',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'bitbucket': 'Bitbucket',
        })

        # Normalização de ferramentas e software
        self.skill_map.update({
            'vs code': 'Visual Studio Code',
            'vscode': 'Visual Studio Code',
            'visual studio': 'Visual Studio',
            'intellij': 'IntelliJ IDEA',
            'pycharm': 'PyCharm',
            'webstorm': 'WebStorm',
            'eclipse': 'Eclipse',
            'jira': 'Jira',
            'confluence': 'Confluence',
            'trello': 'Trello',
            'slack': 'Slack',
            'photoshop': 'Adobe Photoshop',
            'illustrator': 'Adobe Illustrator',
            'xd': 'Adobe XD',
            'figma': 'Figma',
            'sketch': 'Sketch',
        })

        # Normalização de metodologias
        self.skill_map.update({
            'agile': 'Agile',
            'ágil': 'Agile',
            'scrum': 'Scrum',
            'kanban': 'Kanban',
            'lean': 'Lean',
            'waterfall': 'Waterfall',
            'cascata': 'Waterfall',
            'tdd': 'TDD',
            'bdd': 'BDD',
            'xp': 'XP',
            'extreme programming': 'XP',
            'devops': 'DevOps',
            'ci/cd': 'CI/CD',
            'cicd': 'CI/CD',
            'continuous integration': 'CI/CD',
            'continuous delivery': 'CI/CD',
        })

        # Normalização de habilidades não-técnicas
        self.skill_map.update({
            'comunicação': 'Comunicação',
            'communication': 'Comunicação',
            'trabalho em equipe': 'Trabalho em Equipe',
            'teamwork': 'Trabalho em Equipe',
            'liderança': 'Liderança',
            'leadership': 'Liderança',
            'resolução de problemas': 'Resolução de Problemas',
            'problem solving': 'Resolução de Problemas',
            'pensamento crítico': 'Pensamento Crítico',
            'critical thinking': 'Pensamento Crítico',
            'proativo': 'Proatividade',
            'proatividade': 'Proatividade',
            'proactive': 'Proatividade',
            'adaptabilidade': 'Adaptabilidade',
            'adaptability': 'Adaptabilidade',
            'flexibilidade': 'Flexibilidade',
            'flexibility': 'Flexibilidade',
            'gerenciamento de tempo': 'Gerenciamento de Tempo',
            'time management': 'Gerenciamento de Tempo',
            'negociação': 'Negociação',
            'negotiation': 'Negociação',
        })

        # Categoriza algumas habilidades
        # Habilidades técnicas
        self.categories['technical'] = {
            'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'PHP', 'Ruby', 'Go',
            'Swift', 'Kotlin', 'Rust', 'Scala', 'Perl', 'R (language)', 'HTML', 'CSS', 'SQL'
        }

        # Habilidades não-técnicas
        self.categories['soft'] = {
            'Comunicação', 'Trabalho em Equipe', 'Liderança', 'Resolução de Problemas',
            'Pensamento Crítico', 'Proatividade', 'Adaptabilidade', 'Flexibilidade',
            'Gerenciamento de Tempo', 'Negociação', 'Criatividade', 'Empatia', 'Persuasão'
        }

        # Frameworks
        self.categories['frameworks'] = {
            'React', 'Angular', 'AngularJS', 'Vue.js', 'Node.js', 'Express.js', 'Django',
            'Flask', 'Spring', 'Spring Boot', '.NET', 'Laravel', 'Ruby on Rails'
        }

        # Bancos de dados
        self.categories['databases'] = {
            'SQL', 'NoSQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Oracle', 'SQL Server',
            'SQLite', 'Redis', 'Elasticsearch', 'DynamoDB'
        }

        # Plataformas e serviços
        self.categories['platforms'] = {
            'AWS', 'Azure', 'Google Cloud', 'Firebase', 'Heroku', 'Docker', 'Kubernetes',
            'Jenkins', 'Git', 'GitHub', 'GitLab', 'Bitbucket'
        }

        # Ferramentas
        self.categories['tools'] = {
            'Visual Studio Code', 'Visual Studio', 'IntelliJ IDEA', 'PyCharm', 'WebStorm',
            'Eclipse', 'Jira', 'Confluence', 'Trello', 'Slack', 'Adobe Photoshop',
            'Adobe Illustrator', 'Adobe XD', 'Figma', 'Sketch'
        }

        # Metodologias
        self.categories['methodologies'] = {
            'Agile', 'Scrum', 'Kanban', 'Lean', 'Waterfall', 'TDD', 'BDD', 'XP',
            'DevOps', 'CI/CD'
        }

        # Sinônimos para algumas habilidades
        self.synonyms = {
            'JavaScript': ['JS', 'ECMAScript', 'Node.js'],
            'Python': ['Py', 'Django', 'Flask'],
            'AWS': ['Amazon Web Services', 'EC2', 'S3', 'Lambda'],
            'Agile': ['Scrum', 'Kanban', 'Sprint'],
            'SQL': ['Database', 'Queries', 'PostgreSQL', 'MySQL'],
            'DevOps': ['CI/CD', 'Continuous Integration', 'Continuous Deployment'],
        }

        logger.info("Mapeamento padrão de habilidades carregado")

    def normalize_skill(self, skill: str) -> str:
        """
        Normaliza uma habilidade para sua forma padrão.

        Args:
            skill: Habilidade a ser normalizada

        Returns:
            Forma normalizada da habilidade
        """
        if not skill:
            return ""

        # Normaliza a string (remove espaços extras, converte para minúsculas)
        normalized = skill.strip().lower()

        # Tenta encontrar a forma normalizada no mapa
        if normalized in self.skill_map:
            return self.skill_map[normalized]

        # Se não encontrar, tenta encontrar uma correspondência parcial
        best_match = None
        best_score = 0

        for key, value in self.skill_map.items():
            if key in normalized or normalized in key:
                # Se for uma correspondência exata (substring), retorna o valor
                if len(key) > best_score:
                    best_score = len(key)
                    best_match = value
            elif SequenceMatcher(None, key, normalized).ratio() > 0.8:
                # Se for uma correspondência próxima, considera como opção
                match_score = SequenceMatcher(None, key, normalized).ratio() * len(key)
                if match_score > best_score:
                    best_score = match_score
                    best_match = value

        if best_match:
            return best_match

        # Se não encontrar nenhuma correspondência, retorna a habilidade original
        # com a primeira letra maiúscula
        return skill[0].upper() + skill[1:] if skill else ""

    def normalize_skills(self, skills: Union[List[str], Dict[str, List[str]]]) -> Dict[str, List[str]]:
        """
        Normaliza uma lista de habilidades ou um dicionário de habilidades categorizadas.

        Args:
            skills: Lista de habilidades ou dicionário com habilidades categorizadas

        Returns:
            Dicionário com habilidades normalizadas e categorizadas
        """
        normalized = {'technical': [], 'soft': []}

        if isinstance(skills, list):
            # Se for uma lista de habilidades, normaliza cada uma e categoriza
            for skill in skills:
                if not skill:
                    continue

                norm_skill = self.normalize_skill(skill)
                category = self.categorize_skill(norm_skill)

                if category in normalized:
                    if norm_skill not in normalized[category]:
                        normalized[category].append(norm_skill)
                else:
                    # Se a categoria não existir, coloca em 'technical' por padrão
                    if norm_skill not in normalized['technical']:
                        normalized['technical'].append(norm_skill)
        elif isinstance(skills, dict):
            # Se for um dicionário, normaliza mantendo as categorias originais
            for category, skill_list in skills.items():
                if not skill_list:
                    continue

                if category not in normalized:
                    normalized[category] = []

                for skill in skill_list:
                    norm_skill = self.normalize_skill(skill)
                    if norm_skill and norm_skill not in normalized[category]:
                        normalized[category].append(norm_skill)

        return normalized

    def categorize_skill(self, skill: str) -> str:
        """
        Determina a categoria de uma habilidade.

        Args:
            skill: Habilidade a ser categorizada

        Returns:
            Categoria da habilidade: 'technical', 'soft', etc.
        """
        # Normaliza a habilidade para correspondência exata
        norm_skill = self.normalize_skill(skill)

        # Verifica em qual categoria a habilidade se encaixa
        for category, skills in self.categories.items():
            if norm_skill in skills:
                return category

        # Se for uma habilidade não-técnica comum, categoriza como 'soft'
        soft_patterns = [
            'comunicação', 'comunica', 'communication',
            'equipe', 'team', 'grupo', 'group',
            'lideran', 'lead', 'gestão', 'management',
            'resolução', 'solv', 'problem', 'problema',
            'crítico', 'critical', 'think', 'pens',
            'criativ', 'creativ', 'inovat', 'inov',
            'adaptab', 'flex', 'empatia', 'empathy',
            'organiza', 'planeja', 'plan', 'aprend',
            'learn', 'collabor', 'colabor', 'confli',
            'negoci', 'negot', 'persua', 'relationship',
            'relacionamento', 'motivação', 'motivat'
        ]

        skill_lower = skill.lower()
        for pattern in soft_patterns:
            if pattern in skill_lower:
                return 'soft'

        # Por padrão, considera como habilidade técnica
        return 'technical'

    def find_synonyms(self, skill: str) -> List[str]:
        """
        Encontra sinônimos para uma habilidade.

        Args:
            skill: Habilidade para a qual buscar sinônimos

        Returns:
            Lista de sinônimos da habilidade
        """
        # Normaliza a habilidade
        norm_skill = self.normalize_skill(skill)

        # Verifica se há sinônimos diretos
        if norm_skill in self.synonyms:
            return self.synonyms[norm_skill]

        # Verifica se a habilidade é sinônimo de outra
        for key, synonyms in self.synonyms.items():
            if norm_skill in synonyms:
                result = [key] + [s for s in synonyms if s != norm_skill]
                return result

        # Tenta encontrar correspondências parciais
        related = []
        for key, synonyms in self.synonyms.items():
            if (norm_skill in key.lower() or any(norm_skill in s.lower() for s in synonyms) or
                    key.lower() in norm_skill or any(s.lower() in norm_skill for s in synonyms)):
                related.append(key)
                related.extend([s for s in synonyms if s != key])

        if related:
            return list(set(related))

        # Se não encontrar nada, retorna apenas a habilidade original
        return [norm_skill]

    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calcula a similaridade entre duas habilidades.

        Args:
            skill1: Primeira habilidade
            skill2: Segunda habilidade

        Returns:
            Pontuação de similaridade entre 0 e 1
        """
        # Normaliza as habilidades
        norm1 = self.normalize_skill(skill1)
        norm2 = self.normalize_skill(skill2)

        # Se forem idênticas após normalização
        if norm1 == norm2:
            return 1.0

        # Verifica se são sinônimas
        synonyms1 = self.find_synonyms(norm1)
        if norm2 in synonyms1:
            return 0.9

        # Verifica se uma contém a outra
        if norm1 in norm2 or norm2 in norm1:
            return 0.8

        # Calcula a similaridade pelo algoritmo SequenceMatcher
        ratio = SequenceMatcher(None, norm1.lower(), norm2.lower()).ratio()

        return ratio

    def find_most_similar_skill(self, skill: str, skill_list: List[str]) -> Tuple[str, float]:
        """
        Encontra a habilidade mais similar na lista.

        Args:
            skill: Habilidade a ser comparada
            skill_list: Lista de habilidades para comparação

        Returns:
            Tupla contendo a habilidade mais similar e a pontuação de similaridade
        """
        if not skill_list:
            return skill, 0.0

        best_match = skill_list[0]
        best_score = self.calculate_skill_similarity(skill, best_match)

        for candidate in skill_list[1:]:
            score = self.calculate_skill_similarity(skill, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        return best_match, best_score

    def expand_skills(self, skills: List[str]) -> List[str]:
        """
        Expande uma lista de habilidades com seus sinônimos.

        Args:
            skills: Lista de habilidades a expandir

        Returns:
            Lista expandida de habilidades
        """
        expanded = set()

        for skill in skills:
            # Adiciona a habilidade normalizada
            norm_skill = self.normalize_skill(skill)
            expanded.add(norm_skill)

            # Adiciona os sinônimos
            synonyms = self.find_synonyms(norm_skill)
            expanded.update(synonyms)

        return list(expanded)

    def save_to_file(self, file_path: str):
        """
        Salva o mapeamento de habilidades em um arquivo JSON.

        Args:
            file_path: Caminho para o arquivo JSON
        """
        try:
            # Converte os conjuntos para listas para serialização JSON
            categories_dict = {
                category: list(skills)
                for category, skills in self.categories.items()
            }

            data = {
                'skill_map': self.skill_map,
                'categories': categories_dict,
                'synonyms': self.synonyms
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Mapeamento de habilidades salvo em {file_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar mapeamento de habilidades: {str(e)}")

    def add_skill_mapping(self, variant: str, normalized: str, category: str = None):
        """
        Adiciona um novo mapeamento de habilidade.

        Args:
            variant: Variante da habilidade
            normalized: Forma normalizada da habilidade
            category: Categoria da habilidade (opcional)
        """
        variant = variant.strip().lower()

        if not variant or not normalized:
            return

        self.skill_map[variant] = normalized

        if category and category in self.categories:
            self.categories[category].add(normalized)

        logger.info(f"Adicionado mapeamento: {variant} -> {normalized} ({category if category else 'sem categoria'})")

    def add_skill_synonyms(self, skill: str, synonyms: List[str]):
        """
        Adiciona sinônimos para uma habilidade.

        Args:
            skill: Habilidade principal
            synonyms: Lista de sinônimos
        """
        norm_skill = self.normalize_skill(skill)

        if not norm_skill or not synonyms:
            return

        if norm_skill in self.synonyms:
            # Adiciona aos sinônimos existentes
            existing = self.synonyms[norm_skill]
            for synonym in synonyms:
                if synonym and synonym not in existing:
                    existing.append(synonym)
        else:
            # Cria uma nova entrada
            self.synonyms[norm_skill] = [s for s in synonyms if s]

        logger.info(f"Adicionados sinônimos para {norm_skill}: {', '.join(synonyms)}")