# app/utils/cache.py
import redis
import json
import pickle
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
import hashlib
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache Redis"""
    
    def __init__(self, redis_url=None):
        self.redis_url = redis_url
        self._redis = None
    
    @property
    def redis(self):
        """Conexão lazy com Redis"""
        if self._redis is None:
            try:
                # Tentar obter URL do contexto da aplicação se disponível
                redis_url = self.redis_url
                try:
                    from flask import current_app
                    if current_app:
                        redis_url = current_app.config.get('REDIS_URL') or self.redis_url
                except RuntimeError:
                    # Fora do contexto da aplicação, usar URL fornecida
                    pass
                
                # Verificar se temos uma URL válida (não placeholder)
                if redis_url and redis_url != '${{Redis.REDIS_URL}}':
                    self._redis = redis.from_url(
                        redis_url, 
                        decode_responses=False,
                        socket_timeout=10,
                        socket_connect_timeout=10,
                        retry_on_timeout=True
                    )
                    # Testar conexão com diagnóstico detalhado
                    try:
                        result = self._redis.ping()
                        if result:
                            logger.info(f"✅ Conexão Redis estabelecida com sucesso via URL: {redis_url.split('@')[1] if '@' in redis_url else redis_url[:30]}...")
                        else:
                            raise Exception("Ping retornou False")
                    except Exception as ping_error:
                        logger.error(f"❌ Falha no ping Redis: {ping_error}")
                        raise ping_error
                else:
                    logger.info("⚠️ REDIS_URL não configurada, usando cache em memória")
                    self._redis = InMemoryCache()
            except Exception as e:
                logger.error(f"❌ Erro ao conectar com Redis: {e}")
                logger.info("🔄 Usando cache em memória como fallback")
                # Fallback para cache em memória
                self._redis = InMemoryCache()
        
        return self._redis
    
    def get(self, key, default=None):
        """Obter valor do cache"""
        try:
            value = self.redis.get(key)
            if value is not None:
                return pickle.loads(value)
            return default
        except Exception as e:
            logger.error(f"Erro ao obter cache {key}: {e}")
            return default
    
    def set(self, key, value, timeout=3600):
        """Definir valor no cache"""
        try:
            serialized_value = pickle.dumps(value)
            self.redis.setex(key, timeout, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    def delete(self, key):
        """Deletar chave do cache"""
        try:
            return self.redis.delete(key)
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Limpar chaves que correspondem ao padrão"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Erro ao limpar padrão {pattern}: {e}")
            return 0
    
    def get_stats(self):
        """Obter estatísticas do cache"""
        try:
            info = self.redis.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def _calculate_hit_rate(self, info):
        """Calcular taxa de acerto do cache"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total > 0:
            return round((hits / total) * 100, 2)
        return 0

class InMemoryCache:
    """Cache em memória como fallback"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key):
        if key in self._expiry and datetime.now() > self._expiry[key]:
            self.delete(key)
            return None
        return self._cache.get(key)
    
    def setex(self, key, timeout, value):
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=timeout)
    
    def delete(self, key):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        return 1
    
    def keys(self, pattern):
        # Implementação simples de pattern matching
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
    
    def ping(self):
        return True
    
    def info(self):
        return {
            'used_memory_human': f"{len(self._cache)} keys",
            'connected_clients': 1,
            'total_commands_processed': 0,
            'keyspace_hits': 0,
            'keyspace_misses': 0
        }

# Instância global do cache
cache = CacheManager()

def cached(timeout=3600, key_prefix='', vary_on=None):
    """Decorator para cache de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = _generate_cache_key(func, key_prefix, args, kwargs, vary_on)
            
            # Tentar obter do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit para {cache_key}")
                return cached_result
            
            # Executar função e cachear resultado
            logger.debug(f"Cache miss para {cache_key}")
            result = func(*args, **kwargs)
            
            cache.set(cache_key, result, timeout)
            return result
        
        # Adicionar método para limpar cache
        wrapper.clear_cache = lambda: cache.clear_pattern(f"{key_prefix}:{func.__name__}:*")
        
        return wrapper
    return decorator

def cache_user_data(user_id, timeout=1800):
    """Decorator específico para cache de dados do usuário"""
    return cached(timeout=timeout, key_prefix=f"user:{user_id}", vary_on=['user_id'])

def cache_weather_data(timeout=1800):
    """Decorator específico para cache de dados meteorológicos"""
    return cached(timeout=timeout, key_prefix="weather")

def cache_ai_recommendations(user_id, timeout=3600):
    """Decorator específico para cache de recomendações de IA"""
    return cached(timeout=timeout, key_prefix=f"ai_rec:{user_id}")

def _generate_cache_key(func, prefix, args, kwargs, vary_on):
    """Gerar chave única para cache"""
    # Criar string base
    base_string = f"{prefix}:{func.__module__}:{func.__name__}"
    
    # Adicionar argumentos se especificado
    if vary_on:
        vary_values = []
        for var in vary_on:
            if var in kwargs:
                vary_values.append(f"{var}={kwargs[var]}")
        
        if vary_values:
            base_string += ":" + ":".join(vary_values)
    else:
        # Usar todos os argumentos
        all_args = list(args) + [f"{k}={v}" for k, v in sorted(kwargs.items())]
        if all_args:
            args_string = ":".join(str(arg) for arg in all_args)
            base_string += f":{args_string}"
    
    # Gerar hash para chaves muito longas
    if len(base_string) > 200:
        hash_object = hashlib.md5(base_string.encode())
        return f"{prefix}:hash:{hash_object.hexdigest()}"
    
    return base_string

class WeatherCache:
    """Cache especializado para dados meteorológicos"""
    
    def __init__(self):
        self.cache_timeout = 1800  # 30 minutos
    
    @cache_weather_data(timeout=1800)
    def get_weather_data(self, lat, lng, date=None):
        """Obter dados meteorológicos com cache"""
        # Esta função será sobrescrita pelo serviço meteorológico
        pass
    
    def invalidate_weather_cache(self, lat=None, lng=None):
        """Invalidar cache meteorológico"""
        if lat and lng:
            pattern = f"weather:*lat={lat}*lng={lng}*"
        else:
            pattern = "weather:*"
        
        return cache.clear_pattern(pattern)

class UserDataCache:
    """Cache especializado para dados do usuário"""
    
    def __init__(self):
        self.cache_timeout = 1800  # 30 minutos
    
    def get_user_cultures(self, user_id):
        """Obter culturas do usuário com cache"""
        @cache_user_data(user_id, timeout=self.cache_timeout)
        def _get_cultures():
            from app.models import Culture
            return Culture.query.filter_by(user_id=user_id).all()
        
        return _get_cultures()
    
    def get_user_recommendations(self, user_id):
        """Obter recomendações do usuário com cache"""
        @cache_ai_recommendations(user_id, timeout=3600)
        def _get_recommendations():
            try:
                from app.models.ai import Recommendation, RecommendationStatus
                return Recommendation.query.filter_by(
                    user_id=user_id,
                    status=RecommendationStatus.ACTIVE
                ).limit(10).all()
            except ImportError:
                # Fallback se modelo AI não existir
                logger.warning("Modelo AI não encontrado, retornando lista vazia")
                return []
        
        return _get_recommendations()
    
    def invalidate_user_cache(self, user_id):
        """Invalidar cache do usuário"""
        patterns = [
            f"user:{user_id}:*",
            f"ai_rec:{user_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += cache.clear_pattern(pattern)
        
        return total_deleted

# Instâncias especializadas
weather_cache = WeatherCache()
user_cache = UserDataCache()
