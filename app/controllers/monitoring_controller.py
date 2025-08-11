"""
Monitoring Controller - Rotas para monitoramento do sistema com PROMPT 3
"""
import logging
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.monitoring_service import MonitoringService
from app.services.database_manager import DatabaseManager
from app.validators.monitoring_validators import MonitoringValidator
from app.utils.response_helpers import ResponseHandler
from app.utils.logging_helpers import LoggingHelper

# PROMPT 3: Importações dos novos utilitários de monitoramento
from app.utils.metrics import metrics, system_metrics
from app.utils.health_checks import health_manager
from app.utils.monitoring_alerts_fixed import alert_manager
from app.utils.logging_config import audit_logger
from datetime import datetime, timedelta
import json

monitoring_bp = Blueprint('monitoring', __name__)
monitoring_service = MonitoringService()


@monitoring_bp.route('/')
@login_required
def index():
    """Página principal do monitoramento - redireciona para dashboard"""
    try:
        logging.info("Acessando página principal de monitoramento")
        return render_template('monitoring/dashboard.html')
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao carregar página de monitoramento: {str(e)}")
        return ResponseHandler.handle_error("Erro ao carregar monitoramento", 500)


@monitoring_bp.route('/dashboard-status')
@login_required
def dashboard_status():
    """Dashboard de status do sistema para administradores"""
    try:
        # Verificar se é admin
        if not is_admin_user():
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('dashboard.index'))
        
        logging.info("Carregando dashboard de status para admin")
        
        # Carregar dados do banco para o template
        try:
            db_info = DatabaseManager.get_database_info()
            db_validation = DatabaseManager.validate_database()
        except Exception as e:
            logging.error(f"Erro ao carregar dados do banco: {str(e)}")
            db_info = {'success': False, 'error': str(e)}
            db_validation = {'success': False, 'error': str(e)}
        
        return render_template('monitoring/dashboard.html', 
                               db_info=db_info, 
                               db_validation=db_validation)
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao carregar dashboard de status: {str(e)}")
        return ResponseHandler.handle_error("Erro ao carregar dashboard", 500)


@monitoring_bp.route('/api/database/info')
@login_required
def database_info():
    """API: Obter informações do banco de dados"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            logging.warning(f"Acesso negado para database_info - user: {getattr(current_user, 'email', 'NO_EMAIL')}")
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
        db_info = DatabaseManager.get_database_info()
        return jsonify({'success': True, 'data': db_info})
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao obter informações do banco: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao obter informações do banco'}), 500


@monitoring_bp.route('/api/database/validate')
@login_required
def database_validate():
    """API: Validar integridade do banco de dados"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
        db_info = DatabaseManager.get_database_info()
        db_validation = DatabaseManager.validate_database()
        
        result = {
            'database_info': db_info,
            'validation': db_validation
        }
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao validar banco: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao validar banco'}), 500


