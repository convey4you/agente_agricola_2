"""
Sistema de Analytics e Tracking - AgroTech Portugal
Coleta e análise de eventos, métricas de negócio e performance
"""

import json
import time
from datetime import datetime, timedelta
from flask import request, g, current_app, session
from functools import wraps
import logging
from typing import Dict, Any, Optional, List
import uuid
from dataclasses import dataclass, asdict
import threading
from queue import Queue

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Classe para representar um evento de analytics"""
    event_id: str
    event_name: str
    timestamp: str
    user_id: Optional[int]
    session_id: Optional[str]
    properties: Dict[str, Any]
    context: Dict[str, Any]

class AnalyticsTracker:
    """Sistema de tracking de eventos e métricas"""
    
    def __init__(self, app=None):
        self.app = app
        self.events_queue = Queue()
        self.buffer = []
        self.buffer_size = 100
        self.flush_interval = 60
        self.background_thread = None
        self.running = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar tracker com a aplicação"""
        self.app = app
        
        # Configurações padrão
        app.config.setdefault('ANALYTICS_ENABLED', True)
        app.config.setdefault('ANALYTICS_BUFFER_SIZE', 100)
        app.config.setdefault('ANALYTICS_FLUSH_INTERVAL', 60)
        app.config.setdefault('ANALYTICS_DEBUG', False)
        
        # Configurações InfluxDB
        app.config.setdefault('INFLUXDB_URL', 'http://influxdb:8086')
        app.config.setdefault('INFLUXDB_TOKEN', 'agrotech-analytics-token')
        app.config.setdefault('INFLUXDB_ORG', 'agrotech')
        app.config.setdefault('INFLUXDB_BUCKET', 'agrotech-events')
        
        # Registrar middleware
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Iniciar thread de processamento
        self.start_background_processing()
        
        # Registrar shutdown
        import atexit
        atexit.register(self.stop_background_processing)
    
    def start_background_processing(self):
        """Iniciar processamento em background"""
        if self.background_thread is None or not self.background_thread.is_alive():
            self.running = True
            self.background_thread = threading.Thread(target=self._background_processor)
            self.background_thread.daemon = True
            self.background_thread.start()
            logger.info("Analytics background processing started")
    
    def stop_background_processing(self):
        """Parar processamento em background"""
        self.running = False
        if self.background_thread:
            self.flush_events()  # Enviar eventos restantes
            self.background_thread.join(timeout=5)
            logger.info("Analytics background processing stopped")
    
    def _background_processor(self):
        """Processador em background para flush periódico"""
        while self.running:
            try:
                time.sleep(self.flush_interval)
                if len(self.buffer) > 0:
                    self.flush_events()
            except Exception as e:
                logger.error(f"Error in background processor: {e}")
    
    def track_event(self, event_name: str, properties: Dict[str, Any] = None, user_id: Optional[int] = None):
        """Rastrear evento personalizado"""
        if not current_app.config.get('ANALYTICS_ENABLED', True):
            return
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_name=event_name,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id or getattr(g, 'user_id', None),
            session_id=getattr(g, 'session_id', None),
            properties=properties or {},
            context=self._get_request_context()
        )
        
        self._add_to_buffer(event)
        
        if current_app.config.get('ANALYTICS_DEBUG'):
            logger.debug(f"Event tracked: {event_name} - {properties}")
    
    def track_page_view(self, page: str, title: str = None):
        """Rastrear visualização de página"""
        self.track_event('page_view', {
            'page': page,
            'title': title,
            'referrer': request.headers.get('Referer'),
            'user_agent': request.headers.get('User-Agent')
        })
    
    def track_user_action(self, action: str, resource_type: str, resource_id: Optional[int] = None, details: Dict[str, Any] = None):
        """Rastrear ação do usuário"""
        self.track_event('user_action', {
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {}
        })
    
    def track_conversion(self, conversion_type: str, value: float = None, currency: str = 'EUR'):
        """Rastrear conversão/objetivo"""
        self.track_event('conversion', {
            'conversion_type': conversion_type,
            'value': value,
            'currency': currency
        })
    
    def track_error(self, error_type: str, error_message: str, stack_trace: str = None):
        """Rastrear erro"""
        self.track_event('error', {
            'error_type': error_type,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'url': request.url if request else None,
            'endpoint': request.endpoint if request else None
        })
    
    def track_performance(self, metric_name: str, value: float, unit: str = 'ms'):
        """Rastrear métrica de performance"""
        self.track_event('performance', {
            'metric_name': metric_name,
            'value': value,
            'unit': unit
        })
    
    def track_feature_usage(self, feature_name: str, usage_type: str = 'used', metadata: Dict[str, Any] = None):
        """Rastrear uso de funcionalidades"""
        self.track_event('feature_usage', {
            'feature_name': feature_name,
            'usage_type': usage_type,
            'metadata': metadata or {}
        })
    
    def _before_request(self):
        """Middleware executado antes da requisição"""
        g.request_start_time = time.time()
        g.session_id = self._get_or_create_session_id()
        
        # Rastrear início da requisição para endpoints não estáticos
        if request.endpoint and not self._is_static_request():
            self.track_event('request_start', {
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path
            })
    
    def _after_request(self, response):
        """Middleware executado após a requisição"""
        if hasattr(g, 'request_start_time') and not self._is_static_request():
            duration = (time.time() - g.request_start_time) * 1000  # ms
            
            # Rastrear fim da requisição
            self.track_event('request_end', {
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration, 2),
                'response_size': len(response.get_data()) if response.get_data() else 0
            })
            
            # Rastrear performance se for lenta
            if duration > 2000:  # > 2 segundos
                self.track_performance('slow_request', duration, 'ms')
            
            # Rastrear erros HTTP
            if response.status_code >= 400:
                self.track_error('http_error', f"HTTP {response.status_code}", request.url)
        
        return response
    
    def _is_static_request(self):
        """Verificar se é uma requisição para arquivo estático"""
        if not request.endpoint:
            return True
        return request.endpoint.startswith(('static', 'favicon'))
    
    def _get_or_create_session_id(self):
        """Obter ou criar ID da sessão"""
        if hasattr(g, 'session_id'):
            return g.session_id
        
        # Tentar obter da sessão Flask
        if 'analytics_session_id' not in session:
            session['analytics_session_id'] = str(uuid.uuid4())
            session.permanent = True  # Manter sessão persistente
        
        return session['analytics_session_id']
    
    def _get_request_context(self):
        """Obter contexto da requisição"""
        if not request:
            return {}
        
        return {
            'ip_address': self._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', ''),
            'referer': request.headers.get('Referer', ''),
            'accept_language': request.headers.get('Accept-Language', ''),
            'method': request.method,
            'path': request.path,
            'query_string': request.query_string.decode('utf-8') if request.query_string else '',
            'is_mobile': self._is_mobile_request(),
            'browser': self._get_browser_info()
        }
    
    def _get_client_ip(self):
        """Obter IP real do cliente"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def _is_mobile_request(self):
        """Verificar se é uma requisição mobile"""
        user_agent = request.headers.get('User-Agent', '').lower()
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        return any(indicator in user_agent for indicator in mobile_indicators)
    
    def _get_browser_info(self):
        """Extrair informações do browser"""
        user_agent = request.headers.get('User-Agent', '')
        
        browsers = {
            'chrome': 'Chrome',
            'firefox': 'Firefox',
            'safari': 'Safari',
            'edge': 'Edge',
            'opera': 'Opera'
        }
        
        for key, name in browsers.items():
            if key in user_agent.lower():
                return name
        
        return 'Unknown'
    
    def _add_to_buffer(self, event: Event):
        """Adicionar evento ao buffer"""
        self.buffer.append(event)
        
        # Flush se buffer estiver cheio
        if len(self.buffer) >= self.buffer_size:
            self.flush_events()
    
    def flush_events(self):
        """Enviar eventos do buffer para armazenamento"""
        if not self.buffer:
            return
        
        events_to_send = self.buffer.copy()
        self.buffer.clear()
        
        try:
            # Tentar enviar para diferentes sistemas
            self._send_to_influxdb(events_to_send)
            self._send_to_file(events_to_send)  # Backup local
            
            logger.info(f"Flushed {len(events_to_send)} events to analytics systems")
            
        except Exception as e:
            logger.error(f"Error flushing events: {e}")
            # Recolocar eventos no buffer em caso de erro
            self.buffer.extend(events_to_send)
    
    def _send_to_influxdb(self, events: List[Event]):
        """Enviar eventos para InfluxDB"""
        try:
            # Import dinâmico para não quebrar se InfluxDB não estiver disponível
            from influxdb_client import InfluxDBClient, Point
            from influxdb_client.client.write_api import SYNCHRONOUS
            
            client = InfluxDBClient(
                url=current_app.config.get('INFLUXDB_URL'),
                token=current_app.config.get('INFLUXDB_TOKEN'),
                org=current_app.config.get('INFLUXDB_ORG')
            )
            
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            points = []
            for event in events:
                point = Point("agrotech_events") \
                    .tag("event_name", event.event_name) \
                    .tag("user_id", str(event.user_id or 'anonymous')) \
                    .tag("session_id", event.session_id or '') \
                    .field("event_id", event.event_id) \
                    .time(event.timestamp)
                
                # Adicionar propriedades como fields
                for key, value in event.properties.items():
                    if isinstance(value, (int, float)):
                        point = point.field(f"prop_{key}", value)
                    elif isinstance(value, bool):
                        point = point.field(f"prop_{key}", value)
                    else:
                        point = point.field(f"prop_{key}", str(value))
                
                # Adicionar contexto como tags/fields
                context = event.context
                if context.get('path'):
                    point = point.tag("path", context['path'])
                if context.get('method'):
                    point = point.tag("method", context['method'])
                if context.get('browser'):
                    point = point.tag("browser", context['browser'])
                if context.get('is_mobile') is not None:
                    point = point.field("is_mobile", context['is_mobile'])
                
                points.append(point)
            
            write_api.write(
                bucket=current_app.config.get('INFLUXDB_BUCKET'),
                record=points
            )
            
            client.close()
            
        except ImportError:
            logger.warning("InfluxDB client not installed, events stored locally only")
        except Exception as e:
            logger.error(f"Error sending events to InfluxDB: {e}")
            raise
    
    def _send_to_file(self, events: List[Event]):
        """Enviar eventos para arquivo local (backup)"""
        try:
            import os
            
            # Criar diretório se não existir
            log_dir = current_app.config.get('ANALYTICS_LOG_DIR', 'logs/analytics')
            os.makedirs(log_dir, exist_ok=True)
            
            # Nome do arquivo com data
            filename = f"{log_dir}/events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
            
            with open(filename, 'a', encoding='utf-8') as f:
                for event in events:
                    f.write(json.dumps(asdict(event)) + '\n')
                    
        except Exception as e:
            logger.error(f"Error writing events to file: {e}")

class BusinessMetrics:
    """Métricas de negócio específicas do AgroTech"""
    
    def __init__(self, tracker: AnalyticsTracker):
        self.tracker = tracker
    
    def track_user_registration(self, user_id: int, registration_method: str = 'web', user_data: Dict[str, Any] = None):
        """Rastrear registro de usuário"""
        self.tracker.track_conversion('user_registration', 1.0)
        self.tracker.track_user_action('register', 'user', user_id, {
            'registration_method': registration_method,
            'user_data': user_data or {}
        })
        
        # Métrica específica de onboarding
        self.tracker.track_feature_usage('onboarding', 'completed', {
            'method': registration_method
        })
    
    def track_user_login(self, user_id: int, login_method: str = 'password'):
        """Rastrear login de usuário"""
        self.tracker.track_user_action('login', 'user', user_id, {
            'login_method': login_method
        })
        
        # Rastrear engajamento
        self.tracker.track_event('engagement', {
            'action': 'user_login',
            'method': login_method
        }, user_id)
    
    def track_culture_management(self, user_id: int, action: str, culture_data: Dict[str, Any]):
        """Rastrear gestão de culturas"""
        self.tracker.track_user_action(action, 'culture', culture_data.get('id'), {
            'culture_type': culture_data.get('tipo'),
            'area': culture_data.get('area'),
            'location': culture_data.get('localizacao')
        })
        
        # Métrica de engajamento com agricultura
        self.tracker.track_event('agriculture_activity', {
            'action': action,
            'culture_type': culture_data.get('tipo'),
            'area': culture_data.get('area')
        }, user_id)
    
    def track_ai_interaction(self, user_id: int, ai_type: str, query: str, response_quality: Optional[str] = None):
        """Rastrear interação com IA"""
        self.tracker.track_feature_usage('ai_assistant', 'query', {
            'ai_type': ai_type,
            'query_length': len(query),
            'response_quality': response_quality
        })
        
        self.tracker.track_user_action('ask', 'ai', None, {
            'ai_type': ai_type,
            'query': query[:100],  # Primeiros 100 caracteres
            'response_quality': response_quality
        })
    
    def track_weather_usage(self, user_id: int, location: str, weather_type: str):
        """Rastrear uso de dados meteorológicos"""
        self.tracker.track_feature_usage('weather', 'request', {
            'location': location,
            'weather_type': weather_type
        })
        
        self.tracker.track_user_action('request', 'weather', None, {
            'location': location,
            'weather_type': weather_type
        })
    
    def track_marketplace_activity(self, user_id: int, action: str, product_data: Dict[str, Any]):
        """Rastrear atividade no marketplace"""
        self.tracker.track_user_action(action, 'product', product_data.get('id'), {
            'product_name': product_data.get('nome'),
            'category': product_data.get('categoria'),
            'price': product_data.get('preco'),
            'seller_id': product_data.get('vendedor_id')
        })
        
        # Rastrear conversões
        if action in ['purchase', 'buy']:
            self.tracker.track_conversion('marketplace_sale', product_data.get('preco'))
        elif action in ['add_to_cart', 'add_cart']:
            self.tracker.track_conversion('add_to_cart', product_data.get('preco'))
    
    def track_session_metrics(self, user_id: int, session_data: Dict[str, Any]):
        """Rastrear métricas da sessão"""
        duration = session_data.get('duration_minutes', 0)
        pages_viewed = session_data.get('pages_viewed', 0)
        
        self.tracker.track_performance('session_duration', duration, 'minutes')
        self.tracker.track_event('session_end', {
            'duration_minutes': duration,
            'pages_viewed': pages_viewed,
            'bounce': pages_viewed <= 1
        }, user_id)
    
    def track_error_recovery(self, user_id: int, error_type: str, recovery_action: str):
        """Rastrear recuperação de erros pelo usuário"""
        self.tracker.track_event('error_recovery', {
            'error_type': error_type,
            'recovery_action': recovery_action,
            'user_initiated': True
        }, user_id)
    
    def track_help_usage(self, user_id: int, help_type: str, topic: str):
        """Rastrear uso do sistema de ajuda"""
        self.tracker.track_feature_usage('help_system', 'accessed', {
            'help_type': help_type,
            'topic': topic
        })

# Decorators para tracking automático
def track_function_call(event_name: str = None, track_performance: bool = True):
    """Decorator para rastrear chamadas de função"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = event_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                if track_performance:
                    duration = (time.time() - start_time) * 1000
                    analytics.track_performance(f"function_{name}", duration)
                
                analytics.track_event('function_call', {
                    'function_name': name,
                    'success': True,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                
                return result
                
            except Exception as e:
                analytics.track_error('function_error', str(e), name)
                raise
        
        return wrapper
    return decorator

def track_endpoint(track_performance: bool = True):
    """Decorator para rastrear endpoints Flask"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                if track_performance:
                    duration = (time.time() - start_time) * 1000
                    analytics.track_performance(f"endpoint_{request.endpoint}", duration)
                
                return result
                
            except Exception as e:
                analytics.track_error('endpoint_error', str(e))
                raise
        
        return wrapper
    return decorator

# Instâncias globais
analytics = AnalyticsTracker()
business_metrics = BusinessMetrics(analytics)
