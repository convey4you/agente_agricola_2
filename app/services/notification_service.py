from flask import current_app, render_template_string
from app.models.alerts import Alert
import smtplib
import logging
from typing import Optional
import requests
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    """Serviço para envio de notificações"""
    
    def __init__(self):
        self.mail = None
        # Inicializar Flask-Mail se disponível
        try:
            from flask_mail import Mail
            self.mail = Mail()
        except ImportError:
            logger.warning("Flask-Mail não disponível")
    
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
                        <a href="{{ base_url }}{{ alert.action_url }}" class="action-button">
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
                base_url=current_app.config.get('BASE_URL', 'https://www.agenteagricola.com')
            )
            
            # Tentar enviar via Flask-Mail se disponível
            if self.mail:
                try:
                    from flask_mail import Message
                    
                    msg = Message(
                        subject=f"🌱 {alert.title} - AgroTech Portugal",
                        recipients=[user.email],
                        html=html_content,
                        sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@agrotech.pt')
                    )
                    
                    self.mail.send(msg)
                    logger.info(f"Email enviado via Flask-Mail para {user.email} - Alerta {alert.id}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Erro ao enviar via Flask-Mail: {e}")
            
            # Fallback: enviar via SMTP simples
            return self._send_email_smtp(user.email, alert.title, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para alerta {alert.id}: {e}")
            return False
    
    def _send_email_smtp(self, recipient: str, subject: str, html_content: str) -> bool:
        """Enviar email via SMTP simples"""
        try:
            smtp_server = current_app.config.get('SMTP_SERVER', 'localhost')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_user = current_app.config.get('SMTP_USER')
            smtp_password = current_app.config.get('SMTP_PASSWORD')
            
            if not smtp_user:
                logger.warning("SMTP não configurado - email simulado")
                logger.info(f"Email simulado para {recipient}: {subject}")
                return True
            
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = recipient
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado via SMTP para {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email via SMTP: {e}")
            return False
    
    def send_sms_alert(self, alert: Alert) -> bool:
        """Enviar alerta por SMS (implementação futura)"""
        try:
            user = alert.user
            
            # Verificar se usuário tem telefone
            phone = getattr(user, 'telefone', None)
            if not phone:
                logger.warning(f"Usuário {user.id} não tem telefone cadastrado")
                return False
            
            # Preparar mensagem SMS (máximo 160 caracteres)
            sms_message = f"🌱 AgroTech: {alert.title}"
            if len(alert.message) < 100:
                sms_message += f" - {alert.message}"
            
            if len(sms_message) > 160:
                sms_message = sms_message[:157] + "..."
            
            # Enviar via provedor configurado
            success = self._send_sms_via_provider(phone, sms_message)
            
            if success:
                logger.info(f"SMS enviado para {phone} - Alerta {alert.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS para alerta {alert.id}: {e}")
            return False
    
    def _send_sms_via_provider(self, phone: str, message: str) -> bool:
        """Enviar SMS através de provedor"""
        
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

    @classmethod
    def send_system_alert(cls, title: str, message: str, severity: str = 'INFO') -> bool:
        """Enviar alerta de sistema para monitoramento"""
        try:
            logger.info(f"[SYSTEM ALERT] {severity}: {title} - {message}")
            
            # Em produção, aqui seria integração com serviços como:
            # - Slack
            # - PagerDuty
            # - Email para administradores
            # - Webhook para sistema de monitoramento externo
            
            # Por enquanto, apenas log estruturado
            alert_data = {
                'type': 'system_alert',
                'title': title,
                'message': message,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log estruturado para parsing por sistemas externos
            logger.warning(f"SYSTEM_ALERT: {json.dumps(alert_data)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de sistema: {e}")
            return False
