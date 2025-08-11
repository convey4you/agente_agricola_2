"""
Cache Controller - Gerenciamento do sistema de cache
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.utils.cache_manager import cache
from app.utils.response_helpers import ResponseHandler
from app.utils.logging_helpers import LoggingHelper
from app.services.weather_data_service import WeatherDataService
from app.services.ai_service import AIService
from app.services.dashboard_service import DashboardService
from app.services.culture_service import CultureService

cache_bp = Blueprint('cache', __name__)
logger = LoggingHelper()


@cache_bp.route('/stats')
@login_required
def get_cache_stats():
    """Obter estatísticas do cache"""
    try:
        stats = cache.get_stats()
        
        # Adicionar estatísticas específicas por namespace
        namespace_stats = {}
        
        # Stats de IA
        ai_stats = AIService.get_ai_cache_stats()
        namespace_stats['ai'] = ai_stats
        
        stats['namespaces'] = namespace_stats
        
        logger.log_user_action("cache_stats", "get_cache_stats", "Estatísticas obtidas")
        return ResponseHandler.handle_success(
            data=stats,
        )
        
    except Exception as e:
        logger.log_error(f"Erro ao obter estatísticas de cache: {str(e)}")
        return ResponseHandler.handle_server_error("Erro interno do servidor")


@cache_bp.route('/health')
def get_cache_health():
    """Verificar saúde do sistema de cache"""
    try:
        health = cache.health_check()
        
        logger.log_user_action("cache_health", "get_cache_health", "Health check realizado")
        
        response = ResponseHandler.handle_success(data=health)
        if health['status'] != 'healthy':
            response.status_code = 503
        
        return response
        
    except Exception as e:
        logger.log_error(f"Erro no health check do cache: {str(e)}")
        return ResponseHandler.handle_server_error("Erro interno do servidor")


@cache_bp.route('/clear', methods=['POST'])
@login_required
def clear_cache():
    """Limpar cache por namespace ou tudo"""
    try:
        data = request.get_json() or {}
        namespace = data.get('namespace')
        
        if namespace:
            # Limpar namespace específico
            if namespace == 'weather':
                # cleared = WeatherDataService.clear_cache()  # TODO: implementar se necessário
                cleared = 0  # Temporário até implementar cache no WeatherDataService
            elif namespace == 'ai':
                cleared = AIService.clear_all_ai_cache()
            elif namespace == 'dashboard':
                cleared = DashboardService.clear_all_dashboard_cache()
            elif namespace == 'culture':
                cleared = CultureService.clear_all_culture_cache()
            else:
                cleared = cache.clear_namespace(namespace)
            
            message = f"Cache do namespace '{namespace}' limpo: {cleared} chaves removidas"
        else:
            # Limpar todos os namespaces
            total_cleared = 0
            # total_cleared += WeatherDataService.clear_cache()  # TODO: implementar se necessário
            total_cleared += 0  # Temporário
            total_cleared += AIService.clear_all_ai_cache()
            total_cleared += DashboardService.clear_all_dashboard_cache()
            total_cleared += CultureService.clear_all_culture_cache()
            
            message = f"Todo o cache limpo: {total_cleared} chaves removidas"
            cleared = total_cleared
        
        logger.log_user_action(current_user.email if hasattr(current_user, 'email') else 'user', "clear_cache", f"Cache limpo: {message}")
        return ResponseHandler.handle_success(
            data={'cleared_keys': cleared, 'namespace': namespace},
        )
        
    except Exception as e:
        logger.log_error(f"Erro ao limpar cache: {str(e)}")
        return ResponseHandler.handle_server_error("Erro interno do servidor")


@cache_bp.route('/invalidate/user', methods=['POST'])
@login_required
def invalidate_user_cache():
    """Invalidar cache específico do usuário atual"""
    try:
        data = request.get_json() or {}
        cache_types = data.get('types', ['dashboard', 'culture'])
        
        invalidated = []
        
        if 'dashboard' in cache_types:
            if DashboardService.invalidate_user_dashboard_cache(current_user.id):
                invalidated.append('dashboard')
        
        if 'culture' in cache_types:
            if CultureService.invalidate_user_culture_cache(current_user.id):
                invalidated.append('culture')
        
        if 'ai' in cache_types:
            if AIService.invalidate_user_ai_cache(current_user.id):
                invalidated.append('ai')
        
        message = f"Cache invalidado para tipos: {', '.join(invalidated)}"
        
        logger.log_user_action(current_user.email if hasattr(current_user, 'email') else 'user', "invalidate_user_cache", f"Cache invalidado: {invalidated}")
        return ResponseHandler.handle_success(
            data={'invalidated_types': invalidated},
        )
        
    except Exception as e:
        logger.log_error(f"Erro ao invalidar cache de usuário: {str(e)}")
        return ResponseHandler.handle_server_error("Erro interno do servidor")


@cache_bp.route('/invalidate/weather', methods=['POST'])
@login_required
def invalidate_weather_cache():
    """Invalidar cache meteorológico para uma localização"""
    try:
        data = request.get_json() or {}
        location = data.get('location')
        
        if not location:
            return ResponseHandler.handle_error("Localização não fornecida", 400)
        
        if not isinstance(location, dict) or 'latitude' not in location or 'longitude' not in location:
            return ResponseHandler.handle_error("Localização deve conter latitude e longitude", 400)
        
        # success = WeatherDataService.invalidate_cache(location)  # TODO: implementar se necessário
        success = True  # Temporário
        
        if success:
            message = f"Cache meteorológico invalidado para {location['latitude']}, {location['longitude']}"
            logger.log_info(message)
            return ResponseHandler.success(
                data={'invalidated': True, 'location': location},
                message=message
            )
        else:
            return ResponseHandler.handle_error("Falha ao invalidar cache meteorológico", 500)
        
    except Exception as e:
        logger.log_error(f"Erro ao invalidar cache meteorológico: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@cache_bp.route('/invalidate/culture/<int:culture_id>', methods=['POST'])
@login_required
def invalidate_culture_cache(culture_id):
    """Invalidar cache de uma cultura específica"""
    try:
        success = CultureService.invalidate_cache_on_culture_change(culture_id, current_user.id)
        
        if success:
            message = f"Cache invalidado para cultura {culture_id}"
            logger.log_info(message)
            return ResponseHandler.success(
                data={'invalidated': True, 'culture_id': culture_id},
                message=message
            )
        else:
            return ResponseHandler.handle_error("Falha ao invalidar cache da cultura", 500)
        
    except Exception as e:
        logger.log_error(f"Erro ao invalidar cache da cultura: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@cache_bp.route('/refresh/dashboard', methods=['POST'])
@login_required
def refresh_dashboard_cache():
    """Forçar atualização do cache do dashboard"""
    try:
        success = DashboardService.refresh_dashboard_cache_for_user(current_user.id)
        
        if success:
            message = "Cache do dashboard será renovado"
            logger.log_info(f"Renovação de cache solicitada para usuário {current_user.id}")
            return ResponseHandler.success(
                data={'refresh_requested': True},
                message=message
            )
        else:
            return ResponseHandler.handle_error("Falha ao renovar cache do dashboard", 500)
        
    except Exception as e:
        logger.log_error(f"Erro ao renovar cache do dashboard: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@cache_bp.route('/key/<namespace>/<key>', methods=['GET'])
@login_required
def get_cache_key(namespace, key):
    """Obter valor específico do cache"""
    try:
        value = cache.get(key, namespace)
        
        if value is not None:
            logger.log_info(f"Valor obtido do cache: {namespace}:{key}")
            return ResponseHandler.success(
                data={'value': value, 'found': True},
                message="Valor encontrado no cache"
            )
        else:
            logger.log_info(f"Valor não encontrado no cache: {namespace}:{key}")
            return ResponseHandler.success(
                data={'value': None, 'found': False},
                message="Valor não encontrado no cache"
            )
        
    except Exception as e:
        logger.log_error(f"Erro ao obter valor do cache: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@cache_bp.route('/key/<namespace>/<key>', methods=['DELETE'])
@login_required
def delete_cache_key(namespace, key):
    """Deletar chave específica do cache"""
    try:
        success = cache.delete(key, namespace)
        
        message = f"Chave {'deletada' if success else 'não encontrada'}: {namespace}:{key}"
        logger.log_info(message)
        
        return ResponseHandler.success(
            data={'deleted': success},
            message=message
        )
        
    except Exception as e:
        logger.log_error(f"Erro ao deletar chave do cache: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)
