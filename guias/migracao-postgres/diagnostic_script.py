#!/usr/bin/env python3
"""
Script de Diagnóstico para Problemas de Migração
Execute quando houver problemas durante ou após migrações
"""

import os
import psycopg2
import requests
import json
from datetime import datetime

def check_environment():
    """Verifica variáveis de ambiente essenciais"""
    
    print("🔍 VERIFICAÇÃO DE AMBIENTE")
    print("=" * 40)
    
    essential_vars = {
        'DATABASE_URL': 'URL de conexão com PostgreSQL',
        'FLASK_ENV': 'Ambiente Flask (development/production)',
        'FLASK_CONFIG': 'Configuração Flask'
    }
    
    missing_vars = []
    
    for var, description in essential_vars.items():
        value = os.getenv(var)
        if value:
            # Mascarar valores sensíveis
            if 'URL' in var or 'PASSWORD' in var:
                display_value = value[:20] + '...' if len(value) > 20 else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NÃO DEFINIDA ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Variáveis faltantes: {len(missing_vars)}")
        print("💡 Configure as variáveis antes de continuar")
        return False
    else:
        print("✅ Todas as variáveis de ambiente estão configuradas")
        return True

def check_database_connection():
    """Verifica conectividade com o banco de dados"""
    
    print("\n🗄️ VERIFICAÇÃO DE BANCO DE DADOS")
    print("=" * 40)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada!")
        return False
    
    try:
        # Testar conexão
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Informações básicas
        cursor.execute("SELECT version();")
        version_result = cursor.fetchone()
        version = version_result[0] if version_result else "Versão não disponível"
        print(f"✅ PostgreSQL conectado")
        print(f"   Versão: {version.split(',')[0]}")
        
        # Verificar tabelas existentes
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Tabelas encontradas: {len(tables)}")
        
        critical_tables = ['users', 'alerts', 'cultures']
        missing_tables = [table for table in critical_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Tabelas críticas faltantes: {missing_tables}")
        else:
            print("✅ Todas as tabelas críticas estão presentes")
        
        # Verificar específicamente a tabela alerts
        if 'alerts' in tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'alerts' 
                ORDER BY column_name;
            """)
            alert_columns = cursor.fetchall()
            print(f"✅ Tabela 'alerts' possui {len(alert_columns)} colunas")
            
            # Colunas críticas para o funcionamento
            critical_columns = [
                'id', 'user_id', 'type', 'priority', 'status', 'title', 'message',
                'action_text', 'read_at', 'dismissed_at'
            ]
            existing_columns = [col[0] for col in alert_columns]
            missing_critical = [col for col in critical_columns if col not in existing_columns]
            
            if missing_critical:
                print(f"❌ Colunas críticas faltantes em 'alerts': {missing_critical}")
            else:
                print("✅ Todas as colunas críticas estão presentes em 'alerts'")
        
        cursor.close()
        conn.close()
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        return False

def check_api_status():
    """Verifica status das APIs da aplicação"""
    
    print("\n🌐 VERIFICAÇÃO DE APIS")
    print("=" * 40)
    
    base_url = "https://www.agenteagricola.com"
    
    endpoints = [
        ("/health", "Health Check Geral"),
        ("/api/alerts/health", "Health Check Alerts"),
        ("/api/alerts/widget", "Widget de Alertas"),
        ("/api/dashboard/stats", "Stats do Dashboard"),
        ("/", "Página Principal")
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            
            status_ok = response.status_code in [200, 401]  # 401 é OK para endpoints protegidos
            
            if status_ok:
                print(f"✅ {name}: Status {response.status_code}")
                
                if response.status_code == 200 and endpoint.startswith('/api'):
                    try:
                        data = response.json()
                        # Verificar se há erros de coluna (indicativo de problemas de schema)
                        response_text = json.dumps(data).lower()
                        if 'column' in response_text and 'does not exist' in response_text:
                            print(f"❌ {name}: Erro de schema detectado!")
                            print(f"   {data}")
                            results.append(False)
                        else:
                            results.append(True)
                    except json.JSONDecodeError:
                        results.append(True)  # HTML válido
                else:
                    results.append(True)
            else:
                print(f"❌ {name}: Status {response.status_code}")
                if response.status_code == 500:
                    try:
                        error_data = response.json()
                        print(f"   Erro: {error_data}")
                    except:
                        print(f"   Erro: {response.text[:100]}...")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {name}: Erro de conexão - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100 if results else 0
    print(f"\n📊 Taxa de sucesso das APIs: {success_rate:.1f}%")
    
    return success_rate >= 80  # 80% ou mais considerado OK

def diagnose_common_issues():
    """Diagnostica problemas comuns e sugere soluções"""
    
    print("\n🔧 DIAGNÓSTICO DE PROBLEMAS COMUNS")
    print("=" * 40)
    
    issues_found = []
    
    # 1. Verificar se há erros específicos de coluna
    try:
        response = requests.get("https://www.agenteagricola.com/api/alerts/health", timeout=5)
        if response.status_code == 500:
            try:
                error_data = response.json()
                if 'column' in str(error_data).lower() and 'does not exist' in str(error_data).lower():
                    issues_found.append("SCHEMA_ERROR")
                    print("❌ Problema identificado: Erro de schema (coluna inexistente)")
                    print("💡 Solução: Execute o script de migração")
                    print("   python guias/migration_script.py")
            except:
                pass
    except:
        pass
    
    # 2. Verificar conectividade geral
    try:
        response = requests.get("https://www.agenteagricola.com/health", timeout=5)
        if response.status_code != 200:
            issues_found.append("CONNECTIVITY_ERROR")
            print("❌ Problema identificado: Aplicação não responde")
            print("💡 Solução: Verificar status do Railway")
            print("   railway status")
    except:
        issues_found.append("CONNECTIVITY_ERROR")
        print("❌ Problema identificado: Aplicação inacessível")
    
    # 3. Verificar banco de dados
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            conn.close()
        except Exception as e:
            issues_found.append("DATABASE_ERROR")
            print("❌ Problema identificado: Erro de banco de dados")
            print(f"   Erro: {e}")
            print("💡 Solução: Verificar DATABASE_URL e status do banco")
    
    if not issues_found:
        print("✅ Nenhum problema comum identificado")
        print("💡 Execute validação completa: python guias/validation_script.py")
    
    return len(issues_found) == 0

def generate_diagnostic_report():
    """Gera relatório completo de diagnóstico"""
    
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE DIAGNÓSTICO")
    print("="*60)
    
    timestamp = datetime.now().isoformat()
    
    # Executar todos os diagnósticos
    env_ok = check_environment()
    db_ok = check_database_connection()
    api_ok = check_api_status()
    no_issues = diagnose_common_issues()
    
    # Calcular score geral
    checks = [env_ok, db_ok, api_ok, no_issues]
    success_count = sum(checks)
    total_checks = len(checks)
    health_score = (success_count / total_checks) * 100
    
    print(f"\n📊 RESUMO GERAL")
    print("-" * 30)
    print(f"Timestamp: {timestamp}")
    print(f"Ambiente: {'✅ OK' if env_ok else '❌ PROBLEMAS'}")
    print(f"Banco de Dados: {'✅ OK' if db_ok else '❌ PROBLEMAS'}")
    print(f"APIs: {'✅ OK' if api_ok else '❌ PROBLEMAS'}")
    print(f"Problemas Comuns: {'✅ NENHUM' if no_issues else '❌ ENCONTRADOS'}")
    print(f"\n🎯 Score de Saúde: {success_count}/{total_checks} ({health_score:.1f}%)")
    
    # Status final e recomendações
    if health_score == 100:
        print("\n🎉 SISTEMA TOTALMENTE SAUDÁVEL")
        print("✅ Nenhuma ação necessária")
        status = "SAUDAVEL"
    elif health_score >= 75:
        print("\n✅ SISTEMA FUNCIONAL COM PEQUENOS PROBLEMAS")
        print("🔧 Problemas menores identificados - correção recomendada")
        status = "FUNCIONAL"
    elif health_score >= 50:
        print("\n⚠️ SISTEMA COM PROBLEMAS SIGNIFICATIVOS")
        print("🚨 Ação imediata recomendada")
        status = "PROBLEMAS"
    else:
        print("\n❌ SISTEMA COM PROBLEMAS CRÍTICOS")
        print("🆘 Intervenção urgente necessária")
        status = "CRITICO"
    
    # Salvar relatório
    try:
        report_content = f"""# RELATÓRIO DE DIAGNÓSTICO

**Timestamp:** {timestamp}
**Status Geral:** {status}
**Score de Saúde:** {health_score:.1f}%

## Verificações

- **Ambiente:** {'✅ OK' if env_ok else '❌ PROBLEMAS'}
- **Banco de Dados:** {'✅ OK' if db_ok else '❌ PROBLEMAS'}
- **APIs:** {'✅ OK' if api_ok else '❌ PROBLEMAS'}
- **Problemas Comuns:** {'✅ NENHUM' if no_issues else '❌ ENCONTRADOS'}

## Próximos Passos Recomendados

{
'✅ Sistema funcionando normalmente' if health_score == 100 
else '🔧 Executar correções baseadas nos problemas identificados acima'
}

### Scripts Úteis

- Migração: `python guias/migration_script.py`
- Validação: `python guias/validation_script.py`
- Diagnóstico: `python guias/diagnostic_script.py`

---
*Relatório gerado automaticamente*
"""
        
        report_filename = f"guias/diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📄 Relatório salvo em: {report_filename}")
        
    except Exception as e:
        print(f"⚠️ Não foi possível salvar o relatório: {e}")
    
    return health_score >= 75

if __name__ == "__main__":
    print("🔍 SCRIPT DE DIAGNÓSTICO DE MIGRAÇÃO")
    print("=" * 50)
    print(f"Início: {datetime.now().isoformat()}")
    
    system_healthy = generate_diagnostic_report()
    
    print(f"\nFim: {datetime.now().isoformat()}")
    print(f"Sistema {'saudável' if system_healthy else 'requer atenção'}")
    
    exit(0 if system_healthy else 1)
