# app/utils/monitoring_alerts.py
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, has_app_context
import logging
import threading
import time
from collections import defaultdict, deque

class AlertSeverity:
    """Níveis de severidade de alertas"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class AlertChannel:
    """Canais de envio de alertas"""
    EMAIL = 'email'
    LOG = 'log'
    WEBHOOK = 'webhook'

class Alert:
    """Representação de um alerta"""
    
    def __init__(self, title, message, severity=AlertSeverity.MEDIUM, 
                 component=None, metric_name=None, metric_value=None, 
                 threshold=None, channels=None):
        self.id = f"alert_{int(time.time() * 1000)}"
        self.title = title
        self.message = message
        self.severity = severity
        self.component = component
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.threshold = threshold
        self.channels = channels or [AlertChannel.LOG]
        self.timestamp = datetime.utcnow()
        self.resolved = False
        self.resolved_at = None
    
    def resolve(self):
        """Resolver o alerta"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
    
    @property
    def status(self):
        """Status do alerta"""
        return 'resolved' if self.resolved else 'active'
    
    def to_dict(self):
        """Converter alerta para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'component': self.component,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'channels': self.channels,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'status': self.status
        }

class ThresholdRule:
    """Regra de alerta baseada em threshold"""
    
    def __init__(self, name, metric_name, threshold, comparison='greater_than',
                 severity=AlertSeverity.MEDIUM, window_minutes=5, channels=None):
        self.name = name
        self.metric_name = metric_name
        self.threshold = threshold
        self.comparison = comparison  # greater_than, less_than, equals
        self.severity = severity
        self.window_minutes = window_minutes
        self.channels = channels or [AlertChannel.LOG]
        self.last_triggered = None
        
    def should_trigger(self, metric_value):
        """Verificar se deve triggerar o alerta"""
        if self.comparison == 'greater_than':
            return float(metric_value) > float(self.threshold)
        elif self.comparison == 'less_than':
            return float(metric_value) < float(self.threshold)
        elif self.comparison == 'equals':
            return float(metric_value) == float(self.threshold)
        else:
            return False
    
    def can_trigger(self):
        """Verificar se pode triggerar (respeitando janela de tempo)"""
        if self.last_triggered is None:
            return True
        
        time_since_last = datetime.utcnow() - self.last_triggered
        return time_since_last.total_seconds() > (self.window_minutes * 60)
    
    def create_alert(self, metric_value):
        """Criar alerta baseado na regra"""
        self.last_triggered = datetime.utcnow()
        
        return Alert(
            title=self.name,
            message=f"Metric {self.metric_name} value {metric_value} {self.comparison} threshold {self.threshold}",
            severity=self.severity,
            component=f"threshold_monitor_{self.metric_name}",
            metric_name=self.metric_name,
            metric_value=metric_value,
            threshold=self.threshold,
            channels=self.channels
        )
            'severity': self.severity,
            'component': self.component,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'channels': self.channels,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class ThresholdRule:
    """Regra de threshold para alertas"""
    
    def __init__(self, metric_name, operator, threshold, severity, 
                 component=None, message_template=None, channels=None,
                 cooldown_minutes=10):
        self.metric_name = metric_name
        self.operator = operator  # '>', '<', '>=', '<=', '==', '!='
        self.threshold = threshold
        self.severity = severity
        self.component = component
        self.message_template = message_template or f"Metric {metric_name} {operator} {threshold}"
        self.channels = channels or [AlertChannel.LOG]
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None
    
    def should_trigger(self, value):
        """Verificar se a regra deve ser disparada"""
        # Verificar cooldown
        if self.last_triggered:
            cooldown_threshold = datetime.utcnow() - timedelta(minutes=self.cooldown_minutes)
            if self.last_triggered > cooldown_threshold:
                return False
        
        # Verificar condição
        if self.operator == '>':
            return value > self.threshold
        elif self.operator == '<':
            return value < self.threshold
        elif self.operator == '>=':
            return value >= self.threshold
        elif self.operator == '<=':
            return value <= self.threshold
        elif self.operator == '==':
            return value == self.threshold
        elif self.operator == '!=':
            return value != self.threshold
        
        return False
    
    def create_alert(self, value):
        """Criar alerta baseado na regra"""
        self.last_triggered = datetime.utcnow()
        
        message = self.message_template.format(
            metric_name=self.metric_name,
            value=value,
            threshold=self.threshold,
            operator=self.operator
        )
        
        return Alert(
            title=f"Threshold Alert: {self.metric_name}",
            message=message,
            severity=self.severity,
            component=self.component,
            metric_name=self.metric_name,
            metric_value=value,
            threshold=self.threshold,
            channels=self.channels
        )

class EmailNotifier:
    """Notificador por email"""
    
    def __init__(self, smtp_server=None, smtp_port=587, username=None, 
                 password=None, from_email=None, to_emails=None):
        # Usar configurações fornecidas ou valores padrão
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port or 587
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails or []
        self.logger = logging.getLogger(__name__)
        
        # Tentar carregar configurações do Flask se disponível
        self._load_flask_config()
    
    def _load_flask_config(self):
        """Carregar configurações do Flask se contexto disponível"""
        try:
            if has_app_context():
                self.smtp_server = self.smtp_server or current_app.config.get('SMTP_SERVER')
                self.smtp_port = self.smtp_port or current_app.config.get('SMTP_PORT', 587)
                self.username = self.username or current_app.config.get('SMTP_USERNAME')
                self.password = self.password or current_app.config.get('SMTP_PASSWORD')
                self.from_email = self.from_email or current_app.config.get('ALERT_FROM_EMAIL')
                self.to_emails = self.to_emails or current_app.config.get('ALERT_TO_EMAILS', [])
        except Exception:
            # Contexto Flask não disponível, usar valores padrão
            pass
    
    def send_alert(self, alert):
        """Enviar alerta por email"""
        if not all([self.smtp_server, self.username, self.password, self.from_email]):
            self.logger.warning("Email configuration incomplete, skipping email alert")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[AgroTech Alert - {alert.severity.upper()}] {alert.title}"
            
            # Corpo do email
            body = f"""
