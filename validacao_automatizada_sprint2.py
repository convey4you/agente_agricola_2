#!/usr/bin/env python3
"""
Script de Validação Automatizada Sprint 2
PROMPT 4 - Implementação de Testes Automatizados

Este script valida o sistema de alertas em ambiente de produção
Executa uma bateria completa de testes para garantir que tudo funciona
"""
import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any


class AlertsValidationSuite:
    """Suite de validação para sistema de alertas"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
        self.test_user_email = "validation_test@agrotech.pt"
        self.test_user_password = "validation123!"
        
    def log_result(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Registrar resultado de teste"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details and not passed:
            print(f"   Detalhes: {json.dumps(details, indent=2)}")
    
    def create_test_user(self) -> bool:
        """Criar usuário de teste (se não existir)"""
        try:
            # Tentar registrar usuário
            register_data = {
                'nome_completo': 'Validation Test User',
                'email': self.test_user_email,
                'password': self.test_user_password,
                'confirmar_password': self.test_user_password,
                'telefone': '123456789',
                'propriedade_nome': 'Quinta de Testes',
                'cidade': 'Lisboa',
                'estado': 'Lisboa'
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                data=register_data
            )
            
            # Se registro falhou, pode ser porque usuário já existe
            # Tentar fazer login direto
            return self.login_test_user()
            
        except Exception as e:
            self.log_result(
                "create_test_user",
                False,
                f"Erro ao criar usuário de teste: {str(e)}"
            )
            return False
    
    def login_test_user(self) -> bool:
        """Fazer login com usuário de teste"""
        try:
            login_data = {
                'email': self.test_user_email,
                'password': self.test_user_password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                self.log_result(
                    "login_test_user",
                    True,
                    "Login realizado com sucesso"
                )
                return True
            else:
                self.log_result(
                    "login_test_user",
                    False,
                    f"Falha no login: {response.status_code}",
                    {'response_text': response.text[:500]}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "login_test_user",
                False,
                f"Erro ao fazer login: {str(e)}"
            )
            return False
    
    def test_health_checks(self) -> bool:
        """Testar endpoints de health check"""
        try:
            # Health check geral
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                self.log_result(
                    "health_check_general",
                    False,
                    f"Health check geral falhou: {response.status_code}"
                )
                return False
            
            self.log_result(
                "health_check_general",
                True,
                "Health check geral funcionando"
            )
            
            # Health check da API de alertas
            response = self.session.get(f"{self.base_url}/api/alerts/health")
            
            if response.status_code != 200:
                self.log_result(
                    "health_check_alerts",
                    False,
                    f"Health check de alertas falhou: {response.status_code}"
                )
                return False
            
            data = response.json()
            if data.get('status') != 'success':
                self.log_result(
                    "health_check_alerts",
                    False,
                    "Health check de alertas retornou status de erro",
                    {'response': data}
                )
                return False
            
            self.log_result(
                "health_check_alerts",
                True,
                f"Health check de alertas OK - {data.get('data', {}).get('total_alerts', 0)} alertas no sistema"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "health_checks",
                False,
                f"Erro nos health checks: {str(e)}"
            )
            return False
    
    def test_alerts_widget(self) -> bool:
        """Testar endpoint do widget de alertas"""
        try:
            response = self.session.get(f"{self.base_url}/api/alerts/widget")
            
            if response.status_code != 200:
                self.log_result(
                    "alerts_widget",
                    False,
                    f"Widget de alertas falhou: {response.status_code}",
                    {'response_text': response.text[:500]}
                )
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result(
                    "alerts_widget",
                    False,
                    "Widget retornou success=False",
                    {'response': data}
                )
                return False
            
            # Verificar estrutura dos dados
            required_keys = ['data']
            data_keys = ['stats', 'critical_alerts', 'recent_alerts']
            stats_keys = ['total', 'unread', 'critical']
            
            for key in required_keys:
                if key not in data:
                    self.log_result(
                        "alerts_widget",
                        False,
                        f"Chave '{key}' não encontrada na resposta"
                    )
                    return False
            
            for key in data_keys:
                if key not in data['data']:
                    self.log_result(
                        "alerts_widget",
                        False,
                        f"Chave '{key}' não encontrada em data"
                    )
                    return False
            
            for key in stats_keys:
                if key not in data['data']['stats']:
                    self.log_result(
                        "alerts_widget",
                        False,
                        f"Chave '{key}' não encontrada em stats"
                    )
                    return False
            
            stats = data['data']['stats']
            self.log_result(
                "alerts_widget",
                True,
                f"Widget funcionando - Total: {stats['total']}, Não lidos: {stats['unread']}, Críticos: {stats['critical']}"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "alerts_widget",
                False,
                f"Erro no widget de alertas: {str(e)}"
            )
            return False
    
    def test_alerts_crud(self) -> bool:
        """Testar operações CRUD de alertas"""
        try:
            # 1. Listar alertas
            response = self.session.get(f"{self.base_url}/api/alerts/")
            
            if response.status_code != 200:
                self.log_result(
                    "alerts_list",
                    False,
                    f"Listagem de alertas falhou: {response.status_code}"
                )
                return False
            
            list_data = response.json()
            initial_count = list_data['data']['total']
            
            self.log_result(
                "alerts_list",
                True,
                f"Listagem funcionando - {initial_count} alertas encontrados"
            )
            
            # 2. Criar novo alerta
            new_alert_data = {
                'type': 'general',
                'priority': 'medium',
                'title': 'Alerta de Validação Automatizada',
                'message': f'Alerta criado automaticamente em {datetime.utcnow().isoformat()} para validação do sistema.',
                'action_text': 'Ver Detalhes',
                'action_url': '/validation/details'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/alerts/create",
                json=new_alert_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 201:
                self.log_result(
                    "alerts_create",
                    False,
                    f"Criação de alerta falhou: {response.status_code}",
                    {'response_text': response.text[:500]}
                )
                return False
            
            create_data = response.json()
            created_alert = create_data['data']['alert']
            alert_id = created_alert['id']
            
            self.log_result(
                "alerts_create",
                True,
                f"Alerta criado com sucesso - ID: {alert_id}"
            )
            
            # 3. Marcar como lido
            response = self.session.post(f"{self.base_url}/api/alerts/{alert_id}/read")
            
            if response.status_code != 200:
                self.log_result(
                    "alerts_mark_read",
                    False,
                    f"Marcar como lido falhou: {response.status_code}"
                )
                return False
            
            self.log_result(
                "alerts_mark_read",
                True,
                f"Alerta {alert_id} marcado como lido"
            )
            
            # 4. Resolver alerta
            response = self.session.post(f"{self.base_url}/api/alerts/{alert_id}/resolve")
            
            if response.status_code != 200:
                self.log_result(
                    "alerts_resolve",
                    False,
                    f"Resolver alerta falhou: {response.status_code}"
                )
                return False
            
            self.log_result(
                "alerts_resolve",
                True,
                f"Alerta {alert_id} resolvido"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "alerts_crud",
                False,
                f"Erro nas operações CRUD: {str(e)}"
            )
            return False
    
    def test_alerts_generation(self) -> bool:
        """Testar geração de alertas de exemplo"""
        try:
            response = self.session.post(f"{self.base_url}/api/alerts/generate")
            
            if response.status_code != 200:
                self.log_result(
                    "alerts_generate",
                    False,
                    f"Geração de alertas falhou: {response.status_code}",
                    {'response_text': response.text[:500]}
                )
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result(
                    "alerts_generate",
                    False,
                    "Geração retornou success=False",
                    {'response': data}
                )
                return False
            
            generated_count = data.get('count', 0)
            
            self.log_result(
                "alerts_generate",
                True,
                f"{generated_count} alertas de exemplo gerados"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "alerts_generate",
                False,
                f"Erro na geração de alertas: {str(e)}"
            )
            return False
    
    def test_bulk_operations(self) -> bool:
        """Testar operações em lote"""
        try:
            # Marcar todos como lidos
            response = self.session.post(f"{self.base_url}/api/alerts/bulk-read")
            
            if response.status_code != 200:
                self.log_result(
                    "alerts_bulk_read",
                    False,
                    f"Operação em lote falhou: {response.status_code}"
                )
                return False
            
            data = response.json()
            marked_count = data.get('data', {}).get('marked_count', 0)
            
            self.log_result(
                "alerts_bulk_read",
                True,
                f"{marked_count} alertas marcados como lidos em lote"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "alerts_bulk_operations",
                False,
                f"Erro nas operações em lote: {str(e)}"
            )
            return False
    
    def test_performance(self) -> bool:
        """Testar performance dos endpoints críticos"""
        try:
            tests = [
                ('Widget', f"{self.base_url}/api/alerts/widget"),
                ('Listagem', f"{self.base_url}/api/alerts/"),
                ('Health Check', f"{self.base_url}/api/alerts/health")
            ]
            
            all_passed = True
            
            for test_name, url in tests:
                start_time = time.time()
                response = self.session.get(url)
                end_time = time.time()
                
                response_time = end_time - start_time
                max_time = 2.0  # 2 segundos máximo
                
                if response.status_code != 200:
                    self.log_result(
                        f"performance_{test_name.lower()}",
                        False,
                        f"{test_name} falhou: {response.status_code}"
                    )
                    all_passed = False
                    continue
                
                if response_time > max_time:
                    self.log_result(
                        f"performance_{test_name.lower()}",
                        False,
                        f"{test_name} muito lento: {response_time:.2f}s (max: {max_time}s)"
                    )
                    all_passed = False
                else:
                    self.log_result(
                        f"performance_{test_name.lower()}",
                        True,
                        f"{test_name} respondeu em {response_time:.2f}s"
                    )
            
            return all_passed
            
        except Exception as e:
            self.log_result(
                "performance_tests",
                False,
                f"Erro nos testes de performance: {str(e)}"
            )
            return False
    
    def run_validation(self) -> Dict[str, Any]:
        """Executar validação completa"""
        print("🚀 Iniciando Validação Automatizada do Sistema de Alertas")
        print("=" * 60)
        
        start_time = time.time()
        
        # Sequência de testes
        test_sequence = [
            ("Health Checks", self.test_health_checks),
            ("Criar/Login Usuário", self.create_test_user),
            ("Widget de Alertas", self.test_alerts_widget),
            ("Operações CRUD", self.test_alerts_crud),
            ("Geração de Alertas", self.test_alerts_generation),
            ("Operações em Lote", self.test_bulk_operations),
            ("Testes de Performance", self.test_performance)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_func in test_sequence:
            print(f"\n📋 Executando: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                if result:
                    print(f"✅ {test_name} - SUCESSO")
                else:
                    print(f"❌ {test_name} - FALHOU")
            except Exception as e:
                print(f"💥 {test_name} - ERRO: {str(e)}")
                self.log_result(test_name, False, f"Exceção: {str(e)}")
        
        # Calcular resultados
        for result in self.results:
            total_tests += 1
            if result['passed']:
                passed_tests += 1
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DA VALIDAÇÃO")
        print("=" * 60)
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {total_tests - passed_tests}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        print(f"Tempo de execução: {execution_time:.2f}s")
        
        if success_rate >= 80:
            print("🎉 VALIDAÇÃO APROVADA - Sistema funcionando corretamente!")
            exit_code = 0
        else:
            print("⚠️  VALIDAÇÃO FALHOU - Problemas detectados no sistema!")
            exit_code = 1
        
        # Salvar relatório
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'status': 'PASSED' if success_rate >= 80 else 'FAILED'
            },
            'details': self.results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: validation_report.json")
        
        return report


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validação Automatizada do Sistema de Alertas')
    parser.add_argument('--url', default='http://localhost:5000', help='URL base da aplicação')
    parser.add_argument('--email', default='validation_test@agrotech.pt', help='Email do usuário de teste')
    parser.add_argument('--password', default='validation123!', help='Senha do usuário de teste')
    
    args = parser.parse_args()
    
    validator = AlertsValidationSuite(base_url=args.url)
    validator.test_user_email = args.email
    validator.test_user_password = args.password
    
    report = validator.run_validation()
    
    # Exit code baseado no resultado
    exit_code = 0 if report['summary']['success_rate'] >= 80 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