@monitoring_bp.route('/api/database/backup', methods=['POST'])
@login_required
def database_backup():
    """API: Criar backup do banco de dados"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
        data = request.get_json() or {}
        backup_name = data.get('backup_name', f'manual_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        backup_result = DatabaseManager.create_backup(backup_name)
        return jsonify({'success': True, 'data': backup_result})
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao criar backup: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao criar backup'}), 500


@monitoring_bp.route('/database/reset-form', methods=['GET', 'POST'])
@login_required
def database_reset_form():
    """Formulário para reset do banco de dados"""
    try:
        # Log detalhado para debug
        logging.info(f"Reset form - Método: {request.method}")
        logging.info(f"Reset form - Usuário autenticado: {current_user.is_authenticated}")
        logging.info(f"Reset form - Email: {getattr(current_user, 'email', 'N/A')}")
        
        # Verificar permissões (apenas admins)
        admin_check = is_admin_user()
        logging.info(f"Reset form - Admin check result: {admin_check}")
        
        if not admin_check:
            logging.warning(f"Reset form - Acesso negado para usuário: {getattr(current_user, 'email', 'N/A')}")
            if request.method == 'POST':
                return jsonify({'success': False, 'error': 'Acesso negado - apenas administradores'}), 403
            flash('Acesso negado. Apenas administradores podem resetar o banco.', 'error')
            return redirect(url_for('monitoring.dashboard_status'))
        
        if request.method == 'POST':
            # Se for POST, retornar JSON indicando que o formulário está disponível
            return jsonify({
                'success': True,
                'message': 'Formulário de reset disponível',
                'redirect_url': url_for('monitoring.database_reset_form')
            })
        
        return render_template('monitoring/database_reset_form.html')
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao carregar formulário de reset: {str(e)}")
        if request.method == 'POST':
            return jsonify({'success': False, 'error': 'Erro interno'}), 500
        return ResponseHandler.handle_error("Erro ao carregar formulário", 500)


@monitoring_bp.route('/database/reset', methods=['POST'])
@login_required
def database_reset():
    """Reset completo do banco de dados"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            flash('Acesso negado. Apenas administradores podem resetar o banco.', 'error')
            return redirect(url_for('monitoring.dashboard_status'))
        
        # Obter parâmetros
        data = request.form
        confirmation = data.get('confirmation', '').strip().lower()
        create_backup = data.get('create_backup') == 'on'
        
        # Validar confirmação
        if confirmation != 'reset database':
            flash('Confirmação incorreta. Digite exatamente "reset database".', 'error')
            return redirect(url_for('monitoring.database_reset_form'))
        
        # Executar reset
        reset_result = DatabaseManager.reset_database(create_backup_before=create_backup)
        
        if reset_result['success']:
            flash('Banco de dados resetado com sucesso!', 'success')
            LoggingHelper.log_info(f"Database reset realizado por admin: {current_user.email}")
        else:
            flash(f'Erro ao resetar banco: {reset_result.get("error", "Erro desconhecido")}', 'error')
        
        return redirect(url_for('monitoring.dashboard_status'))
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro durante reset do banco: {str(e)}")
        flash('Erro interno durante reset do banco', 'error')
        return redirect(url_for('monitoring.dashboard_status'))


@monitoring_bp.route('/api/database/reset', methods=['GET', 'POST'])
@login_required
def api_database_reset():
    """API: Reset completo do banco de dados"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
        if request.method == 'GET':
            # GET: Retorna informações sobre o reset (sem executar)
            return jsonify({
                'success': True,
                'message': 'Reset endpoint ativo',
                'method': 'POST',
                'required_params': {
                    'confirmation': 'reset database',
                    'create_backup': True
                },
                'warning': 'Esta operação irá eliminar todas as tabelas e recriar do zero'
            })
        
        # POST: Executa o reset
        data = request.get_json() or {}
        confirmation = data.get('confirmation', '').strip().lower()
        create_backup = data.get('create_backup', True)
        
        # Validar confirmação
        if confirmation != 'reset database':
            return jsonify({'success': False, 'error': 'Confirmação incorreta'}), 400
        
        # Executar reset
        reset_result = DatabaseManager.reset_database(create_backup_before=create_backup)
        return jsonify({'success': True, 'data': reset_result})
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro durante reset do banco: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro durante reset'}), 500


@monitoring_bp.route('/database/sync-schema-form', methods=['GET', 'POST'])
@login_required
def database_sync_schema_form():
    """Formulário para sincronização do schema"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            if request.method == 'POST':
                return jsonify({'success': False, 'error': 'Acesso negado'}), 403
            flash('Acesso negado. Apenas administradores podem sincronizar o schema.', 'error')
            return redirect(url_for('monitoring.dashboard_status'))
        
        if request.method == 'POST':
            # Se for POST, retornar JSON indicando que o formulário está disponível
            return jsonify({
                'success': True,
                'message': 'Formulário de sincronização disponível',
                'redirect_url': url_for('monitoring.database_sync_schema_form')
            })
        
        return render_template('monitoring/database_sync_form.html')
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro ao carregar formulário de sync: {str(e)}")
        if request.method == 'POST':
            return jsonify({'success': False, 'error': 'Erro interno'}), 500
        return ResponseHandler.handle_error("Erro ao carregar formulário", 500)


