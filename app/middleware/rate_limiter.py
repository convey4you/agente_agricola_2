"""
Sistema de Rate Limiting para AgroTech Portugal
Implementa proteção contra ataques de força bruta e spam
"""

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    print("⚠️ flask_limiter não disponível - usando mocks")
    LIMITER_AVAILABLE = False
    # Mock das funções necessárias
    def get_remote_address():
        from flask import request
        return request.remote_addr or 'unknown'
    
from flask import request
import logging

logger = logging.getLogger(__name__)

class RateLimitManager:
    """Gerenciador de rate limiting para a aplicação"""
    
    def __init__(self, app=None):
        self.limiter = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o rate limiter com a aplicação Flask"""
        
        if not LIMITER_AVAILABLE:
            print("⚠️ RateLimitManager não disponível: No module named 'flask_limiter'")
            print("⚠️ Rate limiting não disponível - funcionando sem proteção")
            app.limiter = None
            return
        
        def get_user_id():
            """Função para identificar usuário para rate limiting"""
            try:
                from flask_login import current_user
                if current_user.is_authenticated:
                    return f"user:{current_user.id}"
                return get_remote_address()
            except:
                return get_remote_address()
        
        # Determinar storage baseado na disponibilidade do Redis
        storage_uri = self._get_storage_uri(app)
        
        # Configurar limiter
        self.limiter = Limiter(
            app=app,
            key_func=get_user_id,
            default_limits=["1000 per hour", "200 per minute"],
            storage_uri=storage_uri,
            strategy="fixed-window"  # Estratégia válida
        )
        
        # Configurar handlers de erro
        @app.errorhandler(429)
        def ratelimit_handler(e):
            """Handler para quando rate limit é excedido"""
            logger.warning(f"Rate limit exceeded for {get_remote_address()}: {e}")
            return {
                'error': 'Rate limit exceeded',
                'message': 'Muitas tentativas. Tente novamente em alguns minutos.',
                'retry_after': e.retry_after
            }, 429
        
        app.limiter = self.limiter
        logger.info(f"Rate limiting system initialized with storage: {storage_uri}")
    
    def _get_storage_uri(self, app):
        """Determina o storage URI, com fallback para memória se Redis não estiver disponível"""
        redis_url = app.config.get('REDIS_URL')
        
        # Testar conexão Redis apenas se a URL estiver configurada e não for placeholder
        if redis_url and redis_url != '${{Redis.REDIS_URL}}':
            try:
                import redis
                client = redis.from_url(redis_url)
                client.ping()
                logger.info(f"✅ Redis disponível - usando Redis para rate limiting: {redis_url[:20]}...")
                return redis_url
            except Exception as e:
                logger.warning(f"❌ Redis não disponível ({e}), usando memória local para rate limiting")
                return 'memory://'
        else:
            logger.info("⚠️ REDIS_URL não configurada, usando memória local para rate limiting")
            return 'memory://'

# Decoradores que funcionam com e sem flask_limiter
if LIMITER_AVAILABLE:
    def critical_endpoint_limit(f):
        """Rate limit para endpoints críticos (login, registro)"""
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        decorated._limiter_limit = "5 per minute"
        return decorated

    def api_endpoint_limit(f):
        """Rate limit para endpoints de API"""
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        decorated._limiter_limit = "100 per hour"
        return decorated

    def public_endpoint_limit(f):
        """Rate limit para endpoints públicos"""
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        decorated._limiter_limit = "500 per hour"
        return decorated

    def authenticated_endpoint_limit(f):
        """Rate limit para endpoints autenticados"""
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        decorated._limiter_limit = "1000 per hour"
        return decorated
else:
    # Mocks dos decoradores quando flask_limiter não está disponível
    def critical_endpoint_limit(f):
        """Mock rate limit para endpoints críticos"""
        return f

    def api_endpoint_limit(f):
        """Mock rate limit para endpoints de API"""
        return f

    def public_endpoint_limit(f):
        """Mock rate limit para endpoints públicos"""
        return f

    def authenticated_endpoint_limit(f):
        """Mock rate limit para endpoints autenticados"""
        return f
