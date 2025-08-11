"""
Configuração de desenvolvimento limpa - AgTech Portugal
"""
import os
from config import Config

class DevelopmentCleanConfig(Config):
    """Configuração de desenvolvimento com logs reduzidos"""
    
    DEBUG = True
    TESTING = False
    
    # Desabilitar sistemas pesados em desenvolvimento
    DISABLE_PERFORMANCE_MONITORING = True
    DISABLE_METRICS_COLLECTION = True
    DISABLE_HEALTH_CHECKS = True
    DISABLE_BACKGROUND_TASKS = True
    
    # Cache simples em memória
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Logs mínimos
    LOG_LEVEL = 'WARNING'
    
    # Usar banco SQLite do diretório instance - CORRIGIDO para usar agente_agricola.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath('.'), 'instance', 'agente_agricola.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Desabilitar logs SQL
    
    # Segurança mínima para desenvolvimento
    SECRET_KEY = 'dev-secret-key-not-for-production'
    WTF_CSRF_ENABLED = False  # Desabilitar CSRF em desenvolvimento
    
    @staticmethod
    def init_app(app):
        """Inicialização específica para desenvolvimento"""
        import logging
        
        # Configurar logging mínimo
        logging.getLogger('app.utils.metrics').setLevel(logging.CRITICAL)
        logging.getLogger('app.utils.performance_monitoring').setLevel(logging.CRITICAL)
        logging.getLogger('app.services.notification_service').setLevel(logging.CRITICAL)
        logging.getLogger('app.middleware.security').setLevel(logging.CRITICAL)
        logging.getLogger('app.utils.health_checks').setLevel(logging.CRITICAL)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        print("🧹 Configuração de desenvolvimento limpa aplicada")

# Registrar configuração
config = {
    'development_clean': DevelopmentCleanConfig,
    'default': DevelopmentCleanConfig
}
