"""
Controlador de autenticação - Refatorado
Aplicando princípios SOLID e boas práticas
"""
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, render_template, redirect, url_for, session, current_app
from flask_login import logout_user, login_required, current_user

from app.services.auth_service import AuthService
from app.validators.auth_validators import AuthValidator
from app.utils.response_helpers import ResponseHandler, LoggingHelper
from app.middleware.session_middleware import require_valid_session
from app.middleware.rate_limiter import critical_endpoint_limit, api_endpoint_limit, authenticated_endpoint_limit
from app.middleware.validation import ValidationManager, ValidationError

# Configurar logging
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirecionar para login quando acessar /auth/"""
    LoggingHelper.log_request('auth.index', 'GET')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
@critical_endpoint_limit
def login():
    """Rota de login - Refatorada com rate limiting e validação robusta"""
    if request.method == 'GET':
        LoggingHelper.log_request('auth.login', 'GET')
        # Modificando para não esperar um objeto form no template
        return render_template('auth/login.html', form=None)
    
    # Rate limiting aplicado via decorador (forma correta)
    # O rate limiting já é aplicado automaticamente pelo middleware
    
    try:
        # Obter dados da requisição com tratamento de erro
        if request.is_json:
            try:
                data = request.get_json()
            except Exception as e:
                logger.warning(f"Failed to parse JSON: {e}")
                return ResponseHandler.handle_error("Dados JSON inválidos", 400, 'auth/login.html')
        else:
            data = request.form
        LoggingHelper.log_request('auth.login', 'POST', data.get('email'))
        
        # Validação robusta com Marshmallow
        try:
            validated_data = ValidationManager.validate('login', data)
        except ValidationError as e:
            logger.warning(f"Login validation failed: {e.messages}")
            return ResponseHandler.handle_validation_error(str(e.messages), 'auth/login.html')
        
        # Autenticar usuário
        email = validated_data['email']
        password = validated_data['password']
        remember = validated_data.get('remember_me', False)
        
        result = AuthService.authenticate_user(email, password, remember)
        
        if not result['success']:
            # Log de falha - CORREÇÃO SPRINT 1
            from app.middleware.auth_middleware import log_auth_event
            log_auth_event('LOGIN_FAILED', None, {'email': email, 'ip': request.remote_addr})
            LoggingHelper.log_auth_attempt(email, False)
            return ResponseHandler.handle_auth_error(
                result['error'], 
                'auth/login.html'
            )
        
        # Sucesso - CORREÇÃO SPRINT 1
        from app.middleware.auth_middleware import log_auth_event
        user_id = result['user']['id']
        log_auth_event('LOGIN_SUCCESS', user_id, {
            'email': email, 
            'ip': request.remote_addr,
            'remember': remember
        })
        LoggingHelper.log_auth_attempt(email, True)
        
        # Atualizar último acesso
        try:
            from app.models.user import User
            from app import db
            user = User.query.get(user_id)
            if user:
                user.ultimo_acesso = datetime.now(timezone.utc)
                db.session.commit()
        except Exception as e:
            logger.warning(f'Could not update last access: {e}')
        
        # Definir redirecionamento
        if result['needs_onboarding']:
            redirect_url = url_for('auth.onboarding')
        else:
            redirect_url = url_for('dashboard.index')
        
        return ResponseHandler.handle_success(
            result, 
            200, 
            redirect_url=redirect_url
        )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'auth.login')
        return ResponseHandler.handle_server_error(
            'Erro interno durante login', 
            'auth/login.html'
        )


@auth_bp.route('/register', methods=['GET', 'POST'])
@critical_endpoint_limit
def register():
    """Registro de novo usuário - Refatorado com Geocoding"""
    if request.method == 'GET':
        LoggingHelper.log_request('auth.register', 'GET')
        return render_template('auth/register.html')
    
    try:
        # Obter dados da requisição
        data = request.get_json() if request.is_json else request.form
        LoggingHelper.log_request('auth.register', 'POST', data.get('email'))
        
        # Validar dados
        is_valid, error_msg = AuthValidator.validate_register_data(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg, 'auth/register.html')
        
        # Extrair dados básicos
        email = data.get('email').strip()
        password = data.get('password')
        nome_completo = data.get('nome_completo', '')
        location = data.get('location', '').strip()
        
        # Processar telefone - usar telefone_completo se disponível, senão combinar código + número
        telefone = data.get('telefone_completo', '').strip()
        if not telefone and data.get('telefone'):
            # Fallback: combinar código do país + número
            country_code = data.get('country_code', '+351')
            phone_number = data.get('telefone', '').strip()
            if phone_number:
                # Remover formatação do número
                clean_number = ''.join(filter(str.isdigit, phone_number))
                if clean_number:
                    telefone = country_code + clean_number
        
        # Variáveis para coordenadas
        latitude = None
        longitude = None
        formatted_address = None
        
        # Se localização foi fornecida, tentar geocoding
        if location:
            from app.services.geocoding_service import GeocodingService
            geocoding_result = GeocodingService.get_coordinates_from_address(location)
            
            if geocoding_result['success']:
                latitude = geocoding_result['latitude']
                longitude = geocoding_result['longitude']
                formatted_address = geocoding_result['formatted_address']
                logger.info(f"Geocoding bem-sucedido para {email}: {formatted_address} ({latitude}, {longitude})")
            else:
                # Se geocoding falhou, ainda permitir registro mas alertar
                logger.warning(f"Geocoding falhou para {email} com localização '{location}': {geocoding_result['error']}")
        
        # Criar usuário com informações de localização e telefone
        result = AuthService.create_user(
            email=email, 
            password=password, 
            nome_completo=nome_completo,
            telefone=telefone,
            location=formatted_address or location,
            latitude=latitude,
            longitude=longitude
        )
        
        if not result['success']:
            return ResponseHandler.handle_server_error(
                result['error'], 
                'auth/register.html'
            )
        
        # Sucesso - redirecionar para onboarding
        LoggingHelper.log_user_action(email, 'USER_REGISTERED')
        
        return ResponseHandler.handle_success(
            result, 
            201, 
            redirect_url=url_for('auth.onboarding')
        )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'auth.register')
        return ResponseHandler.handle_server_error(
            'Erro interno durante registro', 
            'auth/register.html'
        )


@auth_bp.route('/onboarding')
@login_required
@require_valid_session
def onboarding():
    """Wizard de onboarding para novos usuários - Refatorado"""
    LoggingHelper.log_request('auth.onboarding', 'GET', current_user.email)
    
    if current_user.onboarding_completed:
        return redirect(url_for('dashboard.index'))

    step = request.args.get('step', '1')
    
    # Validar step
    if step not in ['1', '2', '3', '4', '5']:
        step = '1'
    
    template_map = {
        '1': 'auth/onboarding_step1.html',
        '2': 'auth/onboarding_step2.html',
        '3': 'auth/onboarding_step3.html',
        '4': 'auth/onboarding_step4.html',
        '5': 'auth/onboarding_step5.html'
    }
    
    # Recuperar dados salvos temporariamente na sessão
    onboarding_data = session.get('onboarding_data', {})
    
    # Contexto base
    context = {
        'onboarding_data': onboarding_data,
        'current_step': step
    }
    
    # Para o step 3, adicionar dados do usuário para pré-preenchimento
    if step == '3':
        # CORREÇÃO: Usar cidade (onde foi salva a localização do registro) 
        user_location = current_user.cidade or ''
        
        # Se não tem cidade mas tem coordenadas, usar coordenadas como fallback
        if not user_location and current_user.latitude and current_user.longitude:
            user_location = f"Latitude: {current_user.latitude}, Longitude: {current_user.longitude}"
        
        context.update({
            'user_location': user_location,
            'user_latitude': current_user.latitude,
            'user_longitude': current_user.longitude,
            'user_city': current_user.cidade or '',
            'user_state': current_user.estado or ''
        })
    
    return render_template(template_map[step], **context)
@auth_bp.route('/onboarding/save', methods=['POST'])
@authenticated_endpoint_limit
@login_required
@require_valid_session
def save_onboarding():
    """Salvar dados do onboarding - Refatorado"""
    try:
        data = request.get_json() or {}
        step = data.get('step')
        
        LoggingHelper.log_request('auth.save_onboarding', 'POST', current_user.email)
        LoggingHelper.log_user_action(current_user.email, 'ONBOARDING_STEP', f'step_{step}')
        
        # Validar dados
        is_valid, error_msg = AuthValidator.validate_onboarding_data(step, data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Salvar dados na sessão para persistência entre passos
        if 'onboarding_data' not in session:
            session['onboarding_data'] = {}
        
        session['onboarding_data'][f'step_{step}'] = data
        session.permanent = True  # Manter a sessão ativa
        
        # CORREÇÃO: Salvar dados parciais a cada passo para evitar perda
        try:
            partial_result = AuthService.save_onboarding_step(current_user, step, data)
            if not partial_result.get('success'):
                current_app.logger.warning(f"Falha ao salvar passo {step}: {partial_result.get('error')}")
            else:
                # Se é o último passo, as preferências de alerta já foram criadas
                if step in ['5', 5]:
                    current_app.logger.info(f"Onboarding finalizado e preferências de alerta criadas para {current_user.email}")
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar passo {step} parcial: {str(e)}")
        
        # Salvar dados finais no banco no último passo (cumulativo)
        if step in ['5', 5]:
            # Combinar todos os dados dos passos
            all_data = {}
            for step_key, step_data in session['onboarding_data'].items():
                all_data.update(step_data)
            
            # Salvar no banco de dados (final consolidado)
            result = AuthService.save_onboarding_step(current_user, step, all_data)
            
            # Limpar dados temporários da sessão
            session.pop('onboarding_data', None)
            
            return ResponseHandler.handle_success(result)
        else:
            # Para passos intermediários, confirmar salvamento
            return ResponseHandler.handle_success({'message': f'Dados do passo {step} salvos com sucesso'})
        
    except Exception as e:
        LoggingHelper.log_error(e, 'auth.save_onboarding')
        return ResponseHandler.handle_server_error('Erro ao salvar dados')


@auth_bp.route('/onboarding/clear', methods=['POST'])
@login_required
@require_valid_session
def clear_onboarding_data():
    """Limpar dados temporários do onboarding"""
    try:
        LoggingHelper.log_request('auth.clear_onboarding_data', 'POST', current_user.email)
        
        # Limpar dados da sessão
        session.pop('onboarding_data', None)
        
        return ResponseHandler.handle_success({'message': 'Dados temporários limpos'})
        
    except Exception as e:
        LoggingHelper.log_error(e, 'auth.clear_onboarding_data')
        return ResponseHandler.handle_server_error('Erro ao limpar dados')


@auth_bp.route('/check')
def check_auth():
    """Verificar se o usuário está autenticado - CORREÇÃO SPRINT 1"""
    LoggingHelper.log_request('auth.check', 'GET')
    
    if not current_user.is_authenticated:
        # CORREÇÃO SPRINT 1: Retornar 401 para usuários não autenticados
        return ResponseHandler.handle_auth_error(
            'Usuário não autenticado'
        )
    
    result = AuthService.get_user_auth_status(current_user)
    return ResponseHandler.handle_success(result)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Rota de logout - Refatorada"""
    try:
        user_email = current_user.email
        LoggingHelper.log_request('auth.logout', request.method, user_email)
        LoggingHelper.log_user_action(user_email, 'LOGOUT')
        
        # Limpar dados da sessão
        session.clear()
        
        # Fazer logout do usuário
        logout_user()
        
        success_data = {
            'success': True,
            'message': 'Logout realizado com sucesso!'
        }
        
        # Resposta com cabeçalhos de segurança
        response = ResponseHandler.handle_success(
            success_data,
            redirect_url=url_for('auth.login')
        )
        
        # Adicionar cabeçalhos de segurança para evitar cache
        if hasattr(response, 'headers'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        LoggingHelper.log_error(e, 'auth.logout')
        return ResponseHandler.handle_server_error(
            'Erro interno durante logout',
            'auth/login.html'
        )


@auth_bp.route('/detect-climate', methods=['POST'])
@login_required
def detect_climate():
    """Endpoint para detectar clima regional baseado na localização"""
    try:
        from app.services.climate_detection_service import ClimateDetectionService
        
        data = request.get_json()
        location = data.get('location', '')
        coordinates = data.get('coordinates', {})
        
        logger.info(f"Detectando clima para localização: {location}")
        
        # Usar o serviço de detecção de clima
        climate_info = ClimateDetectionService.detect_climate_from_location(
            location=location,
            coordinates=coordinates
        )
        
        return ResponseHandler.handle_success({
            'success': True,
            'climate': climate_info.get('climate', ''),
            'confidence': climate_info.get('confidence', 'low'),
            'description': climate_info.get('description', ''),
            'method': climate_info.get('method', 'unknown'),
            'region': climate_info.get('region', '')
        })
        
    except Exception as e:
        logger.error(f"Erro na detecção de clima: {str(e)}")
        return ResponseHandler.handle_error(
            'Erro na detecção automática de clima',
            status_code=500
        )
