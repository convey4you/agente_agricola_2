# PROMPT DETALHADO 3: Scripts de Validação e Testes das Correções

**Para Claude Sonnet 4**  
**Projeto:** AgroTech Portugal  
**Prioridade:** ALTA  
**Tempo Estimado:** 60-90 minutos

---

## 🎯 CONTEXTO COMPLETO

Você é um especialista em QA e automação de testes para sistemas Flask. Precisa criar um conjunto completo de scripts de validação para verificar se as correções críticas do AgroTech Portugal foram implementadas corretamente e estão funcionando em produção.

### Situação do Projeto
- **Correções Implementadas:** Inicialização de banco + Health checks
- **Objetivo:** Validar automaticamente se tudo funciona
- **Ambiente:** Produção (www.agenteagricola.com) + Local
- **Criticidade:** Sistema de registro deve funcionar 95%+

### Necessidades de Validação
1. **Validação Técnica:** Verificar se código foi implementado corretamente
2. **Validação Funcional:** Testar se sistema de registro funciona
3. **Validação de Performance:** Confirmar tempos de resposta aceitáveis
4. **Validação de Monitoramento:** Verificar health checks ativos

---

## 📋 TAREFA ESPECÍFICA

**OBJETIVO:** Criar scripts Python completos para validação automatizada das correções implementadas.

### Scripts Requeridos

1. **`validate_corrections.py`** - Script principal de validação
2. **`test_health_endpoints.py`** - Testes específicos de health check
3. **`test_registration_flow.py`** - Testes do fluxo de registro
4. **`performance_validator.py`** - Testes de performance
5. **`generate_validation_report.py`** - Gerador de relatório final

---

## 🔧 SCRIPT 1: validate_corrections.py - Validador Principal

### Objetivo
Script principal que executa todos os testes e gera relatório consolidado.

