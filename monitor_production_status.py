#!/usr/bin/env python3
"""
Monitor de Status de Produção - Railway
Verifica se as correções de schema foram aplicadas com sucesso
"""
import requests
import json
from datetime import datetime
import os

def test_production_endpoints():
    """Testa endpoints críticos da aplicação em produção"""
    
    # URLs de teste (tentativas baseadas no padrão Railway)
    possible_urls = [
        "https://agente-agricola.up.railway.app",
        "https://agente-agricola-fresh.up.railway.app", 
        "https://web-production-6f4a.up.railway.app",
        "https://web-production-0d59.up.railway.app"
    ]
    
    print("🔍 ANÁLISE DE STATUS DA APLICAÇÃO RAILWAY")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    working_url = None
    
    # Encontrar URL que funciona
    for url in possible_urls:
        print(f"🌐 Testando: {url}")
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                working_url = url
                print(f"✅ URL encontrada: {url}")
                break
            else:
                print(f"❌ Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    if not working_url:
        print("\n❌ NENHUMA URL RESPONDENDO")
        print("🔧 Possíveis causas:")
        print("   - Aplicação não iniciada no Railway")
        print("   - URL mudou")
        print("   - Erro crítico impedindo inicialização")
        return False
    
    print(f"\n✅ APLICAÇÃO ENCONTRADA: {working_url}")
    print("=" * 60)
    
    # Testar endpoints críticos
    endpoints = {
        "Health Check": "/health",
        "Home": "/",
        "API Dashboard": "/api/dashboard/stats", 
        "API Alerts Widget": "/api/alerts/widget",
        "API Alerts Health": "/api/alerts/health"
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        url = f"{working_url}{endpoint}"
        print(f"\n🔍 Testando {name}: {endpoint}")
        
        try:
            response = requests.get(url, timeout=15)
            status = response.status_code
            
            if status == 200:
                print(f"✅ Status: {status} OK")
                try:
                    data = response.json()
                    if 'error' in data:
                        print(f"⚠️  Resposta contém erro: {data.get('error')}")
                        results[name] = f"200_with_error: {data.get('error')}"
                    else:
                        print(f"✅ Dados: {json.dumps(data, indent=2)[:200]}...")
                        results[name] = "success"
                except:
                    print(f"✅ Conteúdo HTML (não JSON)")
                    results[name] = "success_html"
            
            elif status == 401:
                print(f"🔐 Status: {status} (Autenticação necessária - Normal para endpoints protegidos)")
                results[name] = "auth_required"
            
            elif status == 500:
                print(f"❌ Status: {status} (Erro interno - Possível problema de schema)")
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data}")
                    results[name] = f"500_error: {error_data.get('error', 'unknown')}"
                except:
                    print(f"   Erro HTML: {response.text[:200]}...")
                    results[name] = "500_error"
            
            else:
                print(f"⚠️  Status: {status}")
                results[name] = f"status_{status}"
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            results[name] = f"request_error: {e}"
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    success_count = 0
    total_count = len(results)
    
    for endpoint, result in results.items():
        if result in ["success", "success_html", "auth_required"]:
            status_icon = "✅"
            success_count += 1
        elif "500_error" in result:
            status_icon = "❌"
        else:
            status_icon = "⚠️"
            
        print(f"{status_icon} {endpoint}: {result}")
    
    print(f"\n📈 Taxa de Sucesso: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    # Análise específica da API de alertas
    if "API Alerts Widget" in results:
        alert_result = results["API Alerts Widget"]
        if "500_error" in alert_result:
            print("\n🚨 PROBLEMA IDENTIFICADO: API de Alertas com erro 500")
            print("🔧 Possíveis causas:")
            print("   - Colunas ainda não criadas na tabela alerts")
            print("   - Aplicação não reiniciou após deploy")
            print("   - Erro no código Python do modelo Alert")
            print("\n💡 RECOMENDAÇÕES:")
            print("   1. Aguardar mais 5-10 minutos para restart automático")
            print("   2. Verificar logs do Railway para erros específicos")
            print("   3. Forçar restart manual se necessário")
        elif alert_result == "auth_required":
            print("\n✅ API de Alertas respondendo corretamente (401 = sem autenticação)")
            print("🎯 Schema provavelmente corrigido com sucesso!")
    
    return working_url

if __name__ == "__main__":
    test_production_endpoints()
