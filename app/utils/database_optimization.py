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
        from app import db
        
        # Query única com joins otimizados
        query = text("""
            SELECT 
                u.id as user_id,
                u.nome_completo as user_name,
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
            GROUP BY u.id, u.nome_completo
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {'user_id': user_id}).fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def get_marketplace_products(filters=None, limit=20, offset=0):
        """Query otimizada para produtos do marketplace"""
        from app import db
        
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
                u.nome_completo as seller_name,
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
        from app import db
        
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

# Função para inicializar otimizador
def init_database_optimizer(db):
    """Inicializar otimizador de banco de dados"""
    db_optimizer = DatabaseOptimizer(db)
    return db_optimizer
