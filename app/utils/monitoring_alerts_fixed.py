# app/utils/monitoring_alerts_fixed.py
"""
Sistema de Alertas para Monitoramento - Versão Corrigida
Não depende de contexto Flask para funcionar
"""

import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    
    def __init__(self, rule_name, message, severity=AlertSeverity.MEDIUM, 
                 component=None, metric_name=None, metric_value=None, 
                 threshold=None, channels=None):
        self.id = f"alert_{int(time.time() * 1000)}_{hash(rule_name) % 10000}"
        self.rule_name = rule_name
        self.message = message
        self.severity = severity
        self.component = component
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.threshold = threshold
        self.channels = channels or [AlertChannel.LOG]
        self.triggered_at = datetime.utcnow()
        self.resolved = False
        self.resolved_at = None
        self.status = 'active'
    
    def resolve(self):
        """Resolver o alerta"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.status = 'resolved'
    
    def to_dict(self):
        """Converter alerta para dicionário"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'message': self.message,
            'severity': self.severity,
            'component': self.component,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'channels': self.channels,
            'triggered_at': self.triggered_at.isoformat(),
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
        try:
            value = float(metric_value)
            threshold = float(self.threshold)
            
            if self.comparison == 'greater_than':
                return value > threshold
            elif self.comparison == 'less_than':
                return value < threshold
            elif self.comparison == 'equals':
                return value == threshold
            else:
                return False
        except (ValueError, TypeError):
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
            rule_name=self.name,
            message=f"Metric {self.metric_name} value {metric_value} {self.comparison} threshold {self.threshold}",
            severity=self.severity,
            component=f"threshold_monitor",
            metric_name=self.metric_name,
            metric_value=metric_value,
            threshold=self.threshold,
            channels=self.channels
        )

class LogNotifier:
    """Notificador por log"""
    
    def __init__(self):
        self.logger = logging.getLogger('alerts')
    
    def send_alert(self, alert):
        """Enviar alerta para logs"""
        log_method = getattr(self.logger, alert.severity, self.logger.info)
        
        log_method(
            f"ALERT: {alert.rule_name} - {alert.message}",
            extra={
                'alert_id': alert.id,
                'rule_name': alert.rule_name,
                'severity': alert.severity,
                'component': alert.component,
                'metric_name': alert.metric_name,
                'metric_value': alert.metric_value,
                'threshold': alert.threshold,
                'triggered_at': alert.triggered_at.isoformat()
            }
        )
        return True

