"""
Sistema de Logging para Diagnóstico de Sessões
Implementado conforme PROMPT 1 - Sprint 1 Correções Críticas
"""
import logging
import sys
from datetime import datetime, timezone
from flask import session, request, current_app
from flask_login import current_user
from functools import wraps

# Configurar logger específico para autenticação
auth_logger = logging.getLogger('auth_debug')
auth_logger.setLevel(logging.DEBUG)

# Handler para arquivo de log
file_handler = logging.FileHandler('logs/auth_debug.log')
file_handler.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

auth_logger.addHandler(file_handler)
auth_logger.addHandler(console_handler)


class AuthDebugLogger:
    """Classe para logging detalhado de eventos de autenticação"""
    
    @staticmethod
    def log_login_attempt(email, success, user_id=None, details=None):
        """Log de tentativas de login"""
        event_type = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        auth_logger.info(f'AUTH_EVENT: {event_type} - Email: {email} - User_ID: {user_id} - IP: {request.remote_addr} - Details: {details}')
    
    @staticmethod
    def log_logout_event(user_id, email):
        """Log de eventos de logout"""
        auth_logger.info(f'AUTH_EVENT: LOGOUT - User_ID: {user_id} - Email: {email} - IP: {request.remote_addr}')
    
    @staticmethod
    def log_session_creation(user_id, session_data):
        """Log de criação de sessão"""
        auth_logger.debug(f'SESSION_CREATE - User_ID: {user_id} - Session_Keys: {list(session_data.keys())} - Session_ID: {session.get("_permanent")}')
    
    @staticmethod
    def log_session_destruction(user_id=None, reason="manual"):
        """Log de destruição de sessão"""
        auth_logger.debug(f'SESSION_DESTROY - User_ID: {user_id} - Reason: {reason} - Session_Keys: {list(session.keys())}')
    
    @staticmethod
    def log_user_loading(user_id, success, error=None):
        """Log de carregamento de usuário"""
        if success:
            auth_logger.debug(f'USER_LOAD_SUCCESS - User_ID: {user_id}')
        else:
            auth_logger.warning(f'USER_LOAD_FAILED - User_ID: {user_id} - Error: {error}')
    
    @staticmethod
    def log_authentication_check(endpoint, authenticated, user_id=None):
        """Log de verificação de autenticação"""
        status = "AUTHENTICATED" if authenticated else "NOT_AUTHENTICATED"
        auth_logger.debug(f'AUTH_CHECK - Endpoint: {endpoint} - Status: {status} - User_ID: {user_id}')
    
    @staticmethod
    def log_session_inconsistency(issue, session_data, user_data):
        """Log de inconsistências de sessão"""
        auth_logger.error(f'SESSION_INCONSISTENCY - Issue: {issue} - Session: {session_data} - User: {user_data}')


def debug_session_decorator(f):
    """Decorator para debugging de rotas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log antes da execução
        AuthDebugLogger.log_authentication_check(
            request.endpoint, 
            current_user.is_authenticated, 
            current_user.id if current_user.is_authenticated else None
        )
        
        # Verificar inconsistências
        if 'user_id' in session and not current_user.is_authenticated:
            AuthDebugLogger.log_session_inconsistency(
                "User_ID in session but current_user not authenticated",
                dict(session),
                {"is_authenticated": current_user.is_authenticated}
            )
        
        return f(*args, **kwargs)
    
    return decorated_function


def setup_auth_logging(app):
    """Configurar logging de autenticação para a aplicação"""
    
    @app.before_request
    def log_request_info():
        if request.endpoint and ('auth' in request.endpoint or 'login' in request.endpoint):
            auth_logger.debug(f'REQUEST - {request.method} {request.endpoint} - IP: {request.remote_addr}')
    
    @app.after_request
    def log_response_info(response):
        if request.endpoint and ('auth' in request.endpoint or 'login' in request.endpoint):
            auth_logger.debug(f'RESPONSE - {request.endpoint} - Status: {response.status_code}')
        return response
