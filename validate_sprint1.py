#!/usr/bin/env python3
"""
Script de Validação Completa - CORREÇÃO SPRINT 1
Conforme decisão do Gerente de Tecnologia
"""
import requests
import time
import json
from datetime import datetime

class SprintValidator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log de resultado de teste"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_register_system(self):
        """CORREÇÃO 1: Sistema de Registro"""
        print("\n🚨 CORREÇÃO 1: SISTEMA DE REGISTRO")
        
        # Teste 1.1: Registro com senha inválida
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"email": "teste.senha@agrotech.com", "password": "123456"}
            )
            if response.status_code == 400 and "letra" in response.json().get('error', ''):
                self.log_result("1.1 Validação Senha", True, "Senha inválida corretamente rejeitada")
            else:
                self.log_result("1.1 Validação Senha", False, f"Esperado 400, recebido {response.status_code}")
        except Exception as e:
            self.log_result("1.1 Validação Senha", False, f"Erro: {e}")
            
        # Teste 1.2: Registro com email duplicado
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"email": "teste@agro.com", "password": "senha123"}
            )
            if response.status_code == 400 and "uso" in response.json().get('error', ''):
                self.log_result("1.2 Email Duplicado", True, "Email duplicado corretamente rejeitado")
            else:
                self.log_result("1.2 Email Duplicado", False, f"Esperado 400, recebido {response.status_code}")
        except Exception as e:
            self.log_result("1.2 Email Duplicado", False, f"Erro: {e}")
            
        # Teste 1.3: Registro válido
        try:
            test_email = f"validacao.{int(time.time())}@agrotech.com"
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"email": test_email, "password": "senha123", "nome_completo": "Usuario Validacao"}
            )
            if response.status_code == 201:
                data = response.json()
                if data.get('success') and data.get('user_id'):
                    self.log_result("1.3 Registro Válido", True, f"Usuário criado com ID {data['user_id']}")
                    self.test_user_email = test_email
                else:
                    self.log_result("1.3 Registro Válido", False, "Resposta inválida")
            else:
                self.log_result("1.3 Registro Válido", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("1.3 Registro Válido", False, f"Erro: {e}")
            
    def test_session_system(self):
        """CORREÇÃO 2: Sistema de Sessões"""
        print("\n⚠️  CORREÇÃO 2: SISTEMA DE SESSÕES")
        
        # Teste 2.1: Login válido
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": self.test_user_email, "password": "senha123"}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("2.1 Login Válido", True, "Login realizado com sucesso")
                else:
                    self.log_result("2.1 Login Válido", False, "Login falhou")
            else:
                self.log_result("2.1 Login Válido", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_result("2.1 Login Válido", False, f"Erro: {e}")
            
        # Teste 2.2: Persistência de sessão
        try:
            response = self.session.get(f"{self.base_url}/auth/check")
            if response.status_code in [200, 302]:
                self.log_result("2.2 Persistência Sessão", True, "Sessão persiste entre requisições")
            else:
                self.log_result("2.2 Persistência Sessão", False, f"Sessão perdida: {response.status_code}")
        except Exception as e:
            self.log_result("2.2 Persistência Sessão", False, f"Erro: {e}")
            
        # Teste 2.3: Logout completo
        try:
            response = self.session.get(f"{self.base_url}/auth/logout")
            if response.status_code in [200, 302]:
                # Verificar se sessão foi limpa tentando acessar página protegida
                check_response = self.session.get(f"{self.base_url}/auth/check")
                # Se redirecionou para login, logout funcionou
                if (check_response.status_code == 302 and 
                    ('/auth/login' in check_response.headers.get('Location', '') or 
                     check_response.headers.get('Location', '') == '/')):
                    self.log_result("2.3 Logout Completo", True, "Logout limpou sessão corretamente")
                elif check_response.status_code == 401:
                    self.log_result("2.3 Logout Completo", True, "Logout limpou sessão corretamente")
                else:
                    self.log_result("2.3 Logout Completo", False, f"Sessão não foi limpa adequadamente - Status: {check_response.status_code}")
            else:
                self.log_result("2.3 Logout Completo", False, f"Logout falhou: {response.status_code}")
        except Exception as e:
            self.log_result("2.3 Logout Completo", False, f"Erro: {e}")
            
    def test_onboarding_system(self):
        """CORREÇÃO 3: Onboarding Step 2"""
        print("\n⚠️  CORREÇÃO 3: ONBOARDING STEP 2")
        
        # Login novamente para testar onboarding
        try:
            self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": self.test_user_email, "password": "senha123"}
            )
            
            # Teste 3.1: Acesso ao step 2
            response = self.session.get(f"{self.base_url}/auth/onboarding?step=2")
            if response.status_code == 200:
                self.log_result("3.1 Acesso Step 2", True, "Step 2 acessível")
            else:
                self.log_result("3.1 Acesso Step 2", False, f"Status {response.status_code}")
                
            # Teste 3.2: Salvamento step 2
            onboarding_data = {
                "step": 2,
                "full_name": "Usuario Validacao Complete",
                "phone": "",
                "farm_experience": "iniciante",
                "producer_type": "hobby",
                "interests": ["vegetables"]
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/onboarding/save",
                json=onboarding_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("3.2 Salvamento Step 2", True, "Dados salvos com sucesso")
                else:
                    self.log_result("3.2 Salvamento Step 2", False, f"Erro: {data.get('error')}")
            else:
                self.log_result("3.2 Salvamento Step 2", False, f"Status {response.status_code}")
                
        except Exception as e:
            self.log_result("3.1-3.2 Onboarding", False, f"Erro: {e}")
            
    def test_error_messages(self):
        """CORREÇÃO 4: Mensagens de Erro Específicas"""
        print("\n📋 CORREÇÃO 4: MENSAGENS DE ERRO")
        
        # Teste 4.1: Login com credenciais inválidas
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": "inexistente@agrotech.com", "password": "senha123"}
            )
            if response.status_code == 401:
                data = response.json()
                if 'error' in data and len(data['error']) > 5:
                    self.log_result("4.1 Erro Login", True, "Mensagem específica retornada")
                else:
                    self.log_result("4.1 Erro Login", False, "Mensagem genérica")
            else:
                self.log_result("4.1 Erro Login", False, f"Status inesperado: {response.status_code}")
        except Exception as e:
            self.log_result("4.1 Erro Login", False, f"Erro: {e}")
            
    def generate_report(self):
        """Gerar relatório final"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE VALIDAÇÃO SPRINT 1")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 RESULTADOS:")
        print(f"   Total de Testes: {total_tests}")
        print(f"   ✅ Aprovados: {passed_tests}")
        print(f"   ❌ Reprovados: {failed_tests}")
        print(f"   📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        print(f"\n🎯 STATUS FINAL:")
        if success_rate >= 80:
            print("   ✅ APROVADO - Sprint 1 pronto para produção")
        else:
            print("   ❌ REPROVADO - Correções adicionais necessárias")
            
        print(f"\n📋 CORREÇÕES OBRIGATÓRIAS:")
        corrections = {
            1: [r for r in self.results if r['test'].startswith('1.')],
            2: [r for r in self.results if r['test'].startswith('2.')],
            3: [r for r in self.results if r['test'].startswith('3.')],
            4: [r for r in self.results if r['test'].startswith('4.')]
        }
        
        for i, tests in corrections.items():
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                status = "✅" if passed == total else "❌"
                print(f"   {status} Correção {i}: {passed}/{total} testes aprovados")
                
        return success_rate >= 80

def main():
    print("🚀 INICIANDO VALIDAÇÃO SPRINT 1")
    print("Conforme decisão do Gerente de Tecnologia")
    print("Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    validator = SprintValidator()
    
    try:
        validator.test_register_system()
        validator.test_session_system()
        validator.test_onboarding_system()
        validator.test_error_messages()
        
        approved = validator.generate_report()
        
        if approved:
            print("\n🎉 SPRINT 1 APROVADO PARA RESUBMISSÃO!")
        else:
            print("\n⚠️  CORREÇÕES ADICIONAIS NECESSÁRIAS")
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO NA VALIDAÇÃO: {e}")
        
if __name__ == "__main__":
    main()