Alerta do Sistema AgroTech Portugal

Título: {alert.title}
Severidade: {alert.severity.upper()}
Componente: {alert.component or 'N/A'}
Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Mensagem:
{alert.message}

Detalhes Técnicos:
- Métrica: {alert.metric_name or 'N/A'}
- Valor: {alert.metric_value or 'N/A'}
- Threshold: {alert.threshold or 'N/A'}

---
Sistema de Monitoramento AgroTech
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent successfully: {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False

class LogNotifier:
    """Notificador por log"""
    
    def __init__(self):
        self.logger = logging.getLogger('alerts')
    
    def send_alert(self, alert):
        """Registrar alerta no log"""
        log_level = {
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.WARNING)
        
        self.logger.log(log_level, f"ALERT: {alert.title}", extra={
            'extra_fields': {
                'alert_id': alert.id,
                'component': 'monitoring_alert',
                'severity': alert.severity,
                'alert_component': alert.component,
                'metric_name': alert.metric_name,
                'metric_value': alert.metric_value,
                'threshold': alert.threshold,
                'message': alert.message
            }
        })
        
        return True

class AlertManager:
    """Gerenciador central de alertas"""
    
    def __init__(self):
        self.rules = []
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.notifiers = {
            AlertChannel.EMAIL: EmailNotifier(),
            AlertChannel.LOG: LogNotifier()
        }
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Configurar regras padrão
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configurar regras de alerta padrão"""
        default_rules = [
            # Sistema
            ThresholdRule(
                metric_name='system.cpu.percent',
                operator='>',
                threshold=80,
                severity=AlertSeverity.HIGH,
                component='system',
                message_template='CPU usage high: {value}% (threshold: {threshold}%)',
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                cooldown_minutes=15
            ),
            ThresholdRule(
                metric_name='system.memory.percent',
                operator='>',
                threshold=85,
                severity=AlertSeverity.HIGH,
                component='system',
                message_template='Memory usage high: {value}% (threshold: {threshold}%)',
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                cooldown_minutes=15
            ),
            ThresholdRule(
                metric_name='system.disk.percent',
                operator='>',
                threshold=90,
                severity=AlertSeverity.CRITICAL,
                component='system',
                message_template='Disk space critical: {value}% (threshold: {threshold}%)',
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                cooldown_minutes=30
            ),
            
            # Performance HTTP
            ThresholdRule(
                metric_name='http.request.duration.p95',
                operator='>',
                threshold=2.0,
                severity=AlertSeverity.MEDIUM,
                component='http',
                message_template='HTTP response time high: {value}s P95 (threshold: {threshold}s)',
                channels=[AlertChannel.LOG],
                cooldown_minutes=10
            ),
            
            # Health Checks
            ThresholdRule(
                metric_name='health_check.database.errors',
                operator='>',
                threshold=0,
                severity=AlertSeverity.CRITICAL,
                component='database',
                message_template='Database health check failing',
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                cooldown_minutes=5
            )
        ]
        
        self.rules.extend(default_rules)
    
    def add_rule(self, rule):
        """Adicionar regra de alerta"""
        with self.lock:
            self.rules.append(rule)
        
        self.logger.info(f"Alert rule added: {rule.metric_name}", extra={
            'extra_fields': {
                'component': 'alert_manager',
                'action': 'add_rule',
                'metric_name': rule.metric_name,
                'threshold': rule.threshold,
                'severity': rule.severity
            }
        })
    
    def check_metric(self, metric_name, value):
        """Verificar se uma métrica deve gerar alertas"""
        triggered_alerts = []
        
        with self.lock:
            for rule in self.rules:
                if rule.metric_name == metric_name and rule.should_trigger(value):
                    alert = rule.create_alert(value)
                    triggered_alerts.append(alert)
        
        # Processar alertas
        for alert in triggered_alerts:
            self.process_alert(alert)
        
        return triggered_alerts
    
    def process_alert(self, alert):
        """Processar um alerta"""
        with self.lock:
            # Adicionar ao histórico
            self.alert_history.append(alert)
            
            # Adicionar aos alertas ativos se crítico
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                self.active_alerts[alert.id] = alert
        
        # Enviar por todos os canais configurados
        for channel in alert.channels:
            notifier = self.notifiers.get(channel)
            if notifier:
                try:
                    notifier.send_alert(alert)
                except Exception as e:
                    self.logger.error(f"Failed to send alert via {channel}: {e}")
        
        self.logger.info(f"Alert processed: {alert.id}", extra={
            'extra_fields': {
                'component': 'alert_manager',
                'action': 'process_alert',
                'alert_id': alert.id,
                'severity': alert.severity,
                'channels': alert.channels
            }
        })
    
    def resolve_alert(self, alert_id):
        """Resolver um alerta"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                del self.active_alerts[alert_id]
                
                self.logger.info(f"Alert resolved: {alert_id}", extra={
                    'extra_fields': {
                        'component': 'alert_manager',
                        'action': 'resolve_alert',
                        'alert_id': alert_id
                    }
                })
                
                return True
        
        return False
    
    def get_active_alerts(self):
        """Obter alertas ativos"""
        with self.lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit=100):
        """Obter histórico de alertas"""
        with self.lock:
            return list(self.alert_history)[-limit:]
    
    def get_alert_summary(self):
        """Obter resumo de alertas"""
        with self.lock:
            active_count = len(self.active_alerts)
            severity_counts = defaultdict(int)
            
            for alert in self.active_alerts.values():
                severity_counts[alert.severity] += 1
            
            recent_alerts = list(self.alert_history)[-10:]
            
            return {
                'active_alerts': active_count,
                'severity_breakdown': dict(severity_counts),
                'recent_alerts': [alert.to_dict() for alert in recent_alerts],
                'total_rules': len(self.rules)
            }

# Instância global do gerenciador de alertas
alert_manager = AlertManager()
