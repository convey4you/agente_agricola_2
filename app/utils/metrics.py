# app/utils/metrics.py
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import request, g, has_request_context
from functools import wraps
import json
import logging

class MetricsCollector:
    """Coletor de métricas de performance"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        self.start_time = datetime.utcnow()
        
        # Métricas de negócio
        self.business_metrics = {
            'users_registered_today': 0,
            'cultures_created_today': 0,
            'recommendations_generated_today': 0,
            'alerts_sent_today': 0,
            'marketplace_items_listed_today': 0
        }
        
        logger = logging.getLogger(__name__)
        logger.info("Metrics collector initialized", extra={
            'extra_fields': {
                'component': 'metrics',
                'action': 'initialization'
            }
        })
    
    def increment_counter(self, name, value=1, tags=None):
        """Incrementar contador"""
        with self.lock:
            key = self._build_key(name, tags)
            self.counters[key] += value
            
            # Atualizar métricas de negócio
            self._update_business_metrics(name, value)
    
    def reset(self):
        """Resetar todas as métricas"""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.business_metrics = {
                'users_registered_today': 0,
                'cultures_created_today': 0,
                'recommendations_generated_today': 0,
                'alerts_sent_today': 0,
                'marketplace_items_listed_today': 0
            }
            self.start_time = datetime.utcnow()
            
            logging.getLogger(__name__).info("Metrics collector reset", extra={
                'component': 'metrics',
                'action': 'reset'
            })
    
    def set_gauge(self, name, value, tags=None):
        """Definir valor de gauge"""
        with self.lock:
            key = self._build_key(name, tags)
            self.gauges[key] = value
    
    def add_histogram_value(self, name, value, tags=None):
        """Adicionar valor ao histograma"""
        self.record_histogram(name, value, tags)
    
    def record_histogram(self, name, value, tags=None):
        """Registrar valor em histograma"""
        with self.lock:
            key = self._build_key(name, tags)
            self.histograms[key].append({
                'value': value,
                'timestamp': datetime.utcnow()
            })
    
    def record_timing(self, name, duration, tags=None):
        """Registrar tempo de execução"""
        self.record_histogram(f"{name}.duration", duration, tags)
        
        # Log performance crítica
        if duration > 5.0:  # Mais de 5 segundos
            logging.getLogger(__name__).warning(
                f"Slow operation detected: {name}",
                extra={
                    'component': 'performance',
                    'operation': name,
                    'duration': duration,
                    'threshold_exceeded': True,
                    'tags': tags or {}
                }
            )
    
    def _build_key(self, name, tags):
        """Construir chave da métrica"""
        if tags:
            tag_str = ','.join([f"{k}={v}" for k, v in sorted(tags.items())])
            return f"{name}[{tag_str}]"
        return name
    
    def _update_business_metrics(self, metric_name, value):
        """Atualizar métricas de negócio"""
        today = datetime.utcnow().date()
        
        if 'user.register' in metric_name:
            self.business_metrics['users_registered_today'] += value
        elif 'culture.create' in metric_name:
            self.business_metrics['cultures_created_today'] += value
        elif 'recommendation.generate' in metric_name:
            self.business_metrics['recommendations_generated_today'] += value
        elif 'alert.send' in metric_name:
            self.business_metrics['alerts_sent_today'] += value
        elif 'marketplace.create' in metric_name:
            self.business_metrics['marketplace_items_listed_today'] += value
    
    def get_metrics_summary(self):
        """Obter resumo das métricas"""
        with self.lock:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime_seconds': uptime,
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {},
                'business_metrics': self.business_metrics.copy()
            }
            
            # Calcular estatísticas dos histogramas
            for key, values in self.histograms.items():
                if values:
                    numeric_values = [v['value'] for v in values]
                    summary['histograms'][key] = {
                        'count': len(numeric_values),
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'avg': sum(numeric_values) / len(numeric_values),
                        'p50': self._percentile(numeric_values, 50),
                        'p95': self._percentile(numeric_values, 95),
                        'p99': self._percentile(numeric_values, 99)
                    }
            
            return summary
    
    def _percentile(self, values, percentile):
        """Calcular percentil"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def reset_daily_metrics(self):
        """Resetar métricas diárias"""
        with self.lock:
            self.business_metrics = {
                'users_registered_today': 0,
                'cultures_created_today': 0,
                'recommendations_generated_today': 0,
                'alerts_sent_today': 0,
                'marketplace_items_listed_today': 0
            }

# Instância global do coletor
metrics = MetricsCollector()

