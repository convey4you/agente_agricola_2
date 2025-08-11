# app/controllers/api_integration_controller.py
"""
Controlador para integração robusta de APIs - Sprint 4 Prompt 2
"""
import logging
from typing import Dict, Any, List
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user

from app.services.weather_data_service import WeatherDataService
from app.services.ai_service_v2 import AIServiceV2
from app.utils.api_integration import APIIntegrationManager, BatchAPIProcessor
from app.utils.response_helpers import ResponseHandler, LoggingHelper

# Configurar logging
logger = logging.getLogger(__name__)

api_integration_bp = Blueprint('api_integration', __name__, url_prefix='/api/integration')


@api_integration_bp.route('/status')
@login_required
def integration_status():
    """Status geral da integração de APIs"""
    try:
        LoggingHelper.log_request('api_integration.status', 'GET', current_user.email)
        
        # Verificar configurações de API
        weather_api_configured = bool(current_app.config.get('WEATHER_API_KEY'))
        ai_api_configured = bool(current_app.config.get('OPENAI_API_KEY'))
        
        # Inicializar gerenciador de integração
        api_manager = APIIntegrationManager()
        
        # Obter estatísticas dos rate limiters e circuit breakers
        rate_limiter_stats = {}
        circuit_breaker_stats = {}
        
        for api_name in api_manager.rate_limiters:
            limiter = api_manager.rate_limiters[api_name]
            rate_limiter_stats[api_name] = {
                'calls_remaining': limiter.calls - len(limiter.call_times),
                'reset_time': limiter.get_reset_time()
            }
        
        for api_name in api_manager.circuit_breakers:
            breaker = api_manager.circuit_breakers[api_name]
            circuit_breaker_stats[api_name] = {
                'state': breaker.state,
                'failure_count': breaker.failure_count,
                'last_failure_time': breaker.last_failure_time
            }
        
        status_data = {
            'apis_configured': {
                'weather': weather_api_configured,
                'ai': ai_api_configured
            },
            'rate_limiters': rate_limiter_stats,
            'circuit_breakers': circuit_breaker_stats,
            'integration_healthy': weather_api_configured or ai_api_configured
        }
        
        return ResponseHandler.handle_success(status_data)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.status')
        return ResponseHandler.handle_server_error('Erro ao verificar status da integração')


@api_integration_bp.route('/weather/current')
@login_required
def get_current_weather():
    """Obter clima atual usando integração robusta"""
    try:
        LoggingHelper.log_request('api_integration.current_weather', 'GET', current_user.email)
        
        # Obter parâmetros
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        # Validar parâmetros obrigatórios
        if latitude is None or longitude is None:
            return ResponseHandler.handle_validation_error(
                'latitude e longitude são obrigatórios'
            )
        
        # Verificar API key
        api_key = current_app.config.get('WEATHER_API_KEY')
        if not api_key:
            return ResponseHandler.handle_server_error(
                'WEATHER_API_KEY não configurada', 
                503
            )
        
        # Usar serviço robusto
        weather_service = WeatherDataService()
        result = weather_service.get_current_weather(latitude, longitude, api_key)
        
        if result['success']:
            LoggingHelper.log_user_action(current_user.email, 'WEATHER_API_SUCCESS')
            return ResponseHandler.handle_success(result)
        else:
            logger.warning(f"Weather API failure: {result.get('error')}")
            return ResponseHandler.handle_server_error(
                result.get('error', 'Erro no serviço meteorológico'),
                503
            )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.current_weather')
        return ResponseHandler.handle_server_error('Erro ao obter dados meteorológicos')


