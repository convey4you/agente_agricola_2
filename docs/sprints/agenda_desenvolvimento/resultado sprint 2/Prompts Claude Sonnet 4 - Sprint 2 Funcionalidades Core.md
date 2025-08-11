# Prompts Claude Sonnet 4 - Sprint 2 Funcionalidades Core
## AgroTech Portugal - Implementação de Funcionalidades Principais

**Documento**: Prompts Específicos para Claude Sonnet 4  
**Projeto**: Sistema de Agente Agrícola Inteligente  
**Sprint**: 2 - Funcionalidades Core  
**Período**: 05 de agosto - 16 de agosto de 2025  
**Autor**: Gerente de Tecnologia  
**Baseado em**: Cronograma Atualizado + Análise QA + Especificações Técnicas

---

## 📋 INSTRUÇÕES PARA USO DOS PROMPTS

### Contexto do Sprint 2
O Sprint 2 foca na implementação das funcionalidades core do AgroTech Portugal, construindo sobre a base sólida estabelecida no Sprint 1. Com os problemas críticos de sessões e onboarding resolvidos, agora implementamos as funcionalidades que diferenciam o sistema no mercado português.

### Estrutura dos Prompts
Cada prompt segue o padrão enterprise estabelecido:
- **Contexto do Projeto**: Informações sobre o AgroTech Portugal e progresso atual
- **Funcionalidade Específica**: Descrição detalhada da feature a implementar
- **Arquitetura Proposta**: Design técnico e padrões a seguir
- **Implementação Detalhada**: Código completo e funcional
- **Integração com Sistema**: Como conectar com funcionalidades existentes
- **Testes e Validação**: Suite completa de testes
- **Critérios de Aceitação**: Como validar o sucesso

### Ordem de Execução Recomendada
Os prompts devem ser executados na ordem apresentada, pois há dependências entre as funcionalidades:

1. **Sistema de Alertas** → Base para notificações
2. **Integração Climática IPMA** → Dados para recomendações
3. **Sistema de Recomendações IA** → Core do valor agregado
4. **Gestão de Culturas** → Interface principal do usuário
5. **Marketplace Básico** → Monetização e ecossistema

### Cronograma Sprint 2
- **Semana 1 (05-09/08)**: Prompts 1-2 (Alertas + Clima)
- **Semana 2 (12-16/08)**: Prompts 3-5 (IA + Culturas + Marketplace)

---

## 🚨 PROMPT 1: SISTEMA DE ALERTAS INTELIGENTES

### Contexto do Projeto
Você está implementando o sistema de alertas inteligentes para o AgroTech Portugal, uma funcionalidade core que diferencia o sistema no mercado. O sistema deve fornecer alertas proativos baseados em dados climáticos, condições das culturas e recomendações de IA, específicos para a agricultura portuguesa.

### Funcionalidade a Implementar
Sistema completo de alertas que monitora condições climáticas, pragas, doenças e oportunidades de manejo, enviando notificações personalizadas via web, email e futuramente SMS. O sistema deve ser inteligente, evitando spam e priorizando alertas críticos.

### Arquitetura Proposta

O sistema de alertas seguirá uma arquitetura baseada em eventos com os seguintes componentes:

**Componentes Principais:**
- **Alert Engine**: Motor de processamento de alertas
- **Rule Engine**: Sistema de regras configuráveis
- **Notification Service**: Serviço de envio de notificações
- **Alert Storage**: Armazenamento e histórico de alertas
- **User Preferences**: Configurações personalizadas por usuário

**Fluxo de Dados:**
1. Dados climáticos/culturas → Alert Engine
2. Alert Engine → Rule Engine (avaliação de regras)
3. Rule Engine → Alert Storage (persistir alertas)
4. Alert Storage → Notification Service (envio)
5. Notification Service → Usuário (web/email/SMS)

### Objetivo
Implementar sistema robusto e escalável de alertas inteligentes que forneça valor real aos agricultores portugueses, aumentando produtividade e reduzindo riscos através de notificações proativas e personalizadas.

### Instruções Detalhadas

**ETAPA 1: Modelos de Dados para Alertas**

Crie os modelos necessários em `app/models/alerts.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum
import json

db = SQLAlchemy()

class AlertType(Enum):
    """Tipos de alertas disponíveis"""
    WEATHER = "weather"          # Alertas climáticos
    PEST = "pest"               # Pragas
    DISEASE = "disease"         # Doenças
    IRRIGATION = "irrigation"   # Irrigação
    FERTILIZATION = "fertilization"  # Adubação
    HARVEST = "harvest"         # Colheita
    PRUNING = "pruning"         # Poda
    MARKET = "market"           # Oportunidades de mercado
    GENERAL = "general"         # Alertas gerais

class AlertPriority(Enum):
    """Prioridades de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status dos alertas"""
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    DISMISSED = "dismissed"
    EXPIRED = "expired"

class Alert(db.Model):
    """Modelo principal de alertas"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Classificação do alerta
    type = db.Column(db.Enum(AlertType), nullable=False)
    priority = db.Column(db.Enum(AlertPriority), default=AlertPriority.MEDIUM)
    status = db.Column(db.Enum(AlertStatus), default=AlertStatus.PENDING)
    
    # Conteúdo do alerta
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_text = db.Column(db.String(100))  # Texto do botão de ação
    action_url = db.Column(db.String(500))   # URL da ação
    
    # Dados contextuais
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'))
    location_data = db.Column(db.Text)  # JSON com dados de localização
    weather_data = db.Column(db.Text)   # JSON com dados climáticos
    metadata = db.Column(db.Text)       # JSON com metadados adicionais
    
    # Controle temporal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_for = db.Column(db.DateTime)  # Para alertas agendados
    expires_at = db.Column(db.DateTime)     # Expiração do alerta
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    
    # Controle de envio
    delivery_channels = db.Column(db.String(100), default='web')  # web,email,sms
    retry_count = db.Column(db.Integer, default=0)
    last_retry_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', backref='alerts')
    culture = db.relationship('Culture', backref='alerts')
    
    def to_dict(self):
        """Converter alerta para dicionário"""
        return {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'title': self.title,
            'message': self.message,
            'action_text': self.action_text,
            'action_url': self.action_url,
            'culture_id': self.culture_id,
            'created_at': self.created_at.isoformat(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'metadata': json.loads(self.metadata) if self.metadata else {}
        }
    
    @property
    def is_expired(self):
        """Verificar se alerta expirou"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_urgent(self):
        """Verificar se alerta é urgente"""
        return self.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]
    
    def mark_as_sent(self):
        """Marcar alerta como enviado"""
        self.status = AlertStatus.SENT
        self.sent_at = datetime.utcnow()
    
    def mark_as_read(self):
        """Marcar alerta como lido"""
        if self.status == AlertStatus.SENT:
            self.status = AlertStatus.READ
            self.read_at = datetime.utcnow()
    
    def dismiss(self):
        """Dispensar alerta"""
        self.status = AlertStatus.DISMISSED
        self.dismissed_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Alert {self.id}: {self.title}>'

class AlertRule(db.Model):
    """Regras para geração automática de alertas"""
    __tablename__ = 'alert_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Configuração da regra
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    priority = db.Column(db.Enum(AlertPriority), default=AlertPriority.MEDIUM)
    
    # Condições (JSON)
    conditions = db.Column(db.Text, nullable=False)  # JSON com condições
    
    # Template do alerta
    title_template = db.Column(db.String(200), nullable=False)
    message_template = db.Column(db.Text, nullable=False)
    action_text = db.Column(db.String(100))
    action_url_template = db.Column(db.String(500))
    
    # Controle temporal
    cooldown_hours = db.Column(db.Integer, default=24)  # Evitar spam
    expires_after_hours = db.Column(db.Integer, default=72)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def evaluate_conditions(self, context):
        """Avaliar se condições da regra são atendidas"""
        try:
            conditions = json.loads(self.conditions)
            return self._evaluate_condition_tree(conditions, context)
        except Exception as e:
            print(f"Erro ao avaliar condições da regra {self.id}: {e}")
            return False
    
    def _evaluate_condition_tree(self, condition, context):
        """Avaliar árvore de condições recursivamente"""
        if isinstance(condition, dict):
            if 'operator' in condition:
                operator = condition['operator']
                operands = condition['operands']
                
                if operator == 'AND':
                    return all(self._evaluate_condition_tree(op, context) for op in operands)
                elif operator == 'OR':
                    return any(self._evaluate_condition_tree(op, context) for op in operands)
                elif operator == 'NOT':
                    return not self._evaluate_condition_tree(operands[0], context)
                else:
                    return self._evaluate_simple_condition(condition, context)
            else:
                return self._evaluate_simple_condition(condition, context)
        return False
    
    def _evaluate_simple_condition(self, condition, context):
        """Avaliar condição simples"""
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not all([field, operator, value is not None]):
            return False
        
        context_value = self._get_context_value(field, context)
        
        if operator == 'eq':
            return context_value == value
        elif operator == 'ne':
            return context_value != value
        elif operator == 'gt':
            return float(context_value) > float(value)
        elif operator == 'gte':
            return float(context_value) >= float(value)
        elif operator == 'lt':
            return float(context_value) < float(value)
        elif operator == 'lte':
            return float(context_value) <= float(value)
        elif operator == 'contains':
            return str(value).lower() in str(context_value).lower()
        elif operator == 'in':
            return context_value in value
        
        return False
    
    def _get_context_value(self, field, context):
        """Obter valor do contexto usando notação de ponto"""
        keys = field.split('.')
        value = context
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def generate_alert_content(self, context):
        """Gerar conteúdo do alerta baseado no template"""
        try:
            title = self._render_template(self.title_template, context)
            message = self._render_template(self.message_template, context)
            action_url = self._render_template(self.action_url_template, context) if self.action_url_template else None
            
            return {
                'title': title,
                'message': message,
                'action_text': self.action_text,
                'action_url': action_url
            }
        except Exception as e:
            print(f"Erro ao gerar conteúdo do alerta: {e}")
            return None
    
    def _render_template(self, template, context):
        """Renderizar template simples com substituição de variáveis"""
        if not template:
            return ""
        
        result = template
        for key, value in self._flatten_context(context).items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def _flatten_context(self, context, prefix=""):
        """Achatar contexto aninhado para substituição em templates"""
        flattened = {}
        
        for key, value in context.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_context(value, full_key))
            else:
                flattened[full_key] = value
        
        return flattened
    
    def __repr__(self):
        return f'<AlertRule {self.id}: {self.name}>'

class UserAlertPreference(db.Model):
    """Preferências de alertas por usuário"""
    __tablename__ = 'user_alert_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Preferências por tipo de alerta
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    
    # Canais de entrega preferidos
    web_enabled = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    
    # Configurações de timing
    quiet_hours_start = db.Column(db.Time)  # Início do período silencioso
    quiet_hours_end = db.Column(db.Time)    # Fim do período silencioso
    
    # Filtros de prioridade
    min_priority = db.Column(db.Enum(AlertPriority), default=AlertPriority.LOW)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='alert_preferences')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'alert_type'),)
    
    def should_send_alert(self, alert_priority, current_time=None):
        """Verificar se deve enviar alerta baseado nas preferências"""
        if not self.is_enabled:
            return False
        
        # Verificar prioridade mínima
        priority_levels = {
            AlertPriority.LOW: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.HIGH: 3,
            AlertPriority.CRITICAL: 4
        }
        
        if priority_levels[alert_priority] < priority_levels[self.min_priority]:
            return False
        
        # Verificar horário silencioso (exceto para críticos)
        if (alert_priority != AlertPriority.CRITICAL and 
            self.quiet_hours_start and self.quiet_hours_end):
            
            current_time = current_time or datetime.now().time()
            
            if self.quiet_hours_start <= self.quiet_hours_end:
                # Período normal (ex: 22:00 - 08:00)
                if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                    return False
            else:
                # Período que cruza meia-noite (ex: 22:00 - 08:00)
                if current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end:
                    return False
        
        return True
    
    def get_enabled_channels(self):
        """Obter canais de entrega habilitados"""
        channels = []
        if self.web_enabled:
            channels.append('web')
        if self.email_enabled:
            channels.append('email')
        if self.sms_enabled:
            channels.append('sms')
        return channels
    
    def __repr__(self):
        return f'<UserAlertPreference {self.user_id}-{self.alert_type.value}>'
```

