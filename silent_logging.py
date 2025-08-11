"""
Configuração de logging ultra-silenciosa para desenvolvimento
Remove logs verbosos e mantém apenas o essencial
"""
import logging
import sys
import os

def setup_silent_logging():
    """Configura logging ultra-silencioso para desenvolvimento"""
    
    # Configurar nível de log baseado no ambiente
    if os.getenv('FLASK_ENV') == 'development':
        # Desenvolvimento: apenas ERRORS
        log_level = logging.ERROR
    else:
        # Produção: WARNING e acima
        log_level = logging.WARNING
    
    # Silenciar loggers específicos que geram muito ruído
    noisy_loggers = [
        'app.middleware.security',
        'app.utils.response_helpers', 
        'app.utils.monitoring_alerts_fixed',
        'app.services.notification_service',
        'app.utils.health_checks',
        'app.utils.api_integration',
        'audit',
        'auth_debug',
        'werkzeug'
    ]
    
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Criar handler simples apenas para desenvolvimento
    if os.getenv('FLASK_ENV') == 'development':
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)
        root_logger.addHandler(handler)
    
    print("🔇 Logging ultra-silencioso ativado - apenas ERRORS críticos")

if __name__ == "__main__":
    setup_silent_logging()
