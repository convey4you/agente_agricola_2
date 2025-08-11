"""
Health Check Controller - Monitoramento do Sistema AgroTech Portugal
Criado para monitoramento proativo e diagnóstico de problemas
"""
import os
import time
from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app
from app import db
from app.models.user import User

# Opcional para métricas de sistema
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Blueprint
health_bp = Blueprint('health', __name__)

# Tracking de uptime
APP_START_TIME = time.time()


def mask_database_url():
    """Mascara informações sensíveis da URL do banco"""
    try:
        from flask import current_app
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        if '@' in db_url:
            # postgresql://user:password@host:port/db
            parts = db_url.split('@')
            if '://' in parts[0]:
                protocol_user = parts[0].split('://')
                return f"{protocol_user[0]}://***:***@{parts[1]}"
        
        return "***"
    except:
        return "unavailable"


def generate_db_recommendations(test_results):
    """Gera recomendações baseadas nos testes do banco"""
    recommendations = []
    
    if not test_results.get('connection'):
        recommendations.append("Check database connection configuration")
    
    if not test_results.get('tables_exist'):
        recommendations.append("Run database migrations or create tables")
    
    if not test_results.get('can_write'):
        recommendations.append("Check database permissions for write operations")
    
    if test_results.get('response_time_ms', 0) > 1000:
        recommendations.append("Consider database performance optimization")
    
    return recommendations


def generate_registration_recommendations(tests):
    """Gera recomendações baseadas nos testes de registro"""
    recommendations = []
    
    if not tests.get('database_ready'):
        recommendations.append("Initialize database tables")
    
    if not tests.get('table_structure_valid'):
        recommendations.append("Update database schema")
    
    if not tests.get('validation_works'):
        recommendations.append("Check validator configuration")
    
    sim = tests.get('registration_simulation', {})
    if not sim.get('can_flush'):
        recommendations.append("Check database write permissions and constraints")
    
    return recommendations


def get_app_uptime():
    """Retorna uptime da aplicação em segundos"""
    return round(time.time() - APP_START_TIME, 2)


@health_bp.route('/health')
def health_check():
    """
    Verificação básica de saúde do sistema
    Tempo limite: 1 segundo
    """
    try:
        start_time = time.time()
        
        # Teste 1: Conexão básica com banco
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        # Teste 2: Verificar se tabela principal existe
        User.query.first()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'database': 'connected',
            'tables': 'available',
            'response_time_ms': response_time
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'error_type': type(e).__name__
        }), 503


