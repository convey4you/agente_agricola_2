"""
Dashboard Service - Simplificado sem funcionalidades de clima
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from flask_login import current_user
from flask import current_app

from app import db
from app.models.culture import Culture
from app.models.activity import Activity

logger = logging.getLogger(__name__)


class DashboardService:
    """Serviço simplificado para dados do dashboard"""
    
    @staticmethod
    def get_dashboard_data() -> Dict[str, Any]:
        """Obtém dados básicos do dashboard"""
        try:
            if not current_user.is_authenticated:
                return {
                    'success': False,
                    'error': 'Usuário não autenticado',
                    'status_code': 401
                }
            
            logger.info(f"Obtendo dados do dashboard para usuário: {current_user.email}")
            
            data = {
                'overview': DashboardService.get_overview_data(),
                'alerts': DashboardService.get_alerts_data(),
                'alerts_count': DashboardService.get_unread_alerts_count(),
                'recent_activities': DashboardService.get_recent_activities(),
                'cultures': DashboardService.get_active_cultures()
            }
            
            return {
                'success': True,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do dashboard: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar dados do dashboard',
                'status_code': 500
            }
    
    @staticmethod
    def get_overview_data() -> Dict[str, Any]:
        """Obtém dados de visão geral"""
        try:
            if not current_user.is_authenticated:
                return {}
            
            # Contar culturas ativas
            active_cultures = Culture.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).count()
            
            # Contar atividades pendentes
            pending_activities = Activity.query.filter_by(
                user_id=current_user.id,
                status='pendente'
            ).count()
            
            # Calcular área total
            total_area = db.session.query(
                db.func.sum(Culture.area_plantada)
            ).filter_by(
                user_id=current_user.id,
                is_active=True
            ).scalar() or 0
            
            return {
                'active_cultures': active_cultures,
                'total_area': float(total_area),
                'monthly_production': 0,  # Placeholder
                'projected_revenue': 0   # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de overview: {e}")
            return {
                'active_cultures': 0,
                'total_area': 0,
                'monthly_production': 0,
                'projected_revenue': 0
            }
    
    @staticmethod
    def get_alerts_data() -> List[Dict[str, Any]]:
        """Obtém dados de alertas"""
        try:
            if not current_user.is_authenticated:
                return []
            
            # Importar AlertService localmente para evitar import circular
            from app.services.alert_service import AlertService
            
            alert_service = AlertService()
            
            # Primeiro gerar alertas atualizados
            alert_service.generate_all_alerts(current_user.id)
            
            # Depois buscar alertas ativos
            alerts = alert_service.get_active_alerts(current_user.id, limit=5)
            
            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    'id': alert.id,
                    'title': alert.title,
                    'message': alert.message,
                    'type': alert.type.value if hasattr(alert.type, 'value') else str(alert.type),
                    'priority': alert.priority.value if hasattr(alert.priority, 'value') else str(alert.priority),
                    'created_at': alert.created_at.isoformat() if alert.created_at else None,
                    'is_read': alert.is_read,
                    'action_text': alert.action_text,
                    'action_url': alert.action_url
                })
            
            return alerts_data
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    @staticmethod
    def get_unread_alerts_count() -> int:
        """Conta alertas não lidos"""
        try:
            if not current_user.is_authenticated:
                return 0
            
            # Importar AlertService localmente para evitar import circular
            from app.services.alert_service import AlertService
            
            alert_service = AlertService()
            unread_alerts = alert_service.get_unread_alerts(current_user.id)
            return len(unread_alerts)
            
        except Exception as e:
            logger.error(f"Erro ao contar alertas: {e}")
            return 0
    
    @staticmethod
    def get_recent_activities() -> List[Dict[str, Any]]:
        """Obtém atividades recentes"""
        try:
            if not current_user.is_authenticated:
                return []
            
            # Últimas 5 atividades
            activities = Activity.query.filter_by(
                user_id=current_user.id
            ).order_by(Activity.created_at.desc()).limit(5).all()
            
            return [{
                'id': activity.id,
                'titulo': activity.titulo,
                'status': activity.status,
                'created_at': activity.created_at.isoformat()
            } for activity in activities]
            
        except Exception as e:
            logger.error(f"Erro ao obter atividades recentes: {e}")
            return []
    
    @staticmethod
    def get_active_cultures() -> List[Dict[str, Any]]:
        """Obtém lista de culturas ativas do usuário"""
        try:
            if not current_user.is_authenticated:
                return []
            
            cultures = Culture.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).order_by(Culture.created_at.desc()).all()
            
            cultures_data = []
            for culture in cultures:
                # Formatear data de plantio se existir
                data_plantio_formatted = None
                if culture.data_plantio:
                    data_plantio_formatted = culture.data_plantio.strftime('%d/%m/%Y')
                
                # Determinar status de saúde (placeholder - pode ser expandido)
                health_status = 'healthy'  # Padrão
                
                # Buscar próxima atividade
                next_activity = Activity.query.filter_by(
                    user_id=current_user.id,
                    culture_id=culture.id,
                    status='pendente'
                ).order_by(Activity.data_prevista.asc()).first()
                
                next_activity_data = None
                if next_activity:
                    next_activity_data = {
                        'title': next_activity.titulo,
                        'date': next_activity.data_prevista.strftime('%d/%m/%Y') if next_activity.data_prevista else None
                    }
                
                cultures_data.append({
                    'id': culture.id,
                    'nome': culture.nome,
                    'variedade': culture.variedade,
                    'area_plantada': float(culture.area_plantada) if culture.area_plantada else 0,
                    'data_plantio_formatted': data_plantio_formatted,
                    'health_status': health_status,
                    'next_activity': next_activity_data
                })
            
            return cultures_data
            
        except Exception as e:
            logger.error(f"Erro ao obter culturas ativas: {e}")
            return []
