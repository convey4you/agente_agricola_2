"""
Serviço de Geração Automática de Alertas
Sistema que verifica preferências dos usuários e gera alertas automaticamente
"""
from datetime import datetime, timezone
from app import db
from app.models.alerts import UserAlertPreference, AlertType
from app.services.alert_service import AlertService
import logging

logger = logging.getLogger(__name__)

class AutoAlertService:
    """Serviço para geração automática de alertas baseado nas preferências do usuário"""
    
    def __init__(self):
        self.alert_service = AlertService()
    
    def run_auto_generation(self):
        """Executar geração automática para todos os usuários elegíveis"""
        try:
            current_time = datetime.now()
            logger.info(f"Iniciando geração automática de alertas - {current_time}")
            
            # Buscar todas as preferências que precisam de geração automática
            preferences = UserAlertPreference.query.filter(
                UserAlertPreference.auto_generation_enabled == True,
                UserAlertPreference.is_enabled == True
            ).all()
            
            users_processed = set()
            total_alerts_generated = 0
            
            for preference in preferences:
                try:
                    if preference.should_generate_automatically(current_time):
                        user_id = preference.user_id
                        
                        # Evitar gerar múltiplas vezes para o mesmo usuário
                        if user_id not in users_processed:
                            logger.info(f"Gerando alertas automáticos para usuário {user_id}")
                            
                            # Gerar alertas baseado no tipo de preferência
                            new_alerts = []
                            if preference.alert_type == AlertType.PLANTING:
                                new_alerts = self.alert_service.generate_planting_alerts(user_id)
                            else:
                                # Para outros tipos, usar geração completa
                                new_alerts = self.alert_service.generate_all_alerts(user_id)
                            
                            total_alerts_generated += len(new_alerts)
                            users_processed.add(user_id)
                            
                            # Marcar como processado
                            preference.mark_auto_generation_completed()
                            
                            logger.info(f"Gerados {len(new_alerts)} alertas para usuário {user_id}")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar preferência {preference.id}: {str(e)}")
                    continue
            
            logger.info(f"Geração automática concluída: {len(users_processed)} usuários processados, {total_alerts_generated} alertas gerados")
            return {
                'success': True,
                'users_processed': len(users_processed),
                'alerts_generated': total_alerts_generated,
                'processed_at': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na geração automática de alertas: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def get_users_pending_auto_generation(self):
        """Obter usuários que têm geração automática pendente"""
        current_time = datetime.now()
        
        preferences = UserAlertPreference.query.filter(
            UserAlertPreference.auto_generation_enabled == True,
            UserAlertPreference.is_enabled == True
        ).all()
        
        pending_users = []
        for preference in preferences:
            if preference.should_generate_automatically(current_time):
                pending_users.append({
                    'user_id': preference.user_id,
                    'alert_type': preference.alert_type.value,
                    'frequency': preference.auto_frequency,
                    'next_generation': preference.get_next_auto_generation_time().isoformat() if preference.get_next_auto_generation_time() else None,
                    'last_generation': preference.last_auto_generation.isoformat() if preference.last_auto_generation else None
                })
        
        return pending_users
    
    def create_default_preferences_for_user(self, user_id):
        """Criar preferências padrão para um novo usuário"""
        try:
            # Verificar se já existem preferências
            existing = UserAlertPreference.query.filter_by(user_id=user_id).first()
            if existing:
                return False
            
            # Criar preferência padrão para alertas de plantio
            planting_pref = UserAlertPreference(
                user_id=user_id,
                alert_type=AlertType.PLANTING,
                is_enabled=True,
                auto_generation_enabled=True,
                auto_frequency='weekly',  # Semanal por padrão
                auto_time=datetime.strptime('08:00', '%H:%M').time(),
                auto_weekday=0,  # Segunda-feira
                web_enabled=True,
                email_enabled=False,
                sms_enabled=False
            )
            
            db.session.add(planting_pref)
            db.session.commit()
            
            logger.info(f"Preferências padrão criadas para usuário {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar preferências padrão para usuário {user_id}: {str(e)}")
            return False
    
    def update_user_preferences(self, user_id, alert_type, preferences_data):
        """Atualizar preferências de um usuário"""
        try:
            preference = UserAlertPreference.query.filter_by(
                user_id=user_id,
                alert_type=alert_type
            ).first()
            
            if not preference:
                # Criar nova preferência
                preference = UserAlertPreference(
                    user_id=user_id,
                    alert_type=alert_type
                )
                db.session.add(preference)
            
            # Atualizar campos
            for key, value in preferences_data.items():
                if hasattr(preference, key):
                    if key == 'auto_time' and isinstance(value, str):
                        value = datetime.strptime(value, '%H:%M').time()
                    setattr(preference, key, value)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar preferências: {str(e)}")
            return False
