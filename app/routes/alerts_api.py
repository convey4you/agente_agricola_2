"""
API de Alertas - PROMPT CRÍTICO 2
Sistema de API REST completa para Sistema de Alertas Inteligentes
Endpoints padronizados com validações robustas e tratamento de erros
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.alerts import Alert, AlertType, AlertPriority, AlertStatus
from app.models.user import User
from app import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Blueprint para API de Alertas
alerts_api_bp = Blueprint('alerts_api', __name__)

def validate_alert_data(data):
    """Valida dados de entrada para criação de alerta"""
    errors = []
    
    # Campos obrigatórios
    required_fields = ['type', 'priority', 'title', 'message']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Campo '{field}' é obrigatório")
    
    # Validar valores permitidos
    valid_types = [t.value for t in AlertType]
    if data.get('type') and data.get('type') not in valid_types:
        errors.append(f"Tipo deve ser um de: {', '.join(valid_types)}")
    
    valid_priorities = [p.value for p in AlertPriority]
    if data.get('priority') and data.get('priority') not in valid_priorities:
        errors.append(f"Prioridade deve ser uma de: {', '.join(valid_priorities)}")
    
    # Validar tamanhos
    if data.get('title') and len(data.get('title', '')) > 200:
        errors.append("Título não pode ter mais de 200 caracteres")
    
    if data.get('message') and len(data.get('message', '')) > 5000:
        errors.append("Mensagem não pode ter mais de 5000 caracteres")
    
    # Validar datas (se fornecidas)
    for date_field in ['scheduled_for', 'expires_at']:
        if data.get(date_field):
            try:
                datetime.fromisoformat(data[date_field].replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Data '{date_field}' deve estar no formato ISO 8601")
    
    return errors

@alerts_api_bp.route('/', methods=['GET'])
@login_required
def list_alerts():
    """
    Lista alertas do usuário autenticado
    
    Query Parameters:
    - limit (int): Número máximo de alertas (padrão: 50, máximo: 100)
    - offset (int): Offset para paginação (padrão: 0)
    - status (str): Filtrar por status específico
    - type (str): Filtrar por tipo específico
    - priority (str): Filtrar por prioridade específica
    
    Returns:
    - 200: Lista de alertas
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        # Parâmetros de query
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        status_filter = request.args.get('status')
        type_filter = request.args.get('type')
        priority_filter = request.args.get('priority')
        
        # Query base
        query = Alert.query.filter_by(user_id=current_user.id)
        
        # Aplicar filtros
        if status_filter:
            try:
                # Os valores do enum são em minúsculo
                status_enum = AlertStatus(status_filter.lower())
                query = query.filter(Alert.status == status_enum)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': f'Status inválido: {status_filter}. Valores válidos: {[s.value for s in AlertStatus]}',
                    'error_code': 'VALIDATION_ERROR',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
                
        if type_filter:
            try:
                type_enum = AlertType(type_filter.lower())
                query = query.filter(Alert.type == type_enum)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': f'Tipo inválido: {type_filter}',
                    'error_code': 'VALIDATION_ERROR',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
                
        if priority_filter:
            try:
                priority_enum = AlertPriority(priority_filter.lower())
                query = query.filter(Alert.priority == priority_enum)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': f'Prioridade inválida: {priority_filter}',
                    'error_code': 'VALIDATION_ERROR',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
        
        # Contar total antes da paginação
        total = query.count()
        
        # Ordenação e paginação
        alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
        
        # Serializar dados
        alerts_data = [alert.to_dict() for alert in alerts]
        
        return jsonify({
            'status': 'success',
            'data': {
                'alerts': alerts_data,
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar alertas para usuário {current_user.id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@alerts_api_bp.route('/widget', methods=['GET'])
@login_required
def alerts_widget():
    """
    Endpoint especial para widget de alertas no dashboard
    
    Returns:
    - 200: Dados formatados para o widget (estatísticas + alertas críticos/recentes)
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        # Verificar se o usuário está autenticado
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Usuário não autenticado',
                'error_code': 'UNAUTHORIZED',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 401

        # Buscar estatísticas com tratamento de erro
        try:
            stats_query = Alert.query.filter_by(user_id=current_user.id)
            
            total_alerts = stats_query.count()
            # Corrigir: alertas não lidos são PENDING e SENT (não apenas read_at == None)
            unread_alerts = stats_query.filter(Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT])).count()
            critical_alerts = stats_query.filter(Alert.priority == AlertPriority.CRITICAL).count()
        except Exception as db_error:
            current_app.logger.error(f"Erro ao consultar estatísticas de alertas: {str(db_error)}")
            # Valores padrão em caso de erro na base de dados
            total_alerts = 0
            unread_alerts = 0
            critical_alerts = 0
        
        # Buscar alertas críticos (até 3 mais recentes)
        critical_alerts_list = []
        recent_alerts_list = []
        
        try:
            # Alertas críticos não resolvidos
            critical_alerts_list = (Alert.query
                                   .filter_by(user_id=current_user.id)
                                   .filter(Alert.priority == AlertPriority.CRITICAL)
                                   .filter(Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT]))
                                   .order_by(Alert.created_at.desc())
                                   .limit(3)
                                   .all())
            
            # Buscar alertas recentes não resolvidos (até 5 mais recentes, excluindo críticos)
            recent_alerts_list = (Alert.query
                                 .filter_by(user_id=current_user.id)
                                 .filter(Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT]))
                                 .filter(Alert.priority != AlertPriority.CRITICAL)
                                 .order_by(Alert.created_at.desc())
                                 .limit(5)
                                 .all())
        except Exception as query_error:
            current_app.logger.error(f"Erro ao consultar alertas: {str(query_error)}")
            # Listas vazias em caso de erro
            critical_alerts_list = []
            recent_alerts_list = []
        
        # Serializar dados
        critical_data = []
        for alert in critical_alerts_list:
            alert_dict = alert.to_dict()
            # Adicionar campos extras para o frontend
            alert_dict['type_icon'] = {
                'weather': 'fa-cloud-sun',
                'irrigation': 'fa-tint',
                'disease': 'fa-bug',
                'pests': 'fa-spider',
                'fertilizer': 'fa-leaf',
                'maintenance': 'fa-tools',
                'harvest': 'fa-carrot',
                'planting': 'fa-seedling',
                'general': 'fa-bell'
            }.get(alert.type.value, 'fa-bell')
            
            alert_dict['priority_color'] = {
                'critical': 'red',
                'medium': 'orange',
                'low': 'blue'
            }.get(alert.priority.value, 'gray')
            
            critical_data.append(alert_dict)
        
        recent_data = []
        for alert in recent_alerts_list:
            alert_dict = alert.to_dict()
            # Adicionar campos extras para o frontend
            alert_dict['type_icon'] = {
                'weather': 'fa-cloud-sun',
                'irrigation': 'fa-tint',
                'disease': 'fa-bug',
                'pests': 'fa-spider',
                'fertilizer': 'fa-leaf',
                'maintenance': 'fa-tools',
                'harvest': 'fa-carrot',
                'planting': 'fa-seedling',
                'general': 'fa-bell'
            }.get(alert.type.value, 'fa-bell')
            
            alert_dict['priority_color'] = {
                'critical': 'red',
                'medium': 'orange',
                'low': 'blue'
            }.get(alert.priority.value, 'gray')
            
            recent_data.append(alert_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'stats': {
                    'total': total_alerts,
                    'unread': unread_alerts,
                    'critical': critical_alerts
                },
                'critical_alerts': critical_data,
                'recent_alerts': recent_data
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar widget de alertas para usuário {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@alerts_api_bp.route('/create', methods=['POST'])
@login_required
def create_alert():
    """
    Cria novo alerta para o usuário autenticado
    
    Request Body (JSON):
    {
      "type": "weather|pest|disease|irrigation|fertilization|harvest|pruning|market|general",
      "priority": "low|medium|high|critical",
      "title": "Título do alerta (máx 200 chars)",
      "message": "Mensagem do alerta",
      "action_text": "Texto do botão de ação (opcional)",
      "action_url": "URL da ação (opcional)",
      "culture_id": 123 (opcional),
      "scheduled_for": "2025-08-01T15:30:00Z" (opcional),
      "expires_at": "2025-08-02T15:30:00Z" (opcional)
    }
    
    Returns:
    - 201: Alerta criado com sucesso
    - 400: Dados inválidos
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type deve ser application/json',
                'error_code': 'INVALID_CONTENT_TYPE',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Corpo da requisição JSON é obrigatório',
                'error_code': 'INVALID_JSON',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Validar dados
        validation_errors = validate_alert_data(data)
        if validation_errors:
            return jsonify({
                'status': 'error',
                'message': 'Dados inválidos fornecidos',
                'error_code': 'VALIDATION_ERROR',
                'details': {'errors': validation_errors},
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Validar culture_id se fornecido
        if data.get('culture_id'):
            from app.models.culture import Culture
            culture = Culture.query.filter_by(
                id=data['culture_id'], 
                user_id=current_user.id
            ).first()
            if not culture:
                return jsonify({
                    'status': 'error',
                    'message': 'Cultura não encontrada ou não pertence ao usuário',
                    'error_code': 'VALIDATION_ERROR',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
        
        # Criar alerta
        alert = Alert(
            user_id=current_user.id,
            type=AlertType(data['type']),
            priority=AlertPriority(data['priority']),
            status=AlertStatus.PENDING,  # Status padrão
            title=data['title'],
            message=data['message'],
            action_text=data.get('action_text'),
            action_url=data.get('action_url'),
            culture_id=data.get('culture_id'),
            scheduled_for=datetime.fromisoformat(data['scheduled_for'].replace('Z', '+00:00')) if data.get('scheduled_for') else None,
            expires_at=datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00')) if data.get('expires_at') else None,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(alert)
        db.session.commit()
        
        current_app.logger.info(f"Alerta {alert.id} criado para usuário {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta criado com sucesso',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar alerta para usuário {current_user.id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_api_bp.route('/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """
    Marca alerta como lido
    
    Path Parameters:
    - alert_id (int): ID do alerta
    
    Returns:
    - 200: Alerta marcado como lido
    - 404: Alerta não encontrado
    - 403: Usuário não autorizado
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        # Buscar alerta
        alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        
        if not alert:
            return jsonify({
                'status': 'error',
                'message': 'Alerta não encontrado',
                'error_code': 'NOT_FOUND',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        # Verificar se já foi lido
        if alert.status == AlertStatus.READ:
            return jsonify({
                'status': 'success',
                'message': 'Alerta já estava marcado como lido',
                'data': {
                    'alert': alert.to_dict()
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
        
        # Marcar como lido
        alert.status = AlertStatus.READ
        alert.read_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        current_app.logger.info(f"Alerta {alert_id} marcado como lido por usuário {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta marcado como lido',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao marcar alerta {alert_id} como lido: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@alerts_api_bp.route('/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def dismiss_alert(alert_id):
    """
    Dispensa alerta
    
    Path Parameters:
    - alert_id (int): ID do alerta
    
    Returns:
    - 200: Alerta dispensado
    - 404: Alerta não encontrado
    - 403: Usuário não autorizado
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        # Buscar alerta
        alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        
        if not alert:
            return jsonify({
                'status': 'error',
                'message': 'Alerta não encontrado',
                'error_code': 'NOT_FOUND',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        # Verificar se já foi dispensado
        if alert.status == AlertStatus.DISMISSED:
            return jsonify({
                'status': 'success',
                'message': 'Alerta já estava dispensado',
                'data': {
                    'alert': alert.to_dict()
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
        
        # Dispensar alerta
        alert.status = AlertStatus.DISMISSED
        alert.dismissed_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        current_app.logger.info(f"Alerta {alert_id} dispensado por usuário {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta dispensado',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao dispensar alerta {alert_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@alerts_api_bp.route('/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """
    Resolve (marca como resolvido) um alerta específico
    
    Path Parameters:
    - alert_id (int): ID do alerta
    
    Returns:
    - 200: Alerta resolvido com sucesso
    - 401: Usuário não autenticado
    - 404: Alerta não encontrado
    - 500: Erro interno
    """
    try:
        # Buscar alerta
        alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alerta não encontrado',
                'error_code': 'ALERT_NOT_FOUND',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        # Marcar como resolvido
        alert.status = AlertStatus.RESOLVED
        alert.dismissed_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Alerta resolvido',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao resolver alerta {alert_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@alerts_api_bp.route('/bulk-read', methods=['POST'])
@login_required
def bulk_mark_read():
    """
    Marca todos os alertas ativos do usuário como lidos
    
    Returns:
    - 200: Alertas marcados como lidos
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        # Buscar todos os alertas não lidos do usuário - usar read_at is None
        unread_alerts = Alert.query.filter_by(user_id=current_user.id).filter(Alert.read_at == None).all()
        
        count = len(unread_alerts)
        
        # Marcar todos como lidos
        for alert in unread_alerts:
            alert.status = AlertStatus.READ
            alert.read_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count} alertas marcados como lidos',
            'data': {
                'marked_count': count
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao marcar alertas como lidos em lote: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@alerts_api_bp.route('/generate', methods=['POST'])
@login_required
def generate_alerts():
    """
    Gera todos os alertas reais usando o AlertService
    Inclui alertas de plantio, clima, irrigação, etc.
    
    Returns:
    - 200: Alertas gerados
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
    try:
        from app.services.alert_service import AlertService
        
        alert_service = AlertService()
        new_alerts = alert_service.generate_all_alerts(current_user.id)
        
        return jsonify({
            'success': True,
            'message': f'{len(new_alerts)} alertas gerados',
            'count': len(new_alerts),
            'data': {
                'alerts': [alert.to_dict() for alert in new_alerts],
                'types_generated': list(set([alert.type.value for alert in new_alerts]))
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao gerar alertas: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500



# Health check endpoint para monitoramento
@alerts_api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check da API de alertas"""
    try:
        # Testar conexão com banco de dados
        total_alerts = Alert.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'API de alertas funcionando',
            'data': {
                'total_alerts': total_alerts,
                'available_types': [t.value for t in AlertType],
                'available_priorities': [p.value for p in AlertPriority],
                'available_statuses': [s.value for s in AlertStatus]
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no health check da API de alertas: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@alerts_api_bp.route('/recentes', methods=['GET'])
@login_required
def get_recent_alerts():
    """Obtém alertas recentes do usuário"""
    try:
        from app.services.alert_service import AlertService
        alert_service = AlertService()
        
        # Buscar alertas recentes
        alerts = alert_service.get_active_alerts(current_user.id, limit=5)
        
        # Converter para dicionário
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'type': alert.type.value,
                'priority': alert.priority.value,
                'title': alert.title,
                'message': alert.message,
                'created_at': alert.created_at.isoformat() if alert.created_at else None,
                'status': alert.status.value
            })
        
        return jsonify({
            'success': True,
            'data': alerts_data,
            'total': len(alerts_data)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar alertas recentes: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR'
        }), 500