**ETAPA 2: Motor de Alertas (Alert Engine)**

Crie o motor principal em `app/services/alert_engine.py`:

```python
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.models.alerts import Alert, AlertRule, AlertType, AlertPriority, AlertStatus, UserAlertPreference
from app.models import User, Culture, db
from app.services.notification_service import NotificationService
from app.services.weather_service import WeatherService
import logging
import json

logger = logging.getLogger(__name__)

class AlertEngine:
    """Motor principal de processamento de alertas"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.weather_service = WeatherService()
    
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
                alert.last_retry_at = datetime.utcnow()
                
                # Se muitas tentativas, marcar como expirado
                if alert.retry_count >= 3:
                    alert.status = AlertStatus.EXPIRED
                
                db.session.commit()
    
    def _should_send_alert_now(self, alert: Alert) -> bool:
        """Verificar se alerta deve ser enviado agora"""
        current_time = datetime.utcnow()
        
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
                    
                elif channel == 'email':
                    success = self.notification_service.send_email_alert(alert)
                    
                elif channel == 'sms':
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
        
        cooldown_start = datetime.utcnow() - timedelta(hours=rule.cooldown_hours)
        
        recent_alert = Alert.query.filter(
            Alert.user_id == user.id,
            Alert.type == rule.alert_type,
            Alert.created_at >= cooldown_start,
            Alert.metadata.contains(f'"rule_id": {rule.id}')
        ).first()
        
        return recent_alert is not None
    
    def _build_user_context(self, user: User) -> Dict[str, Any]:
        """Construir contexto do usuário para avaliação de regras"""
        context = {
            'user': {
                'id': user.id,
                'email': user.email,
                'experiencia': user.experiencia,
                'tipo_produtor': user.tipo_produtor,
                'location': self._get_user_location(user)
            },
            'cultures': [],
            'weather': {},
            'datetime': {
                'now': datetime.utcnow().isoformat(),
                'today': datetime.utcnow().date().isoformat(),
                'hour': datetime.utcnow().hour,
                'month': datetime.utcnow().month,
                'season': self._get_current_season()
            }
        }
        
        # Adicionar dados das culturas
        for culture in user.cultures:
            culture_data = {
                'id': culture.id,
                'name': culture.name,
                'type': culture.type,
                'area': culture.area,
                'planting_date': culture.planting_date.isoformat() if culture.planting_date else None,
                'status': culture.status
            }
            context['cultures'].append(culture_data)
        
        # Adicionar dados climáticos
        if user.location_lat and user.location_lng:
            try:
                weather_data = self.weather_service.get_current_weather(
                    user.location_lat, user.location_lng
                )
                context['weather'] = weather_data
            except Exception as e:
                logger.warning(f"Erro ao obter dados climáticos para usuário {user.id}: {e}")
        
        return context
    
    def _get_user_location(self, user: User) -> Dict[str, Any]:
        """Obter localização do usuário"""
        return {
            'lat': user.location_lat,
            'lng': user.location_lng,
            'city': user.location_city,
            'district': user.location_district
        }
    
    def _get_current_season(self) -> str:
        """Determinar estação atual (hemisfério norte)"""
        month = datetime.utcnow().month
        
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
                expires_at = datetime.utcnow() + timedelta(hours=rule.expires_after_hours)
            
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
                metadata=json.dumps({
                    'rule_id': rule.id,
                    'generated_at': datetime.utcnow().isoformat(),
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
            Alert.expires_at < datetime.utcnow(),
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
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
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
            metadata=json.dumps({
                'manual': True,
                'created_at': datetime.utcnow().isoformat()
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
```

**ETAPA 3: Serviço de Notificações**

Crie o serviço de notificações em `app/services/notification_service.py`:

```python
from flask import current_app, render_template_string
from flask_mail import Mail, Message
from app.models.alerts import Alert
import smtplib
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

class NotificationService:
    """Serviço para envio de notificações"""
    
    def __init__(self):
        self.mail = Mail()
    
    def send_email_alert(self, alert: Alert) -> bool:
        """Enviar alerta por email"""
        try:
            user = alert.user
            
            # Template do email
            email_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{{ alert.title }} - AgroTech Portugal</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(90deg, #28a745, #20c997); color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f8f9fa; }
                    .alert-high { border-left: 5px solid #ffc107; }
                    .alert-critical { border-left: 5px solid #dc3545; }
                    .action-button { 
                        display: inline-block; 
                        background: #28a745; 
                        color: white; 
                        padding: 10px 20px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin-top: 15px;
                    }
                    .footer { text-align: center; padding: 20px; color: #6c757d; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌱 AgroTech Portugal</h1>
                        <p>Alerta Agrícola</p>
                    </div>
                    
                    <div class="content {% if alert.priority.value in ['high', 'critical'] %}alert-{{ alert.priority.value }}{% endif %}">
                        <h2>{{ alert.title }}</h2>
                        <p>{{ alert.message }}</p>
                        
                        {% if alert.culture %}
                        <p><strong>Cultura:</strong> {{ alert.culture.name }}</p>
                        {% endif %}
                        
                        <p><strong>Prioridade:</strong> 
                            {% if alert.priority.value == 'critical' %}🔴 Crítica
                            {% elif alert.priority.value == 'high' %}🟡 Alta
                            {% elif alert.priority.value == 'medium' %}🔵 Média
                            {% else %}⚪ Baixa
                            {% endif %}
                        </p>
                        
                        {% if alert.action_url %}
                        <a href="{{ alert.action_url }}" class="action-button">
                            {{ alert.action_text or 'Ver Detalhes' }}
                        </a>
                        {% endif %}
                    </div>
                    
                    <div class="footer">
                        <p>Este é um alerta automático do AgroTech Portugal.</p>
                        <p>Para alterar suas preferências de notificação, 
                           <a href="{{ base_url }}/settings/notifications">clique aqui</a>.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Renderizar template
            html_content = render_template_string(
                email_template,
                alert=alert,
                base_url=current_app.config.get('BASE_URL', 'https://agrotech.pt')
            )
            
            # Criar mensagem
            msg = Message(
                subject=f"🌱 {alert.title} - AgroTech Portugal",
                recipients=[user.email],
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            # Enviar
            self.mail.send(msg)
            
            logger.info(f"Email enviado para {user.email} - Alerta {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para alerta {alert.id}: {e}")
            return False
    
    def send_sms_alert(self, alert: Alert) -> bool:
        """Enviar alerta por SMS (implementação futura)"""
        try:
            user = alert.user
            
            if not user.telefone:
                logger.warning(f"Usuário {user.id} não tem telefone cadastrado")
                return False
            
            # Preparar mensagem SMS (máximo 160 caracteres)
            sms_message = f"🌱 AgroTech: {alert.title}"
            if len(alert.message) < 100:
                sms_message += f" - {alert.message}"
            
            if len(sms_message) > 160:
                sms_message = sms_message[:157] + "..."
            
            # Aqui você integraria com um provedor de SMS
            # Por exemplo: Twilio, AWS SNS, etc.
            success = self._send_sms_via_provider(user.telefone, sms_message)
            
            if success:
                logger.info(f"SMS enviado para {user.telefone} - Alerta {alert.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS para alerta {alert.id}: {e}")
            return False
    
    def _send_sms_via_provider(self, phone: str, message: str) -> bool:
        """Enviar SMS através de provedor (implementação exemplo)"""
        # Implementação de exemplo - substitua pela integração real
        
        # Exemplo com Twilio
        if current_app.config.get('TWILIO_ENABLED'):
            try:
                from twilio.rest import Client
                
                client = Client(
                    current_app.config['TWILIO_ACCOUNT_SID'],
                    current_app.config['TWILIO_AUTH_TOKEN']
                )
                
                message = client.messages.create(
                    body=message,
                    from_=current_app.config['TWILIO_PHONE_NUMBER'],
                    to=phone
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Erro ao enviar SMS via Twilio: {e}")
                return False
        
        # Exemplo com webhook genérico
        elif current_app.config.get('SMS_WEBHOOK_URL'):
            try:
                response = requests.post(
                    current_app.config['SMS_WEBHOOK_URL'],
                    json={
                        'phone': phone,
                        'message': message,
                        'api_key': current_app.config.get('SMS_API_KEY')
                    },
                    timeout=10
                )
                
                return response.status_code == 200
                
            except Exception as e:
                logger.error(f"Erro ao enviar SMS via webhook: {e}")
                return False
        
        else:
            # SMS desabilitado - apenas log
            logger.info(f"SMS simulado para {phone}: {message}")
            return True
    
    def send_bulk_notification(self, user_ids: list, title: str, message: str,
                             alert_type: str = 'general', priority: str = 'medium') -> int:
        """Enviar notificação em massa"""
        from app.services.alert_engine import AlertEngine
        from app.models.alerts import AlertType, AlertPriority
        
        alert_engine = AlertEngine()
        sent_count = 0
        
        try:
            alert_type_enum = AlertType(alert_type)
            priority_enum = AlertPriority(priority)
            
            for user_id in user_ids:
                try:
                    alert_engine.create_manual_alert(
                        user_id=user_id,
                        alert_type=alert_type_enum,
                        title=title,
                        message=message,
                        priority=priority_enum
                    )
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao criar alerta para usuário {user_id}: {e}")
            
            logger.info(f"Notificação em massa enviada para {sent_count} usuários")
            return sent_count
            
        except Exception as e:
            logger.error(f"Erro na notificação em massa: {e}")
            return 0
```

**ETAPA 4: Regras Padrão de Alertas**

Crie script para popular regras padrão em `scripts/create_default_alert_rules.py`:

