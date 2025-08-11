# app/controllers/performance_monitoring_controller.py
"""
Controlador para monitorização de performance - Sprint 4 Prompt 3
"""
import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.utils.performance_monitoring import (
    performance_monitor, get_performance_dashboard_data
)
from app.utils.response_helpers import ResponseHandler, LoggingHelper

# Configurar logging
logger = logging.getLogger(__name__)

performance_monitoring_bp = Blueprint('performance_monitoring', __name__, url_prefix='/api/performance')


@performance_monitoring_bp.route('/dashboard')
@login_required
def performance_dashboard():
    """Dashboard de monitorização de performance"""
    try:
        LoggingHelper.log_request('performance.dashboard', 'GET', current_user.email)
        
        # Verificar se usuário tem permissão (admin ou desenvolvedor)
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error(
                'Acesso negado. Apenas administradores podem visualizar métricas de performance.'
            )
        
        dashboard_data = get_performance_dashboard_data()
        
        return ResponseHandler.handle_success(dashboard_data)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.dashboard')
        return ResponseHandler.handle_server_error('Erro ao obter dados de performance')


@performance_monitoring_bp.route('/metrics/summary')
@login_required
def metrics_summary():
    """Resumo de métricas de performance"""
    try:
        LoggingHelper.log_request('performance.metrics_summary', 'GET', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error(
                'Acesso negado'
            )
        
        summary = performance_monitor.get_performance_summary()
        
        return ResponseHandler.handle_success(summary)
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.metrics_summary')
        return ResponseHandler.handle_server_error('Erro ao obter resumo de métricas')


@performance_monitoring_bp.route('/metrics/history/<metric_name>')
@login_required
def metrics_history(metric_name: str):
    """Histórico de uma métrica específica"""
    try:
        LoggingHelper.log_request('performance.metrics_history', 'GET', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        # Obter parâmetros
        hours = request.args.get('hours', 1, type=int)
        
        # Validar parâmetros
        if hours < 1 or hours > 24:
            return ResponseHandler.handle_validation_error(
                'Parâmetro hours deve estar entre 1 e 24'
            )
        
        # Validar métrica
        valid_metrics = [
            'response_time', 'cpu_usage', 'memory_usage', 'disk_usage',
            'active_connections', 'error_rate', 'cache_hit_rate'
        ]
        
        if metric_name not in valid_metrics:
            return ResponseHandler.handle_validation_error(
                f'Métrica inválida. Métricas válidas: {", ".join(valid_metrics)}'
            )
        
        history = performance_monitor.get_metrics_history(metric_name, hours)
        
        return ResponseHandler.handle_success({
            'metric_name': metric_name,
            'hours': hours,
            'data_points': len(history),
            'history': history
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.metrics_history')
        return ResponseHandler.handle_server_error('Erro ao obter histórico de métricas')


@performance_monitoring_bp.route('/alerts')
@login_required
def get_alerts():
    """Obter alertas ativos"""
    try:
        LoggingHelper.log_request('performance.alerts', 'GET', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        # Obter parâmetros
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        if active_only:
            alerts = performance_monitor.get_active_alerts()
        else:
            # Retornar todos os alertas (últimos 100)
            with performance_monitor._lock:
                alerts = [alert.to_dict() for alert in performance_monitor.alerts[-100:]]
        
        return ResponseHandler.handle_success({
            'active_only': active_only,
            'count': len(alerts),
            'alerts': alerts
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.alerts')
        return ResponseHandler.handle_server_error('Erro ao obter alertas')


@performance_monitoring_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id: str):
    """Resolver um alerta"""
    try:
        LoggingHelper.log_request('performance.resolve_alert', 'POST', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        # Tentar resolver o alerta
        resolved = performance_monitor.resolve_alert(alert_id)
        
        if resolved:
            LoggingHelper.log_user_action(current_user.email, 'ALERT_RESOLVED', {'alert_id': alert_id})
            return ResponseHandler.handle_success({
                'alert_id': alert_id,
                'resolved': True,
                'message': 'Alerta resolvido com sucesso'
            })
        else:
            return ResponseHandler.handle_validation_error(
                'Alerta não encontrado ou já resolvido'
            )
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.resolve_alert')
        return ResponseHandler.handle_server_error('Erro ao resolver alerta')


@performance_monitoring_bp.route('/thresholds')
@login_required
def get_thresholds():
    """Obter thresholds configurados"""
    try:
        LoggingHelper.log_request('performance.thresholds', 'GET', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        return ResponseHandler.handle_success({
            'thresholds': performance_monitor.thresholds
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.thresholds')
        return ResponseHandler.handle_server_error('Erro ao obter thresholds')


@performance_monitoring_bp.route('/thresholds/<metric_name>', methods=['PUT'])
@login_required
def update_threshold(metric_name: str):
    """Atualizar threshold de uma métrica"""
    try:
        LoggingHelper.log_request('performance.update_threshold', 'PUT', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        # Obter dados do request
        data = request.get_json()
        if not data:
            return ResponseHandler.handle_validation_error('Dados JSON obrigatórios')
        
        threshold = data.get('threshold')
        if threshold is None:
            return ResponseHandler.handle_validation_error('Campo threshold é obrigatório')
        
        # Validar threshold
        try:
            threshold = float(threshold)
            if threshold <= 0:
                return ResponseHandler.handle_validation_error('Threshold deve ser maior que zero')
        except (ValueError, TypeError):
            return ResponseHandler.handle_validation_error('Threshold deve ser um número válido')
        
        # Validar métrica
        valid_metrics = [
            'response_time', 'cpu_usage', 'memory_usage', 'disk_usage',
            'active_connections', 'error_rate', 'cache_hit_rate'
        ]
        
        if metric_name not in valid_metrics:
            return ResponseHandler.handle_validation_error(
                f'Métrica inválida. Métricas válidas: {", ".join(valid_metrics)}'
            )
        
        # Atualizar threshold
        old_threshold = performance_monitor.thresholds.get(metric_name)
        performance_monitor.set_threshold(metric_name, threshold)
        
        LoggingHelper.log_user_action(
            current_user.email, 
            'THRESHOLD_UPDATED', 
            {
                'metric': metric_name,
                'old_threshold': old_threshold,
                'new_threshold': threshold
            }
        )
        
        return ResponseHandler.handle_success({
            'metric_name': metric_name,
            'old_threshold': old_threshold,
            'new_threshold': threshold,
            'message': f'Threshold para {metric_name} atualizado com sucesso'
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.update_threshold')
        return ResponseHandler.handle_server_error('Erro ao atualizar threshold')


@performance_monitoring_bp.route('/monitoring/enable', methods=['POST'])
@login_required
def enable_monitoring():
    """Ativar monitorização"""
    try:
        LoggingHelper.log_request('performance.enable_monitoring', 'POST', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        performance_monitor.enable_monitoring()
        
        LoggingHelper.log_user_action(current_user.email, 'MONITORING_ENABLED')
        
        return ResponseHandler.handle_success({
            'enabled': True,
            'message': 'Monitorização ativada com sucesso'
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.enable_monitoring')
        return ResponseHandler.handle_server_error('Erro ao ativar monitorização')


@performance_monitoring_bp.route('/monitoring/disable', methods=['POST'])
@login_required
def disable_monitoring():
    """Desativar monitorização"""
    try:
        LoggingHelper.log_request('performance.disable_monitoring', 'POST', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        performance_monitor.disable_monitoring()
        
        LoggingHelper.log_user_action(current_user.email, 'MONITORING_DISABLED')
        
        return ResponseHandler.handle_success({
            'enabled': False,
            'message': 'Monitorização desativada com sucesso'
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.disable_monitoring')
        return ResponseHandler.handle_server_error('Erro ao desativar monitorização')


@performance_monitoring_bp.route('/system/health')
@login_required
def system_health():
    """Status de saúde do sistema"""
    try:
        LoggingHelper.log_request('performance.system_health', 'GET', current_user.email)
        
        # Este endpoint pode ser acessado por qualquer usuário autenticado
        summary = performance_monitor.get_performance_summary()
        active_alerts = performance_monitor.get_active_alerts()
        
        # Calcular status geral
        critical_alerts = [alert for alert in active_alerts if alert['level'] == 'CRITICAL']
        warning_alerts = [alert for alert in active_alerts if alert['level'] == 'WARNING']
        
        if critical_alerts:
            health_status = 'CRITICAL'
        elif warning_alerts:
            health_status = 'WARNING'
        else:
            health_status = 'HEALTHY'
        
        return ResponseHandler.handle_success({
            'status': health_status,
            'timestamp': LoggingHelper.get_current_timestamp(),
            'summary': {
                'cpu_usage': summary['system'].get('cpu', {}).get('percent', 0),
                'memory_usage': summary['system'].get('memory', {}).get('percent', 0),
                'disk_usage': summary['system'].get('disk', {}).get('percent', 0),
                'avg_response_time': summary['requests'].get('avg_response_time', 0),
                'error_rate': summary['requests'].get('error_rate', 0),
                'cache_hit_rate': summary['cache'].get('hit_rate', 0)
            },
            'alerts': {
                'critical': len(critical_alerts),
                'warning': len(warning_alerts),
                'total_active': len(active_alerts)
            }
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.system_health')
        return ResponseHandler.handle_server_error('Erro ao obter status de saúde')


@performance_monitoring_bp.route('/metrics/live')
@login_required
def live_metrics():
    """Métricas em tempo real"""
    try:
        LoggingHelper.log_request('performance.live_metrics', 'GET', current_user.email)
        
        # Verificar permissões
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'developer']:
            return ResponseHandler.handle_authorization_error('Acesso negado')
        
        # Obter métricas mais recentes
        with performance_monitor._lock:
            recent_metrics = list(performance_monitor.metrics)[-20:]  # Últimas 20 métricas
        
        metrics_by_name = {}
        for metric in recent_metrics:
            metric_dict = metric.to_dict()
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric_dict)
        
        return ResponseHandler.handle_success({
            'timestamp': LoggingHelper.get_current_timestamp(),
            'metrics': metrics_by_name,
            'total_metrics': len(recent_metrics)
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'performance.live_metrics')
        return ResponseHandler.handle_server_error('Erro ao obter métricas em tempo real')


# Registrar blueprint
def register_performance_monitoring_routes(app):
    """Registrar rotas de monitorização de performance"""
    app.register_blueprint(performance_monitoring_bp)
