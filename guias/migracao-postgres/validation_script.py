#!/usr/bin/env python3
"""
Script de Validação Pós-Migração
Valida se todas as migrações foram aplicadas corretamente
"""

import requests
import json
import os
import psycopg2
from datetime import datetime

def validate_database_schema():
    """Valida o schema do banco de dados"""
    
    print("🗄️ VALIDAÇÃO DE SCHEMA")
    print("=" * 40)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada!")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar tabela alerts
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'alerts' 
            ORDER BY column_name;
        """)
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ Tabela 'alerts' não encontrada!")
            return False
        
        print(f"✅ Tabela 'alerts' encontrada com {len(columns)} colunas")
        
        # Colunas essenciais que devem existir
        essential_columns = [
            'action_text', 'action_url', 'read_at', 'dismissed_at', 
            'scheduled_for', 'expires_at', 'delivery_channels'
        ]
        
        existing_column_names = [col[0] for col in columns]
        missing_essential = [col for col in essential_columns if col not in existing_column_names]
        
        if missing_essential:
            print(f"❌ Colunas essenciais faltantes: {missing_essential}")
            return False
        else:
            print("✅ Todas as colunas essenciais estão presentes")
        
        # Testar inserção básica (rollback)
        cursor.execute("BEGIN;")
        try:
            cursor.execute("""
                INSERT INTO alerts (user_id, type, priority, status, title, message, created_at)
                VALUES (999, 'general', 'low', 'pending', 'Teste', 'Teste migração', NOW())
                RETURNING id;
            """)
            result = cursor.fetchone()
            test_id = result[0] if result else 'unknown'
            cursor.execute("ROLLBACK;")
            print(f"✅ Teste de inserção bem-sucedido (ID {test_id}, rolled back)")
        except Exception as e:
            cursor.execute("ROLLBACK;")
            print(f"❌ Falha no teste de inserção: {e}")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação do schema: {e}")
        return False

def validate_api_endpoints():
    """Valida os endpoints da API"""
    
    print("\n🌐 VALIDAÇÃO DE ENDPOINTS")
    print("=" * 40)
    
    base_url = "https://www.agenteagricola.com"
    
    tests = [
        ("Health Check Geral", "/health", [200]),
        ("API Alerts Health", "/api/alerts/health", [200]),
        ("API Alerts Widget", "/api/alerts/widget", [200, 401]),  # 401 = OK (sem auth)
        ("Home Page", "/", [200]),
        ("API Dashboard Stats", "/api/dashboard/stats", [200, 401])  # 401 = OK (sem auth)
    ]
    
    all_passed = True
    
    for name, endpoint, valid_codes in tests:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code in valid_codes:
                print(f"✅ {name}: Status {response.status_code} (OK)")
                
                # Verificar se retorna JSON válido (para APIs)
                if endpoint.startswith("/api") and response.status_code == 200:
                    try:
                        data = response.json()
                        if 'error' in str(data).lower() and 'column' in str(data).lower():
                            print(f"⚠️  {name}: Possível erro de schema - {data}")
                            all_passed = False
                        else:
                            print(f"   Dados válidos recebidos")
                    except:
                        print(f"   Resposta não-JSON (pode ser HTML)")
                        
            else:
                print(f"❌ {name}: Status {response.status_code} (esperava {valid_codes})")
                if response.status_code == 500:
                    try:
                        error_data = response.json()
                        print(f"   Erro: {error_data}")
                    except:
                        print(f"   Erro HTML: {response.text[:100]}...")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {name}: Erro de conexão - {e}")
            all_passed = False
    
    return all_passed

def validate_alert_functionality():
    """Valida funcionalidades específicas do sistema de alertas"""
    
    print("\n🚨 VALIDAÇÃO DE FUNCIONALIDADE")
    print("=" * 40)
    
    base_url = "https://www.agenteagricola.com"
    
    # Testar endpoint de health específico da API de alertas
    try:
        response = requests.get(f"{base_url}/api/alerts/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar campos esperados
            expected_fields = ['status', 'data', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Campos faltantes na resposta: {missing_fields}")
                return False
            
            # Verificar dados internos
            if 'data' in data:
                data_fields = data['data']
                expected_data_fields = ['total_alerts', 'available_types', 'available_priorities']
                missing_data = [field for field in expected_data_fields if field not in data_fields]
                
                if missing_data:
                    print(f"❌ Dados faltantes: {missing_data}")
                    return False
                else:
                    print(f"✅ API de alertas funcionando completamente")
                    print(f"   Total de alertas: {data_fields.get('total_alerts', 0)}")
                    print(f"   Tipos disponíveis: {len(data_fields.get('available_types', []))}")
                    print(f"   Prioridades: {len(data_fields.get('available_priorities', []))}")
                    return True
            
        else:
            print(f"❌ Health check falhou: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao validar funcionalidade: {e}")
        return False

def generate_validation_report():
    """Gera relatório completo de validação"""
    
    print("\n📊 GERANDO RELATÓRIO DE VALIDAÇÃO")
    print("=" * 50)
    
    timestamp = datetime.now().isoformat()
    
    # Executar todas as validações
    schema_valid = validate_database_schema()
    api_valid = validate_api_endpoints()
    functionality_valid = validate_alert_functionality()
    
    # Calcular score geral
    validations = [schema_valid, api_valid, functionality_valid]
    success_count = sum(validations)
    total_count = len(validations)
    success_rate = (success_count / total_count) * 100
    
    # Relatório final
    print(f"\n{'='*60}")
    print("📋 RELATÓRIO FINAL DE VALIDAÇÃO")
    print(f"{'='*60}")
    print(f"Timestamp: {timestamp}")
    print(f"URL Produção: https://www.agenteagricola.com")
    print()
    print(f"{'✅' if schema_valid else '❌'} Validação de Schema: {'PASSOU' if schema_valid else 'FALHOU'}")
    print(f"{'✅' if api_valid else '❌'} Validação de APIs: {'PASSOU' if api_valid else 'FALHOU'}")
    print(f"{'✅' if functionality_valid else '❌'} Validação de Funcionalidades: {'PASSOU' if functionality_valid else 'FALHOU'}")
    print()
    print(f"🎯 Taxa de Sucesso: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 MIGRAÇÃO VALIDADA COM 100% DE SUCESSO!")
        status = "SUCESSO_COMPLETO"
    elif success_rate >= 80:
        print("✅ MIGRAÇÃO VALIDADA COM SUCESSO (pequenos ajustes podem ser necessários)")
        status = "SUCESSO_PARCIAL"
    else:
        print("⚠️ MIGRAÇÃO REQUER ATENÇÃO - Problemas identificados")
        status = "REQUER_ATENCAO"
    
    # Salvar relatório em arquivo
    try:
        report_content = f"""# RELATÓRIO DE VALIDAÇÃO DE MIGRAÇÃO

