"""
Middleware de Autenticação Robusto - CORREÇÃO SPRINT 1
Implementa verificações e correções para problemas de sessão
"""
from functools import wraps
from flask import session, request, redirect, url_for, flash, current_app
from flask_login import current_user
from datetime import datetime, timezone


def ensure_session_valid(f):
    """Middleware para garantir validade da sessão - CORREÇÃO SPRINT 1"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.utils.auth_debug_logger import AuthDebugLogger
        
        # Log da tentativa de acesso
        AuthDebugLogger.log_authentication_check(
            request.endpoint, 
            current_user.is_authenticated,
            current_user.id if current_user.is_authenticated else None
        )
        
        # Verificar se há inconsistência na sessão
        if 'user_id' in session and not current_user.is_authenticated:
            AuthDebugLogger.log_session_inconsistency(
                'Session has user_id but current_user not authenticated',
                {'user_id': session.get('user_id'), 'session_keys': list(session.keys())},
                {'is_authenticated': current_user.is_authenticated}
            )
            session.clear()
            flash('Sua sessão expirou. Por favor, faça login novamente.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Verificar se usuário está realmente autenticado
        if not current_user.is_authenticated:
            current_app.logger.info('User not authenticated - redirecting to login')
            return redirect(url_for('auth.login'))
        
        # Atualizar último acesso
        try:
            current_user.ultimo_acesso = datetime.now(timezone.utc)
            from app import db
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Error updating last access: {e}')
        
        return f(*args, **kwargs)
    return decorated_function


def log_auth_event(event_type, user_id=None, details=None):
    """Função para logging de eventos de autenticação - CORREÇÃO SPRINT 1"""
    from app.utils.auth_debug_logger import AuthDebugLogger
    
    if event_type == 'LOGIN_SUCCESS':
        AuthDebugLogger.log_login_attempt(details.get('email', ''), True, user_id, details)
    elif event_type == 'LOGIN_FAILED':
        AuthDebugLogger.log_login_attempt(details.get('email', ''), False, user_id, details)
    elif event_type == 'LOGOUT':
        AuthDebugLogger.log_logout_event(user_id, details.get('email', ''))
    else:
        current_app.logger.info(f'AUTH_EVENT: {event_type} - User: {user_id} - Details: {details}')


def require_onboarding_complete(f):
    """Middleware para garantir que onboarding foi completado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and not current_user.onboarding_completed:
            flash('Complete seu perfil antes de continuar.', 'info')
            return redirect(url_for('auth.onboarding'))
        return f(*args, **kwargs)
    return decorated_function


def csrf_protect():
    """Middleware simples de proteção CSRF"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                token = session.get('csrf_token')
                form_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
                
                if not token or not form_token or token != form_token:
                    flash('Token de segurança inválido. Tente novamente.', 'error')
                    return redirect(request.url)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
