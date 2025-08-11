"""
Agent Validators - Validações para o agente inteligente
"""
import re
from werkzeug.datastructures import FileStorage


class AgentValidator:
    """Classe para validações relacionadas ao agente inteligente"""
    
    @staticmethod
    def validate_image_file(image_file):
        """Validar arquivo de imagem"""
        if not image_file:
            return False, "Nenhuma imagem fornecida"
        
        if not isinstance(image_file, FileStorage):
            return False, "Formato de arquivo inválido"
        
        if image_file.filename == '':
            return False, "Nome do arquivo inválido"
        
        # Verificar extensão
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        file_ext = image_file.filename.lower().split('.')[-1]
        if f'.{file_ext}' not in allowed_extensions:
            return False, f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
        
        # Verificar tamanho (max 10MB)
        image_file.seek(0, 2)  # Ir para o final do arquivo
        file_size = image_file.tell()
        image_file.seek(0)  # Voltar ao início
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return False, "Arquivo muito grande (máximo 10MB)"
        
        if file_size == 0:
            return False, "Arquivo vazio"
        
        return True, None
    
    @staticmethod
    def validate_conversation_id(conversation_id):
        """Validar ID de conversa"""
        if not conversation_id:
            return False, "ID da conversa é obrigatório"
        
        # Aceitar string numérica também
        if isinstance(conversation_id, str):
            try:
                conversation_id = int(conversation_id)
            except ValueError:
                return False, "ID da conversa deve ser um número válido"
        
        if not isinstance(conversation_id, int) or conversation_id <= 0:
            return False, "ID da conversa deve ser um número positivo"
        
        return True, None
    
    @staticmethod
    def validate_culture_suggestions_data(data):
        """Validar dados para sugestões de cultura"""
        if not data:
            return True, None  # Dados opcionais
        
        if not isinstance(data, dict):
            return False, "Dados devem ser um objeto JSON"
        
        # Validar preferences se fornecidas
        preferences = data.get('preferences', {})
        if preferences and not isinstance(preferences, dict):
            return False, "Preferências devem ser um objeto"
        
        # Validar farm_conditions se fornecidas
        farm_conditions = data.get('farm_conditions', {})
        if farm_conditions and not isinstance(farm_conditions, dict):
            return False, "Condições da fazenda devem ser um objeto"
        
        # Validar área se fornecida
        if 'area' in farm_conditions:
            area = farm_conditions['area']
            if not isinstance(area, (int, float)) or area <= 0:
                return False, "Área deve ser um número positivo"
        
        # Validar soil_type se fornecido
        if 'soil_type' in farm_conditions:
            soil_type = farm_conditions['soil_type']
            allowed_soil_types = ['clay', 'sand', 'loam', 'silt', 'peat', 'chalk']
            if soil_type and soil_type.lower() not in allowed_soil_types:
                return False, f"Tipo de solo inválido. Use: {', '.join(allowed_soil_types)}"
        
        return True, None
    
    @staticmethod
    def validate_culture_id(culture_id):
        """Validar ID de cultura"""
        if not culture_id:
            return False, "ID da cultura é obrigatório"
        
        if not isinstance(culture_id, int) or culture_id <= 0:
            return False, "ID da cultura deve ser um número positivo"
        
        return True, None
    
    @staticmethod
    def validate_pagination_params(page=None, per_page=None):
        """Validar parâmetros de paginação"""
        if page is not None:
            if not isinstance(page, int) or page < 1:
                return False, "Página deve ser um número positivo"
        
        if per_page is not None:
            if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
                return False, "Itens por página deve ser entre 1 e 100"
        
        return True, None
    
    @staticmethod
    def validate_conversation_title(title):
        """Validar título de conversa"""
        if not title:
            return False, "Título é obrigatório"
        
        if not isinstance(title, str):
            return False, "Título deve ser uma string"
        
        title = title.strip()
        if len(title) < 3:
            return False, "Título deve ter pelo menos 3 caracteres"
        
        if len(title) > 100:
            return False, "Título deve ter no máximo 100 caracteres"
        
        # Verificar caracteres válidos
        if not re.match(r'^[a-zA-Z0-9\s\-_.,!?áéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇ]+$', title):
            return False, "Título contém caracteres inválidos"
        
        return True, None
    
    @staticmethod
    def validate_message_role(role):
        """Validar role da mensagem"""
        if not role:
            return False, "Role é obrigatório"
        
        allowed_roles = ['user', 'assistant', 'system']
        if role not in allowed_roles:
            return False, f"Role inválido. Use: {', '.join(allowed_roles)}"
        
        return True, None
    
    @staticmethod
    def validate_analysis_params(analysis_type=None, depth=None):
        """Validar parâmetros de análise"""
        if analysis_type:
            allowed_types = ['basic', 'detailed', 'comprehensive']
            if analysis_type not in allowed_types:
                return False, f"Tipo de análise inválido. Use: {', '.join(allowed_types)}"
        
        if depth is not None:
            if not isinstance(depth, int) or depth < 1 or depth > 5:
                return False, "Profundidade deve ser entre 1 e 5"
        
        return True, None
    
    @staticmethod
    def validate_chat_message(message):
        """Validar mensagem de chat simples"""
        if not message:
            return False, "Mensagem não pode estar vazia"
        
        if not isinstance(message, str):
            return False, "Mensagem deve ser uma string"
        
        message = message.strip()
        if len(message) < 1:
            return False, "Mensagem deve ter pelo menos 1 caractere"
        
        if len(message) > 5000:
            return False, "Mensagem muito longa (máximo 5000 caracteres)"
        
        # Verificar por conteúdo malicioso básico
        malicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'\.\./.*etc/passwd'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Conteúdo malicioso detectado"
        
        return True, None
    
    @staticmethod
    def validate_ai_query(query_data):
        """Validar consulta de IA"""
        if not query_data:
            return False, "Dados da consulta não fornecidos"
        
        if not isinstance(query_data, dict):
            return False, "Dados devem ser um dicionário"
        
        # Validar query
        query = query_data.get('query')
        if not query or not isinstance(query, str):
            return False, "Query é obrigatória e deve ser uma string"
        
        query = query.strip()
        if len(query) < 3:
            return False, "Query deve ter pelo menos 3 caracteres"
        
        if len(query) > 1000:
            return False, "Query muito longa (máximo 1000 caracteres)"
        
        # Validar user_id
        user_id = query_data.get('user_id')
        if user_id is not None:
            try:
                uid = int(user_id)
                if uid <= 0:
                    return False, "user_id deve ser um número positivo"
            except (ValueError, TypeError):
                return False, "user_id deve ser um número válido"
        
        # Validar language
        language = query_data.get('language')
        if language:
            valid_languages = ['pt', 'en', 'es', 'fr']
            if language not in valid_languages:
                return False, f"Linguagem deve ser uma de: {', '.join(valid_languages)}"
        
        # Validar context
        context = query_data.get('context')
        if context:
            valid_contexts = [
                'agriculture', 'pest_control', 'fertilization', 'weather',
                'olivicultura', 'viticultura', 'horticultura', 'cereais',
                'fruticultura', 'pecuaria', 'aquicultura', 'floricultura',
                'agricultura_biologica'
            ]
            if context not in valid_contexts:
                return False, f"Contexto deve ser um de: {', '.join(valid_contexts)}"
        
        return True, None
    
    @staticmethod
    def validate_ai_response(response_data):
        """Validar resposta de IA"""
        if not response_data:
            return False, "Dados da resposta não fornecidos"
        
        if not isinstance(response_data, dict):
            return False, "Dados devem ser um dicionário"
        
        # Validar response
        response = response_data.get('response')
        if not response or not isinstance(response, str):
            return False, "Resposta é obrigatória e deve ser uma string"
        
        response = response.strip()
        if len(response) < 1:
            return False, "Resposta não pode estar vazia"
        
        # Validar confidence
        confidence = response_data.get('confidence')
        if confidence is not None:
            try:
                conf = float(confidence)
                if conf < 0 or conf > 1:
                    return False, "Confiança deve estar entre 0 e 1"
            except (ValueError, TypeError):
                return False, "Confiança deve ser um número válido"
        
        # Validar sources
        sources = response_data.get('sources')
        if sources is not None:
            if not isinstance(sources, list):
                return False, "Sources deve ser uma lista"
        
        # Validar response_time
        response_time = response_data.get('response_time')
        if response_time is not None:
            try:
                rt = float(response_time)
                if rt < 0:
                    return False, "Tempo de resposta não pode ser negativo"
            except (ValueError, TypeError):
                return False, "Tempo de resposta deve ser um número válido"
        
        return True, None
    
    @staticmethod
    def validate_model_config(config):
        """Validar configuração do modelo de IA"""
        if not config:
            return False, "Configuração não fornecida"
        
        if not isinstance(config, dict):
            return False, "Configuração deve ser um dicionário"
        
        # Validar model_name
        model_name = config.get('model_name')
        if not model_name or not isinstance(model_name, str):
            return False, "Nome do modelo é obrigatório"
        
        valid_models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro']
        if model_name not in valid_models:
            return False, f"Modelo deve ser um de: {', '.join(valid_models)}"
        
        # Validar temperature
        temperature = config.get('temperature')
        if temperature is not None:
            try:
                temp = float(temperature)
                if temp < 0 or temp > 2:
                    return False, "Temperatura deve estar entre 0 e 2"
            except (ValueError, TypeError):
                return False, "Temperatura deve ser um número válido"
        
        # Validar max_tokens
        max_tokens = config.get('max_tokens')
        if max_tokens is not None:
            try:
                tokens = int(max_tokens)
                if tokens <= 0:
                    return False, "Max tokens deve ser positivo"
                if tokens > 10000:
                    return False, "Max tokens muito alto (máximo 10.000)"
            except (ValueError, TypeError):
                return False, "Max tokens deve ser um número inteiro válido"
        
        # Validar top_p
        top_p = config.get('top_p')
        if top_p is not None:
            try:
                tp = float(top_p)
                if tp < 0 or tp > 1:
                    return False, "Top_p deve estar entre 0 e 1"
            except (ValueError, TypeError):
                return False, "Top_p deve ser um número válido"
        
        return True, None
    
    @staticmethod
    def validate_user_feedback(feedback_data):
        """Validar feedback do usuário"""
        if not feedback_data:
            return False, "Dados do feedback não fornecidos"
        
        if not isinstance(feedback_data, dict):
            return False, "Dados devem ser um dicionário"
        
        # Validar query_id
        query_id = feedback_data.get('query_id')
        if query_id is not None:
            try:
                qid = int(query_id)
                if qid <= 0:
                    return False, "query_id deve ser um número positivo"
            except (ValueError, TypeError):
                return False, "query_id deve ser um número válido"
        
        # Validar user_id
        user_id = feedback_data.get('user_id')
        if user_id is not None:
            try:
                uid = int(user_id)
                if uid <= 0:
                    return False, "user_id deve ser um número positivo"
            except (ValueError, TypeError):
                return False, "user_id deve ser um número válido"
        
        # Validar rating
        rating = feedback_data.get('rating')
        if rating is not None:
            try:
                rat = int(rating)
                if rat < 1 or rat > 5:
                    return False, "Rating deve estar entre 1 e 5"
            except (ValueError, TypeError):
                return False, "Rating deve ser um número inteiro válido"
        
        # Validar helpful
        helpful = feedback_data.get('helpful')
        if helpful is not None:
            if not isinstance(helpful, bool):
                return False, "Helpful deve ser um booleano"
        
        return True, None
    
    @staticmethod
    def validate_knowledge_base_entry(entry_data):
        """Validar entrada da base de conhecimento"""
        if not entry_data:
            return False, "Dados da entrada não fornecidos"
        
        if not isinstance(entry_data, dict):
            return False, "Dados devem ser um dicionário"
        
        # Validar topic
        topic = entry_data.get('topic')
        if not topic or not isinstance(topic, str):
            return False, "Tópico é obrigatório e deve ser uma string"
        
        topic = topic.strip()
        if len(topic) < 3:
            return False, "Tópico deve ter pelo menos 3 caracteres"
        
        # Validar content
        content = entry_data.get('content')
        if not content or not isinstance(content, str):
            return False, "Conteúdo é obrigatório e deve ser uma string"
        
        content = content.strip()
        if len(content) < 10:
            return False, "Conteúdo deve ter pelo menos 10 caracteres"
        
        # Validar difficulty
        difficulty = entry_data.get('difficulty')
        if difficulty:
            valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
            if difficulty not in valid_difficulties:
                return False, f"Dificuldade deve ser uma de: {', '.join(valid_difficulties)}"
        
        # Validar season
        season = entry_data.get('season')
        if season:
            valid_seasons = ['primavera', 'verao', 'outono', 'inverno']
            if season not in valid_seasons:
                return False, f"Estação deve ser uma de: {', '.join(valid_seasons)}"
        
        return True, None
    
    @staticmethod
    def validate_performance_metric(metric_data):
        """Validar métrica de performance"""
        if not metric_data:
            return False, "Dados da métrica não fornecidos"
        
        if not isinstance(metric_data, dict):
            return False, "Dados devem ser um dicionário"
        
        # Validar metric_name
        metric_name = metric_data.get('metric_name')
        if not metric_name or not isinstance(metric_name, str):
            return False, "Nome da métrica é obrigatório"
        
        valid_metrics = ['response_time', 'accuracy', 'user_satisfaction', 'uptime']
        if metric_name not in valid_metrics:
            return False, f"Nome da métrica deve ser um de: {', '.join(valid_metrics)}"
        
        # Validar value
        value = metric_data.get('value')
        if value is None:
            return False, "Valor da métrica é obrigatório"
        
        try:
            val = float(value)
            if val < 0:
                return False, "Valor da métrica não pode ser negativo"
        except (ValueError, TypeError):
            return False, "Valor da métrica deve ser um número válido"
        
        # Validar timestamp se presente
        timestamp = metric_data.get('timestamp')
        if timestamp:
            try:
                from datetime import datetime, timezone
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False, "Formato de timestamp inválido (use ISO 8601)"
        
        return True, None
