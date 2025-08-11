"""
Middleware de Segurança para AgroTech Portugal
Implementa headers de segurança e proteções adicionais
"""

from flask import request, g, current_app
import logging
from datetime import datetime
import hashlib
import secrets

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Middleware para aplicar headers de segurança e proteções"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o middleware com a aplicação Flask"""
        
        @app.before_request
        def before_request():
            """Processa requisições antes de chegar ao endpoint"""
            self._log_request()
            self._generate_nonce()
            self._check_suspicious_patterns()
        
        @app.after_request
        def after_request(response):
            """Adiciona headers de segurança após processamento"""
            return self._add_security_headers(response)
        
        logger.info("Security middleware initialized")
    
    def _log_request(self):
        """Log de segurança para auditoria"""
        g.request_id = secrets.token_hex(8)
        g.request_start = datetime.utcnow()
        
        # Log informações da requisição
        logger.info(f"[{g.request_id}] {request.method} {request.path} from {request.remote_addr}")
        
        # Log headers suspeitos
        suspicious_headers = ['x-forwarded-for', 'x-real-ip', 'user-agent']
        for header in suspicious_headers:
            value = request.headers.get(header)
            if value:
                logger.debug(f"[{g.request_id}] Header {header}: {value}")
    
    def _generate_nonce(self):
        """Gera nonce para CSP"""
        g.csp_nonce = secrets.token_urlsafe(16)
    
    def _check_suspicious_patterns(self):
        """Verifica padrões suspeitos na requisição"""
        
        # Verificar tamanho excessivo de headers
        total_header_size = sum(len(k) + len(v) for k, v in request.headers)
        if total_header_size > 8192:  # 8KB limite
            logger.warning(f"[{g.request_id}] Large headers detected: {total_header_size} bytes")
        
        # Verificar User-Agent suspeito
        user_agent = request.headers.get('User-Agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'burp', 'nmap', 'curl/7.', 'python-requests']
        if any(agent in user_agent for agent in suspicious_agents):
            logger.warning(f"[{g.request_id}] Suspicious User-Agent: {user_agent}")
        
        # Verificar múltiplos slashes na URL
        if '//' in request.path:
            logger.warning(f"[{g.request_id}] Multiple slashes in path: {request.path}")
    
    def _add_security_headers(self, response):
        """Adiciona headers de segurança à resposta"""
        
        # Content Security Policy - Implementação segura com nonce
        nonce = getattr(g, 'csp_nonce', 'default')
        csp_policy = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://maxcdn.bootstrapcdn.com; "
            f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://maxcdn.bootstrapcdn.com; "
            f"img-src 'self' data: https:; "
            f"font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com https://maxcdn.bootstrapcdn.com; "
            f"connect-src 'self' https://api.openweathermap.org https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com https://maxcdn.bootstrapcdn.com; "
            f"frame-ancestors 'none'; "
            f"base-uri 'self'; "
            f"form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        
        # HTTP Strict Transport Security
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy / Permissions Policy
        permissions_policy = (
            "geolocation=(self), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        response.headers['Permissions-Policy'] = permissions_policy
        
        # Cache Control para rotas sensíveis
        if request.endpoint and any(sensitive in request.endpoint for sensitive in ['auth', 'admin', 'user']):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # Server header removal
        response.headers.pop('Server', None)
        
        # Custom security headers
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        return response

class CSRFProtection:
    """Proteção CSRF customizada"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa proteção CSRF"""
        
        @app.before_request
        def csrf_protect():
            """Verifica token CSRF em requests POST/PUT/DELETE"""
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                if not self._verify_csrf_token():
                    logger.warning(f"CSRF token validation failed for {request.remote_addr}")
                    from flask import abort
                    abort(403)
        
        logger.info("CSRF protection initialized")
    
    def _verify_csrf_token(self):
        """Verifica validade do token CSRF"""
        
        # Exceções para APIs que usam outros métodos de autenticação
        exempt_endpoints = [
            'auth.login', 
            'auth.register',
            'auth.save_onboarding',  # Adicionar para permitir salvamento do onboarding
            'geocoding.search_locations',
            'geocoding.geocode_address',
            'geocoding.validate_coordinates',
            'geocoding.detect_soil',
            'geocoding.detect_climate',
            'geocoding.test_public',
            'culture.verificar_cultura',  # API de verificação de cultura
            'culture.save_wizard_step',    # API de salvamento do wizard
            'alert_preferences_api.get_user_preferences',  # API de preferências de alertas
            'alert_preferences_api.update_preference',
            'alert_preferences_api.run_auto_generation',
            'alert_preferences_api.create_default_preferences',
            'alert_preferences_api.admin_run_auto_generation',
            'alert_preferences_api.admin_get_pending_users',
            'alerts_api.generate_alerts'  # API de geração de alertas
        ]
        if request.endpoint in exempt_endpoints:
            return True
        
        # Obter token do header ou form
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not token:
            return False
        
        # Verificar token na sessão
        from flask import session
        session_token = session.get('csrf_token')
        
        if not session_token:
            return False
        
        # Comparação segura
        return secrets.compare_digest(token, session_token)
    
    @staticmethod
    def generate_csrf_token():
        """Gera novo token CSRF"""
        from flask import session
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return session['csrf_token']

class SecurityAuditLogger:
    """Logger de auditoria de segurança"""
    
    def __init__(self, app=None):
        self.security_logger = logging.getLogger('security_audit')
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa logger de auditoria"""
        
        # Configurar handler específico para logs de segurança
        import os
        log_dir = app.config.get('LOG_DIR', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        security_handler = logging.FileHandler(
            os.path.join(log_dir, 'security_audit.log')
        )
        security_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(formatter)
        
        self.security_logger.addHandler(security_handler)
        self.security_logger.setLevel(logging.INFO)
        
        logger.info("Security audit logger initialized")
    
    def log_security_event(self, event_type, details, severity='INFO'):
        """Log eventos de segurança"""
        message = f"[{event_type}] {details} | IP: {request.remote_addr} | User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        
        if severity == 'WARNING':
            self.security_logger.warning(message)
        elif severity == 'ERROR':
            self.security_logger.error(message)
        elif severity == 'CRITICAL':
            self.security_logger.critical(message)
        else:
            self.security_logger.info(message)

# Instâncias globais
security_middleware = SecurityMiddleware()
csrf_protection = CSRFProtection()
security_audit = SecurityAuditLogger()
