# app/utils/api_integration.py
"""
Sistema robusto de integração com APIs externas - Sprint 4 Prompt 2
"""
import requests
import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


# Exceções customizadas
class RateLimitExceededException(Exception):
    """Exceção para rate limit excedido"""
    pass


class CircuitBreakerOpenException(Exception):
    """Exceção para circuit breaker aberto"""
    pass


class APIResponse:
    """Wrapper para resposta de API com métricas"""
    
    def __init__(self, response, duration, api_name, success, error=None):
        self.response = response
        self.duration = duration
        self.api_name = api_name
        self.success = success
        self.error = error
        self.timestamp = datetime.now()
    
    @property
    def status_code(self):
        return self.response.status_code if self.response else None
    
    @property
    def json_data(self):
        if self.response and self.success:
            try:
                return self.response.json()
            except ValueError:
                return None
        return None
    
    @property
    def text_data(self):
        return self.response.text if self.response else None
    
    def to_dict(self):
        """Converter para dicionário para logging/cache"""
        return {
            'api_name': self.api_name,
            'success': self.success,
            'status_code': self.status_code,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'error': self.error
        }


class APIIntegrationManager:
    """Gerenciador robusto de integrações com APIs externas"""
    
    def __init__(self):
        self.session = self._create_session()
        self.rate_limiters = {}
        self.circuit_breakers = {}
        self.retry_configs = {}
        self.default_timeout = 30
        self.max_concurrent_requests = 10
        
    def _create_session(self):
        """Criar sessão HTTP otimizada"""
        session = requests.Session()
        
        # Configurar retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers padrão
        session.headers.update({
            'User-Agent': 'AgroTech-Portugal/2.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def register_api(self, name: str, config: Dict[str, Any]):
        """Registrar configuração de API"""
        self.rate_limiters[name] = RateLimiter(
            calls=config.get('rate_limit_calls', 100),
            period=config.get('rate_limit_period', 3600)
        )
        
        self.circuit_breakers[name] = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            recovery_timeout=config.get('recovery_timeout', 60),
            expected_exception=requests.RequestException
        )
        
        self.retry_configs[name] = {
            'max_retries': config.get('max_retries', 3),
            'backoff_factor': config.get('backoff_factor', 1),
            'retry_on_status': config.get('retry_on_status', [429, 500, 502, 503, 504])
        }
        
        logger.info(f"API {name} registrada com sucesso")
    
    def make_request(self, api_name: str, method: str, url: str, **kwargs) -> APIResponse:
        """Fazer request robusto com rate limiting e circuit breaker"""
        
        # Verificar rate limiting
        if not self.rate_limiters[api_name].can_proceed():
            raise RateLimitExceededException(f"Rate limit excedido para API {api_name}")
        
        # Verificar circuit breaker
        if not self.circuit_breakers[api_name].can_proceed():
            raise CircuitBreakerOpenException(f"Circuit breaker aberto para API {api_name}")
        
        start_time = time.time()
        
        try:
            # Configurar timeout
            kwargs.setdefault('timeout', self.default_timeout)
            
            # Fazer request
            response = self.session.request(method, url, **kwargs)
            
            # Registrar sucesso no circuit breaker
            self.circuit_breakers[api_name].record_success()
            
            # Calcular métricas
            duration = time.time() - start_time
            
            return APIResponse(
                response=response,
                duration=duration,
                api_name=api_name,
                success=response.status_code < 400
            )
            
        except Exception as e:
            # Registrar falha no circuit breaker
            self.circuit_breakers[api_name].record_failure()
            
            duration = time.time() - start_time
            
            logger.error(f"Erro na API {api_name}: {str(e)}")
            
            return APIResponse(
                response=None,
                duration=duration,
                api_name=api_name,
                success=False,
                error=str(e)
            )


class RateLimiter:
    """Implementação de rate limiting com sliding window"""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.call_times = []
    
    def can_proceed(self) -> bool:
        """Verificar se pode fazer nova chamada"""
        now = time.time()
        
        # Remover chamadas antigas
        cutoff = now - self.period
        self.call_times = [t for t in self.call_times if t > cutoff]
        
        # Verificar se pode fazer nova chamada
        if len(self.call_times) < self.calls:
            self.call_times.append(now)
            return True
        
        return False
    
    def get_reset_time(self) -> float:
        """Obter tempo até próximo reset"""
        if not self.call_times:
            return 0
        
        oldest_call = min(self.call_times)
        return max(0, oldest_call + self.period - time.time())


class CircuitBreaker:
    """Implementação de circuit breaker pattern"""
    
    def __init__(self, failure_threshold: int, recovery_timeout: int, expected_exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_proceed(self) -> bool:
        """Verificar se pode fazer chamada"""
        if self.state == 'CLOSED':
            return True
        
        elif self.state == 'OPEN':
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        
        elif self.state == 'HALF_OPEN':
            return True
        
        return False
    
    def record_success(self):
        """Registrar sucesso"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def record_failure(self):
        """Registrar falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
        elif self.state == 'HALF_OPEN':
            self.state = 'OPEN'


class APICache:
    """Cache específico para respostas de API"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.default_ttl = 300  # 5 minutos
    
    def get_cache_key(self, api_name: str, method: str, url: str, params: dict = None) -> str:
        """Gerar chave de cache para request"""
        key_data = {
            'api': api_name,
            'method': method,
            'url': url,
            'params': params or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"api_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def get(self, api_name: str, method: str, url: str, params: dict = None):
        """Obter resposta do cache"""
        cache_key = self.get_cache_key(api_name, method, url, params)
        return self.cache.get(cache_key)
    
    def set(self, api_name: str, method: str, url: str, response_data: dict, 
            ttl: int = None, params: dict = None):
        """Armazenar resposta no cache"""
        cache_key = self.get_cache_key(api_name, method, url, params)
        ttl = ttl or self.default_ttl
        return self.cache.set(cache_key, response_data, ttl)


# Decorators para APIs específicas
def cached_api_call(ttl: int = 300, cache_key_func: Callable = None):
    """Decorator para cache de chamadas de API"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.utils.cache_manager import cache
            
            # Gerar chave de cache
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"api_call:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Tentar obter do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit para API call {func.__name__}")
                return cached_result
            
            # Executar função e cachear resultado
            logger.debug(f"Cache miss para API call {func.__name__}")
            result = func(*args, **kwargs)
            
            # Só cachear se resultado foi bem-sucedido
            if result and getattr(result, 'success', True):
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 1.0, 
                    retry_on_status: list = None):
    """Decorator para retry automático em falhas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_on_status_codes = retry_on_status or [429, 500, 502, 503, 504]
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Se resultado tem status code, verificar se deve retry
                    if hasattr(result, 'status_code') and result.status_code in retry_on_status_codes:
                        if attempt < max_retries:
                            wait_time = backoff_factor * (2 ** attempt)
                            logger.warning(f"Tentativa {attempt + 1} falhou com status {result.status_code}. Tentando novamente em {wait_time}s")
                            time.sleep(wait_time)
                            continue
                    
                    return result
                    
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}. Tentando novamente em {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Todas as {max_retries + 1} tentativas falharam para {func.__name__}")
                        raise
            
            return None
        
        return wrapper
    return decorator


# Exceções customizadas
class APIIntegrationException(Exception):
    """Exceção base para integrações de API"""
    pass


class RateLimitExceededException(APIIntegrationException):
    """Rate limit excedido"""
    pass


class CircuitBreakerOpenException(APIIntegrationException):
    """Circuit breaker está aberto"""
    pass


class APITimeoutException(APIIntegrationException):
    """Timeout na API"""
    pass


# Integrações específicas
class WeatherAPIIntegration:
    """Integração robusta com API meteorológica"""
    
    def __init__(self, api_manager: APIIntegrationManager):
        self.api_manager = api_manager
        self.api_name = 'openweather'
        
        # Registrar configuração da API
        self.api_manager.register_api(self.api_name, {
            'rate_limit_calls': 1000,
            'rate_limit_period': 3600,
            'failure_threshold': 3,
            'recovery_timeout': 300,
            'max_retries': 2
        })
    
    @cached_api_call(ttl=1800)  # Cache por 30 minutos
    @retry_on_failure(max_retries=2, backoff_factor=2.0)
    def get_current_weather(self, lat: float, lng: float, api_key: str):
        """Obter clima atual com cache e retry"""
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lng,
                'appid': api_key,
                'units': 'metric',
                'lang': 'pt'
            }
            
            response = self.api_manager.make_request(
                self.api_name, 'GET', url, params=params
            )
            
            if response.success and response.json_data:
                return {
                    'success': True,
                    'data': response.json_data,
                    'duration': response.duration,
                    'cached': False
                }
            else:
                return {
                    'success': False,
                    'error': response.error or f"Status code: {response.status_code}",
                    'duration': response.duration
                }
                
        except Exception as e:
            logger.error(f"Erro na integração meteorológica: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'duration': 0
            }
    
    @cached_api_call(ttl=3600)  # Cache por 1 hora
    def get_weather_forecast(self, lat: float, lng: float, api_key: str, days: int = 5):
        """Obter previsão meteorológica"""
        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lng,
                'appid': api_key,
                'units': 'metric',
                'lang': 'pt',
                'cnt': days * 8  # 8 previsões por dia (a cada 3 horas)
            }
            
            response = self.api_manager.make_request(
                self.api_name, 'GET', url, params=params
            )
            
            if response.success and response.json_data:
                return {
                    'success': True,
                    'data': response.json_data,
                    'duration': response.duration,
                    'cached': False
                }
            else:
                return {
                    'success': False,
                    'error': response.error or f"Status code: {response.status_code}",
                    'duration': response.duration
                }
                
        except Exception as e:
            logger.error(f"Erro na previsão meteorológica: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'duration': 0
            }


class AIAPIIntegration:
    """Integração robusta com APIs de IA"""
    
    def __init__(self, api_manager: APIIntegrationManager):
        self.api_manager = api_manager
        self.api_name = 'openai'
        
        # Registrar configuração da API
        self.api_manager.register_api(self.api_name, {
            'rate_limit_calls': 50,
            'rate_limit_period': 60,
            'failure_threshold': 2,
            'recovery_timeout': 180,
            'max_retries': 1
        })
    
    @cached_api_call(ttl=3600, cache_key_func=lambda self, prompt, context, api_key: f"ai_response:{hashlib.md5((prompt + str(context)).encode()).hexdigest()}")
    @retry_on_failure(max_retries=1, backoff_factor=3.0)
    def get_ai_recommendation(self, prompt: str, context: dict, api_key: str):
        """Obter recomendação de IA com cache e retry"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Você é um especialista em agricultura portuguesa. Forneça recomendações práticas e específicas.'
                    },
                    {
                        'role': 'user',
                        'content': f"{prompt}\n\nContexto: {json.dumps(context, ensure_ascii=False)}"
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            response = self.api_manager.make_request(
                self.api_name, 'POST', url, headers=headers, json=data
            )
            
            if response.success and response.json_data:
                return {
                    'success': True,
                    'data': response.json_data,
                    'duration': response.duration,
                    'cached': False
                }
            else:
                return {
                    'success': False,
                    'error': response.error or f"Status code: {response.status_code}",
                    'duration': response.duration
                }
                
        except Exception as e:
            logger.error(f"Erro na integração AI: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'duration': 0
            }


class BatchAPIProcessor:
    """Processador de requests em lote para APIs"""
    
    def __init__(self, api_manager: APIIntegrationManager, max_workers: int = 5):
        self.api_manager = api_manager
        self.max_workers = max_workers
    
    def process_batch_requests(self, requests_data: list) -> list:
        """Processar múltiplos requests em paralelo"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter todas as tarefas
            future_to_request = {
                executor.submit(self._make_single_request, req_data): req_data
                for req_data in requests_data
            }
            
            # Coletar resultados
            for future in as_completed(future_to_request):
                req_data = future_to_request[future]
                try:
                    result = future.result()
                    results.append({
                        'request': req_data,
                        'result': result,
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'request': req_data,
                        'result': None,
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def _make_single_request(self, req_data: dict):
        """Fazer um único request"""
        return self.api_manager.make_request(
            req_data['api_name'],
            req_data['method'],
            req_data['url'],
            **req_data.get('kwargs', {})
        )


# Instância global do gerenciador
api_manager = APIIntegrationManager()
weather_api = WeatherAPIIntegration(api_manager)
ai_api = AIAPIIntegration(api_manager)
batch_processor = BatchAPIProcessor(api_manager)
