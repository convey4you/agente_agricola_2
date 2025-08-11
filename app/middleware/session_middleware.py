"""
Middleware para correção de problemas de sessão
Implementa verificações e correções automáticas para problemas identificados no Sprint 1
"""
import logging
from flask import session, request, current_app, g
from flask_login import current_user
from functools import wraps

logger = logging.getLogger(__name__)


class SessionMiddleware:
    """Middleware para gerenciar sessões de forma robusta"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar middleware com a aplicação Flask"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Registrar handlers de limpeza
        app.teardown_appcontext(self.teardown_session)
    
    def before_request(self):
        """Verificações antes de cada requisição"""
        try:
            # Verificar se é uma rota pública que não precisa de autenticação
            from app.utils.auth_decorators import is_public_endpoint, is_public_path
            
            if (is_public_endpoint(request.endpoint) or 
                is_public_path(request.path) or
                getattr(g, 'is_public_route', False)):
                return  # Pular validações para rotas públicas
            
            # Verificar integridade da sessão
            self._validate_session()
            
            # Log de debug para rotas de auth
            if request.endpoint and 'auth' in request.endpoint:
                self._log_auth_request()
                
            # Verificar necessidade de onboarding
            if current_user.is_authenticated:
                self._check_onboarding_redirect()
                
        except Exception as e:
            logger.error(f"Erro no middleware before_request: {e}")
    
    def after_request(self, response):
        """Processamento após cada resposta"""
        try:
            # Adicionar headers de segurança para sessões
            if self._is_auth_response(response):
                self._add_security_headers(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no middleware after_request: {e}")
            return response
    
    def teardown_session(self, exception=None):
        """Limpeza da sessão ao final da requisição"""
        try:
            if exception:
                logger.error(f"Exceção durante requisição: {exception}")
                
        except Exception as e:
            logger.error(f"Erro no teardown_session: {e}")
    
    def _validate_session(self):
        """Validar integridade da sessão"""
        try:
            # Verificar se a sessão não está corrompida
            if hasattr(g, 'session_validated'):
                return
            
            # Testar acesso básico à sessão
            _ = session.get('_user_id')  # Flask-Login key
            
            # Marcar como validada
            g.session_validated = True
            
        except Exception as e:
            logger.warning(f"Sessão corrompida detectada: {e}")
            # Limpar sessão corrompida
            session.clear()
    
    def _log_auth_request(self):
        """Log de requisições de autenticação"""
        user_info = "authenticated" if current_user.is_authenticated else "anonymous"
        logger.info(f"AUTH REQUEST: {request.method} {request.endpoint} - User: {user_info}")
    
    def _check_onboarding_redirect(self):
        """Verificar se usuário precisa de onboarding"""
        try:
            # Não redirecionar se já estiver em rotas de onboarding, logout ou APIs públicas
            skip_endpoints = [
                'auth.onboarding', 
                'auth.save_onboarding', 
                'auth.logout',
                'geocoding.search_locations',
                'geocoding.geocode_address', 
                'geocoding.validate_coordinates'
            ]
            if request.endpoint in skip_endpoints:
                return
            
            # Não redirecionar para rotas de API em geral
            if request.path.startswith('/api/geocoding'):
                return
            
            # Verificar se precisa de onboarding
            if hasattr(current_user, 'onboarding_completed') and not current_user.onboarding_completed:
                # Marcar para redirecionamento (será processado pelo controller)
                g.needs_onboarding = True
                
        except Exception as e:
            logger.error(f"Erro ao verificar onboarding: {e}")
    
    def _is_auth_response(self, response):
        """Verificar se é uma resposta de autenticação"""
        return (
            request.endpoint and 
            ('auth' in request.endpoint or 'login' in request.endpoint)
        )
    
    def _add_security_headers(self, response):
        """Adicionar headers de segurança para autenticação"""
        # Prevenir cache de páginas de auth
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Headers de segurança adiciais
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        return response


def require_valid_session(f):
    """
    Decorador para garantir sessão válida em rotas críticas
    Uso: @require_valid_session acima de @login_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verificar se a sessão está válida
            if not session or '_user_id' not in session:
                logger.warning("Sessão inválida detectada em rota protegida")
                session.clear()
                
                # Redirecionar para login se for request de navegador
                if request.accept_mimetypes.accept_html:
                    from flask import redirect, url_for
                    return redirect(url_for('auth.login'))
                else:
                    from flask import jsonify
                    return jsonify({'error': 'Sessão inválida', 'redirect': '/auth/login'}), 401
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Erro em require_valid_session: {e}")
            # Em caso de erro, prosseguir normalmente
            return f(*args, **kwargs)
    
    return decorated_function


# Instância global do middleware
session_middleware = SessionMiddleware()
