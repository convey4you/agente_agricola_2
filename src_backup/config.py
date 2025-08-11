"""
Configurações da aplicação Flask
"""
import os
from datetime import timedelta


class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT'
    
    # Configuração do banco de dados com suporte ao Railway PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///./db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    
    # Configurações de API externa
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    
    # Configurações de AI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Configurações de Cache Redis
    CACHE_ENABLED = True
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    CACHE_REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    CACHE_REDIS_SOCKET_TIMEOUT = 5
    CACHE_FALLBACK_ENABLED = True
    CACHE_KEY_PREFIX = 'agagri:'
    CACHE_MAX_MEMORY_ITEMS = 1000
    
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


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    # Desabilitar cache em testes
    CACHE_ENABLED = False


# Configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
