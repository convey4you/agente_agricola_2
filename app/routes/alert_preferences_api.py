"""
API para Preferências de Alertas Automáticos
Gerenciar configurações de geração automática de alertas
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.alerts import UserAlertPreference, AlertType, AlertPriority
from app.services.auto_alert_service import AutoAlertService
from app import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Blueprint para API de Preferências de Alertas
alert_preferences_api_bp = Blueprint('alert_preferences_api', __name__)
auto_alert_service = AutoAlertService()

@alert_preferences_api_bp.route('/', methods=['GET'])
@login_required
def get_user_preferences():
    """
    Obter preferências de alertas do usuário atual
    """
    try:
        preferences = UserAlertPreference.query.filter_by(user_id=current_user.id).all()
        
        preferences_data = []
        for pref in preferences:
            pref_dict = {
                'id': pref.id,
                'alert_type': pref.alert_type.value,
                'is_enabled': pref.is_enabled,
                'web_enabled': pref.web_enabled,
                'email_enabled': pref.email_enabled,
                'sms_enabled': pref.sms_enabled,
                'min_priority': pref.min_priority.value,
                'quiet_hours_start': pref.quiet_hours_start.strftime('%H:%M') if pref.quiet_hours_start else None,
                'quiet_hours_end': pref.quiet_hours_end.strftime('%H:%M') if pref.quiet_hours_end else None,
                'auto_generation_enabled': pref.auto_generation_enabled,
                'auto_frequency': pref.auto_frequency,
                'auto_time': pref.auto_time.strftime('%H:%M') if pref.auto_time else None,
                'auto_weekday': pref.auto_weekday,
                'auto_day_of_month': pref.auto_day_of_month,
                'last_auto_generation': pref.last_auto_generation.isoformat() if pref.last_auto_generation else None,
                'next_auto_generation': pref.get_next_auto_generation_time().isoformat() if pref.get_next_auto_generation_time() else None
            }
            preferences_data.append(pref_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'preferences': preferences_data,
                'available_types': [t.value for t in AlertType],
                'available_priorities': [p.value for p in AlertPriority],
                'frequency_options': ['daily', 'weekly', 'monthly']
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar preferências: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alert_preferences_api_bp.route('/<alert_type>', methods=['PUT'])
@login_required
def update_preference(alert_type):
    """
    Atualizar preferência específica de alerta
    """
    try:
        # Validar tipo de alerta
        try:
            alert_type_enum = AlertType(alert_type)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Tipo de alerta inválido: {alert_type}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Buscar ou criar preferência
        preference = UserAlertPreference.query.filter_by(
            user_id=current_user.id,
            alert_type=alert_type_enum
        ).first()
        
        if not preference:
            preference = UserAlertPreference(
                user_id=current_user.id,
                alert_type=alert_type_enum
            )
            db.session.add(preference)
        
        # Atualizar campos permitidos
        allowed_fields = [
            'is_enabled', 'web_enabled', 'email_enabled', 'sms_enabled',
            'auto_generation_enabled', 'auto_frequency', 'auto_time',
            'auto_weekday', 'auto_day_of_month', 'quiet_hours_start', 'quiet_hours_end'
        ]
        
        for field in allowed_fields:
            if field in data:
                value = data[field]
                
                # Conversões especiais
                if field in ['auto_time', 'quiet_hours_start', 'quiet_hours_end'] and value:
                    try:
                        value = datetime.strptime(value, '%H:%M').time()
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': f'Formato de hora inválido para {field}. Use HH:MM',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }), 400
                
                elif field == 'min_priority' and value:
                    try:
                        value = AlertPriority(value)
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': f'Prioridade inválida: {value}',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }), 400
                
                setattr(preference, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferências atualizadas com sucesso',
            'data': {
                'preference_id': preference.id,
                'next_auto_generation': preference.get_next_auto_generation_time().isoformat() if preference.get_next_auto_generation_time() else None
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar preferência: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alert_preferences_api_bp.route('/run-auto-generation', methods=['POST'])
@login_required
def run_auto_generation():
    """
    Executar geração automática de alertas manualmente (apenas para o usuário atual)
    """
    try:
        # Verificar se o usuário tem preferências de geração automática
        preferences = UserAlertPreference.query.filter_by(
            user_id=current_user.id,
            auto_generation_enabled=True,
            is_enabled=True
        ).all()
        
        if not preferences:
            return jsonify({
                'success': False,
                'message': 'Nenhuma preferência de geração automática ativa encontrada',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Executar geração automática apenas para este usuário
        from app.services.alert_service import AlertService
        alert_service = AlertService()
        
        new_alerts = alert_service.generate_all_alerts(current_user.id)
        
        # Marcar preferências como processadas
        for pref in preferences:
            pref.mark_auto_generation_completed()
        
        return jsonify({
            'success': True,
            'message': f'Geração automática executada com sucesso',
            'data': {
                'alerts_generated': len(new_alerts),
                'alert_types': list(set([alert.type.value for alert in new_alerts]))
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na geração automática manual: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alert_preferences_api_bp.route('/create-defaults', methods=['POST'])
@login_required
def create_default_preferences():
    """
    Criar preferências padrão para o usuário atual
    """
    try:
        success = auto_alert_service.create_default_preferences_for_user(current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Preferências padrão criadas com sucesso',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Preferências já existem ou erro ao criar',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
    except Exception as e:
        logger.error(f"Erro ao criar preferências padrão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

# Admin endpoints (apenas para desenvolvimento/debug)
@alert_preferences_api_bp.route('/admin/run-all-auto-generation', methods=['POST'])
@login_required  
def admin_run_auto_generation():
    """
    [ADMIN] Executar geração automática para todos os usuários
    """
    try:
        # TODO: Adicionar verificação de admin quando implementado
        result = auto_alert_service.run_auto_generation()
        
        return jsonify({
            'success': result['success'],
            'data': result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Erro na geração automática admin: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alert_preferences_api_bp.route('/admin/pending-users', methods=['GET'])
@login_required
def admin_get_pending_users():
    """
    [ADMIN] Obter usuários com geração automática pendente
    """
    try:
        pending_users = auto_alert_service.get_users_pending_auto_generation()
        
        return jsonify({
            'success': True,
            'data': {
                'pending_users': pending_users,
                'count': len(pending_users)
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuários pendentes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
