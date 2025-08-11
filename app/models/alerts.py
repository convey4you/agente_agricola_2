from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from enum import Enum
import json

# Import do db da aplicação
from app import db

class AlertType(Enum):
    """Tipos de alertas disponíveis"""
    WEATHER = "weather"          # Alertas climáticos
    PEST = "pest"               # Pragas
    DISEASE = "disease"         # Doenças
    IRRIGATION = "irrigation"   # Irrigação
    FERTILIZATION = "fertilization"  # Adubação
    HARVEST = "harvest"         # Colheita
    PRUNING = "pruning"         # Poda
    PLANTING = "planting"       # Oportunidades de plantio
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
    ACTIVE = "active"
    SENT = "sent"
    READ = "read"
    RESOLVED = "resolved"
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
    alert_metadata = db.Column(db.Text)       # JSON com metadados adicionais
    
    # Controle temporal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    scheduled_for = db.Column(db.DateTime)  # Para alertas agendados
    expires_at = db.Column(db.DateTime)     # Expiração do alerta
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    
    # Nível de severidade (1-5, onde 5 é mais severo)
    severity_level = db.Column(db.Integer, default=1)
    
    # Controle de envio
    delivery_channels = db.Column(db.String(100), default='web')  # web,email,sms
    retry_count = db.Column(db.Integer, default=0)
    last_retry_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', backref='alerts')
    culture = db.relationship('Culture', backref='alerts')
    
    def to_dict(self):
        """Converter alerta para dicionário"""
        
        # Buscar nome da cultura se existir
        culture_name = None
        if self.culture_id and self.culture:
            culture_name = self.culture.nome
        
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
            'culture_name': culture_name,
            'is_read': self.is_read,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'alert_metadata': json.loads(self.alert_metadata) if self.alert_metadata else {}
        }
    
    @property
    def is_expired(self):
        """Verificar se alerta expirou"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_urgent(self):
        """Verificar se alerta é urgente"""
        return self.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]
    
    @property
    def is_read(self):
        """Verificar se alerta foi lido"""
        return self.read_at is not None
    
    @property
    def is_resolved(self):
        """Verificar se alerta foi resolvido"""
        return self.status in [AlertStatus.DISMISSED, AlertStatus.RESOLVED]
    
    def mark_as_sent(self):
        """Marcar alerta como enviado"""
        self.status = AlertStatus.SENT
        self.sent_at = datetime.now(timezone.utc)
    
    def mark_as_read(self):
        """Marcar alerta como lido"""
        if self.status in [AlertStatus.PENDING, AlertStatus.SENT]:
            self.status = AlertStatus.READ
            self.read_at = datetime.now(timezone.utc)
    
    def dismiss(self):
        """Dispensar alerta"""
        self.status = AlertStatus.DISMISSED
        self.dismissed_at = datetime.now(timezone.utc)
    
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
    
    # NOVAS CONFIGURAÇÕES DE AGENDAMENTO AUTOMÁTICO
    auto_generation_enabled = db.Column(db.Boolean, default=True)  # Habilitar geração automática
    auto_frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    auto_time = db.Column(db.Time)  # Horário para gerar (padrão será definido no serviço)
    auto_weekday = db.Column(db.Integer)  # 0-6 (segunda=0, domingo=6) para frequência semanal
    auto_day_of_month = db.Column(db.Integer)  # 1-31 para frequência mensal
    last_auto_generation = db.Column(db.DateTime)  # Última vez que foi gerado automaticamente
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='alert_preferences')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'alert_type'),)
    
    def should_generate_automatically(self, current_time=None):
        """Verificar se deve gerar alertas automaticamente"""
        if not self.auto_generation_enabled or not self.is_enabled:
            return False
        
        current_time = current_time or datetime.now()
        
        # Verificar se já foi gerado hoje/período
        if self.last_auto_generation:
            if self.auto_frequency == 'daily':
                # Se já gerou hoje, não gerar novamente
                if self.last_auto_generation.date() >= current_time.date():
                    return False
            elif self.auto_frequency == 'weekly':
                # Se gerou esta semana, não gerar novamente
                days_since_last = (current_time - self.last_auto_generation).days
                if days_since_last < 7:
                    return False
            elif self.auto_frequency == 'monthly':
                # Se gerou este mês, não gerar novamente
                if (self.last_auto_generation.year == current_time.year and 
                    self.last_auto_generation.month == current_time.month):
                    return False
        
        # Verificar horário
        default_time = datetime.strptime('08:00', '%H:%M').time()
        target_time = self.auto_time or default_time
        if current_time.time() < target_time:
            return False
        
        # Verificar dia da semana para frequência semanal
        if self.auto_frequency == 'weekly' and self.auto_weekday is not None:
            if current_time.weekday() != self.auto_weekday:
                return False
        
        # Verificar dia do mês para frequência mensal
        if self.auto_frequency == 'monthly' and self.auto_day_of_month:
            if current_time.day != self.auto_day_of_month:
                return False
        
        return True
    
    def mark_auto_generation_completed(self):
        """Marcar que a geração automática foi realizada"""
        self.last_auto_generation = datetime.now(timezone.utc)
        db.session.commit()
    
    def get_next_auto_generation_time(self):
        """Calcular próximo horário de geração automática"""
        if not self.auto_generation_enabled:
            return None
        
        now = datetime.now()
        default_time = datetime.strptime('08:00', '%H:%M').time()
        target_time = self.auto_time or default_time
        
        next_time = now.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=0,
            microsecond=0
        )
        
        if self.auto_frequency == 'daily':
            if next_time <= now:
                next_time += timedelta(days=1)
        elif self.auto_frequency == 'weekly':
            days_ahead = (self.auto_weekday or 0) - now.weekday()
            if days_ahead <= 0:  # Já passou esta semana
                days_ahead += 7
            next_time += timedelta(days=days_ahead)
        elif self.auto_frequency == 'monthly':
            # Próximo dia do mês
            if next_time.day != (self.auto_day_of_month or 1) or next_time <= now:
                if next_time.month == 12:
                    next_time = next_time.replace(year=next_time.year + 1, month=1, day=self.auto_day_of_month or 1)
                else:
                    next_time = next_time.replace(month=next_time.month + 1, day=self.auto_day_of_month or 1)
        
        return next_time

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
