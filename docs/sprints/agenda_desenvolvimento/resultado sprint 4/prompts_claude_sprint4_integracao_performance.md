# PROMPTS CLAUDE SONNET 4 - SPRINT 4: INTEGRAÇÃO E PERFORMANCE
## AgroTech Portugal - Sistema de Agente Agrícola Inteligente

**Autor**: Manus AI - Gerente de Tecnologia  
**Data**: 31 de julho de 2025  
**Versão**: 1.0  
**Sprint**: 4 - Integração e Performance  
**Período**: 02-13 de setembro de 2025  

---

## 📋 VISÃO GERAL DO SPRINT 4

O Sprint 4 concentra-se na otimização de performance, integração robusta de sistemas e preparação para produção do AgroTech Portugal. Este sprint é crucial para garantir que a aplicação possa suportar a carga esperada de usuários e funcione de forma eficiente e confiável no ambiente de produção.

### Objetivos Principais

O Sprint 4 tem como objetivo transformar o AgroTech Portugal de um sistema funcional em uma aplicação enterprise-grade, capaz de atender milhares de agricultores portugueses simultaneamente. Isso inclui otimização de performance, implementação de cache inteligente, otimização de banco de dados, integração robusta com APIs externas e preparação completa da infraestrutura de produção.

### Contexto Estratégico

Com as funcionalidades implementadas e testadas nos sprints anteriores, o Sprint 4 representa o momento de preparação final para o lançamento comercial. A performance e confiabilidade são fatores críticos que determinarão a adoção e satisfação dos usuários, especialmente considerando que agricultores dependem de informações precisas e em tempo hábil para suas decisões.

---

## ⚡ PROMPT 1: OTIMIZAÇÃO DE PERFORMANCE E CACHE

### Contexto do Projeto
Você está implementando um sistema abrangente de otimização de performance para o AgroTech Portugal. Este sistema deve garantir tempos de resposta rápidos, uso eficiente de recursos e uma experiência de usuário fluida, mesmo com milhares de usuários simultâneos e grandes volumes de dados agrícolas.

### Funcionalidade a Implementar
Sistema completo de cache multi-camadas, otimização de queries de banco de dados, compressão de assets, lazy loading de componentes e otimização de APIs. O objetivo é alcançar tempos de resposta inferiores a 2 segundos para todas as operações críticas e suportar pelo menos 1000 usuários simultâneos.

### Arquitetura Proposta

O sistema de performance será baseado em múltiplas camadas de otimização, desde o frontend até o banco de dados. A arquitetura utilizará Redis para cache, otimização de queries SQL, CDN para assets estáticos e técnicas avançadas de otimização web.

**Componentes de Performance:**
- **Cache Redis**: Cache de dados frequentemente acessados
- **Query Optimization**: Otimização de consultas ao banco de dados
- **Asset Optimization**: Compressão e minificação de recursos
- **API Caching**: Cache de respostas de APIs externas
- **Database Indexing**: Índices otimizados para consultas rápidas
- **Connection Pooling**: Pool de conexões para eficiência

### Objetivo
Implementar um sistema robusto de otimização que garanta performance excepcional do AgroTech Portugal, proporcionando uma experiência de usuário rápida e responsiva que atenda às expectativas dos agricultores portugueses modernos.

### Instruções Detalhadas

**ETAPA 1: Sistema de Cache Redis**

Configure o sistema de cache em `app/utils/cache.py`:

```python
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
        self.redis_url = redis_url or current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        self._redis = None
    
    @property
    def redis(self):
        """Conexão lazy com Redis"""
        if self._redis is None:
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=False)
                # Testar conexão
                self._redis.ping()
                logger.info("Conexão Redis estabelecida com sucesso")
            except Exception as e:
                logger.error(f"Erro ao conectar com Redis: {e}")
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
            from app.models.ai import Recommendation, RecommendationStatus
            return Recommendation.query.filter_by(
                user_id=user_id,
                status=RecommendationStatus.ACTIVE
            ).limit(10).all()
        
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
```

