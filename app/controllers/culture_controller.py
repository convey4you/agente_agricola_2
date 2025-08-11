"""
Controlador de culturas - Refatorado
Aplicando princípios SOLID e boas práticas
"""
import logging
from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models.culture import Culture
from app.models.farm import Farm
from app.services.culture_service import CultureService, CultureWizardService
from app.services.base_conhecimento_culturas import buscar_cultura, calcular_custos_estimados, validar_condicoes_cultura, listar_culturas_por_categoria
from app.validators.culture_validators import CultureValidator
from app.utils.response_helpers import ResponseHandler, LoggingHelper

# Configurar logging
logger = logging.getLogger(__name__)

culture_bp = Blueprint('culture', __name__)


@culture_bp.route('/', methods=['GET'])
@login_required
def list_cultures():
    """Listar culturas do usuário - Refatorado"""
    try:
        LoggingHelper.log_request('culture.list_cultures', 'GET', current_user.email)
        
        # Se for uma requisição AJAX (verificar Accept header ou X-Requested-With)
        is_ajax = (request.headers.get('Content-Type') == 'application/json' or 
                  request.headers.get('Accept', '').find('application/json') >= 0 or
                  request.headers.get('X-Requested-With') == 'XMLHttpRequest')
        
        if is_ajax:
            result = CultureService.get_user_cultures()
            
            if not result['success']:
                return ResponseHandler.handle_server_error(result['error'])
            
            return ResponseHandler.handle_success({
                'cultures': result['cultures']
            })
        
        # Se for uma requisição normal do navegador, renderizar template
        return render_template('cultures/index.html')
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.list_cultures')
        return ResponseHandler.handle_server_error('Erro ao buscar culturas')


@culture_bp.route('/api', methods=['GET'])
@login_required
def api_list_cultures():
    """API endpoint para listar culturas do usuário"""
    try:
        LoggingHelper.log_request('culture.api_list_cultures', 'GET', current_user.email)
        
        # Verificar se usuário completou onboarding
        if not current_user.onboarding_completed:
            return ResponseHandler.handle_success({
                'success': False,
                'error': 'Complete seu perfil antes de acessar as culturas',
                'needs_onboarding': True,
                'redirect_url': '/auth/onboarding'
            })
        
        # Versão simplificada sem cache para debug
        try:
            cultures = Culture.query.join(Farm).filter(
                Farm.user_id == current_user.id
            ).all()
            
            cultures_data = [culture.to_dict() for culture in cultures]
            
            return ResponseHandler.handle_success({
                'success': True,
                'cultures': cultures_data
            })
        except Exception as db_error:
            logger.error(f"Erro específico na query: {db_error}")
            return ResponseHandler.handle_server_error(f'Erro no banco: {str(db_error)}')
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.api_list_cultures')
        return ResponseHandler.handle_server_error('Erro ao buscar culturas')


# Rotas de teste removidas por segurança