```python
from app import create_app, db
from app.models.alerts import AlertRule, AlertType, AlertPriority
import json

def create_default_alert_rules():
    """Criar regras padrão de alertas para Portugal"""
    
    app = create_app()
    with app.app_context():
        
        rules = [
            # Alertas Climáticos
            {
                'name': 'Alerta de Geada',
                'description': 'Alerta quando temperatura pode causar geada',
                'alert_type': AlertType.WEATHER,
                'priority': AlertPriority.HIGH,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.temperature', 'operator': 'lte', 'value': 2},
                        {'field': 'datetime.month', 'operator': 'in', 'value': [11, 12, 1, 2, 3]}
                    ]
                }),
                'title_template': '🧊 Alerta de Geada - {weather.temperature}°C',
                'message_template': 'Temperatura prevista de {weather.temperature}°C pode causar geada. Proteja suas culturas sensíveis e considere irrigação preventiva.',
                'action_text': 'Ver Previsão',
                'action_url_template': '/weather',
                'cooldown_hours': 12,
                'expires_after_hours': 24
            },
            
            {
                'name': 'Chuva Intensa',
                'description': 'Alerta para chuva intensa que pode afetar culturas',
                'alert_type': AlertType.WEATHER,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'field': 'weather.precipitation', 'operator': 'gt', 'value': 20
                }),
                'title_template': '🌧️ Chuva Intensa Prevista',
                'message_template': 'Previsão de {weather.precipitation}mm de chuva. Verifique drenagem e considere adiar aplicações de defensivos.',
                'action_text': 'Ver Detalhes',
                'action_url_template': '/weather',
                'cooldown_hours': 6,
                'expires_after_hours': 12
            },
            
            {
                'name': 'Vento Forte',
                'description': 'Alerta para ventos fortes',
                'alert_type': AlertType.WEATHER,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'field': 'weather.wind_speed', 'operator': 'gt', 'value': 40
                }),
                'title_template': '💨 Vento Forte - {weather.wind_speed} km/h',
                'message_template': 'Ventos de {weather.wind_speed} km/h previstos. Evite aplicações e verifique estruturas de suporte.',
                'action_text': 'Ver Previsão',
                'action_url_template': '/weather',
                'cooldown_hours': 8,
                'expires_after_hours': 16
            },
            
            # Alertas de Irrigação
            {
                'name': 'Necessidade de Irrigação',
                'description': 'Alerta quando não chove há muito tempo',
                'alert_type': AlertType.IRRIGATION,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.days_without_rain', 'operator': 'gt', 'value': 7},
                        {'field': 'datetime.month', 'operator': 'in', 'value': [5, 6, 7, 8, 9]}
                    ]
                }),
                'title_template': '💧 Irrigação Recomendada',
                'message_template': 'Sem chuva há {weather.days_without_rain} dias. Verifique umidade do solo e considere irrigação.',
                'action_text': 'Planejar Irrigação',
                'action_url_template': '/cultures',
                'cooldown_hours': 48,
                'expires_after_hours': 72
            },
            
            # Alertas de Adubação
            {
                'name': 'Época de Adubação Primavera',
                'description': 'Lembrete de adubação na primavera',
                'alert_type': AlertType.FERTILIZATION,
                'priority': AlertPriority.LOW,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'datetime.month', 'operator': 'eq', 'value': 3},
                        {'field': 'datetime.day', 'operator': 'in', 'value': [1, 15]}
                    ]
                }),
                'title_template': '🌱 Época de Adubação',
                'message_template': 'Início da primavera é ideal para adubação de base. Analise o solo e aplique nutrientes necessários.',
                'action_text': 'Ver Culturas',
                'action_url_template': '/cultures',
                'cooldown_hours': 336,  # 2 semanas
                'expires_after_hours': 168  # 1 semana
            },
            
            # Alertas de Poda
            {
                'name': 'Época de Poda Inverno',
                'description': 'Lembrete de poda no inverno',
                'alert_type': AlertType.PRUNING,
                'priority': AlertPriority.LOW,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'datetime.month', 'operator': 'in', 'value': [1, 2]},
                        {'field': 'cultures', 'operator': 'contains', 'value': 'fruticultura'}
                    ]
                }),
                'title_template': '✂️ Época de Poda',
                'message_template': 'Inverno é época ideal para poda de árvores frutíferas. Remova ramos doentes e forme a copa.',
                'action_text': 'Ver Culturas',
                'action_url_template': '/cultures',
                'cooldown_hours': 720,  # 1 mês
                'expires_after_hours': 336  # 2 semanas
            },
            
            # Alertas de Pragas e Doenças
            {
                'name': 'Condições para Míldio',
                'description': 'Condições favoráveis ao desenvolvimento de míldio',
                'alert_type': AlertType.DISEASE,
                'priority': AlertPriority.HIGH,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.humidity', 'operator': 'gt', 'value': 80},
                        {'field': 'weather.temperature', 'operator': 'gte', 'value': 15},
                        {'field': 'weather.temperature', 'operator': 'lte', 'value': 25},
                        {'field': 'weather.precipitation', 'operator': 'gt', 'value': 5}
                    ]
                }),
                'title_template': '🦠 Risco de Míldio',
                'message_template': 'Condições climáticas favorecem míldio (umidade {weather.humidity}%, temp {weather.temperature}°C). Monitore culturas sensíveis.',
                'action_text': 'Ver Tratamentos',
                'action_url_template': '/cultures',
                'cooldown_hours': 24,
                'expires_after_hours': 48
            },
            
            {
                'name': 'Condições para Oídio',
                'description': 'Condições favoráveis ao desenvolvimento de oídio',
                'alert_type': AlertType.DISEASE,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.humidity', 'operator': 'gt', 'value': 70},
                        {'field': 'weather.temperature', 'operator': 'gte', 'value': 20},
                        {'field': 'weather.temperature', 'operator': 'lte', 'value': 30},
                        {'field': 'weather.precipitation', 'operator': 'eq', 'value': 0}
                    ]
                }),
                'title_template': '🍄 Risco de Oídio',
                'message_template': 'Tempo seco e quente favorece oídio. Monitore folhas e considere tratamento preventivo.',
                'action_text': 'Ver Culturas',
                'action_url_template': '/cultures',
                'cooldown_hours': 48,
                'expires_after_hours': 72
            }
        ]
        
        for rule_data in rules:
            # Verificar se regra já existe
            existing_rule = AlertRule.query.filter_by(name=rule_data['name']).first()
            
            if not existing_rule:
                rule = AlertRule(**rule_data)
                db.session.add(rule)
                print(f"Criada regra: {rule_data['name']}")
            else:
                print(f"Regra já existe: {rule_data['name']}")
        
        db.session.commit()
        print(f"Processo concluído. Total de regras: {AlertRule.query.count()}")

if __name__ == '__main__':
    create_default_alert_rules()
```

### Testes de Validação

**TESTE 1: Criação e Processamento de Alertas**
```python
# Teste manual no console Python
from app.services.alert_engine import AlertEngine
from app.models.alerts import AlertType, AlertPriority

engine = AlertEngine()

# Criar alerta manual
alert = engine.create_manual_alert(
    user_id=1,
    alert_type=AlertType.WEATHER,
    title="Teste de Alerta",
    message="Este é um teste do sistema de alertas",
    priority=AlertPriority.HIGH
)

# Processar alertas
engine.process_all_alerts()

# Verificar alertas do usuário
alerts = engine.get_user_alerts(user_id=1)
print(f"Usuário tem {len(alerts)} alertas")
```

**TESTE 2: Avaliação de Regras**
```python
# Testar regra específica
from app.models.alerts import AlertRule

rule = AlertRule.query.filter_by(name='Alerta de Geada').first()
context = {
    'weather': {'temperature': 1, 'humidity': 85},
    'datetime': {'month': 12}
}

result = rule.evaluate_conditions(context)
print(f"Regra de geada ativada: {result}")
```

### Critérios de Aceitação
- Sistema de alertas criado e funcional
- Regras padrão implementadas e testadas
- Notificações por email funcionando
- Interface web para visualizar alertas
- Preferências de usuário configuráveis
- Performance adequada (< 5 segundos para processar todos os alertas)
- Logs detalhados implementados

### Entregáveis Esperados
1. **Modelos de Dados** completos para alertas
2. **Alert Engine** funcional com processamento automático
3. **Notification Service** com suporte a email e SMS
4. **Regras Padrão** específicas para agricultura portuguesa
5. **Testes de Validação** executados com sucesso

### Informações Importantes
- Integrar com sistema de usuários existente
- Considerar performance para muitos usuários
- Implementar logs detalhados para debugging
- Preparar para integração com dados climáticos IPMA
- Considerar escalabilidade futura

---

## 🌤️ PROMPT 2: INTEGRAÇÃO CLIMÁTICA IPMA

### Contexto do Projeto
Você está implementando a integração com o Instituto Português do Mar e da Atmosfera (IPMA) para fornecer dados climáticos precisos e específicos para Portugal no AgroTech. Esta integração é fundamental para alimentar o sistema de alertas e fornecer recomendações baseadas em dados reais.

### Funcionalidade a Implementar
Integração completa com as APIs do IPMA para obter dados climáticos atuais, previsões, alertas meteorológicos e dados históricos. O sistema deve cachear dados adequadamente, tratar falhas de conexão e fornecer fallback para outras fontes quando necessário.

### APIs do IPMA Disponíveis

**APIs Principais:**
- **Previsão Meteorológica**: Previsão por distrito/concelho
- **Observações**: Dados atuais das estações meteorológicas
- **Alertas Meteorológicos**: Avisos oficiais do IPMA
- **Índices**: UV, qualidade do ar, risco de incêndio
- **Dados Históricos**: Séries temporais históricas

**Endpoints Principais:**
```
https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/{globalIdLocal}.json
https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json
https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json
https://api.ipma.pt/open-data/distrits-islands.json
```

### Objetivo
Implementar integração robusta e eficiente com IPMA que forneça dados climáticos confiáveis para o sistema de alertas, dashboard e recomendações de IA, específicos para a localização de cada agricultor português.

### Instruções Detalhadas

**ETAPA 1: Modelos de Dados Climáticos**