**ETAPA 2: Otimização de Banco de Dados**

Crie otimizações de banco em `app/utils/database_optimization.py`:

```python
# app/utils/database_optimization.py
from sqlalchemy import text, event, Index
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from flask_sqlalchemy import SQLAlchemy
import time
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Otimizador de performance do banco de dados"""
    
    def __init__(self, db):
        self.db = db
        self.slow_query_threshold = 1.0  # 1 segundo
    
    def setup_connection_pool(self, app):
        """Configurar pool de conexões otimizado"""
        app.config.update({
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'poolclass': QueuePool,
                'pool_size': 20,
                'max_overflow': 30,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'echo': app.config.get('DEBUG', False)
            }
        })
    
    def create_indexes(self):
        """Criar índices para otimização de queries"""
        with self.db.engine.connect() as conn:
            # Índices para tabela users
            self._create_index_if_not_exists(conn, 'idx_users_email', 'users', ['email'])
            self._create_index_if_not_exists(conn, 'idx_users_location', 'users', ['location_district'])
            
            # Índices para tabela cultures
            self._create_index_if_not_exists(conn, 'idx_cultures_user_id', 'cultures', ['user_id'])
            self._create_index_if_not_exists(conn, 'idx_cultures_type', 'cultures', ['type'])
            self._create_index_if_not_exists(conn, 'idx_cultures_status', 'cultures', ['status'])
            self._create_index_if_not_exists(conn, 'idx_cultures_planting_date', 'cultures', ['planting_date'])
            
            # Índices para tabela recommendations
            self._create_index_if_not_exists(conn, 'idx_recommendations_user_id', 'recommendations', ['user_id'])
            self._create_index_if_not_exists(conn, 'idx_recommendations_status', 'recommendations', ['status'])
            self._create_index_if_not_exists(conn, 'idx_recommendations_type', 'recommendations', ['type'])
            self._create_index_if_not_exists(conn, 'idx_recommendations_created_at', 'recommendations', ['created_at'])
            
            # Índices para tabela products
            self._create_index_if_not_exists(conn, 'idx_products_user_id', 'products', ['user_id'])
            self._create_index_if_not_exists(conn, 'idx_products_category', 'products', ['category_id'])
            self._create_index_if_not_exists(conn, 'idx_products_location', 'products', ['location_district'])
            self._create_index_if_not_exists(conn, 'idx_products_active', 'products', ['is_active'])
            
            # Índices para tabela alerts
            self._create_index_if_not_exists(conn, 'idx_alerts_user_id', 'alerts', ['user_id'])
            self._create_index_if_not_exists(conn, 'idx_alerts_status', 'alerts', ['status'])
            self._create_index_if_not_exists(conn, 'idx_alerts_priority', 'alerts', ['priority'])
            
            # Índices compostos para queries complexas
            self._create_index_if_not_exists(conn, 'idx_cultures_user_status', 'cultures', ['user_id', 'status'])
            self._create_index_if_not_exists(conn, 'idx_recommendations_user_status', 'recommendations', ['user_id', 'status'])
            self._create_index_if_not_exists(conn, 'idx_products_location_active', 'products', ['location_district', 'is_active'])
    
    def _create_index_if_not_exists(self, conn, index_name, table_name, columns):
        """Criar índice se não existir"""
        try:
            # Verificar se índice já existe
            check_query = text("""
                SELECT COUNT(*) 
                FROM pg_indexes 
                WHERE indexname = :index_name
            """)
            
            result = conn.execute(check_query, {'index_name': index_name}).scalar()
            
            if result == 0:
                # Criar índice
                columns_str = ', '.join(columns)
                create_query = text(f"""
                    CREATE INDEX CONCURRENTLY {index_name} 
                    ON {table_name} ({columns_str})
                """)
                
                conn.execute(create_query)
                logger.info(f"Índice {index_name} criado com sucesso")
            else:
                logger.debug(f"Índice {index_name} já existe")
                
        except Exception as e:
            logger.error(f"Erro ao criar índice {index_name}: {e}")
    
    def analyze_slow_queries(self):
        """Analisar queries lentas"""
        with self.db.engine.connect() as conn:
            # Habilitar log de queries lentas (PostgreSQL)
            try:
                conn.execute(text(f"SET log_min_duration_statement = {int(self.slow_query_threshold * 1000)}"))
                logger.info("Log de queries lentas habilitado")
            except Exception as e:
                logger.warning(f"Não foi possível habilitar log de queries lentas: {e}")
    
    def get_table_stats(self):
        """Obter estatísticas das tabelas"""
        with self.db.engine.connect() as conn:
            try:
                stats_query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """)
                
                result = conn.execute(stats_query)
                return [dict(row) for row in result]
                
            except Exception as e:
                logger.error(f"Erro ao obter estatísticas das tabelas: {e}")
                return []

class QueryOptimizer:
    """Otimizador de queries específicas"""
    
    @staticmethod
    def get_user_dashboard_data(user_id):
        """Query otimizada para dados do dashboard"""
        from app.models import User, Culture, Recommendation, Alert
        
        # Query única com joins otimizados
        query = text("""
            SELECT 
                u.id as user_id,
                u.name as user_name,
                COUNT(DISTINCT c.id) as culture_count,
                COUNT(DISTINCT r.id) as recommendation_count,
                COUNT(DISTINCT a.id) as alert_count,
                MAX(r.created_at) as last_recommendation,
                MAX(a.created_at) as last_alert
            FROM users u
            LEFT JOIN cultures c ON u.id = c.user_id AND c.status != 'completed'
            LEFT JOIN recommendations r ON u.id = r.user_id AND r.status = 'active'
            LEFT JOIN alerts a ON u.id = a.user_id AND a.status = 'active'
            WHERE u.id = :user_id
            GROUP BY u.id, u.name
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {'user_id': user_id}).fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def get_marketplace_products(filters=None, limit=20, offset=0):
        """Query otimizada para produtos do marketplace"""
        base_query = """
            SELECT 
                p.id,
                p.name,
                p.description,
                p.price,
                p.unit,
                p.quantity_available,
                p.location_district,
                p.created_at,
                u.name as seller_name,
                u.phone as seller_phone,
                pc.name as category_name
            FROM products p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            WHERE p.is_active = true
        """
        
        params = {}
        conditions = []
        
        if filters:
            if filters.get('search'):
                conditions.append("p.name ILIKE :search OR p.description ILIKE :search")
                params['search'] = f"%{filters['search']}%"
            
            if filters.get('category_id'):
                conditions.append("p.category_id = :category_id")
                params['category_id'] = filters['category_id']
            
            if filters.get('location'):
                conditions.append("p.location_district = :location")
                params['location'] = filters['location']
            
            if filters.get('max_price'):
                conditions.append("p.price <= :max_price")
                params['max_price'] = filters['max_price']
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY p.created_at DESC LIMIT :limit OFFSET :offset"
        params.update({'limit': limit, 'offset': offset})
        
        with db.engine.connect() as conn:
            result = conn.execute(text(base_query), params)
            return [dict(row) for row in result]
    
    @staticmethod
    def get_culture_activities_summary(culture_id):
        """Query otimizada para resumo de atividades da cultura"""
        query = text("""
            SELECT 
                ca.type,
                COUNT(*) as activity_count,
                SUM(ca.cost) as total_cost,
                MAX(ca.activity_date) as last_activity,
                AVG(ca.cost) as avg_cost
            FROM culture_activities ca
            WHERE ca.culture_id = :culture_id
            GROUP BY ca.type
            ORDER BY activity_count DESC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {'culture_id': culture_id})
            return [dict(row) for row in result]

# Event listeners para monitoramento de performance
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Registrar início da query"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Registrar fim da query e log se for lenta"""
    total = time.time() - context._query_start_time
    
    if total > 1.0:  # Log queries que demoram mais de 1 segundo
        logger.warning(
            f"Slow query detected: {total:.2f}s - {statement[:100]}...",
            extra={
                'extra_fields': {
                    'query_duration': total,
                    'query_statement': statement[:500],
                    'query_parameters': str(parameters)[:200] if parameters else None
                }
            }
        )

# Instância global do otimizador
db_optimizer = DatabaseOptimizer(db)
```