@api_integration_bp.route('/weather/forecast')
@login_required
def get_weather_forecast():
    """Obter previsão meteorológica usando integração robusta"""
    try:
        LoggingHelper.log_request('api_integration.weather_forecast', 'GET', current_user.email)
        
        # Obter parâmetros
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        days = request.args.get('days', 5, type=int)
        
        # Validar parâmetros
        if latitude is None or longitude is None:
            return ResponseHandler.handle_validation_error(
                'latitude e longitude são obrigatórios'
            )
        
        if days < 1 or days > 10:
            return ResponseHandler.handle_validation_error(
                'days deve estar entre 1 e 10'
            )
        
        # Verificar API key
        api_key = current_app.config.get('WEATHER_API_KEY')
        if not api_key:
            return ResponseHandler.handle_server_error(
                'WEATHER_API_KEY não configurada', 
                503
            )
        
        # Usar serviço robusto
        weather_service = WeatherDataService()
        result = weather_service.get_weather_forecast(latitude, longitude, api_key, days)
        
        if result['success']:
            LoggingHelper.log_user_action(current_user.email, 'WEATHER_FORECAST_SUCCESS')
            return ResponseHandler.handle_success(result)
        else:
            logger.warning(f"Weather forecast API failure: {result.get('error')}")
            return ResponseHandler.handle_server_error(
                result.get('error', 'Erro no serviço de previsão'),
                503
            )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.weather_forecast')
        return ResponseHandler.handle_server_error('Erro ao obter previsão meteorológica')


@api_integration_bp.route('/ai/recommendation', methods=['POST'])
@login_required
def get_ai_recommendation():
    """Obter recomendação de IA usando integração robusta"""
    try:
        LoggingHelper.log_request('api_integration.ai_recommendation', 'POST', current_user.email)
        
        # Obter dados do request
        data = request.get_json()
        if not data:
            return ResponseHandler.handle_validation_error('Dados JSON obrigatórios')
        
        # Validar campos obrigatórios
        culture_data = data.get('culture_data')
        weather_data = data.get('weather_data')
        
        if not culture_data:
            return ResponseHandler.handle_validation_error('culture_data é obrigatório')
        
        if not weather_data:
            return ResponseHandler.handle_validation_error('weather_data é obrigatório')
        
        # Verificar API key
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            return ResponseHandler.handle_server_error(
                'OPENAI_API_KEY não configurada', 
                503
            )
        
        # Usar serviço de IA robusto
        ai_service = AIServiceV2()
        result = ai_service.get_agricultural_recommendation(
            culture_data, 
            weather_data, 
            api_key
        )
        
        if result['success']:
            LoggingHelper.log_user_action(current_user.email, 'AI_RECOMMENDATION_SUCCESS')
            return ResponseHandler.handle_success(result)
        else:
            logger.warning(f"AI API failure: {result.get('error')}")
            return ResponseHandler.handle_server_error(
                result.get('error', 'Erro no serviço de IA'),
                503
            )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.ai_recommendation')
        return ResponseHandler.handle_server_error('Erro ao obter recomendação de IA')


@api_integration_bp.route('/ai/pest-analysis', methods=['POST'])
@login_required
def get_pest_analysis():
    """Análise de pragas e doenças usando IA robusta"""
    try:
        LoggingHelper.log_request('api_integration.pest_analysis', 'POST', current_user.email)
        
        # Obter dados do request
        data = request.get_json()
        if not data:
            return ResponseHandler.handle_validation_error('Dados JSON obrigatórios')
        
        # Validar campos obrigatórios
        symptoms = data.get('symptoms')
        culture_type = data.get('culture_type')
        
        if not symptoms:
            return ResponseHandler.handle_validation_error('symptoms é obrigatório')
        
        if not culture_type:
            return ResponseHandler.handle_validation_error('culture_type é obrigatório')
        
        # Verificar API key
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            return ResponseHandler.handle_server_error(
                'OPENAI_API_KEY não configurada', 
                503
            )
        
        # Usar serviço de IA robusto
        ai_service = AIServiceV2()
        result = ai_service.analyze_pest_disease(symptoms, culture_type, api_key)
        
        if result['success']:
            LoggingHelper.log_user_action(current_user.email, 'AI_PEST_ANALYSIS_SUCCESS')
            return ResponseHandler.handle_success(result)
        else:
            logger.warning(f"AI pest analysis failure: {result.get('error')}")
            return ResponseHandler.handle_server_error(
                result.get('error', 'Erro na análise de pragas'),
                503
            )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.pest_analysis')
        return ResponseHandler.handle_server_error('Erro na análise de pragas e doenças')


