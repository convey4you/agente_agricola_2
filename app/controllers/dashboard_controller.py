"""
Controlador do dashboard - Simplificado
"""
import logging
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from app.services.dashboard_service import DashboardService
from app.services.weather_data_service import WeatherDataService
from app.services.weather_collector import WeatherCollectorService

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required  
def index():
    """Dashboard principal"""
    try:
        # Importar datetime para fornecer a data atual
        from datetime import datetime, timedelta
        
        # Obter dados básicos do dashboard
        result = DashboardService.get_dashboard_data()
        
        if not result['success']:
            # Em caso de erro, fornecer dados vazios
            context = {
                'overview': {
                    'active_cultures': 0,
                    'total_area': 0,
                    'monthly_production': 0,
                    'projected_revenue': 0
                },
                'alerts': [],
                'weather': None,
                'recent_activities': [],
                'cultures': []
            }
        else:
            context = result['data']
            # Garantir que cultures está disponível no contexto principal
            if 'cultures' in context:
                context['cultures'] = context['cultures']
        
        # Adicionar a variável hoje para o template
        context['hoje'] = 0  # Começa com 0 para o dia atual
        
        # Tentar obter dados de clima do novo serviço
        try:
            weather_result = WeatherDataService.get_current_weather()
            
            if weather_result['success']:
                context['weather'] = weather_result['data']
            else:
                context['weather'] = None
                logger.warning(f"Falha ao obter dados meteorológicos: {weather_result.get('message')}")
        except Exception as e:
            logger.error(f"Erro ao acessar serviço meteorológico: {e}")
            context['weather'] = None
        
        return render_template('dashboard/index.html', **context)
    
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        # Contexto mínimo em caso de erro crítico
        return render_template('dashboard/index.html', 
                             overview={'active_cultures': 0, 'total_area': 0, 'monthly_production': 0, 'projected_revenue': 0},
                             alerts=[], weather=None, recent_activities=[], cultures=[])


@dashboard_bp.route('/weather/refresh')
@login_required
def refresh_weather():
    """Endpoint para atualizar dados meteorológicos baseado na localização do usuário"""
    try:
        # Usar localização do usuário logado se disponível
        location_name = None
        lat = None
        lon = None
        
        if current_user.cidade:
            location_name = current_user.cidade
            logger.info(f"Usando localização do usuário: {location_name}")
        elif current_user.latitude and current_user.longitude:
            lat = current_user.latitude
            lon = current_user.longitude
            logger.info(f"Usando coordenadas do usuário: {lat}, {lon}")
        else:
            logger.info("Usuário sem localização definida, usando localização padrão")
        
        result = WeatherDataService.get_current_weather(
            location_name=location_name,
            lat=lat,
            lon=lon
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Falha ao obter dados meteorológicos')
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao atualizar clima: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@dashboard_bp.route('/weather/force-collect')
@login_required
def force_collect_weather():
    """Endpoint para forçar coleta da API e retornar dados atualizados"""
    try:
        # Executar coleta da API
        collection_result = WeatherCollectorService.force_collection_now()
        
        # Aguardar um pouco para garantir que os dados foram salvos
        import time
        time.sleep(1)
        
        # Usar localização do usuário logado se disponível
        location_name = None
        lat = None
        lon = None
        
        if current_user.cidade:
            location_name = current_user.cidade
        elif current_user.latitude and current_user.longitude:
            lat = current_user.latitude
            lon = current_user.longitude
        
        # Obter dados atualizados
        result = WeatherDataService.get_current_weather(
            location_name=location_name,
            lat=lat,
            lon=lon
        )
        
        return jsonify({
            'success': result['success'],
            'data': result.get('data'),
            'collection': {
                'success': collection_result.get('success', False),
                'locations_processed': collection_result.get('locations_processed', 0),
                'message': f"{collection_result.get('locations_processed', 0)} localizações atualizadas"
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao forçar coleta: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao executar coleta da API'
        }), 500


@dashboard_bp.route('/api')
@login_required
def api_dashboard():
    """API para dados do dashboard"""
    try:
        result = DashboardService.get_dashboard_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro na API do dashboard: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500


@dashboard_bp.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    """API para estatísticas do dashboard"""
    try:
        result = DashboardService.get_dashboard_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro na API de estatísticas do dashboard: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500


@dashboard_bp.route('/api/dashboard/alertas')
@login_required
def api_dashboard_alertas():
    """API para alertas do dashboard"""
    try:
        from app.services.alert_service import AlertService
        alert_service = AlertService()
        
        # Buscar alertas ativos do usuário
        alerts = alert_service.get_active_alerts(current_user.id, limit=10)
        
        # Converter para dicionário
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'type': alert.type.value,
                'priority': alert.priority.value,
                'title': alert.title,
                'message': alert.message,
                'created_at': alert.created_at.isoformat() if alert.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': alerts_data,
            'total': len(alerts_data)
        })
    except Exception as e:
        logger.error(f"Erro na API de alertas do dashboard: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500


@dashboard_bp.route('/api/dashboard/culturas')
@login_required
def api_dashboard_culturas():
    """API para culturas do dashboard"""
    try:
        result = DashboardService.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': result.get('culturas', [])
        })
    except Exception as e:
        logger.error(f"Erro na API de culturas do dashboard: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500


@dashboard_bp.route('/api/dashboard/animais')
@login_required
def api_dashboard_animais():
    """API para animais do dashboard"""
    try:
        result = DashboardService.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': result.get('animais', [])
        })
    except Exception as e:
        logger.error(f"Erro na API de animais do dashboard: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500


@dashboard_bp.route('/api/dashboard/tarefas')
@login_required
def api_dashboard_tarefas():
    """API para tarefas do dashboard"""
    try:
        result = DashboardService.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': result.get('tarefas', [])
        })
    except Exception as e:
        logger.error(f"Erro na API de tarefas do dashboard: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500
