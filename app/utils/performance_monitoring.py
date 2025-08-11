# app/utils/performance_monitoring.py
"""
Sistema de monitorização de performance e alertas - Sprint 4 Prompt 3
"""
import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
from flask import current_app, request, g
from collections import defaultdict, deque
import threading
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Métrica de performance"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags or {}
        }


@dataclass
class SystemAlert:
    """Alerta de sistema"""
    id: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    title: str
    message: str
    metric_name: str
    metric_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'title': self.title,
            'message': self.message,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class PerformanceMonitor:
    """Monitor de performance do sistema"""
    
    def __init__(self):
        self.metrics = deque(maxlen=1000)  # Últimas 1000 métricas
        self.alerts = []
        self.thresholds = {
            'response_time': 2.0,  # segundos
            'cpu_usage': 80.0,     # porcentagem
            'memory_usage': 85.0,  # porcentagem
            'disk_usage': 90.0,    # porcentagem
            'active_connections': 1000,  # número de conexões
            'error_rate': 15.0,    # porcentagem (ajustado para bots)
            'cache_hit_rate': 60.0  # porcentagem (mais tolerante durante startup)
        }
        self.enabled = True
        self._lock = threading.Lock()
        self.request_times = deque(maxlen=100)
        self.error_count = 0
        self.total_requests = 0
        
        # Sistema de cooldown para alertas
        self.alert_cooldown = {}  # {metric_name: last_alert_time}
        self.cooldown_seconds = 300  # 5 minutos entre alertas do mesmo tipo
    
    def add_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Adicionar métrica de performance"""
        if not self.enabled:
            return
        
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
        with self._lock:
            self.metrics.append(metric)
            
        # Verificar se precisa gerar alerta
        self._check_threshold(metric)
        
        logger.debug(f"Métrica adicionada: {name}={value}{unit}")
    
    def _check_threshold(self, metric: PerformanceMetric):
        """Verificar se métrica ultrapassou threshold"""
        threshold = self.thresholds.get(metric.name)
        if not threshold:
            return
        
        # Verificar cooldown para evitar spam de alertas
        now = time.time()
        last_alert = self.alert_cooldown.get(metric.name, 0)
        if now - last_alert < self.cooldown_seconds:
            return  # Ainda em cooldown
        
        # Diferentes tipos de verificação
        if metric.name == 'cache_hit_rate':
            # Cache hit rate - alerta se estiver ABAIXO do threshold
            if metric.value < threshold:
                self.alert_cooldown[metric.name] = now  # Atualizar cooldown
                self._generate_alert(
                    level='WARNING',
                    title='Taxa de Cache Baixa',
                    message=f'Taxa de cache hit está em {metric.value:.1f}%, abaixo do mínimo de {threshold}%',
                    metric=metric,
                    threshold=threshold
                )
        else:
            # Outras métricas - alerta se estiver ACIMA do threshold
            if metric.value > threshold:
                self.alert_cooldown[metric.name] = now  # Atualizar cooldown
                level = 'CRITICAL' if metric.value > threshold * 1.2 else 'WARNING'
                self._generate_alert(
                    level=level,
                    title=f'{metric.name.replace("_", " ").title()} Alto',
                    message=f'{metric.name} está em {metric.value:.1f}{metric.unit}, acima do threshold de {threshold}{metric.unit}',
                    metric=metric,
                    threshold=threshold
                )
    
    def _generate_alert(self, level: str, title: str, message: str, metric: PerformanceMetric, threshold: float):
        """Gerar alerta de sistema"""
        import uuid
        
        alert = SystemAlert(
            id=str(uuid.uuid4()),
            level=level,
            title=title,
            message=message,
            metric_name=metric.name,
            metric_value=metric.value,
            threshold=threshold,
            timestamp=datetime.now()
        )
        
        with self._lock:
            self.alerts.append(alert)
            
        logger.warning(f"Alerta gerado: {title} - {message}")
        
        # Tentar enviar alerta via notification service
        try:
            self._send_alert_notification(alert)
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de alerta: {e}")
    
    def _send_alert_notification(self, alert: SystemAlert):
        """Enviar notificação de alerta"""
        try:
            from app.services.notification_service import NotificationService
            
            # Só enviar alertas CRITICAL e WARNING
            if alert.level in ['CRITICAL', 'WARNING']:
                NotificationService.send_system_alert(
                    title=alert.title,
                    message=alert.message,
                    severity=alert.level  # Usar 'severity' ao invés de 'level'
                )
        except ImportError:
            logger.debug("NotificationService não disponível")
    
    def record_request(self, response_time: float, status_code: int):
        """Registrar tempo de resposta de request"""
        with self._lock:
            self.request_times.append(response_time)
            self.total_requests += 1
            
            if status_code >= 400:
                self.error_count += 1
        
        # Adicionar métricas
        self.add_metric('response_time', response_time, 's', {'status_code': str(status_code)})
        
        # Calcular taxa de erro
        if self.total_requests > 0:
            error_rate = (self.error_count / self.total_requests) * 100
            self.add_metric('error_rate', error_rate, '%')
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obter métricas do sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric('cpu_usage', cpu_percent, '%')
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.add_metric('memory_usage', memory_percent, '%')
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self.add_metric('disk_usage', disk_percent, '%')
            
            # Métricas de rede
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory_percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': disk_percent,
                    'used': disk.used
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas do sistema: {e}")
            return {}
    
    def get_cache_metrics(self) -> Dict[str, Any]:
        """Obter métricas de cache"""
        try:
            from app.utils.cache_manager import cache
            
            stats = cache.get_stats()
            if stats:
                hit_rate = stats.get('hit_rate', 0)
                self.add_metric('cache_hit_rate', hit_rate, '%')
                
                return {
                    'hit_rate': hit_rate,
                    'keyspace_hits': stats.get('keyspace_hits', 0),
                    'keyspace_misses': stats.get('keyspace_misses', 0),
                    'used_memory': stats.get('used_memory', 'N/A'),
                    'connected_clients': stats.get('connected_clients', 0)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas de cache: {e}")
            return {}
    
    def get_database_metrics(self) -> Dict[str, Any]:
        """Obter métricas de banco de dados"""
        try:
            from flask import current_app
            from app import db
            from sqlalchemy import text
            
            # Verificar se estamos em um contexto de aplicação
            if not current_app:
                return {}
            
            with current_app.app_context():
                with db.engine.connect() as conn:
                    # Verificar se é PostgreSQL ou SQLite
                    engine_name = db.engine.dialect.name
                    
                    if engine_name == 'postgresql':
                        # Conexões ativas - PostgreSQL
                        active_connections_query = text("""
                            SELECT count(*) as active_connections
                            FROM pg_stat_activity 
                            WHERE state = 'active'
                        """)
                        
                        result = conn.execute(active_connections_query).fetchone()
                        active_connections = result[0] if result else 0
                        
                        # Tamanho do banco - PostgreSQL
                        db_size_query = text("""
                            SELECT pg_size_pretty(pg_database_size(current_database())) as size
                        """)
                        
                        result = conn.execute(db_size_query).fetchone()
                        db_size = result[0] if result else 'N/A'
                        
                    else:
                        # SQLite - métricas básicas
                        active_connections = 1  # SQLite só tem uma conexão ativa
                        db_size = 'N/A'  # Tamanho não facilmente disponível no SQLite
                    
                    self.add_metric('active_connections', active_connections, 'count')
                    
                    return {
                        'active_connections': active_connections,
                        'database_size': db_size,
                        'max_connections': 100,  # Valor padrão
                        'engine': engine_name
                    }
                
        except Exception as e:
            logger.error(f"Erro ao obter métricas de banco: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obter resumo de performance"""
        with self._lock:
            recent_metrics = list(self.metrics)[-50:]  # Últimas 50 métricas
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            
            # Calcular médias
            avg_response_time = 0
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
            
            error_rate = 0
            if self.total_requests > 0:
                error_rate = (self.error_count / self.total_requests) * 100
            
            return {
                'system': self.get_system_metrics(),
                'cache': self.get_cache_metrics(),
                'database': self.get_database_metrics(),
                'requests': {
                    'total': self.total_requests,
                    'errors': self.error_count,
                    'error_rate': error_rate,
                    'avg_response_time': avg_response_time
                },
                'alerts': {
                    'active': len(active_alerts),
                    'total': len(self.alerts)
                },
                'metrics_count': len(recent_metrics)
            }
    
    def get_metrics_history(self, metric_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Obter histórico de uma métrica específica"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            filtered_metrics = [
                metric.to_dict() 
                for metric in self.metrics 
                if metric.name == metric_name and metric.timestamp >= cutoff_time
            ]
        
        return sorted(filtered_metrics, key=lambda x: x['timestamp'])
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obter alertas ativos"""
        with self._lock:
            active_alerts = [
                alert.to_dict() 
                for alert in self.alerts 
                if not alert.resolved
            ]
        
        return sorted(active_alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolver alerta"""
        with self._lock:
            for alert in self.alerts:
                if alert.id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    logger.info(f"Alerta {alert_id} resolvido")
                    return True
        
        return False
    
    def set_threshold(self, metric_name: str, threshold: float):
        """Definir threshold para métrica"""
        self.thresholds[metric_name] = threshold
        logger.info(f"Threshold para {metric_name} definido como {threshold}")
    
    def enable_monitoring(self):
        """Ativar monitorização"""
        self.enabled = True
        logger.info("Monitorização de performance ativada")
    
    def disable_monitoring(self):
        """Desativar monitorização"""
        self.enabled = False
        logger.info("Monitorização de performance desativada")


