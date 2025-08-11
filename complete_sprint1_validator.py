#!/usr/bin/env python3
"""
Script Principal de Validação das Correções Críticas - AgroTech Portugal
Executa testes automatizados para verificar implementação dos 3 prompts
Autor: Gerente de Tecnologia
Data: 1 de agosto de 2025
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

class CorrectionsValidator:
    """Validador completo das correções críticas implementadas"""
    
    def __init__(self, base_url: str = "https://www.agenteagricola.com"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_database_initialization(self) -> Dict[str, Any]:
        """Teste 1: Validar inicialização automática do banco (PROMPT 1)"""
        print("\n🗄️ TESTE 1: INICIALIZAÇÃO DO BANCO DE DADOS")
        print("=" * 60)
        
        test_result = {
            'test_name': 'Database Initialization (PROMPT 1)',
            'status': 'unknown',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Verificar se health check do banco está disponível
            response = self.session.get(f"{self.base_url}/health/db")
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Verificar se tabelas existem
                tables_exist = health_data.get('tests', {}).get('tables_exist', False)
                available_tables = health_data.get('tests', {}).get('available_tables', [])
                user_count = health_data.get('tests', {}).get('user_count', 0)
                
                if tables_exist and 'users' in available_tables:
                    test_result['status'] = 'PASS'
                    test_result['details'] = {
                        'tables_created': True,
                        'users_table_exists': True,
                        'available_tables': available_tables,
                        'user_count': user_count,
                        'database_status': health_data.get('status'),
                        'validation': 'db.create_all() funcionando corretamente'
                    }
                    print("✅ Inicialização do banco: APROVADA")
                    print(f"   - Tabelas criadas automaticamente: {len(available_tables)}")
                    print(f"   - Tabela 'users' existe: {True}")
                    print(f"   - Usuários no sistema: {user_count}")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details'] = {
                        'tables_created': tables_exist,
                        'users_table_exists': 'users' in available_tables,
                        'error': 'Tabelas críticas não encontradas'
                    }
                    print("❌ Inicialização do banco: FALHOU")
                    print("   - Tabelas não foram criadas automaticamente")
            else:
                test_result['status'] = 'FAIL'
                test_result['details'] = {
                    'error': f"Health check do banco inacessível: {response.status_code}",
                    'validation': 'Inicialização pode não ter funcionado'
                }
                print("❌ Inicialização do banco: FALHOU")
                print("   - Health check do banco não disponível")
                
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['details'] = {
                'error': str(e),
                'error_type': type(e).__name__
            }
            print(f"❌ Erro no teste de inicialização: {e}")
        
        return test_result
    
    def test_health_check_implementation(self) -> Dict[str, Any]:
        """Teste 2: Validar implementação dos health checks (PROMPT 2)"""
        print("\n🏥 TESTE 2: IMPLEMENTAÇÃO DOS HEALTH CHECKS")
        print("=" * 60)
        
        test_result = {
            'test_name': 'Health Check Implementation (PROMPT 2)',
            'status': 'unknown',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        endpoints_to_test = [
            '/health',
            '/health/db',
            '/health/registration'
        ]
        
        endpoint_results = {}
        total_passed = 0
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                endpoint_result = {
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'content_type': response.headers.get('content-type', ''),
                    'has_json': False,
                    'json_valid': False
                }
                
                # Verificar se resposta é JSON válida
                try:
                    json_data = response.json()
                    endpoint_result['has_json'] = True
                    endpoint_result['json_valid'] = True
                    endpoint_result['status_field'] = json_data.get('status', 'unknown')
                    endpoint_result['has_timestamp'] = 'timestamp' in json_data
                    
                    if response.status_code == 200:
                        endpoint_result['test_status'] = 'PASS'
                        total_passed += 1
                        print(f"✅ {endpoint}: FUNCIONANDO")
                        print(f"   - Status: {json_data.get('status', 'N/A')}")
                        print(f"   - Tempo: {endpoint_result['response_time_ms']:.1f}ms")
                    else:
                        endpoint_result['test_status'] = 'FAIL'
                        print(f"❌ {endpoint}: FALHOU ({response.status_code})")
                        
                except json.JSONDecodeError:
                    endpoint_result['test_status'] = 'FAIL'
                    endpoint_result['error'] = 'Resposta não é JSON válido'
                    print(f"❌ {endpoint}: FALHOU (JSON inválido)")
                
                endpoint_results[endpoint] = endpoint_result
                
            except Exception as e:
                endpoint_results[endpoint] = {
                    'test_status': 'ERROR',
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                print(f"❌ {endpoint}: ERRO ({e})")
        
        # Avaliar resultado geral
        total_endpoints = len(endpoints_to_test)
        success_rate = (total_passed / total_endpoints) * 100
        
        if total_passed == total_endpoints:
            test_result['status'] = 'PASS'
        elif total_passed >= 2:  # Pelo menos 2 de 3
            test_result['status'] = 'PARTIAL'
        else:
            test_result['status'] = 'FAIL'
        
        test_result['details'] = {
            'endpoints_tested': total_endpoints,
            'endpoints_passed': total_passed,
            'success_rate': success_rate,
            'endpoints': endpoint_results,
            'validation': f'Health checks implementados conforme PROMPT 2'
        }
        
        print(f"\n📊 Resumo Health Checks: {total_passed}/{total_endpoints} funcionando ({success_rate:.1f}%)")
        
        return test_result
    
    def test_registration_system(self) -> Dict[str, Any]:
        """Teste 3: Validar sistema de registro corrigido"""
        print("\n📝 TESTE 3: SISTEMA DE REGISTRO")
        print("=" * 60)
        
        test_result = {
            'test_name': 'Registration System Validation',
            'status': 'unknown',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Passo 1: Verificar se página de registro carrega
            reg_page = self.session.get(f"{self.base_url}/auth/register")
            
            if reg_page.status_code == 200:
                print("✅ Página de registro: ACESSÍVEL")
                
                # Passo 2: Verificar health check específico de registro
                reg_health = self.session.get(f"{self.base_url}/health/registration")
                
                if reg_health.status_code == 200:
                    health_data = reg_health.json()
                    
                    if health_data.get('status') == 'healthy':
                        test_result['status'] = 'PASS'
                        test_result['details'] = {
                            'page_accessible': True,
                            'health_check_status': 'healthy',
                            'registration_ready': health_data.get('registration_ready', False),
                            'critical_tests_passed': health_data.get('critical_tests_passed', 0),
                            'validation': 'Sistema de registro funcionando'
                        }
                        print("✅ Sistema de registro: FUNCIONANDO")
                        print(f"   - Health status: {health_data.get('status')}")
                        print(f"   - Pronto para registros: {health_data.get('registration_ready', False)}")
                    else:
                        test_result['status'] = 'PARTIAL'
                        test_result['details'] = {
                            'page_accessible': True,
                            'health_check_status': health_data.get('status'),
                            'registration_ready': health_data.get('registration_ready', False),
                            'recommendations': health_data.get('recommendations', [])
                        }
                        print("⚠️ Sistema de registro: PARCIALMENTE FUNCIONANDO")
                        print(f"   - Status: {health_data.get('status')}")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details'] = {
                        'page_accessible': True,
                        'health_check_available': False,
                        'error': f"Health check de registro falhou: {reg_health.status_code}"
                    }
                    print("❌ Health check de registro: INDISPONÍVEL")
            else:
                test_result['status'] = 'FAIL'
                test_result['details'] = {
                    'page_accessible': False,
                    'status_code': reg_page.status_code,
                    'error': 'Página de registro inacessível'
                }
                print(f"❌ Página de registro: INACESSÍVEL ({reg_page.status_code})")
                
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['details'] = {
                'error': str(e),
                'error_type': type(e).__name__
            }
            print(f"❌ Erro no teste de registro: {e}")
        
        return test_result
    
    def test_logs_and_monitoring(self) -> Dict[str, Any]:
        """Teste 4: Validar logs e monitoramento"""
        print("\n📊 TESTE 4: LOGS E MONITORAMENTO")
        print("=" * 60)
        
        test_result = {
            'test_name': 'Logs and Monitoring Validation',
            'status': 'unknown',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Verificar se health checks têm timestamps
            health_response = self.session.get(f"{self.base_url}/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                has_timestamp = 'timestamp' in health_data
                has_version = 'version' in health_data
                has_environment = 'environment' in health_data
                
                # Verificar health check detalhado
                db_response = self.session.get(f"{self.base_url}/health/db")
                db_has_logs = False
                
                if db_response.status_code == 200:
                    db_data = db_response.json()
                    db_has_logs = 'timestamp' in db_data.get('tests', {})
                
                monitoring_score = sum([has_timestamp, has_version, has_environment, db_has_logs])
                
                if monitoring_score >= 3:
                    test_result['status'] = 'PASS'
                    print("✅ Logs e monitoramento: ADEQUADOS")
                elif monitoring_score >= 2:
                    test_result['status'] = 'PARTIAL'
                    print("⚠️ Logs e monitoramento: PARCIAIS")
                else:
                    test_result['status'] = 'FAIL'
                    print("❌ Logs e monitoramento: INADEQUADOS")
                
                test_result['details'] = {
                    'has_timestamp': has_timestamp,
                    'has_version': has_version,
                    'has_environment': has_environment,
                    'db_has_logs': db_has_logs,
                    'monitoring_score': f"{monitoring_score}/4",
                    'validation': 'Logs de inicialização e timestamps presentes'
                }
                
                print(f"   - Timestamps: {'✅' if has_timestamp else '❌'}")
                print(f"   - Versão: {'✅' if has_version else '❌'}")
                print(f"   - Environment: {'✅' if has_environment else '❌'}")
                print(f"   - DB Logs: {'✅' if db_has_logs else '❌'}")
                
            else:
                test_result['status'] = 'FAIL'
                test_result['details'] = {
                    'error': 'Health check principal inacessível',
                    'status_code': health_response.status_code
                }
                print("❌ Health check principal inacessível")
                
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['details'] = {
                'error': str(e),
                'error_type': type(e).__name__
            }
            print(f"❌ Erro no teste de logs: {e}")
        
        return test_result
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Executa todos os testes de validação"""
        print("🚀 VALIDAÇÃO COMPLETA DAS CORREÇÕES CRÍTICAS")
        print("=" * 80)
        print(f"URL Testada: {self.base_url}")
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Executar todos os testes
        self.results = [
            self.test_database_initialization(),
            self.test_health_check_implementation(),
            self.test_registration_system(),
            self.test_logs_and_monitoring()
        ]
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório consolidado de validação"""
        if not self.results:
            self.run_all_tests()
        
        # Contar resultados
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['status'] == 'PASS')
        partial_tests = sum(1 for r in self.results if r['status'] == 'PARTIAL')
        failed_tests = sum(1 for r in self.results if r['status'] in ['FAIL', 'ERROR'])
        
        # Calcular score final
        score = ((passed_tests * 100) + (partial_tests * 50)) / total_tests if total_tests > 0 else 0
        
        # Determinar status de aprovação
        if score >= 95:
            approval_status = 'APPROVED - EXCELENTE'
            approval_emoji = '🎉'
        elif score >= 85:
            approval_status = 'APPROVED - BOM'
            approval_emoji = '✅'
        elif score >= 70:
            approval_status = 'CONDITIONAL - ACEITÁVEL'
            approval_emoji = '⚠️'
        else:
            approval_status = 'REJECTED - INADEQUADO'
            approval_emoji = '❌'
        
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'partial_tests': partial_tests,
            'failed_tests': failed_tests,
            'final_score': round(score, 1),
            'approval_status': approval_status,
            'approval_emoji': approval_emoji,
            'results': self.results,
            'sprint_1_ready': score >= 85
        }
        
        return report
    
    def print_final_report(self):
        """Imprime relatório final formatado"""
        report = self.generate_report()
        
        print("\n" + "=" * 80)
        print("RELATÓRIO FINAL DE VALIDAÇÃO - SPRINT 1")
        print("=" * 80)
        print(f"📊 SCORE FINAL: {report['final_score']}%")
        print(f"{report['approval_emoji']} STATUS: {report['approval_status']}")
        print(f"\n📋 RESULTADOS DETALHADOS:")
        print(f"  ✅ Testes Aprovados: {report['passed_tests']}")
        print(f"  ⚠️ Testes Parciais: {report['partial_tests']}")
        print(f"  ❌ Testes Falharam: {report['failed_tests']}")
        print(f"  📈 Total de Testes: {report['total_tests']}")
        
        print(f"\n🚀 SPRINT 1 PRONTO: {'SIM' if report['sprint_1_ready'] else 'NÃO'}")
        
        print("\n📝 CHECKLIST DE CONFORMIDADE:")
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
            print(f"  {i}. {status_icon} {result['test_name']}")
        
        if report['sprint_1_ready']:
            print("\n🎉 TODAS AS CORREÇÕES VALIDADAS - SPRINT 1 APROVADO!")
        else:
            print("\n⚠️ CORREÇÕES ADICIONAIS NECESSÁRIAS ANTES DA APROVAÇÃO")
        
        print("=" * 80)
    
    def save_report(self, filename: str = None):
        """Salva relatório em arquivo JSON"""
        report = self.generate_report()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sprint1_validation_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório detalhado salvo em: {filename}")
        return filename

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validador de Correções Críticas AgroTech Portugal')
    parser.add_argument('--url', default='https://www.agenteagricola.com', 
                       help='URL base do sistema')
    parser.add_argument('--output', help='Arquivo de saída do relatório')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso')
    
    args = parser.parse_args()
    
    # Executar validação
    validator = CorrectionsValidator(args.url)
    validator.run_all_tests()
    
    # Gerar e salvar relatório
    report_file = validator.save_report(args.output)
    
    # Imprimir relatório final
    if not args.quiet:
        validator.print_final_report()
    
    # Exit code baseado no score
    report = validator.generate_report()
    final_score = report['final_score']
    
    if final_score >= 95:
        sys.exit(0)  # Excelente
    elif final_score >= 85:
        sys.exit(0)  # Aprovado
    elif final_score >= 70:
        sys.exit(1)  # Condicional
    else:
        sys.exit(2)  # Rejeitado

if __name__ == "__main__":
    main()
