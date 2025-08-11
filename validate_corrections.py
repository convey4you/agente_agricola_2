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
