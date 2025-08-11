"""
Configurações da aplicação Flask
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()


class Config:
    """Configuração base"""
    # SECRET_KEY otimizada para Flask-Login - CORREÇÃO SPRINT 1
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agrotech-portugal-secret-key-2025'
    
    # Configuração do banco de dados - SQLite para desenvolvimento e produção
    # TEMPORÁRIO: Durante desenvolvimento, usar SQLite em produção também
    
    # Sempre usar SQLite - mais simples para desenvolvimento
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(instance_dir, 'agente_agricola.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de sessão ROBUSTAS - CORREÇÃO SPRINT 1
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # 30 minutos timeout
    SESSION_COOKIE_SECURE = False  # True apenas em HTTPS/produção
    SESSION_COOKIE_HTTPONLY = True  # Previne acesso via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Proteção CSRF melhorada
    SESSION_COOKIE_NAME = 'agtech_session'
    SESSION_COOKIE_PATH = '/'
    SESSION_PROTECTION = 'strong'  # Proteção forte de sessão
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    
    # Configurações de API externa
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    
    # Configurações de AI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Cache simplificado - sem Redis
    CACHE_ENABLED = False
    
    # Rate limiting simplificado
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"
    
    # SPRINT 4 - Configurações de Performance (sem cache Redis)
    # Configurações de Database Pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 20)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 30)),
        'pool_pre_ping': True,
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30))
    }
    
    # Configurações de Cache de Performance
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 3600))
    CACHE_USER_DATA_TIMEOUT = int(os.environ.get('CACHE_USER_DATA_TIMEOUT', 1800))
    CACHE_WEATHER_DATA_TIMEOUT = int(os.environ.get('CACHE_WEATHER_DATA_TIMEOUT', 1800))
    CACHE_AI_RECOMMENDATIONS_TIMEOUT = int(os.environ.get('CACHE_AI_RECOMMENDATIONS_TIMEOUT', 3600))
    
    # Configurações de Cache Warming
    CACHE_WARMING_ENABLED = os.environ.get('CACHE_WARMING_ENABLED', 'true').lower() == 'true'
    
    # Configurações de Asset Optimization
    ASSET_COMPRESSION_ENABLED = os.environ.get('ASSET_COMPRESSION_ENABLED', 'true').lower() == 'true'
    ASSET_CACHE_TIMEOUT = int(os.environ.get('ASSET_CACHE_TIMEOUT', 31536000))  # 1 ano
    CDN_BASE_URL = os.environ.get('CDN_BASE_URL')
    
    # Configurações de Performance Monitoring
    SLOW_QUERY_THRESHOLD = float(os.environ.get('SLOW_QUERY_THRESHOLD', 1.0))
    SLOW_REQUEST_THRESHOLD = float(os.environ.get('SLOW_REQUEST_THRESHOLD', 2.0))
    PERFORMANCE_MONITORING_ENABLED = os.environ.get('PERFORMANCE_MONITORING_ENABLED', 'true').lower() == 'true'
    
    # Configurações de Lazy Loading
    LAZY_LOADING_ENABLED = os.environ.get('LAZY_LOADING_ENABLED', 'true').lower() == 'true'
    
    # PROMPT 3: Configurações de Monitoramento
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/agrotech.log')
    JSON_LOGGING = os.environ.get('JSON_LOGGING', 'true').lower() == 'true'
    
    # Métricas do sistema
    SYSTEM_METRICS_ENABLED = os.environ.get('SYSTEM_METRICS_ENABLED', 'true').lower() == 'true'
    METRICS_COLLECTION_INTERVAL = int(os.environ.get('METRICS_COLLECTION_INTERVAL', 60))
    
    # Health checks
    HEALTH_CHECKS_ENABLED = os.environ.get('HEALTH_CHECKS_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 300))
    
    # Sistema de alertas
    ALERTS_ENABLED = os.environ.get('ALERTS_ENABLED', 'true').lower() == 'true'
    ALERT_CONFIG = {
        'email_enabled': os.environ.get('ALERT_EMAIL_ENABLED', 'false').lower() == 'true',
        'smtp_host': os.environ.get('ALERT_SMTP_HOST'),
        'smtp_port': int(os.environ.get('ALERT_SMTP_PORT', 587)),
        'smtp_user': os.environ.get('ALERT_SMTP_USER'),
        'smtp_password': os.environ.get('ALERT_SMTP_PASSWORD'),
        'from_email': os.environ.get('ALERT_FROM_EMAIL'),
        'to_emails': os.environ.get('ALERT_TO_EMAILS', '').split(',') if os.environ.get('ALERT_TO_EMAILS') else []
    }
    
    # Timeouts de cache por tipo
    CACHE_TIMEOUT_WEATHER = 30 * 60      # 30 minutos
    CACHE_TIMEOUT_AI = 60 * 60           # 1 hora
    CACHE_TIMEOUT_DASHBOARD = 15 * 60    # 15 minutos
    CACHE_TIMEOUT_CULTURE = 24 * 60 * 60 # 24 horas


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    TESTING = False
    # Cache mais agressivo em desenvolvimento
    CACHE_TIMEOUT_WEATHER = 10 * 60      # 10 minutos
    CACHE_TIMEOUT_AI = 30 * 60           # 30 minutos
    CACHE_TIMEOUT_DASHBOARD = 5 * 60     # 5 minutos
    # Desabilitar cache warming em desenvolvimento
    CACHE_WARMING_ENABLED = False


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    TESTING = False
    
    # Configurações de sessão para HTTPS/produção
    SESSION_COOKIE_SECURE = True  # Requer HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Sessão mais longa em produção
    
    # Cache mais longo em produção
    CACHE_TIMEOUT_WEATHER = 30 * 60     # 30 minutos
    CACHE_TIMEOUT_AI = 60 * 60          # 1 hora  
    CACHE_TIMEOUT_DASHBOARD = 15 * 60   # 15 minutos


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    # Desabilitar cache em testes
    CACHE_ENABLED = False
    # Configurações específicas para SQLite em testes
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }


# Configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