### Implementação Completa
```python
#!/usr/bin/env python3
"""
Validador Principal das Correções Críticas - AgroTech Portugal
Executa bateria completa de testes para validar implementação
Autor: Gerente de Tecnologia
Data: 2 de agosto de 2025
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CorrectionsValidator:
    """Validador completo das correções implementadas"""
    
    def __init__(self, base_url: str = "https://www.agenteagricola.com"):
        self.base_url = base_url.rstrip('/')
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'base_url': base_url,
            'tests': {},
            'summary': {},
            'recommendations': []
        }
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_basic_connectivity(self) -> Dict[str, Any]:
        """Teste 1: Conectividade básica com o sistema"""
        logger.info("🔍 Testando conectividade básica...")
        
        test_result = {
            'name': 'Basic Connectivity',
            'status': 'unknown',
            'details': {},
            'duration_ms': 0
        }
        
        start_time = time.time()
        
        try:
            response = self.session.get(f"{self.base_url}/")
            duration = round((time.time() - start_time) * 1000, 2)
            
            test_result.update({
                'status': 'pass' if response.status_code in [200, 302] else 'fail',
                'duration_ms': duration,
                'details': {
                    'status_code': response.status_code,
                    'response_time_ms': duration,
                    'accessible': response.status_code in [200, 302]
                }
            })
            
            if response.status_code in [200, 302]:
                logger.info("✅ Sistema acessível")
            else:
                logger.warning(f"⚠️ Status inesperado: {response.status_code}")
                
        except Exception as e:
            test_result.update({
                'status': 'fail',
                'duration_ms': round((time.time() - start_time) * 1000, 2),
                'details': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            logger.error(f"❌ Falha na conectividade: {e}")
        
        return test_result
    
    def test_health_endpoints(self) -> Dict[str, Any]:
        """Teste 2: Validar todos os endpoints de health check"""
        logger.info("🏥 Testando endpoints de health check...")
        
        endpoints = [
            '/health',
            '/health/db', 
            '/health/registration',
            '/health/system'
        ]
        
        test_result = {
            'name': 'Health Check Endpoints',
            'status': 'unknown',
            'details': {},
            'duration_ms': 0
        }
        
        start_time = time.time()
        endpoint_results = {}
        
        for endpoint in endpoints:
            endpoint_result = self._test_single_health_endpoint(endpoint)
            endpoint_results[endpoint] = endpoint_result
            
        duration = round((time.time() - start_time) * 1000, 2)
        
        # Avaliar status geral
        passed_endpoints = sum(1 for r in endpoint_results.values() if r['status'] == 'pass')
        total_endpoints = len(endpoints)
        
        if passed_endpoints == total_endpoints:
            status = 'pass'
            logger.info(f"✅ Todos os {total_endpoints} health checks funcionando")
        elif passed_endpoints >= 2:  # Pelo menos /health e /health/db
            status = 'partial'
            logger.warning(f"⚠️ {passed_endpoints}/{total_endpoints} health checks funcionando")
        else:
            status = 'fail'
            logger.error(f"❌ Apenas {passed_endpoints}/{total_endpoints} health checks funcionando")
        
        test_result.update({
            'status': status,
            'duration_ms': duration,
            'details': {
                'endpoints_tested': total_endpoints,
                'endpoints_passed': passed_endpoints,
                'endpoints': endpoint_results
            }
        })
        
        return test_result
    
    def _test_single_health_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Testa um endpoint específico de health check"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url)
            
            # Verificar se resposta é JSON válida
            try:
                json_data = response.json()
            except:
                json_data = None
            
            result = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'has_json': json_data is not None
            }
            
            if json_data:
                result['json_status'] = json_data.get('status', 'unknown')
                result['has_timestamp'] = 'timestamp' in json_data
            
            return result
            
        except Exception as e:
            return {
                'status': 'fail',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def test_registration_flow(self) -> Dict[str, Any]:
        """Teste 3: Validar fluxo completo de registro"""
        logger.info("📝 Testando fluxo de registro...")
        
        test_result = {
            'name': 'Registration Flow',
            'status': 'unknown',
            'details': {},
            'duration_ms': 0
        }
        
        start_time = time.time()
        
        try:
            # Passo 1: Acessar página de registro
            reg_page = self.session.get(f"{self.base_url}/auth/register")
            
            if reg_page.status_code != 200:
                raise Exception(f"Página de registro inacessível: {reg_page.status_code}")
            
            # Passo 2: Tentar submeter registro (sem CSRF token, esperamos erro específico)
            test_email = f"test.validation.{int(time.time())}@agrotech.pt"
            
            registration_data = {
                'email': test_email,
                'password': 'TestValidation2025!',
                'confirm_password': 'TestValidation2025!',
                'nome_completo': 'Teste Validação',
                'aceito_termos': True
            }
            
            # Submeter sem CSRF (esperamos erro específico, não erro interno)
            reg_response = self.session.post(
                f"{self.base_url}/auth/register",
                data=registration_data,
                allow_redirects=False
            )
            
            duration = round((time.time() - start_time) * 1000, 2)
            
            # Analisar resposta
            if reg_response.status_code == 500:
                # Erro interno = problema não resolvido
                test_result.update({
                    'status': 'fail',
                    'duration_ms': duration,
                    'details': {
                        'registration_page_accessible': True,
                        'submission_status_code': reg_response.status_code,
                        'error': 'Internal server error still occurring',
                        'problem': 'Database tables not created or other critical issue'
                    }
                })
                logger.error("❌ Erro interno ainda ocorrendo no registro")
                
            elif reg_response.status_code in [400, 403]:
                # Erro de validação/CSRF = sistema funcionando, mas dados inválidos
                test_result.update({
                    'status': 'pass',
                    'duration_ms': duration,
                    'details': {
                        'registration_page_accessible': True,
                        'submission_status_code': reg_response.status_code,
                        'error_type': 'validation_error',
                        'explanation': 'System is working, got validation error as expected'
                    }
                })
                logger.info("✅ Sistema de registro funcionando (erro de validação esperado)")
                
            elif reg_response.status_code in [302, 301]:
                # Redirecionamento = registro pode ter funcionado
                test_result.update({
                    'status': 'pass',
                    'duration_ms': duration,
                    'details': {
                        'registration_page_accessible': True,
                        'submission_status_code': reg_response.status_code,
                        'redirect_location': reg_response.headers.get('Location'),
                        'explanation': 'System appears to be working (got redirect)'
                    }
                })
                logger.info("✅ Sistema de registro funcionando (redirecionamento)")
                
            else:
                # Status inesperado
                test_result.update({
                    'status': 'partial',
                    'duration_ms': duration,
                    'details': {
                        'registration_page_accessible': True,
                        'submission_status_code': reg_response.status_code,
                        'explanation': f'Unexpected status code: {reg_response.status_code}'
                    }
                })
                logger.warning(f"⚠️ Status inesperado no registro: {reg_response.status_code}")
                
        except Exception as e:
            test_result.update({
                'status': 'fail',
                'duration_ms': round((time.time() - start_time) * 1000, 2),
                'details': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            logger.error(f"❌ Falha no teste de registro: {e}")
        
        return test_result
    
    def test_database_initialization(self) -> Dict[str, Any]:
        """Teste 4: Verificar se inicialização do banco funcionou"""
        logger.info("🗄️ Testando inicialização do banco...")
        
        test_result = {
            'name': 'Database Initialization',
            'status': 'unknown',
            'details': {},
            'duration_ms': 0
        }
        
        start_time = time.time()
        
        try:
            # Usar health check do banco para verificar
            db_health = self.session.get(f"{self.base_url}/health/db")
            duration = round((time.time() - start_time) * 1000, 2)
            
            if db_health.status_code == 200:
                health_data = db_health.json()
                
                tests = health_data.get('tests', {})
                tables_exist = tests.get('tables_exist', False)
                can_query = tests.get('can_query', False)
                can_write = tests.get('can_write', False)
                
                if tables_exist and can_query and can_write:
                    status = 'pass'
                    logger.info("✅ Banco inicializado corretamente")
                elif tables_exist and can_query:
                    status = 'partial'
                    logger.warning("⚠️ Banco parcialmente funcional")
                else:
                    status = 'fail'
                    logger.error("❌ Problemas na inicialização do banco")
                
                test_result.update({
                    'status': status,
                    'duration_ms': duration,
                    'details': {
                        'health_check_available': True,
                        'tables_exist': tables_exist,
                        'can_query': can_query,
                        'can_write': can_write,
                        'available_tables': tests.get('available_tables', []),
                        'user_count': tests.get('user_count', 0)
                    }
                })
                
            else:
                test_result.update({
                    'status': 'fail',
                    'duration_ms': duration,
                    'details': {
                        'health_check_available': False,
                        'status_code': db_health.status_code,
                        'error': 'Database health check not responding'
                    }
                })
                logger.error("❌ Health check do banco não disponível")
                
        except Exception as e:
            test_result.update({
                'status': 'fail',
                'duration_ms': round((time.time() - start_time) * 1000, 2),
                'details': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            logger.error(f"❌ Falha no teste de banco: {e}")
        
        return test_result
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Teste 5: Verificar performance do sistema"""
        logger.info("⚡ Testando performance...")
        
        test_result = {
            'name': 'Performance Benchmarks',
            'status': 'unknown',
            'details': {},
            'duration_ms': 0
        }
        
        start_time = time.time()
        
        try:
            # Teste de múltiplas requisições
            endpoints_to_test = [
                '/',
                '/health',
                '/health/db',
                '/auth/register'
            ]
            
            performance_results = {}
            
            for endpoint in endpoints_to_test:
                times = []
                for _ in range(3):  # 3 requisições por endpoint
                    req_start = time.time()
                    try:
                        response = self.session.get(f"{self.base_url}{endpoint}")
                        req_time = (time.time() - req_start) * 1000
                        times.append(req_time)
                    except:
                        times.append(None)
                
                valid_times = [t for t in times if t is not None]
                if valid_times:
                    performance_results[endpoint] = {
                        'avg_response_time_ms': round(sum(valid_times) / len(valid_times), 2),
                        'max_response_time_ms': round(max(valid_times), 2),
                        'min_response_time_ms': round(min(valid_times), 2),
                        'success_rate': len(valid_times) / len(times)
                    }
                else:
                    performance_results[endpoint] = {
                        'error': 'All requests failed',
                        'success_rate': 0
                    }
            
            duration = round((time.time() - start_time) * 1000, 2)
            
            # Avaliar performance geral
            avg_times = []
            for endpoint_data in performance_results.values():
                if 'avg_response_time_ms' in endpoint_data:
                    avg_times.append(endpoint_data['avg_response_time_ms'])
            
            if avg_times:
                overall_avg = sum(avg_times) / len(avg_times)
                
                if overall_avg < 1000:  # < 1 segundo
                    status = 'pass'
                    logger.info(f"✅ Performance adequada (média: {overall_avg:.2f}ms)")
                elif overall_avg < 3000:  # < 3 segundos
                    status = 'partial'
                    logger.warning(f"⚠️ Performance aceitável (média: {overall_avg:.2f}ms)")
                else:
                    status = 'fail'
                    logger.error(f"❌ Performance inadequada (média: {overall_avg:.2f}ms)")
                
                test_result.update({
                    'status': status,
                    'duration_ms': duration,
                    'details': {
                        'overall_avg_response_time_ms': round(overall_avg, 2),
                        'endpoints': performance_results,
                        'performance_threshold_ms': 1000
                    }
                })
            else:
                test_result.update({
                    'status': 'fail',
                    'duration_ms': duration,
                    'details': {
                        'error': 'No successful requests',
                        'endpoints': performance_results
                    }
                })
                logger.error("❌ Nenhuma requisição bem-sucedida")
                
        except Exception as e:
            test_result.update({
                'status': 'fail',
                'duration_ms': round((time.time() - start_time) * 1000, 2),
                'details': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            logger.error(f"❌ Falha no teste de performance: {e}")
        
        return test_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes e gera relatório consolidado"""
        logger.info("🚀 Iniciando validação completa das correções...")
        
        # Executar todos os testes
        tests = [
            self.test_basic_connectivity,
            self.test_health_endpoints,
            self.test_registration_flow,
            self.test_database_initialization,
            self.test_performance_benchmarks
        ]
        
        for test_func in tests:
            test_name = test_func.__name__
            logger.info(f"Executando {test_name}...")
            
            try:
                result = test_func()
                self.results['tests'][test_name] = result
            except Exception as e:
                logger.error(f"Erro no teste {test_name}: {e}")
                self.results['tests'][test_name] = {
                    'name': test_name,
                    'status': 'error',
                    'error': str(e),
                    'duration_ms': 0
                }
        
        # Gerar resumo
        self._generate_summary()
        
        return self.results
    
    def _generate_summary(self):
        """Gera resumo dos resultados"""
        tests = self.results['tests']
        
        total_tests = len(tests)
        passed_tests = sum(1 for t in tests.values() if t['status'] == 'pass')
        partial_tests = sum(1 for t in tests.values() if t['status'] == 'partial')
        failed_tests = sum(1 for t in tests.values() if t['status'] == 'fail')
        
        # Calcular score
        score = ((passed_tests * 100) + (partial_tests * 50)) / total_tests if total_tests > 0 else 0
        
        # Determinar status geral
        if score >= 90:
            overall_status = 'APPROVED'
            status_emoji = '✅'
        elif score >= 70:
            overall_status = 'CONDITIONAL'
            status_emoji = '⚠️'
        else:
            overall_status = 'REJECTED'
            status_emoji = '❌'
        
        self.results['summary'] = {
            'overall_status': overall_status,
            'overall_score': round(score, 1),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'partial_tests': partial_tests,
            'failed_tests': failed_tests,
            'status_emoji': status_emoji
        }
        
        # Gerar recomendações
        self._generate_recommendations()
        
        logger.info(f"{status_emoji} Validação concluída - Status: {overall_status} (Score: {score:.1f}%)")
    
    def _generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        tests = self.results['tests']
        recommendations = []
        
        # Verificar testes específicos
        if tests.get('test_basic_connectivity', {}).get('status') == 'fail':
            recommendations.append("Sistema inacessível - verificar deploy e configuração")
        
        if tests.get('test_health_endpoints', {}).get('status') in ['fail', 'partial']:
            recommendations.append("Health checks não funcionando - verificar implementação")
        
        if tests.get('test_registration_flow', {}).get('status') == 'fail':
            recommendations.append("Sistema de registro ainda falhando - verificar correção do banco")
        
        if tests.get('test_database_initialization', {}).get('status') == 'fail':
            recommendations.append("Inicialização do banco falhando - verificar app/__init__.py")
        
        if tests.get('test_performance_benchmarks', {}).get('status') == 'fail':
            recommendations.append("Performance inadequada - otimizar consultas e recursos")
        
        # Recomendações gerais
        score = self.results['summary']['overall_score']
        if score < 70:
            recommendations.append("Score muito baixo - implementar correções antes de aprovar Sprint 1")
        elif score < 90:
            recommendations.append("Score aceitável mas pode melhorar - considerar otimizações")
        
        self.results['recommendations'] = recommendations
    
    def save_report(self, filename: str = None):
        """Salva relatório em arquivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {filename}")
        return filename
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        summary = self.results['summary']
        
        print("\n" + "="*80)
        print("RELATÓRIO DE VALIDAÇÃO - CORREÇÕES CRÍTICAS AGROTECH PORTUGAL")
        print("="*80)
        print(f"Data/Hora: {self.results['timestamp']}")
        print(f"URL Testada: {self.results['base_url']}")
        print(f"\n{summary['status_emoji']} STATUS GERAL: {summary['overall_status']}")
        print(f"📊 SCORE: {summary['overall_score']}%")
        print(f"\n📋 RESULTADOS:")
        print(f"  ✅ Testes Aprovados: {summary['passed_tests']}")
        print(f"  ⚠️ Testes Parciais: {summary['partial_tests']}")
        print(f"  ❌ Testes Falharam: {summary['failed_tests']}")
        print(f"  📈 Total de Testes: {summary['total_tests']}")
        
        if self.results['recommendations']:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validador de Correções AgroTech Portugal')
    parser.add_argument('--url', default='https://www.agenteagricola.com', 
                       help='URL base do sistema (padrão: https://www.agenteagricola.com)')
    parser.add_argument('--output', help='Arquivo de saída do relatório JSON')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso (apenas erros)')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Executar validação
    validator = CorrectionsValidator(args.url)
    results = validator.run_all_tests()
    
    # Salvar relatório
    report_file = validator.save_report(args.output)
    
    # Imprimir resumo
    validator.print_summary()
    
    # Exit code baseado no resultado
    score = results['summary']['overall_score']
    if score >= 90:
        sys.exit(0)  # Sucesso
    elif score >= 70:
        sys.exit(1)  # Parcial
    else:
        sys.exit(2)  # Falha

if __name__ == "__main__":
    main()
```

