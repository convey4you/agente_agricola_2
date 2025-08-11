# app/monitoring_integration.py
"""
PROMPT 3: Integração do Sistema de Monitoramento
Inicializa e configura todos os componentes de monitoramento
"""

import logging
import threading
import atexit
from flask import Flask, request, g
from app.utils.logging_config import setup_logging, StructuredFormatter, audit_logger
from app.utils.metrics import metrics, system_metrics, track_performance
from app.utils.health_checks import health_manager
from app.utils.monitoring_alerts_fixed import alert_manager
from app.utils.bot_detection import bot_detector

class MonitoringIntegration:
    """Classe principal para integração do sistema de monitoramento"""
    
    def __init__(self):
        self.initialized = False
        self.background_threads = []
        
    def initialize(self, app: Flask):
        """Inicializa todo o sistema de monitoramento"""
        try:
            # 1. Configurar logging estruturado
            self._setup_logging(app)
            
            # 2. Configurar métricas
            self._setup_metrics(app)
            
            # 3. Configurar health checks
            self._setup_health_checks(app)
            
            # 4. Configurar alertas
            self._setup_alerts(app)
            
            # 5. Configurar middleware de monitoramento
            self._setup_middleware(app)
            
            # 6. Iniciar processos em background
            self._start_background_processes()
            
            # 7. Registrar cleanup
            self._register_cleanup()
            
            self.initialized = True
            logging.info("Sistema de monitoramento PROMPT 3 inicializado com sucesso")
            
            # Log de auditoria
            audit_logger.log_system_event(
                event_type='monitoring_initialized',
                description='Sistema de monitoramento inicializado com sucesso',
                details={'components': ['logging', 'metrics', 'health_checks', 'alerts']}
            )
            
        except Exception as e:
            logging.error(f"Erro ao inicializar sistema de monitoramento: {str(e)}")
            raise
    
    def _setup_logging(self, app: Flask):
        """Configura o sistema de logging estruturado"""
        # Configurar logging principal
        setup_logging(
            level=app.config.get('LOG_LEVEL', 'INFO'),
            log_file=app.config.get('LOG_FILE', 'logs/agrotech.log'),
            json_format=app.config.get('JSON_LOGGING', True)
        )
        
        # Configurar handler específico para erros
        error_handler = logging.FileHandler('logs/agrotech_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        
        # Configurar handler para auditoria
        audit_handler = logging.FileHandler('logs/agrotech_audit.log')
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(StructuredFormatter())
        
        # Adicionar handlers ao logger root
        root_logger = logging.getLogger()
        root_logger.addHandler(error_handler)
        
        # Configurar logger de auditoria
        audit_log = logging.getLogger('audit')
        audit_log.addHandler(audit_handler)
        audit_log.setLevel(logging.INFO)
        
        logging.info("Sistema de logging estruturado configurado")
    
    def _setup_metrics(self, app: Flask):
        """Configura o sistema de métricas"""
        # Configurar métricas da aplicação
        metrics.reset()
        
        # Configurar métricas do sistema se habilitado
        if app.config.get('SYSTEM_METRICS_ENABLED', True):
            system_metrics.start_collection(
                interval=app.config.get('METRICS_COLLECTION_INTERVAL', 60)
            )
            logging.info("Coleta de métricas do sistema iniciada")
        
        logging.info("Sistema de métricas configurado")
    
    def _setup_health_checks(self, app: Flask):
        """Configura o sistema de health checks"""
        # Configurar intervalo de execução
        check_interval = app.config.get('HEALTH_CHECK_INTERVAL', 300)  # 5 minutos
        
        # Iniciar execução periódica
        if app.config.get('HEALTH_CHECKS_ENABLED', True):
            health_manager.start_periodic_checks(interval_seconds=check_interval)
            logging.info(f"Health checks configurados com intervalo de {check_interval}s")
    
    def _setup_alerts(self, app: Flask):
        """Configura o sistema de alertas"""
        # Configurar alertas baseado na configuração
        alert_config = app.config.get('ALERT_CONFIG', {})
        
        # Configurar notificações por email se habilitado
        if alert_config.get('email_enabled', False):
            alert_manager.configure_email(
                smtp_host=alert_config.get('smtp_host'),
                smtp_port=alert_config.get('smtp_port', 587),
                smtp_user=alert_config.get('smtp_user'),
                smtp_password=alert_config.get('smtp_password'),
                from_email=alert_config.get('from_email'),
                to_emails=alert_config.get('to_emails', [])
            )
        
        # Configurar regras de alerta padrão
        self._setup_default_alert_rules()
        
        # Iniciar processamento de alertas
        if app.config.get('ALERTS_ENABLED', True):
            alert_manager.start_processing()
            logging.info("Sistema de alertas configurado e iniciado")
    
    def _setup_default_alert_rules(self):
        """Configura regras de alerta padrão"""
        # CPU alto
        alert_manager.add_threshold_rule(
            name="CPU Usage High",
            metric_name="system_cpu_percent",
            threshold=85.0,
            comparison="greater_than",
            severity="warning"
        )
        
        alert_manager.add_threshold_rule(
            name="CPU Usage Critical",
            metric_name="system_cpu_percent",
            threshold=95.0,
            comparison="greater_than",
            severity="critical"
        )
        
        # Memória alta
        alert_manager.add_threshold_rule(
            name="Memory Usage High",
            metric_name="system_memory_percent",
            threshold=85.0,
            comparison="greater_than",
            severity="warning"
        )
        
        alert_manager.add_threshold_rule(
            name="Memory Usage Critical",
            metric_name="system_memory_percent",
            threshold=95.0,
            comparison="greater_than",
            severity="critical"
        )
        
        # Disco cheio
        alert_manager.add_threshold_rule(
            name="Disk Usage High",
            metric_name="system_disk_percent",
            threshold=90.0,
            comparison="greater_than",
            severity="warning"
        )
        
        # Response time alto
        alert_manager.add_threshold_rule(
            name="Response Time High",
            metric_name="avg_response_time",
            threshold=1000.0,  # 1 segundo
            comparison="greater_than",
            severity="warning"
        )
        
        # Muitos erros (ajustado para reduzir falsos positivos de bots)
        alert_manager.add_threshold_rule(
            name="Error Rate High",
            metric_name="error_rate",
            threshold=15.0,  # 15% (mais tolerante a tráfego de bot)
            comparison="greater_than",
            severity="critical"
        )
        
        logging.info("Regras de alerta padrão configuradas")
    
    def _setup_middleware(self, app: Flask):
        """Configura middleware de monitoramento"""
        
        @app.before_request
        def before_request():
            """Executa antes de cada request"""
            from flask import request, g
            import time
            
            # Marcar início do request
            g.start_time = time.time()
            
            # Detectar bots
            bot_info = bot_detector.is_bot_request()
            g.bot_info = bot_info
            
            # Log detecção de bot se necessário
            if bot_info.get('is_bot', False) and bot_info.get('confidence', 0) > 0.8:
                reasons = bot_info.get('reasons', [])
                logging.info(f"Bot detectado: {reasons}")
            
            # Incrementar contadores (excluir bots maliciosos)
            if not bot_info.get('should_exclude_metrics', False):
                metrics.increment_counter('total_requests')
                metrics.increment_counter(f'requests_by_method_{request.method.lower()}')
                metrics.increment_counter(f'requests_by_endpoint_{request.endpoint or "unknown"}')
            else:
                metrics.increment_counter('bot_requests_filtered')
                
            # Contadores específicos de bots
            if bot_info['is_bot']:
                metrics.increment_counter('bot_requests_total')
                if bot_info.get('bot_type'):
                    metrics.increment_counter(f'bot_requests_{bot_info["bot_type"]}')
        
        @app.after_request
        def after_request(response):
            """Executa após cada request"""
            from flask import g
            import time
            
            if hasattr(g, 'start_time'):
                # Calcular tempo de resposta
                response_time = (time.time() - g.start_time) * 1000  # em ms
                
                # Verificar se deve excluir métricas (bots maliciosos)
                bot_info = getattr(g, 'bot_info', {})
                should_exclude = bot_info.get('should_exclude_metrics', False)
                
                if not should_exclude:
                    # Registrar métricas normais
                    metrics.add_histogram_value('response_time', response_time)
                    metrics.set_gauge('last_response_time', response_time)
                    
                    # Status codes
                    metrics.increment_counter(f'responses_by_status_{response.status_code}')
                    
                    if response.status_code >= 400:
                        metrics.increment_counter('error_responses')
                else:
                    # Métricas separadas para bots filtrados
                    metrics.add_histogram_value('bot_response_time', response_time)
                    metrics.increment_counter(f'bot_responses_by_status_{response.status_code}')
            
            return response
        
        @app.teardown_appcontext
        def teardown_appcontext(error):
            """Executa ao final do contexto da aplicação"""
            if error:
                # Log de erro estruturado
                logging.error(f"Erro no contexto da aplicação: {str(error)}")
                metrics.increment_counter('application_errors')
        
        logging.info("Middleware de monitoramento configurado")
    
    def _start_background_processes(self):
        """Inicia processos em background"""
        # Thread para coleta de métricas do sistema
        if system_metrics:
            metrics_thread = threading.Thread(
                target=system_metrics.start_collection,
                daemon=True,
                name="SystemMetricsCollector"
            )
            metrics_thread.start()
            self.background_threads.append(metrics_thread)
        
        # Thread para health checks periódicos
        health_thread = threading.Thread(
            target=health_manager.start_periodic_checks,
            daemon=True,
            name="HealthCheckManager"
        )
        health_thread.start()
        self.background_threads.append(health_thread)
        
        # Thread para processamento de alertas
        alerts_thread = threading.Thread(
            target=alert_manager.start_processing,
            daemon=True,
            name="AlertManager"
        )
        alerts_thread.start()
        self.background_threads.append(alerts_thread)
        
        logging.info(f"Iniciados {len(self.background_threads)} processos em background")
    
    def _register_cleanup(self):
        """Registra funções de cleanup"""
        def cleanup():
            """Função de cleanup ao finalizar aplicação"""
            try:
                # Parar coleta de métricas
                if system_metrics:
                    if hasattr(system_metrics, 'stop_collection'):
                        system_metrics.stop_collection()
                    elif hasattr(system_metrics, 'stop'):
                        system_metrics.stop()
                
                # Parar health checks
                health_manager.stop_periodic_checks()
                
                # Parar processamento de alertas
                alert_manager.stop_processing()
                
                # Log final
                audit_logger.log_system_event(
                    event_type='monitoring_shutdown',
                    description='Sistema de monitoramento finalizado',
                    details={'clean_shutdown': True}
                )
                
                logging.info("Sistema de monitoramento finalizado com sucesso")
                
            except Exception as e:
                logging.error(f"Erro durante cleanup do monitoramento: {str(e)}")
        
        atexit.register(cleanup)
    
    def get_status(self):
        """Retorna status do sistema de monitoramento"""
        return {
            'initialized': self.initialized,
            'components': {
                'logging': True,
                'metrics': metrics is not None,
                'system_metrics': system_metrics is not None,
                'health_checks': health_manager is not None,
                'alerts': alert_manager is not None
            },
            'background_threads': len(self.background_threads),
            'threads_alive': sum(1 for t in self.background_threads if t.is_alive())
        }

# Instância global
monitoring_integration = MonitoringIntegration()

def init_monitoring(app: Flask):
    """Função helper para inicializar monitoramento"""
    monitoring_integration.initialize(app)
    return monitoring_integration
