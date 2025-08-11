# PROMPT DETALHADO 2: Implementação Completa de Health Check

**Para Claude Sonnet 4**  
**Projeto:** AgroTech Portugal  
**Prioridade:** ALTA  
**Tempo Estimado:** 45-60 minutos

---

## 🎯 CONTEXTO COMPLETO

Você é um desenvolvedor Python especialista em monitoramento e observabilidade de sistemas Flask. Precisa criar um sistema completo de health check para o AgroTech Portugal que permita monitorar proativamente a saúde do sistema e diagnosticar problemas rapidamente.

### Situação do Projeto
- **Sistema:** AgroTech Portugal (agricultura familiar)
- **Problema Resolvido:** Sistema de registro (correção anterior)
- **Necessidade Atual:** Monitoramento proativo para evitar problemas futuros
- **Ambiente:** Flask + PostgreSQL + Railway

### Objetivos do Health Check
1. **Monitoramento Proativo:** Detectar problemas antes dos usuários
2. **Diagnóstico Rápido:** Identificar causa raiz de falhas
3. **Validação de Deploy:** Confirmar que correções funcionam
4. **Observabilidade:** Métricas para tomada de decisão

---

## 📋 TAREFA ESPECÍFICA

**OBJETIVO:** Criar arquivo `app/controllers/health_controller.py` com sistema completo de health check.

### Estrutura de Endpoints Requerida

1. **`/health`** - Health check básico e rápido
2. **`/health/db`** - Verificação detalhada do banco de dados
3. **`/health/registration`** - Teste específico do sistema de registro
4. **`/health/system`** - Informações do sistema e recursos

---

## 🔧 ESPECIFICAÇÕES DETALHADAS

### 1. ENDPOINT `/health` - Health Check Básico

**Objetivo:** Verificação rápida (< 1 segundo) do status geral do sistema.

**Implementação Esperada:**
```python
@health_bp.route('/health')
def health_check():
    """
    Verificação básica de saúde do sistema
    Tempo limite: 1 segundo
    """
    try:
        start_time = time.time()
        
        # Teste 1: Conexão básica com banco
        db.session.execute('SELECT 1')
        
        # Teste 2: Verificar se tabela principal existe
        User.query.first()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'database': 'connected',
            'tables': 'available',
            'response_time_ms': response_time
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'error_type': type(e).__name__
        }), 503
```

### 2. ENDPOINT `/health/db` - Health Check de Banco Detalhado

**Objetivo:** Verificação completa do banco de dados e estrutura.

**Implementação Esperada:**
```python
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
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        start_time = time.time()
        
        # Teste 1: Conexão básica
        db.session.execute('SELECT 1')
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
            test_user = User(email='test@healthcheck.com', password_hash='test')
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
```

### 3. ENDPOINT `/health/registration` - Health Check do Sistema de Registro

**Objetivo:** Validar especificamente o sistema de registro que estava falhando.

**Implementação Esperada:**
```python
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
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
        }), 503
```

### 4. ENDPOINT `/health/system` - Informações do Sistema

**Objetivo:** Métricas de sistema e recursos para monitoramento.

**Implementação Esperada:**
```python
@health_bp.route('/health/system')
def system_health():
    """
    Informações detalhadas do sistema e recursos
    """
    try:
        import psutil
        import platform
        
        # Informações básicas
        system_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'flask_env': os.environ.get('FLASK_ENV', 'production')
        }
        
        # Recursos do sistema
        resources = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent if os.path.exists('/') else None
        }
        
        # Informações da aplicação
        app_info = {
            'uptime_seconds': get_app_uptime(),
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(ativo=True).count(),
            'completed_onboarding': User.query.filter_by(onboarding_completed=True).count()
        }
        
        # Status geral baseado em thresholds
        status = 'healthy'
        warnings = []
        
        if resources['cpu_percent'] > 80:
            status = 'degraded'
            warnings.append('High CPU usage')
        
        if resources['memory_percent'] > 85:
            status = 'degraded'
            warnings.append('High memory usage')
        
        if resources['disk_percent'] and resources['disk_percent'] > 90:
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
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
```

---

## 🛠️ FUNÇÕES AUXILIARES REQUERIDAS

### 1. Mascarar URL do Banco
```python
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
```

### 2. Recomendações do Banco
```python
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
```

### 3. Recomendações do Registro
```python
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
```

### 4. Uptime da Aplicação
```python
import time

# Variável global para tracking de uptime
APP_START_TIME = time.time()

def get_app_uptime():
    """Retorna uptime da aplicação em segundos"""
    return round(time.time() - APP_START_TIME, 2)
```

---

## 📝 ESTRUTURA COMPLETA DO ARQUIVO

### Imports Necessários
```python
"""
Health Check Controller - Monitoramento do Sistema AgroTech Portugal
Criado para monitoramento proativo e diagnóstico de problemas
"""
import os
import time
from datetime import datetime
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
```

### Blueprint Registration
```python
# No app/__init__.py, adicionar:
try:
    from app.controllers.health_controller import health_bp
    app.register_blueprint(health_bp, url_prefix='/')
    print("✅ Health check endpoints registrados")
except ImportError:
    print("⚠️ Health check não disponível")
```

---

## 🧪 TESTES DE VALIDAÇÃO

### 1. Testes Básicos
```bash
# Testar endpoints
curl https://www.agenteagricola.com/health
curl https://www.agenteagricola.com/health/db
curl https://www.agenteagricola.com/health/registration
curl https://www.agenteagricola.com/health/system
```

### 2. Validação de Respostas
```python
# Todas as respostas devem ter:
{
    "status": "healthy|degraded|unhealthy",
    "timestamp": "2025-08-02T...",
    # ... outros campos específicos
}
```

### 3. Códigos HTTP Esperados
- **200**: Sistema saudável
- **206**: Sistema degradado mas funcional
- **503**: Sistema com problemas críticos

---

## 📊 MÉTRICAS E MONITORAMENTO

### 1. Métricas Coletadas
- Tempo de resposta dos endpoints
- Status de conectividade do banco
- Contagem de usuários
- Uso de recursos do sistema
- Estrutura de tabelas

### 2. Alertas Recomendados
- Health check falhando por > 2 minutos
- Tempo de resposta > 5 segundos
- Uso de CPU > 80%
- Uso de memória > 85%
- Falhas de conectividade com banco

---

## 🚀 RESULTADO ESPERADO

Após implementação:

1. **Monitoramento Ativo**
   - 4 endpoints de health check funcionais
   - Diagnóstico automático de problemas
   - Métricas de performance disponíveis

2. **Diagnóstico Rápido**
   - Identificação imediata de problemas de banco
   - Validação específica do sistema de registro
   - Recomendações automáticas de correção

3. **Observabilidade**
   - Logs estruturados em JSON
   - Métricas de sistema e aplicação
   - Tracking de uptime e performance

4. **Validação de Deploy**
   - Confirmação automática de correções
   - Testes de regressão integrados
   - Alertas proativos de problemas

---

**PROMPT PRONTO PARA EXECUÇÃO COM CLAUDE SONNET 4**  
**IMPLEMENTAR APÓS CORREÇÃO DO __init__.py**