**ETAPA 3: Otimização de Assets e Frontend**

Crie otimizações de frontend em `app/utils/asset_optimization.py`:

```python
# app/utils/asset_optimization.py
import os
import gzip
import hashlib
from flask import current_app, request, make_response
from functools import wraps
import mimetypes

class AssetOptimizer:
    """Otimizador de assets estáticos"""
    
    def __init__(self, app=None):
        self.app = app
        self.cache_timeout = 31536000  # 1 ano
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar otimizador com a aplicação"""
        self.app = app
        
        # Configurar compressão
        app.config.setdefault('COMPRESS_MIMETYPES', [
            'text/html',
            'text/css',
            'text/xml',
            'application/json',
            'application/javascript',
            'text/javascript',
            'application/xml+rss',
            'application/atom+xml',
            'image/svg+xml'
        ])
        
        # Registrar blueprint para assets otimizados
        from flask import Blueprint
        
        assets_bp = Blueprint('optimized_assets', __name__)
        
        @assets_bp.route('/static/<path:filename>')
        def optimized_static(filename):
            return self.serve_optimized_asset(filename)
        
        app.register_blueprint(assets_bp)
    
    def serve_optimized_asset(self, filename):
        """Servir asset otimizado"""
        static_folder = current_app.static_folder
        file_path = os.path.join(static_folder, filename)
        
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Verificar se cliente suporta gzip
        accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')
        
        # Gerar ETag baseado no arquivo
        etag = self._generate_etag(file_path)
        
        # Verificar cache do cliente
        if request.headers.get('If-None-Match') == etag:
            return '', 304
        
        # Ler arquivo
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Comprimir se suportado e benéfico
        if accepts_gzip and self._should_compress(filename):
            content = gzip.compress(content)
            encoding = 'gzip'
        else:
            encoding = None
        
        # Criar resposta
        response = make_response(content)
        
        # Headers de cache
        response.headers['ETag'] = etag
        response.headers['Cache-Control'] = f'public, max-age={self.cache_timeout}'
        
        # Content-Type
        mimetype, _ = mimetypes.guess_type(filename)
        if mimetype:
            response.headers['Content-Type'] = mimetype
        
        # Encoding
        if encoding:
            response.headers['Content-Encoding'] = encoding
        
        return response
    
    def _generate_etag(self, file_path):
        """Gerar ETag para arquivo"""
        stat = os.stat(file_path)
        etag_data = f"{stat.st_mtime}-{stat.st_size}"
        return hashlib.md5(etag_data.encode()).hexdigest()
    
    def _should_compress(self, filename):
        """Verificar se arquivo deve ser comprimido"""
        # Não comprimir arquivos já comprimidos
        compressed_extensions = ['.gz', '.zip', '.rar', '.7z', '.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for ext in compressed_extensions:
            if filename.lower().endswith(ext):
                return False
        
        # Comprimir apenas arquivos de texto
        text_extensions = ['.css', '.js', '.html', '.xml', '.json', '.svg', '.txt']
        
        for ext in text_extensions:
            if filename.lower().endswith(ext):
                return True
        
        return False

def compress_response(f):
    """Decorator para comprimir respostas HTTP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        
        # Verificar se cliente aceita gzip
        accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')
        
        if not accepts_gzip:
            return response
        
        # Verificar se content-type deve ser comprimido
        content_type = response.headers.get('Content-Type', '')
        
        compressible_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'text/xml',
            'application/xml'
        ]
        
        should_compress = any(ct in content_type for ct in compressible_types)
        
        if should_compress and len(response.data) > 1024:  # Só comprimir se > 1KB
            response.data = gzip.compress(response.data)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.data)
        
        return response
    
    return decorated_function

class LazyLoadingHelper:
    """Helper para lazy loading de componentes"""
    
    @staticmethod
    def generate_lazy_image_html(src, alt="", css_class="", placeholder_color="#f0f0f0"):
        """Gerar HTML para imagem com lazy loading"""
        return f'''
        <img 
            data-src="{src}" 
            alt="{alt}" 
            class="lazy-load {css_class}"
            style="background-color: {placeholder_color};"
            loading="lazy"
        />
        '''
    
    @staticmethod
    def generate_lazy_script():
        """Gerar script JavaScript para lazy loading"""
        return '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const lazyImages = document.querySelectorAll('.lazy-load');
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy-load');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        });
        </script>
        '''

class CDNHelper:
    """Helper para integração com CDN"""
    
    def __init__(self, cdn_base_url=None):
        self.cdn_base_url = cdn_base_url or current_app.config.get('CDN_BASE_URL')
    
    def asset_url(self, filename):
        """Gerar URL do asset via CDN"""
        if self.cdn_base_url:
            return f"{self.cdn_base_url.rstrip('/')}/{filename.lstrip('/')}"
        else:
            return f"/static/{filename}"
    
    def image_url(self, filename, width=None, height=None, quality=85):
        """Gerar URL de imagem otimizada via CDN"""
        base_url = self.asset_url(filename)
        
        if not self.cdn_base_url:
            return base_url
        
        # Parâmetros de otimização (exemplo para Cloudinary)
        params = []
        
        if width:
            params.append(f"w_{width}")
        
        if height:
            params.append(f"h_{height}")
        
        if quality != 85:
            params.append(f"q_{quality}")
        
        if params:
            param_string = ",".join(params)
            return f"{self.cdn_base_url}/image/upload/{param_string}/{filename}"
        
        return base_url

# Instâncias globais
asset_optimizer = AssetOptimizer()
cdn_helper = CDNHelper()
```

