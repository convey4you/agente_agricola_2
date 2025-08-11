"""
Alert Controller - Gestão de Alertas Inteligentes Sprint 2
Sistema de alertas proativos para agricultores portugueses
"""
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from app.services.alert_engine import AlertEngine
from app.models.alerts import Alert, AlertRule, AlertType, AlertPriority, AlertStatus, UserAlertPreference
from app.models.user import User
from app import db
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Blueprint
alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@alerts_bp.route('/')
@login_required
def get_user_alerts():
    """Obter alertas do usuário logado"""
    try:
        # Parâmetros da query
        limit = min(int(request.args.get('limit', 50)), 100)
        include_read = request.args.get('include_read', 'true').lower() == 'true'
        
        # Obter alertas
        alert_engine = AlertEngine()
        alerts = alert_engine.get_user_alerts(
            user_id=current_user.id,
            limit=limit,
            include_read=include_read
        )
        
        # Estatísticas
        total_alerts = Alert.query.filter_by(user_id=current_user.id).count()
        # Corrigir: usar status correto para alertas não lidos
        unread_count = Alert.query.filter_by(user_id=current_user.id).filter(
            Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT])
        ).count()
        
        # Verificar se deve retornar JSON ou HTML
        # Priorizar HTML a menos que seja explicitamente uma requisição de API
        accept_header = request.headers.get('Accept', '')
        content_type = request.headers.get('Content-Type', '')
        format_param = request.args.get('format', '')
        
        # Debug
        logger.info(f"Request headers - Accept: {accept_header}, Content-Type: {content_type}, format: {format_param}")
        
        wants_json = (
            content_type == 'application/json' or
            ('application/json' in accept_header and 'text/html' not in accept_header) or
            format_param == 'json'
        )
        
        logger.info(f"wants_json: {wants_json}")
        
        if wants_json:
            logger.info("Retornando JSON")
            return jsonify({
                'status': 'success',
                'alerts': [alert.to_dict() for alert in alerts],
                'statistics': {
                    'total': total_alerts,
                    'unread': unread_count,
                    'returned': len(alerts)
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        # Renderizar template HTML
        logger.info("Tentando renderizar template HTML")
        try:
            # Preparar estatísticas para o template
            stats = {
                'critical': Alert.query.filter_by(user_id=current_user.id).filter(
                    Alert.priority == AlertPriority.CRITICAL
                ).count(),
                'high': Alert.query.filter_by(user_id=current_user.id).filter(
                    Alert.priority == AlertPriority.HIGH
                ).count(),
                'medium': Alert.query.filter_by(user_id=current_user.id).filter(
                    Alert.priority == AlertPriority.MEDIUM
                ).count(),
                'low': Alert.query.filter_by(user_id=current_user.id).filter(
                    Alert.priority == AlertPriority.LOW
                ).count(),
                'total': total_alerts,
                'unread': unread_count
            }
            
            logger.info("Renderizando template alerts/index.html")
            return render_template('alerts/index.html',
                                 alerts=alerts,
                                 stats=stats,
                                 total_alerts=total_alerts,
                                 unread_count=unread_count)
        except Exception as e:
            logger.error(f"Erro ao renderizar template: {e}")
            # Fallback para JSON se template não existir
            return jsonify({
                'status': 'success',
                'alerts': [alert.to_dict() for alert in alerts],
                'statistics': {
                    'total': total_alerts,
                    'unread': unread_count,
                    'returned': len(alerts)
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas do usuário {current_user.id}: {e}")
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Erro interno do servidor',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
        return jsonify({'status': 'error', 'message': str(e)}), 500

@alerts_bp.route('/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """Marcar alerta como lido"""
    try:
        alert_engine = AlertEngine()
        success = alert_engine.mark_alert_as_read(alert_id, current_user.id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Alerta marcado como lido',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Alerta não encontrado',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao marcar alerta {alert_id} como lido: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_bp.route('/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def dismiss_alert(alert_id):
    """Dispensar alerta"""
    try:
        alert_engine = AlertEngine()
        success = alert_engine.dismiss_alert(alert_id, current_user.id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Alerta dispensado',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Alerta não encontrado',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao dispensar alerta {alert_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_bp.route('/create', methods=['POST'])
@login_required
def create_manual_alert():
    """Criar alerta manual (para testes ou uso administrativo)"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['title', 'message', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Campo obrigatório: {field}',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
        
        # Validar enums
        try:
            alert_type = AlertType(data['type'])
            priority = AlertPriority(data.get('priority', 'medium'))
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'Valor inválido: {e}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Criar alerta
        alert_engine = AlertEngine()
        alert = alert_engine.create_manual_alert(
            user_id=current_user.id,
            alert_type=alert_type,
            title=data['title'],
            message=data['message'],
            priority=priority,
            action_text=data.get('action_text'),
            action_url=data.get('action_url'),
            culture_id=data.get('culture_id'),
            expires_hours=data.get('expires_hours', 72)
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta criado com sucesso',
            'alert': alert.to_dict(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar alerta manual: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_bp.route('/preferences')
@login_required
def get_alert_preferences():
    """Obter preferências de alertas do usuário"""
    try:
        preferences = UserAlertPreference.query.filter_by(
            user_id=current_user.id
        ).all()
        
        # Criar preferências padrão se não existirem
        if not preferences:
            for alert_type in AlertType:
                pref = UserAlertPreference(
                    user_id=current_user.id,
                    alert_type=alert_type
                )
                db.session.add(pref)
            
            db.session.commit()
            preferences = UserAlertPreference.query.filter_by(
                user_id=current_user.id
            ).all()
        
        prefs_dict = {}
        for pref in preferences:
            prefs_dict[pref.alert_type.value] = {
                'is_enabled': pref.is_enabled,
                'web_enabled': pref.web_enabled,
                'email_enabled': pref.email_enabled,
                'sms_enabled': pref.sms_enabled,
                'min_priority': pref.min_priority.value,
                'quiet_hours_start': pref.quiet_hours_start.strftime('%H:%M') if pref.quiet_hours_start else None,
                'quiet_hours_end': pref.quiet_hours_end.strftime('%H:%M') if pref.quiet_hours_end else None
            }
        
        return jsonify({
            'status': 'success',
            'preferences': prefs_dict,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter preferências de alertas: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_bp.route('/preferences', methods=['POST'])
@login_required
def update_alert_preferences():
    """Atualizar preferências de alertas"""
    try:
        data = request.get_json()
        
        for alert_type_str, settings in data.items():
            try:
                alert_type = AlertType(alert_type_str)
            except ValueError:
                continue
            
            # Buscar ou criar preferência
            pref = UserAlertPreference.query.filter_by(
                user_id=current_user.id,
                alert_type=alert_type
            ).first()
            
            if not pref:
                pref = UserAlertPreference(
                    user_id=current_user.id,
                    alert_type=alert_type
                )
                db.session.add(pref)
            
            # Atualizar configurações
            if 'is_enabled' in settings:
                pref.is_enabled = settings['is_enabled']
            if 'web_enabled' in settings:
                pref.web_enabled = settings['web_enabled']
            if 'email_enabled' in settings:
                pref.email_enabled = settings['email_enabled']
            if 'sms_enabled' in settings:
                pref.sms_enabled = settings['sms_enabled']
            if 'min_priority' in settings:
                try:
                    pref.min_priority = AlertPriority(settings['min_priority'])
                except ValueError:
                    pass
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Preferências atualizadas com sucesso',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preferências de alertas: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_bp.route('/stats')
@login_required
def get_alert_statistics():
    """Obter estatísticas de alertas do usuário"""
    try:
        # Estatísticas gerais
        total = Alert.query.filter_by(user_id=current_user.id).count()
        unread = Alert.query.filter_by(user_id=current_user.id, status='sent').count()
        
        # Últimos 30 dias
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent = Alert.query.filter(
            Alert.user_id == current_user.id,
            Alert.created_at >= thirty_days_ago
        ).count()
        
        # Por tipo
        by_type = {}
        for alert_type in AlertType:
            count = Alert.query.filter_by(
                user_id=current_user.id,
                type=alert_type
            ).count()
            by_type[alert_type.value] = count
        
        # Por prioridade
        by_priority = {}
        for priority in AlertPriority:
            count = Alert.query.filter_by(
                user_id=current_user.id,
                priority=priority
            ).count()
            by_priority[priority.value] = count
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total': total,
                'unread': unread,
                'last_30_days': recent,
                'by_type': by_type,
                'by_priority': by_priority
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de alertas: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_bp.route('/process', methods=['POST'])
@login_required
def trigger_alert_processing():
    """Disparar processamento manual de alertas (para testes)"""
    try:
        # Apenas administradores ou em modo de desenvolvimento
        if not (hasattr(current_user, 'is_admin') and current_user.is_admin) and not current_app.debug:
            return jsonify({
                'status': 'error',
                'message': 'Acesso negado',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 403
        
        alert_engine = AlertEngine()
        alert_engine.process_all_alerts()
        
        return jsonify({
            'status': 'success',
            'message': 'Processamento de alertas executado',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar alertas manualmente: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