Crie os modelos em `app/models/weather.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum
import json

db = SQLAlchemy()

class WeatherStation(db.Model):
    """Estações meteorológicas do IPMA"""
    __tablename__ = 'weather_stations'
    
    id = db.Column(db.Integer, primary_key=True)
    ipma_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Localização
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float)
    
    # Localização administrativa
    district = db.Column(db.String(50))
    municipality = db.Column(db.String(50))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_update = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<WeatherStation {self.name}>'

class WeatherObservation(db.Model):
    """Observações meteorológicas atuais"""
    __tablename__ = 'weather_observations'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('weather_stations.id'), nullable=False)
    
    # Timestamp da observação
    observation_time = db.Column(db.DateTime, nullable=False)
    
    # Dados meteorológicos
    temperature = db.Column(db.Float)           # Temperatura (°C)
    humidity = db.Column(db.Float)              # Umidade relativa (%)
    pressure = db.Column(db.Float)              # Pressão atmosférica (hPa)
    wind_speed = db.Column(db.Float)            # Velocidade do vento (km/h)
    wind_direction = db.Column(db.Float)        # Direção do vento (graus)
    precipitation = db.Column(db.Float)         # Precipitação (mm)
    visibility = db.Column(db.Float)            # Visibilidade (km)
    
    # Dados derivados
    dew_point = db.Column(db.Float)             # Ponto de orvalho (°C)
    feels_like = db.Column(db.Float)            # Sensação térmica (°C)
    
    # Metadados
    data_quality = db.Column(db.String(20))     # Qualidade dos dados
    source = db.Column(db.String(20), default='IPMA')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    station = db.relationship('WeatherStation', backref='observations')
    
    __table_args__ = (db.UniqueConstraint('station_id', 'observation_time'),)
    
    def to_dict(self):
        return {
            'station_id': self.station_id,
            'observation_time': self.observation_time.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'precipitation': self.precipitation,
            'visibility': self.visibility,
            'dew_point': self.dew_point,
            'feels_like': self.feels_like
        }

class WeatherForecast(db.Model):
    """Previsões meteorológicas"""
    __tablename__ = 'weather_forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.String(20), nullable=False)  # ID do IPMA para localização
    
    # Data da previsão
    forecast_date = db.Column(db.Date, nullable=False)
    forecast_period = db.Column(db.String(20))  # morning, afternoon, night
    
    # Dados previstos
    min_temperature = db.Column(db.Float)
    max_temperature = db.Column(db.Float)
    precipitation_probability = db.Column(db.Float)  # %
    precipitation_amount = db.Column(db.Float)       # mm
    wind_speed = db.Column(db.Float)                 # km/h
    wind_direction = db.Column(db.String(10))        # N, NE, E, etc.
    humidity = db.Column(db.Float)                   # %
    
    # Condições
    weather_type = db.Column(db.String(50))          # Tipo de tempo
    weather_description = db.Column(db.String(200))  # Descrição
    
    # Índices
    uv_index = db.Column(db.Float)
    fire_risk = db.Column(db.String(20))             # baixo, moderado, elevado, muito elevado
    
    # Metadados
    forecast_issued_at = db.Column(db.DateTime)      # Quando foi emitida
    confidence = db.Column(db.Float)                 # Confiança da previsão (0-1)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('location_id', 'forecast_date', 'forecast_period'),)
    
    def to_dict(self):
        return {
            'location_id': self.location_id,
            'forecast_date': self.forecast_date.isoformat(),
            'forecast_period': self.forecast_period,
            'min_temperature': self.min_temperature,
            'max_temperature': self.max_temperature,
            'precipitation_probability': self.precipitation_probability,
            'precipitation_amount': self.precipitation_amount,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'humidity': self.humidity,
            'weather_type': self.weather_type,
            'weather_description': self.weather_description,
            'uv_index': self.uv_index,
            'fire_risk': self.fire_risk,
            'confidence': self.confidence
        }

class WeatherAlert(db.Model):
    """Alertas meteorológicos oficiais do IPMA"""
    __tablename__ = 'weather_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    ipma_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Localização
    district = db.Column(db.String(50))
    municipalities = db.Column(db.Text)  # JSON com municípios afetados
    
    # Tipo de alerta
    phenomenon = db.Column(db.String(50))        # chuva, vento, neve, etc.
    severity = db.Column(db.String(20))          # amarelo, laranja, vermelho
    awareness_level = db.Column(db.String(50))   # Nível de consciencialização
    
    # Conteúdo
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)            # Instruções para o público
    
    # Período de validade
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    issued_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_current(self):
        """Verificar se alerta está ativo no momento"""
        now = datetime.utcnow()
        return (self.is_active and 
                self.start_time <= now <= self.end_time)
    
    @property
    def severity_color(self):
        """Cor associada à severidade"""
        colors = {
            'amarelo': '#FFC107',
            'laranja': '#FF9800',
            'vermelho': '#F44336'
        }
        return colors.get(self.severity.lower(), '#9E9E9E')
    
    def get_affected_municipalities(self):
        """Obter lista de municípios afetados"""
        if self.municipalities:
            try:
                return json.loads(self.municipalities)
            except:
                return []
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'ipma_id': self.ipma_id,
            'district': self.district,
            'municipalities': self.get_affected_municipalities(),
            'phenomenon': self.phenomenon,
            'severity': self.severity,
            'awareness_level': self.awareness_level,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_current': self.is_current,
            'severity_color': self.severity_color
        }

class LocationMapping(db.Model):
    """Mapeamento de localizações para IDs do IPMA"""
    __tablename__ = 'location_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identificação
    district = db.Column(db.String(50), nullable=False)
    municipality = db.Column(db.String(50))
    parish = db.Column(db.String(50))
    
    # IDs do IPMA
    ipma_district_id = db.Column(db.String(20))
    ipma_location_id = db.Column(db.String(20))   # Para previsões
    
    # Coordenadas representativas
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Estação meteorológica mais próxima
    nearest_station_id = db.Column(db.Integer, db.ForeignKey('weather_stations.id'))
    distance_to_station = db.Column(db.Float)  # km
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    nearest_station = db.relationship('WeatherStation')
    
    def __repr__(self):
        return f'<LocationMapping {self.district}/{self.municipality}>'
```

**ETAPA 2: Serviço de Integração IPMA**

Crie o serviço principal em `app/services/ipma_service.py`:

```python
import requests
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from app.models.weather import (
    WeatherStation, WeatherObservation, WeatherForecast, 
    WeatherAlert, LocationMapping, db
)
import logging
import json
import time
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)

class IPMAService:
    """Serviço de integração com APIs do IPMA"""
    
    BASE_URL = "https://api.ipma.pt/open-data"
    CACHE_DURATION = 3600  # 1 hora em segundos
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgroTech-Portugal/1.0',
            'Accept': 'application/json'
        })
        self._last_request_time = 0
        self._min_request_interval = 1  # 1 segundo entre requests
    
    def _rate_limit(self):
        """Implementar rate limiting básico"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Fazer requisição para API do IPMA com tratamento de erros"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"Fazendo requisição para IPMA: {url}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Resposta recebida do IPMA: {len(str(data))} caracteres")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout na requisição para {url}")
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão com {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {e.response.status_code} para {url}")
            return None
            
        except json.JSONDecodeError:
            logger.error(f"Resposta inválida (não JSON) de {url}")
            return None
            
        except Exception as e:
            logger.error(f"Erro inesperado na requisição para {url}: {e}")
            return None
    
    def update_weather_stations(self) -> int:
        """Atualizar lista de estações meteorológicas"""
        logger.info("Atualizando estações meteorológicas do IPMA")
        
        data = self._make_request("observation/meteorology/stations/stations.json")
        if not data:
            logger.error("Falha ao obter lista de estações")
            return 0
        
        updated_count = 0
        
        try:
            for station_data in data:
                station_id = station_data.get('properties', {}).get('idEstacao')
                if not station_id:
                    continue
                
                # Verificar se estação já existe
                station = WeatherStation.query.filter_by(ipma_id=station_id).first()
                
                if not station:
                    # Criar nova estação
                    geometry = station_data.get('geometry', {})
                    coordinates = geometry.get('coordinates', [])
                    
                    if len(coordinates) >= 2:
                        station = WeatherStation(
                            ipma_id=station_id,
                            name=station_data.get('properties', {}).get('localEstacao', ''),
                            longitude=coordinates[0],
                            latitude=coordinates[1],
                            altitude=coordinates[2] if len(coordinates) > 2 else None
                        )
                        
                        db.session.add(station)
                        updated_count += 1
                        
                        logger.info(f"Nova estação criada: {station.name}")
                
                else:
                    # Atualizar estação existente
                    station.last_update = datetime.utcnow()
                    updated_count += 1
            
            db.session.commit()
            logger.info(f"Atualização de estações concluída: {updated_count} estações")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Erro ao processar estações: {e}")
            db.session.rollback()
            return 0
    
    def update_weather_observations(self) -> int:
        """Atualizar observações meteorológicas atuais"""
        logger.info("Atualizando observações meteorológicas")
        
        data = self._make_request("observation/meteorology/stations/observations.json")
        if not data:
            logger.error("Falha ao obter observações")
            return 0
        
        updated_count = 0
        
        try:
            observation_time = datetime.utcnow()
            
            for obs_data in data:
                station_id_ipma = obs_data.get('idEstacao')
                if not station_id_ipma:
                    continue
                
                # Encontrar estação no banco
                station = WeatherStation.query.filter_by(ipma_id=station_id_ipma).first()
                if not station:
                    continue
                
                # Verificar se observação já existe
                existing_obs = WeatherObservation.query.filter_by(
                    station_id=station.id,
                    observation_time=observation_time.replace(minute=0, second=0, microsecond=0)
                ).first()
                
                if existing_obs:
                    continue
                
                # Criar nova observação
                observation = WeatherObservation(
                    station_id=station.id,
                    observation_time=observation_time,
                    temperature=self._safe_float(obs_data.get('temperatura')),
                    humidity=self._safe_float(obs_data.get('humidade')),
                    pressure=self._safe_float(obs_data.get('pressao')),
                    wind_speed=self._safe_float(obs_data.get('intensidadeVento')),
                    wind_direction=self._safe_float(obs_data.get('direcaoVento')),
                    precipitation=self._safe_float(obs_data.get('precAcumulada')),
                    visibility=self._safe_float(obs_data.get('visibilidade'))
                )
                
                # Calcular dados derivados
                if observation.temperature and observation.humidity:
                    observation.dew_point = self._calculate_dew_point(
                        observation.temperature, observation.humidity
                    )
                    observation.feels_like = self._calculate_feels_like(
                        observation.temperature, observation.humidity, observation.wind_speed or 0
                    )
                
                db.session.add(observation)
                updated_count += 1
            
            db.session.commit()
            logger.info(f"Observações atualizadas: {updated_count}")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Erro ao processar observações: {e}")
            db.session.rollback()
            return 0
    
    def update_weather_forecasts(self, location_id: str = None) -> int:
        """Atualizar previsões meteorológicas"""
        logger.info(f"Atualizando previsões meteorológicas para {location_id or 'todas as localizações'}")
        
        # Se não especificado, atualizar para todas as localizações mapeadas
        if not location_id:
            locations = LocationMapping.query.filter(
                LocationMapping.ipma_location_id.isnot(None)
            ).all()
            
            total_updated = 0
            for location in locations:
                total_updated += self.update_weather_forecasts(location.ipma_location_id)
            
            return total_updated
        
        # Atualizar para localização específica
        data = self._make_request(f"forecast/meteorology/cities/daily/{location_id}.json")
        if not data:
            logger.error(f"Falha ao obter previsões para {location_id}")
            return 0
        
        updated_count = 0
        
        try:
            forecast_data = data.get('data', [])
            
            for day_data in forecast_data:
                forecast_date_str = day_data.get('forecastDate')
                if not forecast_date_str:
                    continue
                
                forecast_date = datetime.strptime(forecast_date_str, '%Y-%m-%d').date()
                
                # Processar diferentes períodos do dia
                periods = {
                    'morning': day_data,
                    'afternoon': day_data,
                    'night': day_data
                }
                
                for period, period_data in periods.items():
                    # Verificar se previsão já existe
                    existing_forecast = WeatherForecast.query.filter_by(
                        location_id=location_id,
                        forecast_date=forecast_date,
                        forecast_period=period
                    ).first()
                    
                    if existing_forecast:
                        # Atualizar previsão existente
                        self._update_forecast_data(existing_forecast, period_data)
                    else:
                        # Criar nova previsão
                        forecast = WeatherForecast(
                            location_id=location_id,
                            forecast_date=forecast_date,
                            forecast_period=period
                        )
                        self._update_forecast_data(forecast, period_data)
                        db.session.add(forecast)
                    
                    updated_count += 1
            
            db.session.commit()
            logger.info(f"Previsões atualizadas para {location_id}: {updated_count}")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Erro ao processar previsões para {location_id}: {e}")
            db.session.rollback()
            return 0
    
    def _update_forecast_data(self, forecast: WeatherForecast, data: Dict):
        """Atualizar dados de previsão"""
        forecast.min_temperature = self._safe_float(data.get('tMin'))
        forecast.max_temperature = self._safe_float(data.get('tMax'))
        forecast.precipitation_probability = self._safe_float(data.get('probabilidadePrecipita'))
        forecast.wind_speed = self._safe_float(data.get('intensidadeVento'))
        forecast.wind_direction = data.get('direcaoVento')
        forecast.weather_type = data.get('idTipoTempo')
        forecast.uv_index = self._safe_float(data.get('iUv'))
        
        # Mapear descrição do tempo
        weather_types = self._get_weather_type_mapping()
        forecast.weather_description = weather_types.get(
            forecast.weather_type, 'Condições não especificadas'
        )
        
        forecast.forecast_issued_at = datetime.utcnow()
        forecast.updated_at = datetime.utcnow()
    
    def update_weather_alerts(self) -> int:
        """Atualizar alertas meteorológicos"""
        logger.info("Atualizando alertas meteorológicos")
        
        data = self._make_request("forecast/warnings/warnings_www.json")
        if not data:
            logger.error("Falha ao obter alertas")
            return 0
        
        updated_count = 0
        
        try:
            # Marcar todos os alertas como inativos primeiro
            WeatherAlert.query.update({'is_active': False})
            
            alerts_data = data.get('data', [])
            
            for alert_data in alerts_data:
                ipma_id = alert_data.get('idAreaAviso')
                if not ipma_id:
                    continue
                
                # Verificar se alerta já existe
                alert = WeatherAlert.query.filter_by(ipma_id=ipma_id).first()
                
                if not alert:
                    alert = WeatherAlert(ipma_id=ipma_id)
                    db.session.add(alert)
                
                # Atualizar dados do alerta
                alert.district = alert_data.get('local')
                alert.phenomenon = alert_data.get('idFenomeno')
                alert.severity = alert_data.get('idNivelAviso')
                alert.awareness_level = alert_data.get('awarenessTypeName')
                alert.title = alert_data.get('text')
                alert.description = alert_data.get('descFenomeno')
                
                # Processar datas
                start_time_str = alert_data.get('startTime')
                end_time_str = alert_data.get('endTime')
                
                if start_time_str:
                    alert.start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                if end_time_str:
                    alert.end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                
                alert.is_active = True
                alert.issued_at = datetime.utcnow()
                alert.updated_at = datetime.utcnow()
                
                updated_count += 1
            
            db.session.commit()
            logger.info(f"Alertas atualizados: {updated_count}")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Erro ao processar alertas: {e}")
            db.session.rollback()
            return 0
    
    def get_weather_for_location(self, latitude: float, longitude: float) -> Dict:
        """Obter dados climáticos para localização específica"""
        try:
            # Encontrar estação mais próxima
            nearest_station = self._find_nearest_station(latitude, longitude)
            
            # Encontrar mapeamento de localização
            location_mapping = self._find_location_mapping(latitude, longitude)
            
            result = {
                'current': None,
                'forecast': [],
                'alerts': [],
                'station': None,
                'location': None
            }
            
            # Dados atuais da estação mais próxima
            if nearest_station:
                latest_observation = WeatherObservation.query.filter_by(
                    station_id=nearest_station.id
                ).order_by(WeatherObservation.observation_time.desc()).first()
                
                if latest_observation:
                    result['current'] = latest_observation.to_dict()
                    result['station'] = {
                        'name': nearest_station.name,
                        'distance': self._calculate_distance(
                            latitude, longitude,
                            nearest_station.latitude, nearest_station.longitude
                        )
                    }
            
            # Previsões
            if location_mapping and location_mapping.ipma_location_id:
                forecasts = WeatherForecast.query.filter_by(
                    location_id=location_mapping.ipma_location_id
                ).filter(
                    WeatherForecast.forecast_date >= date.today()
                ).order_by(WeatherForecast.forecast_date).limit(7).all()
                
                result['forecast'] = [f.to_dict() for f in forecasts]
                result['location'] = {
                    'district': location_mapping.district,
                    'municipality': location_mapping.municipality
                }
            
            # Alertas ativos para a região
            if location_mapping:
                alerts = WeatherAlert.query.filter(
                    WeatherAlert.is_active == True,
                    WeatherAlert.district == location_mapping.district
                ).all()
                
                result['alerts'] = [a.to_dict() for a in alerts if a.is_current]
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter dados climáticos para {latitude}, {longitude}: {e}")
            return {}
    
    def _find_nearest_station(self, latitude: float, longitude: float) -> Optional[WeatherStation]:
        """Encontrar estação meteorológica mais próxima"""
        stations = WeatherStation.query.filter_by(is_active=True).all()
        
        if not stations:
            return None
        
        nearest_station = None
        min_distance = float('inf')
        
        for station in stations:
            distance = self._calculate_distance(
                latitude, longitude,
                station.latitude, station.longitude
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        
        return nearest_station
    
    def _find_location_mapping(self, latitude: float, longitude: float) -> Optional[LocationMapping]:
        """Encontrar mapeamento de localização mais próximo"""
        mappings = LocationMapping.query.all()
        
        if not mappings:
            return None
        
        nearest_mapping = None
        min_distance = float('inf')
        
        for mapping in mappings:
            if mapping.latitude and mapping.longitude:
                distance = self._calculate_distance(
                    latitude, longitude,
                    mapping.latitude, mapping.longitude
                )
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_mapping = mapping
        
        return nearest_mapping
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcular distância entre duas coordenadas (fórmula de Haversine)"""
        # Converter para radianos
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Raio da Terra em km
        r = 6371
        
        return c * r
    
    def _safe_float(self, value) -> Optional[float]:
        """Converter valor para float de forma segura"""
        if value is None or value == '':
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _calculate_dew_point(self, temperature: float, humidity: float) -> float:
        """Calcular ponto de orvalho"""
        # Fórmula aproximada de Magnus
        a = 17.27
        b = 237.7
        
        alpha = ((a * temperature) / (b + temperature)) + (humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return round(dew_point, 1)
    
    def _calculate_feels_like(self, temperature: float, humidity: float, wind_speed: float) -> float:
        """Calcular sensação térmica"""
        # Fórmula simplificada de heat index
        if temperature >= 27:
            # Heat index para temperaturas altas
            hi = -42.379 + 2.04901523 * temperature + 10.14333127 * humidity
            hi -= 0.22475541 * temperature * humidity
            hi -= 0.00683783 * temperature * temperature
            hi -= 0.05481717 * humidity * humidity
            hi += 0.00122874 * temperature * temperature * humidity
            hi += 0.00085282 * temperature * humidity * humidity
            hi -= 0.00000199 * temperature * temperature * humidity * humidity
            
            return round(hi, 1)
        
        elif temperature <= 10 and wind_speed > 4.8:
            # Wind chill para temperaturas baixas
            wc = 13.12 + 0.6215 * temperature
            wc -= 11.37 * (wind_speed ** 0.16)
            wc += 0.3965 * temperature * (wind_speed ** 0.16)
            
            return round(wc, 1)
        
        else:
            # Temperatura normal
            return temperature
    
    def _get_weather_type_mapping(self) -> Dict[str, str]:
        """Mapeamento de tipos de tempo do IPMA"""
        return {
            '1': 'Céu limpo',
            '2': 'Céu pouco nublado',
            '3': 'Céu parcialmente nublado',
            '4': 'Céu muito nublado',
            '5': 'Céu nublado',
            '6': 'Aguaceiros fracos',
            '7': 'Aguaceiros',
            '8': 'Aguaceiros fortes',
            '9': 'Chuva fraca',
            '10': 'Chuva',
            '11': 'Chuva forte',
            '12': 'Período de chuva',
            '13': 'Chuva fraca/Aguaceiros fracos',
            '14': 'Chuva/Aguaceiros',
            '15': 'Chuva forte/Aguaceiros fortes',
            '16': 'Trovoada',
            '17': 'Aguaceiros/Trovoada',
            '18': 'Chuva/Trovoada',
            '19': 'Neve',
            '20': 'Aguaceiros de neve',
            '21': 'Chuva/Neve',
            '22': 'Nevoeiro',
            '23': 'Nevoeiro',
            '24': 'Céu limpo',
            '25': 'Céu pouco nublado',
            '26': 'Céu parcialmente nublado',
            '27': 'Céu muito nublado'
        }
    
    def initialize_location_mappings(self):
        """Inicializar mapeamentos de localização básicos"""
        logger.info("Inicializando mapeamentos de localização")
        
        # Distritos principais de Portugal com IDs do IPMA
        districts_data = [
            {'district': 'Aveiro', 'ipma_id': '1010500', 'lat': 40.6443, 'lng': -8.6455},
            {'district': 'Beja', 'ipma_id': '1020500', 'lat': 38.0150, 'lng': -7.8650},
            {'district': 'Braga', 'ipma_id': '1030300', 'lat': 41.5454, 'lng': -8.4265},
            {'district': 'Bragança', 'ipma_id': '1040200', 'lat': 41.8071, 'lng': -6.7570},
            {'district': 'Castelo Branco', 'ipma_id': '1050200', 'lat': 39.8221, 'lng': -7.4909},
            {'district': 'Coimbra', 'ipma_id': '1060300', 'lat': 40.2033, 'lng': -8.4103},
            {'district': 'Évora', 'ipma_id': '1070500', 'lat': 38.5667, 'lng': -7.9000},
            {'district': 'Faro', 'ipma_id': '1080500', 'lat': 37.0194, 'lng': -7.9322},
            {'district': 'Guarda', 'ipma_id': '1090700', 'lat': 40.5364, 'lng': -7.2683},
            {'district': 'Leiria', 'ipma_id': '1100900', 'lat': 39.7436, 'lng': -8.8071},
            {'district': 'Lisboa', 'ipma_id': '1110600', 'lat': 38.7223, 'lng': -9.1393},
            {'district': 'Portalegre', 'ipma_id': '1121400', 'lat': 39.2967, 'lng': -7.4281},
            {'district': 'Porto', 'ipma_id': '1131200', 'lat': 41.1579, 'lng': -8.6291},
            {'district': 'Santarém', 'ipma_id': '1141600', 'lat': 39.2369, 'lng': -8.6867},
            {'district': 'Setúbal', 'ipma_id': '1151200', 'lat': 38.5244, 'lng': -8.8882},
            {'district': 'Viana do Castelo', 'ipma_id': '1160900', 'lat': 41.6947, 'lng': -8.8314},
            {'district': 'Vila Real', 'ipma_id': '1171400', 'lat': 41.3006, 'lng': -7.7441},
            {'district': 'Viseu', 'ipma_id': '1182300', 'lat': 40.6566, 'lng': -7.9122}
        ]
        
        created_count = 0
        
        for district_data in districts_data:
            existing = LocationMapping.query.filter_by(
                district=district_data['district']
            ).first()
            
            if not existing:
                mapping = LocationMapping(
                    district=district_data['district'],
                    ipma_location_id=district_data['ipma_id'],
                    latitude=district_data['lat'],
                    longitude=district_data['lng']
                )
                
                db.session.add(mapping)
                created_count += 1
        
        db.session.commit()
        logger.info(f"Mapeamentos de localização criados: {created_count}")
        
        return created_count
```