@culture_bp.route('/', methods=['POST'])
@login_required
def create_culture():
    """Criar nova cultura - Refatorado"""
    try:
        data = request.get_json() or {}
        LoggingHelper.log_request('culture.create_culture', 'POST', current_user.email)
        
        if not data:
            return ResponseHandler.handle_validation_error('Dados não fornecidos')
        
        # Validar dados
        is_valid, error_msg = CultureValidator.validate_create_culture_data(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Criar cultura
        result = CultureService.create_culture(data)
        
        if not result['success']:
            return ResponseHandler.handle_server_error(
                result['error'], 
                result.get('status_code', 500)
            )
        
        LoggingHelper.log_user_action(
            current_user.email, 
            'CULTURE_CREATED', 
            f"Cultura: {data.get('nome')}"
        )
        
        return ResponseHandler.handle_success(result, 201)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.create_culture')
        return ResponseHandler.handle_server_error('Erro ao criar cultura')


@culture_bp.route('/<int:culture_id>', methods=['GET'])
@login_required
def get_culture(culture_id):
    """Obter cultura específica - Refatorado"""
    try:
        LoggingHelper.log_request('culture.get_culture', 'GET', current_user.email)
        
        result = CultureService.get_culture_by_id(culture_id)
        
        if not result['success']:
            status_code = result.get('status_code', 500)
            if status_code == 404:
                return ResponseHandler.handle_error(result['error'], 404)
            return ResponseHandler.handle_server_error(result['error'])
        
        return ResponseHandler.handle_success({
            'culture': result['culture']
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.get_culture')
        return ResponseHandler.handle_server_error('Erro ao buscar cultura')


@culture_bp.route('/<int:culture_id>', methods=['PUT'])
@login_required
def update_culture(culture_id):
    """Atualizar cultura - Refatorado"""
    try:
        data = request.get_json() or {}
        LoggingHelper.log_request('culture.update_culture', 'PUT', current_user.email)
        
        if not data:
            return ResponseHandler.handle_validation_error('Dados não fornecidos')
        
        # Validar dados
        is_valid, error_msg = CultureValidator.validate_update_culture_data(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Atualizar cultura
        result = CultureService.update_culture(culture_id, data)
        
        if not result['success']:
            status_code = result.get('status_code', 500)
            if status_code == 404:
                return ResponseHandler.handle_error(result['error'], 404)
            return ResponseHandler.handle_server_error(result['error'])
        
        LoggingHelper.log_user_action(
            current_user.email, 
            'CULTURE_UPDATED', 
            f"ID: {culture_id}"
        )
        
        return ResponseHandler.handle_success(result)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.update_culture')
        return ResponseHandler.handle_server_error('Erro ao atualizar cultura')


@culture_bp.route('/<int:culture_id>', methods=['DELETE'])
@login_required
def delete_culture(culture_id):
    """Excluir cultura - Refatorado"""
    try:
        LoggingHelper.log_request('culture.delete_culture', 'DELETE', current_user.email)
        
        result = CultureService.delete_culture(culture_id)
        
        if not result['success']:
            status_code = result.get('status_code', 500)
            if status_code == 404:
                return ResponseHandler.handle_error(result['error'], 404)
            return ResponseHandler.handle_server_error(result['error'])
        
        LoggingHelper.log_user_action(
            current_user.email, 
            'CULTURE_DELETED', 
            f"ID: {culture_id}"
        )
        
        return ResponseHandler.handle_success(result)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.delete_culture')
        return ResponseHandler.handle_server_error('Erro ao excluir cultura')


@culture_bp.route('/types', methods=['GET'])
def get_culture_types():
    """Obter tipos de cultura disponíveis - Refatorado"""
    try:
        LoggingHelper.log_request('culture.get_culture_types', 'GET')
        
        result = CultureService.get_culture_types()
        
        return ResponseHandler.handle_success(result)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.get_culture_types')
        return ResponseHandler.handle_server_error('Erro ao buscar tipos de cultura')


# ===== WIZARD DE CULTURA =====

@culture_bp.route('/wizard')
@login_required
def culture_wizard():
    """Wizard de adição de nova cultura - Refatorado"""
    LoggingHelper.log_request('culture.culture_wizard', 'GET', current_user.email)
    
    step = request.args.get('step', '1')
    
    # Validar step
    if step not in ['1', '2', '3', '4', '5']:
        step = '1'
    
    # Verificar se é requisição AJAX (para modal)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              'application/json' in request.headers.get('Accept', '') or \
              request.args.get('modal') == 'true'
    
    template_map = {
        '1': 'cultures/wizard_step1.html',
        '2': 'cultures/wizard_step2.html',
        '3': 'cultures/wizard_step3.html',
        '4': 'cultures/wizard_step4.html',
        '5': 'cultures/wizard_step5.html'
    }
    
    # Templates modais (apenas conteúdo, sem layout)
    modal_template_map = {
        '1': 'cultures/wizard_step1_modal.html',
        '2': 'cultures/wizard_step2_modal.html',
        '3': 'cultures/wizard_step3_modal.html',
        '4': 'cultures/wizard_step4_modal.html',
        '5': 'cultures/wizard_step5_modal.html'
    }
    
    # Se for AJAX, usar template modal; senão usar template completo
    if is_ajax:
        try:
            return render_template(modal_template_map[step])
        except:
            # Fallback para template completo se modal não existir
            return render_template(template_map[step])
    else:
        return render_template(template_map[step])


@culture_bp.route('/wizard/save', methods=['POST'])
@login_required
def save_wizard_step():
    """Salvar dados de uma etapa do wizard - Refatorado"""
    try:
        data = request.get_json() or {}
        step = data.get('step')
        
        LoggingHelper.log_request('culture.save_wizard_step', 'POST', current_user.email)
        LoggingHelper.log_user_action(current_user.email, 'WIZARD_STEP', f'step_{step}')
        
        # Validar dados
        is_valid, error_msg = CultureValidator.validate_wizard_step_data(step, data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Salvar dados
        result = CultureWizardService.save_wizard_step(step, data)
        
        return ResponseHandler.handle_success(result)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.save_wizard_step')
        return ResponseHandler.handle_server_error('Erro ao salvar dados do wizard')


# ===== API ENDPOINTS =====

@culture_bp.route('/api/verificar', methods=['POST'])
@login_required
def verificar_cultura():
    """API para verificar informações de cultura com busca IA automática"""
    try:
        data = request.get_json()
        nome_cultura = data.get('nome', '').strip()
        
        if not nome_cultura:
            return ResponseHandler.handle_validation_error('Nome da cultura é obrigatório')
        
        LoggingHelper.log_request('culture.verificar_cultura', 'POST', current_user.email)
        
        # Buscar na base de conhecimento
        cultura_info = buscar_cultura(nome_cultura)
        
        if cultura_info:
            return ResponseHandler.handle_success({
                'encontrada': True,
                'dados_sugeridos': cultura_info,
                'message': f'Encontrámos informações sobre {cultura_info["nome"]}!',
                'fonte': cultura_info.get('fonte', 'base')
            })
        else:
            # Se não encontrou, tentar buscar via IA
            logger.info(f"Cultura {nome_cultura} não encontrada na base, tentando buscar via IA...")
            
            try:
                from app.services.culture_ai_service import CultureAIService
                
                # Debug: Verificar se o serviço está funcionando
                logger.info(f"DEBUG: Iniciando busca via IA para {nome_cultura}")
                
                # Buscar via IA e salvar na base
                cultura_ia = CultureAIService.buscar_e_salvar_cultura(nome_cultura)
                
                logger.info(f"DEBUG: Resultado da busca IA: {cultura_ia}")
                
                if cultura_ia:
                    logger.info(f"Cultura {nome_cultura} encontrada via IA e adicionada à base")
                    return ResponseHandler.handle_success({
                        'encontrada': True,
                        'dados_sugeridos': cultura_ia,
                        'message': f'🤖 Encontrámos informações sobre {cultura_ia["nome"]} via IA!',
                        'fonte': 'IA',
                        'nova_cultura': True
                    })
                else:
                    logger.warning(f"DEBUG: IA retornou None para {nome_cultura}")
                    logger.info(f"Cultura {nome_cultura} não foi encontrada nem via IA")
                    return ResponseHandler.handle_success({
                        'encontrada': False,
                        'message': '🤖 Mesmo consultando nossa IA, não conseguimos encontrar informações sobre esta cultura. Pode continuar manualmente.',
                        'fonte': 'nenhuma'
                    })
                    
            except Exception as e:
                logger.error(f"DEBUG: Exceção na busca via IA: {e}")
                logger.warning(f"Erro ao buscar via IA: {e}")
                # Se der erro com IA, retornar resposta padrão
                return ResponseHandler.handle_success({
                    'encontrada': False,
                    'message': 'Cultura não encontrada na nossa base de dados. Pode continuar manualmente.',
                    'fonte': 'base'
                })
            
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.verificar_cultura')
        return ResponseHandler.handle_server_error('Erro ao verificar cultura')


@culture_bp.route('/api/categorias', methods=['GET'])
@login_required  
def listar_categorias():
    """API para listar categorias de culturas"""
    try:
        LoggingHelper.log_request('culture.listar_categorias', 'GET', current_user.email)
        
        categorias = listar_culturas_por_categoria()
        
        return ResponseHandler.handle_success({
            'categorias': categorias
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.listar_categorias')
        return ResponseHandler.handle_server_error('Erro ao carregar categorias')


@culture_bp.route('/api/calcular-custos', methods=['POST'])
@login_required
def calcular_custos():
    """API para calcular custos estimados"""
    try:
        data = request.get_json()
        cultura_nome = data.get('cultura', '').strip()
        area_m2 = float(data.get('area', 0))
        
        if not cultura_nome or area_m2 <= 0:
            return ResponseHandler.handle_validation_error('Cultura e área são obrigatórios')
        
        LoggingHelper.log_request('culture.calcular_custos', 'POST', current_user.email)
        
        custos = calcular_custos_estimados(cultura_nome, area_m2)
        
        if custos:
            return ResponseHandler.handle_success({
                'custos': custos
            })
        else:
            return ResponseHandler.handle_validation_error('Cultura não encontrada para cálculo')
            
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.calcular_custos')
        return ResponseHandler.handle_server_error('Erro ao calcular custos')


@culture_bp.route('/wizard/data', methods=['GET'])
@login_required
def get_wizard_data():
    """Obter dados salvos no wizard - Refatorado"""
    try:
        LoggingHelper.log_request('culture.get_wizard_data', 'GET', current_user.email)
        
        result = CultureWizardService.get_wizard_data()
        
        # FORÇAR RETORNO JSON sempre para este endpoint
        from flask import jsonify
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify({'success': False, 'data': {}, 'message': 'Nenhum dado encontrado'}), 200
        
    except Exception as e:
        LoggingHelper.log_error(e, 'culture.get_wizard_data')
        from flask import jsonify
        return jsonify({'success': False, 'error': 'Erro ao buscar dados do wizard', 'data': {}}), 500
