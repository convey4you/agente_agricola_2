"""
Sistema de Cache Redis para Aplicação Agrícola
"""
import json
import functools
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict, Union
from flask import current_app, g
import pickle
import hashlib

# Tentar importar Redis, mas continuar sem ele se não disponível
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    current_app = None  # Placeholder para evitar erros


class CacheManager:
    """Gerenciador de cache Redis com fallback em memória"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.memory_cache = {}  # Fallback cache
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'fallback_hits': 0
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar o cache com a aplicação Flask"""
        self.app = app
        
        # Configurações de cache
        cache_config = {
            'CACHE_REDIS_HOST': app.config.get('CACHE_REDIS_HOST'),
            'CACHE_REDIS_PORT': app.config.get('CACHE_REDIS_PORT', 6379),
            'CACHE_REDIS_DB': app.config.get('CACHE_REDIS_DB', 0),
            'CACHE_REDIS_PASSWORD': app.config.get('CACHE_REDIS_PASSWORD'),
            'CACHE_REDIS_SOCKET_TIMEOUT': app.config.get('CACHE_REDIS_SOCKET_TIMEOUT', 5),
            'CACHE_ENABLED': app.config.get('CACHE_ENABLED', True),
            'CACHE_FALLBACK_ENABLED': app.config.get('CACHE_FALLBACK_ENABLED', True),
            'CACHE_KEY_PREFIX': app.config.get('CACHE_KEY_PREFIX', 'agagri:'),
            'CACHE_MAX_MEMORY_ITEMS': app.config.get('CACHE_MAX_MEMORY_ITEMS', 1000)
        }
        
        # Atualizar configuração da app
        app.config.update(cache_config)
        
        # Tentar conectar ao Redis
        self._init_redis_connection()
        
        # Registrar contexto de limpeza
        app.teardown_appcontext(self._cleanup_memory_cache)
    
    def _init_redis_connection(self):
        """Inicializar conexão Redis"""
        app = self._get_app()
        if not app or not app.config.get('CACHE_ENABLED'):
            if current_app:
                current_app.logger.info("Cache desabilitado por configuração")
            return

        if not REDIS_AVAILABLE:
            if current_app:
                current_app.logger.warning("Redis não disponível. Usando apenas cache em memória")
            return

        try:
            redis_url = app.config.get('REDIS_URL')
            
            # Se temos REDIS_URL, usar ela diretamente
            if redis_url and redis_url != '${{Redis.REDIS_URL}}':  # Ignorar placeholder
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    health_check_interval=30,
                    socket_timeout=10,  # Aumentar timeout
                    socket_connect_timeout=10,  # Timeout de conexão
                    retry_on_timeout=True
                )
                if current_app:
                    current_app.logger.info(f"🔗 Tentando conectar ao Redis: {redis_url.split('@')[1] if '@' in redis_url else redis_url[:30]}...")
                    
            # Fallback para configuração individual
            elif app.config.get('CACHE_REDIS_HOST'):
                self.redis_client = redis.Redis(
                    host=app.config['CACHE_REDIS_HOST'],
                    port=app.config['CACHE_REDIS_PORT'],
                    db=app.config['CACHE_REDIS_DB'],
                    password=app.config['CACHE_REDIS_PASSWORD'],
                    socket_timeout=app.config['CACHE_REDIS_SOCKET_TIMEOUT'],
                    decode_responses=True,
                    health_check_interval=30
                )
                if current_app:
                    current_app.logger.info("🔗 Tentando conectar ao Redis via configuração individual")
            else:
                if current_app:
                    current_app.logger.info("⚠️ REDIS_URL não configurada, usando cache em memória")
                return
            
            # Teste de conexão mais robusto
            try:
                # Teste ping simples
                result = self.redis_client.ping()
                if result:
                    if current_app:
                        current_app.logger.info("✅ Conexão Redis estabelecida com sucesso!")
                else:
                    raise Exception("Ping falhou")
                    
                # Teste de escrita/leitura
                test_key = "agagri:connection_test"
                self.redis_client.set(test_key, "test_value", ex=10)
                test_result = self.redis_client.get(test_key)
                if test_result == "test_value":
                    self.redis_client.delete(test_key)
                    if current_app:
                        current_app.logger.info("✅ Teste de escrita/leitura Redis OK!")
                else:
                    raise Exception("Teste de escrita/leitura falhou")
                    
            except Exception as ping_error:
                if current_app:
                    current_app.logger.warning(f"❌ Teste de conexão Redis falhou: {ping_error}")
                raise ping_error
            
        except Exception as e:
            if current_app:
                current_app.logger.warning(f"⚠️ Falha na conexão Redis: {e}. Usando cache em memória como fallback")
            self.redis_client = None
    
    def _get_app(self):
        """Obter aplicação Flask atual (self.app ou current_app)"""
        return self.app or current_app
    
    def _generate_cache_key(self, key: str, namespace: str = None) -> str:
        """Gerar chave de cache com prefixo e namespace"""
        app = self._get_app()
        prefix = app.config.get('CACHE_KEY_PREFIX', 'agagri:') if app else 'agagri:'
        
        if namespace:
            full_key = f"{prefix}{namespace}:{key}"
        else:
            full_key = f"{prefix}{key}"
        
        # Hash para keys muito longas
        if len(full_key) > 200:
            return f"{prefix}hashed:{hashlib.md5(full_key.encode()).hexdigest()}"
        
        return full_key
    
    def _serialize_data(self, data: Any) -> str:
        """Serializar dados para armazenamento"""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
                return json.dumps(data, default=str)
            else:
                # Para objetos complexos, usar pickle convertido para base64
                import base64
                pickled = pickle.dumps(data)
                return base64.b64encode(pickled).decode('utf-8')
        except Exception:
            # Último recurso: converter para string
            return str(data)
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserializar dados do cache"""
        try:
            # Tentar JSON primeiro
            return json.loads(data)
        except json.JSONDecodeError:
            try:
                # Tentar pickle/base64
                import base64
                pickled = base64.b64decode(data.encode('utf-8'))
                return pickle.loads(pickled)
            except Exception:
                # Retornar como string se falhar
                return data
    
    def get(self, key: str, namespace: str = None) -> Optional[Any]:
        """Obter valor do cache"""
        app = self.app or current_app
        if not app or not app.config.get('CACHE_ENABLED'):
            self.cache_stats['misses'] += 1
            return None
        
        cache_key = self._generate_cache_key(key, namespace)
        
        # Tentar Redis primeiro
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    self.cache_stats['hits'] += 1
                    return self._deserialize_data(cached_data)
            except Exception as e:
                if current_app:
                    current_app.logger.warning(f"Erro ao acessar Redis: {e}")
                self.cache_stats['errors'] += 1
        
        # Fallback para memória
        if app and app.config.get('CACHE_FALLBACK_ENABLED'):
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if entry['expires_at'] > datetime.now(timezone.utc):
                    self.cache_stats['fallback_hits'] += 1
                    return entry['data']
                else:
                    # Remover entrada expirada
                    del self.memory_cache[cache_key]
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, timeout: int = 3600, namespace: str = None) -> bool:
        """Definir valor no cache"""
        app = self.app or current_app
        if not app or not app.config.get('CACHE_ENABLED'):
            return False
        
        cache_key = self._generate_cache_key(key, namespace)
        serialized_value = self._serialize_data(value)
        
        success = False
        
        # Tentar Redis primeiro
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, timeout, serialized_value)
                success = True
            except Exception as e:
                if current_app:
                    current_app.logger.warning(f"Erro ao escrever no Redis: {e}")
                self.cache_stats['errors'] += 1
        
        # Fallback para memória
        if app.config.get('CACHE_FALLBACK_ENABLED'):
            self._cleanup_memory_cache_if_needed()
            self.memory_cache[cache_key] = {
                'data': value,
                'expires_at': datetime.now(timezone.utc) + timedelta(seconds=timeout)
            }
            success = True
        
        return success
    
    def delete(self, key: str, namespace: str = None) -> bool:
        """Deletar chave do cache"""
        cache_key = self._generate_cache_key(key, namespace)
        success = False
        
        # Redis
        if self.redis_client:
            try:
                self.redis_client.delete(cache_key)
                success = True
            except Exception as e:
                if current_app:
                    current_app.logger.warning(f"Erro ao deletar do Redis: {e}")
        
        # Memória
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            success = True
        
        return success
    
    def clear_namespace(self, namespace: str) -> int:
        """Limpar todas as chaves de um namespace"""
        pattern = self._generate_cache_key("*", namespace)
        cleared = 0
        
        # Redis
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    cleared += self.redis_client.delete(*keys)
            except Exception as e:
                if current_app:
                    current_app.logger.warning(f"Erro ao limpar namespace no Redis: {e}")
        
        # Memória
        memory_keys = [k for k in self.memory_cache.keys() if k.startswith(pattern.replace('*', ''))]
        for key in memory_keys:
            del self.memory_cache[key]
            cleared += 1
        
        return cleared
    
    def _cleanup_memory_cache_if_needed(self):
        """Limpar cache em memória se necessário"""
        app = self._get_app()
        max_items = app.config.get('CACHE_MAX_MEMORY_ITEMS', 1000) if app else 1000
        
        if len(self.memory_cache) >= max_items:
            # Remover 25% dos itens mais antigos
            items_to_remove = max_items // 4
            now = datetime.now(timezone.utc)
            
            # Primeiro remover expirados
            expired_keys = [
                k for k, v in self.memory_cache.items()
                if v['expires_at'] <= now
            ]
            
            for key in expired_keys[:items_to_remove]:
                del self.memory_cache[key]
            
            # Se ainda precisar remover mais, remover os mais antigos
            if len(expired_keys) < items_to_remove:
                remaining = items_to_remove - len(expired_keys)
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1]['expires_at']
                )
                
                for key, _ in sorted_items[:remaining]:
                    del self.memory_cache[key]
    
    def _cleanup_memory_cache(self, exception=None):
        """Limpar cache em memória no final da requisição"""
        now = datetime.now(timezone.utc)
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
    
    def get_stats(self) -> Dict:
        """Obter estatísticas de cache"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'errors': self.cache_stats['errors'],
            'fallback_hits': self.cache_stats['fallback_hits'],
            'memory_cache_size': len(self.memory_cache),
            'redis_connected': self.redis_client is not None
        }
        
        # Informações do Redis se disponível
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats['redis_info'] = {
                    'used_memory': redis_info.get('used_memory_human'),
                    'connected_clients': redis_info.get('connected_clients'),
                    'total_commands_processed': redis_info.get('total_commands_processed')
                }
            except Exception:
                stats['redis_info'] = 'Não disponível'
        
        return stats
    
    def health_check(self) -> Dict:
        """Verificar saúde do sistema de cache"""
        app = self._get_app()
        health = {
            'cache_enabled': app.config.get('CACHE_ENABLED', False) if app else False,
            'redis_connected': False,
            'memory_fallback': app.config.get('CACHE_FALLBACK_ENABLED', False) if app else False,
            'status': 'unhealthy'
        }
        
        if self.redis_client:
            try:
                self.redis_client.ping()
                health['redis_connected'] = True
                health['status'] = 'healthy'
            except Exception as e:
                health['redis_error'] = str(e)
        
        if health['memory_fallback'] and not health['redis_connected']:
            health['status'] = 'degraded'  # Funcionando com fallback
        
        return health