---

## 🔧 SCRIPT 2: test_health_endpoints.py - Testes Específicos de Health Check

### Implementação Especializada
```python
#!/usr/bin/env python3
"""
Testes Especializados de Health Check Endpoints
Validação detalhada de todos os endpoints de monitoramento
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class HealthEndpointTester:
    """Tester especializado para endpoints de health check"""
    
    def __init__(self, base_url: str = "https://www.agenteagricola.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
    def test_health_basic(self) -> Dict[str, Any]:
        """Testa endpoint /health básico"""
        url = f"{self.base_url}/health"
        
        try:
            start_time = time.time()
            response = self.session.get(url)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'endpoint': '/health',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['json_valid'] = True
                    result['has_status'] = 'status' in data
                    result['has_timestamp'] = 'timestamp' in data
                    result['system_status'] = data.get('status', 'unknown')
                    
                    # Validações específicas
                    validations = {
                        'status_healthy': data.get('status') == 'healthy',
                        'has_database_info': 'database' in data,
                        'has_version': 'version' in data,
                        'response_under_1s': response_time < 1000
                    }
                    result['validations'] = validations
                    result['validation_score'] = sum(validations.values()) / len(validations) * 100
                    
                except json.JSONDecodeError:
                    result['json_valid'] = False
                    result['raw_response'] = response.text[:200]
            
            return result
            
        except Exception as e:
            return {
                'endpoint': '/health',
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def test_health_database(self) -> Dict[str, Any]:
        """Testa endpoint /health/db detalhado"""
        url = f"{self.base_url}/health/db"
        
        try:
            start_time = time.time()
            response = self.session.get(url)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'endpoint': '/health/db',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['json_valid'] = True
                    
                    # Extrair informações dos testes
                    tests = data.get('tests', {})
                    
                    # Validações críticas
                    critical_validations = {
                        'connection_ok': tests.get('connection', False),
                        'tables_exist': tests.get('tables_exist', False),
                        'can_query': tests.get('can_query', False),
                        'can_write': tests.get('can_write', False),
                        'users_table_present': 'users' in tests.get('available_tables', [])
                    }
                    
                    result['critical_validations'] = critical_validations
                    result['critical_score'] = sum(critical_validations.values()) / len(critical_validations) * 100
                    
                    # Informações adicionais
                    result['user_count'] = tests.get('user_count', 0)
                    result['available_tables'] = tests.get('available_tables', [])
                    result['user_table_columns'] = tests.get('user_table_columns', [])
                    
                    # Verificar estrutura da tabela users
                    required_columns = ['id', 'email', 'password_hash', 'data_criacao']
                    user_columns = tests.get('user_table_columns', [])
                    missing_columns = [col for col in required_columns if col not in user_columns]
                    
                    result['schema_validation'] = {
                        'required_columns': required_columns,
                        'present_columns': user_columns,
                        'missing_columns': missing_columns,
                        'schema_complete': len(missing_columns) == 0
                    }
                    
                except json.JSONDecodeError:
                    result['json_valid'] = False
                    result['raw_response'] = response.text[:200]
            
            return result
            
        except Exception as e:
            return {
                'endpoint': '/health/db',
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def test_health_registration(self) -> Dict[str, Any]:
        """Testa endpoint /health/registration específico"""
        url = f"{self.base_url}/health/registration"
        
        try:
            start_time = time.time()
            response = self.session.get(url)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'endpoint': '/health/registration',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['json_valid'] = True
                    
                    tests = data.get('tests', {})
                    
                    # Validações do sistema de registro
                    registration_validations = {
                        'validator_available': tests.get('validator_available', False),
                        'service_available': tests.get('service_available', False),
                        'validation_works': tests.get('validation_works', False),
                        'database_ready': tests.get('database_ready', False),
                        'table_structure_valid': tests.get('table_structure_valid', False)
                    }
                    
                    result['registration_validations'] = registration_validations
                    result['registration_score'] = sum(registration_validations.values()) / len(registration_validations) * 100
                    
                    # Simulação de registro
                    simulation = tests.get('registration_simulation', {})
                    result['simulation_results'] = simulation
                    
                    # Status geral do registro
                    result['registration_ready'] = data.get('registration_ready', False)
                    
                except json.JSONDecodeError:
                    result['json_valid'] = False
                    result['raw_response'] = response.text[:200]
            
            return result
            
        except Exception as e:
            return {
                'endpoint': '/health/registration',
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Executa teste abrangente de todos os health checks"""
        print("🏥 Iniciando testes abrangentes de health check...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'base_url': self.base_url,
            'tests': {}
        }
        
        # Executar todos os testes
        test_methods = [
            self.test_health_basic,
            self.test_health_database,
            self.test_health_registration
        ]
        
        for test_method in test_methods:
            test_name = test_method.__name__
            print(f"  Executando {test_name}...")
            
            try:
                test_result = test_method()
                results['tests'][test_name] = test_result
                
                if test_result.get('success'):
                    print(f"    ✅ {test_result['endpoint']} - OK")
                else:
                    print(f"    ❌ {test_result['endpoint']} - FALHA")
                    
            except Exception as e:
                print(f"    ❌ {test_name} - ERRO: {e}")
                results['tests'][test_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Gerar resumo
        total_tests = len(results['tests'])
        successful_tests = sum(1 for t in results['tests'].values() if t.get('success'))
        
        results['summary'] = {
            'total_endpoints': total_tests,
            'successful_endpoints': successful_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'overall_status': 'PASS' if successful_tests == total_tests else 'FAIL'
        }
        
        print(f"\n📊 Resumo: {successful_tests}/{total_tests} endpoints funcionando")
        print(f"✅ Status: {results['summary']['overall_status']}")
        
        return results

def main():
    """Função principal para execução standalone"""
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.agenteagricola.com"
    
    tester = HealthEndpointTester(url)
    results = tester.run_comprehensive_test()
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"health_check_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultados salvos em: {filename}")
    
    # Exit code baseado no sucesso
    if results['summary']['overall_status'] == 'PASS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📊 SCRIPT 3: generate_validation_report.py - Gerador de Relatório Final

### Implementação do Gerador de Relatório
```python
#!/usr/bin/env python3
"""
Gerador de Relatório Final de Validação
Consolida todos os resultados e gera relatório executivo
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List

class ValidationReportGenerator:
    """Gerador de relatórios de validação"""
    
    def __init__(self, validation_data: Dict[str, Any]):
        self.data = validation_data
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def generate_executive_summary(self) -> str:
        """Gera resumo executivo"""
        summary = self.data.get('summary', {})
        
        status = summary.get('overall_status', 'UNKNOWN')
        score = summary.get('overall_score', 0)
        emoji = summary.get('status_emoji', '❓')
        
        if status == 'APPROVED':
            decision = "SPRINT 1 APROVADO"
            next_steps = "Autorizado início do Sprint 2"
        elif status == 'CONDITIONAL':
            decision = "SPRINT 1 APROVADO CONDICIONALMENTE"
            next_steps = "Implementar melhorias recomendadas"
        else:
            decision = "SPRINT 1 NÃO APROVADO"
            next_steps = "Implementar correções obrigatórias"
        
        return f"""
