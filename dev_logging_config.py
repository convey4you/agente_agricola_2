# Configuração de logs ultra-silenciosa para desenvolvimento
# Reduz drasticamente os logs para um ambiente de desenvolvimento mais limpo

import logging
import os

def setup_dev_logging():
    """Configuração ultra-silenciosa de logs para desenvolvimento"""
    
    # Silenciar praticamente todos os logs
    logging.basicConfig(
        level=logging.CRITICAL,  # Apenas CRITICAL
        format='%(message)s',  # Formato mínimo
        handlers=[logging.NullHandler()]  # Handler nulo (sem output)
    )
    
    # Lista abrangente de loggers para silenciar
    loggers_to_silence = [
        'root',
        'app',
        'app.utils.health_checks',
        'app.utils.cache_optimization', 
        'app.utils.performance_monitoring',
        'app.utils.metrics',
        'app.services.weather_scheduler',
        'app.services.recommendations',
        'app.services.culture_manager',
        'app.services.notification_service',
        'app.routes.dashboard',
        'app.routes.weather',
        'app.routes.alerts',
        'app.routes.culture',
        'apscheduler',
        'werkzeug',
        'urllib3',
        'requests',
        'flask',
        'sqlalchemy'
    ]
    
    # Configurar todos os loggers para CRITICAL
    for logger_name in loggers_to_silence:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        logger.disabled = True  # Desabilitar completamente
    
    # Configurar apenas um handler mínimo para erros críticos
    critical_handler = logging.StreamHandler()
    critical_handler.setLevel(logging.CRITICAL)
    critical_handler.setFormatter(logging.Formatter('ERRO CRÍTICO: %(message)s'))
    
    # Aplicar apenas aos erros mais críticos
    root_logger = logging.getLogger()
    root_logger.handlers = [critical_handler]
    root_logger.setLevel(logging.CRITICAL)
    
    # Silenciar mensagens específicas do Werkzeug em desenvolvimento
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)
    
    # Filtro personalizado para mensagens do debugger
    class DebuggerFilter(logging.Filter):
        def filter(self, record):
            # Filtrar mensagens do debugger
            return not any(msg in record.getMessage() for msg in [
                "Debugger is active",
                "Debugger PIN",
                "Running on"
            ])
    
    # Aplicar filtro ao logger werkzeug
    werkzeug_logger.addFilter(DebuggerFilter())
    
    print("🔇 Logs reduzidos para desenvolvimento - apenas WARNINGS e ERRORS serão mostrados")

# Para usar esta configuração, adicione no início do run.py:
# from dev_logging_config import setup_dev_logging
# setup_dev_logging()