# Instância global do cache
cache = CacheManager()


# Decorators para cache
def cached(timeout=3600, namespace=None, key_func=None):
    """Decorator para cache de funções"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Chave baseada no nome da função e argumentos
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{func.__name__}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # Tentar obter do cache
            cached_result = cache.get(cache_key, namespace)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            
            # Resolver timeout se for função
            cache_timeout = timeout() if callable(timeout) else timeout
            cache.set(cache_key, result, cache_timeout, namespace)
            
            return result
        
        # Adicionar método para invalidar cache
        wrapper.invalidate_cache = lambda *args, **kwargs: cache.delete(
            key_func(*args, **kwargs) if key_func else f"{func.__name__}:{hashlib.md5((str(args) + str(sorted(kwargs.items()))).encode()).hexdigest()}",
            namespace
        )
        
        return wrapper
    return decorator


def cache_key_for_weather(lat, lon, *args, **kwargs):
    """Função para gerar chave de cache para dados climáticos"""
    return f"weather:lat_{lat}_lon_{lon}"


def cache_key_for_ai(message, context_hash, *args, **kwargs):
    """Função para gerar chave de cache para IA"""
    message_hash = hashlib.md5(message.encode()).hexdigest()[:10]
    return f"ai:msg_{message_hash}_ctx_{context_hash}"


def cache_key_for_dashboard(user_id, *args, **kwargs):
    """Função para gerar chave de cache para dashboard"""
    return f"dashboard:user_{user_id}"


def cache_key_for_culture(culture_id, *args, **kwargs):
    """Função para gerar chave de cache para cultura"""
    return f"culture:id_{culture_id}"