@api_integration_bp.route('/ai/planning-advice', methods=['POST'])
@login_required
def get_planning_advice():
    """Conselhos de planeamento agrícola usando IA robusta"""
    try:
        LoggingHelper.log_request('api_integration.planning_advice', 'POST', current_user.email)
        
        # Obter dados do request
        data = request.get_json()
        if not data:
            return ResponseHandler.handle_validation_error('Dados JSON obrigatórios')
        
        # Validar campos obrigatórios
        location = data.get('location')
        season = data.get('season')
        
        if not location:
            return ResponseHandler.handle_validation_error('location é obrigatório')
        
        if not season:
            return ResponseHandler.handle_validation_error('season é obrigatório')
        
        # Campos opcionais
        current_cultures = data.get('current_cultures', [])
        
        # Verificar API key
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            return ResponseHandler.handle_server_error(
                'OPENAI_API_KEY não configurada', 
                503
            )
        
        # Usar serviço de IA robusto
        ai_service = AIServiceV2()
        result = ai_service.get_planning_advice(location, season, current_cultures, api_key)
        
        if result['success']:
            LoggingHelper.log_user_action(current_user.email, 'AI_PLANNING_SUCCESS')
            return ResponseHandler.handle_success(result)
        else:
            logger.warning(f"AI planning advice failure: {result.get('error')}")
            return ResponseHandler.handle_server_error(
                result.get('error', 'Erro nos conselhos de planeamento'),
                503
            )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.planning_advice')
        return ResponseHandler.handle_server_error('Erro ao obter conselhos de planeamento')