### Testes de Validação

**TESTE 1: Integração Básica**
```python
# Teste no console Python
from app.services.ipma_service import IPMAService

ipma = IPMAService()

# Testar conexão
stations = ipma.update_weather_stations()
print(f"Estações atualizadas: {stations}")

# Testar observações
observations = ipma.update_weather_observations()
print(f"Observações atualizadas: {observations}")

# Testar dados para localização
weather_data = ipma.get_weather_for_location(38.7223, -9.1393)  # Lisboa
print(f"Dados climáticos: {weather_data}")
```

**TESTE 2: Validação de Dados**
```python
# Verificar qualidade dos dados
from app.models.weather import WeatherObservation

recent_obs = WeatherObservation.query.order_by(
    WeatherObservation.observation_time.desc()
).limit(10).all()

for obs in recent_obs:
    print(f"Estação: {obs.station.name}")
    print(f"Temperatura: {obs.temperature}°C")
    print(f"Umidade: {obs.humidity}%")
    print("---")
```

### Critérios de Aceitação
- Integração com APIs do IPMA funcionando
- Dados climáticos sendo coletados e armazenados
- Previsões atualizadas regularmente
- Alertas meteorológicos sincronizados
- Performance adequada (< 30 segundos para atualização completa)
- Tratamento robusto de erros
- Cache implementado adequadamente

### Entregáveis Esperados
1. **Modelos de Dados** completos para dados climáticos
2. **IPMAService** funcional com todas as integrações
3. **Mapeamentos de Localização** para Portugal
4. **Sistema de Cache** implementado
5. **Testes de Validação** executados com sucesso

### Informações Importantes
- Respeitar rate limits das APIs do IPMA
- Implementar fallback para falhas de conexão
- Considerar fuso horário português (UTC+0/+1)
- Otimizar queries de banco para performance
- Preparar para integração com sistema de alertas



---

## 🧠 PROMPT 3: SISTEMA DE RECOMENDAÇÕES IA

### Contexto do Projeto
Você está implementando o coração do AgroTech Portugal: o sistema de recomendações de Inteligência Artificial. Este sistema utilizará dados climáticos, de culturas e de mercado para fornecer recomendações personalizadas e proativas aos agricultores, aumentando a eficiência e a produtividade.

### Funcionalidade a Implementar
Sistema completo de recomendações de IA que analisa dados em tempo real e fornece insights sobre:
- **Melhor época para plantio e colheita**
- **Necessidades de irrigação e adubação**
- **Prevenção de pragas e doenças**
- **Otimização de tratamentos fitossanitários**
- **Oportunidades de mercado**

### Arquitetura Proposta

O sistema de IA será modular, com os seguintes componentes:

**Componentes Principais:**
- **IA Engine**: Motor principal de processamento de IA
- **Data Aggregator**: Agregador de dados de diferentes fontes
- **Recommendation Models**: Modelos de IA para diferentes tipos de recomendação
- **Personalization Layer**: Camada de personalização para cada usuário
- **Feedback Loop**: Sistema para capturar feedback e treinar modelos

**Fluxo de Dados:**
1. Dados (clima, culturas, mercado) → Data Aggregator
2. Data Aggregator → IA Engine
3. IA Engine → Recommendation Models (processamento)
4. Recommendation Models → Personalization Layer
5. Personalization Layer → Recomendações para usuário
6. Usuário → Feedback Loop → IA Engine (retreinamento)

### Objetivo
Implementar sistema de IA robusto e inteligente que forneça recomendações acionáveis e personalizadas, tornando-se o principal diferencial competitivo do AgroTech Portugal e uma ferramenta indispensável para os agricultores.

### Instruções Detalhadas

**ETAPA 1: Modelos de Dados para IA**

Crie os modelos em `app/models/ai.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum
import json

db = SQLAlchemy()

class RecommendationType(Enum):
    """Tipos de recomendações de IA"""
    PLANTING = "planting"          # Plantio
    HARVEST = "harvest"            # Colheita
    IRRIGATION = "irrigation"      # Irrigação
    FERTILIZATION = "fertilization"  # Adubação
    PEST_CONTROL = "pest_control"    # Controle de pragas
    DISEASE_CONTROL = "disease_control" # Controle de doenças
    MARKET_OPPORTUNITY = "market_opportunity" # Oportunidade de mercado
    SOIL_MANAGEMENT = "soil_management" # Manejo do solo
    GENERAL_ADVICE = "general_advice" # Conselho geral

class RecommendationStatus(Enum):
    """Status das recomendações"""
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Recommendation(db.Model):
    """Modelo principal de recomendações de IA"""
    __tablename__ = "recommendations"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Classificação da recomendação
    type = db.Column(db.Enum(RecommendationType), nullable=False)
    status = db.Column(db.Enum(RecommendationStatus), default=RecommendationStatus.ACTIVE)
    
    # Conteúdo da recomendação
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # JSON com detalhes técnicos
    justification = db.Column(db.Text) # Explicação da IA
    
    # Ações sugeridas
    action_text = db.Column(db.String(100))
    action_url = db.Column(db.String(500))
    
    # Dados contextuais
    culture_id = db.Column(db.Integer, db.ForeignKey("cultures.id"))
    confidence_score = db.Column(db.Float) # Score de confiança da IA (0-1)
    potential_impact = db.Column(db.String(50)) # baixo, médio, alto
    
    # Controle temporal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Feedback do usuário
    feedback_rating = db.Column(db.Integer) # 1-5 estrelas
    feedback_comment = db.Column(db.Text)
    feedback_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship("User", backref="recommendations")
    culture = db.relationship("Culture", backref="recommendations")
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "title": self.title,
            "summary": self.summary,
            "details": json.loads(self.details) if self.details else {},
            "justification": self.justification,
            "action_text": self.action_text,
            "action_url": self.action_url,
            "culture_id": self.culture_id,
            "confidence_score": self.confidence_score,
            "potential_impact": self.potential_impact,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    def accept(self):
        """Marcar recomendação como aceita"""
        self.status = RecommendationStatus.ACCEPTED
    
    def reject(self):
        """Marcar recomendação como rejeitada"""
        self.status = RecommendationStatus.REJECTED
    
    def provide_feedback(self, rating: int, comment: str = None):
        """Registrar feedback do usuário"""
        self.feedback_rating = rating
        self.feedback_comment = comment
        self.feedback_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Recommendation {self.id}: {self.title}>"

class AIModel(db.Model):
    """Modelos de IA utilizados no sistema"""
    __tablename__ = "ai_models"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    
    # Configuração do modelo
    model_type = db.Column(db.String(50)) # e.g., RandomForest, NeuralNetwork, LLM
    parameters = db.Column(db.Text) # JSON com parâmetros
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_trained_at = db.Column(db.DateTime)
    
    # Métricas de performance
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIModel {self.name} v{self.version}>"
```

**ETAPA 2: Motor de IA (IA Engine)**

Crie o motor principal em `app/services/ai_engine.py`:

```python
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.models.ai import Recommendation, RecommendationType, AIModel, db
from app.models import User, Culture
from app.services.weather_service import IPMAService
from app.services.market_service import MarketService
import logging
import json

logger = logging.getLogger(__name__)

class AIEngine:
    """Motor principal de processamento de IA"""
    
    def __init__(self):
        self.weather_service = IPMAService()
        self.market_service = MarketService()
    
    def generate_recommendations_for_user(self, user: User):
        """Gerar todas as recomendações para um usuário"""
        logger.info(f"Gerando recomendações para usuário {user.id}")
        
        try:
            context = self._build_user_context(user)
            
            # Gerar recomendações para cada cultura
            for culture in user.cultures:
                culture_context = self._build_culture_context(culture, context)
                
                self._generate_planting_recommendations(user, culture, culture_context)
                self._generate_irrigation_recommendations(user, culture, culture_context)
                self._generate_pest_disease_recommendations(user, culture, culture_context)
                self._generate_harvest_recommendations(user, culture, culture_context)
            
            # Gerar recomendações de mercado
            self._generate_market_recommendations(user, context)
            
            logger.info(f"Recomendações geradas para usuário {user.id}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações para usuário {user.id}: {e}", exc_info=True)
    
    def _build_user_context(self, user: User) -> Dict[str, Any]:
        """Construir contexto do usuário para IA"""
        weather_data = self.weather_service.get_weather_for_location(
            user.location_lat, user.location_lng
        )
        
        return {
            "user": {
                "id": user.id,
                "experiencia": user.experiencia,
                "tipo_produtor": user.tipo_produtor,
                "interesses": user.get_interesses_list()
            },
            "location": {
                "lat": user.location_lat,
                "lng": user.location_lng,
                "district": user.location_district
            },
            "weather": weather_data,
            "datetime": {
                "now": datetime.utcnow()
            }
        }
    
    def _build_culture_context(self, culture: Culture, user_context: Dict) -> Dict[str, Any]:
        """Construir contexto da cultura"""
        culture_context = user_context.copy()
        culture_context["culture"] = {
            "id": culture.id,
            "name": culture.name,
            "type": culture.type,
            "area": culture.area,
            "planting_date": culture.planting_date,
            "status": culture.status,
            "soil_type": culture.soil_type
        }
        return culture_context
    
    def _generate_planting_recommendations(self, user: User, culture: Culture, context: Dict):
        """Gerar recomendações de plantio"""
        # Lógica de IA para plantio
        # Exemplo: verificar se está na época ideal para a cultura e região
        
        # Exemplo simples
        if culture.status == "planning" and context["datetime"]["now"].month in [3, 4]:
            self._create_recommendation(
                user_id=user.id,
                culture_id=culture.id,
                type=RecommendationType.PLANTING,
                title=f"Época Ideal para Plantar {culture.name}",
                summary="As condições climáticas atuais são favoráveis para o plantio.",
                justification="A temperatura e umidade do solo estão nos níveis ideais para germinação.",
                confidence_score=0.85,
                potential_impact="alto"
            )
    
    def _generate_irrigation_recommendations(self, user: User, culture: Culture, context: Dict):
        """Gerar recomendações de irrigação"""
        # Lógica de IA para irrigação
        # Exemplo: verificar dias sem chuva e evapotranspiração
        
        weather = context.get("weather", {})
        current_weather = weather.get("current", {})
        
        if (current_weather and 
            current_weather.get("days_without_rain", 0) > 5 and
            current_weather.get("temperature", 0) > 25):
            
            self._create_recommendation(
                user_id=user.id,
                culture_id=culture.id,
                type=RecommendationType.IRRIGATION,
                title="Necessidade de Irrigação Urgente",
                summary=f"Sua cultura de {culture.name} pode estar sofrendo com a falta de água.",
                justification="Não chove há mais de 5 dias e as temperaturas estão altas, aumentando a evapotranspiração.",
                confidence_score=0.9,
                potential_impact="alto"
            )
    
    def _generate_pest_disease_recommendations(self, user: User, culture: Culture, context: Dict):
        """Gerar recomendações de controle de pragas e doenças"""
        # Lógica de IA para pragas e doenças
        # Exemplo: usar dados climáticos para prever risco
        
        weather = context.get("weather", {})
        current_weather = weather.get("current", {})
        
        if (current_weather and 
            current_weather.get("humidity", 0) > 80 and
            15 < current_weather.get("temperature", 0) < 25):
            
            self._create_recommendation(
                user_id=user.id,
                culture_id=culture.id,
                type=RecommendationType.DISEASE_CONTROL,
                title="Risco Elevado de Míldio",
                summary=f"As condições climáticas são favoráveis ao desenvolvimento de míldio em sua cultura de {culture.name}.",
                justification="Alta umidade e temperaturas amenas criam o ambiente perfeito para o fungo. Inspecione suas plantas e considere tratamento preventivo.",
                confidence_score=0.8,
                potential_impact="alto"
            )
    
    def _generate_harvest_recommendations(self, user: User, culture: Culture, context: Dict):
        """Gerar recomendações de colheita"""
        # Lógica de IA para colheita
        # Exemplo: verificar tempo desde o plantio e condições climáticas
        
        if culture.planting_date:
            days_since_planting = (context["datetime"]["now"].date() - culture.planting_date).days
            
            # Exemplo para uma cultura de 90 dias
            if 85 < days_since_planting < 100:
                self._create_recommendation(
                    user_id=user.id,
                    culture_id=culture.id,
                    type=RecommendationType.HARVEST,
                    title=f"Época de Colheita para {culture.name}",
                    summary="Sua cultura está se aproximando do ponto ideal de colheita.",
                    justification=f"Passaram-se {days_since_planting} dias desde o plantio. Verifique a maturação e planeje a colheita.",
                    confidence_score=0.75,
                    potential_impact="médio"
                )
    
    def _generate_market_recommendations(self, user: User, context: Dict):
        """Gerar recomendações de mercado"""
        # Lógica de IA para mercado
        # Exemplo: usar dados de mercado para identificar oportunidades
        
        market_data = self.market_service.get_market_trends()
        
        for trend in market_data:
            if trend["product"] in user.get_interesses_list() and trend["trend"] == "up":
                self._create_recommendation(
                    user_id=user.id,
                    type=RecommendationType.MARKET_OPPORTUNITY,
                    title=f"Oportunidade de Mercado: {trend["product"]}",
                    summary=f"O preço de {trend["product"]} está em alta no mercado.",
                    justification=f"Dados recentes mostram um aumento de {trend["change_pct"]}% no preço. Considere vender sua produção agora.",
                    confidence_score=0.9,
                    potential_impact="alto"
                )
    
    def _create_recommendation(self, **kwargs):
        """Criar e salvar uma nova recomendação"""
        try:
            # Verificar se recomendação similar já existe e está ativa
            existing_rec = Recommendation.query.filter_by(
                user_id=kwargs["user_id"],
                culture_id=kwargs.get("culture_id"),
                type=kwargs["type"],
                status=RecommendationStatus.ACTIVE
            ).first()
            
            if existing_rec:
                logger.info(f"Recomendação similar já existe: {existing_rec.id}")
                return
            
            # Criar nova recomendação
            recommendation = Recommendation(**kwargs)
            
            db.session.add(recommendation)
            db.session.commit()
            
            logger.info(f"Recomendação criada: {recommendation.id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar recomendação: {e}")
            db.session.rollback()
    
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[Recommendation]:
        """Obter recomendações ativas para um usuário"""
        return Recommendation.query.filter_by(
            user_id=user_id,
            status=RecommendationStatus.ACTIVE
        ).order_by(Recommendation.created_at.desc()).limit(limit).all()
    
    def record_feedback(self, recommendation_id: int, user_id: int, 
                      rating: int, comment: str = None) -> bool:
        """Registrar feedback do usuário em uma recomendação"""
        recommendation = Recommendation.query.filter_by(
            id=recommendation_id,
            user_id=user_id
        ).first()
        
        if recommendation:
            recommendation.provide_feedback(rating, comment)
            db.session.commit()
            logger.info(f"Feedback registrado para recomendação {recommendation_id}")
            return True
        
        return False
```

**ETAPA 3: Serviço de Mercado**

Crie um serviço mock para dados de mercado em `app/services/market_service.py`:

```python
import random

class MarketService:
    """Serviço para obter dados de mercado (mock)"""
    
    def get_market_trends(self) -> list:
        """Obter tendências de mercado (mock)"""
        products = ["cereais", "horticultura", "fruticultura", "olivicultura", "viticultura"]
        trends = []
        
        for product in products:
            trends.append({
                "product": product,
                "trend": random.choice(["up", "down", "stable"]),
                "change_pct": round(random.uniform(-5.0, 5.0), 2)
            })
        
        return trends
```

### Testes de Validação

**TESTE 1: Geração de Recomendações**
```python
# Teste no console Python
from app.services.ai_engine import AIEngine
from app.models import User

engine = AIEngine()
user = User.query.get(1)

engine.generate_recommendations_for_user(user)

recommendations = engine.get_user_recommendations(user.id)
print(f"Recomendações geradas: {len(recommendations)}")

for rec in recommendations:
    print(f"- {rec.title}")
```

**TESTE 2: Feedback do Usuário**
```python
# Teste no console Python
rec_id = recommendations[0].id

engine.record_feedback(rec_id, user.id, 5, "Ótima recomendação!")

rec = Recommendation.query.get(rec_id)
print(f"Feedback: {rec.feedback_rating} estrelas, {rec.feedback_comment}")
```

### Critérios de Aceitação
- Sistema de IA gera recomendações relevantes
- Recomendações são personalizadas para cada usuário e cultura
- Integração com dados climáticos e de mercado funcionando
- Sistema de feedback implementado e funcional
- Performance adequada (< 10 segundos para gerar recomendações para um usuário)
- Logs detalhados para debugging e auditoria

### Entregáveis Esperados
1. **Modelos de Dados** completos para IA
2. **AIEngine** funcional com lógica de recomendação
3. **Serviço de Mercado** (mock) implementado
4. **Integração** com serviços de clima e usuário
5. **Testes de Validação** executados com sucesso

### Informações Importantes
- Começar com lógica simples e expandir
- Focar na personalização e relevância para Portugal
- Implementar sistema de feedback desde o início
- Considerar explicabilidade da IA (justificativas)
- Preparar para modelos mais complexos no futuro

---

## 🌿 PROMPT 4: GESTÃO DE CULTURAS

### Contexto do Projeto
Você está implementando a funcionalidade de Gestão de Culturas para o AgroTech Portugal. Esta é a interface principal onde os agricultores irão registrar, monitorar e gerenciar suas culturas, recebendo alertas e recomendações personalizadas.

### Funcionalidade a Implementar
Sistema completo de CRUD (Create, Read, Update, Delete) para culturas, permitindo que usuários registrem diferentes tipos de culturas (anuais, perenes, etc.), monitorem seu progresso e visualizem dados relevantes. A interface deve ser intuitiva e fácil de usar, seguindo um formato de wizard para criação de novas culturas.

### Arquitetura Proposta

**Componentes Principais:**
- **Culture Models**: Modelos de dados para culturas e seus ciclos
- **Culture Service**: Lógica de negócio para gestão de culturas
- **Culture Controller**: Rotas e endpoints para interface web
- **Culture Views**: Templates HTML para visualização e edição
- **Culture Wizard**: Interface passo-a-passo para criação de culturas

### Objetivo
Implementar sistema de gestão de culturas robusto e intuitivo que permita aos agricultores portugueses gerenciar facilmente suas atividades agrícolas, fornecendo uma base sólida para alertas e recomendações de IA.

### Instruções Detalhadas

**ETAPA 1: Modelos de Dados para Culturas**

Crie os modelos em `app/models/cultures.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from enum import Enum

db = SQLAlchemy()

class CultureType(Enum):
    """Tipos de culturas"""
    ANNUAL = "annual"          # Anual (e.g., milho, trigo)
    PERENNIAL = "perennial"      # Perene (e.g., oliveiras, vinhas)
    HORTICULTURE = "horticulture" # Hortaliças
    FRUIT_TREE = "fruit_tree"    # Árvores de fruto
    VINEYARD = "vineyard"        # Vinha
    OLIVE_GROVE = "olive_grove"  # Olival

class CultureStatus(Enum):
    """Status do ciclo da cultura"""
    PLANNING = "planning"
    PLANTED = "planted"
    GROWING = "growing"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    HARVESTING = "harvesting"
    COMPLETED = "completed"
    DORMANT = "dormant"

class Culture(db.Model):
    """Modelo principal de culturas"""
    __tablename__ = "cultures"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Informações básicas
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(CultureType), nullable=False)
    variety = db.Column(db.String(100)) # Variedade específica
    
    # Localização e área
    area = db.Column(db.Float) # em hectares
    location_polygon = db.Column(db.Text) # JSON com polígono da área
    
    # Datas importantes
    planting_date = db.Column(db.Date)
    expected_harvest_date = db.Column(db.Date)
    actual_harvest_date = db.Column(db.Date)
    
    # Status e ciclo
    status = db.Column(db.Enum(CultureStatus), default=CultureStatus.PLANNING)
    cycle_duration_days = db.Column(db.Integer) # Duração esperada do ciclo
    
    # Características do solo
    soil_type = db.Column(db.String(50)) # argiloso, arenoso, etc.
    soil_ph = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship("User", backref="cultures")
    activities = db.relationship("CultureActivity", backref="culture", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "variety": self.variety,
            "area": self.area,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "status": self.status.value
        }
    
    def get_current_stage(self) -> str:
        """Calcular estágio atual do ciclo"""
        if not self.planting_date or not self.cycle_duration_days:
            return self.status.value
        
        days_since_planting = (date.today() - self.planting_date).days
        progress_pct = (days_since_planting / self.cycle_duration_days) * 100
        
        if progress_pct < 20:
            return "Germinação/Crescimento Inicial"
        elif progress_pct < 50:
            return "Crescimento Vegetativo"
        elif progress_pct < 75:
            return "Floração/Frutificação"
        elif progress_pct < 100:
            return "Maturação"
        else:
            return "Pronto para Colheita"
    
    def __repr__(self):
        return f"<Culture {self.id}: {self.name}>"

class ActivityType(Enum):
    """Tipos de atividades agrícolas"""
    PLANTING = "planting"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PEST_CONTROL = "pest_control"
    DISEASE_CONTROL = "disease_control"
    PRUNING = "pruning"
    HARVEST = "harvest"
    SOIL_PREP = "soil_prep"
    MONITORING = "monitoring"

class CultureActivity(db.Model):
    """Registro de atividades em uma cultura"""
    __tablename__ = "culture_activities"
    
    id = db.Column(db.Integer, primary_key=True)
    culture_id = db.Column(db.Integer, db.ForeignKey("cultures.id"), nullable=False)
    
    # Tipo de atividade
    type = db.Column(db.Enum(ActivityType), nullable=False)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Detalhes da atividade
    description = db.Column(db.Text)
    products_used = db.Column(db.Text) # JSON com produtos e quantidades
    cost = db.Column(db.Float)
    
    # Status
    is_completed = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "activity_date": self.activity_date.isoformat(),
            "description": self.description,
            "products_used": json.loads(self.products_used) if self.products_used else {},
            "cost": self.cost
        }
    
    def __repr__(self):
        return f"<CultureActivity {self.id}: {self.type.value}>"
```