def monitor_performance(func):
    """Decorator para monitorizar performance de funções"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Registrar métrica de performance
            performance_monitor.add_metric(
                name=f'function_{func.__name__}_time',
                value=execution_time,
                unit='s',
                tags={'function': func.__name__, 'module': func.__module__}
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Registrar erro
            performance_monitor.add_metric(
                name=f'function_{func.__name__}_error',
                value=1,
                unit='count',
                tags={'function': func.__name__, 'error': str(e)}
            )
            
            raise
    
    return wrapper


def monitor_request_performance(app):
    """Middleware para monitorizar performance de requests"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            
            # Registrar performance do request
            performance_monitor.record_request(response_time, response.status_code)
            
            # Adicionar header de performance
            response.headers['X-Response-Time'] = f"{response_time:.3f}s"
        
        return response


class PerformanceCollector:
    """Coletor de métricas de performance em background"""
    
    def __init__(self, monitor: PerformanceMonitor, interval: int = 60):
        self.monitor = monitor
        self.interval = interval
        self.running = False
        self.thread = None
        self.app = None  # Referência para a aplicação Flask
    
    def set_app(self, app):
        """Definir aplicação Flask"""
        self.app = app
    
    def start(self):
        """Iniciar coleta em background"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.thread.start()
        logger.info("Coletor de métricas iniciado")
    
    def stop(self):
        """Parar coleta"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Coletor de métricas parado")
    
    def _collect_loop(self):
        """Loop de coleta de métricas"""
        while self.running:
            try:
                # Coletar métricas do sistema
                self.monitor.get_system_metrics()
                
                # Coletar métricas de cache
                self.monitor.get_cache_metrics()
                
                # Coletar métricas de banco (com contexto da aplicação)
                if self.app:
                    with self.app.app_context():
                        self.monitor.get_database_metrics()
                else:
                    # Sem contexto, pular métricas de banco
                    logger.debug("Contexto de aplicação não disponível - pulando métricas de banco")
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
                time.sleep(self.interval)


# Instância global do monitor
performance_monitor = PerformanceMonitor()

# Instância do coletor
performance_collector = PerformanceCollector(performance_monitor, interval=60)


def init_performance_monitoring(app):
    """Inicializar monitorização de performance"""
    
    # Configurar middleware
    monitor_request_performance(app)
    
    # Configurar aplicação no coletor
    performance_collector.set_app(app)
    
    # Iniciar coletor em background
    performance_collector.start()
    
    # Registrar shutdown handler
    import atexit
    atexit.register(performance_collector.stop)
    
    logger.info("Sistema de monitorização de performance iniciado")


def get_performance_dashboard_data():
    """Obter dados para dashboard de performance"""
    return {
        'summary': performance_monitor.get_performance_summary(),
        'alerts': performance_monitor.get_active_alerts(),
        'thresholds': performance_monitor.thresholds,
        'enabled': performance_monitor.enabled
    }