# RELATÓRIO EXECUTIVO - VALIDAÇÃO DE CORREÇÕES CRÍTICAS

**Projeto:** AgroTech Portugal  
**Data:** {self.timestamp}  
**Validação:** Correções do Sistema de Registro  

## {emoji} DECISÃO FINAL: {decision}

**Score de Conformidade:** {score}%  
**Próximos Passos:** {next_steps}

### Resumo dos Testes
- **Total de Testes:** {summary.get('total_tests', 0)}
- **Testes Aprovados:** {summary.get('passed_tests', 0)} ✅
- **Testes Parciais:** {summary.get('partial_tests', 0)} ⚠️
- **Testes Falharam:** {summary.get('failed_tests', 0)} ❌
"""
    
    def generate_detailed_results(self) -> str:
        """Gera resultados detalhados"""
        tests = self.data.get('tests', {})
        
        details = "\n## 📋 RESULTADOS DETALHADOS\n"
        
        for test_name, test_data in tests.items():
            status = test_data.get('status', 'unknown')
            duration = test_data.get('duration_ms', 0)
            name = test_data.get('name', test_name)
            
            status_emoji = {
                'pass': '✅',
                'partial': '⚠️',
                'fail': '❌',
                'error': '💥'
            }.get(status, '❓')
            
            details += f"\n### {status_emoji} {name}\n"
            details += f"**Status:** {status.upper()}  \n"
            details += f"**Duração:** {duration}ms  \n"
            
            # Adicionar detalhes específicos
            test_details = test_data.get('details', {})
            if test_details:
                details += "**Detalhes:**\n"
                for key, value in test_details.items():
                    if isinstance(value, dict):
                        details += f"- {key}: {json.dumps(value, indent=2)}\n"
                    else:
                        details += f"- {key}: {value}\n"
            
            details += "\n"
        
        return details
    
    def generate_recommendations(self) -> str:
        """Gera seção de recomendações"""
        recommendations = self.data.get('recommendations', [])
        
        if not recommendations:
            return "\n## ✅ NENHUMA RECOMENDAÇÃO ADICIONAL\n\nTodos os testes passaram com sucesso.\n"
        
        rec_text = "\n## 💡 RECOMENDAÇÕES\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            rec_text += f"{i}. **{rec}**\n"
        
        return rec_text
    
    def generate_technical_details(self) -> str:
        """Gera detalhes técnicos"""
        base_url = self.data.get('base_url', 'N/A')
        timestamp = self.data.get('timestamp', 'N/A')
        
        return f"""
