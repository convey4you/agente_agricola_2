# app/controllers/performance_controller.py
"""
Controller para APIs de performance e monitoramento do Sprint 4
"""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
import time
import psutil
import logging

from app.utils.cache_manager import cache
from app.utils.database_optimization import DatabaseOptimizer, QueryOptimizer
from app.utils.asset_optimization import performance_monitor
from app import db

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')


@performance_bp.route('/cache/stats', methods=['GET'])
@login_required
def get_cache_stats():
    """Obter estatísticas do cache Redis"""
    try:
        stats = cache.get_stats()
        
        # Adicionar informações extras
        stats['cache_enabled'] = current_app.config.get('CACHE_ENABLED', True)
        stats['redis_url'] = current_app.config.get('REDIS_URL', 'N/A')
        stats['fallback_enabled'] = current_app.config.get('CACHE_FALLBACK_ENABLED', True)
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/cache/clear', methods=['POST'])
@login_required
def clear_cache():
    """Limpar cache por padrão ou chave específica"""
    try:
        data = request.get_json() or {}
        pattern = data.get('pattern', '*')
        
        # Verificar permissões (só admin pode limpar cache completo)
        if pattern == '*' and not getattr(current_user, 'is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Permissão negada. Apenas administradores podem limpar todo o cache.'
            }), 403
        
        deleted_count = cache.clear_pattern(pattern)
        
        logger.info(f"Cache limpo pelo usuário {current_user.id}. Padrão: {pattern}, Deletados: {deleted_count}")
        
        return jsonify({
            'success': True,
            'data': {
                'pattern': pattern,
                'deleted_keys': deleted_count
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/cache/user/<int:user_id>/clear', methods=['POST'])
@login_required
def clear_user_cache(user_id):
    """Limpar cache específico de um usuário"""
    try:
        # Verificar permissões (usuário só pode limpar próprio cache)
        if current_user.id != user_id and not getattr(current_user, 'is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Permissão negada.'
            }), 403
        
        deleted_count = user_cache.invalidate_user_cache(user_id)
        
        logger.info(f"Cache do usuário {user_id} limpo por {current_user.id}. Deletados: {deleted_count}")
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'deleted_keys': deleted_count
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache do usuário {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/cache/weather/clear', methods=['POST'])
@login_required
def clear_weather_cache():
    """Limpar cache meteorológico"""
    try:
        data = request.get_json() or {}
        lat = data.get('lat')
        lng = data.get('lng')
        
        deleted_count = weather_cache.invalidate_weather_cache(lat=lat, lng=lng)
        
        logger.info(f"Cache meteorológico limpo por {current_user.id}. Lat: {lat}, Lng: {lng}, Deletados: {deleted_count}")
        
        return jsonify({
            'success': True,
            'data': {
                'lat': lat,
                'lng': lng,
                'deleted_keys': deleted_count
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache meteorológico: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/database/stats', methods=['GET'])
@login_required
def get_database_stats():
    """Obter estatísticas do banco de dados"""
    try:
        optimizer = DatabaseOptimizer(db)
        table_stats = optimizer.get_table_stats()
        
        # Informações do pool de conexões
        engine_info = {
            'pool_size': db.engine.pool.size(),
            'checked_out': db.engine.pool.checkedout(),
            'overflow': db.engine.pool.overflow(),
            'invalid': db.engine.pool.invalid()
        }
        
        return jsonify({
            'success': True,
            'data': {
                'table_stats': table_stats,
                'connection_pool': engine_info,
                'slow_query_threshold': optimizer.slow_query_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do banco: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/database/optimize', methods=['POST'])
@login_required
def optimize_database():
    """Executar otimizações no banco de dados"""
    try:
        # Verificar permissões de admin
        if not getattr(current_user, 'is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Permissão negada. Apenas administradores podem otimizar o banco.'
            }), 403
        
        data = request.get_json() or {}
        operation = data.get('operation', 'indexes')
        
        optimizer = DatabaseOptimizer(db)
        
        if operation == 'indexes':
            optimizer.create_indexes()
            message = "Índices criados/verificados com sucesso"
        elif operation == 'analyze':
            optimizer.analyze_slow_queries()
            message = "Análise de queries lentas habilitada"
        else:
            return jsonify({
                'success': False,
                'error': 'Operação não reconhecida. Use: indexes, analyze'
            }), 400
        
        logger.info(f"Otimização de banco executada por {current_user.id}. Operação: {operation}")
        
        return jsonify({
            'success': True,
            'data': {
                'operation': operation,
                'message': message
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao otimizar banco: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/system/metrics', methods=['GET'])
@login_required
def get_system_metrics():
    """Obter métricas do sistema"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memória
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used,
            'free': memory.free
        }
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': (disk.used / disk.total) * 100
        }
        
        # Rede (opcional)
        try:
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        except:
            network_info = None
        
        # Processos Python
        python_processes = len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()])
        
        return jsonify({
            'success': True,
            'data': {
                'timestamp': time.time(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'processes': {
                    'python_count': python_processes,
                    'total_count': len(list(psutil.process_iter()))
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas do sistema: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/queries/dashboard/<int:user_id>', methods=['GET'])
@login_required
@performance_monitor.monitor_request
def get_optimized_dashboard_data(user_id):
    """API otimizada para dados do dashboard"""
    try:
        # Verificar permissões
        if current_user.id != user_id and not getattr(current_user, 'is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Permissão negada.'
            }), 403
        
        start_time = time.time()
        
        # Usar query otimizada
        dashboard_data = QueryOptimizer.get_user_dashboard_data(user_id)
        
        end_time = time.time()
        query_duration = end_time - start_time
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'performance': {
                'query_duration': round(query_duration, 3),
                'cached': False  # Pode ser implementado cache adicional aqui
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter dados do dashboard para usuário {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/queries/marketplace', methods=['GET'])
@performance_monitor.monitor_request
def get_optimized_marketplace_data():
    """API otimizada para dados do marketplace"""
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        category_id = request.args.get('category_id', type=int)
        location = request.args.get('location')
        max_price = request.args.get('max_price', type=float)
        
        # Preparar filtros
        filters = {}
        if search:
            filters['search'] = search
        if category_id:
            filters['category_id'] = category_id
        if location:
            filters['location'] = location
        if max_price:
            filters['max_price'] = max_price
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        start_time = time.time()
        
        # Usar query otimizada
        products = QueryOptimizer.get_marketplace_products(
            filters=filters,
            limit=per_page,
            offset=offset
        )
        
        end_time = time.time()
        query_duration = end_time - start_time
        
        return jsonify({
            'success': True,
            'data': {
                'products': products,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(products)  # Seria ideal implementar count separado
                }
            },
            'performance': {
                'query_duration': round(query_duration, 3),
                'filters_applied': len(filters)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter dados do marketplace: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@performance_bp.route('/test/performance', methods=['POST'])
@login_required
def test_performance():
    """Endpoint para testar performance geral do sistema"""
    try:
        data = request.get_json() or {}
        test_type = data.get('type', 'all')
        
        results = {}
        
        if test_type in ['all', 'cache']:
            # Testar cache
            start_time = time.time()
            test_key = f"perf_test_{current_user.id}_{time.time()}"
            cache.set(test_key, {'test': 'data'}, 60)
            cached_value = cache.get(test_key)
            cache.delete(test_key)
            cache_duration = time.time() - start_time
            
            results['cache'] = {
                'duration': round(cache_duration, 3),
                'success': cached_value is not None
            }
        
        if test_type in ['all', 'database']:
            # Testar banco de dados
            start_time = time.time()
            db.engine.execute('SELECT 1')
            db_duration = time.time() - start_time
            
            results['database'] = {
                'duration': round(db_duration, 3),
                'success': True
            }
        
        if test_type in ['all', 'system']:
            # Testar métricas do sistema
            start_time = time.time()
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            system_duration = time.time() - start_time
            
            results['system'] = {
                'duration': round(system_duration, 3),
                'cpu_percent': cpu,
                'memory_percent': memory,
                'success': True
            }
        
        overall_duration = sum(r.get('duration', 0) for r in results.values())
        
        return jsonify({
            'success': True,
            'data': {
                'test_type': test_type,
                'results': results,
                'overall_duration': round(overall_duration, 3),
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no teste de performance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Registrar blueprint
def register_performance_routes(app):
    """Registrar rotas de performance na aplicação"""
    app.register_blueprint(performance_bp)
