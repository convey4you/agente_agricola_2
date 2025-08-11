from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from app.models.alerts import Alert, AlertRule, AlertType, AlertPriority, AlertStatus, UserAlertPreference
from app.models.user import User
from app.models.culture import Culture
from app import db
import logging
import json

logger = logging.getLogger(__name__)

class AlertEngine:
    """Motor principal de processamento de alertas"""
    
    def __init__(self):
        # Importações dinâmicas para evitar dependências circulares
        try:
            from app.services.notification_service import NotificationService
            self.notification_service = NotificationService()
        except ImportError:
            logger.warning("NotificationService não disponível")
            self.notification_service = None
        
        # Weather service será implementado no próximo sprint
        self.weather_service = None
    
    def process_all_alerts(self):
        """Processar todos os alertas pendentes e gerar novos"""
        logger.info("Iniciando processamento de alertas")
        
        try:
            # 1. Processar alertas pendentes
            self._process_pending_alerts()
            
            # 2. Gerar novos alertas baseados em regras
            self._generate_rule_based_alerts()
            
            # 3. Limpar alertas expirados
            self._cleanup_expired_alerts()
            
            logger.info("Processamento de alertas concluído")
            
        except Exception as e:
            logger.error(f"Erro no processamento de alertas: {e}", exc_info=True)
    
    def _process_pending_alerts(self):
        """Processar alertas pendentes para envio"""
        pending_alerts = Alert.query.filter_by(status=AlertStatus.PENDING).all()
        
        logger.info(f"Processando {len(pending_alerts)} alertas pendentes")
        
        for alert in pending_alerts:
            try:
                # Verificar se deve ser enviado agora
                if self._should_send_alert_now(alert):
                    self._send_alert(alert)
                
            except Exception as e:
                logger.error(f"Erro ao processar alerta {alert.id}: {e}")
                alert.retry_count += 1
                alert.last_retry_at = datetime.now(timezone.utc)
                
                # Se muitas tentativas, marcar como expirado
                if alert.retry_count >= 3:
                    alert.status = AlertStatus.EXPIRED
                
                db.session.commit()
    
    def _should_send_alert_now(self, alert: Alert) -> bool:
        """Verificar se alerta deve ser enviado agora"""
        current_time = datetime.now(timezone.utc)
        
        # Verificar se está agendado para o futuro
        if alert.scheduled_for and alert.scheduled_for > current_time:
            return False
        
        # Verificar se expirou
        if alert.is_expired:
            alert.status = AlertStatus.EXPIRED
            db.session.commit()
            return False
        
        # Verificar preferências do usuário
        user_prefs = self._get_user_preferences(alert.user_id, alert.type)
        if not user_prefs.should_send_alert(alert.priority):
            return False
        
        return True
    
    def _send_alert(self, alert: Alert):
        """Enviar alerta através dos canais configurados"""
        user_prefs = self._get_user_preferences(alert.user_id, alert.type)
        channels = user_prefs.get_enabled_channels()
        
        success = False
        
        for channel in channels:
            try:
                if channel == 'web':
                    # Alerta web já está no banco, apenas marcar como enviado
                    success = True
                    
                elif channel == 'email' and self.notification_service:
                    success = self.notification_service.send_email_alert(alert)
                    
                elif channel == 'sms' and self.notification_service:
                    success = self.notification_service.send_sms_alert(alert)
                
                if success:
                    logger.info(f"Alerta {alert.id} enviado via {channel}")
                
            except Exception as e:
                logger.error(f"Erro ao enviar alerta {alert.id} via {channel}: {e}")
        
        if success:
            alert.mark_as_sent()
            db.session.commit()
            logger.info(f"Alerta {alert.id} marcado como enviado")
    
    def _generate_rule_based_alerts(self):
        """Gerar alertas baseados em regras ativas"""
        active_rules = AlertRule.query.filter_by(is_active=True).all()
        users = User.query.filter_by(is_active=True).all()
        
        logger.info(f"Avaliando {len(active_rules)} regras para {len(users)} usuários")
        
        for user in users:
            for rule in active_rules:
                try:
                    # Verificar cooldown
                    if self._is_rule_in_cooldown(rule, user):
                        continue
                    
                    # Obter contexto do usuário
                    context = self._build_user_context(user)
                    
                    # Avaliar condições da regra
                    if rule.evaluate_conditions(context):
                        self._create_alert_from_rule(rule, user, context)
                
                except Exception as e:
                    logger.error(f"Erro ao avaliar regra {rule.id} para usuário {user.id}: {e}")
    
    def _is_rule_in_cooldown(self, rule: AlertRule, user: User) -> bool:
        """Verificar se regra está em período de cooldown"""
        if rule.cooldown_hours <= 0:
            return False
        
        cooldown_start = datetime.now(timezone.utc) - timedelta(hours=rule.cooldown_hours)
        
        recent_alert = Alert.query.filter(
            Alert.user_id == user.id,
            Alert.type == rule.alert_type,
            Alert.created_at >= cooldown_start,
            Alert.alert_metadata.contains(f'"rule_id": {rule.id}')
        ).first()
        
        return recent_alert is not None
    
    def _build_user_context(self, user: User) -> Dict[str, Any]:
        """Construir contexto do usuário para avaliação de regras"""
        context = {
            'user': {
                'id': user.id,
                'email': user.email,
                'experiencia': getattr(user, 'experiencia', 'iniciante'),
                'tipo_produtor': getattr(user, 'tipo_produtor', 'individual'),
                'location': self._get_user_location(user)
            },
            'cultures': [],
            'weather': {},
            'datetime': {
                'now': datetime.now(timezone.utc).isoformat(),
                'today': datetime.now(timezone.utc).date().isoformat(),
                'hour': datetime.now(timezone.utc).hour,
                'month': datetime.now(timezone.utc).month,
                'season': self._get_current_season()
            }
        }
        
        # Adicionar dados das culturas se existirem
        try:
            cultures = getattr(user, 'cultures', [])
            for culture in cultures:
                culture_data = {
                    'id': culture.id,
                    'name': getattr(culture, 'name', ''),
                    'type': getattr(culture, 'type', ''),
                    'area': getattr(culture, 'area', 0),
                    'planting_date': culture.planting_date.isoformat() if hasattr(culture, 'planting_date') and culture.planting_date else None,
                    'status': getattr(culture, 'status', 'active')
                }
                context['cultures'].append(culture_data)
        except:
            pass
        
        # Adicionar dados climáticos (simulados por agora)
        context['weather'] = {
            'temperature': 15.0,
            'humidity': 75.0,
            'precipitation': 0.0,
            'wind_speed': 10.0,
            'days_without_rain': 3
        }
        
        return context
    
    def _get_user_location(self, user: User) -> Dict[str, Any]:
        """Obter localização do usuário"""
        return {
            'lat': getattr(user, 'location_lat', None),
            'lng': getattr(user, 'location_lng', None),
            'city': getattr(user, 'location_city', None),
            'district': getattr(user, 'location_district', None)
        }
    
    def _get_current_season(self) -> str:
        """Determinar estação atual (hemisfério norte)"""
        month = datetime.now(timezone.utc).month
        
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _create_alert_from_rule(self, rule: AlertRule, user: User, context: Dict[str, Any]):
        """Criar alerta baseado em regra"""
        try:
            # Gerar conteúdo do alerta
            content = rule.generate_alert_content(context)
            if not content:
                return
            
            # Determinar expiração
            expires_at = None
            if rule.expires_after_hours > 0:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=rule.expires_after_hours)
            
            # Criar alerta
            alert = Alert(
                user_id=user.id,
                type=rule.alert_type,
                priority=rule.priority,
                title=content['title'],
                message=content['message'],
                action_text=content.get('action_text'),
                action_url=content.get('action_url'),
                expires_at=expires_at,
                alert_metadata=json.dumps({
                    'rule_id': rule.id,
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'context_snapshot': context
                })
            )
            
            db.session.add(alert)
            db.session.commit()
            
            logger.info(f"Alerta criado da regra {rule.id} para usuário {user.id}: {alert.id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta da regra {rule.id}: {e}")
            db.session.rollback()
    
    def _cleanup_expired_alerts(self):
        """Limpar alertas expirados"""
        expired_alerts = Alert.query.filter(
            Alert.expires_at < datetime.now(timezone.utc),
            Alert.status != AlertStatus.EXPIRED
        ).all()
        
        for alert in expired_alerts:
            alert.status = AlertStatus.EXPIRED
        
        db.session.commit()
        
        if expired_alerts:
            logger.info(f"Marcados {len(expired_alerts)} alertas como expirados")
    
    def _get_user_preferences(self, user_id: int, alert_type: AlertType) -> UserAlertPreference:
        """Obter preferências do usuário para tipo de alerta"""
        pref = UserAlertPreference.query.filter_by(
            user_id=user_id,
            alert_type=alert_type
        ).first()
        
        if not pref:
            # Criar preferência padrão
            pref = UserAlertPreference(
                user_id=user_id,
                alert_type=alert_type
            )
            db.session.add(pref)
            db.session.commit()
        
        return pref
    
    def create_manual_alert(self, user_id: int, alert_type: AlertType, 
                          title: str, message: str, priority: AlertPriority = AlertPriority.MEDIUM,
                          action_text: str = None, action_url: str = None,
                          culture_id: int = None, expires_hours: int = 72) -> Alert:
        """Criar alerta manual"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
        
        alert = Alert(
            user_id=user_id,
            type=alert_type,
            priority=priority,
            title=title,
            message=message,
            action_text=action_text,
            action_url=action_url,
            culture_id=culture_id,
            expires_at=expires_at,
            alert_metadata=json.dumps({
                'manual': True,
                'created_at': datetime.now(timezone.utc).isoformat()
            })
        )
        
        db.session.add(alert)
        db.session.commit()
        
        logger.info(f"Alerta manual criado: {alert.id}")
        return alert
    
    def get_user_alerts(self, user_id: int, limit: int = 50, 
                       include_read: bool = True) -> List[Alert]:
        """Obter alertas do usuário"""
        query = Alert.query.filter_by(user_id=user_id)
        
        if not include_read:
            query = query.filter(Alert.status != AlertStatus.READ)
        
        query = query.filter(Alert.status != AlertStatus.EXPIRED)
        query = query.order_by(Alert.created_at.desc())
        
        return query.limit(limit).all()
    
    def mark_alert_as_read(self, alert_id: int, user_id: int) -> bool:
        """Marcar alerta como lido"""
        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        
        if alert:
            alert.mark_as_read()
            db.session.commit()
            return True
        
        return False
    
    def dismiss_alert(self, alert_id: int, user_id: int) -> bool:
        """Dispensar alerta"""
        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        
        if alert:
            alert.dismiss()
            db.session.commit()
            return True
        
        return False