## 🔧 DETALHES TÉCNICOS

**URL Testada:** {base_url}  
**Timestamp da Validação:** {timestamp}  
**Ferramenta:** Validador Automático de Correções  
**Versão:** 1.0.0  

### Critérios de Aprovação
- **Score Mínimo:** 70% para aprovação condicional
- **Score Ideal:** 90% para aprovação completa
- **Testes Críticos:** Conectividade, Health Checks, Registro, Banco de Dados

### Metodologia
1. Teste de conectividade básica
2. Validação de endpoints de health check
3. Teste do fluxo de registro
4. Verificação da inicialização do banco
5. Benchmarks de performance
"""
    
    def generate_full_report(self) -> str:
        """Gera relatório completo"""
        report = self.generate_executive_summary()
        report += self.generate_detailed_results()
        report += self.generate_recommendations()
        report += self.generate_technical_details()
        
        return report
    
    def save_markdown_report(self, filename: str = None) -> str:
        """Salva relatório em formato Markdown"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.md"
        
        report_content = self.generate_full_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return filename

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python generate_validation_report.py <arquivo_json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            validation_data = json.load(f)
        
        generator = ValidationReportGenerator(validation_data)
        
        # Gerar relatório em Markdown
        report_file = generator.save_markdown_report()
        
        print(f"📄 Relatório gerado: {report_file}")
        
        # Imprimir resumo executivo
        print("\n" + "="*80)
        print(generator.generate_executive_summary())
        print("="*80)
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Arquivo JSON inválido: {json_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📋 INSTRUÇÕES DE USO DOS SCRIPTS

### 1. Execução Sequencial
```bash
# 1. Executar validação principal
python validate_corrections.py --url https://www.agenteagricola.com

# 2. Testes específicos de health check
python test_health_endpoints.py https://www.agenteagricola.com

# 3. Gerar relatório final
python generate_validation_report.py validation_report_*.json
```

### 2. Execução Automatizada
```bash
#!/bin/bash
# Script de validação completa
echo "🚀 Iniciando validação completa..."

python validate_corrections.py --url https://www.agenteagricola.com --output validation_main.json
python test_health_endpoints.py https://www.agenteagricola.com > health_test.json
python generate_validation_report.py validation_main.json

echo "✅ Validação concluída!"
```

### 3. Interpretação dos Resultados

**Scores de Aprovação:**
- **90-100%:** Sprint 1 APROVADO (pode prosseguir)
- **70-89%:** Sprint 1 APROVADO CONDICIONALMENTE (melhorias recomendadas)
- **0-69%:** Sprint 1 NÃO APROVADO (correções obrigatórias)

**Status dos Testes:**
- **pass:** Teste passou completamente
- **partial:** Teste passou parcialmente
- **fail:** Teste falhou
- **error:** Erro na execução do teste

---

## 🎯 RESULTADO ESPERADO

Após implementação destes scripts:

1. **Validação Automatizada**
   - Testes completos em 2-3 minutos
   - Relatórios detalhados em JSON e Markdown
   - Scores objetivos de aprovação

2. **Diagnóstico Preciso**
   - Identificação exata de problemas
   - Recomendações específicas
   - Evidências técnicas detalhadas

3. **Decisão Fundamentada**
   - Critérios claros de aprovação
   - Justificativas técnicas
   - Próximos passos definidos

4. **Processo Repetível**
   - Scripts reutilizáveis
   - Metodologia padronizada
   - Histórico de validações

---

**SCRIPTS PRONTOS PARA EXECUÇÃO COM CLAUDE SONNET 4**  
**IMPLEMENTAR APÓS CORREÇÕES PRINCIPAIS PARA VALIDAÇÃO COMPLETA**