### Testes de Validação

**TESTE 1: Validação do Sistema de Cache**
```python
# Testar cache Redis
from app.utils.cache import cache, cached

@cached(timeout=60)
def test_function(param):
    return f"Result for {param}"

# Primeira chamada - cache miss
result1 = test_function("test")

# Segunda chamada - cache hit
result2 = test_function("test")

# Verificar estatísticas
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}%")
```

**TESTE 2: Validação de Performance de Queries**
```python
# Testar queries otimizadas
from app.utils.database_optimization import QueryOptimizer
import time

start_time = time.time()
dashboard_data = QueryOptimizer.get_user_dashboard_data(1)
end_time = time.time()

print(f"Dashboard query took: {end_time - start_time:.3f}s")
assert end_time - start_time < 0.5  # Deve ser menor que 500ms
```

**TESTE 3: Validação de Compressão de Assets**
```python
# Testar compressão de assets
from app.utils.asset_optimization import compress_response
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
@compress_response
def test_compression():
    return jsonify({"data": "x" * 1000})  # Dados grandes para testar compressão

# Testar com cliente que aceita gzip
with app.test_client() as client:
    response = client.get('/test', headers={'Accept-Encoding': 'gzip'})
    assert 'gzip' in response.headers.get('Content-Encoding', '')
```

### Critérios de Aceitação
- Sistema de cache Redis funcionando com hit rate > 80%
- Queries de dashboard executando em < 500ms
- Assets estáticos sendo servidos com compressão
- Índices de banco de dados criados e otimizados
- Lazy loading implementado para imagens
- CDN configurado para assets estáticos

### Entregáveis Esperados
1. **Sistema de Cache Redis** completo e funcional
2. **Otimização de Banco de Dados** com índices e queries otimizadas
3. **Compressão de Assets** e lazy loading implementados
4. **Monitoramento de Performance** de queries
5. **Documentação de Otimização** com métricas de performance

### Informações Importantes
- Configurar Redis com persistência adequada
- Implementar fallback para cache em memória
- Monitorar hit rate do cache continuamente
- Criar índices de forma não-bloqueante (CONCURRENTLY)
- Testar performance em ambiente similar à produção

---