@api_integration_bp.route('/batch/weather-data', methods=['POST'])
@login_required
def batch_weather_requests():
    """Processamento em lote de pedidos meteorológicos"""
    try:
        LoggingHelper.log_request('api_integration.batch_weather', 'POST', current_user.email)
        
        # Obter dados do request
        data = request.get_json()
        if not data:
            return ResponseHandler.handle_validation_error('Dados JSON obrigatórios')
        
        locations = data.get('locations', [])
        if not locations:
            return ResponseHandler.handle_validation_error('locations é obrigatório')
        
        if len(locations) > 10:
            return ResponseHandler.handle_validation_error('Máximo de 10 localizações por lote')
        
        # Verificar API key
        api_key = current_app.config.get('WEATHER_API_KEY')
        if not api_key:
            return ResponseHandler.handle_server_error(
                'WEATHER_API_KEY não configurada', 
                503
            )
        
        # Preparar pedidos para processamento em lote
        api_manager = APIIntegrationManager()
        batch_processor = BatchAPIProcessor(api_manager, max_workers=5)
        
        # Registrar API meteorológica se não estiver registrada
        if 'openweather' not in api_manager.rate_limiters:
            api_manager.register_api('openweather', {
                'rate_limit_calls': 1000,
                'rate_limit_period': 3600,
                'failure_threshold': 5,
                'recovery_timeout': 60
            })
        
        # Criar lista de pedidos
        batch_requests = []
        for location in locations:
            if 'latitude' not in location or 'longitude' not in location:
                continue
                
            batch_requests.append({
                'api_name': 'openweather',
                'method': 'GET',
                'url': f"https://api.openweathermap.org/data/2.5/weather",
                'kwargs': {
                    'params': {
                        'lat': location['latitude'],
                        'lon': location['longitude'],
                        'appid': api_key,
                        'units': 'metric',
                        'lang': 'pt'
                    }
                }
            })
        
        # Processar em lote
        results = batch_processor.process_batch_requests(batch_requests)
        
        # Processar resultados
        processed_results = []
        for i, result in enumerate(results):
            location_data = locations[i] if i < len(locations) else {}
            processed_results.append({
                'location': location_data,
                'success': result.get('success', False),
                'data': result.get('data'),
                'error': result.get('error'),
                'duration': result.get('duration', 0)
            })
        
        LoggingHelper.log_user_action(current_user.email, 'BATCH_WEATHER_SUCCESS')
        
        return ResponseHandler.handle_success({
            'results': processed_results,
            'total_requests': len(batch_requests),
            'successful_requests': sum(1 for r in results if r.get('success')),
            'batch_duration': sum(r.get('duration', 0) for r in results)
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.batch_weather')
        return ResponseHandler.handle_server_error('Erro no processamento em lote')


@api_integration_bp.route('/test/connectivity')
@login_required
def test_api_connectivity():
    """Testar conectividade com APIs externas"""
    try:
        LoggingHelper.log_request('api_integration.test_connectivity', 'GET', current_user.email)
        
        connectivity_results = {}
        
        # Testar API meteorológica
        weather_api_key = current_app.config.get('WEATHER_API_KEY')
        if weather_api_key:
            try:
                weather_service = WeatherDataService()
                weather_test = weather_service.get_current_weather(
                    "Lisboa", weather_api_key  # Simplified for new service
                )
                connectivity_results['weather'] = {
                    'configured': True,
                    'reachable': weather_test.get('success', False),
                    'error': weather_test.get('error'),
                    'duration': weather_test.get('duration', 0)
                }
            except Exception as e:
                connectivity_results['weather'] = {
                    'configured': True,
                    'reachable': False,
                    'error': str(e)
                }
        else:
            connectivity_results['weather'] = {
                'configured': False,
                'reachable': False,
                'error': 'WEATHER_API_KEY não configurada'
            }
        
        # Testar API de IA
        ai_api_key = current_app.config.get('OPENAI_API_KEY')
        if ai_api_key:
            try:
                ai_service = AIServiceV2()
                ai_test = ai_service.get_agricultural_recommendation(
                    {'type': 'teste', 'area': 1},
                    {'temperature': 20, 'humidity': 60},
                    ai_api_key
                )
                connectivity_results['ai'] = {
                    'configured': True,
                    'reachable': ai_test.get('success', False),
                    'error': ai_test.get('error'),
                    'duration': ai_test.get('duration', 0)
                }
            except Exception as e:
                connectivity_results['ai'] = {
                    'configured': True,
                    'reachable': False,
                    'error': str(e)
                }
        else:
            connectivity_results['ai'] = {
                'configured': False,
                'reachable': False,
                'error': 'OPENAI_API_KEY não configurada'
            }
        
        # Calcular status geral
        overall_health = any(
            result.get('reachable', False) 
            for result in connectivity_results.values()
        )
        
        return ResponseHandler.handle_success({
            'overall_health': overall_health,
            'apis': connectivity_results,
            'timestamp': LoggingHelper.get_current_timestamp()
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.test_connectivity')
        return ResponseHandler.handle_server_error('Erro no teste de conectividade')


@api_integration_bp.route('/metrics')
@login_required
def get_integration_metrics():
    """Métricas de performance da integração de APIs"""
    try:
        LoggingHelper.log_request('api_integration.metrics', 'GET', current_user.email)
        
        # Inicializar gerenciador
        api_manager = APIIntegrationManager()
        
        metrics = {
            'rate_limiters': {},
            'circuit_breakers': {},
            'cache_stats': {},
            'performance': {}
        }
        
        # Métricas dos rate limiters
        for api_name, limiter in api_manager.rate_limiters.items():
            metrics['rate_limiters'][api_name] = {
                'total_calls_allowed': limiter.calls,
                'period_seconds': limiter.period,
                'calls_made': len(limiter.call_times),
                'calls_remaining': limiter.calls - len(limiter.call_times),
                'reset_time_seconds': limiter.get_reset_time()
            }
        
        # Métricas dos circuit breakers
        for api_name, breaker in api_manager.circuit_breakers.items():
            metrics['circuit_breakers'][api_name] = {
                'state': breaker.state,
                'failure_count': breaker.failure_count,
                'failure_threshold': breaker.failure_threshold,
                'recovery_timeout': breaker.recovery_timeout,
                'last_failure_time': breaker.last_failure_time,
                'success_count': getattr(breaker, 'success_count', 0)
            }
        
        # Métricas de cache (se disponível)
        try:
            from app.utils.cache import CacheManager
            cache_manager = CacheManager()
            if hasattr(cache_manager, 'get_stats'):
                metrics['cache_stats'] = cache_manager.get_stats()
        except Exception:
            metrics['cache_stats'] = {'available': False}
        
        return ResponseHandler.handle_success(metrics)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'api_integration.metrics')
        return ResponseHandler.handle_server_error('Erro ao obter métricas')


# Registrar blueprint
def register_api_integration_routes(app):
    """Registrar rotas de integração de APIs"""
    app.register_blueprint(api_integration_bp)