**ETAPA 2: Serviço de Gestão de Culturas**

Crie o serviço em `app/services/culture_service.py`:

```python
from typing import List, Dict, Any, Optional
from app.models.cultures import Culture, CultureActivity, CultureType, CultureStatus, ActivityType, db
from app.models import User
from datetime import datetime
import json

class CultureService:
    """Serviço para lógica de negócio de culturas"""
    
    def create_culture(self, user_id: int, data: Dict) -> Culture:
        """Criar nova cultura"""
        culture = Culture(
            user_id=user_id,
            name=data["name"],
            type=CultureType(data["type"]),
            variety=data.get("variety"),
            area=data.get("area"),
            planting_date=datetime.strptime(data["planting_date"], "%Y-%m-%d").date() if data.get("planting_date") else None,
            status=CultureStatus.PLANNING
        )
        
        db.session.add(culture)
        db.session.commit()
        
        return culture
    
    def get_user_cultures(self, user_id: int) -> List[Culture]:
        """Obter todas as culturas de um usuário"""
        return Culture.query.filter_by(user_id=user_id).all()
    
    def get_culture_by_id(self, culture_id: int, user_id: int) -> Optional[Culture]:
        """Obter cultura por ID"""
        return Culture.query.filter_by(id=culture_id, user_id=user_id).first()
    
    def update_culture(self, culture: Culture, data: Dict) -> Culture:
        """Atualizar dados de uma cultura"""
        for key, value in data.items():
            if hasattr(culture, key):
                setattr(culture, key, value)
        
        db.session.commit()
        return culture
    
    def delete_culture(self, culture: Culture):
        """Deletar uma cultura"""
        db.session.delete(culture)
        db.session.commit()
    
    def add_activity(self, culture_id: int, data: Dict) -> CultureActivity:
        """Adicionar atividade a uma cultura"""
        activity = CultureActivity(
            culture_id=culture_id,
            type=ActivityType(data["type"]),
            description=data.get("description"),
            products_used=json.dumps(data.get("products_used", {})),
            cost=data.get("cost")
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return activity
    
    def get_culture_activities(self, culture_id: int) -> List[CultureActivity]:
        """Obter atividades de uma cultura"""
        return CultureActivity.query.filter_by(culture_id=culture_id).order_by(
            CultureActivity.activity_date.desc()
        ).all()
```

**ETAPA 3: Rotas e Views**

Crie as rotas em `app/routes/cultures.py` e os templates correspondentes:

```python
# app/routes/cultures.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.culture_service import CultureService

bp = Blueprint("cultures", __name__, url_prefix="/cultures")
culture_service = CultureService()

@bp.route("/")
@login_required
def index():
    cultures = culture_service.get_user_cultures(current_user.id)
    return render_template("cultures/index.html", cultures=cultures)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_culture():
    if request.method == "POST":
        data = request.form.to_dict()
        culture = culture_service.create_culture(current_user.id, data)
        flash(f"Cultura ", "success")
        return redirect(url_for("cultures.view_culture", culture_id=culture.id))
    
    return render_template("cultures/new_wizard.html")

@bp.route("/<int:culture_id>")
@login_required
def view_culture(culture_id):
    culture = culture_service.get_culture_by_id(culture_id, current_user.id)
    if not culture:
        flash("Cultura não encontrada", "error")
        return redirect(url_for("cultures.index"))
    
    activities = culture_service.get_culture_activities(culture_id)
    return render_template("cultures/view.html", culture=culture, activities=activities)

# ... outras rotas para editar, deletar, adicionar atividades, etc.
```

**ETAPA 4: Wizard de Criação de Cultura**

Crie um wizard passo-a-passo em `templates/cultures/new_wizard.html`:

- **Passo 1**: Informações Básicas (Nome, Tipo, Variedade)
- **Passo 2**: Localização e Área (Mapa interativo, área em hectares)
- **Passo 3**: Datas e Ciclo (Plantio, colheita esperada)
- **Passo 4**: Características do Solo (Tipo, pH)
- **Passo 5**: Resumo e Confirmação

### Testes de Validação

**TESTE 1: CRUD de Culturas**
- Criar nova cultura usando o wizard
- Visualizar detalhes da cultura criada
- Editar informações da cultura
- Deletar a cultura

**TESTE 2: Gestão de Atividades**
- Adicionar nova atividade a uma cultura
- Visualizar histórico de atividades
- Editar uma atividade existente

### Critérios de Aceitação
- CRUD completo de culturas funcionando
- Wizard de criação de culturas intuitivo e funcional
- Gestão de atividades implementada
- Integração com sistema de usuários e alertas
- Interface responsiva e fácil de usar

### Entregáveis Esperados
1. **Modelos de Dados** completos para culturas e atividades
2. **CultureService** com toda a lógica de negócio
3. **Rotas e Views** para gestão de culturas
4. **Wizard de Criação** passo-a-passo
5. **Testes de Validação** executados com sucesso

### Informações Importantes
- Focar na usabilidade e simplicidade da interface
- Utilizar mapas interativos para localização
- Preparar para integração com dados de sensores no futuro
- Garantir que dados de culturas alimentem o sistema de IA

---

## 🛒 PROMPT 5: MARKETPLACE BÁSICO

### Contexto do Projeto
Você está implementando a versão inicial do Marketplace para o AgroTech Portugal. Esta funcionalidade permitirá que agricultores comprem e vendam produtos, insumos e serviços, criando um ecossistema completo e gerando uma nova fonte de receita para a plataforma.

### Funcionalidade a Implementar
Marketplace básico com as seguintes funcionalidades:
- **Listagem de Produtos**: Usuários podem listar produtos para venda
- **Busca e Filtros**: Encontrar produtos por categoria, localização, etc.
- **Página de Produto**: Detalhes do produto, vendedor e contato
- **Sistema de Mensagens**: Comunicação entre comprador e vendedor

### Arquitetura Proposta

**Componentes Principais:**
- **Product Models**: Modelos de dados para produtos, categorias, etc.
- **Marketplace Service**: Lógica de negócio para o marketplace
- **Marketplace Controller**: Rotas e endpoints para a interface
- **Messaging Service**: Sistema de mensagens internas

### Objetivo
Implementar um marketplace funcional e seguro que conecte agricultores portugueses, facilitando o comércio de produtos agrícolas e insumos, e estabelecendo a base para futuras funcionalidades de e-commerce.

### Instruções Detalhadas

**ETAPA 1: Modelos de Dados para Marketplace**

Crie os modelos em `app/models/marketplace.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("product_categories.id"))
    parent = db.relationship("ProductCategory", remote_side=[id])

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id"), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20)) # kg, litro, unidade, etc.
    quantity_available = db.Column(db.Float)
    
    location_district = db.Column(db.String(50))
    location_municipality = db.Column(db.String(50))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="products")
    category = db.relationship("ProductCategory", backref="products")

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    
    subject = db.Column(db.String(200))
    body = db.Column(db.Text, nullable=False)
    
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    product = db.relationship("Product")
```

**ETAPA 2: Serviço de Marketplace**

Crie o serviço em `app/services/marketplace_service.py`:

```python
from typing import List, Dict, Optional
from app.models.marketplace import Product, ProductCategory, Message, db
from app.models import User

class MarketplaceService:
    def create_product(self, user_id: int, data: Dict) -> Product:
        # ... lógica para criar produto
        pass
    
    def search_products(self, query: str, category_id: int = None, 
                        location: str = None) -> List[Product]:
        # ... lógica para buscar produtos
        pass
    
    def send_message(self, sender_id: int, recipient_id: int, 
                     product_id: int, body: str) -> Message:
        # ... lógica para enviar mensagem
        pass
```

**ETAPA 3: Rotas e Views**

Crie as rotas em `app/routes/marketplace.py` e os templates:

- `/marketplace`: Página principal com listagem de produtos
- `/marketplace/new`: Formulário para criar novo produto
- `/marketplace/product/<int:product_id>`: Página de detalhes do produto
- `/marketplace/messages`: Caixa de entrada de mensagens

### Testes de Validação

- Criar, editar e deletar um produto
- Buscar produtos por nome e categoria
- Enviar e receber mensagens sobre um produto

### Critérios de Aceitação
- CRUD de produtos funcionando
- Busca e filtros implementados
- Sistema de mensagens funcional
- Interface intuitiva e segura

### Entregáveis Esperados
1. **Modelos de Dados** para marketplace
2. **MarketplaceService** com lógica de negócio
3. **Rotas e Views** para a interface
4. **Sistema de Mensagens** interno
5. **Testes de Validação** executados

### Informações Importantes
- Focar na segurança e validação de dados
- Não implementar pagamentos nesta fase
- Garantir que informações de contato não sejam públicas
- Preparar para futuras funcionalidades de avaliação e reputação

---

## 📋 RESUMO DOS PROMPTS PARA SPRINT 2

### Ordem de Execução Recomendada
1. **PROMPT 1**: Sistema de Alertas Inteligentes
2. **PROMPT 2**: Integração Climática IPMA
3. **PROMPT 3**: Sistema de Recomendações IA
4. **PROMPT 4**: Gestão de Culturas
5. **PROMPT 5**: Marketplace Básico

### Tempo Estimado Total
- **Alertas**: 16-20 horas
- **Clima**: 20-24 horas
- **IA**: 24-30 horas
- **Culturas**: 16-20 horas
- **Marketplace**: 12-16 horas
- **Total**: 88-110 horas (11-14 dias de trabalho)

### Recursos Necessários
- Acesso às APIs do IPMA
- Ambiente de desenvolvimento robusto
- Ferramentas de teste e validação

### Critérios de Sucesso
- Todas as funcionalidades core implementadas
- Sistema integrado e funcional
- Performance e segurança garantidas
- Pronto para testes com usuários beta

**Estes prompts fornecem um guia completo para implementar as funcionalidades core do AgroTech Portugal no Sprint 2, utilizando Claude Sonnet 4.**

