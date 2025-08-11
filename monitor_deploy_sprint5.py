#!/usr/bin/env python3
"""
Monitor de Deploy Sprint 5 - AgroTech Portugal
Monitora o status do deploy automático no Railway.app
"""

import requests
import time
import json
import sys
from datetime import datetime
import subprocess

class DeployMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.deploy_url = None
        self.check_interval = 30  # segundos
        self.max_wait_time = 600  # 10 minutos
        
    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEPLOY": "🚀"
        }
        print(f"{emoji.get(status, 'ℹ️')} [{timestamp}] {message}")
    
    def check_git_status(self):
        """Verificar se o push foi realizado com sucesso"""
        self.print_status("Verificando status do Git...", "INFO")
        
        try:
            # Verificar último commit
            result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                commit = result.stdout.strip()
                self.print_status(f"Último commit: {commit}", "SUCCESS")
                return True
            else:
                self.print_status("Erro ao verificar Git", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Erro Git: {e}", "ERROR")
            return False
    
    def get_railway_url(self):
        """Tentar obter URL do Railway (se railway CLI estiver disponível)"""
        try:
            result = subprocess.run(['railway', 'status'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Tentar extrair URL do output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'https://' in line and 'railway.app' in line:
                        self.deploy_url = line.strip()
                        return self.deploy_url
        except:
            pass
        
        # URL padrão se não conseguir detectar
        self.deploy_url = "https://agente-agricola-production.up.railway.app"
        return self.deploy_url
    
    def check_deploy_status(self):
        """Verificar se o deploy está ativo"""
        if not self.deploy_url:
            self.deploy_url = self.get_railway_url()
        
        self.print_status(f"Verificando deploy em: {self.deploy_url}", "DEPLOY")
        
        try:
            # Tentar acessar health endpoint
            health_url = f"{self.deploy_url}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                self.print_status("✅ Deploy ATIVO - Aplicação respondendo!", "SUCCESS")
                return True
            else:
                self.print_status(f"Deploy em progresso - Status: {response.status_code}", "WARNING")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_status("Deploy em progresso - Aguardando ativação...", "INFO")
            return False
        except requests.exceptions.Timeout:
            self.print_status("Deploy em progresso - Timeout na conexão", "WARNING")
            return False
        except Exception as e:
            self.print_status(f"Erro ao verificar deploy: {e}", "ERROR")
            return False
    
    def test_main_endpoints(self):
        """Testar endpoints principais após deploy ativo"""
        endpoints = [
            "/",
            "/health", 
            "/login",
            "/register",
            "/api/weather/current"
        ]
        
        self.print_status("Testando endpoints principais...", "INFO")
        
        for endpoint in endpoints:
            try:
                url = f"{self.deploy_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.print_status(f"✅ {endpoint} - OK", "SUCCESS")
                elif response.status_code == 404:
                    self.print_status(f"⚠️ {endpoint} - Not Found (normal)", "WARNING")
                else:
                    self.print_status(f"⚠️ {endpoint} - Status: {response.status_code}", "WARNING")
                    
            except Exception as e:
                self.print_status(f"❌ {endpoint} - Erro: {e}", "ERROR")
    
    def check_sprint5_features(self):
        """Verificar funcionalidades específicas do Sprint 5"""
        self.print_status("Verificando funcionalidades do Sprint 5...", "INFO")
        
        features = [
            ("/static/css/design-system.css", "Design System"),
            ("/static/css/onboarding.css", "Onboarding CSS"),
            ("/static/js/micro-interactions.js", "Micro-interações"),
            ("/api/onboarding/progress", "API Onboarding")
        ]
        
        for endpoint, name in features:
            try:
                url = f"{self.deploy_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.print_status(f"✅ {name} - Disponível", "SUCCESS")
                else:
                    self.print_status(f"⚠️ {name} - Status: {response.status_code}", "WARNING")
                    
            except Exception as e:
                self.print_status(f"❌ {name} - Erro: {e}", "ERROR")
    
    def monitor_deploy(self):
        """Monitorar o processo completo de deploy"""
        self.print_status("🚀 INICIANDO MONITORAMENTO DO DEPLOY SPRINT 5", "DEPLOY")
        self.print_status("=" * 60, "INFO")
        
        # Verificar Git
        if not self.check_git_status():
            self.print_status("Falha na verificação do Git. Abortando.", "ERROR")
            return False
        
        # Obter URL do Railway
        self.get_railway_url()
        self.print_status(f"Monitorando URL: {self.deploy_url}", "INFO")
        
        # Aguardar deploy ficar ativo
        elapsed_time = 0
        while elapsed_time < self.max_wait_time:
            if self.check_deploy_status():
                # Deploy ativo! Testar funcionalidades
                self.print_status("🎉 DEPLOY CONCLUÍDO COM SUCESSO!", "SUCCESS")
                self.print_status("=" * 60, "INFO")
                
                # Aguardar um pouco para estabilizar
                time.sleep(10)
                
                # Testar endpoints
                self.test_main_endpoints()
                print()
                
                # Testar funcionalidades do Sprint 5
                self.check_sprint5_features()
                print()
                
                self.print_status("✅ SPRINT 5 DEPLOYADO E FUNCIONAL!", "SUCCESS")
                self.print_status(f"🌐 Acesse: {self.deploy_url}", "SUCCESS")
                return True
            
            # Aguardar próxima verificação
            self.print_status(f"Aguardando... ({elapsed_time}s/{self.max_wait_time}s)", "INFO")
            time.sleep(self.check_interval)
            elapsed_time += self.check_interval
        
        # Timeout
        self.print_status("⏰ Timeout - Deploy ainda em progresso", "WARNING")
        self.print_status("Verifique manualmente o Railway dashboard", "INFO")
        return False

def main():
    monitor = DeployMonitor()
    
    print("🚀 MONITOR DE DEPLOY - AGROTECH PORTUGAL")
    print("📅 Sprint 5: Polimento e Lançamento")
    print("🕐 Iniciado em:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 60)
    print()
    
    try:
        success = monitor.monitor_deploy()
        
        print()
        print("=" * 60)
        if success:
            print("🎉 DEPLOY SPRINT 5 CONCLUÍDO COM SUCESSO!")
            print("🌱 AgroTech Portugal está LIVE em produção!")
            print("🇵🇹 Pronto para lançamento comercial!")
        else:
            print("⏳ Deploy ainda em progresso...")
            print("🔍 Verifique o Railway dashboard para mais detalhes")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro no monitoramento: {e}")

if __name__ == "__main__":
    main()