@health_bp.route('/health/db')
def database_health():
    """
    Verificação detalhada do banco de dados
    Inclui estrutura, conectividade e performance
    """
    test_results = {
        'connection': False,
        'tables_exist': False,
        'can_query': False,
        'can_write': False,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    try:
        start_time = time.time()
        
        # Teste 1: Conexão básica
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        test_results['connection'] = True
        
        # Teste 2: Verificar estrutura de tabelas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        test_results['tables_exist'] = 'users' in tables
        test_results['available_tables'] = tables
        
        # Teste 3: Verificar estrutura da tabela users
        if 'users' in tables:
            user_columns = [col['name'] for col in inspector.get_columns('users')]
            test_results['user_table_columns'] = user_columns
            
            required_columns = ['id', 'email', 'password_hash', 'data_criacao']
            missing_columns = [col for col in required_columns if col not in user_columns]
            test_results['missing_columns'] = missing_columns
            test_results['schema_valid'] = len(missing_columns) == 0
        
        # Teste 4: Query de leitura
        user_count = User.query.count()
        test_results['can_query'] = True
        test_results['user_count'] = user_count
        
        # Teste 5: Teste de escrita (simulado)
        try:
            # Não criar usuário real, apenas validar que poderia
            test_user = User(
                email='test@healthcheck.com', 
                password_hash='test'
            )
                
            db.session.add(test_user)
            db.session.flush()  # Testa sem commit
            db.session.rollback()  # Desfaz
            test_results['can_write'] = True
        except Exception as write_error:
            test_results['can_write'] = False
            test_results['write_error'] = str(write_error)
        
        # Performance
        response_time = round((time.time() - start_time) * 1000, 2)
        test_results['response_time_ms'] = response_time
        
        # Status geral
        all_tests_passed = all([
            test_results['connection'],
            test_results['tables_exist'],
            test_results['can_query'],
            test_results['can_write']
        ])
        
        return jsonify({
            'status': 'healthy' if all_tests_passed else 'degraded',
            'tests': test_results,
            'database_url_masked': mask_database_url(),
            'recommendations': generate_db_recommendations(test_results)
        }), 200 if all_tests_passed else 206
        
    except Exception as e:
        test_results['error'] = str(e)
        test_results['error_type'] = type(e).__name__
        
        return jsonify({
            'status': 'unhealthy',
            'tests': test_results
        }), 503


@health_bp.route('/health/registration')
def registration_health():
    """
    Teste específico do sistema de registro
    Valida toda a cadeia de registro sem criar usuários reais
    """
    try:
        from app.services.auth_service import AuthService
        from app.validators.auth_validators import AuthValidator
        
        tests = {
            'validator_available': False,
            'service_available': False,
            'validation_works': False,
            'database_ready': False,
            'table_structure_valid': False,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Teste 1: Verificar se classes estão disponíveis
        tests['validator_available'] = AuthValidator is not None
        tests['service_available'] = AuthService is not None
        
        # Teste 2: Testar validação
        test_data = {
            'email': 'test@healthcheck.com',
            'password': 'TestPassword123!',
            'nome_completo': 'Health Check Test'
        }
        
        is_valid, error_msg = AuthValidator.validate_register_data(test_data)
        tests['validation_works'] = is_valid
        if not is_valid:
            tests['validation_error'] = error_msg
        
        # Teste 3: Verificar estrutura do banco
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        tests['database_ready'] = 'users' in tables
        
        if 'users' in tables:
            columns = [col['name'] for col in inspector.get_columns('users')]
            required_columns = ['id', 'email', 'password_hash', 'data_criacao']
            missing_columns = [col for col in required_columns if col not in columns]
            
            tests['table_structure_valid'] = len(missing_columns) == 0
            tests['available_columns'] = columns
            tests['missing_columns'] = missing_columns
        
        # Teste 4: Simular processo de registro (sem commit)
        registration_simulation = {
            'can_create_user_object': False,
            'can_add_to_session': False,
            'can_flush': False
        }
        
        try:
            # Simular criação de usuário
            test_user = User(
                email='healthcheck@test.com',
                password_hash='test_hash',
                nome_completo='Health Check'
            )
            
            registration_simulation['can_create_user_object'] = True
            
            # Simular adição à sessão
            db.session.add(test_user)
            registration_simulation['can_add_to_session'] = True
            
            # Simular flush (detecta erros de DB)
            db.session.flush()
            registration_simulation['can_flush'] = True
            
            # Rollback para não criar usuário real
            db.session.rollback()
            
        except Exception as sim_error:
            registration_simulation['error'] = str(sim_error)
            db.session.rollback()
        
        tests['registration_simulation'] = registration_simulation
        
        # Status geral
        critical_tests = [
            tests['validator_available'],
            tests['service_available'],
            tests['validation_works'],
            tests['database_ready'],
            tests['table_structure_valid'],
            registration_simulation['can_flush']
        ]
        
        all_critical_passed = all(critical_tests)
        
        return jsonify({
            'status': 'healthy' if all_critical_passed else 'unhealthy',
            'tests': tests,
            'critical_tests_passed': sum(critical_tests),
            'critical_tests_total': len(critical_tests),
            'registration_ready': all_critical_passed,
            'recommendations': generate_registration_recommendations(tests)
        }), 200 if all_critical_passed else 503
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503


@health_bp.route('/health/system')
def system_health():
    """
    Informações detalhadas do sistema e recursos
    """
    try:
        # Informações básicas
        system_info = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'platform': 'Railway Cloud Platform',
            'python_version': '3.13',
            'flask_env': os.environ.get('FLASK_ENV', 'production')
        }
        
        # Recursos do sistema (se psutil disponível)
        resources = {}
        if PSUTIL_AVAILABLE:
            resources = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if os.path.exists('/') else None
            }
        else:
            resources = {
                'cpu_percent': 'unavailable',
                'memory_percent': 'unavailable',
                'disk_percent': 'unavailable',
                'note': 'psutil not installed'
            }
        
        # Informações da aplicação
        try:
            app_info = {
                'uptime_seconds': get_app_uptime(),
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(ativo=True).count() if hasattr(User, 'ativo') else 'unavailable',
                'completed_onboarding': User.query.filter_by(onboarding_completed=True).count() if hasattr(User, 'onboarding_completed') else 'unavailable'
            }
        except Exception as app_error:
            app_info = {
                'uptime_seconds': get_app_uptime(),
                'error': str(app_error)
            }
        
        # Status geral baseado em thresholds
        status = 'healthy'
        warnings = []
        
        if PSUTIL_AVAILABLE:
            if isinstance(resources.get('cpu_percent'), (int, float)) and resources['cpu_percent'] > 80:
                status = 'degraded'
                warnings.append('High CPU usage')
            
            if isinstance(resources.get('memory_percent'), (int, float)) and resources['memory_percent'] > 85:
                status = 'degraded'
                warnings.append('High memory usage')
            
            if isinstance(resources.get('disk_percent'), (int, float)) and resources['disk_percent'] > 90:
                status = 'degraded'
                warnings.append('High disk usage')
        
        return jsonify({
            'status': status,
            'warnings': warnings,
            'system': system_info,
            'resources': resources,
            'application': app_info
        }), 200
        
    except ImportError:
        # psutil não disponível
        return jsonify({
            'status': 'limited',
            'message': 'System monitoring not available (psutil not installed)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503
