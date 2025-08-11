"""
Configuração de desenvolvimento com logs reduzidos
"""
import os
import logging

def configure_dev_logging():
    """Configurar logging mais limpo para desenvolvimento"""
    
    # Reduzir nível de logging para desenvolvimento
    logging.getLogger('app.utils.metrics').setLevel(logging.ERROR)
    logging.getLogger('app.utils.performance_monitoring').setLevel(logging.ERROR)
    logging.getLogger('app.services.notification_service').setLevel(logging.ERROR)
    logging.getLogger('app.middleware.security').setLevel(logging.WARNING)
    
    # Configurar logger root para INFO
    logging.getLogger().setLevel(logging.INFO)
    
    print("✅ Configuração de desenvolvimento aplicada - logs reduzidos")

def disable_monitoring_for_dev():
    """Desabilitar monitoramento excessivo em desenvolvimento"""
    os.environ['DISABLE_PERFORMANCE_MONITORING'] = 'true'
    os.environ['DISABLE_METRICS_COLLECTION'] = 'true'
    os.environ['DISABLE_HEALTH_CHECKS'] = 'true'
    print("⚠️ Monitoramento desabilitado para desenvolvimento")

if __name__ == "__main__":
    configure_dev_logging()
    disable_monitoring_for_dev()
