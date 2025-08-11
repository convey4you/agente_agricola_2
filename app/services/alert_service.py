"""
Serviço de Alertas Inteligentes
Motor principal para geração e gestão de alertas
"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from app import db
from app.models.alerts import Alert, AlertRule, AlertType, AlertPriority, AlertStatus
from app.models.culture import Culture
from app.models.user import User
from app.services.weather_data_service import WeatherDataService
import logging
import json

logger = logging.getLogger(__name__)


class AlertService:
    """Serviço principal de alertas inteligentes"""
    
    def __init__(self):
        self.weather_service = WeatherDataService()
    
    def generate_all_alerts(self, user_id: int) -> List[Alert]:
        """Gera todos os alertas para um usuário"""
        alerts = []
        
        try:
            user = User.query.get(user_id)
            if not user:
                return alerts

            # Limpar alertas duplicados/antigos primeiro
            self._cleanup_old_alerts(user_id)
            
            # Gerar alertas meteorológicos
            weather_alerts = self.generate_weather_alerts(user)
            alerts.extend(weather_alerts)
            
            # Gerar alertas de culturas
            culture_alerts = self.generate_culture_alerts(user)
            alerts.extend(culture_alerts)
            
            # Gerar alertas de oportunidades de plantio
            planting_alerts = self.generate_planting_alerts(user)
            alerts.extend(planting_alerts)
            
            # Gerar alertas de tarefas
            task_alerts = self.generate_task_alerts(user)
            alerts.extend(task_alerts)

            # Filtrar duplicatas antes de salvar
            alerts = self._remove_duplicates(alerts, user_id)
            
            # Salvar alertas no banco
            for alert in alerts:
                db.session.add(alert)
            
            db.session.commit()
            logger.info(f"Gerados {len(alerts)} alertas para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar alertas: {str(e)}")
            db.session.rollback()
        
        return alerts

    def _cleanup_old_alerts(self, user_id: int):
        """Remove alertas antigos e duplicados"""
        try:
            # Remover alertas expirados
            expired_alerts = Alert.query.filter_by(user_id=user_id).filter(
                Alert.expires_at.isnot(None),
                Alert.expires_at < datetime.now(timezone.utc)
            ).all()
            
            for alert in expired_alerts:
                db.session.delete(alert)
            
            # Remover alertas de plantio antigos (mais de 30 dias)
            old_planting_alerts = Alert.query.filter_by(
                user_id=user_id,
                type=AlertType.PLANTING
            ).filter(
                Alert.created_at < datetime.now() - timedelta(days=30)
            ).all()
            
            for alert in old_planting_alerts:
                db.session.delete(alert)
                
            db.session.commit()
            logger.info(f"Removidos {len(expired_alerts) + len(old_planting_alerts)} alertas antigos para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"Erro ao limpar alertas antigos: {str(e)}")
            db.session.rollback()

    def _remove_duplicates(self, new_alerts: List[Alert], user_id: int) -> List[Alert]:
        """Remove alertas duplicados baseado em título e tipo"""
        try:
            # Buscar alertas existentes ativos
            existing_alerts = Alert.query.filter_by(user_id=user_id).filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).all()
            
            existing_signatures = set()
            for alert in existing_alerts:
                signature = f"{alert.type.value}:{alert.title}"
                existing_signatures.add(signature)
            
            # Filtrar novos alertas para remover duplicatas
            unique_alerts = []
            for alert in new_alerts:
                signature = f"{alert.type.value}:{alert.title}"
                if signature not in existing_signatures:
                    unique_alerts.append(alert)
                    existing_signatures.add(signature)  # Evitar duplicatas dentro dos novos alertas
                else:
                    logger.info(f"Alerta duplicado ignorado: {alert.title}")
            
            return unique_alerts
            
        except Exception as e:
            logger.error(f"Erro ao remover duplicatas: {str(e)}")
            return new_alerts

    def generate_weather_alerts(self, user: User) -> List[Alert]:
        """Gera alertas baseados em condições meteorológicas"""
        alerts = []
        
        try:
            # Obter dados meteorológicos
            location = {
                'latitude': user.latitude if hasattr(user, 'latitude') and user.latitude else 38.7223,
                'longitude': user.longitude if hasattr(user, 'longitude') and user.longitude else -9.1393
            }
            weather_result = self.weather_service.get_current_weather()
            
            if not weather_result or not weather_result.get('success'):
                return alerts
            
            # Extrair dados corretos da estrutura retornada
            weather_data = weather_result.get('data', {})
            current = weather_data.get('current', weather_data) if isinstance(weather_data, dict) else weather_data
            forecast = weather_data.get('forecast', [])
            
            # Alertas de temperatura extrema
            alerts.extend(self._check_temperature_alerts(user, current, forecast))
            
            # Alertas de humidade
            alerts.extend(self._check_humidity_alerts(user, current))
            
            # Alertas de vento forte
            alerts.extend(self._check_wind_alerts(user, current))
            
            # Alertas de precipitação
            alerts.extend(self._check_precipitation_alerts(user, forecast))
            
        except Exception as e:
            logger.error(f"Erro ao gerar alertas meteorológicos: {str(e)}")
        
        return alerts
    
    def generate_culture_alerts(self, user: User) -> List[Alert]:
        """Gera alertas baseados no estado das culturas"""
        alerts = []
        
        try:
            cultures = Culture.query.filter_by(user_id=user.id, active=True).all()
            
            for culture in cultures:
                # Alertas de irrigação
                alerts.extend(self._check_irrigation_alerts(user, culture))
                
                # Alertas de colheita
                alerts.extend(self._check_harvest_alerts(user, culture))
                
                # Alertas de saúde da cultura
                alerts.extend(self._check_health_alerts(user, culture))
                
        except Exception as e:
            logger.error(f"Erro ao gerar alertas de culturas: {str(e)}")
        
        return alerts
    
    def generate_task_alerts(self, user: User) -> List[Alert]:
        """Gera alertas baseados em tarefas e cronogramas"""
        alerts = []
        
        try:
            # Alertas de tarefas vencidas (implementar quando tiver sistema de tarefas)
            # Por enquanto, criar alertas de exemplo baseados nas culturas
            cultures = Culture.query.filter_by(user_id=user.id, active=True).all()
            
            for culture in cultures:
                # Verificar se precisa de manutenção
                days_since_planting = (datetime.now() - culture.created_at).days
                
                if days_since_planting > 7 and days_since_planting % 7 == 0:
                    alert = Alert(
                        user_id=user.id,
                        culture_id=culture.id,
                        type=AlertType.GENERAL,
                        priority=AlertPriority.MEDIUM,
                        title=f'Verificação semanal - {culture.nome}',
                        message=f'É hora de verificar o estado da sua cultura de {culture.nome}. Verifique sinais de pragas, doenças e necessidades de irrigação.',
                        data_dict={
                            'culture_name': culture.nome,
                            'days_since_planting': days_since_planting,
                            'task_type': 'weekly_check'
                        }
                    )
                    alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Erro ao gerar alertas de tarefas: {str(e)}")
        
        return alerts
    
    def _check_temperature_alerts(self, user: User, current: Dict, forecast: List) -> List[Alert]:
        """Verifica alertas de temperatura"""
        alerts = []
        
        try:
            temp = current.get('temperature', 0)
            
            # Temperatura muito alta (>35°C)
            if temp > 35:
                alert = Alert(
                    user_id=user.id,
                    type='weather',
                    priority='critical',
                    title='🌡️ Temperatura Extrema Detectada',
                    message=f'Temperatura atual de {temp}°C pode causar stress térmico nas plantas. Considere irrigação adicional e sombreamento.',
                    data_dict={
                        'temperature': temp,
                        'threshold': 35,
                        'recommendation': 'increase_irrigation'
                    }
                )
                alerts.append(alert)
            
            # Temperatura muito baixa (<5°C)
            elif temp < 5:
                alert = Alert(
                    user_id=user.id,
                    type='weather',
                    priority='critical',
                    title='🥶 Risco de Geada',
                    message=f'Temperatura baixa de {temp}°C representa risco de geada. Proteja as culturas sensíveis.',
                    data_dict={
                        'temperature': temp,
                        'threshold': 5,
                        'recommendation': 'frost_protection'
                    }
                )
                alerts.append(alert)
            
            # Verificar previsão de geada nos próximos dias
            for day in forecast[:3]:  # Próximos 3 dias
                if day.get('temperature_min', 10) < 2:
                    alert = Alert(
                        user_id=user.id,
                        type='weather',
                        priority='medium',
                        title='❄️ Previsão de Geada',
                        message=f'Previsão de temperatura mínima de {day.get("temperature_min")}°C. Prepare proteções para as culturas.',
                        data_dict={
                            'forecast_temp': day.get('temperature_min'),
                            'date': day.get('date'),
                            'recommendation': 'prepare_frost_protection'
                        }
                    )
                    alerts.append(alert)
                    break  # Apenas um alerta de previsão
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de temperatura: {str(e)}")
        
        return alerts
    
    def _check_humidity_alerts(self, user: User, current: Dict) -> List[Alert]:
        """Verifica alertas de humidade"""
        alerts = []
        
        try:
            humidity = current.get('humidity', 50)
            
            # Humidade muito baixa (<30%)
            if humidity < 30:
                alert = Alert(
                    user_id=user.id,
                    type='weather',
                    priority='medium',
                    title='💧 Humidade Baixa',
                    message=f'Humidade de {humidity}% pode causar stress hídrico. Considere irrigação adicional.',
                    data_dict={
                        'humidity': humidity,
                        'threshold': 30,
                        'recommendation': 'increase_irrigation'
                    }
                )
                alerts.append(alert)
            
            # Humidade muito alta (>85%)
            elif humidity > 85:
                alert = Alert(
                    user_id=user.id,
                    type='weather',
                    priority='medium',
                    title='🍄 Humidade Alta - Risco de Fungos',
                    message=f'Humidade de {humidity}% favorece o desenvolvimento de doenças fúngicas. Monitore as plantas.',
                    data_dict={
                        'humidity': humidity,
                        'threshold': 85,
                        'recommendation': 'monitor_fungal_diseases'
                    }
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de humidade: {str(e)}")
        
        return alerts
    
    def _check_wind_alerts(self, user: User, current: Dict) -> List[Alert]:
        """Verifica alertas de vento forte"""
        alerts = []
        
        try:
            wind_speed = current.get('wind_speed', 0)
            
            # Vento forte (>10 m/s = 36 km/h)
            if wind_speed > 10:
                alert = Alert(
                    user_id=user.id,
                    type='weather',
                    priority='medium',
                    title='💨 Vento Forte',
                    message=f'Ventos de {wind_speed:.1f} m/s podem danificar plantas jovens. Verifique suportes e proteções.',
                    data_dict={
                        'wind_speed': wind_speed,
                        'threshold': 10,
                        'recommendation': 'check_plant_supports'
                    }
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de vento: {str(e)}")
        
        return alerts
    
    def _check_precipitation_alerts(self, user: User, forecast: List) -> List[Alert]:
        """Verifica alertas de precipitação"""
        alerts = []
        
        try:
            # Verificar previsão de chuva intensa nos próximos dias
            for day in forecast[:3]:
                # Se houver dados de precipitação (implementar quando a API fornecer)
                # Por enquanto, simular baseado na condição
                condition = day.get('condition', '').lower()
                
                if 'chuva' in condition or 'rain' in condition:
                    alert = Alert(
                        user_id=user.id,
                        type='weather',
                        priority='low',
                        title='🌧️ Previsão de Chuva',
                        message=f'Chuva prevista para os próximos dias. Ajuste a programação de irrigação.',
                        data_dict={
                            'condition': condition,
                            'date': day.get('date'),
                            'recommendation': 'adjust_irrigation'
                        }
                    )
                    alerts.append(alert)
                    break  # Apenas um alerta de chuva
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de precipitação: {str(e)}")
        
        return alerts
    
    def _check_irrigation_alerts(self, user: User, culture: Culture) -> List[Alert]:
        """Verifica necessidade de irrigação"""
        alerts = []
        
        try:
            # Verificar se já existe um alerta de irrigação ativo para esta cultura
            existing_irrigation_alert = Alert.query.filter_by(
                user_id=user.id,
                culture_id=culture.id,
                type=AlertType.IRRIGATION
            ).filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).first()
            
            if existing_irrigation_alert:
                logger.info(f"Alerta de irrigação já existe para cultura {culture.nome} (ID: {culture.id})")
                return []
            
            # Usar data_plantio em vez de created_at para consistência
            if not culture.data_plantio:
                return alerts
                
            # Calcular dias desde o plantio
            days_since_planting = (datetime.now().date() - culture.data_plantio).days
            
            # Alertas baseados no tipo de cultura
            irrigation_intervals = {
                'tomate': 2,
                'alface': 1,
                'cenoura': 3,
                'batata': 3,
                'milho': 4,
                'feijao': 3,
                'espargos': 3
            }
            
            culture_type = culture.nome.lower()
            interval = irrigation_intervals.get(culture_type, 3)
            
            # Condição mais permissiva: se passou mais de 3 dias desde plantio
            if days_since_planting > 3:
                alert = Alert(
                    user_id=user.id,
                    culture_id=culture.id,
                    type=AlertType.IRRIGATION,
                    priority=AlertPriority.MEDIUM,
                    title=f'💧 Irrigação Necessária - {culture.nome}',
                    message=f'Sua cultura de {culture.nome} precisa de irrigação. Plantada há {days_since_planting} dias.',
                    alert_metadata=f'{{"culture_name": "{culture.nome}", "days_since_planting": {days_since_planting}, "recommendation": "irrigate_now"}}'
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de irrigação: {str(e)}")
        
        return alerts
    
    def _check_harvest_alerts(self, user: User, culture: Culture) -> List[Alert]:
        """Verifica alertas de colheita"""
        alerts = []
        
        try:
            # Verificar se já existe um alerta de colheita ativo para esta cultura
            existing_harvest_alert = Alert.query.filter_by(
                user_id=user.id,
                culture_id=culture.id,
                type=AlertType.HARVEST
            ).filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).first()
            
            if existing_harvest_alert:
                logger.info(f"Alerta de colheita já existe para cultura {culture.nome} (ID: {culture.id})")
                return []
            
            # Tempos aproximados de colheita (em dias)
            harvest_times = {
                'alface': 45,
                'cenoura': 90,
                'tomate': 75,
                'batata': 120,
                'milho': 100,
                'feijao': 60
            }
            
            culture_type = culture.nome.lower()
            harvest_days = harvest_times.get(culture_type, 75)
            
            days_since_planting = (datetime.now() - culture.created_at).days
            
            # Alerta quando próximo da colheita (5 dias antes)
            if days_since_planting >= (harvest_days - 5) and days_since_planting <= harvest_days:
                alert = Alert(
                    user_id=user.id,
                    culture_id=culture.id,
                    type=AlertType.HARVEST,
                    priority=AlertPriority.MEDIUM,
                    title=f'🌾 Colheita Próxima - {culture.nome}',
                    message=f'Sua cultura de {culture.nome} estará pronta para colheita em breve. Verifique o desenvolvimento.',
                    alert_metadata=json.dumps({
                        'culture_name': culture.nome,
                        'expected_harvest_days': harvest_days,
                        'days_since_planting': days_since_planting,
                        'recommendation': 'check_harvest_readiness'
                    })
                )
                alerts.append(alert)
            
            # Alerta quando passou do tempo ideal
            elif days_since_planting > (harvest_days + 10):
                alert = Alert(
                    user_id=user.id,
                    culture_id=culture.id,
                    type=AlertType.HARVEST,
                    priority=AlertPriority.CRITICAL,
                    title=f'⚠️ Colheita Atrasada - {culture.nome}',
                    message=f'Sua cultura de {culture.nome} passou do tempo ideal de colheita. Colha o quanto antes.',
                    alert_metadata=json.dumps({
                        'culture_name': culture.nome,
                        'expected_harvest_days': harvest_days,
                        'days_since_planting': days_since_planting,
                        'days_overdue': days_since_planting - harvest_days,
                        'recommendation': 'harvest_immediately'
                    })
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de colheita: {str(e)}")
        
        return alerts
    
    def _check_health_alerts(self, user: User, culture: Culture) -> List[Alert]:
        """Verifica alertas de saúde das culturas"""
        alerts = []
        
        try:
            # Verificar se já existe um alerta de saúde ativo para esta cultura
            existing_health_alert = Alert.query.filter_by(
                user_id=user.id,
                culture_id=culture.id,
                type=AlertType.GENERAL  # Usando GENERAL para alertas de saúde
            ).filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT]),
                Alert.title.contains('Saúde')
            ).first()
            
            if existing_health_alert:
                logger.info(f"Alerta de saúde já existe para cultura {culture.nome} (ID: {culture.id})")
                return []
            
            # Baseado no status de saúde da cultura
            if hasattr(culture, 'health_status'):
                if culture.health_status == 'poor':
                    alert = Alert(
                        user_id=user.id,
                        culture_id=culture.id,
                        type=AlertType.GENERAL,
                        priority=AlertPriority.CRITICAL,
                        title=f'🚨 Problemas de Saúde - {culture.nome}',
                        message=f'Sua cultura de {culture.nome} apresenta problemas de saúde. Investigação necessária.',
                        alert_metadata=json.dumps({
                            'culture_name': culture.nome,
                            'health_status': culture.health_status,
                            'recommendation': 'investigate_health_issues'
                        })
                    )
                    alerts.append(alert)
                
                elif culture.health_status == 'fair':
                    alert = Alert(
                        user_id=user.id,
                        culture_id=culture.id,
                        type=AlertType.GENERAL,
                        priority=AlertPriority.MEDIUM,
                        title=f'⚠️ Atenção Necessária - {culture.nome}',
                        message=f'Sua cultura de {culture.nome} precisa de atenção. Monitore mais de perto.',
                        alert_metadata=json.dumps({
                            'culture_name': culture.nome,
                            'health_status': culture.health_status,
                            'recommendation': 'increase_monitoring'
                        })
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de saúde: {str(e)}")
        
        return alerts
    
    def get_active_alerts(self, user_id: int, limit: int = 10) -> List[Alert]:
        """Obtém alertas ativos do usuário"""
        try:
            # Buscar todos os alertas do usuário e filtrar no Python
            alerts = Alert.query.filter(
                Alert.user_id == user_id
            ).order_by(
                Alert.priority.desc(),
                Alert.created_at.desc()
            ).all()
            
            # Filtrar por status válidos
            active_alerts = [
                alert for alert in alerts 
                if alert.status in [AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT]
            ]
            
            return active_alerts[:limit]
        except Exception as e:
            logger.error(f"Erro ao buscar alertas ativos: {e}")
            return []
    
    def get_unread_alerts(self, user_id: int) -> List[Alert]:
        """Obtém alertas não lidos"""
        try:
            # Buscar todos os alertas do usuário e filtrar no Python
            alerts = Alert.query.filter(
                Alert.user_id == user_id
            ).order_by(Alert.created_at.desc()).all()
            
            # Filtrar por status não lidos
            unread_alerts = [
                alert for alert in alerts 
                if alert.status in [AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT]
            ]
            
            return unread_alerts
        except Exception as e:
            logger.error(f"Erro ao buscar alertas não lidos: {e}")
            return []
    
    def mark_alert_as_read(self, alert_id: int, user_id: int) -> bool:
        """Marca alerta como lido"""
        try:
            alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
            if alert:
                alert.mark_as_read()
                return True
        except Exception as e:
            logger.error(f"Erro ao marcar alerta como lido: {str(e)}")
        return False
    
    def resolve_alert(self, alert_id: int, user_id: int) -> bool:
        """Resolve um alerta"""
        try:
            alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
            if alert:
                alert.resolve()
                return True
        except Exception as e:
            logger.error(f"Erro ao resolver alerta: {str(e)}")
        return False

    def generate_planting_alerts(self, user: User) -> List[Alert]:
        """Gera alertas de oportunidades de plantio baseados na época ideal"""
        alerts = []
        
        try:
            from app.services.base_conhecimento_culturas import CULTURAS_PORTUGAL
            import calendar
            
            # Obter mês atual
            current_month = datetime.now().strftime('%B')  # Nome do mês em inglês
            
            # Mapear nomes dos meses para português
            month_mapping = {
                'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
                'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
                'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
                'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
            }
            
            current_month_pt = month_mapping.get(current_month, current_month)
            
            # Verificar se já existe alerta de plantio para este mês - buscar todos e filtrar
            all_alerts = Alert.query.filter_by(
                user_id=user.id,
                type=AlertType.PLANTING
            ).all()
            
            existing_alert = None
            for alert in all_alerts:
                if (current_month_pt in alert.title and 
                    alert.created_at >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) and
                    alert.status in [AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT]):
                    existing_alert = alert
                    break
            
            if existing_alert:
                logger.info(f"Alerta de plantio para {current_month_pt} já existe para usuário {user.id}")
                return []
            
            # Buscar culturas que têm época de plantio no mês atual
            planting_opportunities = []
            
            for cultura_nome, cultura_data in CULTURAS_PORTUGAL.items():
                epoca_plantio = cultura_data.get('epoca_plantio', [])
                
                if current_month_pt in epoca_plantio:
                    planting_opportunities.append({
                        'nome': cultura_data.get('nome', cultura_nome.title()),
                        'categoria': cultura_data.get('categoria', 'Hortícola'),
                        'dificuldade': cultura_data.get('dificuldade', 'Média'),
                        'tempo_crescimento': cultura_data.get('tempo_crescimento', 90),
                        'icon': cultura_data.get('icon', '🌱'),
                        'observacoes': cultura_data.get('observacoes', ''),
                        'rendimento_m2': cultura_data.get('rendimento_m2', 0),
                        'area_minima': cultura_data.get('area_minima', 1)
                    })
            
            # Criar alertas para as oportunidades encontradas
            if planting_opportunities:
                # Limitar a 5 culturas para não sobrecarregar
                top_opportunities = planting_opportunities[:5]
                
                # Ordenar por facilidade (fácil primeiro) e rendimento
                top_opportunities.sort(key=lambda x: (
                    {'Fácil': 1, 'Média': 2, 'Difícil': 3}.get(x['dificuldade'], 2),
                    -x['rendimento_m2']
                ))
                
                cultura_names = [opp['nome'] for opp in top_opportunities]
                cultura_icons = [opp['icon'] for opp in top_opportunities]
                
                # Criar alerta principal de oportunidades
                alert_message = f"Este é o mês ideal para plantar: {', '.join(cultura_names)}. "
                alert_message += f"Aproveite as condições favoráveis de {current_month_pt} para começar novas culturas!"
                
                alert = Alert(
                    user_id=user.id,
                    type=AlertType.PLANTING,
                    priority=AlertPriority.MEDIUM,
                    title=f"🌱 Oportunidades de Plantio - {current_month_pt}",
                    message=alert_message,
                    action_text="Ver Culturas",
                    action_url="/cultures/wizard",
                    alert_metadata=json.dumps({
                        'month': current_month_pt,
                        'opportunities': top_opportunities,
                        'total_count': len(planting_opportunities),
                        'recommendation': 'start_planting'
                    })
                )
                alerts.append(alert)
                
                # Criar alertas específicos para culturas de destaque (máximo 2)
                for i, opp in enumerate(top_opportunities[:2]):
                    if opp['dificuldade'] == 'Fácil':  # Focar em culturas fáceis
                        detail_message = f"A {opp['nome']} é ideal para iniciantes e pode ser plantada agora. "
                        detail_message += f"Tempo de crescimento: {opp['tempo_crescimento']} dias. "
                        detail_message += f"Rendimento esperado: {opp['rendimento_m2']} kg/m². "
                        detail_message += f"Área mínima: {opp['area_minima']} m²."
                        
                        detail_alert = Alert(
                            user_id=user.id,
                            type=AlertType.PLANTING,
                            priority=AlertPriority.LOW,
                            title=f"{opp['icon']} Destaque: {opp['nome']}",
                            message=detail_message,
                            action_text="Criar Cultura",
                            action_url=f"/cultures/wizard?cultura={opp['nome'].lower()}",
                            alert_metadata=json.dumps({
                                'cultura_nome': opp['nome'],
                                'cultura_categoria': opp['categoria'],
                                'month': current_month_pt,
                                'recommendation': 'create_specific_culture'
                            })
                        )
                        alerts.append(detail_alert)
            
            logger.info(f"Gerados {len(alerts)} alertas de plantio para {current_month_pt}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar alertas de plantio: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return alerts
    
    def get_alert_stats(self, user_id: int) -> Dict:
        """Obtém estatísticas de alertas do usuário"""
        try:
            total = Alert.query.filter_by(user_id=user_id, is_active=True).count()
            unread = Alert.query.filter_by(user_id=user_id, is_read=False, is_active=True).count()
            critical = Alert.query.filter_by(user_id=user_id, priority='critical', is_active=True, is_resolved=False).count()
            
            return {
                'total': total,
                'unread': unread,
                'critical': critical,
                'read': total - unread
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de alertas: {str(e)}")
            return {'total': 0, 'unread': 0, 'critical': 0, 'read': 0}
