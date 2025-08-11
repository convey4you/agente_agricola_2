"""
Agent Controller - Rotas do agente inteligente (Refatorado)
Segue padrões SOLID com separação de responsabilidades
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

# Services e Validators
from app.services.agent_service import AgentService
from app.validators.agent_validators import AgentValidator

# Utilitários compartilhados
from app.utils.response_helpers import ResponseHandler
from app.utils.logging_helpers import LoggingHelper

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')


@agent_bp.route('/')
@login_required
def index():
    """Interface principal do agente - Refatorado"""
    try:
        LoggingHelper.log_request('agent.index', 'GET', current_user.email)
        
        # Obter dados da página inicial do agente
        result = AgentService.get_agent_index_data()
        
        if not result['success']:
            return ResponseHandler.handle_server_error(
                result['error'],
                'agent/index.html'
            )
        
        return render_template('agent/index.html', **result['data'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.index')
        return ResponseHandler.handle_server_error(
            'Erro ao carregar interface do agente',
            'agent/index.html'
        )


@agent_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Processar mensagem do usuário - Refatorado"""
    try:
        LoggingHelper.log_request('agent.chat', 'POST', current_user.email)
        
        data = request.get_json()
        
        # Validar dados da mensagem
        is_valid, error_msg = AgentValidator.validate_chat_message(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        message_text = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        # Processar mensagem através do service
        result = AgentService.process_chat_message(message_text, conversation_id)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'CHAT_MESSAGE_SENT',
                {'conversation_id': result['data']['conversation_id']}
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.chat')
        return ResponseHandler.handle_server_error('Erro ao processar mensagem')


@agent_bp.route('/image-analysis', methods=['POST'])
@login_required
def analyze_image():
    """Analisar imagem enviada pelo usuário - Refatorado"""
    try:
        LoggingHelper.log_request('agent.analyze_image', 'POST', current_user.email)
        
        # Verificar se imagem foi enviada
        if 'image' not in request.files:
            return ResponseHandler.handle_validation_error('Nenhuma imagem enviada')
        
        image_file = request.files['image']
        
        # Validar arquivo de imagem
        is_valid, error_msg = AgentValidator.validate_image_file(image_file)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Processar análise através do service
        result = AgentService.analyze_plant_image(image_file)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'IMAGE_ANALYZED'
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.analyze_image')
        return ResponseHandler.handle_server_error('Erro ao analisar imagem')


@agent_bp.route('/conversations')
@login_required
def list_conversations():
    """Listar conversas do usuário - Refatorado"""
    try:
        LoggingHelper.log_request('agent.list_conversations', 'GET', current_user.email)
        
        # Obter conversas através do service
        result = AgentService.get_user_conversations()
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.list_conversations')
        return ResponseHandler.handle_server_error('Erro ao listar conversas')


@agent_bp.route('/conversations/<int:conversation_id>')
@login_required
def get_conversation(conversation_id):
    """Obter mensagens de uma conversa - Refatorado"""
    try:
        LoggingHelper.log_request('agent.get_conversation', 'GET', current_user.email)
        
        # Validar ID da conversa
        is_valid, error_msg = AgentValidator.validate_conversation_id(conversation_id)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Obter conversa através do service
        result = AgentService.get_conversation_details(conversation_id)
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_not_found(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.get_conversation')
        return ResponseHandler.handle_server_error('Erro ao obter conversa')


@agent_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """Deletar uma conversa - Refatorado"""
    try:
        LoggingHelper.log_request('agent.delete_conversation', 'DELETE', current_user.email)
        
        # Validar ID da conversa
        is_valid, error_msg = AgentValidator.validate_conversation_id(conversation_id)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Deletar conversa através do service
        result = AgentService.delete_conversation(conversation_id)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'CONVERSATION_DELETED',
                {'conversation_id': conversation_id}
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_not_found(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.delete_conversation')
        return ResponseHandler.handle_server_error('Erro ao deletar conversa')


@agent_bp.route('/suggestions/cultures', methods=['POST'])
@login_required
def culture_suggestions():
    """Sugestões de culturas baseadas em localização e época - Refatorado"""
    try:
        LoggingHelper.log_request('agent.culture_suggestions', 'POST', current_user.email)
        
        data = request.get_json() or {}
        
        # Validar dados de entrada
        is_valid, error_msg = AgentValidator.validate_culture_suggestions_data(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        preferences = data.get('preferences', {})
        farm_conditions = data.get('farm_conditions', {})
        
        # Obter sugestões através do service
        result = AgentService.get_culture_suggestions(preferences, farm_conditions)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'CULTURE_SUGGESTIONS_REQUESTED'
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.culture_suggestions')
        return ResponseHandler.handle_server_error('Erro ao gerar sugestões')


@agent_bp.route('/analysis/culture/<int:culture_id>', methods=['GET'])
@login_required
def analyze_culture(culture_id):
    """Análise de cultura específica - Refatorado"""
    try:
        LoggingHelper.log_request('agent.analyze_culture', 'GET', current_user.email)
        
        # Validar ID da cultura
        is_valid, error_msg = AgentValidator.validate_culture_id(culture_id)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Analisar cultura através do service
        result = AgentService.analyze_specific_culture(culture_id)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'CULTURE_ANALYZED',
                {'culture_id': culture_id}
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            if 'não encontrada' in result['error']:
                return ResponseHandler.handle_not_found(result['error'])
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.analyze_culture')
        return ResponseHandler.handle_server_error('Erro na análise')


@agent_bp.route('/recommendations/activities', methods=['GET'])
@login_required
def activity_recommendations():
    """Recomendações de atividades baseadas nas culturas do usuário - Refatorado"""
    try:
        LoggingHelper.log_request('agent.activity_recommendations', 'GET', current_user.email)
        
        # Obter recomendações através do service
        result = AgentService.get_activity_recommendations()
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'agent.activity_recommendations')
        return ResponseHandler.handle_server_error('Erro ao gerar recomendações')


# === FIM DOS CONTROLLERS REFATORADOS ===
