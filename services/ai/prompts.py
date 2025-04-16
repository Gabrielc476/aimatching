"""
Templates de prompts para o Claude 3.7 Sonnet.

Este módulo contém os templates de prompts utilizados para interagir
com o modelo Claude 3.7 Sonnet para diferentes tarefas.
"""

import json
from typing import Dict, List, Any


class PromptTemplates:
    """
    Templates de prompts para o Claude 3.7 Sonnet.

    Esta classe fornece métodos para gerar prompts estruturados
    para diferentes tarefas relacionadas a currículos e vagas.
    """

    def get_resume_analysis_prompt(self, resume_text: str) -> str:
        """
        Gera um prompt para análise de currículo.

        Args:
            resume_text: Texto do currículo

        Returns:
            Prompt formatado para envio ao Claude
        """
        prompt = f"""
        Analise o seguinte currículo e extraia as informações mais relevantes no formato JSON:

        ```
        {resume_text}
        ```

        Extraia as seguintes informações:

        1. Informações pessoais (nome, contato)
        2. Habilidades técnicas
        3. Habilidades não-técnicas (soft skills)
        4. Experiência profissional (estruturada com empresa, cargo, período, responsabilidades)
        5. Formação acadêmica (instituição, curso, período)
        6. Certificações
        7. Idiomas

        Estruture o resultado no seguinte formato JSON:

        ```json
        {{
            "personal_info": {{
                "name": "Nome do candidato",
                "email": "email@exemplo.com",
                "phone": "Telefone (se disponível)",
                "location": "Localização (se disponível)"
            }},
            "skills": {{
                "technical": ["Habilidade 1", "Habilidade 2", ...],
                "soft": ["Habilidade 1", "Habilidade 2", ...]
            }},
            "experience": [
                {{
                    "company": "Nome da empresa",
                    "title": "Cargo",
                    "start_date": "Data de início (ISO ou texto)",
                    "end_date": "Data de término (ISO ou 'Presente')",
                    "description": "Descrição das responsabilidades",
                    "achievements": ["Realização 1", "Realização 2", ...]
                }},
                ...
            ],
            "education": [
                {{
                    "institution": "Nome da instituição",
                    "degree": "Grau acadêmico",
                    "field_of_study": "Área de estudo",
                    "start_date": "Data de início",
                    "end_date": "Data de término"
                }},
                ...
            ],
            "certifications": [
                {{
                    "name": "Nome da certificação",
                    "issuer": "Emissor",
                    "date": "Data de emissão",
                    "expires": "Data de expiração (se aplicável)"
                }},
                ...
            ],
            "languages": [
                {{
                    "language": "Idioma",
                    "proficiency": "Nível de proficiência"
                }},
                ...
            ]
        }}
        ```

        Notas importantes:
        - Se alguma informação não estiver disponível, use null ou omita o campo.
        - Extraia apenas informações que estejam explicitamente mencionadas no currículo.
        - Seja preciso nas datas, respeitando o formato encontrado no documento.
        - Para habilidades técnicas, inclua linguagens de programação, frameworks, ferramentas e tecnologias.
        - Para habilidades não-técnicas, inclua competências comportamentais e interpessoais.

        Retorne apenas o JSON sem explicações adicionais.
        """

        return prompt

    def get_job_analysis_prompt(self, job_data: Dict[str, str]) -> str:
        """
        Gera um prompt para análise de vaga.

        Args:
            job_data: Dicionário com dados da vaga (título, empresa, descrição)

        Returns:
            Prompt formatado para envio ao Claude
        """
        prompt = f"""
        Analise a seguinte descrição de vaga e extraia as informações mais relevantes no formato JSON:

        Título: {job_data.get('title', 'Não especificado')}
        Empresa: {job_data.get('company', 'Não especificada')}

        Descrição:
        ```
        {job_data.get('description', '')}
        ```

        Extraia as seguintes informações:

        1. Título da vaga
        2. Empresa
        3. Localização
        4. Tipo de contrato (CLT, PJ, Freelance, etc.)
        5. Nível de experiência requerido
        6. Faixa salarial (se disponível)
        7. Habilidades técnicas necessárias
        8. Habilidades não-técnicas desejáveis
        9. Requisitos
        10. Responsabilidades
        11. Benefícios

        Estruture o resultado no seguinte formato JSON:

        ```json
        {{
            "title": "Título da vaga",
            "company": "Nome da empresa",
            "location": "Localização",
            "job_type": "Tipo de contrato",
            "experience_level": "Nível de experiência",
            "salary_range": "Faixa salarial (se disponível)",
            "skills": {{
                "technical": ["Habilidade 1", "Habilidade 2", ...],
                "soft": ["Habilidade 1", "Habilidade 2", ...]
            }},
            "requirements": ["Requisito 1", "Requisito 2", ...],
            "responsibilities": ["Responsabilidade 1", "Responsabilidade 2", ...],
            "benefits": ["Benefício 1", "Benefício 2", ...],
            "is_remote": true/false,
            "keywords": ["Palavra-chave 1", "Palavra-chave 2", ...]
        }}
        ```

        Notas importantes:
        - Se alguma informação não estiver disponível, use null ou omita o campo.
        - Extraia apenas informações que estejam explicitamente mencionadas na descrição.
        - Seja específico nas habilidades técnicas, incluindo linguagens, frameworks e ferramentas.
        - Inclua palavras-chave relevantes que representem as tecnologias e competências principais da vaga.
        - Determine se a vaga é remota com base nas informações disponíveis.

        Retorne apenas o JSON sem explicações adicionais.
        """

        return prompt

    def get_match_calculation_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """
        Gera um prompt para cálculo de correspondência entre currículo e vaga.

        Args:
            resume_data: Dados do currículo analisado
            job_data: Dados da vaga analisada

        Returns:
            Prompt formatado para envio ao Claude
        """
        # Converte os dados para JSON formatado
        resume_json = json.dumps(resume_data, indent=2, ensure_ascii=False)
        job_json = json.dumps(job_data, indent=2, ensure_ascii=False)

        prompt = f"""
        Avalie o grau de compatibilidade entre o currículo e a vaga de emprego abaixo:

        CURRÍCULO:
        ```json
        {resume_json}
        ```

        VAGA:
        ```json
        {job_json}
        ```

        Analise cuidadosamente ambos e determine o nível de correspondência entre o candidato e a vaga.

        Por favor, avalie os seguintes aspectos:

        1. Compatibilidade de habilidades técnicas (0-100)
        2. Compatibilidade de habilidades não-técnicas (0-100)
        3. Compatibilidade de experiência profissional (0-100)
        4. Compatibilidade de formação acadêmica (0-100)
        5. Compatibilidade geral (0-100)
        6. Habilidades do candidato que correspondem aos requisitos da vaga
        7. Habilidades requeridas pela vaga que o candidato não possui
        8. Pontos fortes do candidato para esta vaga
        9. Recomendações para aumentar a compatibilidade

        Estruture o resultado no seguinte formato JSON:

        ```json
        {{
            "score_overall": 85.5,
            "score_details": {{
                "technical_skills": 80,
                "soft_skills": 90,
                "experience": 85,
                "education": 75,
                "job_title_match": 70
            }},
            "matching_skills": ["Habilidade 1", "Habilidade 2", ...],
            "missing_skills": ["Habilidade 1", "Habilidade 2", ...],
            "strengths": ["Ponto forte 1", "Ponto forte 2", ...],
            "recommendations": ["Recomendação 1", "Recomendação 2", ...]
        }}
        ```

        Notas importantes:
        - A pontuação deve ser entre 0 e 100, onde 100 representa correspondência perfeita.
        - Dê maior peso para habilidades técnicas essenciais e experiência relevante.
        - Considere correspondências parciais (por exemplo, experiência em tecnologias semelhantes).
        - Forneça recomendações específicas e acionáveis para melhorar a candidatura.
        - Identifique claramente as habilidades que correspondem e as que estão faltando.

        Seja objetivo e imparcial na sua avaliação. Retorne apenas o JSON sem explicações adicionais.
        """

        return prompt

    def get_recommendations_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """
        Gera um prompt para recomendações detalhadas para uma candidatura.

        Args:
            resume_data: Dados do currículo analisado
            job_data: Dados da vaga analisada

        Returns:
            Prompt formatado para envio ao Claude
        """
        # Converte os dados para JSON formatado
        resume_json = json.dumps(resume_data, indent=2, ensure_ascii=False)
        job_json = json.dumps(job_data, indent=2, ensure_ascii=False)

        prompt = f"""
        Com base no currículo e na vaga abaixo, forneça recomendações detalhadas para melhorar a candidatura:

        CURRÍCULO:
        ```json
        {resume_json}
        ```

        VAGA:
        ```json
        {job_json}
        ```

        Analise cuidadosamente ambos os documentos e forneça recomendações detalhadas e personalizadas para ajudar o candidato a melhorar suas chances de conseguir esta vaga.

        Por favor, inclua:

        1. Uma análise da adequação geral do candidato para a vaga
        2. Recomendações para o currículo:
           - Modificações específicas para destacar experiências relevantes
           - Habilidades que devem ser enfatizadas
           - Realizações que devem ser quantificadas
           - Seções que precisam ser expandidas ou reduzidas
        3. Recomendações para a carta de apresentação:
           - Pontos-chave a destacar
           - Experiências específicas a mencionar
           - Como abordar possíveis lacunas ou áreas de melhoria
        4. Preparação para entrevista:
           - Questões técnicas prováveis com base nos requisitos da vaga
           - Como abordar perguntas sobre experiência
           - Como demonstrar as habilidades-chave necessárias
        5. Desenvolvimento profissional:
           - Habilidades a desenvolver no curto prazo
           - Certificações ou cursos rápidos recomendados
           - Recursos para aprendizado das tecnologias necessárias

        Estruture o resultado no seguinte formato JSON:

        ```json
        {{
            "fit_analysis": {{
                "overall_fit": "Avaliação geral da adequação (texto)",
                "strengths": ["Ponto forte 1", "Ponto forte 2", ...],
                "gaps": ["Lacuna 1", "Lacuna 2", ...]
            }},
            "resume_recommendations": [
                "Recomendação específica 1",
                "Recomendação específica 2",
                ...
            ],
            "cover_letter_recommendations": [
                "Elemento a incluir 1",
                "Elemento a incluir 2",
                ...
            ],
            "interview_preparation": {{
                "technical_questions": [
                    {{
                        "topic": "Tópico 1",
                        "sample_questions": ["Pergunta 1", "Pergunta 2", ...],
                        "preparation_tips": "Dicas para se preparar"
                    }},
                    ...
                ],
                "experience_questions": [
                    {{
                        "question": "Pergunta sobre experiência",
                        "recommended_approach": "Abordagem recomendada"
                    }},
                    ...
                ]
            }},
            "skill_development": [
                {{
                    "skill": "Habilidade a desenvolver",
                    "importance": "Alta/Média/Baixa",
                    "resources": ["Recurso 1", "Recurso 2", ...],
                    "estimated_time": "Tempo estimado para aprendizado"
                }},
                ...
            ]
        }}
        ```

        Forneça recomendações altamente específicas e acionáveis. Evite conselhos genéricos que se aplicariam a qualquer candidatura. Concentre-se nas particularidades desta combinação específica de candidato e vaga.

        Retorne apenas o JSON sem explicações adicionais.
        """

        return prompt

    def get_skills_extraction_prompt(self, text: str) -> str:
        """
        Gera um prompt para extração de habilidades de um texto.

        Args:
            text: Texto a ser analisado

        Returns:
            Prompt formatado para envio ao Claude
        """
        prompt = f"""
        Extraia todas as habilidades profissionais mencionadas no texto a seguir:

        ```
        {text}
        ```

        Classifique as habilidades em duas categorias:
        1. Habilidades técnicas: linguagens de programação, frameworks, ferramentas, tecnologias, etc.
        2. Habilidades não-técnicas (soft skills): comunicação, liderança, trabalho em equipe, etc.

        Estruture o resultado no seguinte formato JSON:

        ```json
        {{
            "technical": ["Habilidade 1", "Habilidade 2", ...],
            "soft": ["Habilidade 1", "Habilidade 2", ...]
        }}
        ```

        Notas importantes:
        - Extraia apenas habilidades explicitamente mencionadas no texto.
        - Normalize os nomes das habilidades (por exemplo, "Javascript" como "JavaScript").
        - Não inclua termos genéricos que não são habilidades específicas.
        - Agrupe variações da mesma tecnologia (por exemplo, "React.js" e "ReactJS" como apenas "React").

        Retorne apenas o JSON sem explicações adicionais.
        """

        return prompt

    def get_summary_prompt(self, text: str, max_length: int = 200) -> str:
        """
        Gera um prompt para resumir um texto.

        Args:
            text: Texto a ser resumido
            max_length: Comprimento máximo do resumo em caracteres

        Returns:
            Prompt formatado para envio ao Claude
        """
        prompt = f"""
        Resuma o seguinte texto em no máximo {max_length} caracteres, mantendo as informações mais relevantes:

        ```
        {text}
        ```

        O resumo deve:
        - Capturar os pontos principais do texto original
        - Ser conciso e direto
        - Ter no máximo {max_length} caracteres
        - Manter um tom profissional

        Retorne apenas o resumo, sem introdução ou explicação adicional.
        """

        return prompt

    def get_custom_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """
        Gera um prompt personalizado com base em um template e contexto.

        Args:
            template: Template de prompt com placeholders
            context: Dicionário com valores para substituir os placeholders

        Returns:
            Prompt formatado para envio ao Claude
        """
        # Substitui os placeholders no template
        formatted_prompt = template

        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in formatted_prompt:
                # Se o valor for um dicionário ou lista, converte para JSON
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, indent=2, ensure_ascii=False)
                else:
                    value_str = str(value)

                formatted_prompt = formatted_prompt.replace(placeholder, value_str)

        return formatted_prompt.strip()