def track_performance(metric_name=None, tags=None):
    """Decorator para rastrear performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = metric_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                metrics.record_timing(name, duration, tags)
                metrics.increment_counter(f"{name}.calls", tags=tags)
                metrics.increment_counter(f"{name}.success", tags=tags)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_timing(name, duration, tags)
                metrics.increment_counter(f"{name}.calls", tags=tags)
                metrics.increment_counter(f"{name}.errors", tags={
                    **(tags or {}),
                    'error_type': type(e).__name__
                })
                
                raise
        
        return wrapper
    return decorator

class SystemMetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
    
    def start_collection(self, interval=60):
        """Iniciar coleta de métricas do sistema com intervalo específico"""
        self.interval = interval
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collect_loop)
            self.thread.daemon = True
            self.thread.start()
            
            self.logger.info("System metrics collection started", extra={
                'extra_fields': {
                    'component': 'system_metrics',
                    'action': 'start',
                    'interval': interval
                }
            })
    
    def start(self):
        """Iniciar coleta de métricas do sistema"""
        self.start_collection()  # Usar método padrão
    
    def stop(self):
        """Parar coleta de métricas"""
        self.running = False
        if self.thread:
            self.thread.join()
            
        self.logger.info("System metrics collection stopped", extra={
            'extra_fields': {
                'component': 'system_metrics',
                'action': 'stop'
            }
        })
    
    def _collect_loop(self):
        """Loop de coleta de métricas"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(30)  # Coletar a cada 30 segundos
            except Exception as e:
                self.logger.error(f"Erro na coleta de métricas: {e}", exc_info=True)
                time.sleep(60)  # Aguardar mais tempo em caso de erro
    
    def _collect_system_metrics(self):
        """Coletar métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.set_gauge('system.cpu.percent', cpu_percent)
            
            # Memória
            memory = psutil.virtual_memory()
            metrics.set_gauge('system.memory.percent', memory.percent)
            metrics.set_gauge('system.memory.available_mb', memory.available / 1024 / 1024)
            metrics.set_gauge('system.memory.used_mb', memory.used / 1024 / 1024)
            
            # Disco
            disk = psutil.disk_usage('/')
            metrics.set_gauge('system.disk.percent', disk.percent)
            metrics.set_gauge('system.disk.free_gb', disk.free / 1024 / 1024 / 1024)
            metrics.set_gauge('system.disk.used_gb', disk.used / 1024 / 1024 / 1024)
            
            # Processos
            process_count = len(psutil.pids())
            metrics.set_gauge('system.processes.count', process_count)
            
            # Conexões de rede
            connections = psutil.net_connections()
            metrics.set_gauge('system.network.connections', len(connections))
            
            # Alertas de recursos
            if cpu_percent > 80:
                self.logger.warning("High CPU usage detected", extra={
                    'component': 'system_alert',
                    'metric': 'cpu_usage',
                    'value': cpu_percent,
                    'threshold': 80
                })
            
            if memory.percent > 85:
                self.logger.warning("High memory usage detected", extra={
                    'component': 'system_alert',
                    'metric': 'memory_usage',
                    'value': memory.percent,
                    'threshold': 85
                })
        
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def get_current_stats(self):
        """Obter estatísticas atuais do sistema"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}

# Instância global do coletor de sistema
system_metrics = SystemMetricsCollector()

def track_request_metrics():
    """Middleware para rastrear métricas de requisições"""
    def before_request():
        g.start_time = time.time()
        
        # Incrementar contador de requisições
        if has_request_context():
            metrics.increment_counter('http.requests.total', tags={
                'method': request.method,
                'endpoint': request.endpoint or 'unknown'
            })
    
    def after_request(response):
        if hasattr(g, 'start_time') and has_request_context():
            duration = time.time() - g.start_time
            
            # Registrar tempo de resposta
            metrics.record_timing('http.request.duration', duration, tags={
                'method': request.method,
                'endpoint': request.endpoint or 'unknown',
                'status_code': response.status_code
            })
            
            # Incrementar contador de respostas
            metrics.increment_counter('http.responses.total', tags={
                'method': request.method,
                'endpoint': request.endpoint or 'unknown',
                'status_code': response.status_code
            })
            
            # Alertar sobre requisições lentas
            if duration > 2.0:
                logging.getLogger(__name__).warning(
                    f"Slow HTTP request: {request.method} {request.path}",
                    extra={
                        'extra_fields': {
                            'component': 'http_performance',
                            'method': request.method,
                            'path': request.path,
                            'duration': duration,
                            'status_code': response.status_code
                        }
                    }
                )
        
        return response
    
    return before_request, after_request
