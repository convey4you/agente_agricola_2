#!/usr/bin/env python3
"""
Script para Correção dos Health Checks em Produção
Força novo deploy e verifica se os endpoints estão funcionando
Autor: Gerente de Tecnologia
Data: 1 de agosto de 2025
"""

import requests
import time
import sys
from datetime import datetime

class ProductionHealthFixer:
    """Fix para health checks em produção"""
    
    def __init__(self):
        self.production_url = "https://www.agenteagricola.com"
        self.local_url = "http://localhost:5000"
        
    def check_local_health(self):
        """Verifica se health checks funcionam localmente"""
        print("🔍 Verificando health checks localmente...")
        
        try:
            response = requests.get(f"{self.local_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Health checks funcionando localmente")
                return True
            else:
                print(f"❌ Health check local falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar localmente: {e}")
            return False
    
    def check_production_health(self):
        """Verifica health checks em produção"""
        print("🔍 Verificando health checks em produção...")
        
        endpoints = ['/health', '/health/db', '/health/registration', '/health/system']
        working_endpoints = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.production_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {endpoint} funcionando")
                    working_endpoints += 1
                else:
                    print(f"❌ {endpoint} retornando {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} erro: {e}")
        
        print(f"📊 Endpoints funcionando: {working_endpoints}/{len(endpoints)}")
        return working_endpoints == len(endpoints)
    
    def suggest_deploy_fix(self):
        """Sugere comandos para corrigir o deploy"""
        print("\n" + "="*60)
        print("🚀 PLANO DE CORREÇÃO DO DEPLOY")
        print("="*60)
        
        print("\n1. VERIFICAR ARQUIVOS CRÍTICOS:")
        print("   - app/__init__.py (linha ~206: register_blueprint(health_bp))")
        print("   - app/controllers/health_controller.py (deve existir)")
        print("   - requirements.txt (psutil deve estar incluído)")
        
        print("\n2. COMANDOS PARA RAILWAY DEPLOY:")
        print("   railway login")
        print("   railway link")
        print("   git add .")
        print("   git commit -m 'Fix: Force health check endpoints deploy'")
        print("   git push origin main")
        print("   railway up")
        
        print("\n3. VERIFICAR LOGS EM PRODUÇÃO:")
        print("   railway logs")
        
        print("\n4. TESTAR APÓS DEPLOY:")
        print("   curl https://www.agenteagricola.com/health")
        
        print("\n" + "="*60)
    
    def create_railway_deploy_script(self):
        """Cria script para deploy no Railway"""
        deploy_script = """#!/bin/bash
# Script de Deploy para Railway - Health Check Fix

echo "Iniciando deploy das correcoes de health check..."

# Verificar se estamos na pasta correta
if [ ! -f "app/__init__.py" ]; then
    echo "Erro: Execute este script na raiz do projeto"
    exit 1
fi

# Verificar se health_controller existe
if [ ! -f "app/controllers/health_controller.py" ]; then
    echo "Erro: health_controller.py nao encontrado"
    exit 1
fi

# Verificar registro do blueprint
if ! grep -q "health_bp" app/__init__.py; then
    echo "Erro: health_bp nao esta registrado em app/__init__.py"
    exit 1
fi

echo "Arquivos verificados"

# Fazer deploy
echo "Fazendo commit das mudancas..."
git add .
git commit -m "Fix: Force deploy health check endpoints - Sprint 1 corrections"

echo "Fazendo push para Railway..."
git push origin main

echo "Aguardando deploy..."
sleep 30

echo "Testando endpoints..."
curl -f https://www.agenteagricola.com/health || echo "Health check ainda nao funcionando"

echo "Deploy concluido. Verificar logs com: railway logs"
"""
        
        with open("deploy_health_fix.sh", "w", encoding='utf-8') as f:
            f.write(deploy_script)
        
        print("📄 Script de deploy criado: deploy_health_fix.sh")
    
    def run_diagnosis(self):
        """Executa diagnóstico completo"""
        print("🏥 DIAGNÓSTICO DOS HEALTH CHECKS")
        print("="*50)
        print(f"Data/Hora: {datetime.now()}")
        print(f"Local URL: {self.local_url}")
        print(f"Produção URL: {self.production_url}")
        print()
        
        # Verificar local
        local_ok = self.check_local_health()
        
        # Verificar produção
        production_ok = self.check_production_health()
        
        print("\n" + "="*50)
        print("📊 RESUMO DO DIAGNÓSTICO")
        print("="*50)
        print(f"Local: {'✅ OK' if local_ok else '❌ FALHOU'}")
        print(f"Produção: {'✅ OK' if production_ok else '❌ FALHOU'}")
        
        if local_ok and not production_ok:
            print("\n🎯 PROBLEMA IDENTIFICADO:")
            print("   Health checks funcionam localmente mas não em produção")
            print("   Isso indica problema de deploy ou configuração de produção")
            
            self.suggest_deploy_fix()
            self.create_railway_deploy_script()
            
        elif not local_ok and not production_ok:
            print("\n🎯 PROBLEMA CRÍTICO:")
            print("   Health checks não funcionam nem localmente nem em produção")
            print("   Verificar implementação do health_controller.py")
            
        elif local_ok and production_ok:
            print("\n🎉 TUDO FUNCIONANDO:")
            print("   Health checks operacionais em ambos os ambientes")
            
        else:
            print("\n🤔 SITUAÇÃO INUSITADA:")
            print("   Produção funciona mas local não")

def main():
    """Função principal"""
    fixer = ProductionHealthFixer()
    fixer.run_diagnosis()

if __name__ == "__main__":
    main()