class EmailNotifier:
    """Notificador por email - versão independente do Flask"""
    
    def __init__(self, smtp_server=None, smtp_port=587, username=None, 
                 password=None, from_email=None, to_emails=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port or 587
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails or []
        self.logger = logging.getLogger(__name__)
    
    def configure(self, smtp_server, smtp_port, username, password, from_email, to_emails):
        """Configurar notificador por email"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    def send_alert(self, alert):
        """Enviar alerta por email"""
        if not all([self.smtp_server, self.username, self.password, self.from_email]):
            self.logger.warning("Email configuration incomplete, skipping email alert")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[AgroTech Alert - {alert.severity.upper()}] {alert.rule_name}"
            
            # Corpo do email
            body = f"""
Alerta do Sistema AgroTech Portugal

Regra: {alert.rule_name}
Severidade: {alert.severity.upper()}
Componente: {alert.component or 'N/A'}
Timestamp: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Mensagem:
{alert.message}

Detalhes:
- Métrica: {alert.metric_name or 'N/A'}
- Valor: {alert.metric_value or 'N/A'}
- Threshold: {alert.threshold or 'N/A'}

ID do Alerta: {alert.id}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Alert email sent successfully: {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {str(e)}")
            return False

class AlertManager:
    """Gerenciador de alertas independente do Flask"""
    
    def __init__(self):
        self.alerts = {}  # alert_id -> Alert
        self.rules = {}   # rule_name -> ThresholdRule
        self.notifiers = {
            AlertChannel.LOG: LogNotifier(),
            AlertChannel.EMAIL: EmailNotifier()
        }
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.processing_thread = None
        self.lock = threading.Lock()
        
        # Estatísticas
        self.stats = {
            'total_alerts': 0,
            'alerts_by_severity': defaultdict(int),
            'alerts_by_rule': defaultdict(int)
        }
    
    def add_threshold_rule(self, name, metric_name, threshold, comparison='greater_than', severity=AlertSeverity.MEDIUM):
        """Adicionar regra de threshold"""
        with self.lock:
            rule = ThresholdRule(
                name=name,
                metric_name=metric_name,
                threshold=threshold,
                comparison=comparison,
                severity=severity
            )
            self.rules[name] = rule
            self.logger.info(f"Added threshold rule: {name}")
    
    def create_alert(self, rule_name, message, severity=AlertSeverity.MEDIUM, **kwargs):
        """Criar alerta manualmente"""
        alert = Alert(
            rule_name=rule_name,
            message=message,
            severity=severity,
            **kwargs
        )
        
        with self.lock:
            self.alerts[alert.id] = alert
            self.stats['total_alerts'] += 1
            self.stats['alerts_by_severity'][severity] += 1
            self.stats['alerts_by_rule'][rule_name] += 1
        
        self._send_alert(alert)
        return alert
    
    def check_metric_alerts(self, metric_name, metric_value):
        """Verificar se métricas devem gerar alertas"""
        triggered_alerts = []
        
        with self.lock:
            for rule_name, rule in self.rules.items():
                if rule.metric_name == metric_name:
                    if rule.should_trigger(metric_value) and rule.can_trigger():
                        alert = rule.create_alert(metric_value)
                        self.alerts[alert.id] = alert
                        self.stats['total_alerts'] += 1
                        self.stats['alerts_by_severity'][alert.severity] += 1
                        self.stats['alerts_by_rule'][rule_name] += 1
                        triggered_alerts.append(alert)
        
        # Enviar alertas fora do lock
        for alert in triggered_alerts:
            self._send_alert(alert)
        
        return triggered_alerts
    
    def _send_alert(self, alert):
        """Enviar alerta através dos canais configurados"""
        for channel in alert.channels:
            if channel in self.notifiers:
                try:
                    self.notifiers[channel].send_alert(alert)
                except Exception as e:
                    self.logger.error(f"Failed to send alert via {channel}: {str(e)}")
    
    def get_active_alerts(self):
        """Obter alertas ativos"""
        with self.lock:
            return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_history(self, limit=50):
        """Obter histórico de alertas"""
        with self.lock:
            sorted_alerts = sorted(
                self.alerts.values(),
                key=lambda x: x.triggered_at,
                reverse=True
            )
            return sorted_alerts[:limit]
    
    def resolve_alert(self, alert_id):
        """Resolver alerta"""
        with self.lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolve()
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
            return False
    
    def get_alert_summary(self):
        """Obter resumo dos alertas"""
        with self.lock:
            active_alerts = [a for a in self.alerts.values() if not a.resolved]
            
            return {
                'active_count': len(active_alerts),
                'total_count': len(self.alerts),
                'rules_count': len(self.rules),
                'by_severity': dict(self.stats['alerts_by_severity']),
                'by_rule': dict(self.stats['alerts_by_rule']),
                'last_24h': len([
                    a for a in self.alerts.values()
                    if (datetime.utcnow() - a.triggered_at).total_seconds() < 86400
                ])
            }
    
    def configure_email(self, smtp_host, smtp_port, smtp_user, smtp_password, from_email, to_emails):
        """Configurar notificações por email"""
        if AlertChannel.EMAIL in self.notifiers:
            self.notifiers[AlertChannel.EMAIL].configure(
                smtp_host, smtp_port, smtp_user, smtp_password, from_email, to_emails
            )
            self.logger.info("Email notifications configured")
    
    def start_processing(self):
        """Iniciar processamento de alertas em background"""
        if not self.running:
            self.running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            self.logger.info("Alert processing started")
    
    def stop_processing(self):
        """Parar processamento de alertas"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
        self.logger.info("Alert processing stopped")
    
    def _processing_loop(self):
        """Loop de processamento de alertas"""
        while self.running:
            try:
                # Limpar alertas antigos resolvidos (mais de 7 dias)
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                
                with self.lock:
                    old_alerts = [
                        alert_id for alert_id, alert in self.alerts.items()
                        if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time
                    ]
                    
                    for alert_id in old_alerts:
                        del self.alerts[alert_id]
                
                if old_alerts:
                    self.logger.info(f"Cleaned up {len(old_alerts)} old resolved alerts")
                
                time.sleep(300)  # 5 minutos
                
            except Exception as e:
                self.logger.error(f"Error in alert processing loop: {str(e)}")
                time.sleep(60)

# Instância global do gerenciador de alertas
alert_manager = AlertManager()