@monitoring_bp.route('/database/sync-schema', methods=['POST'])
@login_required
def database_sync_schema():
    """Sincronização segura do schema do banco"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            flash('Acesso negado. Apenas administradores podem sincronizar o schema.', 'error')
            return redirect(url_for('monitoring.dashboard_status'))
        
        # Executar sincronização
        result = DatabaseManager.sync_schema()
        
        if result['success']:
            flash('Schema sincronizado com sucesso!', 'success')
            LoggingHelper.log_info(f"Schema sync realizado por admin: {current_user.email}")
        else:
            flash(f'Erro ao sincronizar schema: {result.get("error", "Erro desconhecido")}', 'error')
        
        return redirect(url_for('monitoring.dashboard_status'))
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro durante sync do schema: {str(e)}")
        flash('Erro interno durante sincronização do schema', 'error')
        return redirect(url_for('monitoring.dashboard_status'))


@monitoring_bp.route('/api/database/sync-schema', methods=['GET', 'POST'])
@login_required
def api_database_sync_schema():
    """API: Sincronização segura do schema do banco"""
    try:
        # Verificar permissões (apenas admins)
        if not is_admin_user():
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
        if request.method == 'GET':
            # GET: Retorna informações sobre a sincronização (sem executar)
            return jsonify({
                'success': True,
                'message': 'Sync schema endpoint ativo',
                'method': 'POST',
                'description': 'Cria tabelas ou campos ausentes sem destruir dados existentes',
                'warning': 'Esta operação apenas adiciona elementos faltantes ao schema'
            })
        
        # POST: Executa a sincronização
        result = DatabaseManager.sync_schema()
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        LoggingHelper.log_error(f"Erro durante sync do schema: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro durante sincronização'}), 500


# Rotas de debug removidas por segurança - use logs do sistema para diagnóstico
    """Debug: Informações gerais do sistema"""
    try:
        debug_data = {
            'user_info': {
                'is_authenticated': current_user.is_authenticated,
                'email': getattr(current_user, 'email', None),
                'is_admin_check': is_admin_user()
            },
            'system_info': {
                'flask_app': True,
                'database_available': True,
                'monitoring_active': True
            },
            'endpoints': {
                'database_info': '/monitoring/api/database/info',
                'database_validate': '/monitoring/api/database/validate',
                'database_reset': '/monitoring/api/database/reset',
                'database_sync': '/monitoring/api/database/sync-schema'
            }
        }
        
        return jsonify({'success': True, 'data': debug_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Rota de debug removida por segurança


def is_admin_user():
    """Verificar se o usuário atual é admin"""
    try:
        if not current_user.is_authenticated:
            logging.warning("Usuário não autenticado")
            return False
        
        email = getattr(current_user, 'email', '')
        is_admin = email == 'admin@agrotech.pt'
        
        logging.info(f"Verificação admin - Email: {email}, Is Admin: {is_admin}")
        return is_admin
        
    except Exception as e:
        logging.error(f"Erro na verificação de admin: {str(e)}")
        return False


@monitoring_bp.route('/system-status')
@login_required
def system_status():
    """Status do sistema em tempo real - Requer autenticação"""
    try:
        # Obter status do sistema
        result = monitoring_service.get_system_status()
        
        if result['success']:
            logging.info("Status do sistema obtido com sucesso")
            return ResponseHandler.handle_success(
                data=result['data'],
                message="Status do sistema obtido com sucesso"
            )
        else:
            LoggingHelper.log_error(f"Erro ao obter status do sistema: {result['error']}")
            return ResponseHandler.handle_error(result['error'], 500)
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em system_status: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@monitoring_bp.route('/public-status')
def public_system_status():
    """Status público do sistema para dashboard"""
    try:
        # Obter status do sistema
        result = monitoring_service.get_system_status()
        
        if result['success']:
            logging.info("Status público do sistema obtido com sucesso")
            return jsonify(result['data'])
        else:
            LoggingHelper.log_error(f"Erro ao obter status do sistema: {result['error']}")
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em public_system_status: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@monitoring_bp.route('/health-check')
def health_check():
    """Health check simples para monitoramento externo"""
    try:
        # Obter parâmetros opcionais
        component = request.args.get('component')
        detailed = request.args.get('detailed', default='false').lower() == 'true'
        
        # Validar parâmetros
        is_valid, error_msg = MonitoringValidator.validate_component_name(component)
        if not is_valid:
            LoggingHelper.log_warning(f"Componente inválido em health_check: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        # Realizar health check
        result = monitoring_service.get_health_check(
            component=component,
            detailed=detailed
        )
        
        if result['success']:
            logging.info("Health check realizado com sucesso")
            status_code = 200 if result['data']['status'] == 'healthy' else 503
            return ResponseHandler.handle_success(
                data=result['data'],
                message="Health check realizado com sucesso"
            ), status_code
        else:
            LoggingHelper.log_error(f"Erro no health check: {result['error']}")
            return ResponseHandler.handle_error(result['error'], 503)
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em health_check: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 503)


@monitoring_bp.route('/performance-metrics')
@login_required
def performance_metrics():
    """Métricas de performance do sistema"""
    try:
        # Obter parâmetros
        period = request.args.get('period', '1h')
        metric_type = request.args.get('metric_type')
        aggregation = request.args.get('aggregation', 'avg')
        
        # Validar parâmetros
        is_valid, error_msg = MonitoringValidator.validate_time_period(period)
        if not is_valid:
            LoggingHelper.log_warning(f"Período inválido em performance_metrics: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        is_valid, error_msg = MonitoringValidator.validate_metric_type(metric_type)
        if not is_valid:
            LoggingHelper.log_warning(f"Tipo de métrica inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        is_valid, error_msg = MonitoringValidator.validate_aggregation_method(aggregation)
        if not is_valid:
            LoggingHelper.log_warning(f"Método de agregação inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        # Obter métricas
        result = monitoring_service.get_performance_metrics(
            period=period,
            metric_type=metric_type,
            aggregation=aggregation
        )
        
        if result['success']:
            logging.info(f"Métricas de performance obtidas: período={period}, tipo={metric_type}")
            return ResponseHandler.handle_success(
                data=result['data'],
                message="Métricas de performance obtidas com sucesso"
            )
        else:
            LoggingHelper.log_error(f"Erro ao obter métricas: {result['error']}")
            return ResponseHandler.handle_error(result['error'], 500)
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em performance_metrics: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@monitoring_bp.route('/user-activity-stats')
@login_required
def user_activity_stats():
    """Estatísticas de atividade dos usuários"""
    try:
        # Obter parâmetros
        period = request.args.get('period', '24h')
        limit = request.args.get('limit', 50, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validar parâmetros
        is_valid, error_msg = MonitoringValidator.validate_time_period(period)
        if not is_valid:
            LoggingHelper.log_warning(f"Período inválido em user_activity_stats: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        is_valid, error_msg = MonitoringValidator.validate_limit_parameter(limit)
        if not is_valid:
            LoggingHelper.log_warning(f"Limite inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        is_valid, error_msg = MonitoringValidator.validate_date_range(start_date, end_date)
        if not is_valid:
            LoggingHelper.log_warning(f"Intervalo de datas inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        # Obter estatísticas
        result = monitoring_service.get_user_activity_stats(
            period=period,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            logging.info(f"Estatísticas de atividade obtidas: período={period}")
            return ResponseHandler.handle_success(
                data=result['data'],
                message="Estatísticas de atividade obtidas com sucesso"
            )
        else:
            LoggingHelper.log_error(f"Erro ao obter estatísticas: {result['error']}")
            return ResponseHandler.handle_error(result['error'], 500)
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em user_activity_stats: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@monitoring_bp.route('/error-logs')
@login_required
def error_logs():
    """Logs de erro do sistema"""
    try:
        # Obter parâmetros
        severity = request.args.get('severity')
        limit = request.args.get('limit', 100, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validar parâmetros
        is_valid, error_msg = MonitoringValidator.validate_severity_level(severity)
        if not is_valid:
            LoggingHelper.log_warning(f"Severidade inválida em error_logs: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        is_valid, error_msg = MonitoringValidator.validate_limit_parameter(limit)
        if not is_valid:
            LoggingHelper.log_warning(f"Limite inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        is_valid, error_msg = MonitoringValidator.validate_date_range(start_date, end_date)
        if not is_valid:
            LoggingHelper.log_warning(f"Intervalo de datas inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        # Obter logs
        result = monitoring_service.get_error_logs(
            severity=severity,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            logging.info(f"Logs de erro obtidos: severidade={severity}, limite={limit}")
            return ResponseHandler.handle_success(
                data=result['data'],
                message="Logs de erro obtidos com sucesso"
            )
        else:
            LoggingHelper.log_error(f"Erro ao obter logs: {result['error']}")
            return ResponseHandler.handle_error(result['error'], 500)
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em error_logs: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


@monitoring_bp.route('/dashboard-data')
@login_required
def dashboard_data():
    """Dados completos para dashboard de monitoramento"""
    try:
        # Obter parâmetros
        refresh_interval = request.args.get('refresh_interval', 30, type=int)
        include_charts = request.args.get('include_charts', default='true').lower() == 'true'
        
        # Validar parâmetros
        is_valid, error_msg = MonitoringValidator.validate_refresh_interval(refresh_interval)
        if not is_valid:
            LoggingHelper.log_warning(f"Intervalo de refresh inválido: {error_msg}")
            return ResponseHandler.handle_error(error_msg, 400)
        
        # Obter dados do dashboard
        result = monitoring_service.get_dashboard_data(
            refresh_interval=refresh_interval,
            include_charts=include_charts
        )
        
        if result['success']:
            logging.info("Dados do dashboard de monitoramento obtidos com sucesso")
            return ResponseHandler.handle_success(
                data=result['data'],
                message="Dados do dashboard obtidos com sucesso"
            )
        else:
            LoggingHelper.log_error(f"Erro ao obter dados do dashboard: {result['error']}")
            return ResponseHandler.handle_error(result['error'], 500)
    
    except Exception as e:
        LoggingHelper.log_error(f"Erro inesperado em dashboard_data: {str(e)}")
        return ResponseHandler.handle_error("Erro interno do servidor", 500)


# PROMPT 3: Novas rotas para monitoramento avançado

@monitoring_bp.route('/prompt3-dashboard')
def prompt3_dashboard():
    """Dashboard PROMPT 3 - Monitoramento de Qualidade e Métricas"""
    try:
        # Obter dados básicos do sistema
        metrics_summary = metrics.get_metrics_summary()
        health_results = health_manager.get_last_results() or health_manager.run_all_checks()
        alert_summary = alert_manager.get_alert_summary()
        
        # Log de auditoria
        audit_logger.log_user_action(
            user_id=request.args.get('user_id', 'anonymous'),
            action='view_monitoring_dashboard',
            resource_type='monitoring'
        )
        
        return render_template('monitoring/prompt3_dashboard.html',
                             metrics=metrics_summary,
                             health=health_results,
                             alerts=alert_summary)
    
    except Exception as e:
        logging.error(f"Erro no dashboard PROMPT 3: {str(e)}")
        return ResponseHandler.handle_error("Erro ao carregar dashboard", 500)


@monitoring_bp.route('/api/prompt3/metrics')
def api_prompt3_metrics():
    """API para métricas PROMPT 3 em tempo real"""
    try:
        summary = metrics.get_metrics_summary()
        system_stats = system_metrics.get_current_stats() if system_metrics else {}
        
        return jsonify({
            'application_metrics': summary,
            'system_metrics': system_stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Erro ao obter métricas PROMPT 3: {str(e)}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/prompt3/health')
def api_prompt3_health():
    """API para health checks PROMPT 3"""
    try:
        # Verificar se deve executar novos checks
        force_check = request.args.get('force', 'false').lower() == 'true'
        
        if force_check or not health_manager.last_results:
            results = health_manager.run_all_checks()
        else:
            results = health_manager.last_results
        
        # Adicionar timestamp
        results['timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify(results)
    except Exception as e:
        logging.error(f"Erro em health checks PROMPT 3: {str(e)}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/prompt3/health/<check_name>')
def api_prompt3_health_specific(check_name):
    """API para health check específico PROMPT 3"""
    try:
        result = health_manager.run_check(check_name)
        result['timestamp'] = datetime.utcnow().isoformat()
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(f"Erro em health check {check_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/prompt3/alerts')
def api_prompt3_alerts():
    """API para alertas PROMPT 3"""
    try:
        alert_type = request.args.get('type', 'active')
        
        if alert_type == 'active':
            alerts = alert_manager.get_active_alerts()
            return jsonify({
                'alerts': [alert.to_dict() for alert in alerts],
                'total': len(alerts),
                'timestamp': datetime.utcnow().isoformat()
            })
        elif alert_type == 'history':
            limit = int(request.args.get('limit', 50))
            alerts = alert_manager.get_alert_history(limit)
            return jsonify({
                'alerts': [alert.to_dict() for alert in alerts],
                'total': len(alerts),
                'timestamp': datetime.utcnow().isoformat()
            })
        elif alert_type == 'summary':
            summary = alert_manager.get_alert_summary()
            summary['timestamp'] = datetime.utcnow().isoformat()
            return jsonify(summary)
        else:
            return jsonify({'error': 'Invalid alert type'}), 400
    
    except Exception as e:
        logging.error(f"Erro ao obter alertas PROMPT 3: {str(e)}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/prompt3/alerts/<alert_id>/resolve', methods=['POST'])
@login_required
def api_prompt3_resolve_alert(alert_id):
    """API para resolver alerta PROMPT 3"""
    try:
        success = alert_manager.resolve_alert(alert_id)
        
        if success:
            audit_logger.log_user_action(
                user_id=request.args.get('user_id', 'system'),
                action='resolve_alert',
                resource_type='alert',
                resource_id=alert_id
            )
            return jsonify({'success': True, 'timestamp': datetime.utcnow().isoformat()})
        else:
            return jsonify({'error': 'Alert not found'}), 404
    
    except Exception as e:
        logging.error(f"Erro ao resolver alerta {alert_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/prompt3/system-info')
def api_prompt3_system_info():
    """API para informações do sistema PROMPT 3"""
    try:
        import psutil
        import platform
        
        system_info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            },
            'python': {
                'version': platform.python_version(),
                'implementation': platform.python_implementation()
            },
            'resources': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
                'disk_total_gb': round(psutil.disk_usage('/').total / 1024 / 1024 / 1024, 2)
            },
            'application': {
                'uptime_seconds': metrics.get_metrics_summary().get('uptime_seconds', 0),
                'start_time': (datetime.utcnow() - timedelta(seconds=metrics.get_metrics_summary().get('uptime_seconds', 0))).isoformat()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(system_info)
    
    except Exception as e:
        logging.error(f"Erro ao obter informações do sistema: {str(e)}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/prompt3/logs')
@login_required
def prompt3_logs_viewer():
    """Visualizador de logs PROMPT 3"""
    try:
        log_type = request.args.get('type', 'general')
        lines = int(request.args.get('lines', 100))
        
        log_files = {
            'general': 'logs/agrotech.log',
            'errors': 'logs/agrotech_errors.log',
            'audit': 'logs/agrotech_audit.log'
        }
        
        log_file = log_files.get(log_type)
        if not log_file:
            return ResponseHandler.handle_error('Invalid log type', 400)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()[-lines:]
                
            # Processar logs JSON
            parsed_logs = []
            for line in log_lines:
                try:
                    log_entry = json.loads(line.strip())
                    parsed_logs.append(log_entry)
                except json.JSONDecodeError:
                    # Log não é JSON, adicionar como texto simples
                    parsed_logs.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'level': 'INFO',
                        'message': line.strip()
                    })
            
            return render_template('monitoring/prompt3_logs.html',
                                 logs=parsed_logs,
                                 log_type=log_type,
                                 total_lines=len(parsed_logs))
        
        except FileNotFoundError:
            return render_template('monitoring/prompt3_logs.html',
                                 logs=[],
                                 log_type=log_type,
                                 error=f'Log file not found: {log_file}')
    
    except Exception as e:
        logging.error(f"Erro no visualizador de logs: {str(e)}")
        return ResponseHandler.handle_error("Erro ao carregar logs", 500)


@monitoring_bp.route('/api/prompt3/logs/<log_type>')
@login_required
def api_prompt3_logs(log_type):
    """API para obter logs PROMPT 3"""
    try:
        lines = int(request.args.get('lines', 100))
        level = request.args.get('level', None)
        
        log_files = {
            'general': 'logs/agrotech.log',
            'errors': 'logs/agrotech_errors.log',
            'audit': 'logs/agrotech_audit.log'
        }
        
        log_file = log_files.get(log_type)
        if not log_file:
            return jsonify({'error': 'Invalid log type'}), 400
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()[-lines:]
            
            parsed_logs = []
            for line in log_lines:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Filtrar por nível se especificado
                    if level and log_entry.get('level', '').upper() != level.upper():
                        continue
                        
                    parsed_logs.append(log_entry)
                except json.JSONDecodeError:
                    if not level:  # Incluir logs não-JSON apenas se não há filtro de nível
                        parsed_logs.append({
                            'timestamp': datetime.utcnow().isoformat(),
                            'level': 'INFO',
                            'message': line.strip()
                        })
            
            return jsonify({
                'logs': parsed_logs,
                'total': len(parsed_logs),
                'log_type': log_type,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        except FileNotFoundError:
            return jsonify({
                'logs': [],
                'total': 0,
                'error': f'Log file not found: {log_file}',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    except Exception as e:
        logging.error(f"Erro ao obter logs via API: {str(e)}")
        return jsonify({'error': str(e)}), 500