**Timestamp:** {timestamp}
**URL Produção:** https://www.agenteagricola.com
**Status Geral:** {status}

## Resultados

- **Validação de Schema:** {'✅ PASSOU' if schema_valid else '❌ FALHOU'}
- **Validação de APIs:** {'✅ PASSOU' if api_valid else '❌ FALHOU'} 
- **Validação de Funcionalidades:** {'✅ PASSOU' if functionality_valid else '❌ FALHOU'}

**Taxa de Sucesso:** {success_count}/{total_count} ({success_rate:.1f}%)

## Próximos Passos

{'✅ Sistema totalmente funcional - nenhuma ação necessária' if success_rate == 100 else '🔧 Verificar logs e corrigir problemas identificados'}

---
*Relatório gerado automaticamente pelo script de validação*
"""
        
        report_filename = f"guias/relatorio_validacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📄 Relatório salvo em: {report_filename}")
        
    except Exception as e:
        print(f"⚠️ Não foi possível salvar o relatório: {e}")
    
    return success_rate == 100

if __name__ == "__main__":
    print("🧪 SCRIPT DE VALIDAÇÃO PÓS-MIGRAÇÃO")
    print("=" * 50)
    print(f"Início: {datetime.now().isoformat()}")
    
    success = generate_validation_report()
    
    print(f"\nFim: {datetime.now().isoformat()}")
    exit(0 if success else 1)
